from fastapi import APIRouter, Depends
from typing import List
from ..models import schemas
from ..services import hymn_service
from psycopg2.extensions import connection
from ..database import get_db_connection

router = APIRouter()

@router.get("/hymns", response_model=List[schemas.Hymn])
def read_hymns(db: connection = Depends(get_db_connection)):
    return hymn_service.get_hymns(db)

@router.get("/hymns/{hymn_id}", response_model=schemas.Hymn)
def read_hymn(hymn_id: int, db: connection = Depends(get_db_connection)):
    return hymn_service.get_hymn(db, hymn_id)
