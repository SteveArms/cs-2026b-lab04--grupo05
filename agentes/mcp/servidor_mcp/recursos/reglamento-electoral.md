# Reglamento electoral de VotoEPIS (resumen para agentes)

> Texto de referencia del proyecto (ficticio, con fines académicos). Resume las reglas que ya implementa el código y los ADR-002 y ADR-003.

1. **Un voto por estudiante y elección.** El sistema rechaza un segundo voto del mismo código o correo, aunque cambie mayúsculas o espacios (ISSUE-01).
2. **Voto secreto (ADR-002).** La papeleta nunca guarda la identidad del votante. Ningún reporte, log u observación puede vincular a una persona (DNI, código, correo) con su voto.
3. **Ventana de votación.** Solo se vota con la elección en estado ABIERTA. La mesa no puede cerrarse antes de la hora de fin configurada (ISSUE-03).
4. **Resultados.** Mientras la elección está ABIERTA o CERRADA solo se informa la **participación**. El conteo por lista se publica recién después del escrutinio (ESCRUTADA o PUBLICADA).
5. **Votos válidos.** Los votos en blanco y nulos se reportan por separado y no se suman a ninguna lista (ISSUE-02).
6. **Escrutinio.** El número de papeletas debe ser igual al de participaciones; si difieren, el escrutinio se detiene.
7. **Publicación.** Solo se publica con el acta firmada por el comité electoral.
8. **Observaciones.** Cualquier miembro del comité o personero puede registrar una observación sobre una elección. Las observaciones no se editan ni se borran: se responden con una nueva.
