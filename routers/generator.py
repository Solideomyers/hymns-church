from fastapi import APIRouter, Depends
from ..services import generator_service

router = APIRouter()

@router.post("/generate-hymnary")
def generate_hymnary():
    return generator_service.generate_hymnary()
