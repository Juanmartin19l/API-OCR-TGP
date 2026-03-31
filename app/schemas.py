from pydantic import BaseModel, Field
from typing import List, Optional


class OCRResult(BaseModel):
    texto: str
    confianza: float
    caja: List[int]
    pagina: Optional[int] = None  # 1-indexed page number (None for single-image input)


class OCRResponse(BaseModel):
    nombre_archivo: str
    resultados: List[OCRResult]
    confianza_promedio: float
    total_paginas: int = Field(
        1, description="Número total de páginas procesadas (1 para imágenes)"
    )


class OCRBatchResponse(BaseModel):
    total_imagenes: int
    resultados_por_archivo: List[OCRResponse]
