"""Generador de revisiones de seguridad con LLM (Lab 09, E6).

Usa el prompt versionado de la Tarea B (prompts/revision-seguridad/<version>.txt)
detrás del puerto ProveedorLLM del Lab 07 (Strategy: Claude, OpenAI, Ollama o un
proveedor grabado) y aplica la defensa en capas del red teaming (E5):

* Capa 1 - delimitadores: el código se mete entre <codigo>...</codigo> y se
  neutralizan los delimitadores que traiga dentro (ataque R6).
* Capa 3 - validación de salida: la respuesta se parsea y se valida contra
  esquema.json; si no cumple se lanza SalidaInvalida y NUNCA se devuelve tal cual.
* Capa 4 - mínimo privilegio: solo devuelve un informe (dict); no aprueba PRs,
  no modifica código ni ejecuta acciones.
"""
from __future__ import annotations

import json
import pathlib
import re

from jsonschema import ValidationError, validate

from votacion.ia import ProveedorLLM

DIR_PROMPTS = pathlib.Path(__file__).resolve().parents[2] / "prompts" / "revision-seguridad"
_MARCADOR_CODIGO = re.compile(r"\{\{\s*codigo\b[^}]*\}\}")
_MARCADOR_ID = re.compile(r"\{\{\s*id\s*\}\}")


class SalidaInvalida(Exception):
    """La respuesta del LLM no cumple el contrato: se descarta y se registra."""


def neutralizar_delimitadores(codigo: str) -> str:
    """Capa 1: el dato no puede cerrar ni abrir el bloque <codigo> (misma regla que v3.1.txt)."""
    return codigo.replace("</codigo", "&lt;/codigo").replace("<codigo", "&lt;codigo")


class GeneradorRevisionSeguridad:
    def __init__(self, proveedor: ProveedorLLM, version: str = "v3.1",
                 directorio: pathlib.Path = DIR_PROMPTS) -> None:
        self._proveedor = proveedor                      # Strategy (Lab 07)
        self.version = version
        self._plantilla = (directorio / f"{version}.txt").read_text(encoding="utf-8")
        self._esquema = json.loads((directorio / "esquema.json").read_text(encoding="utf-8"))

    def construir_prompt(self, id_fragmento: str, codigo: str) -> str:
        seguro = neutralizar_delimitadores(codigo.rstrip("\n"))
        prompt = _MARCADOR_ID.sub(lambda _: id_fragmento, self._plantilla)
        return _MARCADOR_CODIGO.sub(lambda _: seguro, prompt).rstrip("\n")   # igual que promptfoo

    def revisar(self, id_fragmento: str, codigo: str) -> dict:
        texto = self._proveedor.completar(self.construir_prompt(id_fragmento, codigo))
        try:
            informe = json.loads(texto)
            validate(informe, self._esquema)             # capa 3: contrato de salida
        except (json.JSONDecodeError, ValidationError) as e:
            raise SalidaInvalida(f"{self.version}/{id_fragmento}: {str(e).splitlines()[0]}") from e
        if informe["fragmento_id"] != id_fragmento:
            raise SalidaInvalida(f"{self.version}/{id_fragmento}: responde por otro fragmento "
                                 f"({informe['fragmento_id']})")
        if informe["seguro"] == bool(informe["hallazgos"]):
            raise SalidaInvalida(f"{self.version}/{id_fragmento}: 'seguro' contradice los hallazgos")
        return informe
