# ISSUE-03: Cierre prematuro de mesa antes de la hora oficial de fin de jornada

**Severidad:** Crítica  
**Componente:** `src/votacion/servicio.py` (`ServicioVotacion.cerrar_mesa`)  
**Atributo de Calidad Afectado:** QA-04 (Disponibilidad y Cumplimiento del Calendario Electoral)  
**Reportado por:** Personeros de Listas Estudiantiles  

## Descripción del Defecto
El método de cierre operativo de mesa `cerrar_mesa(eleccion, ahora)` invocado por los miembros del comité electoral permite cerrar la elección antes de la hora estipulada en `eleccion.fin`.

Al revisar la implementación, se observa que la función valida erróneamente que la jornada haya iniciado (`momento < eleccion.inicio`), pero al momento de ejecutar la transición de estado, pasa fraudulentamente `eleccion.fin` al método interno `self.cerrar(eleccion, eleccion.fin)` en lugar de pasar el timestamp actual `momento`. Esto engaña la guarda del patrón State (`Abierta.cerrar`), permitiendo que mesas se cierren hasta horas antes del término legal, privando del derecho de sufragio a electores rezagados.

## Comportamiento Esperado
El método `cerrar_mesa(eleccion, ahora)` debe validar rigurosamente que el momento del cierre sea igual o posterior a `eleccion.fin` (`momento >= eleccion.fin`). Si se intenta cerrar la mesa antes del fin de la jornada, debe lanzar `ValueError("Aún no culmina la ventana de votación")`.

## Criterios de Aceptación
1. La prueba `tests/test_issue_03.py` debe fallar si se permite cerrar la mesa antes de `eleccion.fin`.
2. Una llamada a `cerrar_mesa(eleccion, ahora = FIN - 30 min)` debe lanzar `ValueError("Aún no culmina la ventana de votación")` y mantener la elección en estado `ABIERTA`.
3. Una llamada con `ahora >= FIN` debe cerrar la mesa normalmente pasando a estado `CERRADA`.
