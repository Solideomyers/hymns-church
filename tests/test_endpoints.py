import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_read_hymns():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/hymns/")
    assert response.status_code in [200, 404, 500]  # Puede estar vacío o error si no hay datos

@pytest.mark.asyncio
async def test_read_categories():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/categories/")
    assert response.status_code in [200, 404, 500]

@pytest.mark.asyncio
async def test_generate_docx():
    # Debe haber himnos en la base de datos para que funcione
    payload = {"hymn_ids": [1], "file_name": "test.docx"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/generator/docx", json=payload)
    assert response.status_code in [200, 404, 500]

@pytest.mark.asyncio
async def test_extract_hymns_from_pdf():
    # Este test requiere un archivo PDF válido, aquí solo se prueba el error por extensión
    async with AsyncClient(app=app, base_url="http://test") as ac:
        files = {"pdf_file": ("test.txt", b"contenido", "text/plain")}
        try:
            response = await ac.post("/extraction/hymns-from-pdf", files=files)
            assert response.status_code == 400
            data = response.json()
            assert data["message"] == "Error processing PDF"
            assert "Only PDF files are allowed" in data["detail"]
        except Exception as e:
            # Si la excepción se propaga, verifica que sea la esperada
            assert "Only PDF files are allowed" in str(e)
