class HimnarioGeneratorException(Exception):
    """Base exception class for this application."""
    def __init__(self, detail: str = None):
        self.detail = detail or "An unexpected error occurred in the Himnario Generator application."
        super().__init__(self.detail)

class PdfProcessingError(HimnarioGeneratorException):
    """Raised when an error occurs during PDF processing or OCR."""
    def __init__(self, detail: str = "Error processing the PDF file."):
        super().__init__(detail)

class DatabaseError(HimnarioGeneratorException):
    """Raised for database-related errors."""
    def __init__(self, detail: str = "A database error occurred."):
        super().__init__(detail)

class HymnNotFoundError(DatabaseError):
    """Raised when a specific hymn is not found."""
    def __init__(self, hymn_id: int):
        super().__init__(detail=f"Hymn with id {hymn_id} not found.")

class CategoryNotFoundError(DatabaseError):
    """Raised when a specific category is not found."""
    def __init__(self, category_id: int):
        super().__init__(detail=f"Category with id {category_id} not found.")