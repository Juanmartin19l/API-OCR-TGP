# OCR API (PaddleOCR)

API REST para extracción de texto a partir de imágenes y PDFs usando PaddleOCR. Proporciona un endpoint HTTP para procesar uno o varios archivos y devuelve resultados estructurados por archivo. Está diseñada para integrarse con otros servicios y para operaciones por lotes.

Características principales

- Endpoint unificado para subida de archivos (soporta múltiples archivos multipart/form-data).
- Procesamiento por archivo con respuesta detallada en caso de error.
- Modo fail-fast: si algún archivo falla durante el procesamiento la API retorna un error (HTTP 400 o 500) con detalle de los archivos fallidos.
- Documentación OpenAPI disponible en /docs (Swagger UI) y /redoc.

Requisitos

- Python 3.10 o superior
- Docker (opcional)

Instalación rápida (entorno virtual)

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate     # Windows (PowerShell)
pip install --upgrade pip
pip install fastapi uvicorn python-multipart
# Instalar PaddlePaddle (CPU) y PaddleOCR, ajustar según plataforma
pip install paddlepaddle==3.2.2 --index-url https://www.paddlepaddle.org.cn/packages/stable/cpu/
pip install paddleocr
```

Ejecución local

```bash
uvicorn app.main:app --reload --port 8000
# Documentación: http://127.0.0.1:8000/docs (Swagger) /redoc (Redoc)
```

Uso con Docker

```bash
docker build -t paddle-ocr-api .
docker run -p 8000:8000 paddle-ocr-api
```

Uso con Docker Compose

```bash
docker compose up --build
```

Endpoints principales

- GET /health
  - Health check simple que devuelve {"status": "healthy"}.
- POST /api/v1/ocr/upload
  - Descripción: sube uno o varios archivos en multipart/form-data.
  - Campo: files (array de archivos)
  - Respuesta 200: OCRBatchResponse cuando todos los archivos se procesan correctamente.
  - Respuesta 400/500: en caso de fallos (fail-fast). El body de error incluye detalle.failed_files con información por archivo.

Ejemplo de uso (curl)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ocr/upload" \
  -F "files=@doc1.png" -F "files=@doc2.pdf"
```

Ejemplo de respuesta exitosa (parcializado)

```json
{
  "total_imagenes": 1,
  "resultados_por_archivo": [
    {
      "nombre_archivo": "doc1.png",
      "ok": true,
      "resultado": {
        "nombre_archivo": "doc1.png",
        "resultados": [
          { "texto": "Texto detectado", "confianza": 0.9982, "caja": [0,0,100,20], "pagina": 1 }
        ],
        "confianza_promedio": 0.9982,
        "total_paginas": 1
      },
      "error_code": null,
      "error_message": null
    }
  ]
}
```

Ejemplo de error (fail-fast)

```json
{
  "detail": {
    "message": "Algunos archivos fallaron en el procesamiento",
    "failed_files": [
      { "nombre_archivo": "doc2.pdf", "error_code": "processing_error", "error_message": "Se produjo un error al procesar este archivo. Por favor vuelva a subirlo." }
    ],
    "total_processed": 0,
    "total_failed": 1
  }
}
```

Contribuir

1. Abrir un issue describiendo el cambio o bug.
2. Crear una rama con un nombre descriptivo.
3. Enviar un pull request con descripción y pruebas (si procede).

Licencia

Este proyecto se entrega bajo la licencia MIT.
