# E4. El agente del Lab 10 usando el servidor MCP

**Qué cambió del Lab 10:** solo las herramientas. El núcleo ReAct (`agentes/agente/nucleo.py`), el contrato y el modelo siguen igual. Las herramientas ahora llegan del servidor `votoepis` a través de `agentes/mcp/agente/herramientas_mcp.py`, un **Adapter** (Lab 07) que ofrece la misma interfaz que las herramientas locales del Lab 10: `catalogo()` y una función por herramienta.

| Pieza | Archivo | Cambio |
|---|---|---|
| Adaptador MCP → interfaz del Lab 10 | `agentes/mcp/agente/herramientas_mcp.py` | **Nuevo**. Descubre el catálogo en tiempo de ejecución, agrega `leer_recurso` (decisión del host) y deriva de las anotaciones qué herramientas escriben |
| Política ampliada | `agentes/agente/politica.py` | `requieren_aprobacion` + `aprobar_accion(accion, args)`. **Falla cerrado**: si una herramienta escribe y no hay revisor, se bloquea |
| Humano en el circuito | `agentes/humano.py` | `pedir_respuesta` acepta el texto de la pregunta. Sigue aceptando solo `s`/`n` |
| Espía de stdio | `agentes/mcp/cliente/espia.py` | Nuevo. Se coloca entre el agente y el servidor y guarda cada mensaje JSON-RPC en `trazas/mcp_trafico.jsonl` |
| Agente analista | `agentes/mcp/analista.py` | Nuevo. Arma la política, conecta por el espía y ejecuta la consulta |

Cadena de conexión: `analista.py` (host) → `espia.py` → `votoepis_mcp.py` (servidor), todo por **stdio**.

## Consulta de negocio
> «El comité electoral pide un reporte breve: (1) el resultado oficial de la elección *Delegados EPIS 2026*, con los votos válidos y la lista ganadora; (2) la participación actual de la elección *Tercio estudiantil 2026*. Si en Delegados los votos en blanco y nulos superan el 15 % de la participación, registra una observación para el comité. Respeta el reglamento electoral.»

Requiere un recurso, 2 consultas a `resultados_parciales` (3 llamadas, contando el error) y **una escritura** (`registrar_observacion`).

## Cómo se ejecuta
```bash
pip install -r agentes/mcp/requirements.txt
python agentes/mcp/analista.py                # decisiones grabadas, herramientas reales vía MCP; usted aprueba la escritura
python agentes/mcp/analista.py --interactivo  # usted copia el contexto a su asistente y pega cada decisión
```
Cuando el agente llega a `registrar_observacion`, la consola muestra los argumentos y pregunta `¿Aprueba ejecutar esta herramienta? [s/n]`. La decisión queda en `trazas/aprobaciones_mcp.jsonl`.

## Trayectoria (decisiones grabadas, herramientas reales vía MCP)

| Paso | Pensamiento (resumen) | Acción vía MCP | Observación real |
|---|---|---|---|
| 1 | Revisar qué se puede informar en cada estado | `leer_recurso("votoepis://reglamento")` | Reglamento: el conteo solo tras el escrutinio |
| 2 | Consultar Delegados | `resultados_parciales("Delegados EPIS 2026")` | **ERROR:** «Elección desconocida… Códigos válidos: E-2026-DELEGADOS, E-2026-TERCIO, E-2027-ETICA» |
| 3 | Corregirse con el código que indica el error | `resultados_parciales("E-2026-DELEGADOS")` | PUBLICADA, 100 votantes; Lista A 46, Lista B 38, blanco 10, nulo 6 |
| 4 | Participación del Tercio | `resultados_parciales("E-2026-TERCIO")` | ABIERTA, 40 votantes; `conteo: null` (ADR-002) |
| 5 | 16 % > 15 %: registrar observación (escritura) | `registrar_observacion(...)` | **Aprobada por el humano**; `Creado OBS-01.md` |
| 6 | Responder | `final` | Gana la Lista A (46 vs 38); 16 % de blancos y nulos con observación registrada; Tercio con 40 votantes y sin conteo |

- **Error corregido solo (paso 2 → 3):** el agente usó el nombre de la elección en vez de su código. El servidor respondió con `isError: true` y la lista de códigos válidos (`ToolError`), y el modelo se corrigió en el paso siguiente sin intervención humana. Es un error de **negocio**, no de protocolo: viaja como resultado y el modelo lo puede leer.
- **Escritura aprobada:** la política del analista se construyó con `requieren_aprobacion = h.herramientas_de_escritura()`, que da `{"registrar_observacion"}` a partir de `readOnlyHint=false`. Sin aprobación no se escribe nada (`test_si_el_humano_rechaza_no_se_escribe_nada`).
- **El agente respetó el secreto del voto:** no pidió ni reportó el conteo del Tercio, que sigue ABIERTA, y la observación no contiene datos personales (el servidor la habría rechazado).

## Evidencia generada
- `trayectorias/analista.json`: las 6 decisiones del modelo.
- `trazas/analista.jsonl`: la traza del núcleo ReAct (estados, acciones y observaciones).
- `trazas/mcp_trafico.jsonl`: los 14 mensajes JSON-RPC capturados por el espía (`server/discover`, `tools/list`, `resources/read` y 4 `tools/call`). Se analiza en E6.
- `trazas/aprobaciones_mcp.jsonl`: la aprobación humana de la escritura.
- `observaciones/OBS-01.md`: la observación creada.
- `pruebas/test_agente_mcp.py`: 3 pruebas que reproducen la trayectoria con el servidor real por stdio (aprobada, rechazada y política sin revisor).

> **Sobre las decisiones del modelo:** las tomó un asistente de IA (Claude) en el papel de `ModeloInteractivo`, paso a paso y sobre las observaciones reales que devolvió el servidor. Así se registra en la bitácora (E7). Para reproducirlas con su propio asistente use `--interactivo`.
