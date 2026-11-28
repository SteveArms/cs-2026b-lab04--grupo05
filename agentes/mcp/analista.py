"""E4 (Lab 11): el agente del Lab 10 resuelve una consulta de negocio de VotoEPIS usando el servidor MCP.

El núcleo ReAct, el contrato y la política son los del Lab 10 (agentes/agente/). Solo cambian las
herramientas: ahora vienen del servidor MCP a través del adaptador HerramientasMCP, y el tráfico pasa
por el espía de stdio (trazas/mcp_trafico.jsonl).

Uso (desde la raíz del repositorio):
  python agentes/mcp/analista.py                 # reproduce las decisiones grabadas; usted aprueba la escritura
  python agentes/mcp/analista.py --interactivo   # copie el contexto a su asistente de IA y pegue el JSON
"""
import datetime
import json
import pathlib
import sys

AQUI = pathlib.Path(__file__).resolve().parent
AGENTES = AQUI.parent
sys.path[:0] = [str(AGENTES), str(AQUI)]

from mcp import StdioServerParameters  # noqa: E402

from agente.herramientas_mcp import HerramientasMCP  # noqa: E402  (adaptador del Lab 11)
from agente.modelos import ModeloGrabado, ModeloInteractivo  # noqa: E402  (Lab 10, sin cambios)
from agente.nucleo import Agente  # noqa: E402
from agente.politica import Politica  # noqa: E402
from humano import pedir_respuesta  # noqa: E402  (E6 del Lab 10: solo acepta s/n)
from protocolo import objetivo  # noqa: E402

TRAYECTORIA = AQUI / "trayectorias" / "analista.json"
TRAZA_AGENTE = AQUI / "trazas" / "analista.jsonl"
TRAFICO = AQUI / "trazas" / "mcp_trafico.jsonl"
APROBACIONES = AQUI / "trazas" / "aprobaciones_mcp.jsonl"

CONSULTA = ("El comité electoral pide un reporte breve: (1) el resultado oficial de la elección 'Delegados EPIS "
            "2026', con los votos válidos y la lista ganadora; (2) la participación actual de la elección 'Tercio "
            "estudiantil 2026'. Si en Delegados los votos en blanco y nulos superan el 15 % de la participación, "
            "registra una observación para el comité. Respeta el reglamento electoral.")


def parametros(traza: pathlib.Path = TRAFICO, env: dict | None = None) -> StdioServerParameters:
    """El agente lanza el ESPÍA, y el espía lanza el servidor: así se registra cada mensaje JSON-RPC."""
    return StdioServerParameters(
        command=sys.executable,
        args=[str(AQUI / "cliente" / "espia.py"), str(traza), sys.executable,
              str(AQUI / "servidor_mcp" / "votoepis_mcp.py")],
        cwd=str(AGENTES.parent), env=env)


def aprobar_por_consola(accion: str, args: dict, entrada=input, salida=print, registro=APROBACIONES) -> bool:
    salida(f"\n===== EL AGENTE QUIERE EJECUTAR UNA HERRAMIENTA DE ESCRITURA: {accion} =====")
    for k, v in args.items():
        salida(f"  {k}: {v}")
    r = pedir_respuesta(entrada, salida, "¿Aprueba ejecutar esta herramienta? [s/n]: ")
    registro.parent.mkdir(parents=True, exist_ok=True)
    with open(registro, "a", encoding="utf-8") as f:
        f.write(json.dumps({"momento": datetime.datetime.now().isoformat(timespec="seconds"), "accion": accion,
                            "args": args, "decision": "APROBADA" if r == "s" else "RECHAZADA"},
                           ensure_ascii=False) + "\n")
    return r == "s"


def main(interactivo: bool = False, aprobador=aprobar_por_consola, trayectoria=TRAYECTORIA,
         traza_agente=TRAZA_AGENTE, trafico=TRAFICO, env: dict | None = None) -> Agente:
    trafico.parent.mkdir(parents=True, exist_ok=True)
    trafico.write_text("", encoding="utf-8")                    # una traza limpia por ejecución
    h = HerramientasMCP(parametros(trafico, env))
    try:
        politica = Politica(herramientas_permitidas=set(h.catalogo()), max_pasos=8,
                            requieren_aprobacion=h.herramientas_de_escritura())
        politica.aprobar_accion = aprobador                     # humano en el circuito para la escritura
        modelo = ModeloInteractivo(str(trayectoria)) if interactivo else ModeloGrabado(str(trayectoria))
        agente = Agente("analista", modelo, h, politica, objetivo(CONSULTA, h.catalogo()), str(traza_agente))
        print(f"Conectado vía MCP (protocolo {h.protocolo}). Herramientas de escritura: "
              f"{sorted(politica.requieren_aprobacion)}")
        respuesta = agente.ejecutar()
    finally:
        h.cerrar()
    print(f"\nANALISTA:\n{respuesta}")
    print(f"\nTraza del agente: {traza_agente} | tráfico JSON-RPC: {trafico}")
    return agente


if __name__ == "__main__":
    main("--interactivo" in sys.argv)
