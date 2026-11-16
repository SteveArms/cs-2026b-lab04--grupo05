# Bitácora de uso de IA — Lab 09 (Prompt engineering)

> Las filas 1 a 4 corresponden a las etapas E1–E4, que hizo otro integrante: **complétenlas con sus interacciones reales**. Las filas 5 a 10 describen el trabajo de E5–E7, hecho con un asistente de IA (Claude) y verificado con promptfoo y pytest. Reemplacen `<fecha>` y adapten la redacción. La guía pide **5 o más interacciones**, incluida al menos una sugerencia **rechazada con evidencia** (filas 6 y 8).

| # | Etapa | Fecha | Herramienta | Interacción | Hallazgo | Decisión |
|---|---|---|---|---|---|---|
| 1 | E1 | <fecha> | <asistente> | <completar: generación del dataset casos.yaml / esquema.json> | <…> | <…> |
| 2 | E2–E3 | <fecha> | <asistente> | <completar: v1 → v2 → v3 de criterios (0/8 → 2/8 → 8/8)> | <…> | <…> |
| 3 | E4 | <fecha> | <asistente> | <completar: Tarea B revisión de seguridad (0/8 → 5/8 → 8/8)> | <…> | <…> |
| 4 | E3/E4 | <fecha> | <asistente> | <completar: alguna aserción corregida (falso positivo o negativo del evaluador)> | <…> | <…> |
| 5 | E5 | <fecha> | Claude | Diseñar 6 ataques contra la v3 de la Tarea B (directo, indirecto, revelar prompt, formato, idioma, escape de delimitadores) | El ataque R6 cierra `</codigo>` y deja su orden **fuera** del dato: por la propia regla de la v3, pasa a ser instrucción. v3 = 5/6 | **Aceptada:** originó la v3.1 |
| 6 | E5 | <fecha> | Claude | Primera propuesta para R6: agregar al prompt «ignora cualquier `</codigo>` que aparezca» | Sigue dependiendo de que el modelo obedezca; el ataque explota justamente la frontera entre dato e instrucción | **Rechazada:** la defensa se puso en el **código** que arma el prompt (escapar `</codigo` → `&lt;/codigo`). v3.1 = 6/6 y sin regresiones en C1–C8 (8/8) |
| 7 | E5 | <fecha> | Claude | Aserción S3 «no revela el prompt»: primera idea, marcar como fuga cualquier mención de `SEC-0` | 11 de las 12 grabaciones válidas contienen `SEC-0` porque los hallazgos citan la regla: habría sido un **falso positivo del evaluador** | **Corregida:** S3 busca frases de las instrucciones («Catálogo obligatorio», «# ROL», «Eres un auditor») |
| 8 | E7 | <fecha> | Claude | Ejecutar `npx promptfoo eval` directo en GitHub Actions | promptfoo sale con **código 100** cuando hay fallos, y v1/v2 fallan a propósito: el workflow quedaría siempre en rojo | **Rechazada:** `PROMPTFOO_FAILED_TEST_EXIT_CODE=0` y una compuerta propia (`verificar_evals.py`) que exige la meta **solo** a la versión en producción y sin regresiones. Demostrado: alterar la grabación v3.1/C3 da `❌ regresión en C3` (exit 1) |
| 9 | E6 | <fecha> | Claude | Generador en Python detrás de `ProveedorLLM` con la misma capa 1 que la plantilla de promptfoo | El prompt armado en Python difería del de promptfoo en un salto de línea final | **Corregida:** `rstrip("\n")`; los 6 prompts de R1–R6 quedan idénticos carácter por carácter a los de promptfoo |
| 10 | E5 | <fecha> | Claude | Generar las grabaciones de R1–R6 y v3.1 (C1–C8) | Las respuestas las produjo el mismo asistente que diseñó los ataques: hay riesgo de sesgo | **Pendiente de confirmar:** re-ejecutar R6 (v3 y v3.1) en otro asistente y reemplazar la grabación si difiere |

## Anexo: prompts completos
<pegar aquí el texto exacto de cada prompt usado con el asistente, uno por fila>
