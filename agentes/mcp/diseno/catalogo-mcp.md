# Catálogo MCP del servidor `votoepis` (Lab 11, E1)

**Objetivo:** que cualquier host MCP (VS Code con Copilot, Claude Code, Gemini CLI o el agente del Lab 10) consulte el estado y los resultados de las elecciones de VotoEPIS **sin reescribir integraciones**, y que el comité pueda dejar observaciones. Se expone **lo mínimo**, con una sola escritura y solo para crear.

Datos: **ficticios**. Las elecciones se construyen y los votos se emiten con el código real de `src/votacion` (`ServicioVotacion`, State, Observer); el servidor no duplica la lógica de dominio.

## 1. Qué se expone y con qué primitiva

| Capacidad | Primitiva | ¿Escribe? | Justificación |
|---|---|---|---|
| Elecciones registradas (código, nombre, estado) | Herramienta `listar_elecciones` | No | El modelo necesita descubrir los códigos válidos antes de consultar |
| Estado de una elección | Herramienta `estado_eleccion` | No | Consulta con parámetro que el modelo elige; ciclo de vida del patrón State |
| Participación y resultados | Herramienta `resultados_parciales` | No | Cálculo que usa `conteo()` y `computar_votos_validos()` (ISSUE-02). **El conteo por lista solo se devuelve tras el escrutinio** (ADR-002) |
| Registrar una observación del comité | Herramienta ★ `registrar_observacion` | **Sí, solo crea** | Única escritura: crea `OBS-NN.md` nuevo; nunca edita ni borra |
| Reglamento electoral | Recurso `votoepis://reglamento` | No | Contexto estable; lo decide el host, no el modelo |
| Estados de la elección | Recurso `votoepis://elecciones/estados` | No | Contexto estable del dominio (Lab 05/07) |
| ADR del proyecto | Recurso plantilla `votoepis://adr/{numero}` | No | Decisiones del equipo por URI; rechaza rutas como `../` |
| Redactar el acta de escrutinio | Prompt `redactar_acta(eleccion_id)` | No | Plantilla que el usuario invoca; trae los datos oficiales para que el modelo no invente cifras |
| Revisión de seguridad de código | Prompt `revisar_seguridad(codigo)` | No | Reutiliza el prompt **v3.1 del Lab 09** (SEC-01..06, delimitadores neutralizados) |

**Qué NO se expone (y por qué):**
- `emitir_voto`, `abrir`, `cerrar`, `escrutar`, `publicar`: cambian el resultado de una elección. Solo los ejecuta el comité desde la aplicación, nunca un modelo.
- El padrón, los correos y los códigos de estudiante: datos personales (Ley 29733).
- La urna y el registro de participación: juntos permitirían romper el secreto del voto.

## 2. Descripciones escritas ANTES de programar

| Herramienta | Descripción (lo que lee el modelo) | Parámetros y valores válidos | Devuelve |
|---|---|---|---|
| `listar_elecciones` | Lista las elecciones registradas con su código, nombre y estado | Ninguno | Lista de `{eleccion_id, nombre, estado}` |
| `estado_eleccion` | Fase del ciclo de vida, si admite votos, hora de cierre (`AAAA-MM-DD HH:MM`), opciones y participación | `eleccion_id`: código como `E-2026-DELEGADOS` (se aceptan minúsculas y espacios) | `{eleccion_id, nombre, estado, admite_votos, cierre, opciones, participacion}` |
| `resultados_parciales` | Participación y, **solo si está ESCRUTADA o PUBLICADA**, el conteo por opción y los votos válidos sin blancos ni nulos; antes, `conteo` y `votos_validos` vienen en `null` | `eleccion_id`: igual que arriba | `{eleccion_id, estado, participacion, conteo, votos_validos, nota}` |
| ★ `registrar_observacion` | Crea un archivo **nuevo** `OBS-NN.md` con una observación del comité; no modifica ni borra nada | `eleccion_id`; `titulo`: 5 a 80 caracteres; `descripcion`: 20 a 2000 caracteres, **sin datos personales** (8 dígitos seguidos ni correos) | `"Creado OBS-NN.md para <eleccion_id>"` |

Errores de entrada: un `eleccion_id` desconocido devuelve un resultado con `isError: true` y la **lista de códigos válidos**, para que el modelo se corrija solo.

## 3. ¿Por qué la escritura no puede causar daño irreversible?

1. **Solo crea:** abre el archivo en modo `"x"` (falla si ya existe), calcula el siguiente número libre y nunca recibe una ruta del modelo. No puede sobrescribir, editar ni borrar.
2. **No toca el dominio:** una observación no cambia votos, estados ni resultados. Es un registro aparte, como un acta de incidencias.
3. **Valida el contenido:** longitudes acotadas y rechazo de datos personales (DNI de 8 dígitos o correos), para que una observación no rompa el secreto del voto (ADR-002).
4. **Está anotada:** `readOnlyHint=false`, `destructiveHint=false`, `idempotentHint=false`, `openWorldHint=false`. El host y el agente del Lab 10 piden **aprobación humana** antes de ejecutarla.
5. **Es reversible por procedimiento:** si una observación es incorrecta, se responde con otra; el archivo puede revisarse en el Pull Request antes de llegar a `main`.
