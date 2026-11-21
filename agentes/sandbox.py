"""Copia de trabajo aislada para los agentes (regla: nunca sobre main ni sobre src/ real).

preparar() copia trabajo_original/ -> trabajo/ y hace un commit local, para que la
herramienta ver_cambios() (git diff src/) muestre solo lo que cambió el agente.
"""
import os
import pathlib
import shutil
import stat
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
ORIGINAL = RAIZ / "trabajo_original"
TRABAJO = RAIZ / "trabajo"


def _forzar_borrado(funcion, ruta, _error):
    """En Windows, git deja sus objetos como solo lectura y rmtree no puede borrarlos:
    se quita el atributo y se reintenta."""
    os.chmod(ruta, stat.S_IWRITE)
    funcion(ruta)


def _borrar(carpeta: pathlib.Path) -> None:
    if not carpeta.exists():
        return
    if sys.version_info >= (3, 12):
        shutil.rmtree(carpeta, onexc=_forzar_borrado)
    else:
        shutil.rmtree(carpeta, onerror=_forzar_borrado)


def preparar() -> pathlib.Path:
    _borrar(TRABAJO)                                         # cada ejecución parte del estado original
    shutil.copytree(ORIGINAL, TRABAJO, ignore=shutil.ignore_patterns("__pycache__"))
    git = ["git", "-c", "user.name=sandbox", "-c", "user.email=sandbox@votoepis.invalid"]
    subprocess.run(["git", "init", "-q"], cwd=TRABAJO, check=True)
    subprocess.run(git + ["add", "-A"], cwd=TRABAJO, check=True)
    subprocess.run(git + ["commit", "-q", "-m", "estado original (ISSUE-02 sin resolver)"], cwd=TRABAJO, check=True)
    return TRABAJO


def contexto_chars(agente) -> int:
    """Tamaño final del historial del agente (memoria de corto plazo), en caracteres."""
    import json
    return len(json.dumps(agente.historial, ensure_ascii=False))
