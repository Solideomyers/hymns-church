# Himnario Generator Project Flow

## 1. Carga y Extracción de Himnos

- **Inicio:** Usuario sube un archivo PDF (API: `POST /extraction/hymns-from-pdf`)
  - **Validación:** El router valida el tipo de archivo (PDF).
  - **Servicio de Extracción (`extraction_service`):**
    - **Verificación de Dependencias:** Comprueba Tesseract y Poppler.
    - **Caché de OCR:** Verifica si el texto del PDF ya está en caché (Redis).
    - **Extracción de Texto:**
      - Intenta extracción directa (`pdfminer.six`).
      - Si falla o está vacío, realiza OCR (Tesseract) en imágenes de página (soporte a dos columnas).
    - **Parseo de Himnos (`hymn_parser`):** El texto extraído se parsea para identificar himnos, títulos, estrofas y coros.
    - **Almacenamiento en BD (`hymn_service`):**
      - Los datos parseados se envían a `hymn_service.create_or_update_hymns_from_parsed_data`.
      - **Lógica de Upsert:** Busca himnos existentes por número; actualiza o crea nuevos.
      - Guarda contenido (estrofas, coros, líneas) asociado a cada himno.
      - Invalida cachés relevantes.
- **Fin:** Confirmación de extracción exitosa.

## 2. Consulta de Himnos y Categorías

- **Inicio:** Usuario solicita himnos (API: `GET /hymns`, `GET /hymns/{id}`) o categorías (API: `GET /categories`)
  - **Router:** Recibe la petición y delega al servicio correspondiente.
  - **Servicio (`hymn_service` o `category_service`):**
    - **Caché:** Intenta obtener los datos de Redis.
    - **Base de Datos:** Si no está en caché, consulta la base de datos usando SQLAlchemy ORM.
    - **Mapeo:** Mapea los objetos ORM a esquemas Pydantic.
    - **Caché:** Almacena los resultados en caché para futuras peticiones.
- **Fin:** Retorna los datos solicitados.

## 3. Generación de Documentos DOCX

- **Inicio:** Usuario solicita generar un DOCX (API: `POST /generator/docx`)
  - **Router:** Recibe la petición con IDs de himnos y nombre de archivo.
  - **Servicio de Generación (`generator_service`):**
    - **Consulta de Himnos:** Obtiene los himnos completos de la base de datos usando SQLAlchemy ORM.
    - **Creación de Documento:** Utiliza `python-docx` para construir el documento DOCX.
    - **Guardar Archivo:** Guarda el documento generado en un directorio temporal.
- **Fin:** Retorna el archivo DOCX como respuesta HTTP.

## 4. Manejo de Errores Global

- **Inicio:** Se produce una excepción en cualquier capa de la aplicación.
  - **Excepciones Personalizadas:** Los servicios lanzan excepciones personalizadas (`PdfProcessingError`, `DatabaseError`, `HymnNotFoundError`, etc.).
  - **Manejadores Globales (`main.py`):** FastAPI intercepta estas excepciones.
  - **Respuesta HTTP:** Los manejadores transforman la excepción en una respuesta HTTP adecuada (ej. 400 Bad Request, 404 Not Found, 500 Internal Server Error) con un mensaje detallado.
- **Fin:** Usuario recibe una respuesta de error clara.