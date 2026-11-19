# ISSUE-01: Doble voto por diferencia de mayúsculas y espacios en código de estudiante

**Severidad:** Crítica  
**Componente:** `src/votacion/servicio.py` (`ServicioVotacion.emitir_voto`)  
**Atributo de Calidad Afectado:** QA-01 (Seguridad e Integridad del Sufragio - ADR-002)  
**Reportado por:** Comité Electoral Universitario  

## Descripción del Defecto
En elecciones universitarias, los estudiantes ingresan su código de matrícula para identificarse ante la mesa o en la interfaz de sufragio. Se ha detectado una vulnerabilidad crítica donde un estudiante puede emitir dos o más votos en la misma elección si varía el uso de mayúsculas o incluye espacios accidentales o maliciosos en su código identificador.

Por ejemplo:
1. El estudiante vota primero ingresando el código `"20221234a"`. El voto se registra exitosamente.
2. Posteriormente, el mismo estudiante vuelve a votar ingresando `" 20221234A "`.
3. El sistema evalúa la clave `(votante.codigo, eleccion.id)` como no existente en el conjunto `self.participaciones`, permitiendo un segundo sufragio y violando la regla fundamental de un solo voto por estudiante.

## Comportamiento Esperado
El sistema debe normalizar cualquier identificador de estudiante (eliminando espacios en blanco en los extremos con `strip()` y convirtiendo a minúsculas con `lower()`) antes de registrarlo o verificar su existencia en `self.participaciones`. Ante cualquier variación de formato del mismo código, el segundo intento debe lanzar un `ValueError("Ya emitiste tu voto")`.

## Criterios de Aceptación
1. La prueba unitaria `tests/test_issue_01.py` debe pasar exitosamente.
2. Si un estudiante emite un voto con `"20221234a"`, cualquier intento posterior con `" 20221234A "`, `"20221234A"`, o `"  20221234a  "` debe ser rechazado inmediatamente.
3. No se deben romper las pruebas existentes de votación regular sin código explícito.
