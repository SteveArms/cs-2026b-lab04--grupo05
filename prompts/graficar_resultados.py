"""Gráfico de resultados del Lab 09 (E8) a partir de los resultados.json de promptfoo.

Uso (desde la raíz):  python prompts/graficar_resultados.py   -> prompts/img/resultados-lab09.png
Requiere matplotlib (solo local; el CI no lo usa).
"""
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

AQUI = pathlib.Path(__file__).parent
sys.path.insert(0, str(AQUI))
from verificar_evals import resumen_por_version  # noqa: E402


def tasas(suite):
    return {v.removesuffix(".txt"): (sum(c.values()), len(c)) for v, c in
            resumen_por_version(AQUI / suite / "resultados.json").items()}


if __name__ == "__main__":
    a, b = tasas("criterios"), tasas("revision-seguridad")
    rt = resumen_por_version(AQUI / "seguridad" / "resultados.json")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.3, 1]})
    for desplaz, (nombre, datos, color) in zip((-0.2, 0.2), (("Tarea A: criterios", a, "#2980b9"),
                                                             ("Tarea B: revisión de seguridad", b, "#c0392b"))):
        versiones = ["v1", "v2", "v3", "v3.1"]
        xs = [i + desplaz for i, v in enumerate(versiones) if v in datos]
        ys = [100 * datos[v][0] / datos[v][1] for v in versiones if v in datos]
        barras = ax1.bar(xs, ys, 0.38, label=nombre, color=color)
        for bar, v in zip(barras, [v for v in versiones if v in datos]):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                     f"{bar.get_height():.0f} %\n({datos[v][0]}/{datos[v][1]})", ha="center", fontsize=8)
    ax1.axhline(85, ls="--", c="k", lw=1)
    ax1.text(-0.45, 88, "meta 85 %", fontsize=8)
    ax1.set_xticks(range(4))
    ax1.set_xticklabels(["v1", "v2", "v3", "v3.1"])
    ax1.set_ylim(0, 118)
    ax1.set_ylabel("Casos que pasan TODAS las aserciones (%)")
    ax1.set_title("Tasa de aprobación por versión (8 casos por tarea)")
    ax1.legend(fontsize=8, loc="upper left")

    ataques = sorted(next(iter(rt.values())).keys())
    versiones = list(rt.keys())
    for j, v in enumerate(versiones):
        for i, at in enumerate(ataques):
            ok = rt[v][at]
            ax2.add_patch(plt.Rectangle((j, i), 0.95, 0.9, color="#d5f5e3" if ok else "#fadbd8"))
            ax2.text(j + 0.47, i + 0.45, "✔ resiste" if ok else "✘ falla", ha="center", va="center",
                     fontsize=9, color="#1e8449" if ok else "#c0392b")
    nombres = {"R1": "R1 inyección directa", "R2": "R2 inyección indirecta", "R3": "R3 revelar prompt",
               "R4": "R4 fuera de formato", "R5": "R5 cambio de idioma", "R6": "R6 escape de delimitador"}
    ax2.set_xlim(0, len(versiones))
    ax2.set_ylim(len(ataques), 0)
    ax2.set_xticks([j + 0.47 for j in range(len(versiones))])
    ax2.set_xticklabels([f"{v.removesuffix('.txt')} ({sum(rt[v].values())}/{len(rt[v])})" for v in versiones])
    ax2.set_yticks([i + 0.45 for i in range(len(ataques))])
    ax2.set_yticklabels([nombres.get(a, a) for a in ataques], fontsize=8)
    ax2.set_title("Red teaming de la Tarea B: antes (v3) y después (v3.1)")
    for s in ax2.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    (AQUI / "img").mkdir(exist_ok=True)
    fig.savefig(AQUI / "img" / "resultados-lab09.png", dpi=130)
    print("Gráfico:", AQUI / "img" / "resultados-lab09.png")
