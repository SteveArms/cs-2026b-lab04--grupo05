"""Proveedor de promptfoo con respuestas grabadas (red teaming, Lab 09 E5).

Detecta la versión del prompt por su contenido y devuelve la respuesta grabada
en grabaciones/<version>/<id>.txt, sin editarla.
"""
import pathlib

BASE = pathlib.Path(__file__).parent


def detectar_version(prompt: str) -> str:
    if "# DEFENSAS" in prompt:
        return "v3.1"
    if "<codigo" in prompt:
        return "v3"
    raise ValueError("Versión de prompt no reconocida")


def call_api(prompt, options, context):
    case_id = context.get("vars", {}).get("id")
    ruta = BASE / "grabaciones" / detectar_version(prompt) / f"{case_id}.txt"
    return {"output": ruta.read_text(encoding="utf-8")}
