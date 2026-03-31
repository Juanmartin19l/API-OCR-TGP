from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import get_settings
from app.core.di import get_ocr_service
from app.api.v1.router import api_router
from scalar_fastapi import get_scalar_api_reference
from fastapi import FastAPI

settings = get_settings()
ocr_service = get_ocr_service()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cargar modelo OCR en startup
    await ocr_service.load()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="OCR API", version="1.0.0", lifespan=lifespan)
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/scalar", include_in_schema=False)
    def get_scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url, title="OCR API Documentation"
        )

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()
