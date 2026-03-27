# PaddleOCR

Extracción de texto con OCR - API REST + Script CLI

## Stack

- **FastAPI** - API REST
- **PaddleOCR** - Motor OCR
- **uv** - Gestor de paquetes
- **Docker** - Contenedor

## Versiones

| Paquete | Versión |
|---------|---------|
| paddlepaddle | 3.2.2 |
| paddleocr | 3.3.3 |

## Uso con Docker

```bash
# Build
docker build -t paddle-ocr-api .

# Run
docker run -p 8000:8000 paddle-ocr-api
```

## Uso con Docker Compose

```bash
docker compose up
```

## Endpoints API

### Health Check

```bash
GET /health
```

### OCR Single Image

```bash
POST /ocr
Content-Type: multipart/form-data

curl -X POST "http://localhost:8000/ocr" -F "file=@imagen.png"
```

### OCR Batch (máx. 20 imágenes)

```bash
POST /ocr/batch
Content-Type: multipart/form-data

curl -X POST "http://localhost:8000/ocr/batch" \
  -F "files=@img1.png" -F "files=@img2.jpg"
```

## Respuesta API

```json
{
  "nombre_archivo": "imagen.png",
  "resultados": [
    {
      "texto": "Texto detectado",
      "confianza": 0.9982,
      "caja": [x1, y1, x2, y2]
    }
  ],
  "confianza_promedio": 0.9982
}
```

## Script CLI

```bash
# Una imagen
uv run --no-sync python ocr_proceso.py foto.png

# Varias imágenes
uv run --no-sync python ocr_proceso.py img1.png img2.jpg

# Carpeta
uv run --no-sync python ocr_proceso.py "./carpeta/"
```

## Desarrollo Local

```bash
uv pip install fastapi uvicorn python-multipart
uv pip install paddlepaddle==3.2.2 --index-url https://www.paddlepaddle.org.cn/packages/stable/cpu/
uv pip install paddleocr --index-url https://pypi.org/simple/
uv run uvicorn src.main:app --reload --port 8000
```
