<!-- doc-head: SUPERSEDED (W435, 31/10): the bounded-log admitter was deployed and verified on the three Guarida APs on 29/10 (Panel1 0300d1, Panel2 193cd9, Panel3 47ad80; logs 52 KB or less). Stage 2945A (W344 P1) ES: arreglo offline de la causa raiz de la deriva de memoria en los AP de Panel1/2/3: panel1_admitter.sh escribia sin limite en tmpfs (events.jsonl, state.log, actions.log); tope de 16 KiB por log con una generacion .1, events.jsonl solo con DEBUG=1, builders de Panel2/Panel3 con guarda, pruebas con 100k eventos y plan de despliegue para los 3 AP -->
Que cubre: la causa raiz que midio lane 2, el cambio en el script (y por que ese tope), lo que no cambia, como lo toman las imagenes de Panel2 y Panel3, las pruebas y el plan de despliegue.
Estado: arreglo de codigo y pruebas offline. Cero SSH. El despliegue en los 3 AP esta escrito, NO ejecutado, y necesita orden del operador.
Datos maquina: artifacts/verification/wave344_lane3_admitter_log_bound_gate.json. Medicion de origen: artifacts/autoresearch/wave343_ap_tmp_and_rss_growth.json (lane 2).
Horas: Argentina (UTC-3). Leer cuando: antes de desplegar el admitter, o antes de agregar cualquier log a un script que corre en /tmp de un AP.
<!-- /doc-head -->
# Stage 2945A: admitter con logs acotados (W344 P1)

## 1. Causa raiz (medida por lane 2, W343)

`tools/panel1/panel1_admitter.sh` corre en `/tmp/fmx-panelN-admitter`, que es tmpfs: RAM sin swap. Las imagenes de Panel2 y Panel3 lo copian desde los builders. Escribia sin limite en tres archivos:

| Archivo | Que escribia | Crecimiento medido en 20 min (Panel1 / Panel2 / Panel3) |
| :-- | :-- | :-- |
| `events.jsonl` | cada evento de ubus; el script nunca lo lee | 204 / 12 / 12 KiB |
| `state.log` | una linea por vuelta del bucle (1 Hz) | 76 / 76 / 68 KiB |
| `actions.log` | cada accion del IE | 8 / 4 / 0 KiB |

En Panel1 eso da unos 288 KiB cada 20 min. Panel2 ya tenia 4,8 MB en `state.log`. Es la deriva de MemAvailable en reposo del presupuesto STAGE2896A, y lo que deja a un AP de 64 MB sin margen para las colas.

## 2. El cambio

1. **`events.jsonl` solo con `FMX_ADMITTER_DEBUG=1`.** Sin DEBUG no se crea, y al arrancar se borra el que haya quedado. Con DEBUG tambien tiene tope.
2. **Tope de `LOG_CAP` = 16384 B por archivo, con una sola generacion `.1`** que se sobrescribe. Para medir el tamaño no hace falta un fork: se suma `${#linea} + 1` en una variable del shell y, al pasar el tope, `mv -f archivo archivo.1`. Solo usa comandos de BusyBox.
3. **Al arrancar**, de cada log anterior se guardan solo los ultimos `LOG_CAP` bytes (`tail -c`) en `.1`. Asi un reinicio del admitter tambien libera un log enorme, como los 4,8 MB de Panel2.

**Por que 16 KiB por archivo y 64 KiB en total:**
- La regla de higiene de STAGE2896A fija un tope de 512 KiB para todo lo FuturaMAX en /tmp de un equipo de 64 MB. Dos logs × (actual + `.1`) × 16 KiB = 64 KiB, un octavo de ese tope, y deja lugar a los otros dueños.
- Historia que queda a las tasas medidas:
  - `actions.log`, el que tiene las acciones del IE: unas 1,3 h en Panel1 (8 KiB / 20 min) y unas 2,7 h en Panel2;
  - `state.log`: unos 7-8 min a 1 Hz, suficiente para diagnosticar en vivo.
- Las paginas de tmpfs son de 4 KiB, y 16384 es multiplo exacto: no se desperdicia una pagina parcial por archivo.

**Por que no mandarlo a `logger`:** el ring buffer de logd es unico y chico (64 KiB por defecto en OpenWrt). Una linea por segundo de `state.log` lo daria vuelta en minutos y borraria el resto del syslog del equipo.

**Lo que no cambia:**
- La logica del IE queda igual: ventana de 35 s, pausa de 65 s, rafaga de 4 s, sueño de 600 ms, re-pulso a 180 s, `set_ie`, `collect` y `heal_stale_wds_and_reapply_qos`.
- El texto de cada linea de log es el mismo.
- `listener.stderr` sigue igual: se trunca al arrancar y solo recibe errores de ubus.

