from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from services.admin_service import reset_database

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

@router.post("/reset-db", status_code=status.HTTP_200_OK, summary="Resetear la base de datos", description="Elimina todos los datos de himnos, contenidos y categorías. Solo para uso administrativo.")
def reset_db_endpoint(db: Session = Depends(get_db)):
    return reset_database(db)
