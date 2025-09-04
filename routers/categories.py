from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from ..models import schemas
from ..services import category_service
from ..database import get_db

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)

@router.get("/", 
            response_model=List[schemas.Category],
            summary="Get all categories",
            description="Returns a list of all hymn categories available in the database.",
            response_description="A list of category objects.")
def read_categories(db: Session = Depends(get_db)):
    """
    Retrieves a list of all categories.
    """
    return category_service.get_categories(db)

@router.post("/", 
             response_model=schemas.Category, 
             status_code=status.HTTP_201_CREATED,
             summary="Create a new category",
             description="Adds a new category to the database.",
             response_description="The newly created category object.")
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """
    Creates a new category.
    - **name**: The name of the category to create.
    """
    return category_service.create_category(db, category)

@router.put("/assign",
            status_code=status.HTTP_200_OK,
            summary="Assign a category to a hymn",
            description="Assigns an existing category to an existing hymn.")
def assign_category_to_hymn(hymn_id: int, category_id: int, db: Session = Depends(get_db)):
    """
    Assigns a category to a hymn.
    - **hymn_id**: The ID of the hymn.
    - **category_id**: The ID of the category.
    """
    # The service layer now handles the HTTPException for not found items
    response = category_service.assign_category_to_hymn(db, hymn_id, category_id)
    return response