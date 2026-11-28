"""Pruebas del agente del Lab 10 conectado al servidor MCP (Lab 11, E4).

Reproducen la trayectoria grabada con el servidor REAL (por stdio, a través del espía) y un
"humano" simulado. Sin red ni LLM. Ejecutar:  python -m pytest -q agentes/mcp/pruebas
"""
import json
import pathlib
import sys

AQUI = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(AQUI.parent), str(AQUI)]

import analista  # noqa: E402
from agente.politica import Politica  # noqa: E402


def correr(tmp_path, aprobador):
    llamadas = []

    def humano(accion, args):
        llamadas.append(accion)
        return aprobador

    agente = analista.main(aprobador=humano, traza_agente=tmp_path / "analista.jsonl",
                           trafico=tmp_path / "trafico.jsonl",
                           env={"VOTOEPIS_OBSERVACIONES": str(tmp_path / "obs")})
    return agente, llamadas


def test_agente_resuelve_la_consulta_via_mcp_con_aprobacion(tmp_path):
    agente, llamadas = correr(tmp_path, True)
    assert llamadas == ["registrar_observacion"]                         # el humano aprobó la única escritura
    assert [f.name for f in (tmp_path / "obs").iterdir()] == ["OBS-01.md"]
    estados = [e["estado"] for e in agente.eventos if e["tipo"] == "accion"]
    assert estados == ["OBSERVANDO"] * 5 and agente.eventos[-1]["estado"] == "FINALIZADO"
    assert agente.eventos[2]["observacion"].startswith("ERROR: ")       # se equivocó y se corrigió solo
    metodos = [json.loads(l)["msg"].get("method") for l in open(tmp_path / "trafico.jsonl", encoding="utf-8")]
    assert metodos[0] == "server/discover" and metodos.count("tools/call") == 4


def test_si_el_humano_rechaza_no_se_escribe_nada(tmp_path):
    agente, _ = correr(tmp_path, False)
    bloqueos = [e for e in agente.eventos if e.get("estado") == "BLOQUEADO"]
    assert len(bloqueos) == 1 and "rechazó registrar_observacion" in bloqueos[0]["observacion"]
    assert not (tmp_path / "obs").exists() or list((tmp_path / "obs").iterdir()) == []


def test_politica_falla_cerrado_sin_revisor():
    p = Politica(herramientas_permitidas={"registrar_observacion"}, requieren_aprobacion={"registrar_observacion"})
    d = p.evaluar("registrar_observacion", {}, 1)
    assert not d.permitido and "requiere aprobación humana" in d.motivo
