from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from routers import hymns, categories, generator, extraction, admin
from database import create_tables
from core.exceptions import HimnarioGeneratorException, PdfProcessingError, DatabaseError, HymnNotFoundError

app = FastAPI(
    title="Himnario Generator API",
    description="API for extracting, managing, and generating hymnaries from PDF files.",
    version="1.0.0",
)

# Exception Handlers
@app.exception_handler(HimnarioGeneratorException)
async def himnario_generator_exception_handler(request: Request, exc: HimnarioGeneratorException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An internal server error occurred", "detail": exc.detail},
    )

@app.exception_handler(PdfProcessingError)
async def pdf_processing_error_handler(request: Request, exc: PdfProcessingError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Error processing PDF", "detail": exc.detail},
    )

@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "A database error occurred", "detail": exc.detail},
    )

@app.exception_handler(HymnNotFoundError)
async def hymn_not_found_error_handler(request: Request, exc: HymnNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Hymn not found", "detail": exc.detail},
    )


# Usar el nuevo manejador de eventos lifespan
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(
    title="Himnario Generator API",
    description="API for extracting, managing, and generating hymnaries from PDF files.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(hymns.router)
app.include_router(categories.router)
app.include_router(generator.router)
app.include_router(extraction.router)
app.include_router(admin.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to the Himnario API"}