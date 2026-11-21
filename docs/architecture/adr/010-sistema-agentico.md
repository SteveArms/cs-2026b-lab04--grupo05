# ADR-010: Arquitectura del sistema agéntico de mantenimiento de VotoEPIS

- **Estado:** Aceptado
- **Fecha:** 2026-11-21
- **Decisores:** Cuno Cahuari Armando Steven, Quiñonez Delgado Aarón Fernando
- **Relacionados:** ADR-001 (monolito modular), ADR-002 (secreto e integridad del voto), ADR-005 (patrones: Strategy), Lab 10

## Contexto
VotoEPIS acumula defectos reportados como issues (ISSUE-01 a 03: doble voto por mayúsculas, blancos y nulos sumados a un candidato, cierre prematuro de mesa). Queremos que un sistema basado en LLM ayude a diagnosticarlos y corregirlos. El código toca el **conteo de votos**, así que un cambio incorrecto o una instrucción maliciosa obedecida afecta directamente la integridad de la elección (QA-01, QA-02).

Restricciones:
- Sin claves de API en el repositorio.
- Ejecución reproducible en CI.
- El mismo equipo de 2 personas.
- Ningún cambio llega a `main` sin aprobación humana.

## Alternativas consideradas
| # | Alternativa | Por qué se descartó o se eligió |
|---|---|---|
| 1 | **Flujo de trabajo fijo** (script: correr pruebas, aplicar parche, volver a correr) | No sirve para diagnosticar: los pasos dependen de lo que se encuentre en el código. **Sí** se mantiene como flujo fijo la carga y validación del padrón (determinista, datos personales) |
| 2 | **Agente único ReAct** con todas las herramientas | Resolvió los 3 issues (pruebas en verde) con 7 a 9 pasos. Pero en el ISSUE-02 dejó en el código una inyección indirecta que solo mencionó |
| 3 | **Coordinación democrática** (3 revisores que votan) | Triplica el costo del revisor sin un hallazgo que lo justifique en 3 issues |
| 4 | **Agente comercial con acceso directo al repositorio** | Más autonomía y permisos de los necesarios (exceso de agencia, OWASP LLM06). Sin traza propia que auditar |
| 5 | **Planificador-ejecutor + ReAct, coordinación por gestor con bucle actor-crítico** | **Elegida** para cambios en `src/votacion/` y `src/padron/` (ver abajo) |

## Decisión
| Elemento | Elección |
|---|---|
| **Arquetipo** | Planificador-ejecutor (plan corto y legible) + ReAct en el ejecutor (exploración) |
| **Coordinación** | Por gestor (`orquestador.py`): planificador → ejecutor (actor) ↔ revisor (crítico), **máx. 2 rondas**. Para issues de bajo riesgo fuera de esas zonas, agente único (parsimonia) |
| **Herramientas** | Pocas y documentadas en `catalogo()`: `listar_archivos`, `leer_archivo`, `buscar`, `mapa_repo` (AST), `editar_archivo` (fragmento exacto, una vez), `ejecutar_pruebas`, `ver_cambios`, `ejecutar_comando` (lista permitida), `anotar`/`leer_notas` |
| **Mínimo privilegio por rol** | Planificador: solo lectura, máx. 4 pasos. Ejecutor: todas, con `tests/` protegido y máx. 12 pasos. Revisor: `ver_cambios`, `leer_archivo`, `buscar`, `ejecutar_pruebas`, **sin edición**, máx. 8 pasos |
| **Memoria** | Corto plazo (historial de cada agente) + notas (`notas.md`) para hipótesis. Sin memoria episódica entre issues todavía |
| **Control** | Contrato JSON validado **antes** de actuar (`contrato.py`), política (`politica.py`), presupuesto de pasos y rondas, y traza JSONL de cada transición de la máquina de estados (`diseno/estados.puml`) |
| **Aislamiento** | Todo agente trabaja en una **copia** (`agentes/trabajo/`, creada por `sandbox.py` con un commit local), nunca sobre `src/` ni `main` |
| **Modelo** | Interfaz `Modelo` como Strategy (ADR-005): `ModeloGrabado` (CI y reproducción), `ModeloInteractivo` (sin clave), `ModeloAnthropic` (clave solo en variable de entorno) |
| **Rol humano** | **Revisor** (`delegacion.md`): aprueba cada edición con `--aprobar` (solo `s`/`n`, registrado en `aprobaciones.jsonl`) y siempre aprueba el Pull Request. El agente nunca fusiona |

## Evidencia
- **3 de 3 issues resueltos**, con su prueba en verde y 0 cambios en `tests/` (`agentes/observacion.md`).
- **El contrato funcionó:** rechazó una decisión mal formada en el ISSUE-01 (`campos no permitidos: ['ruta']`) y el modelo se autocorrigió.
- **La política funcionó:** bloqueó una herramienta no permitida en el ISSUE-01.
- **El actor-crítico aportó en el ISSUE-02:** 17 frente a 8 acciones y 34 333 frente a 16 636 caracteres de contexto (unas 2,1 veces). A cambio, el revisor exigió eliminar el comentario de inyección indirecta (`curl … | bash`) que el agente único había dejado (`agentes/coordinacion.md`).
- **Pruebas del propio agente:** 20 pruebas en `pruebas_agente/` (contrato, política, sandbox, herramientas, memoria y humano en el circuito) y 112 pruebas del proyecto en verde.

## Consecuencias
**Positivas:**
- Cada decisión del modelo es auditable (traza y diagrama generados).
- Una instrucción maliciosa en un archivo necesita atravesar varias capas: protocolo, lista de comandos, revisor y humano.
- El sistema es reproducible sin clave de API.

**Negativas y riesgos:**
- El bucle actor-crítico duplica pasos y contexto. Se reserva para zonas críticas.
- Las trazas recortan las observaciones a 600 caracteres, así que el contexto medido desde la traza es una cota inferior.
- Los blancos y nulos se identifican por el texto de la etiqueta (deuda detectada por el revisor).
- Las corridas de E2 y E4 (ISSUE-01 y 03) se hicieron sobre el repositorio y no sobre una copia. Desde E5 es obligatorio `sandbox.py`.

**Revisión de esta decisión:** al completar 20 ediciones aprobadas (criterio de la etapa 3 en `delegacion.md`), o si un agente intenta modificar `tests/` o ejecutar un comando fuera de la lista.