## 3. Builders de Panel2 y Panel3

`make_panel2_admitter_sh()` y `make_panel3_admitter_sh()` leen `tools/panel1/panel1_admitter.sh` y le cambian BSSID, IE, MACs y OUIs con `.replace()`, asi que toman el arreglo solos.

Le agregue a cada uno una guarda: si el resultado no contiene `bounded_append` o el BSSID de su panel, falla en lugar de armar una imagen. Antes, un `.replace()` que no encontraba su ancla dejaba pasar en silencio el BSSID de Panel1.

## 4. Pruebas (`tests/test_panel_admitter_log_bound.py`)

- **No quedan escrituras sin tope:** solo `bounded_append` y el stderr de ubus. Defaults `LOG_CAP` 16384 y `DEBUG` 0.
- **Las lineas de la logica del IE siguen identicas.**
- **Los dos builders generan scripts con el tope** y con su BSSID, no el de Panel1.
- **`bounded_append` con 100 000 lineas** y el tope real: el archivo y su `.1` quedan en 16 KiB o menos cada uno.
- **El admitter real con un flujo falso de 100 000 eventos de ubus** (unos 11 MB, que era lo que habria crecido `events.jsonl`):
  - no se crea `events.jsonl`;
  - el directorio queda bajo 4 × tope;
  - el IE se abre y se cierra (ubus recibe `set_vendor_elements` con el IE y vacio);
  - `actions.log` muestra `IE_WINDOW_OPEN`, `UNASSOC_UBNT_PROBE_WHILE_IE_ON` e `IE_WINDOW_CLOSED`.
- **Los tests existentes de `tests/test_panel1_universal_admitter.py` siguen pasando.**
- **Limite:** las pruebas corren en WSL con `bash --posix`, porque WSL no tiene BusyBox. El equipo usa BusyBox ash.

## 5. Plan de despliegue para los 3 AP (no ejecutado)

Panel1 `/usr/sbin/panel1_admitter.sh` en .84; Panel2 `/usr/sbin/panel2_admitter.sh` y Panel3 `/usr/sbin/panel3_admitter.sh`, generados por sus builders. Va un AP por vez, en una sola sesion SSH por AP.

1. **Antes de escribir:** MemAvailable ≥ 6144 KiB; si no, se aborta.
   - Anotar el pid del admitter, el sha del script instalado y `du -k` del directorio del admitter.
   - Copiar el script instalado a `/overlay/fmx_rollback/panelN_admitter.sh.pre_w344`. Es una escritura chica en flash, para que sobreviva a un reinicio.
2. **Escribir el script nuevo** en `/usr/sbin/panelN_admitter.sh.w344new`, comparar su sha con el local, darle `chmod 0755` y moverlo sobre el instalado con `mv`.
3. **Reiniciar solo el admitter:**
   - `kill -TERM <pid>`: su trap cierra el IE (`set_ie ''`) y escribe `ENDED`;
   - volver a lanzarlo con la misma linea de rc.local, es decir `/usr/sbin/panelN_admitter.sh /tmp/fmx-panelN-admitter >/tmp/fmx-panelN-admitter.boot.log 2>&1 &`;
   - sin reload de Wi-Fi y sin tocar hostapd.
4. **Verificar en los primeros 2 min:**
   - aparece el marcador `ready`;
   - `actions.log` muestra `LISTENER_STARTED` y despues `IE_WINDOW_OPEN` o `IE_WINDOW_CLOSED`, segun estado;
   - las estaciones de las CPE activas siguen asociadas;
   - `events.jsonl` no existe.
5. **Verificar el tope durante 30 min:** `du -k` del directorio a los 0, 10 y 30 min, y debe quedar en 64 KiB o menos. MemAvailable no debe bajar por el admitter (la tendencia la sigue lane 2).
6. **Rollback:** `mv` de la copia de `/overlay` sobre el script y el mismo reinicio del paso 3.

**Riesgo:** mientras el admitter esta caido (unos segundos), una CPE que hace scan puede no ver el IE. Las CPE ya asociadas no se ven afectadas: el trap deja el IE cerrado, que es el estado normal con todas asociadas.

## 6. Limites

- No se probo en BusyBox real ni en un AP. Es la primera tarea del despliegue o del banco.
- Las tasas de crecimiento son de una sola ventana de 20 min por AP (lane 2).
- Labels con los dos ultimos octetos; sin MACs de abonados en este documento.
