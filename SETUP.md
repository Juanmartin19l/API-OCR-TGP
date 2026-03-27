# PaddleOCR - Setup y Ejecución

## Requisitos

- Python 3.10+
- Windows
- uv (gestor de paquetes)

## Instalación

```bash
# Instalar dependencias
uv pip install paddlepaddle==3.2.2 --index-url https://www.paddlepaddle.org.cn/packages/stable/cpu/
uv pip install "paddleocr>=3.3.0" --index-url https://pypi.org/simple/
```

## Versiones

| Paquete      | Versión |
| ------------ | ------- |
| paddlepaddle | 3.2.2   |
| paddleocr    | 3.3.3   |

## Ejecución

```bash
# Una imagen
uv run --no-sync python ocr_proceso.py imagen.png

# Varias imágenes
uv run --no-sync python ocr_proceso.py img1.png img2.jpg img3.png

# Carpeta completa
uv run --no-sync python ocr_proceso.py "./fotos/"
```

## Salida

Los resultados JSON se guardan en la carpeta `output/`.

## Solución de Problemas

| Problema       | Solución                                                           |
| -------------- | ------------------------------------------------------------------ |
| Error Shapely  | `uv pip install shapely`                                           |
| Modelos lentos | Los modelos se descargan automáticamente en el primer uso (~200MB) |
| Error GPU/CUDA | Asegurarse de usar `device='cpu'` en el script                     |
