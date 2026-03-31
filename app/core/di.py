from functools import lru_cache
from app.services.ocr_service import OCRService
from app.core.config import get_settings


@lru_cache()
def get_ocr_service() -> OCRService:
    settings = get_settings()
    return OCRService(lang=settings.OCR_MODEL_LANG)
