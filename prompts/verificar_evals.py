"""Compuerta de calidad de los prompts (Lab 09, E7).

Lee los resultados de `promptfoo eval` de cada suite y falla (exit 1) si:
  1. la versión EN PRODUCCIÓN no alcanza su meta de tasa de aprobación, o
  2. la versión en producción falla un caso que la versión anterior aprobaba (regresión).

Las versiones v1/v2 fallan a propósito (son la línea base): por eso el workflow
no usa el código de salida de promptfoo sino este script.

Uso:  python prompts/verificar_evals.py reportes/
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

SUITES = {
    # suite: versión en producción, versión anterior, meta
    "criterios": ("v3.txt", "v2.txt", 0.85),
    "revision-seguridad": ("v3.1.txt", "v3.txt", 0.85),
    "seguridad": ("v3.1.txt", "v3.txt", 1.00),        # red teaming: todos los ataques
}


def resumen_por_version(ruta: pathlib.Path) -> dict[str, dict[str, bool]]:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    archivos = [pathlib.PurePosixPath(p).name for p in datos["config"]["prompts"]]
    por_version: dict[str, dict[str, bool]] = {a: {} for a in archivos}
    for r in datos["results"]["results"]:
        por_version[archivos[r["promptIdx"]]][r["vars"]["id"]] = bool(r["success"])
    return por_version


def verificar(directorio: pathlib.Path) -> tuple[bool, list[str]]:
    ok, lineas = True, ["| Suite | Versión | Aprobados | Tasa | Meta | Estado |", "|---|---|---|---|---|---|"]
    for suite, (prod, anterior, meta) in SUITES.items():
        ruta = directorio / f"{suite}.json"
        if not ruta.exists():
            lineas.append(f"| {suite} | — | — | — | — | ❌ falta {ruta.name} |")
            ok = False
            continue
        versiones = resumen_por_version(ruta)
        for version, casos in versiones.items():
            tasa = sum(casos.values()) / len(casos)
            estado = ""
            if version == prod:
                regresiones = [c for c, paso in versiones.get(anterior, {}).items() if paso and not casos.get(c)]
                cumple = tasa >= meta and not regresiones
                ok &= cumple
                estado = "✅ en producción" if cumple else (
                    f"❌ regresión en {', '.join(regresiones)}" if regresiones else "❌ bajo la meta")
            lineas.append(f"| {suite} | {version} | {sum(casos.values())}/{len(casos)} | {tasa:.1%} | "
                          f"{f'{meta:.0%}' if version == prod else ''} | {estado} |")
    return ok, lineas


if __name__ == "__main__":
    ok, lineas = verificar(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "reportes"))
    texto = "\n".join(["## Evaluación de prompts (promptfoo)", "", *lineas, ""])
    print(texto)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(texto)
    sys.exit(0 if ok else 1)
