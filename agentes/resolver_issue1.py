"""Ejecutor del agente ReAct para el ISSUE-01 (VotoEPIS)."""
import pathlib
import sys

# Asegurar que el paquete 'agentes' y la raíz del repo estén en sys.path
BASE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(REPO_ROOT / "src"))

from agente.herramientas import Herramientas
from agente.modelos import ModeloGrabado
from agente.nucleo import Agente
from agente.politica import Politica

def main():
    h = Herramientas(str(REPO_ROOT))
    politica = Politica(max_pasos=12)
    trayectoria_path = BASE_DIR / "trayectorias" / "issue1.json"
    traza_path = BASE_DIR / "trazas" / "issue1.jsonl"
    (BASE_DIR / "trazas").mkdir(exist_ok=True)

    modelo = ModeloGrabado(str(trayectoria_path))
    objetivo = "Resuelve el defecto reportado en issues/ISSUE-01.md: evitar el doble voto por diferencia de mayúsculas/espacios en código de estudiante."

    agente = Agente("ejecutor", modelo, h, politica, objetivo, str(traza_path))
    print(f"[*] Iniciando agente ReAct sobre ISSUE-01...")
    resultado = agente.ejecutar()
    print(f"\n[+] Agente finalizado con éxito.\nResultado final:\n{resultado}\n")

if __name__ == "__main__":
    main()
