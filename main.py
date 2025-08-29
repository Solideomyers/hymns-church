from fastapi import FastAPI
from .routers import hymns, categories, generator

app = FastAPI()

app.include_router(hymns.router)
app.include_router(categories.router)
app.include_router(generator.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Himnario API"}
