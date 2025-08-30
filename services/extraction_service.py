import os
import json
import shutil
import re
import hashlib
from fastapi import UploadFile, HTTPException, Depends
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from pdfminer.high_level import extract_text
import subprocess
from psycopg2.extensions import connection

from ..database import get_db
from ..services.hymn_service import invalidate_hymn_cache
from ..services.cache import cache

# --- Configuration ---
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")
POPPLER_PATH = os.getenv("POPPLER_PATH")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# ---------------------------------------------------------------------------
# HYMN PARSING LOGIC
# ---------------------------------------------------------------------------

def _process_hymn_content(lines, hymn_number):
    if not lines:
        return []

    has_explicit_stanza_nums = False
    if hymn_number != 176:
        for line in lines:
            if re.match(r'^\s*\d+\s*$', line.strip()):
                has_explicit_stanza_nums = True
                break

    content = []
    current_stanza_lines = []
    current_type = 'estrofa'
    current_stanza_num = 1

    def save_current_stanza():
        nonlocal current_stanza_num
        if not current_stanza_lines:
            return
        
        block = {"tipo": current_type}
        if current_type == 'estrofa':
            block["estrofa_num"] = current_stanza_num
            block["texto"] = current_stanza_lines
            current_stanza_num += 1
        else:
            block["texto"] = current_stanza_lines
        
        content.append(block)

    for line in lines:
        stripped_line = line.strip()
        
        if not stripped_line:
            if not has_explicit_stanza_nums and current_stanza_lines:
                save_current_stanza()
                current_stanza_lines = []
                current_type = 'estrofa'
            continue

        stanza_match = None
        if hymn_number == 176:
            stanza_match = re.match(r'^(\d+)\.\s*(.*)', stripped_line)
        elif has_explicit_stanza_nums:
            stanza_match = re.match(r'^(\d+)\s*$', stripped_line)

        if stanza_match:
            if current_stanza_lines:
                save_current_stanza()
            
            current_stanza_lines = []
            current_type = 'estrofa'
            current_stanza_num = int(stanza_match.group(1))
            
            if hymn_number == 176 and stanza_match.group(2):
                current_stanza_lines.append(stanza_match.group(2).strip())

        elif stripped_line.upper().startswith('CORO'):
            if current_stanza_lines:
                save_current_stanza()
            current_stanza_lines = []
            current_type = 'coro'
        else:
            current_stanza_lines.append(stripped_line)

    if current_stanza_lines:
        save_current_stanza()

    return content

def parse_hymns_from_text(all_text: str):
    print("Parsing extracted text to find hymns...")
    all_lines = all_text.split('\n')
    hymns = []
    current_hymn_info = None
    current_hymn_lines = []
    
    hymn_title_regex = re.compile(r'^\s*(\d+)\.\s+([A-ZÁÉÍÓÚÑ\s-]{5,})', re.IGNORECASE)

    for line in all_lines:
        match = hymn_title_regex.search(line)
        
        if match:
            if current_hymn_info and current_hymn_info['numero'] == 176:
                current_hymn_lines.append(line.lower())
                continue

            if current_hymn_info:
                current_hymn_info['contenido'] = _process_hymn_content(current_hymn_lines, current_hymn_info['numero'])
                hymns.append(current_hymn_info)

            hymn_number = int(match.group(1))
            hymn_title = match.group(2).strip().lower()
            current_hymn_info = {'numero': hymn_number, 'titulo': hymn_title}
            current_hymn_lines = []
        
        elif current_hymn_info:
            current_hymn_lines.append(line.lower())

    if current_hymn_info:
        current_hymn_info['contenido'] = _process_hymn_content(current_hymn_lines, current_hymn_info['numero'])
        hymns.append(current_hymn_info)
    
    print(f"Parsing finished. Found {len(hymns)} hymns.")
    return hymns

# ---------------------------------------------------------------------------
# DATABASE INTERACTION LOGIC
# ---------------------------------------------------------------------------

