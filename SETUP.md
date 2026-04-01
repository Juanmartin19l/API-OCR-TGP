## PaddleOCR — Instalación y ejecución

### Requisitos

- Python 3.10 o superior
- Acceso a Internet para la descarga de dependencias y modelos

### Instalación (entorno virtual)

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate     # Windows (PowerShell)
uv pip install --upgrade pip
uv pip install -r requirements.txt
```

Si no dispone de `requirements.txt`, instalar dependencias mínimas:

```bash
uv pip install fastapi uvicorn python-multipart
uv pip install paddlepaddle==3.2.2 --index-url https://www.paddlepaddle.org.cn/packages/stable/cpu/
uv pip install paddleocr
```

### Ejecutar (local)

```bash
uv run uvicorn app.main:app --reload --port 8000
``` 

### Uso de la CLI (scripts locales)

```bash
# Procesar una imagen
python ocr_proceso.py imagen.png

# Procesar varias imágenes
python ocr_proceso.py img1.png img2.jpg

# Procesar una carpeta
python ocr_proceso.py "./fotos/"
```

### Salida

Los resultados se registran en salida estándar y, según la configuración, pueden guardarse en `output/`.

### Resolución de problemas

- Error relacionado con dependencias nativas: instale paquetes requeridos para su plataforma (por ejemplo `libjpeg`, `zlib`).
- Problemas con GPU/CUDA: asegúrese de instalar la versión de PaddlePaddle compatible con GPU y que los drivers estén instalados.
- Modelos: la descarga del modelo puede tardar en la primera ejecución (descarga automática, ~200MB).
