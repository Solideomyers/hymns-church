from fastapi import APIRouter, Depends
from typing import List
from ..models import schemas
from ..services import category_service
from psycopg2.extensions import connection
from ..database import get_db_connection

router = APIRouter()

@router.get("/categories", response_model=List[schemas.Category])
def read_categories(db: connection = Depends(get_db_connection)):
    return category_service.get_categories(db)

@router.post("/categories", response_model=schemas.Category)
def create_category(category: schemas.Category, db: connection = Depends(get_db_connection)):
    return category_service.create_category(db, category)

@router.put("/hymns/{hymn_id}/category")
def assign_category_to_hymn(hymn_id: int, category_id: int, db: connection = Depends(get_db_connection)):
    return category_service.assign_category_to_hymn(db, hymn_id, category_id)
