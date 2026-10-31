<!-- doc-head: Wave68: sincronización v3, CPU nueva, suites unificadas y canales sólo planificados -->
La evidencia viva1446 y la ejecución conjunta1447 se verifican por separado.
Los datos cacheados de canales no prueban ruido, frecuencia ni regulación actuales.
No se ejecutan cambios RF, flash ni comandos de inspección desde el gate local.
<!-- /doc-head -->

# Stage 1449A — Daemon LED v3 y verificación unificada

La sincronización viva llevó el daemon de distribución v3 a AP .241 y
STA .242. Se comprobó la versión080942, distinta de la
fuente694 utilizada en el experimento histórico ON/OFF. El gate exige hashes
del archivo remoto y conserva el estado antes/después, sin atribuir una
actualización del repositorio a un despliegue real.

La medición nueva exige al menos120 segundos por radio, PID y startticks
estables y CPU del padre más hijos esperados, dividida por el delta total de
los primeros ocho contadores de `/proc/stat`. El límite es estrictamente
menor que0.5%; no se reciclan porcentajes de Wave53 ni del contraste Wave60.
El recibo prueba AUTO, cuatro salidas GPIO, avance de polls, ausencia de
reescrituras de brillo y conservación de RF/boot/reset/configuración.

| Radio | CPU padre+hijos / ticks totales | Intervalo | CPU % | Polls | AUTO |
| :--- | :--- | ---: | ---: | :--- | :--- |
| AP .241 | 61 / 13668 | 136.680s | 0.446298 | 3→16 | 4 barras, −63dBm |
| STA .242 | 57 / 13672 | 136.720s | 0.416910 | 2→16 | 4 barras, −52dBm |

Ambos valores son estrictamente menores que0.5%. Hubo3/3 respuestas de salud
por radio, readback remoto080942, aceptación explícita y liberación de locks.
No se generó carga RF adicional ni se modificaron parámetros de radio.

Las cinco suites históricas se ejecutaron juntas en Linux:311 casos, cero
fallos/errores/skips, con colección, identidad JUnit y hashes antes/después.
Los siete fallos Wave48 reproducidos antes con694 se repararon mediante
fixtures y compatibilidad explícita de esquema;
un cambio de expectativa debe mantener las garantías originales. No se
reescriben recibos sellados para presentarlos como ejecuciones nuevas.

## Canales COLO: plan pasivo, sin Step0

`check_ptp_colo_candidate_channels_readonly.py` evalúa los candidatos149/5745,
165/5825 y56/5280MHz a20MHz de planificación. Sólo usa los recibos1344/1374.
El inventario permite una inferencia histórica de cercanía entre emisores;
no constituye un escaneo RF ni garantiza ausencia de otros transmisores.

1344 registró6035MHz, ruido AP−97/STA−101dBm y scan_list STA6035. No son
valores actuales y ese ruido no se transfiere a los tres canales candidatos.
Ruido por candidato, regulación actual, compatibilidad de scan_list y canal
actual permanecen UNKNOWN. Ningún candidato queda habilitado para Step0.

El modo predeterminado es dry-run y devuelve exit20/PLANNED. Los comandos
pasivos exactos se incluyen como datos: identidad, claves RF/scan_list de
`/tmp/system.cfg`, ruido del canal observado mediante `mca-status`, detección
de herramientas, `iw reg get` y `iwlist ath0 channel` si están disponibles.
El inspector no ejecuta ninguno, no abre conexiones ni modifica los radios.
La ausencia de una herramienta o lectura conserva el requisito pendiente.

Antes de Step0 se requieren lecturas nuevas de ambos extremos, regulación,
capacidades y evidencia específica de ruido/espectro. Medir en otro canal
podría requerir retune o escaneo activo: ese trabajo necesita su propio plan
autorizado, compatibilidad del par y rollback; no se sustituye por el cache.

## Recibos

- [Despliegue vivo1446](../artifacts/verification/stage1446a_live_v3_led_daemon_sync_and_cpu_verification.json)
- [Cinco suites1447](../artifacts/verification/stage1447a_unified_5suite_led_regression_zero_fail.json)
- [Plan de canales1448](../artifacts/verification/stage1448a_ptp_colo_candidate_channel_precheck_receipt.json)
- [Gate1451](../artifacts/verification/stage1451a_wave68_codex2_gate.json)

El gate final verifica1446,1447 y los53 casos de la suite nueva. Conserva los
recibos previos sin promover su aceptación histórica. Sysfs demuestra estado
del driver; aceptación visual física permanece
UNKNOWN cuando no existe observación humana independiente.
