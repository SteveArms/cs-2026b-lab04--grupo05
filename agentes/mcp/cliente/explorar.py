"""Explora el servidor MCP de VotoEPIS como lo haría un host: lo lanza por stdio, descubre su catálogo
en tiempo de ejecución y hace algunas llamadas de prueba.

Uso (desde la raíz del repositorio):  python agentes/mcp/cliente/explorar.py
"""
import asyncio
import json
import pathlib
import sys

from mcp import Client, StdioServerParameters

RAIZ = pathlib.Path(__file__).resolve().parents[3]
SERVIDOR = RAIZ / "agentes" / "mcp" / "servidor_mcp" / "votoepis_mcp.py"


def parametros_servidor() -> StdioServerParameters:
    return StdioServerParameters(command=sys.executable, args=[str(SERVIDOR)], cwd=str(RAIZ))


def tipo(tool) -> str:
    a = tool.annotations
    return "solo lectura" if a and a.read_only_hint else "ESCRITURA"


async def main() -> None:
    async with Client(parametros_servidor()) as c:
        print(f"Servidor: {c.server_info.name} | protocolo {c.protocol_version}\n")
        print("HERRAMIENTAS (las elige el modelo):")
        for t in (await c.list_tools()).tools:
            params = ", ".join(t.input_schema.get("properties", {}))
            print(f"  - {t.name}({params})  [{tipo(t)}]")
        print("\nRECURSOS (los elige la aplicación):")
        for r in (await c.list_resources()).resources:
            print(f"  - {r.uri}  {r.title or r.name}")
        for r in (await c.list_resource_templates()).resource_templates:
            print(f"  - {r.uri_template}  {r.title or r.name} (plantilla)")
        print("\nPROMPTS (los elige el usuario):")
        for p in (await c.list_prompts()).prompts:
            print(f"  - {p.name}({', '.join(a.name for a in p.arguments or [])})")

        print("\nPRUEBAS DE USO:")
        r = await c.call_tool("resultados_parciales", {"eleccion_id": "E-2026-DELEGADOS"})
        print("  resultados_parciales(E-2026-DELEGADOS) ->", json.dumps(r.structured_content, ensure_ascii=False))
        r = await c.call_tool("resultados_parciales", {"eleccion_id": "E-2026-TERCIO"})
        print("  resultados_parciales(E-2026-TERCIO)    ->", json.dumps(r.structured_content, ensure_ascii=False))
        r = await c.call_tool("estado_eleccion", {"eleccion_id": "Delegados"})
        print(f"  estado_eleccion(Delegados) -> is_error = {r.is_error} | {r.content[0].text[:110]}")
        rr = await c.read_resource("votoepis://adr/002")
        print("  read_resource(adr/002) ->", rr.contents[0].text.splitlines()[0])
        p = await c.get_prompt("redactar_acta", {"eleccion_id": "E-2026-DELEGADOS"})
        print("  get_prompt(redactar_acta) ->", p.messages[0].content.text[:90], "…")


if __name__ == "__main__":
    asyncio.run(main())
