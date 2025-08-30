from fastapi import FastAPI
from .routers import hymns, categories, generator, extraction
from .database import initialize_db_pool, close_db_pool

app = FastAPI(
    title="Himnario Generator API",
    description="API for extracting, managing, and generating hymnaries from PDF files.",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    initialize_db_pool()

@app.on_event("shutdown")
async def shutdown_event():
    close_db_pool()

app.include_router(hymns.router)
app.include_router(categories.router)
app.include_router(generator.router)
app.include_router(extraction.router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to the Himnario API"}