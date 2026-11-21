# E6. Humano en el circuito y delegación progresiva — VotoEPIS

## 1. Aprobación humana de ediciones (activa)
En el ejecutor del orquestador se conecta `humano.aprobar_por_consola` a la política:

```python
politica_ejecutor = Politica(max_pasos=12)
politica_ejecutor.aprobar_edicion = aprobar_por_consola   # python orquestador.py --aprobar
```

- Antes de cada `editar_archivo`, la consola muestra el archivo, el fragmento **ANTES** y el **DESPUÉS**, y pregunta `¿Aprueba esta edición? [s/n]`.
- **La entrada humana también se valida:** solo se acepta `s` o `n`. Cualquier otra respuesta («si», vacío, «ok») se vuelve a pedir.
- Si el integrante responde `n`, la política devuelve `BLOQUEADO POR LA POLÍTICA: El revisor humano rechazó la edición`. Esa observación vuelve al agente y el archivo **no cambia**.
- Cada decisión queda en `trazas/aprobaciones.jsonl` (momento, ruta, APROBADA/RECHAZADA) como evidencia auditable.

Pruebas en `pruebas_agente/test_agente.py`:
- `test_humano_solo_acepta_s_o_n`
- `test_humano_rechaza_y_se_registra`
- `test_politica_con_humano_bloquea_la_edicion_rechazada`: el archivo queda igual y la traza registra `BLOQUEADO`.

Con esto el sistema tiene **dos** puntos de control humano: la aprobación de cada edición y la aprobación del Pull Request.

## 2. Hoja de ruta de autonomía para VotoEPIS

VotoEPIS cuenta votos: un error del agente afecta la integridad del sufragio (ADR-002) y la confianza en el escrutinio. Por eso la autonomía se concede **por evidencia** y **por zona del código**. `src/votacion/` y `src/padron/` son zonas críticas; `docs/` y `fitness/` no lo son.

| Etapa | Rol del humano | Permisos del agente | Qué evidencia de las trazas justifica pasar a la siguiente |
|---|---|---|---|
| **1. Ejecutor** (inicio) | El humano inicia cada tarea y ejecuta él mismo los cambios | Solo lectura: `listar_archivos`, `leer_archivo`, `buscar`, `mapa_repo`, `ejecutar_pruebas`. Propone el parche como texto | En 10 issues seguidos, el diagnóstico del agente (archivo, línea y causa) coincide con el del humano. 0 acciones bloqueadas por intentar comandos fuera de la lista |
| **2. Revisor** (**donde está hoy**) | El agente edita en la **copia**; el humano aprueba **cada edición** (`--aprobar`) y el PR | + `editar_archivo` solo en la copia `agentes/trabajo/`, `tests/` protegido, comandos en lista permitida, máx. 12 pasos y 2 rondas | En `aprobaciones.jsonl`, ≥ 95 % de ediciones aprobadas en al menos 20 ediciones. 0 cambios en `tests/`. 0 regresiones detectadas después en CI. El revisor-agente detecta lo mismo que el humano (por ejemplo, la inyección del ISSUE-02) |
| **3. Colaborador** | Humano y agente comparten contexto (`notas.md`) y refinan juntos. El humano aprueba **solo el PR**, no cada edición, en zonas **no críticas** | + Ediciones sin aprobación una a una en `docs/`, `fitness/` y pruebas nuevas del agente (no las existentes). En `src/votacion/` sigue la aprobación por edición | 3 meses sin incidentes. Fitness functions FF-01 a FF-09 siempre en verde en los PR del agente. Trazas con 0 decisiones fuera de contrato en las últimas 50 corridas |
| **4. Gobernador** | El humano fija objetivos, límites y presupuestos, y **audita** trazas por muestreo | Abre PR por sí mismo para issues etiquetados como `bajo-riesgo`. **Nunca fusiona** y nunca toca `src/votacion/` ni `src/padron/` sin aprobación | Solo si el comité electoral lo autoriza por escrito. Para el código que cuenta votos, el equipo **no recomienda** llegar a esta etapa |

**Dónde lo dejamos hoy: etapa 2 (Revisor).**
- Las trazas muestran que el agente diagnostica bien: 3 de 3 issues resueltos con las pruebas en verde.
- La política ya tuvo que intervenir: en el ISSUE-01 rechazó una decisión fuera de contrato y bloqueó una herramienta no permitida.
- El hallazgo más importante del ISSUE-02, la inyección indirecta, lo resolvió el bucle con revisor y no el agente solo.
- Con 3 issues no hay todavía la muestra que pide la etapa 3.

## 3. Qué nunca se delega
- Fusionar a `main` o crear etiquetas de versión.
- Editar las pruebas existentes (`tests/`), que son el oráculo del agente.
- Usar credenciales, el padrón real o datos personales (Ley 29733). El agente solo trabaja con datos de prueba en la copia.
- Ejecutar comandos fuera de la lista permitida: `pytest`, `radon cc`, `lint-imports` y `git status/diff`.
