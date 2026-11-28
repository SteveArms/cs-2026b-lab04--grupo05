"""Espía de stdio: se coloca entre el host y el servidor MCP, reenvía cada línea SIN cambiarla
y la guarda en un archivo JSONL (una línea por mensaje JSON-RPC, con dirección, tiempo y tamaño).

Uso:  python espia.py <traza.jsonl> <comando del servidor> [argumentos...]
      p. ej. python espia.py trazas/mcp_trafico.jsonl python servidor_mcp/votoepis_mcp.py
"""
import json
import subprocess
import sys
import threading
import time


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    traza, comando = sys.argv[1], sys.argv[2:]
    t0 = time.perf_counter()
    candado = threading.Lock()
    registro = open(traza, "a", encoding="utf-8")
    servidor = subprocess.Popen(comando, stdin=subprocess.PIPE, stdout=subprocess.PIPE)   # stderr se hereda

    def anotar(direccion: str, linea: bytes) -> None:
        texto = linea.decode("utf-8", errors="replace").rstrip("\r\n")
        try:
            mensaje = json.loads(texto)
        except json.JSONDecodeError:
            mensaje = {"no_json": texto}
        with candado:
            registro.write(json.dumps({"t_ms": round((time.perf_counter() - t0) * 1000, 2), "dir": direccion,
                                       "bytes": len(linea), "msg": mensaje}, ensure_ascii=False) + "\n")
            registro.flush()

    def host_a_servidor() -> None:
        for linea in iter(sys.stdin.buffer.readline, b""):
            anotar("host->servidor", linea)
            servidor.stdin.write(linea)
            servidor.stdin.flush()
        servidor.stdin.close()                             # el host cerró: el servidor termina

    threading.Thread(target=host_a_servidor, daemon=True).start()
    for linea in iter(servidor.stdout.readline, b""):
        anotar("servidor->host", linea)
        sys.stdout.buffer.write(linea)
        sys.stdout.buffer.flush()
    registro.close()
    return servidor.wait()


if __name__ == "__main__":
    sys.exit(main())
