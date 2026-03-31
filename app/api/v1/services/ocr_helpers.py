import logging
from fastapi import UploadFile
from typing import Optional
from app.services.ocr_service import OCRService
from app.models import OCRResponse, OCRResult, OCRBatchItem

logger = logging.getLogger(__name__)

VALID_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf"}


def _format_ocr_response(file_name: str, datos: dict) -> OCRResponse:
    resultados = [
        OCRResult(
            texto=r["texto"],
            confianza=r["confianza"],
            caja=r["caja"],
            pagina=r.get("pagina"),
        )
        for r in datos.get("resultados", [])
    ]
    return OCRResponse(
        nombre_archivo=file_name,
        resultados=resultados,
        confianza_promedio=datos.get("confianza_promedio", 0.0),
        total_paginas=datos.get("total_paginas", 1),
    )


async def process_single_file(file: UploadFile, ocr: OCRService) -> OCRBatchItem:
    # Validaciones básicas
    if not file.filename:
        return OCRBatchItem(
            nombre_archivo="",
            ok=False,
            error_code="missing_filename",
            error_message="El archivo no tiene nombre; suba el archivo de nuevo con un nombre válido.",
        )

    ext = "." + file.filename.split(".")[-1].lower()
    if ext not in VALID_EXTS:
        return OCRBatchItem(
            nombre_archivo=file.filename,
            ok=False,
            error_code="invalid_format",
            error_message=(
                "Formato no soportado. Vuelva a subir un archivo con extensión png, jpg, "
                "jpeg, bmp, gif o pdf."
            ),
        )

    try:
        content = await file.read()
        datos = await ocr.process_image(content)
        ocr_resp = _format_ocr_response(file.filename, datos)
        return OCRBatchItem(nombre_archivo=file.filename, ok=True, resultado=ocr_resp)
    except ValueError as ve:
        logger.exception("ValueError procesando archivo %s", file.filename)
        return OCRBatchItem(
            nombre_archivo=file.filename,
            ok=False,
            error_code="invalid_file",
            error_message=str(ve) or "Archivo inválido. Intente subirlo de nuevo.",
        )
    except Exception:
        logger.exception("Error procesando archivo %s", file.filename)
        return OCRBatchItem(
            nombre_archivo=file.filename,
            ok=False,
            error_code="processing_error",
            error_message=(
                "Se produjo un error al procesar este archivo. Por favor vuelva a subirlo."
            ),
        )
