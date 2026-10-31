<!-- doc-head: Wave270, cierre acotado Panel3, comparación observacional y banco LTU -->
La meta de Panel3 se decide con contadores nativos comparables y un proceso identificado.
Los resultados descriptivos y las capacidades LTU no sustituyen esa aceptación.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Cierre vivo de Panel3 y banco LTU

## Contrato antes de medir

La [prerregistración](../artifacts/autoresearch/stage2652a_wave270_preregistration.json)
fijó hasta tres rondas y un plazo menor o igual a treinta minutos.
Cada ronda usa `A1 → B1 → A2 → B2`, con tráfico ambiental real y ventanas
de quince segundos. El candidato es RTS 512; no se modifica canal ni ancho.
La meta exige simultáneamente admitter de Panel3 vivo, reducción de al menos
50% en la tasa de `tx_failed` del CPE terminado en `.9`, y delta cero del
contador exportado `fq_overmemory` del AP Panel3, no del CPE.

La dirección relevante es CPE hacia AP: se lee el contador propio del CPE,
no se sustituye por el contador de transmisión descendente del AP.
Cada tasa usa el delta nativo y el tiempo de actividad nativo de su ventana.
Se compara la media de las tasas de A1/A2 con la media de B1/B2.
Las ventanas deben pertenecer al mismo arranque y al mismo par asociado.
La tolerancia de duración de cinco segundos se congeló antes de medir.

Si la tasa anterior es cero, el porcentaje queda indefinido (`null`): no
equivale a una mejora del 100%. Las lecturas acumuladas de toda la vida del
nodo tampoco se comparan con una sola ventana corta.

## Proceso y reversión

La identidad del admitter requiere PID, generación de proceso y hash del
script realmente ejecutado. La presencia del archivo no prueba que esté vivo.
Los cambios de RTS usan una guarda de reversión de sesenta segundos.
Solo se permite persistir RTS 512 cuando la medición cumple la meta, las
condiciones de seguridad y el readback. En otro caso se restaura el valor previo.
Los hashes de `rc.local` y los readbacks AQL conservan el alcance de cada cambio.

## Intentos conservados

La ronda 1 conservó sus cuatro ventanas. B2 duró 27,55 segundos y superó
la tolerancia congelada: quedó `INVALID_MEASUREMENT_INTERVAL`, sin porcentaje
aceptado ni persistencia de RTS. No se ensanchó la tolerancia después de medir.
La ronda 2 conservó A1; una `ConnectionResetError` impidió adquirir B1.
Quedó `INCOMPLETE_WINDOW_ACQUISITION`, con métricas de comparación `null`.
Ambas consumen el presupuesto de tres rondas; no se reinicia el contador de intentos.
Las fallas originales y la restauración del RTS previo se conservan en los recibos.
La ronda 3 también conservó A1; después se registró `SSHException: No existing
session`. No se fabricaron B1, A2 ni B2. Se agotó el presupuesto y no hubo
una cuarta ronda. No existe un porcentaje válido que justifique persistir RTS 512.

## Antes/después observacional

Los sondeos nuevos desde el mismo CPE hacia `198.18.0.132` permiten describir
el mismo destino histórico. No prueban una carga ni una ruta idénticas.
Los valores históricos de subida cargada de 132,9 y 86,3 ms no son una
referencia causal para el tráfico actual en reposo. Un porcentaje descriptivo
mantiene explícita esa incertidumbre y no se publica como mejora de subida.
El core `198.18.0.2`, el destino `198.18.0.132` y el segmento RF IPv6
siguen siendo mediciones distintas.
El ciclo nuevo envió quince sondeos por CPE: `.41` recibió trece respuestas
y `.223` recibió catorce, con pérdidas observadas de 13,33% y 6,67%.
La tabla conserva ocho filas descriptivas, cuatro estadísticas por CPE.
No son ocho comparaciones plenamente equivalentes ni una certificación de mejora causal.

## Contadores FQ

La condición de delta cero se refiere al rótulo exportado observado.
Las fuentes primarias detectaron una inversión de nombres entre ciertos
campos internos y debugfs; falta confirmar el backport exacto de los AP.
Por ello no se atribuye automáticamente ese rótulo a presión de memoria.
Los eventos no son bytes ni un denominador directo de pérdida de paquetes.
La cola global no prueba aislamiento de memoria por CPE.

## Banco LTU

La [evidencia del banco `.110`](../artifacts/autoresearch/stage2653a_live_ltu_lite_110_calibrated_and_smp_receipt.json)
confirma un LTU-Lite con dos CPU y una IRQ de red identificada: SMP sí está
disponible. La validación RAM quedó bloqueada antes de escribir un parámetro.
El último intento observó un hijo separado con PID distinto de su SID;
la comprobación del propio helper exigía erróneamente igualdad y rechazó el armado.
Se conservaron los tres intentos y sus dos reparaciones. No se hizo otro intento.
Los tres procesos propios terminaron; el readback conservó backlog 2500 y
afinidad de red `2`. Esto prueba estado sin cambios, no reversión autónoma probada.
Una sola observación pasiva de 3,83 segundos no calibra umbrales productivos.
No se accede a `/dev/ame*`, no se modifica firmware ni se reclama goodput.

## Verificación

El [gate de Wave270](../artifacts/verification/stage2657a_wave270_codex2_gate.json)
calcula la meta independientemente de los indicadores publicados.
Las pruebas desechables cubren reinicios, contadores faltantes, dirección
incorrecta, intervalos repetidos, denominador cero y persistencia insegura.
Las pruebas de integridad pueden pasar aunque la meta física sea `PARTIAL`.
