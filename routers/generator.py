from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from ..services import generator_service
from ..models import schemas

router = APIRouter(
    prefix="/generator",
    tags=["Generator"],
)

@router.post("/docx",
            summary="Generate a DOCX document from a list of hymn numbers",
            description="Creates a .docx file containing the full content of the specified hymns. The generated file is returned as a response.",
            response_class=FileResponse)
async def generate_hymnary_docx(request: schemas.GenerateDocxRequest):
    """
    Generates a DOCX document from a list of hymn numbers.

    - **hymn_numbers**: A list of hymn numbers to include in the document.
    - **file_name**: The desired name for the output .docx file.
    """
    try:
        file_path = await generator_service.generate_hymnary_docx(request.hymn_numbers, request.file_name)
        return FileResponse(path=file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=request.file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate document: {e}")