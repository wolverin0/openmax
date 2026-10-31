<!-- doc-head: SUPERSEDED (W435, 31/10): the 72 C guard and cooling .110 first were removed by the operator on 30/10 (temperature is telemetry only); .110 has had 0 links since 27/10, see STAGE3038A, STAGE3043A and STAGE3064A. Stage 3030A (W370) ES: estado del banco LTU, solo lectura. El LTU-Lite .110 muestra slave y syncing porque su radio esta parada desde el 27/10, cuando el guarda termico del AP en RAM (Stage 1352A) corto a 73 C y ejecuto ame_drv.sh stop; no es un par apagado ni un canal equivocado. Incluye los recibos del PtP entre los dos LTU-Lite (funciono el 26/10) y del PtMP con el Rocket (nunca asocio), y el cambio minimo propuesto para volver a la topologia documentada, sin aplicar -->
Que cubre: lectura en vivo de .110 (rol, frecuencia, ancho, estado de enlace, pares, senal y firmware), los recibos de las pruebas PtP y PtMP anteriores, por que quedo en syncing y que hay que hacer para volver al banco documentado.
Estado: solo lectura. 3 sesiones SSH con la clave de host fijada antes de autenticar y el mismo acceso a credenciales que W347. 0 escrituras, 0 accesos a /dev/ame, sin reboot.
Datos maquina: artifacts/autoresearch/wave370_ltu_bench_state.json.
Leer cuando: antes de volver a levantar el AP de .110, de reiniciarlo o de planear el PtMP con el LTU-Rocket.
<!-- /doc-head -->
# Stage 3030A: estado del banco LTU (W370)

## 1. Lectura en vivo de .110 (30/10, CONFIRMED_LIVE_READONLY)

| Campo | Valor |
| :-- | :-- |
| Firmware y placa | afltu.v2.4.0, LTU-Lite (0xae08); mismo arranque que W347, 2,6 dias encendido |
| Rol | `afOpmode=slave`; `system.cfg` y `running.cfg` iguales, con `radio.1.mode=managed` y `ptpmode=0` |
| Frecuencia y ancho | 5500 MHz tx/rx, 20 MHz; lista de escaneo 5500 5520 |
| Enlace | `afLinkState=syncing`, `wlanUptime=0`, senal 0, capacidad 0/0; **ath0 DOWN** |
| Pares vistos | ninguno por RF |
| Config de RAM del driver (`/tmp/ame.cfg`) | role ap, ptmp, 5500, txpwr -30: es lo que dejo el ultimo arranque del AP |

**Detalles de la lectura:**
- El binario parcheado en RAM sigue montado sobre `/bin/air_fpga`.
- El reloj del equipo no esta sincronizado (marca agosto de 2025), asi que sus horas solo sirven como relativas.
- **mca-status esta congelado:** `uptime=21950` no avanza entre lecturas. 21950 s despues del arranque es justo la hora del corte termico, asi que todo mca-status quedo fijo al parar la radio (INFERRED por coincidencia de hora).
- **La tabla ARP no prueba enlace:** muestra la LAN del LTU-Lite 2 (.111) STALE en br1 y la IP de su ath0 como PERMANENT, pero esa entrada la pone el propio `rc.poststart`.

## 2. Por que esta en syncing (CONFIRMED_LIVE_READONLY, logs de /tmp en el equipo)

El 27/10, en el mismo arranque, hubo **tres arranques del AP en RAM y los tres terminaron con la radio parada por su guarda**. El rollback del guarda es `ame_drv.sh stop`, que para la radio y no la vuelve a levantar.

| Corrida | Reloj del equipo | Que paso |
| :-- | :-- | :-- |
| wave47-1320 | 06:32 | RADIO_STOPPED_BY_SAFETY_GUARD |
| ensure-39e3939c2563 (powerout 0) | commit 07:03, corte 07:07 | RADIO_STOPPED_BY_SAFETY_GUARD, sin linea de motivo |
| ensure-9e9b2fde0b79 (powerout -4, Stage 1352A) | commit 07:20, corte 07:25:12 | **THERMAL_TRIP_OVER_72**: temp0/temp1/rtemp0 72 C, rtemp1 73 C |

