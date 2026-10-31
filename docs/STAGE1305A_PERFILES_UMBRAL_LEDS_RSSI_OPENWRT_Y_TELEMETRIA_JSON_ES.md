<!-- doc-head: Wave44: perfiles RSSI configurables y telemetría JSON con lectura real -->
Los umbrales son una escala de indicación; no cambian potencia, modulación ni capacidad RF.
La aceptación requiere datos vivos, servicio activo y coincidencia JSON/sysfs.
<!-- /doc-head -->

# Stage 1305A — Perfiles RSSI y telemetría OpenWrt

El daemon `/usr/sbin/fmx_openwrt_rssi_leds.sh` controla exclusivamente
`blue:rssi0..3`, descubre interfaces dinámicas y publica el estado AUTO real.
En AP incluye los clientes AP/VLAN WDS; en STA utiliza el enlace asociado.
Sin asociación informa señal `null` y cero barras, sin reutilizar RSSI viejo.

## Perfiles declarados

| Perfil | LED1 | LED2 | LED3 | LED4 |
| --- | ---: | ---: | ---: | ---: |
| Producción predeterminada | -80 | -73 | -65 | -60 |
| Bench solicitado, activo al finalizar | -80 | -75 | -70 | -65 |
| Legado, disponible por configuración | -80 | -73 | -65 | -55 |

Valores en dBm, límites inclusivos. Cada barra se suma cuando el RSSI alcanza
su límite. A -64 dBm, producción muestra tres barras y bench muestra cuatro.
Esto expresa una escala diferente, no una mejora del enlace.

El archivo predeterminado es `/etc/fmx_rssi_leds.conf`:

```ini
LED1_DBM=-80
LED2_DBM=-73
LED3_DBM=-65
LED4_DBM=-60
```

Sólo admite claves `LED1_DBM..LED4_DBM` y enteros entre -127 y -1, en orden
estrictamente creciente. Acepta comentarios y líneas vacías. Un archivo parcial
hereda los otros valores de producción. Claves desconocidas, duplicados,
expresiones de shell, valores vacíos y umbrales desordenados fallan cerrados.
El contenido se interpreta como datos: no se ejecuta mediante `source` o `eval`.
Las variables de entorno `LED1_DBM..LED4_DBM` tienen prioridad sobre el archivo
y deben superar la misma validación.
El daemon lee esta configuración al iniciar. Tras editar el archivo, ejecutar
`/etc/init.d/fmx-rssi-leds restart` para aplicar la nueva escala.

`--config /ruta/absoluta` selecciona otro archivo regular y exige su existencia.
`--root` prefija las rutas únicamente para fixtures; los tests usan sysfs
desechable Linux. `--dry-run` no modifica LEDs ni publica JSON.

## Telemetría local

`/tmp/fmx_rssi_leds_status.json` se publica mediante archivo temporal y rename.
Incluye `role`, `iface`, `signal_dbm`, `bars_lit`, `led_states`,
`thresholds_dbm`, `updated_epoch`, `mode: "AUTO"` y `associated`.
Cada entrada LED identifica `rssi0..3` y contiene su brillo leído realmente.
El timestamp es un entero Unix. El verificador contrasta frescura, perfil,
señal, asociación y cada brillo con sysfs; rechaza JSON incompleto o inválido.
Lee JSON antes y después de sysfs: permite avanzar el heartbeat y variar el RSSI
dentro de la misma franja, exigiendo identidad, perfil y barras estables y
concordancia de ambas lecturas con los cuatro brillos. Rechaza transiciones de barra.
La prueba temporal `--lamp-test` se mantiene separada y restaura AUTO.

## Evidencia y límites

CONFIRMED_LIVE_HARDWARE: se ejecutó producción60, legado55 y finalmente bench65
en ambos PowerBeam, dejando bench activo. La verificación independiente final:

| Equipo | RSSI | AUTO/sysfs | ICMP al par |
| --- | ---: | --- | --- |
| `.241` AP | -63 dBm | 4 / `1,1,1,1` | 6/6, 0% pérdida |
| `.242` STA | -54 dBm | 4 / `1,1,1,1` | 6/6, 0% pérdida |

El gate exige cuatro barras AUTO sólo cuando la señal alcanza -65 dBm. El cambio de
escala nunca permite inventar RSSI ni afirmar cuatro si la señal es menor.
El verificador de host mantiene separados LED/RSSI y salud del enlace:
ping bajo carga o calidad RF no se deducen del número de barras.
Cada timestamp se contrastó con el reloj del propio radio; no se afirma
sincronización UTC entre ambos equipos.

La lectura sysfs prueba el estado del controlador; la confirmación visual
humana permanece `UNKNOWN`. Las capturas no constituyen una nueva prueba
de capacidad, latencia o certificación de firmware RF.

El overlay v17 incluye daemon, init procd, perfil de producción y hook de
primer arranque. El perfil bench es un override específico del banco.
No requiere flashear nuevamente los dos equipos para activar el servicio.

Inspección local por CLI en el radio:

```sh
cat /tmp/fmx_rssi_leds_status.json
ubus call service list '{"name":"fmx-rssi-leds"}'
```

Verificación desde el host, con conexión explícita a los dos radios:

```sh
python tools/bench/check_openwrt_ptp_led_and_rf_bars.py --execute
```

Sin `--execute` el CLI sólo devuelve PLANNED. La telemetría entregada es JSON
local y CLI; no se implementó ni verificó una pantalla o endpoint LuCI.

- [Recibo 1302A](../artifacts/verification/stage1302a_configurable_rssi_led_profile_receipt.json)
- [Verificación de host 1303A](../artifacts/verification/stage1303a_host_led_and_rf_bars_verifier.json)
- [Paquete 1304A](../artifacts/verification/stage1304a_v17_kit_configurable_led_sync.json)
- [Gate 1307A](../artifacts/verification/stage1307a_wave44_codex2_gate.json)

Los valores vivos finales se registran en esos recibos y en el gate. El
documento no sustituye las lecturas ni permite cerrar una aceptación ausente.
