"""E5 (variante 2): sistema multiagente con coordinación por gestor (Albada, 2025, cap. 8).
Planificador -> [Ejecutor (actor) <-> Revisor (crítico)] -> Humano, sobre el ISSUE-02 de VotoEPIS.
Cada agente tiene su propia política (mínimo privilegio) y todos trabajan en la copia agentes/trabajo/.

Uso (desde agentes/):
  python orquestador.py                  # reproduce las trayectorias grabadas
  python orquestador.py --interactivo    # decisiones pegadas desde su asistente de IA
  python orquestador.py --aprobar        # E6: un integrante aprueba (s/n) cada edición del ejecutor
"""
import json
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

MAX_RONDAS = 2                                                     # presupuesto del bucle actor-crítico
TRAY = BASE / "trayectorias" / "issue2_multi"
TRAZ = BASE / "trazas" / "issue2_multi"
SOLO_LECTURA = {"listar_archivos", "leer_archivo", "buscar", "mapa_repo"}


def modelo(nombre: str, interactivo: bool):
    ruta = TRAY / f"{nombre}.json"
    return ModeloInteractivo(str(ruta)) if interactivo else ModeloGrabado(str(ruta))


def sufijo(ronda: int) -> str:
    return "" if ronda == 1 else f"_r{ronda}"


def main(interactivo: bool = False, aprobar: bool = False) -> list:
    TRAY.mkdir(parents=True, exist_ok=True)
    TRAZ.mkdir(parents=True, exist_ok=True)
    h = Herramientas(preparar())

    planificador = Agente("planificador", modelo("planificador", interactivo), h,
                          Politica(herramientas_permitidas=SOLO_LECTURA, max_pasos=4),
                          objetivo("Eres el PLANIFICADOR. Planifica en 3 a 5 pasos cómo resolver "
                                   "issues/ISSUE-02.md. No editas nada.", h.catalogo()),
                          str(TRAZ / "planificador.jsonl"))
    plan = planificador.ejecutar()
    print(f"PLANIFICADOR:\n{plan}\n")
    agentes, retro = [planificador], ""

    for ronda in range(1, MAX_RONDAS + 1):
        politica_ejecutor = Politica(max_pasos=12)
        if aprobar:                                                # E6: humano en el circuito
            from humano import aprobar_por_consola
            politica_ejecutor.aprobar_edicion = aprobar_por_consola
        ejecutor = Agente("ejecutor", modelo(f"ejecutor{sufijo(ronda)}", interactivo), h, politica_ejecutor,
                          objetivo(f"Eres el EJECUTOR. Resuelve issues/ISSUE-02.md siguiendo este plan:\n{plan}\n"
                                   f"{retro}Corrige src/, nunca las pruebas.", h.catalogo()),
                          str(TRAZ / f"ejecutor{sufijo(ronda)}.jsonl"))
        resumen = ejecutor.ejecutar()
        revisor = Agente("revisor", modelo(f"revisor{sufijo(ronda)}", interactivo), h,
                         Politica(herramientas_permitidas={"ver_cambios", "leer_archivo", "buscar",
                                                           "ejecutar_pruebas"}, max_pasos=8),
                         objetivo("Eres el REVISOR (solo lectura). Revisa el cambio del ejecutor: corrección, "
                                  "regresiones y seguridad. Tu 'final' debe empezar con APROBADO o con "
                                  f"CAMBIOS SOLICITADOS.\nResumen del ejecutor:\n{resumen}", h.catalogo()),
                         str(TRAZ / f"revisor{sufijo(ronda)}.jsonl"))
        veredicto = revisor.ejecutar()
        agentes += [ejecutor, revisor]
        print(f"--- RONDA {ronda}\nEJECUTOR: {resumen}\nREVISOR: {veredicto}\n")
        if not veredicto.startswith("CAMBIOS SOLICITADOS"):        # el crítico acepta: pasa al humano
            break
        retro = f"El revisor solicitó cambios:\n{veredicto}\n"     # el crítico rechaza: nueva ronda

    print(f"Rondas actor-crítico: {ronda} de {MAX_RONDAS}. Decisión final: HUMANO (aprobar o rechazar el PR).")
    for a in agentes:
        print(f"[{a.nombre}] contexto final: {contexto_chars(a)} caracteres (~{contexto_chars(a) // 4} tokens)")
    print("\nDIFF FINAL (ver_cambios):\n" + h.ver_cambios())
    return agentes


if __name__ == "__main__":
    main("--interactivo" in sys.argv, "--aprobar" in sys.argv)
