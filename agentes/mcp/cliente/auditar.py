"""Audita descripciones y esquemas MCP desde una traza o fuente Python estática."""
import argparse
import ast
import re
from pathlib import Path

from .traza_mcp import catalogo, leer_jsonl

PATRONES = (
    ('ALTA', r'<\s*important\s*>|\bignora\b|ignore (all|previous)|no (le )?(menciones|digas)',
     'instrucciones dirigidas al modelo'),
    ('ALTA', r'\.env\b|id_rsa|\.ssh|credencial|password|contraseña|token|api[_ ]?key',
     'referencia a secretos o credenciales'),
    ('ALTA', r'\bcurl\s|\bwget\s|https?://', 'comandos o enlaces en la descripción'),
    ('MEDIA', r'(lee|read).{0,40}(archivo|file|recurso|resource)', 'solicita leer datos ajenos'),
)


def auditar(herramientas):
    for tool in herramientas:
        nombre = tool['name']
        descripcion = tool.get('description') or ''
        for nivel, patron, motivo in PATRONES:
            if re.search(patron, descripcion, re.IGNORECASE):
                yield nivel, nombre, motivo
        anotaciones = tool.get('annotations') or {}
        if not anotaciones:
            yield 'BAJA', nombre, 'sin anotaciones'
        if anotaciones.get('readOnlyHint') is not True and not isinstance(anotaciones.get('destructiveHint'), bool):
            yield 'MEDIA', nombre, 'posible escritura sin destructiveHint explícito'
        for parametro, esquema in tool.get('inputSchema', {}).get('properties', {}).items():
            if parametro in {'contexto', 'context', 'notas', 'notes', 'extra', 'metadata', 'debug'}:
                yield 'MEDIA', nombre, f"parámetro genérico '{parametro}'"
            if esquema.get('type') == 'string' and not esquema.keys() & {'maxLength', 'enum', 'const'}:
                yield 'MEDIA', nombre, f"texto '{parametro}' sin límite en inputSchema"


def desde_fuente(path):
    """Lee docstrings y parámetros str simples de funciones decoradas con .tool."""
    arbol = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    for nodo in arbol.body:
        if not isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decoradores = (d.func if isinstance(d, ast.Call) else d for d in nodo.decorator_list)
        if not any(isinstance(d, ast.Attribute) and d.attr == 'tool' for d in decoradores):
            continue
        parametros = [*nodo.args.posonlyargs, *nodo.args.args, *nodo.args.kwonlyargs]
        propiedades = {p.arg: {'type': 'string'} for p in parametros
                       if isinstance(p.annotation, ast.Name) and p.annotation.id == 'str'}
        yield {'name': nodo.name, 'description': ast.get_docstring(nodo),
               'inputSchema': {'properties': propiedades}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    entradas = parser.add_mutually_exclusive_group(required=True)
    entradas.add_argument('--traza', type=Path)
    entradas.add_argument('--fuente', type=Path)
    args = parser.parse_args()
    if args.traza:
        print('Origen: catálogo tools/list de E4')
        herramientas = catalogo(leer_jsonl(args.traza))
    else:
        print(f'Origen: {args.fuente.name} (lectura estática)')
        herramientas = desde_fuente(args.fuente)
    hallazgos = list(auditar(herramientas))
    for nivel, herramienta, motivo in hallazgos:
        print(f'[{nivel:<5}] {herramienta}: {motivo}')
    if not hallazgos:
        print('Sin hallazgos')
    return int(any(nivel == 'ALTA' for nivel, _, _ in hallazgos))


if __name__ == '__main__':
    raise SystemExit(main())
