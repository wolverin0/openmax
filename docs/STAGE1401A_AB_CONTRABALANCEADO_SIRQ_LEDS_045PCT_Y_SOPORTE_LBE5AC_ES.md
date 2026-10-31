<!-- doc-head: Wave60: cuatro slots ON/OFF reales, alcance descriptivo y soporte LiteBeam local -->
Cuatro capturas conservadas; comparacion estricta observada favorable, sin certificacion poblacional.
La recuperacion del parser no agrego ventanas RF; falta el control inmediato posterior a B2.
Los paquetes activos incorporan soporte LiteBeam; los radios medidos mantienen fuente694.
<!-- /doc-head -->

# Stage 1401A - LEDs ON/OFF y Sirq

Se ejecuto el preregistro A1 ON -> B1 OFF -> A2 ON -> B2 OFF en AP .241 y STA .242.
En B se detuvo procd y se mantuvieron cuatro salidas GPIO encendidas como
`HELD_OUTPUT`: el JSON cacheado no representa RSSI AUTO fresco.
ON exigio daemon activo, JSON fresco y cuatro readbacks positivos.
La carga fue TCP/ICMP; UDP no formo parte de este protocolo.

| Slot | Daemon | HTTP Mbps | AP Sirq % | STA Sirq % | ICMP recibido/enviado |
| :--- | :--- | ---: | ---: | ---: | ---: |
| A1 | ON | 17.2516 | 31.6943 | 43.0848 | 10/10 |
| B1 | OFF | 16.1611 | 33.3333 | 42.0203 | 10/10 |
| A2 | ON | 15.3831 | 32.1662 | 39.7611 | 9/10 |
| B2 | OFF | 15.6705 | 32.1259 | 41.8888 | 8/10 |

Media HTTP ON 16.3174 frente a OFF 15.9158 Mbps: +2.5233%.
Sirq AP ON 31.9302 frente a OFF 32.7296%: -0.7994 puntos.
Sirq STA ON 41.4229 frente a OFF 41.9545%: -0.5316 puntos.
Se cumplen las desigualdades congeladas goodput ON >= OFF y Sirq ON <= OFF
por radio, con margen cero. Es un resultado **CONFIRMED descriptivo** de estas
cuatro ventanas. ICMP fue 37/40: no se afirma ausencia de perdidas.

## Recuperacion y limites

El parser original rechazo el 16% entero de BusyBox para 5/6 respuestas.
Se conservaron el error inicial, sus tres slots parseados y los ocho RAW de
las cuatro ventanas. La recuperacion offline normaliza perdida desde los
contadores reales y conserva `reported_loss_pct`; no volvio a ejecutar carga.

La excepcion omitio la lectura de salud inmediatamente posterior a B2.
Despues de restaurar ON se obtuvo una captura distinta de salud: 6/6 entre
ambos radios, AUTO cuatro barras y GPIO positivos. Esta captura no reemplaza
ni pretende ser el control omitido. RF, colas, boot y fuente694 no cambiaron;
ambos servicios quedaron ON y se liberaron los locks compartidos.

ABAB no invierte el orden en el segundo par. N=2 por brazo y la confusion de
periodo impiden CERTIFIED, equivalencia poblacional o prueba de cero overhead
causal. Los intervalos `/proc/stat` incluyen el observador y difieren del HTTP:
AP ~16.8 s, STA 15.67-17.56 s y HTTP 15.56-17.45 s. Son medias descriptivas de
ventana completa, no una exposicion causal identica.

HTTP es payload completado/tiempo; los deltas inalambricos se registran aparte.
El 0.45% del titulo remite al CPU en reposo Wave53, no al Sirq bajo carga aqui.
La confirmacion visual humana del LED permanece UNKNOWN; sysfs prueba estado
reportado por el driver.

## LiteBeam y comparacion COLO

El soporte nuevo maneja LiteBeam sin GPIO o con `blue:power`, sin inventar
cuatro LEDs fisicos a partir de `bars_lit` logico. Diecinueve fixtures Linux
comprueban 16 casos normales y tres rechazos adversarios. No hubo flash ni
aplicacion de esta variante a los radios del experimento.

Los overlays de distribucion v17/WA y sus manifiestos/TAR se sincronizaron
con la variante nueva; el archivo versionado694 y el recibo1358 se preservaron.
La fuente distribuida y la fuente medida son evidencias distintas.

El comparador COLO valida el baseline cacheado Stage1344 de .105.62/.54.
Ese baseline no contiene ping ni contadores del router. El modo predeterminado
es dry-run, sin nuevas consultas, y devuelve UNKNOWN postflash (exit20).
Sin transaccion de migracion, incluso un candidato valido no prueba flash ni
no inferioridad. No se solicito ejecutar un flash en esta etapa.

La suite nueva ejecuto 44/44 casos sin skips. Las suites historicas afectadas
registraron 250 PASS y siete fallos Wave48, reproducidos con la fuente694
anterior. Wave37/44/53 sumaron 207/207 PASS; no se afirma suite global verde.

- [Datos y recuperacion1398](../artifacts/verification/stage1398a_counterbalanced_led_sirq_ab_receipt.json)
- [Paquete1399](../artifacts/verification/stage1399a_lbe5ac_zero_gpio_leds_overlay_verification.json)
- [Comparador1400](../artifacts/verification/stage1400a_ptp_colo_health_comparator_receipt.json)
- [Gate1403](../artifacts/verification/stage1403a_wave60_codex2_gate.json)
