# AGENTS.md - Agent Coding Guidelines

## Project Overview

FastAPI-based OCR API that extracts text from images and PDFs using PaddleOCR. Provides a REST endpoint for processing multiple files with detailed results.

## Tech Stack

- **Python 3.12** (required), **FastAPI**, **PaddleOCR**, **Pydantic**, **uv**

## Build & Run Commands

```bash
# Install & run dev server
python -m venv .venv && source .venv/bin/activate
pip install uv && uv sync
uv run uvicorn app.main:app --reload --port 8000

# Docker
docker build -t paddle-ocr-api . && docker run -p 8000:8000 paddle-ocr-api
docker compose up --build
```

## Testing

**No test framework configured yet.** When adding tests:

```bash
pytest                          # Run all tests
pytest tests/test_ocr.py       # Run single test file
pytest tests/test_ocr.py::test_process_image  # Run single test function
```

## Code Style Guidelines

### General
- Python 3.12+ syntax, follow PEP 8 with 100-char line limit
- No comments unless explaining complex logic
- Use English for code, Spanish for user-facing strings (e.g., `texto`, `confianza`)

### Imports Order
1. Standard library (`io`, `asyncio`, `typing`)
2. Third-party (`fastapi`, `paddleocr`, `pydantic`)
3. Local app (`app.core.config`, `app.services.ocr_service`)

### Type Hints
- Use native Python 3.12+ syntax, include return types
- Use `Optional[X]` over `X | None`, `list[X]` not `List[X]`

### Naming
- Variables/functions: `snake_case`, Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`, Private methods: `_private_method`

### Pydantic Schemas
```python
class OCRResult(BaseModel):
    texto: str
    confianza: float
    caja: List[int]
    pagina: Optional[int] = None
```

### Error Handling
- Use try/except with specific exceptions, avoid bare `except:`
- Use HTTPException for API errors

### Async Patterns
- Use `async def` for endpoints, wrap blocking code with `asyncio.to_thread()`
- Initialize heavy resources (OCR model) in lifespan startup

## Project Structure

```
app/
├── main.py              # FastAPI app factory
├── schemas.py           # Pydantic models
├── core/
│   ├── config.py       # Settings (pydantic-settings)
│   └── di.py           # Dependency injection (lru_cache)
├── services/
│   └── ocr_service.py  # OCR business logic
└── api/v1/
    ├── router.py
    ├── endpoints/ocr.py
    └── services/ocr_helpers.py
```

## Configuration Pattern

```python
class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    OCR_MODEL_LANG: str = "es"
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

## Dependency Injection

```python
@lru_cache()
def get_ocr_service() -> OCRService:
    return OCRService(lang=get_settings().OCR_MODEL_LANG)

async def upload_files(files: list[UploadFile] = File(...), ocr: OCRService = Depends(get_ocr_service)):
    ...
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Scalar: `http://localhost:8000/scalar`

## Important Notes

1. **Model Loading**: PaddleOCR loads async on startup (several seconds first run)
2. **Supported Formats**: PNG, JPG, JPEG, BMP, GIF, PDF
3. **Max Files**: 10 per request (configurable in `app/api/v1/endpoints/ocr.py`)
4. **Fail-Fast**: Returns HTTP 400/500 if any file fails