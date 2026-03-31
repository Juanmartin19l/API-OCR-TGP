from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.di import get_ocr_service
from app.services.ocr_service import OCRService
from app.models import OCRBatchResponse
from app.api.v1.services.ocr_helpers import process_single_file

router = APIRouter()


# Configurable máximo de archivos por petición. Cambiar a None para sin límite.
MAX_FILES = 10


@router.post(
    "/upload",
    response_model=OCRBatchResponse,
    summary="Procesar uno o varios archivos para OCR",
    description=(
        "Acepta uno o varios archivos (imágenes o PDFs). Devuelve siempre un objeto "
        "con total_imagenes y resultados_por_archivo. Extensiones soportadas: "
        "png, jpg, jpeg, bmp, gif, pdf."
    ),
    operation_id="upload_files",
    tags=["ocr"],
)
async def upload_files(
    files: list[UploadFile] = File(...), ocr: OCRService = Depends(get_ocr_service)
):
    if not files:
        raise HTTPException(status_code=400, detail="No se proporcionó ningún archivo")

    if MAX_FILES is not None and len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400, detail=f"Máximo {MAX_FILES} archivos por request"
        )

    resultados = []
    for file in files:
        item = await process_single_file(file, ocr)
        resultados.append(item)

    return {"total_imagenes": len(resultados), "resultados_por_archivo": resultados}
