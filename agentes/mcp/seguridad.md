# E7. Auditoría y controles de VotoEPIS

El auditor encontró cinco propiedades de texto sin límite publicado en `inputSchema` en la captura de `tools/list` de E4. La única escritura declaró `destructiveHint: false`. El servidor valida en tiempo de ejecución el código, el título y la descripción. Las anotaciones del catálogo sirven para orientar la política del host.

La lectura estática de `terceros/clima_mcp.py` encontró siete alertas, dos de severidad alta por instrucciones dirigidas al modelo y referencias a secretos. El análisis leyó la fuente mediante AST. El servidor de ejemplo quedó fuera de los hosts.

| Control | Verificación |
| --- | --- |
| Mínimo privilegio | Tres herramientas de lectura y una que crea observaciones. El ciclo electoral permanece dentro de la aplicación. |
| Validación de entradas | Código conocido, título de 5 a 80 caracteres y descripción de 20 a 2000. Filtro de correos y secuencias de ocho dígitos. |
| Rutas seguras | La plantilla de ADR exige tres dígitos. El servidor fija el directorio y crea `OBS-NN.md` mediante apertura exclusiva. |
| Ausencia de secretos | Las cuentas y los OTP del conjunto de demostración son ficticios. La configuración local contiene rutas y variables de arranque. |
| Aprobación de escritura | La política de E4 exige aprobación y la traza conserva la decisión. En E5, el usuario confirmó que Codex mostró el permiso antes de crear la observación. |

Las dos reglas nuevas señalan posibles escrituras sin `destructiveHint` explícito y cadenas de entrada sin `maxLength`, `enum` o `const`. Se probaron casos con y sin hallazgos. La tercera prueba comprobó la trayectoria del catálogo abreviado.

```bash
python -m agentes.mcp.cliente.auditar --traza agentes/mcp/trazas/mcp_trafico.jsonl
python -m agentes.mcp.cliente.auditar --fuente /ruta/a/terceros/clima_mcp.py
python -m pytest -q agentes/mcp/pruebas/test_cierre_offline.py
```
