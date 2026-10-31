<!-- doc-head: Wave 37 RSSI LEDs: activaci?n real, umbrales y l?mites de aceptaci?n -->
Daemon procd desplegado en los dos PowerBeam 5AC Gen2; lectura independiente de sysfs.
El indicador autom?tico sigue el RSSI medido: AP tres barras y STA cuatro en la captura final.
La prueba temporal de cuatro salidas no equivale a cuatro barras autom?ticas ni a confirmaci?n visual.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 1263A ? Indicadores RSSI en OpenWrt PtP

Fecha de captura: 2026-10-27. Equipos: `198.18.0.45` AP y
`198.18.0.46` STA, PowerBeam 5AC Gen2, OpenWrt 24.10.4, kernel 6.6.110.

## Causa observada en estos equipos

CONFIRMED: los cuatro nodos existen como `blue:rssi0`, `blue:rssi1`,
`blue:rssi2`, `blue:rssi3`; `max_brightness=1`. Antes del despliegue estaban
apagados (`brightness=0`, disparador `[none]`). El binario y servicio
OpenWrt `rssileds` s? existen. No faltan f?sicamente los nodos LED.

CONFIRMED: `/etc/board.json` y `system.rssid_wlan0.dev` todav?a apuntan a
`wlan0`, mientras `iw dev` enumera interfaces din?micas `phy2-*`.
El AP expone el cliente asociado en `phy2-ap0.sta1` (AP/VLAN WDS), y el
`station dump` del padre `phy2-ap0` est? vac?o. La STA utiliza `phy2-sta0`.
Esta evidencia explica el desajuste del monitor configurado en estas im?genes;
no demuestra un defecto universal de todas las instalaciones OpenWrt 24.10.4.
Atribuci?n: Linux/sysfs y configuraci?n del monitor externo; RSSI de mac80211/ath10k.

## Comportamiento instalado

`/usr/sbin/fmx_openwrt_rssi_leds.sh` descubre las interfaces actuales con `iw dev`.
En STA usa `iw dev <interfaz> link`; en AP y AP/VLAN inspecciona los clientes
asociados y utiliza el RSSI m?s d?bil cuando hay varios. No utiliza `signal avg`
ni los valores individuales de las cadenas como RSSI principal.

| RSSI asociado | Barras acumuladas |
| --- | ---: |
| menor que -80 dBm | 0 |
| desde -80 dBm | 1 |
| desde -73 dBm | 2 |
| desde -65 dBm | 3 |
| desde -55 dBm | 4 |

Los l?mites son inclusivos. Sin asociaci?n o sin clientes, muestra cero barras.
Cada escritura modifica solamente los cuatro nodos RSSI y verifica su lectura
real. `--dry-run` inspecciona sin escribir; `--once` actualiza una vez.
El servicio `/etc/init.d/fmx-rssi-leds` usa procd, reaparici?n autom?tica y
recarga por cambios de configuraci?n inal?mbrica. Se habilit? para el arranque.
Si la configuraci?n antigua apunta al `wlan0` ausente, detiene el monitor antiguo
para evitar dos escritores; conserva intacto `/etc/config/system`.

## Evidencia real y aceptaci?n

| Equipo | RSSI inicial | RSSI captura final | AUTO final | Prueba temporal |
| --- | ---: | ---: | ---: | --- |
| AP .241 | -62 dBm | -64 dBm | 3: `1,1,1,0` | cuatro salidas `1,1,1,1` |
| STA .242 | -55 dBm | -55 dBm | 4: `1,1,1,1` | cuatro salidas `1,1,1,1` |

CONFIRMED_LIVE_HARDWARE: lecturas sysfs, proceso procd en ejecuci?n, habilitaci?n
de inicio y hashes SHA256 remotos coincidentes con las fuentes locales.
La prueba `--lamp-test` enciende las cuatro salidas durante dos segundos y restaura
AUTO; una captura posterior verifica AUTO con el servicio nuevamente activo.
Las capturas antes/despu?s conservan configuraci?n de radio, colas, canal,
identidad de arranque y contadores de reinicio del firmware.

La estimaci?n inicial de aproximadamente -49 dBm no coincide con las capturas.
**El requisito literal de cuatro barras autom?ticas en ambos equipos permanece
parcial**: a -64 dBm corresponde mostrar tres en el AP. No se alteraron umbrales,
potencia ni radio para fabricar cuatro barras. La confirmaci?n visual f?sica es
`UNKNOWN`: sysfs acredita el estado solicitado al controlador, no una inspecci?n
humana de los diodos.

## Integraci?n v17 y recibos

El hook compa?ero v17 incorpora daemon, init y `99-fmx-rssi-leds` en el overlay
SquashFS. El primer arranque ejecuta `enable` y `start`; el kit de colas v17
conserva sus bytes. El manifiesto SHA256SUMS verifica los tres miembros.
Esta integraci?n de paquete es est?tica; no se realiz? un nuevo flasheo.

- [Probe 1260A](../artifacts/verification/stage1260a_openwrt_pbe5ac_led_sysfs_probe.json)
- [Despliegue 1261A](../artifacts/verification/stage1261a_live_pbe5ac_rssi_leds_receipt.json)
- [Overlay 1262A](../artifacts/verification/stage1262a_v17_kit_rssi_led_integration.json)
- [Gate 1265A](../artifacts/verification/stage1265a_wave37_codex2_gate.json)

Los tests 1264A ejecutan el daemon real sobre sysfs desechable Linux y un `iw`
controlado: l?mites, WDS, STA, desconexi?n, lectura conservadora, ambig?edad,
nodos incompletos, `--dry-run`, restauraci?n y preservaci?n de POWER/LAN.
El gate s?lo lee recibos locales; nunca abre una conexi?n a los radios.
