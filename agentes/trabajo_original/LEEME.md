# Copia de trabajo para el agente (E5)

Instantánea de VotoEPIS **con el defecto del ISSUE-02** (estado del commit `a27bb49`,
antes de la corrección manual `98624f3` hecha en `main` para que la integración continua pasara).

El orquestador y el agente único NUNCA trabajan sobre `src/` del repositorio: copian esta carpeta
a `agentes/trabajo/` (ignorada por git), la versionan con un commit local para que
`ver_cambios()` muestre el diff, y el agente edita solo esa copia. El humano decide después
si lleva el cambio a `main` mediante un Pull Request.
