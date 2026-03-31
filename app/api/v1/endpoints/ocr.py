from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.di import get_ocr_service
from app.services.ocr_service import OCRService
from app.models import OCRResponse, OCRResult

router = APIRouter()


@router.post("/upload", response_model=OCRResponse)
async def recognize(
    file: UploadFile = File(...), ocr: OCRService = Depends(get_ocr_service)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó archivo")

    ext = file.filename.split(".")[-1].lower()
    if f".{ext}" not in [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Formato no soportado. Use: png, jpg, jpeg, bmp, gif, pdf",
        )

    try:
        content = await file.read()
        datos = await ocr.process_image(content)

        resultados = [
            OCRResult(
                texto=r["texto"],
                confianza=r["confianza"],
                caja=r["caja"],
                pagina=r.get("pagina"),
            )
            for r in datos["resultados"]
        ]

        return OCRResponse(
            nombre_archivo=file.filename,
            resultados=resultados,
            confianza_promedio=datos["confianza_promedio"],
            total_paginas=datos.get("total_paginas", 1),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/batch", response_model=dict)
async def recognize_batch(
    files: list[UploadFile] = File(...), ocr: OCRService = Depends(get_ocr_service)
):
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Máximo 20 archivos por request")

    resultados_por_archivo = []

    for file in files:
        ext = file.filename.split(".")[-1].lower()
        if f".{ext}" not in [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf"]:
            continue

        try:
            content = await file.read()
            datos = await ocr.process_image(content)

            resultados = [
                {
                    "texto": r["texto"],
                    "confianza": r["confianza"],
                    "caja": r["caja"],
                    "pagina": r.get("pagina"),
                }
                for r in datos["resultados"]
            ]

            resultados_por_archivo.append(
                {
                    "nombre_archivo": file.filename,
                    "resultados": resultados,
                    "confianza_promedio": datos["confianza_promedio"],
                    "total_paginas": datos.get("total_paginas", 1),
                }
            )
        except Exception:
            continue

    return {
        "total_imagenes": len(resultados_por_archivo),
        "resultados_por_archivo": resultados_por_archivo,
    }
