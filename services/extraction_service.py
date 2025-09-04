import os
import hashlib
import subprocess
from fastapi import UploadFile, Depends
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from pdfminer.high_level import extract_text
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import hymn_service
from ..services import hymn_parser # Import the new parser module
from ..services.cache import cache
from ..core.exceptions import PdfProcessingError, DatabaseError

# --- Configuration ---
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")
POPPLER_PATH = os.getenv("POPPLER_PATH")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# ---------------------------------------------------------------------------
# PDF EXTRACTION SERVICE LOGIC
# ---------------------------------------------------------------------------

async def process_pdf_for_hymns(pdf_file: UploadFile, db: Session = Depends(get_db)):
    # --- Dependency Verification ---
    try:
        subprocess.run([TESSERACT_CMD, "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise PdfProcessingError(
            detail=f"Tesseract OCR not found or not configured. Ensure it is in your system PATH or set the TESSERACT_CMD env variable."
        )

    if POPPLER_PATH and not os.path.isdir(POPPLER_PATH):
        raise PdfProcessingError(
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
                    raise PdfProcessingError(detail=f"OCR processing failed: {e}")

        if not text_content.strip():
            raise PdfProcessingError(detail="No text could be extracted from the PDF.")

        # --- Parsing and DB Insertion ---
        hymns_data = hymn_parser.parse_hymns_from_text(text_content)
        if hymns_data:
            try:
                hymn_service.create_or_update_hymns_from_parsed_data(db, hymns_data)
            except Exception as e:
                raise DatabaseError(detail=f"Failed to save extracted hymns to database: {e}")

        return {"status": "success", "hymns_extracted": len(hymns_data)}

    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
