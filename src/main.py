import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from src.models import OCRResponse, OCRBatchResponse, OCRResult
from src.ocr_service import ocr_service


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="PaddleOCR API",
    description="API para extracción de texto con OCR",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/ocr", response_model=OCRResponse)
async def ocr_single(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó archivo")

    ext = Path(file.filename).suffix.lower()
    if ext not in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]:
        raise HTTPException(
            status_code=400,
            detail="Formato no soportado. Use: png, jpg, jpeg, bmp, gif",
        )

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename

    try:
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)

        datos = ocr_service.process_image(str(filepath))

        resultados = [
            OCRResult(texto=r["texto"], confianza=r["confianza"], caja=r["caja"])
            for r in datos["resultados"]
        ]

        return OCRResponse(
            nombre_archivo=file.filename,
            resultados=resultados,
            confianza_promedio=datos["confianza_promedio"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if filepath.exists():
            os.remove(filepath)


@app.post("/ocr/batch", response_model=OCRBatchResponse)
async def ocr_batch(files: list[UploadFile] = File(...)):
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Máximo 20 archivos por request")

    resultados_por_archivo = []

    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]:
            continue

        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = UPLOAD_DIR / filename

        try:
            with open(filepath, "wb") as f:
                content = await file.read()
                f.write(content)

            datos = ocr_service.process_image(str(filepath))

            resultados = [
                OCRResult(texto=r["texto"], confianza=r["confianza"], caja=r["caja"])
                for r in datos["resultados"]
            ]

            resultados_por_archivo.append(
                OCRResponse(
                    nombre_archivo=file.filename,
                    resultados=resultados,
                    confianza_promedio=datos["confianza_promedio"],
                )
            )

        except Exception:
            continue

        finally:
            if filepath.exists():
                os.remove(filepath)

    return OCRBatchResponse(
        total_imagenes=len(resultados_por_archivo),
        resultados_por_archivo=resultados_por_archivo,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
