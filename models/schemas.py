from pydantic import BaseModel
from typing import List, Optional

# Schema for creating a new category (input)
class CategoryCreate(BaseModel):
    name: str

# Schema for representing a category (output)
class Category(CategoryCreate):
    id: int

    class Config:
        orm_mode = True

class ContentLine(BaseModel):
    id: int
    hymn_content_id: int
    line_text: str
    line_order: int

    class Config:
        orm_mode = True

class HymnContent(BaseModel):
    id: int
    hymn_id: int
    content_type: str
    stanza_number: Optional[int]
    content_order: int
    lines: List[ContentLine] = []

    class Config:
        orm_mode = True

class Hymn(BaseModel):
    id: int
    hymn_number: int
    title: str
    category_id: Optional[int]
    content: List[HymnContent] = []

    class Config:
        orm_mode = True

class GenerateDocxRequest(BaseModel):
    hymn_ids: List[int]
    file_name: str