def insert_extracted_data_to_db(hymns_data: list, db: connection):
    conn = db
    try:
        with conn.cursor() as cur:
            for hymn in hymns_data:
                cur.execute(
                    """
                    INSERT INTO hymns (hymn_number, title)
                    VALUES (%s, %s)
                    ON CONFLICT (hymn_number) DO UPDATE SET title = EXCLUDED.title
                    RETURNING id;
                    """,
                    (hymn['numero'], hymn['titulo'])
                )
                hymn_id = cur.fetchone()[0]

                cur.execute("DELETE FROM hymn_content WHERE hymn_id = %s;", (hymn_id,))

                for i, content_item in enumerate(hymn['contenido']):
                    cur.execute(
                        """
                        INSERT INTO hymn_content (hymn_id, content_type, stanza_number, content_order)
                        VALUES (%s, %s, %s, %s) RETURNING id;
                        """,
                        (hymn_id, content_item['tipo'], content_item.get('estrofa_num'), i)
                    )
                    content_id = cur.fetchone()[0]

                    for j, line in enumerate(content_item['texto']):
                        cur.execute(
                            """
                            INSERT INTO content_lines (hymn_content_id, line_text, line_order)
                            VALUES (%s, %s, %s);
                            """,
                            (content_id, line, j)
                        )
            
            conn.commit()
            print(f"Inserted/updated data for {len(hymns_data)} hymns.")
            invalidate_hymn_cache()

    except Exception as e:
        print(f"Error during data insertion/update: {e}")
        conn.rollback()
        raise

# ---------------------------------------------------------------------------
# PDF EXTRACTION SERVICE LOGIC
# ---------------------------------------------------------------------------

async def process_pdf_for_hymns(pdf_file: UploadFile, db: connection = Depends(get_db)):
    # --- Dependency Verification ---
    try:
        subprocess.run([TESSERACT_CMD, "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise HTTPException(
            status_code=500,
            detail=f"Tesseract OCR not found or not configured. Ensure it is in your system PATH or set the TESSERACT_CMD env variable."
        )

    if POPPLER_PATH and not os.path.isdir(POPPLER_PATH):
        raise HTTPException(
            status_code=500,
            detail=f"Poppler path is not a valid directory. Check POPPLER_PATH env variable."
        )

    temp_pdf_path = f"./temp_{pdf_file.filename}"
    try:
        pdf_content = await pdf_file.read()
        pdf_hash = hashlib.sha256(pdf_content).hexdigest()
        cache_key = f"ocr_text:{pdf_hash}"

        # --- Text Extraction with Cache ---
        text_content = cache.get(cache_key)
        if text_content:
            print(f"Found cached OCR text for PDF hash: {pdf_hash}")
        else:
            print("No cache found. Starting extraction process...")
            with open(temp_pdf_path, "wb") as buffer:
                buffer.write(pdf_content)

            try:
                text_content = extract_text(temp_pdf_path)
                if not text_content.strip():
                    print("Direct text extraction yielded empty content. Falling back to OCR.")
                    text_content = ""
                else:
                    print("Text extracted directly from PDF.")
            except Exception as e:
                print(f"Could not extract text directly, falling back to OCR. Error: {e}")
                text_content = ""

            if not text_content.strip():
                print("Performing two-column OCR on PDF pages...")
                try:
                    images = convert_from_path(temp_pdf_path, poppler_path=POPPLER_PATH, dpi=300)
                    ocr_text_parts = []
                    for i, image in enumerate(images):
                        print(f"Processing page {i+1} with OCR...")
                        width, height = image.size
                        mid_width = width // 2
                        
                        left_image = image.crop((0, 0, mid_width, height))
                        ocr_text_parts.append(pytesseract.image_to_string(left_image, lang='spa'))
                        
                        right_image = image.crop((mid_width, 0, width, height))
                        ocr_text_parts.append(pytesseract.image_to_string(right_image, lang='spa'))

                    text_content = "\n".join(ocr_text_parts)
                    print("OCR processing finished. Caching result.")
                    cache.set(cache_key, text_content, ex=3600) # Cache for 1 hour
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"OCR processing failed: {e}")

        if not text_content.strip():
            raise Exception("No text could be extracted from the PDF.")

        # --- Parsing and DB Insertion ---
        hymns_data = parse_hymns_from_text(text_content)
        if hymns_data:
            insert_extracted_data_to_db(hymns_data, db)

        return {"status": "success", "hymns_extracted": len(hymns_data)}

    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)