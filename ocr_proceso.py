import json
import multiprocessing as mp
from pathlib import Path

from paddleocr import PaddleOCR


def _crear_ocr():
    return PaddleOCR(
        lang="es",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        device="cpu",
    )


def _procesar_en_worker(ruta_imagen: str) -> dict:
    ocr = _crear_ocr()
    result = ocr.predict(ruta_imagen)

    datos = {"imagen": str(Path(ruta_imagen).absolute()), "resultados": []}

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

    return datos


def procesar_una_imagen(ruta_imagen: str) -> dict:
    return _procesar_en_worker(ruta_imagen)


def procesar_varias_imagenes(rutas: list[str], workers: int = None) -> list[dict]:  # type: ignore
    if workers is None:
        workers = max(1, mp.cpu_count() - 1)

    with mp.Pool(workers) as pool:
        return pool.map(_procesar_en_worker, rutas)


def guardar_json(datos: dict, carpeta_salida: Path = None):  # type: ignore
    confianzas = [r["confianza"] for r in datos["resultados"]]
    datos["confianza_promedio"] = (
        round(sum(confianzas) / len(confianzas), 4) if confianzas else 0.0
    )

    if carpeta_salida is None:
        carpeta_salida = Path(__file__).parent / "output"
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    nombre_json = Path(datos["imagen"]).stem + ".json"
    output_path = carpeta_salida / nombre_json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    print(f"Guardado: {output_path}")


def main():
    import sys

    if len(sys.argv) < 2:
        print("Uso: python ocr_proceso.py <imagen1> [imagen2] ... [imagenN]")
        print("Ejemplo: python ocr_proceso.py foto1.png foto2.jpg")
        sys.exit(1)

    rutas = sys.argv[1:]

    archivos = []
    for ruta in rutas:
        path = Path(ruta)
        if path.is_dir():
            archivos.extend([str(p) for p in path.glob("*.png")])
            archivos.extend([str(p) for p in path.glob("*.jpg")])
            archivos.extend([str(p) for p in path.glob("*.jpeg")])
            archivos.extend([str(p) for p in path.glob("*.bmp")])
        else:
            archivos.append(ruta)

    if not archivos:
        print("No se encontraron imágenes.")
        sys.exit(1)

    workers = max(1, mp.cpu_count() - 1)

    if len(archivos) <= 2:
        print(f"Modo secuencial ({len(archivos)} imagenes)")
        resultados = [procesar_una_imagen(r) for r in archivos]
    else:
        print(f"Modo paralelo: {len(archivos)} imagenes con {workers} workers")
        resultados = procesar_varias_imagenes(archivos, workers)

    print()
    carpeta_salida = Path(__file__).parent / "output"
    for datos in resultados:
        guardar_json(datos, carpeta_salida)

    tiempo_total = 0
    for datos in resultados:
        tiempo_total += sum(1 for _ in datos["resultados"])

    print(f"\n{len(resultados)} imagenes procesadas")
    for datos in resultados:
        print(f"\n--- {Path(datos['imagen']).name} ---")
        for r in datos["resultados"]:
            print(f'  "{r["texto"]}" ({r["confianza"]:.2%})')
        conf_avg = (
            sum(r["confianza"] for r in datos["resultados"]) / len(datos["resultados"])
            if datos["resultados"]
            else 0
        )
        print(f"  Confianza promedio: {conf_avg:.2%}")


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
