import json
from pathlib import Path

from paddleocr import PaddleOCR


def procesar_imagen(ruta_imagen: str, lang: str = "es"):
    ocr = PaddleOCR(
        lang=lang,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        device="cpu",
    )

    result = ocr.predict(ruta_imagen)

    imagen_path = Path(ruta_imagen)
    output_path = imagen_path.with_suffix(".json")

    datos = {"imagen": str(imagen_path.absolute()), "resultados": []}

    for res in result:
        texts = res["rec_texts"]
        scores = res["rec_scores"]
        boxes = res["rec_boxes"]

        if not texts:
            print("No se detectó texto en la imagen.")
            return datos

        for text, score, box in zip(texts, scores, boxes):
            datos["resultados"].append(
                {
                    "texto": text,
                    "confianza": round(float(score), 4),
                    "caja": [int(float(c)) for c in box],
                }
            )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

    print(f"Resultados guardados en: {output_path}")
    return datos


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python ocr_proceso.py <ruta_imagen>")
        sys.exit(1)

    datos = procesar_imagen(sys.argv[1])
    print(json.dumps(datos, indent=2, ensure_ascii=False))
