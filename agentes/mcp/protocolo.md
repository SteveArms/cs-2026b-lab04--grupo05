# E6. Protocolo y costo de contexto

La [traza de E4](trazas/mcp_trafico.jsonl) registra 14 mensajes JSON-RPC, 11 184 bytes, un error de herramienta y cero errores de protocolo. El analizador empareja solicitudes y respuestas por identificador, resta sus marcas `t_ms` y suma los bytes medidos por el espía.

| Método | Solicitudes | Latencias en ms |
| --- | ---: | --- |
| `server/discover` | 1 | 1 880,79 |
| `tools/list` | 1 | 2,86 |
| `resources/read` | 1 | 4,03 |
| `tools/call` | 4 | 2,08 · 1,82 · 1,91 · 4,30 |

El descubrimiento inicial tuvo la mayor latencia. Entre la respuesta de Tercio y el envío de la observación transcurrieron 48,68 s, intervalo que incluye la revisión humana. La [secuencia generada](trazas/mcp_secuencia.mmd) muestra la consulta con argumento incorrecto, su corrección y la aprobación antes de la escritura.

Se abreviaron las cuatro descripciones sin cambiar el esquema de entrada, los límites de la escritura ni la regla de escrutinio. Al serializar el catálogo del adaptador, incluida la acción `leer_recurso`, pasó de **1 537 a 1 140 caracteres** (25,83 % menos), unos **384 a 285 tokens** a razón de cuatro caracteres por token. La prueba reutilizó el catálogo capturado, sustituyó las descripciones por las actuales y verificó todas las acciones y los argumentos de la trayectoria grabada. Queda pendiente medir la selección de herramientas con una corrida nueva del modelo.

```bash
python agentes/mcp/cliente/traza_mcp.py --diagrama agentes/mcp/trazas/mcp_secuencia.mmd
python -m pytest -q -s agentes/mcp/pruebas/test_cierre_offline.py
```
