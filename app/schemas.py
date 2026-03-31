from pydantic import BaseModel, Field
from typing import List, Optional


class OCRResult(BaseModel):
    texto: str
    confianza: float
    caja: List[int]
    pagina: Optional[int] = None


class OCRResponse(BaseModel):
    nombre_archivo: str
    resultados: List[OCRResult]
    confianza_promedio: float
    total_paginas: int = Field(
        1, description="Número total de páginas procesadas (1 para imágenes)"
    )


class OCRBatchItem(BaseModel):
    nombre_archivo: str
    ok: bool = Field(..., description="True si el archivo se procesó correctamente")
    resultado: Optional[OCRResponse] = None
    error_code: Optional[str] = Field(
        None,
        description="Código corto del error (ej. invalid_format, processing_error)",
    )
    error_message: Optional[str] = Field(
        None, description="Mensaje legible para el usuario con la acción sugerida"
    )


class OCRBatchResponse(BaseModel):
    total_imagenes: int
    resultados_por_archivo: List[OCRBatchItem]
