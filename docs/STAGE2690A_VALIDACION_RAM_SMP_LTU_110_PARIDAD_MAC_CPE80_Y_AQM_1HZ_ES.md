<!-- doc-head: Wave276, evidencia RAM LTU, paridad privada y AQM nominal de 1 Hz -->
El resultado compara una brecha de CPU pasiva; no mide goodput ni mejora causal RF.
Los valores originales se restauraron y las identidades privadas no se publican.
<!-- /doc-head -->

# Validación RAM SMP, paridad de identidad y AQM

## Contrato congelado

La [prerregistración](../artifacts/autoresearch/stage2688a_wave276_preregistration.json)
fijó un máximo de tres rondas en treinta minutos, con secuencia `A1 → B1 → A2 → B2`.
Cada ventana mide quince segundos y usa una guarda autónoma de sesenta segundos,
tanto en A como en B. Se prohibieron accesos a `/dev/ame*`, cambios RF, flash y recarga de driver.

La métrica es la diferencia absoluta entre los porcentajes de CPU ocupada de
CPU0 y CPU1. Se obtiene de deltas nativos de `/proc/stat`: idle más iowait
se excluyen de ocupado y guest no se cuenta dos veces. Se compara la media
de las dos brechas A con la media de las dos B: `100 × (B − A) / A`.
Una media A igual a cero deja el porcentaje indefinido, nunca implica mejora completa.
Los eventos y la afinidad de IRQ63 se verifican por separado.

## LTU `.110`: resultado real

El [recibo LTU](../artifacts/autoresearch/stage2688a_ltu_lite_110_smp_backlog_a1b1a2b2_receipt.json)
conserva dos muestras pasivas válidas separadas por 10,13 segundos nativos.
Aquí «calibradas» significa ese par de observaciones válidas; no significa
calibración de umbrales productivos ni de falsas alarmas.

La preimagen real fue backlog 2500 y afinidad IRQ63 `2`. En B se aplicaron
backlog 4096 y afinidad `1`, solo en RAM. No se usó un valor histórico como preimagen.

| Ronda | Brecha media A | Brecha media B | Cambio relativo | Eventos IRQ A/B |
|---|---:|---:|---:|---:|
| 1 | 0,465112 p.p. | 0,596026 p.p. | +28,146820% | 290 / 307 |
| 2 | 0,788651 p.p. | 0,194728 p.p. | −75,308683% | 323 / 316 |

La segunda ronda cumplió el objetivo de reducir la **brecha** al menos 15%,
con eventos IRQ en ambos brazos. Se detuvo en la primera ronda elegible:
dos de tres rondas posibles. El resultado no dice que el uso total de CPU bajó 75%.
La reducción absoluta de la brecha en la segunda ronda fue aproximadamente
0,593923 puntos porcentuales; el tráfico ambiente y la gestión SSH forman parte de la observación.

Las ocho ventanas conservaron las guardas hasta su vencimiento real de
60,06–60,07 segundos. Todas terminaron con backlog 2500 y afinidad `2`.
Los PID, ticks de creación y sesiones nativas identifican cada guarda;
un hijo BusyBox con PID distinto de SID es válido si su sesión es independiente de SSH.
La validación liga el script generado LF con el artefacto local CRLF mediante
normalización explícita y compara su readback real, sin declarar hashes de bytes distintos como iguales.

No hubo escrituras ni lecturas AME, carga de aplicación generada ni medición
de goodput. Es evidencia de seguridad RAM y asociación pasiva de CPU,
no certificación de mejora causal RF ni recomendación de despliegue productivo.

## Guarida: paridad y cadencia

El [recibo de Guarida](../artifacts/autoresearch/stage2689a_panel1_cpe80_mac_parity_and_panel3_1hz_aqm_receipt.json)
verifica igualdad exacta de la MAC inalámbrica del CPE `.80` con una de las tres
estaciones asociadas al AP `.84`. La comprobación privada se liga a etiquetas
HMAC públicas; no se publican la MAC ni la clave. El CPE mantiene airOS
`WA.v8.7.25`; esta paridad no demuestra migración ni aceptación completa del plano de datos.

Panel3 `.83` produjo treinta muestras AQM nativas. La adquisición duró
32,07 segundos; los períodos fueron de 1,04 a 1,21 segundos, con media de
1,070345 segundos. Es una captura nominal de 1 Hz dentro de la tolerancia
prerregistrada de ±0,25 segundos, no una cadencia exacta de 1,000 Hz.
El rótulo exportado `fq_overmemory` permaneció en 10364: delta cero conocido.
La interpretación exacta del backport sigue sin verificar; ese rótulo no
prueba causa de memoria, pérdida de paquetes ni aislamiento por CPE.

## Evidencia y límites

El [gate](../artifacts/verification/stage2693a_wave276_codex2_gate.json)
recalcula CPU, IRQ, temporizadores, readbacks, HMAC y cadencia desde los recibos nativos.
Las pruebas desechables verifican reinicios, denominador cero, identidad de guarda,
ventanas repetidas, manipulación de hashes y confusión entre medición pasiva y calibración productiva.
La aceptación permanece limitada a esta observación de banco y a los valores restaurados.
El [anexo de resultados](../artifacts/autoresearch/stage2692a_results_crlf_append_receipt.json)
liga cuatro filas CRLF nuevas al prefijo conservado del registro, permitiendo anexos posteriores.
El [registro de memoria](../artifacts/autoresearch/stage2691a_memorymaster_ingest_receipt.json)
es una entrada candidata aceptada, no validación independiente ni aprobación productiva.
