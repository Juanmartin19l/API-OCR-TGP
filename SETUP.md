# PaddleOCR - Setup y Ejecución

## Requisitos

- Python 3.10+
- Windows
- uv (gestor de paquetes)

## Instalación

```bash
# Instalar PaddlePaddle CPU
uv pip install paddlepaddle==3.2.0 --index-url https://www.paddlepaddle.org.cn/packages/stable/cpu/

# Instalar PaddleOCR
uv pip install paddleocr --index-url https://pypi.org/simple/
```

## Ejecución

```bash
uv run --no-sync python ocr_proceso.py <ruta_imagen>
```

Ejemplo:
```bash
uv run --no-sync python ocr_proceso.py "C:\fotos\documento.png"
```

## Solución de Problemas

| Problema | Solución |
|----------|----------|
| Error Shapely | `uv pip install shapely` |
| Modelos lentos | Los modelos se descargan automáticamente en el primer uso (~200MB) |
| Error GPU/CUDA | Asegurarse de usar `device='cpu'` en el script |
