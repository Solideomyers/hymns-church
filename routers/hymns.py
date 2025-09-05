from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from models import schemas
from services import hymn_service
from database import get_db

router = APIRouter(
    prefix="/hymns",
    tags=["Hymns"],
)

@router.get("/", 
            response_model=List[schemas.Hymn],
            summary="Get a list of all hymns",
            description="Returns a list of all hymns stored in the database, without their content.",
            response_description="A list of hymns, each with a number and a title.")
def read_hymns(db: Session = Depends(get_db)):
    """
    Retrieves a list of all hymns.
    """
    return hymn_service.get_hymns(db)

@router.get("/{hymn_id}", 
            response_model=schemas.Hymn,
            summary="Get a specific hymn by its ID",
            description="Returns a single hymn, including its full content (stanzas and choruses).",
            response_description="The full hymn object, including content.")
def read_hymn(hymn_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific hymn by its unique ID.
    - **hymn_id**: The database ID of the hymn to retrieve.
    """
    # The service layer now raises HymnNotFoundError, which is handled globally
    return hymn_service.get_hymn(db, hymn_id)