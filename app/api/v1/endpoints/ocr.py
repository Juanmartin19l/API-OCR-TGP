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
    responses={
        400: {
            "description": "Bad Request - uno o varios archivos no válidos",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_files": {
                            "summary": "Ejemplo de error 400 por archivos inválidos",
                            "value": {
                                "detail": {
                                    "message": "Algunos archivos fallaron en el procesamiento",
                                    "failed_files": [
                                        {
                                            "nombre_archivo": "doc1.txt",
                                            "error_code": "invalid_format",
                                            "error_message": "Formato no soportado. Vuelva a subir un archivo con extensión png, jpg, jpeg, bmp, gif o pdf.",
                                        }
                                    ],
                                    "total_processed": 0,
                                    "total_failed": 1,
                                }
                            },
                        }
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - fallo en el procesamiento de uno o varios archivos",
            "content": {
                "application/json": {
                    "examples": {
                        "processing_error": {
                            "summary": "Ejemplo de error 500 por fallo interno",
                            "value": {
                                "detail": {
                                    "message": "Algunos archivos fallaron en el procesamiento",
                                    "failed_files": [
                                        {
                                            "nombre_archivo": "doc2.pdf",
                                            "error_code": "processing_error",
                                            "error_message": "Se produjo un error al procesar este archivo. Por favor vuelva a subirlo.",
                                        }
                                    ],
                                    "total_processed": 0,
                                    "total_failed": 1,
                                }
                            },
                        }
                    }
                }
            },
        },
    },
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

    failed = [i for i in resultados if not i.ok]
    if failed:
        has_processing_error = any(f.error_code == "processing_error" for f in failed)
        status_code = 500 if has_processing_error else 400
        detalle = {
            "message": "Algunos archivos fallaron en el procesamiento",
            "failed_files": [
                {
                    "nombre_archivo": f.nombre_archivo,
                    "error_code": f.error_code,
                    "error_message": f.error_message,
                }
                for f in failed
            ],
            "total_processed": len(resultados) - len(failed),
            "total_failed": len(failed),
        }
        raise HTTPException(status_code=status_code, detail=detalle)

    return {"total_imagenes": len(resultados), "resultados_por_archivo": resultados}
