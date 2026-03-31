import io
import asyncio
from typing import List, Optional

from paddleocr import PaddleOCR
from PIL import Image
import numpy as np

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None


class OCRService:
    """Async OCR service wrapper that processes bytes (images or PDFs).

    Use load() on startup to initialize PaddleOCR.
    """

    def __init__(self, lang: str = "es"):
        self.lang = lang
        self._ocr = None

    async def load(self) -> None:
        if self._ocr is None:

            def _build():
                return PaddleOCR(
                    lang=self.lang,
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False,
                    use_textline_orientation=False,
                    device="cpu",
                )

            self._ocr = await asyncio.to_thread(_build)

    async def _pdf_bytes_to_pil_images(
        self, pdf_bytes: bytes, scale: float = 2.0
    ) -> List[Image.Image]:
        if fitz is None:
            raise RuntimeError(
                "PyMuPDF (pymupdf) no está instalado. Instálalo para soportar PDF."
            )

        def _render_all():
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            images: List[Image.Image] = []
            mat = fitz.Matrix(scale, scale)
            for page_index in range(doc.page_count):
                page = doc.load_page(page_index)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                w, h = pix.width, pix.height
                mode = "RGB"
                img = Image.frombytes(mode, (w, h), pix.samples)
                images.append(img)
            return images

        return await asyncio.to_thread(_render_all)

    async def _image_bytes_to_pil(self, image_bytes: bytes) -> Image.Image:
        def _open():
            return Image.open(io.BytesIO(image_bytes)).convert("RGB")

        return await asyncio.to_thread(_open)

    async def process_image(self, image_bytes: bytes) -> dict:
        if self._ocr is None:
            raise RuntimeError(
                "OCR modelo no cargado. Llama a await ocr_service.load() en startup."
            )

        is_pdf = image_bytes[:4] == b"%PDF"

        if is_pdf:
            pil_images = await self._pdf_bytes_to_pil_images(image_bytes)
        else:
            pil_images = [await self._image_bytes_to_pil(image_bytes)]

        datos = {"resultados": []}

        def _predict(img_arr: np.ndarray):
            if hasattr(self._ocr, "predict"):
                return self._ocr.predict(img_arr)
            if hasattr(self._ocr, "ocr"):
                return self._ocr.ocr(img_arr, cls=False)
            raise RuntimeError("El objeto PaddleOCR no tiene 'predict' ni 'ocr'")

        for page_idx, pil_img in enumerate(pil_images):
            img_np = np.array(pil_img)
            try:
                result = await asyncio.to_thread(_predict, img_np)
            except Exception:
                continue

            try:
                for res in result:
                    if isinstance(res, dict) and "rec_texts" in res:
                        for text, score, box in zip(
                            res["rec_texts"], res["rec_scores"], res["rec_boxes"]
                        ):
                            datos["resultados"].append(
                                {
                                    "texto": text,
                                    "confianza": round(float(score), 4),
                                    "caja": [int(float(c)) for c in box],
                                    "pagina": page_idx + 1,
                                }
                            )
                    else:
                        flattened = []
                        if isinstance(res, list):
                            for item in res:
                                if isinstance(item, list):
                                    flattened.extend(item)
                                else:
                                    flattened.append(item)
                        else:
                            flattened.append(res)

                        for item in flattened:
                            try:
                                if isinstance(item, tuple) and len(item) == 2:
                                    box, text_score = item
                                    text, score = text_score
                                elif isinstance(item, tuple) and len(item) >= 3:
                                    box, text, score = item[0], item[1], item[2]
                                else:
                                    continue
                                datos["resultados"].append(
                                    {
                                        "texto": text,
                                        "confianza": round(float(score), 4),
                                        "caja": [int(float(c)) for c in box],
                                        "pagina": page_idx + 1,
                                    }
                                )
                            except Exception:
                                continue
            except Exception:
                continue

        confianzas = [r["confianza"] for r in datos["resultados"]]
        datos["confianza_promedio"] = (
            round(sum(confianzas) / len(confianzas), 4) if confianzas else 0.0
        )
        datos["total_paginas"] = len(pil_images)

        return datos
