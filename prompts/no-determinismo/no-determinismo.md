# No determinismo: el mismo prompt, 3 veces (Lab 09, E7)

**Prompt:** `revision-seguridad/v3.1.txt`, nuestra mejor versión.

**Casos:**
- **C1:** SQL vulnerable.
- **C5:** código limpio, para ver si aparecen falsos positivos.
- **C8:** SQL vulnerable con un comentario de inyección.

**Modelo:** <nombre y versión del asistente usado>. **Fecha:** <fecha>.

## Procedimiento
1. `python prompts/no-determinismo/renderizar.py` genera `renderizados/C1.txt`, `C5.txt` y `C8.txt`. Son los prompts exactos que enviaría el generador de producción, con la capa 1 aplicada.
2. Cada prompt se pega **3 veces**, cada vez en un **chat nuevo**, y la respuesta se guarda **sin editar** en `ejecuciones/<caso>_r<n>.txt` (9 archivos).
3. `python prompts/no-determinismo/comparar.py` imprime la tabla de abajo.

## Resultados
<pegar aquí la tabla y el detalle que imprime comparar.py>

## Análisis (5 líneas)
1. <¿El texto fue idéntico entre ejecuciones? ¿Qué partes cambiaron: resumen, redacción, orden de las claves, severidad?>
2. <¿Cambió el veredicto (seguro) o las parejas (línea, regla)? Es lo único que el código consume.>
3. <¿Alguna ejecución rompió el contrato JSON? La capa 3 la habría rechazado.>
4. <Implicancia para las grabaciones: una grabación es UNA muestra; las aserciones deben verificar estructura y hechos (regla, línea), nunca el texto exacto.>
5. <Implicancia para CI: por eso el CI usa el proveedor grabado; con un modelo real hay que usar temperatura 0, varias muestras o umbrales en lugar de 100 % exacto.>
