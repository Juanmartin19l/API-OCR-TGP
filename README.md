# PaddleOCR - Extracción de Texto con OCR

Script de Python para extraer texto de imágenes usando PaddleOCR, optimizado para español y CPU.

## Características

- Reconocimiento OCR en español (modelo `latin_PP-OCRv5_mobile_rec`)
- Procesamiento paralelo de múltiples imágenes
- Extracción de texto, bounding boxes y confianza
- Salida en JSON estructurada
- Optimizado para CPU (sin GPU)

## Estructura

```terminal
paddle/
├── ocr_proceso.py    # Script principal
├── output/           # Resultados JSON
├── SETUP.md          # Instrucciones de instalación
└── README.md         # Este archivo
```

## Uso

```bash
# Una imagen
python ocr_proceso.py foto.png

# Varias imágenes
python ocr_proceso.py img1.png img2.jpg

# Carpeta completa
python ocr_proceso.py "./carpeta/"
```

## Salida JSON

```json
{
  "imagen": "ruta/a/imagen.png",
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

## Dependencias

- Python 3.10+
- paddlepaddle==3.2.2
- paddleocr>=3.3.0

Ver `SETUP.md` para instrucciones de instalación.
