# ISSUE-02: Conteo erróneo de votos en blanco y nulos asignados al primer candidato

**Severidad:** Alta  
**Componente:** `src/votacion/servicio.py` (`ServicioVotacion.computar_votos_validos`)  
**Atributo de Calidad Afectado:** QA-01 / QA-02 (Integridad del Escrutinio y Auditabilidad)  
**Reportado por:** Auditores Externos de la Elección  

## Descripción del Defecto
Durante el escrutinio de actas, la función de cómputo de votos válidos `computar_votos_validos()` presenta una falla de lógica aritmética: los votos clasificados como `"Voto en Blanco"` y `"Voto Nulo"` se están sumando erróneamente al primer candidato/lista de la elección en lugar de computarse únicamente los votos válidos directos.

Esto altera ilegítimamente la votación del candidato favorecido y descuadra el conteo respecto a las papeletas individuales depositadas en la urna electrónica.

## Comportamiento Esperado
- La función `computar_votos_validos(eleccion)` debe devolver un diccionario que contenga estrictamente los votos obtenidos por cada candidato o lista legítima.
- Los votos en blanco o nulos no deben sumarse a ningún candidato bajo ninguna circunstancia.
- El total de votos válidos debe coincidir exactamente con la suma de votos emitidos por candidatos habilitados.

## Criterios de Aceptación
1. La prueba `tests/test_issue_02.py` debe validar que con 10 votos para Lista A, 8 votos para Lista B, 5 votos en Blanco y 2 Nulos, el cómputo de votos válidos sea exactamente `{"Lista A": 10, "Lista B": 8}`.
2. Ningún voto en blanco o nulo debe ser transferido a Lista A ni a Lista B.
