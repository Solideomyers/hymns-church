from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..services import generator_service
from ..models import schemas
from ..database import get_db
from ..core.exceptions import HimnarioGeneratorException

router = APIRouter(
    prefix="/generator",
    tags=["Generator"],
)

@router.post("/docx",
            summary="Generate a DOCX document from a list of hymn numbers",
            description="Creates a .docx file containing the full content of the specified hymns. The generated file is returned as a response.",
            response_class=FileResponse)
async def generate_hymnary_docx(request: schemas.GenerateDocxRequest, db: Session = Depends(get_db)):
    """
    Generates a DOCX document from a list of hymn numbers.

    - **hymn_numbers**: A list of hymn numbers to include in the document.
    - **file_name**: The desired name for the output .docx file.
    """
    # The service layer should raise appropriate exceptions
    file_path = await generator_service.generate_hymnary_docx(db, request.hymn_ids, request.file_name)
    return FileResponse(path=file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=request.file_name)