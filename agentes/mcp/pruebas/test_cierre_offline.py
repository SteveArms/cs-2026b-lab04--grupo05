"""Pruebas de catálogo, esquemas y trayectoria sin conexiones ni LLM."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace

from agentes.mcp.agente.herramientas_mcp import HerramientasMCP
from agentes.mcp.cliente.auditar import auditar
from agentes.mcp.cliente.traza_mcp import catalogo, leer_jsonl

LAB = Path(__file__).resolve().parents[1]


def test_exige_anotacion_destructiva_en_posible_escritura():
    herramienta = {'name': 'guardar', 'annotations': {'readOnlyHint': False}}
    assert list(auditar([herramienta])) == [('MEDIA', 'guardar', 'posible escritura sin destructiveHint explícito')]
    herramienta['annotations']['destructiveHint'] = False
    assert list(auditar([herramienta])) == []
    herramienta['annotations'] = {'readOnlyHint': True}
    assert list(auditar([herramienta])) == []


def test_detecta_texto_sin_limite():
    propiedades = {nombre: {'type': 'string', **limite} for nombre, limite in [
        ('libre', {}), ('acotado', {'maxLength': 30}), ('opciones', {'enum': ['a', 'b']}),
        ('fijo', {'const': 'a'}),
    ]}
    herramienta = {'name': 'consultar', 'annotations': {'readOnlyHint': True},
                   'inputSchema': {'properties': propiedades}}
    assert list(auditar([herramienta])) == [('MEDIA', 'consultar', "texto 'libre' sin límite en inputSchema")]


def test_catalogo_abreviado_conserva_trayectoria():
    tools = catalogo(leer_jsonl(LAB / 'trazas/mcp_trafico.jsonl'))
    fuente = LAB / 'servidor_mcp/votoepis_mcp.py'
    arbol = ast.parse(fuente.read_text(encoding='utf-8'))
    nuevas = {n.name: ast.get_docstring(n) for n in arbol.body if isinstance(n, ast.FunctionDef)}
    adaptador = object.__new__(HerramientasMCP)
    adaptador._exponer_recursos = True
    adaptador._tools = {t['name']: SimpleNamespace(description=t['description'], input_schema=t['inputSchema'])
                        for t in tools}
    original = adaptador.catalogo()
    for nombre, tool in adaptador._tools.items():
        tool.description = nuevas[nombre]
    abreviado = adaptador.catalogo()
    tamanos = [len(json.dumps(v, ensure_ascii=False)) for v in (original, abreviado)]
    print(f'Catálogo del agente (caracteres): {tamanos[0]} → {tamanos[1]}')
    assert tamanos[1] < tamanos[0]
    assert original.keys() == abreviado.keys()
    trayectoria = json.loads((LAB / 'trayectorias/analista.json').read_text(encoding='utf-8'))
    for paso in trayectoria:
        if 'accion' in paso:
            assert paso['accion'] in abreviado
            assert all(arg in abreviado[paso['accion']] for arg in paso['args'])
