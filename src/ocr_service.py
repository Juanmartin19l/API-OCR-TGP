import os
import uuid
from pathlib import Path

from paddleocr import PaddleOCR


class OCRService:
    _instance = None
    _ocr = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._ocr is None:
            self._ocr = PaddleOCR(
                lang="es",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                device="cpu",
            )

    def process_image(self, image_path: str) -> dict:
        result = self._ocr.predict(image_path)

        datos = {"resultados": []}

        for res in result:
            for text, score, box in zip(
                res["rec_texts"], res["rec_scores"], res["rec_boxes"]
            ):
                datos["resultados"].append(
                    {
                        "texto": text,
                        "confianza": round(float(score), 4),
                        "caja": [int(float(c)) for c in box],
                    }
                )

        confianzas = [r["confianza"] for r in datos["resultados"]]
        datos["confianza_promedio"] = (
            round(sum(confianzas) / len(confianzas), 4) if confianzas else 0.0
        )

        return datos


ocr_service = OCRService()
