# E7. Bitácora de interacciones con Codex

| Interacción | Verificación o corrección |
| --- | --- |
| Descubrimiento del servidor | El usuario comprobó que `votoepis` apareció en `/mcp` tras instalar el SDK y añadir la configuración. |
| Listado de elecciones | `listar_elecciones` devolvió tres elecciones. Se verificaron sus estados contra el escenario esperado. |
| Estado de Tercio | `estado_eleccion` confirmó que la elección admitía votos y registraba 40 participantes. |
| Resultado de Delegados | `resultados_parciales` devolvió 46 y 38 votos. Se calculó el margen de ocho. |
| Código auxiliar para el acta | Codex indicó ejecutar `obtener_prompt_mcp.py`. Ante el bloqueo por stdio se corrigió el procedimiento y se invocó directamente `redactar_acta`. La tabla consigna el cambio de vía. |
| Escritura de la observación | El usuario confirmó que Codex pidió aprobación. Se verificó que `OBS-01.md` registra 10 votos en blanco y 6 nulos sobre 100. |
| Alcance de la reducción del catálogo | Se midió el tamaño con el adaptador real y se verificó la trayectoria grabada. La elección de herramientas en una nueva corrida quedó pendiente. |