**Diagnostico:**
- El ultimo corte fue unos 5 min despues del commit de 1352A, cerca de las 17:00 ART del 27/10 (INFERRED a partir de la hora del recibo).
- Desde entonces nada volvio a levantar la radio. Con el driver parado, mca-status muestra el **rol nativo del LTU-Lite** (slave, porque system.cfg dice managed), syncing y senal 0.
- **Causa:** la radio de .110 esta parada por el guarda termico. No es que el par este apagado ni que haya quedado un rol o canal equivocado despues de una prueba.
- **Recibo viejo:** `artifacts/verification/stage1352a_ltu110_ram_ap_helper_receipt.json` dice AP_RUNNING_RAM_VERIFIED (68-69 C), pero se escribio antes del corte.
- **Los pares, UNKNOWN:** solo se llega a ellos por RF a traves de .110. El 27/10, 1254A vio al LTU-Lite 2 sin alimentacion (gi7 DOWN) y al Rocket sin alimentacion (0 beacons en 5 canales), y 1321A los encontro sin respuesta.

## 3. Pruebas anteriores y sus configuraciones

**PtP entre los dos LTU-Lite (CONFIRMED, 25-26/10):** se hizo en modo PtMP con una sola CPE. Recibos 47B, 48B y 51C (`artifacts/autoresearch/stage47b_*`, `stage48b_*`, `stage51c_*`).
- **.110:** AP-PTMP(Run) en 5500 MHz, 20 MHz, SSID FMX-LTU sin cifrado, txpower 15 (EIRP 28), autolink 1, una estacion.
- **LTU-Lite 2:** CPE-PTMP(Run) con PoE propio. Su config esta guardada en flash y el arranque en frio esta verificado. Senal -33/-36 dBm.

**PtMP con el LTU-Rocket (NO ASOCIO, 25/10):** recibos Stage 15 (`stage15_ltu_ptmp_sector_20261025.json`) y 17B.
- **Config:** el Rocket como AP-PTMP en 5825 MHz, 20 MHz, trama 2000 us, duty 750 y WPA, con powerout 0 por guarda termica; los dos LTU-Lite como CPE en Scan.
- **Resultado:** TOTAL LINKS 0 y Stations count 0. En 17B el Rocket aparecia como ap-ptmp en 5725 MHz. Su config actual es UNKNOWN.

**Doc del banco desactualizado:** la fila 8 de `docs/BANCO_DE_PRUEBAS_Y_EQUIPOS_A_AGREGAR.md` sigue diciendo que .110 esta ONLINE como AP-PTMP.

## 4. Cambio minimo para volver a la topologia documentada (propuesto, no aplicado)

**Objetivo:** la topologia que funciono el 26/10, .110 AP-PTMP en 5500 MHz, 20 MHz, FMX-LTU, con el LTU-Lite 2 como CPE.

1. **Operador: bajar la temperatura de .110** (sombra, ventilacion o reubicacion). Arranco a 68-69 C y a -4 dBm llego a 73 C en 5 min, asi que relanzar sin cambiar esto vuelve a cortar.
2. **Operador: confirmar que el LTU-Lite 2 tiene PoE.** Su config de CPE esta en flash y asocia sola.
3. **Una corrida de `tools/bench/ensure_ltu110_ram_ap_ptmp.py`** en una ola autorizada a escribir: es solo RAM y mantiene el guarda de 72 C. No hay lock viejo en /tmp.
4. **Verificacion de solo lectura:** afOpmode master, afLinkState operational, una estacion y temperatura por debajo de 72 C durante al menos 15 min.

**No hacer:**
- **No reiniciar .110 como arreglo.** El `rc.poststart` del arranque (Stage 40A, md5 f3c4c318) levanta el AP con `af set powerout 28` y **sin guarda termica**.
- **No subir el limite de 72 C.**

**El PtMP con el Rocket** no es una topologia que haya funcionado. Necesita un plan aparte: PoE del Rocket, rol y canal elegidos, y primero leer su config actual.

## 5. Contrato y limites

- **Contrato Karpathy: TARGET_NOT_MET.** Sin enlace RF no hay contadores que calibrar, e `irq_cpu_balance` exige escribir la afinidad. `ame_device_writes` en 0 si se cumple.
- **Sesiones:** use 3 sesiones cortas en lugar de la regla de una sola sesion de W347, porque el estado necesitaba leer los logs del guarda. Todas tuvieron la clave de host verificada antes de autenticar.
