"""Genera los 3 prompts del experimento de no determinismo (Lab 09, E7).

Usa el MISMO generador de producción (v3.1, con la capa 1 de delimitadores), así que lo
que se pega en el asistente es exactamente lo que enviaría VotoEPIS.

Uso (desde la raíz del repo):  python prompts/no-determinismo/renderizar.py
"""
import pathlib
import sys

import yaml

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
from votacion.generador_revision import GeneradorRevisionSeguridad  # noqa: E402
from votacion.ia import ProveedorSimulado  # noqa: E402

CASOS = ["C1", "C5", "C8"]          # vulnerable, limpio y con inyección

if __name__ == "__main__":
    casos = {c["vars"]["id"]: c["vars"]["codigo"]
             for c in yaml.safe_load((RAIZ / "prompts/revision-seguridad/casos.yaml").read_text(encoding="utf-8"))}
    gen = GeneradorRevisionSeguridad(ProveedorSimulado(), version="v3.1")
    salida = pathlib.Path(__file__).parent / "renderizados"
    salida.mkdir(exist_ok=True)
    for c in CASOS:
        (salida / f"{c}.txt").write_text(gen.construir_prompt(c, casos[c]), encoding="utf-8")
        print("escrito", salida / f"{c}.txt")
