"""E6: humano en el circuito (human-in-the-loop) para las ediciones del ejecutor.

Se conecta a la política:  politica.aprobar_edicion = aprobar_por_consola
Cada edición propuesta se muestra en consola y un integrante responde 's' (aprobar) o 'n' (rechazar).
La entrada humana también se valida (patrón "validar la entrada humana", Koenigstein, 2026, cap. 2):
cualquier otra respuesta se vuelve a pedir. Cada decisión queda registrada en trazas/aprobaciones.jsonl.
"""
import datetime
import json
import pathlib

REGISTRO = pathlib.Path(__file__).resolve().parent / "trazas" / "aprobaciones.jsonl"


def _vista_previa(args: dict, max_lineas: int = 12) -> str:
    def recortar(texto: str) -> str:
        lineas = texto.splitlines() or [""]
        extra = f"\n      ... ({len(lineas) - max_lineas} líneas más)" if len(lineas) > max_lineas else ""
        return "\n".join("      " + l for l in lineas[:max_lineas]) + extra
    return (f"  archivo: {args.get('ruta', '?')}\n"
            f"  - ANTES:\n{recortar(args.get('antes', ''))}\n"
            f"  + DESPUÉS:\n{recortar(args.get('despues', '')) if args.get('despues') else '      (se elimina el fragmento)'}")


def pedir_respuesta(entrada=input, salida=print) -> str:
    """Devuelve 's' o 'n'. Repite la pregunta ante cualquier otra respuesta."""
    while True:
        r = entrada("¿Aprueba esta edición? [s/n]: ").strip().lower()
        if r in ("s", "n"):
            return r
        salida(f"Respuesta inválida {r!r}: escriba solo 's' o 'n'.")


def aprobar_por_consola(args: dict, entrada=input, salida=print, registro: pathlib.Path = REGISTRO) -> bool:
    salida("\n===== EL EJECUTOR PROPONE UNA EDICIÓN =====")
    salida(_vista_previa(args))
    r = pedir_respuesta(entrada, salida)
    registro.parent.mkdir(parents=True, exist_ok=True)
    with open(registro, "a", encoding="utf-8") as f:
        f.write(json.dumps({"momento": datetime.datetime.now().isoformat(timespec="seconds"),
                            "ruta": args.get("ruta"), "decision": "APROBADA" if r == "s" else "RECHAZADA"},
                           ensure_ascii=False) + "\n")
    return r == "s"
