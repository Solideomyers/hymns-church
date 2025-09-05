from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.orm import Session
from services import extraction_service
from database import get_db
from core.exceptions import PdfProcessingError

router = APIRouter(
    prefix="/extraction",
    tags=["Extraction"],
)

@router.post("/hymns-from-pdf",
            summary="Extract hymns from a PDF file",
            description="Upload a PDF file of a hymnary. The service will process the file, extract the hymns using OCR, parse them, and store them in the database.",
            response_description="A confirmation message with the number of hymns extracted.")
async def extract_hymns_from_pdf(pdf_file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Extracts hymns from an uploaded PDF file.

    - **pdf_file**: The PDF file to process.
    """
    if not pdf_file.filename.endswith(".pdf"):
        raise PdfProcessingError(detail="Only PDF files are allowed")
    
    result = await extraction_service.process_pdf_for_hymns(pdf_file, db)
    return {"message": "Extraction process completed successfully", "result": result}