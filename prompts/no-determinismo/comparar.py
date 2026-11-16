"""Compara 3 ejecuciones del mismo prompt sobre los mismos casos (Lab 09, E7).

Lee ejecuciones/<caso>_r1.txt, _r2.txt y _r3.txt (respuestas pegadas SIN editar)
y muestra qué cambió entre ejecuciones.

Uso (desde la raíz del repo):  python prompts/no-determinismo/comparar.py
"""
import difflib
import json
import pathlib

from jsonschema import ValidationError, validate

AQUI = pathlib.Path(__file__).parent
ESQUEMA = json.loads((AQUI.parent / "revision-seguridad/esquema.json").read_text(encoding="utf-8"))
CASOS = ["C1", "C5", "C8"]


def leer(caso: str, n: int):
    texto = (AQUI / "ejecuciones" / f"{caso}_r{n}.txt").read_text(encoding="utf-8").strip()
    try:
        datos = json.loads(texto)
        validate(datos, ESQUEMA)
        return texto, datos
    except (json.JSONDecodeError, ValidationError):
        return texto, None


def similitud(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


if __name__ == "__main__":
    print("| Caso | Válidas | Texto idéntico | Mismo veredicto | Mismas (línea, regla) | Similitud media del texto | Similitud de 'resumen' |")
    print("|---|---|---|---|---|---|---|")
    for caso in CASOS:
        runs = [leer(caso, n) for n in (1, 2, 3)]
        textos = [t for t, _ in runs]
        datos = [d for _, d in runs if d is not None]
        pares = [(0, 1), (0, 2), (1, 2)]
        sim_txt = sum(similitud(textos[i], textos[j]) for i, j in pares) / 3
        if len(datos) == 3:
            veredictos = {d["seguro"] for d in datos}
            hallazgos = {frozenset((h["linea"], h["regla"]) for h in d["hallazgos"]) for d in datos}
            sim_res = sum(similitud(datos[i]["resumen"], datos[j]["resumen"]) for i, j in pares) / 3
            fila = (f"{'sí' if len(veredictos) == 1 else 'NO'} | {'sí' if len(hallazgos) == 1 else 'NO'} | "
                    f"{sim_txt:.0%} | {sim_res:.0%}")
        else:
            fila = f"— | — | {sim_txt:.0%} | —"
        print(f"| {caso} | {len(datos)}/3 | {'sí' if len(set(textos)) == 1 else 'no'} | {fila} |")
    print("\nDetalle por ejecución (línea, regla):")
    for caso in CASOS:
        for n in (1, 2, 3):
            _, d = leer(caso, n)
            hs = sorted((h["linea"], h["regla"]) for h in d["hallazgos"]) if d else "INVÁLIDA"
            print(f"  {caso} r{n}: seguro={d['seguro'] if d else '—'} {hs}")
