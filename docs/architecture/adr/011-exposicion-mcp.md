# ADR-011. Exposición de VotoEPIS mediante MCP

- **Estado** Propuesto
- **Fecha** 28 de noviembre de 2026
- **Decisiones relacionadas** [ADR-002](002-voto-secreto-e-integridad.md) y [ADR-010](010-sistema-agentico.md)

## Contexto

El agente del Lab 10, MCP Inspector y Codex CLI requieren acceso al dominio electoral. El ADR-002 exige conservar el secreto del voto. Los hosts también requieren una forma de distinguir consultas de escrituras y dejar evidencia de cada aprobación.

## Decisión

Exponer un servidor local por stdio. El agente de E4 usó MCP `2026-07-28` con `server/discover`. El servidor reutiliza `ServicioVotacion` y expone tres herramientas de consulta, una de creación de observaciones, recursos de consulta y dos prompts. Se excluyen el padrón, los datos personales, el vínculo entre urna y participación y las operaciones que cambian el ciclo electoral.

Validar códigos de elección, longitud y datos personales en observaciones. Restringir la selección de ADR a tres dígitos y crear archivos en modo exclusivo bajo el directorio del servidor. El host pide aprobación antes de la escritura y mantiene trazas para revisión.

## Alternativas

| Alternativa | Consecuencia |
| --- | --- |
| API REST directa | Cada host tendría que adaptar sus consultas y construir su propia integración de herramientas, recursos y prompts. |
| Function calling en el analista | Los esquemas quedarían ligados al agente de E4 y habría que duplicarlos para otros hosts. |

## Consecuencias

Los hosts comparten las capacidades y las restricciones del mismo servidor. Un despliegue remoto requeriría autenticar y autorizar al cliente y definir almacenamiento compartido para observaciones. La [auditoría de E7](../../../agentes/mcp/seguridad.md) documenta los límites actuales del catálogo y los controles probados.
