from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.di import get_ocr_service
from app.api.v1.router import api_router
from scalar_fastapi import get_scalar_api_reference

settings = get_settings()
ocr_service = get_ocr_service()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cargar modelo OCR en startup
    await ocr_service.load()
    yield


def create_app() -> FastAPI:
    tags_metadata = [
        {
            "name": "ocr",
            "description": "Endpoints para subir archivos y obtener resultados OCR",
        }
    ]

    app = FastAPI(
        title="OCR API",
        version="1.0.0",
        description=(
            "API para extraer texto de imágenes y PDFs usando PaddleOCR. \n"
            "Soporta subida de múltiples archivos y devuelve un resultado por archivo."
        ),
        lifespan=lifespan,
        openapi_tags=tags_metadata,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/scalar", include_in_schema=False)
    def get_scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url, title="OCR API Documentation"
        )

    return app


app = create_app()
