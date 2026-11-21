"""E5 (variante 1): un SOLO agente ReAct resuelve el ISSUE-02 en la copia de trabajo.

Uso (desde agentes/):
  python resolver_issue2_unico.py                 # reproduce la trayectoria grabada
  python resolver_issue2_unico.py --interactivo   # usted copia el contexto a su asistente y pega el JSON
"""
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from agente.herramientas import Herramientas
from agente.modelos import ModeloGrabado, ModeloInteractivo
from agente.nucleo import Agente
from agente.politica import Politica
from protocolo import objetivo
from sandbox import contexto_chars, preparar

TRAYECTORIA = BASE / "trayectorias" / "issue2_unico.json"
TRAZA = BASE / "trazas" / "issue2_unico.jsonl"


def main(interactivo: bool = False) -> Agente:
    h = Herramientas(preparar())
    (BASE / "trazas").mkdir(exist_ok=True)
    modelo = ModeloInteractivo(str(TRAYECTORIA)) if interactivo else ModeloGrabado(str(TRAYECTORIA))
    agente = Agente("ejecutor", modelo, h, Politica(max_pasos=12),
                    objetivo("Resuelve el defecto de issues/ISSUE-02.md en este repositorio. "
                             "Corrige el código de src/, nunca las pruebas.", h.catalogo()),
                    str(TRAZA))
    resultado = agente.ejecutar()
    print(f"AGENTE ÚNICO:\n{resultado}\n")
    print(f"[ejecutor] contexto final: {contexto_chars(agente)} caracteres (~{contexto_chars(agente) // 4} tokens)")
    return agente


if __name__ == "__main__":
    main("--interactivo" in sys.argv)
