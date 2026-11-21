"""E7: métricas de observación calculadas SOLO a partir de las trazas JSONL de los 3 issues.

Uso (desde agentes/):  python metricas.py      -> imprime la tabla Markdown y genera
                                                   trazas/metricas.json y diseno/img/metricas.png
"""
import collections
import json
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from agente.traza import a_mermaid, cargar, cargar_archivo  # noqa: E402

CORRIDAS = {
    "ISSUE-01 (agente único, E2)": ("archivo", BASE / "trazas" / "issue1.jsonl"),
    "ISSUE-02 (agente único, E5)": ("archivo", BASE / "trazas" / "issue2_unico.jsonl"),
    "ISSUE-02 (actor-crítico, E5)": ("carpeta", BASE / "trazas" / "issue2_multi"),
    "ISSUE-03 (agente único + mapa_repo y notas, E4)": ("archivo", BASE / "trazas" / "issue3.jsonl"),
}


def contexto_estimado(eventos) -> int:
    """Caracteres del historial reconstruidos desde la traza (cota inferior: la traza recorta
    cada observación a 600 caracteres). Si hay varios agentes, se suman sus historiales."""
    total = 0
    for e in eventos:
        if e["tipo"] == "objetivo":
            total += len(e.get("texto", ""))
        elif e["tipo"] == "accion":
            decision = {"pensamiento": e.get("pensamiento", ""), "accion": e.get("accion"), "args": e.get("args", {})}
            total += len(json.dumps(decision, ensure_ascii=False)) + len("Observación: ") + len(e.get("observacion", ""))
        elif e["tipo"] == "final":
            total += len(json.dumps({"pensamiento": e.get("pensamiento", ""), "final": e.get("texto", "")},
                                    ensure_ascii=False))
    return total


def metricas(eventos) -> dict:
    acciones = [e for e in eventos if e["tipo"] == "accion"]
    herramientas = collections.Counter(e["accion"] for e in acciones if e["estado"] != "CONTRATO_INVALIDO")
    return {
        "agentes": len({e["agente"] for e in eventos}),
        "rondas": max((e.get("ronda", 1) for e in eventos), default=1),
        "pasos": len(acciones),
        "herramientas": dict(herramientas),
        "contrato_rechazado": sum(e["estado"] == "CONTRATO_INVALIDO" for e in acciones),
        "bloqueadas_politica": sum(e["estado"] in ("BLOQUEADO", "LIMITE_ALCANZADO") for e in acciones),
        "finalizado": any(e["tipo"] == "final" for e in eventos),
        "contexto_estimado": contexto_estimado(eventos),
    }


def cargar_corrida(tipo, ruta):
    return cargar(str(ruta)) if tipo == "carpeta" else cargar_archivo(str(ruta))


def tabla(res: dict) -> str:
    filas = ["| Corrida | Agentes | Rondas | Pasos (acciones) | Herramientas usadas | Rechazadas por el contrato | "
             "Bloqueadas por la política | ¿Terminó? | Contexto final estimado |",
             "|---|---|---|---|---|---|---|---|---|"]
    for nombre, m in res.items():
        hs = "; ".join(f"{k} ×{v}" for k, v in sorted(m["herramientas"].items(), key=lambda x: -x[1]))
        ctx = f"{m['contexto_estimado']:,}".replace(",", " ")
        tok = f"{m['contexto_estimado'] // 4:,}".replace(",", " ")
        filas.append(f"| {nombre} | {m['agentes']} | {m['rondas']} | {m['pasos']} | {hs} | {m['contrato_rechazado']} | "
                     f"{m['bloqueadas_politica']} | {'sí' if m['finalizado'] else 'no'} | {ctx} car. (~{tok} tokens) |")
    return "\n".join(filas)


def grafico(res: dict, salida: pathlib.Path) -> None:  # pragma: no cover
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    nombres = [n.split(" (")[0] + "\n" + n.split("(")[1].rstrip(")").split(",")[0] for n in res]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6))
    ok = [m["pasos"] - m["contrato_rechazado"] - m["bloqueadas_politica"] for m in res.values()]
    con = [m["contrato_rechazado"] for m in res.values()]
    bloq = [m["bloqueadas_politica"] for m in res.values()]
    a1.bar(nombres, ok, color="#2e7d32", label="Ejecutadas")
    a1.bar(nombres, con, bottom=ok, color="#f9a825", label="Rechazadas por el contrato")
    a1.bar(nombres, bloq, bottom=[a + b for a, b in zip(ok, con)], color="#c62828", label="Bloqueadas por la política")
    for i, m in enumerate(res.values()):
        a1.text(i, m["pasos"] + 0.3, str(m["pasos"]), ha="center", fontsize=9)
    a1.set_ylabel("Acciones")
    a1.set_ylim(0, max(m["pasos"] for m in res.values()) * 1.18)
    a1.set_title("Pasos por corrida")
    a1.legend(fontsize=8, loc="upper left")
    ctx = [m["contexto_estimado"] / 1000 for m in res.values()]
    a2.bar(nombres, ctx, color="#1565c0")
    for i, v in enumerate(ctx):
        a2.text(i, v + 0.3, f"{v:.1f} k", ha="center", fontsize=9)
    a2.set_ylabel("Miles de caracteres (suma de historiales)")
    a2.set_ylim(0, max(ctx) * 1.15)
    a2.set_title("Contexto final estimado desde la traza")
    for a in (a1, a2):
        a.tick_params(axis="x", labelsize=8)
    fig.tight_layout()
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=130)


if __name__ == "__main__":
    res = {n: metricas(cargar_corrida(t, r)) for n, (t, r) in CORRIDAS.items()}
    print(tabla(res))
    (BASE / "trazas" / "metricas.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (BASE / "trazas" / "issue2_multi.mmd").write_text(
        a_mermaid(cargar(str(BASE / "trazas" / "issue2_multi"))), encoding="utf-8")
    (BASE / "trazas" / "issue2_unico.mmd").write_text(
        a_mermaid(cargar_archivo(str(BASE / "trazas" / "issue2_unico.jsonl"))), encoding="utf-8")
    try:
        grafico(res, BASE / "diseno" / "img" / "metricas.png")
        print("\nGráfico: diseno/img/metricas.png")
    except ImportError:
        print("\n(instale matplotlib para generar el gráfico)")
