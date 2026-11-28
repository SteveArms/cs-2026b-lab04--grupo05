"""Adaptador (patrón Adapter, Lab 07): presenta las herramientas de un servidor MCP con la MISMA
interfaz que las herramientas locales del Lab 10 (catalogo() + una función por herramienta).
Así el núcleo ReAct, el contrato y la política del Lab 10 no cambian.

El cliente MCP es asíncrono y el núcleo del Lab 10 es síncrono: una tarea dueña de la conexión vive en
un hilo con su propio bucle de eventos y atiende las llamadas por una cola.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import json
import threading

from mcp import Client, Implementation, StdioServerParameters


class HerramientasMCP:
    def __init__(self, parametros: StdioServerParameters, exponer_recursos: bool = True,
                 nombre_cliente: str = "agente-lab10", timeout_s: float = 60) -> None:
        self._exponer_recursos, self._timeout = exponer_recursos, timeout_s
        self._loop = asyncio.new_event_loop()
        self._listo = threading.Event()
        self._error: BaseException | None = None
        self._hilo = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._hilo.start()
        self._tarea = asyncio.run_coroutine_threadsafe(
            self._servir(parametros, Implementation(name=nombre_cliente, version="1.1")), self._loop)
        if not self._listo.wait(timeout_s) or self._error:
            raise RuntimeError(f"No se pudo conectar con el servidor MCP: {self._error}")
        self._tools = {t.name: t for t in self._llamar(lambda c: c.list_tools()).tools}

    # ------------------------------------------------------------------ conexión
    async def _servir(self, parametros, info) -> None:
        self._cola: asyncio.Queue = asyncio.Queue()
        try:
            async with Client(parametros, client_info=info) as cliente:
                self.protocolo = cliente.protocol_version
                self._listo.set()
                while True:
                    fn, futuro = await self._cola.get()
                    if fn is None:
                        break
                    try:
                        futuro.set_result(await fn(cliente))
                    except Exception as e:                      # el error vuelve al hilo del agente
                        futuro.set_exception(e)
        except Exception as e:
            self._error = e
            self._listo.set()

    def _llamar(self, fn):
        futuro: concurrent.futures.Future = concurrent.futures.Future()
        self._loop.call_soon_threadsafe(self._cola.put_nowait, (fn, futuro))
        return futuro.result(timeout=self._timeout)

    def cerrar(self) -> None:
        self._loop.call_soon_threadsafe(self._cola.put_nowait, (None, None))
        self._tarea.result(timeout=self._timeout)
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._hilo.join(timeout=5)

    # ------------------------------------------------------------------ interfaz del Lab 10
    def catalogo(self) -> dict:
        cat = {n: f"{t.description.strip()} Parámetros: "
                  f"{json.dumps(t.input_schema.get('properties', {}), ensure_ascii=False)}"
               for n, t in self._tools.items()}
        if self._exponer_recursos:                     # decisión del HOST: los recursos los controla la aplicación
            cat["leer_recurso"] = ("Lee un recurso MCP por URI (votoepis://reglamento, votoepis://elecciones/estados "
                                   "o votoepis://adr/NNN). Parámetros: uri")
        return cat

    def herramientas_de_escritura(self) -> set:
        """Las anotaciones son PISTAS del servidor, no garantías: úselas solo con servidores de confianza."""
        return {n for n, t in self._tools.items() if not (t.annotations and t.annotations.read_only_hint)}

    def leer_recurso(self, uri: str) -> str:
        r = self._llamar(lambda c: c.read_resource(uri))
        return "\n".join(getattr(c, "text", "") for c in r.contents)

    def __getattr__(self, nombre):
        if nombre.startswith("_") or nombre not in self.__dict__.get("_tools", {}):
            raise AttributeError(nombre)

        def invocar(**args):
            r = self._llamar(lambda c: c.call_tool(nombre, args))
            if r.structured_content is not None:
                cuerpo = json.dumps(r.structured_content, ensure_ascii=False)
            else:
                cuerpo = " ".join(getattr(c, "text", "") for c in r.content)
            return ("ERROR: " if r.is_error else "") + cuerpo
        return invocar
