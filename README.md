# Himnario Generator Backend

[![Build Status](https://img.shields.io/travis/com/your_username/your_repository.svg)](https://travis-ci.com/your_username/your_repository)
[![Coverage Status](https://img.shields.io/coveralls/github/your_username/your_repository.svg)](https://coveralls.io/github/your_username/your_repository?branch=main)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Este es el backend para el proyecto Himnario Generator. Es una API de FastAPI diseñada para extraer, gestionar y generar documentos de himnarios a partir de archivos PDF.

## Features

- **Extracción de Himnos desde PDF**: Sube un archivo PDF y extrae automáticamente los himnos, incluyendo número, título y contenido (estrofas y coros).
- **Procesamiento OCR de Dos Columnas**: La lógica de OCR está diseñada para manejar el formato de dos columnas de los himnarios para mantener el orden correcto.
- **Cache con Redis**: Almacena en caché los resultados de OCR para evitar el reprocesamiento de los mismos archivos PDF.
- **Gestión de Himnos**: Endpoints para listar, ver, crear, actualizar y eliminar himnos.
- **Gestión de Categorías**: Endpoints para gestionar las categorías de los himnos.
- **Generación de Documentos**: Funcionalidad para generar documentos (e.g., `.docx`) a partir de los himnos almacenados.
- **Acceso a Datos Moderno con SQLAlchemy**: Implementación de un ORM para interacciones con la base de datos más seguras, eficientes y legibles, resolviendo el problema N+1.
- **Gestión de Migraciones con Alembic**: Sistema robusto para gestionar cambios en el esquema de la base de datos.
- **Manejo de Errores Mejorado**: Implementación de excepciones personalizadas y manejadores globales para una gestión de errores consistente y clara.

## Instalación y Setup

Sigue estos pasos para configurar el entorno de desarrollo local.

### Prerrequisitos

- Python 3.9+
- PostgreSQL
- Redis
- Tesseract-OCR: [Guía de Instalación](https://tesseract-ocr.github.io/tessdoc/Installation.html)
- Poppler: Necesario para la conversión de PDF a imagen. [Guía para Windows](https://github.com/oschwartz10612/poppler-windows/releases/)

### Pasos

1.  **Clona el repositorio (si aplica):**
    ```bash
    git clone <repository_url>
    cd himanario-generator/backend
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura las variables de entorno:**
    - Crea un archivo `.env` en la raíz del directorio `backend`.
    - Copia el contenido de `.env.example` (si existe) o usa la siguiente plantilla:
      ```
      POSTGRES_DB=himnario_db
      POSTGRES_USER=postgres
      POSTGRES_PASSWORD=tu_contraseña
      REDIS_HOST=localhost
      REDIS_PORT=6379
      TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe" # Ajusta esta ruta
      POPPLER_PATH="C:\path\to\poppler\bin" # Ajusta esta ruta
      ```

5.  **Ejecuta las migraciones de la base de datos con Alembic:**
    Asegúrate de que tu base de datos PostgreSQL esté corriendo y que las credenciales en `.env` sean correctas.
    ```bash
    # Desde el directorio 'backend'
    alembic upgrade head
    ```

## Uso

Para iniciar la aplicación FastAPI, ejecuta el siguiente comando en la raíz del directorio `backend`:

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

La documentación interactiva de la API (Swagger UI) se encuentra en `http://127.0.0.1:8000/docs`.

## Comandos Útiles

- **Iniciar la aplicación**: `uvicorn main:app --reload`
- **Ejecutar tests**: `pytest`
- **Congelar dependencias**: `pip freeze > requirements.txt`
- **Generar nueva migración de Alembic**: `alembic revision --autogenerate -m "Descripción de la migración"`
- **Aplicar migraciones de Alembic**: `alembic upgrade head`
- **Ver estado de las migraciones de Alembic**: `alembic current`

## API Endpoints

A continuación se muestra un resumen de los endpoints disponibles. Para más detalles, consulta la documentación de Swagger en `/docs`.

- `GET /`: Mensaje de bienvenida.
- `POST /extract-hymns`: Sube un archivo PDF para extraer los himnos.
- `GET /hymns`: Lista todos los himnos.
- `GET /hymns/{hymn_id}`: Obtiene un himno específico.
- `GET /categories`: Lista todas las categorías.
- `POST /generator/docx`: Genera un documento `.docx` con los himnos seleccionados.