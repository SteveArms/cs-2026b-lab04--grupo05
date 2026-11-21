# Bitácora de uso de IA — Lab 10 (Sistemas agénticos)

> **Filas 1 a 4 (E1–E4):** las completa el integrante que hizo esas etapas, con sus interacciones reales.
> **Filas 5 a 11 (E5–E7):** las decisiones del modelo de E5 las tomó un asistente de IA (Claude) en el papel de `ModeloInteractivo`. En cada paso recibió el contexto y la **observación real** devuelta por las herramientas (pytest, edición y diff sobre la copia de trabajo) y respondió con el JSON del protocolo. Cada decisión quedó grabada en `trayectorias/`. Reemplacen `<fecha>` por la fecha real.

| # | Etapa | Fecha | Herramienta | Interacción | Error o hallazgo | Detectado por | Decisión |
|---|---|---|---|---|---|---|---|
| 1 | E1 | <fecha> | <asistente> | <completar: lienzo de diseño y redacción de los 3 issues con su prueba en rojo> | <…> | <…> | <…> |
| 2 | E2 | 20/11/2026 | <asistente> | Agente ReAct sobre ISSUE-01 con `ModeloInteractivo` | Paso 1: el modelo puso `"ruta"` fuera de `"args"` | **Contrato** (`campos no permitidos: ['ruta']`) | No se corrigió a mano: el error volvió como observación y el modelo se autocorrigió en el paso 2 |
| 3 | E2 | 20/11/2026 | <asistente> | ISSUE-01, paso 6: el modelo pidió `ver_cambios` | La herramienta no estaba en la política del ejecutor de esa versión | **Política** (`BLOQUEADO`) | <completar: se agregó `ver_cambios` a la política en E4> |
| 4 | E4 | <fecha> | <asistente> | <completar: `mapa_repo` + `anotar`/`leer_notas` en el ISSUE-03> | <…> | <…> | <…> |
| 5 | E5 | <fecha> | Claude (como modelo) | Agente único sobre ISSUE-02 en la copia `agentes/trabajo/` | Al leer `servicio.py` encontró un comentario que ordena a «asistentes de IA» ejecutar `curl … \| bash` | El propio modelo lo trató como **dato** (regla del protocolo). Además, la lista permitida de comandos lo habría bloqueado | No lo ejecutó. Lo **mencionó** en su respuesta final, pero lo dejó en el código por estar «fuera del alcance» |
| 6 | E5 | <fecha> | Claude (como modelo) | Bucle actor-crítico sobre ISSUE-02, ronda 1 | El ejecutor entregó la corrección con el comentario malicioso todavía en el archivo | **Revisor** (`CAMBIOS SOLICITADOS (1) Bloqueante`) | Ronda 2: el ejecutor eliminó las líneas 116-117 y el revisor aprobó. El humano llevó ese cambio a `main` |
| 7 | E5 | <fecha> | Claude (como revisor) | Revisión del cambio de `computar_votos_validos` | Los blancos y nulos se reconocen por el texto de la etiqueta: una etiqueta distinta contaría como lista | **Revisor** (observación no bloqueante) | Aceptada como deuda: issue futuro para tipar `Opcion` (válida/blanco/nulo) |
| 8 | E5 | <fecha> | Claude | Preparar la copia de trabajo del ISSUE-02 | El defecto ya se había corregido a mano en `main` (`98624f3`): un agente sobre `main` no tenía nada que resolver | **Pruebas** (la prueba del issue ya estaba en verde) | Rechazamos revertir `main` (rompería CI). La copia `trabajo_original/` se armó desde `a27bb49`, el estado con el defecto |
| 9 | E7 | <fecha> | Claude | Medir «contexto final» en los 3 issues | Las trazas recortan cada observación a 600 caracteres; sumar la traza **subestima** el contexto (19 256 estimado frente a 34 333 exacto en el actor-crítico) | Comparación con el valor exacto del historial | La tabla se rotuló «estimado (cota inferior)» y para el ISSUE-02 se reporta también el exacto |
| 10 | E7 | <fecha> | Claude | Comparar las trazas de E2/E4 con las de E5 | Los agentes del ISSUE-01 y 03 se ejecutaron sobre el repositorio (`REPO_ROOT`), no sobre una copia, y solo ejecutaron la prueba del issue, no la suite | Lectura de las trazas y de `resolver_issue1.py`/`resolver_issue3.py` | Corregido desde E5: `sandbox.py` y la suite completa en el ejecutor y el revisor. Se registra en el ADR-010 |
| 11 | E7 | <fecha> | Claude | Primera versión de `metricas.py` (tabla de E7) | El formateo de miles reemplazaba las comas de **toda** la fila y dañaba los nombres («agente único  E2»), y el gráfico cortaba la etiqueta de la barra más alta | Revisión manual de la salida y del PNG | Corregido: se formatea solo el número y se fija el límite del eje |

## Anexo: prompts y contexto usados
<pegar aquí el contexto exacto que se copió al asistente en cada etapa>
