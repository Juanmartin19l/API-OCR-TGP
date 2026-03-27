from pydantic import BaseModel


class OCRResult(BaseModel):
    texto: str
    confianza: float
    caja: list[int]


class OCRResponse(BaseModel):
    nombre_archivo: str
    resultados: list[OCRResult]
    confianza_promedio: float


class OCRBatchResponse(BaseModel):
    total_imagenes: int
    resultados_por_archivo: list[OCRResponse]
