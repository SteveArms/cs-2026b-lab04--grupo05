# E5. Consultas de prueba en Codex CLI

| N.º | Consulta | Herramienta o prompt observado | ¿Pidió permiso? | ¿Resultado correcto? | Resultado esperado |
| --- | --- | --- | --- | --- | --- |
| 1 | ¿Qué elecciones conoce VotoEPIS y en qué estado está cada una? | `listar_elecciones` | No | Sí. Delegados EPIS 2026 `PUBLICADA`, Tercio estudiantil 2026 `ABIERTA` y Comité de ética 2027 `CONFIGURADA`. | Delegados EPIS 2026 está `PUBLICADA`, Tercio estudiantil 2026 está `ABIERTA` y Ética 2027 está `CONFIGURADA`. |
| 2 | ¿Cuál es el estado de Tercio estudiantil 2026 y cuántas personas votaron? | `estado_eleccion` | No | Sí. Está `ABIERTA`, admite votos y ya votaron 40 personas. | Está `ABIERTA`, admite votos y registra 40 participantes. |
| 3 | ¿Quién ganó Delegados EPIS 2026 y por cuántos votos? | `resultados_parciales` | No | Sí. Lista A obtuvo 46 votos y Lista B obtuvo 38. El margen fue de 8 votos. | Ganó la Lista A con 46 votos frente a 38 de la Lista B, una diferencia de 8 votos. |
| 4 | Redacta el acta de Delegados EPIS 2026 usando el prompt `redactar_acta` del servidor. | `redactar_acta` mediante llamada directa a la función del servidor. El cliente auxiliar quedó esperando respuesta por stdio. | No | Sí en el contenido del acta. Se consignaron 100 participantes, 84 votos válidos y la victoria de Lista A por 8 votos. | El acta indica 100 participantes, 84 votos válidos y la victoria de la Lista A. |
| 5 | Registra una observación para Delegados EPIS 2026 por sus 10 votos en blanco y 6 nulos, que suman 16 de 100. | `registrar_observacion` | Sí | Sí. Se creó `observaciones-host/OBS-01.md` con 10 votos en blanco y 6 nulos, 16 de 100 votos emitidos (16 %). | Codex solicita aprobación y, tras recibirla, se crea un archivo `OBS-NN.md` con las cifras agregadas. |
