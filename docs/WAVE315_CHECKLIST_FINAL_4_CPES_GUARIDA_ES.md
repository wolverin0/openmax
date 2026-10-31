<!-- doc-head: Waves 315 a 328, checklist de cutover de los 4 CPE airOS 8 stock reales de Guarida (imagen, sha256, board.sysid, señal, memoria, watchdog) y cutover en vivo de .200.80 a OpenWrt 24.10.4 (Wave 328) -->
.200.80 (NanoStation 5AC Loco, 0xe7fa) migró a OpenWrt 24.10.4 el 28/10 a las 23:00 UTC, con la imagen y el writer de Wave
325: guarda de watchdog 75792 ms, SSH a los 252,88 s, asociado a .84 en el canal 48. Los 18 nodos monitoreados corren ya
OpenWrt 24.10.4. Quedan 3 CPE stock, los tres fuera de servicio: .200.91 (sector Panel1), .200.68 y .120.30 (sector Panel3).
Datos: artifacts/autoresearch/wave315_*.json, wave323_*.json y artifacts/canary_panel1_guarida/cpe_200_80/ (recibos).
<!-- /doc-head -->

# Waves 315 a 328: checklist de los 4 CPE stock de Guarida y cutover de .200.80

Historia: Wave 315 (solo disco) → 319 (lectura en vivo, 0 escrituras) → 323 (plan de staging) → 325 (build offline) →
cutover con orden del operador → 328 (este registro). Base: la matriz corregida de Wave 310.

## 1. Estado

| CPE | sector | estado | qué falta |
|---|---|---|---|
| .200.80 | Panel1 .84 | **MIGRADO a OpenWrt 24.10.4** (28/10, 22:55 a 23:00 UTC) | nada para el cutover; seguir la telemetría |
| .200.91 | Panel1 .84 | stock, fuera de línea desde Wave 319 | visita a campo; después board.info, imagen y writer |
| .200.68 | Panel3 .83 | stock, enlace caído, identidad ambigua | visita a campo |
| .120.30 | Panel3 .83 | stock, enlace caído, identidad ambigua, distancia incoherente | visita a campo |

**Flota monitoreada: 18 de 18 nodos en OpenWrt 24.10.4.** Es la última muestra OBSERVED de cada nodo del registro en
`telemetry.db` (lectura `mode=ro`), tomada entre las 23:02:13 y las 23:04:09 UTC. Incluye AP de Panel1, Panel2 y
Panel3, PtP-Colo AP/STA y 13 CPE. En el ciclo de las 23:03:37, 6 nodos dieron `TimeoutError` del colector (los 5 AP/PtP y
.200.41), y .210.21 dio `AuthenticationException` a las 23:02:32. En ambos casos la muestra válida siguiente o anterior
es 24.10.4. La nota del registro todavía describe a .200.80 como stock: quedó desactualizada.

## 2. Checklist por CPE

| verificación | .200.80 | .200.91 | .200.68 | .120.30 |
|---|---|---|---|---|
| modelo | NanoStation 5AC Loco | LiteBeam 5AC Gen2 | LiteBeam 5AC Gen2 | LiteBeam 5AC Gen2 |
| firmware | **OpenWrt 24.10.4** (antes WA.v8.7.25) | WA.v8.7.22 | WA.v8.7.22 | WA.v8.7.19 |
| imagen / writer propios | 52740fd6…eb742 / 1896b275…e4e8a | falta | falta | falta |
| board / sysid | `ubnt,nanostation-ac-loco` / 0xe7fa leído en vivo | 0xe7f9 por modelo | 0xe7f9 por modelo | 0xe7f9 por modelo |
| board_sha256 | d093e094…92bdf (exigido por el writer) | sin leer | sin leer | sin leer |
| señal dBm | -59 (CPE, en el cutover) / -55 (telemetría) | sin estación en .84 | -75 (radiografía) | -75 (radiografía) |
| distancia m / ethernet | 272 / 100 full | 327 / 100 full | 800 / 0 Mbps | 9 / 0 Mbps |
| memoria | preflight: 16268 KiB bloqueados; después MemFree 16276 kB | - | - | - |

Notas:

- **sysid:** el 0xe7f9 del Gen2 se leyó en vivo en otras unidades (1903A, 6 de los 7 CPE de Panel2 y .210.9). En .200.91 y
  en el par de Panel3 no se leyó.
- **.200.91:** figura en `IGNORE_MACS` del admitter de Panel1. Wave 319 lo encontró sin asociar y sin responder: 0/4
  pings y el puerto 22 cerrado.
- **.200.68 y .120.30:** UISP (114A) y la radiografía dan MAC distintas para la misma dirección, y 114A los marca
  `connected=false`. Además, -75 dBm a 9 m es incoherente.
- **Contenedor sin firmar:** airOS WA.v8.7.25 lo rechaza con rc 99, así que la ruta es el writer. En 8.7.19 y 8.7.22 no
  se probó por separado.

## 3. Barreras del writer (fail-closed)

| barrera | valor |
|---|---|
| identidad de placa | sha256 de `/proc/ubnthal/board.info` igual al BOARD_SHA del writer y layout MTD válido |
| memoria | el CLI de producción solo corre en lowram: MemFree ≥ 8878 KiB con la imagen en `/tmp` (runner), ≥ 8352 antes y ≥ 8192 después de `mlockall` (writer) |
| guarda de watchdog | init quieto y `/bin/watchdog -t 1 /dev/watchdog` estable durante 75 s antes del primer borrado |
| vuelta atrás | ante una falla de escritura o de verificación: `journal_restore` y `verify_all`; antes del traspaso alcanza con borrar `/tmp` o reiniciar |
| traspaso | `inittab.original` guardado; hook `::shutdown:` de 119 B (sha256 1c1e6bd7…) |
| sin salida remota | si OpenWrt no responde en 420 s, hay que ir a campo (no hay en disco un procedimiento TFTP para el Loco) |

Watchdogs de configuración (contexto, no son del flasheo): psk2 en Panel3 (AP 80 s, CPE 150 s); arnés 114A (no DFS
45 s, DFS 120 s); puente de canal en Panel1 (180 s); reversión de 2534A (240 s).

## 4. Plantillas para los 3 restantes (no se pueden reutilizar tal cual)

| para | plantilla | sha256 |
|---|---|---|
| Gen2 del sector Panel1 | imagen del CPE .200.223 (23/10) | 098ee698…a192e |
| Gen2 del sector Panel3 | `panel3_cpe_10_10_210_9_openwrt_20261028.bin` | 504eef7f…dcdb2c0 |

Cada imagen va personalizada (hostname, dirección, WDS/SSID) y su writer queda atado al `board_sha256` de la unidad.
Builders: `tools/panel1/build_loco_cpe_image_20261023.py` (`build_one()`, nunca `main()`, que pisa las imágenes de
.200.41 y .200.223) y `tools/panel3/build_panel3_and_3cpe_openwrt_images_20261028.py`. Para cada CPE hay que leer
board.info en vivo antes de construir.

## 5. Wave 319: lectura en vivo de solo lectura (22:37 a 22:38 UTC)

- **AP .84:** canal 48, 20 MHz, 17 dBm, 3 estaciones WDS (.200.41, .200.223 y .200.80), admitter activo y MemAvailable
  7540 kB.
- **.200.80:**
  - sysid 0xe7fa, `board_sha256` d093e094…, WA.v8.7.25, MemFree 22332 kB y -56 dBm.
  - airOS no trae `sha256sum`: el hash se calculó sobre los bytes leídos con `cat`.
- **.200.91:** fuera de línea.
- Las direcciones reales son 10.10.200.x, no 192.168.200.x como decía el brief.

## 6. Wave 323: linaje de la imagen y plan

- **La imagen Loco estaba probada solo en .200.41.** .200.223 es un LiteBeam Gen2.
- **Receta:** kernel del sysupgrade `ubnt_nanostation-ac-loco` (r28959, Linux 6.6.110), más rootfs y cola de la v3 de
  Panel1.
- **Los bytes exactos flasheados en .200.41 no están en disco:** se regeneraron 25 min después de su cutover.
- **Plan de 8 pasos** (`staging_plan` en el JSON de Wave 323): imagen, writer, pines stock, staging en `/tmp`,
  memory_preflight, hook, traspaso y verificación.

## 7. Wave 325: build offline (WSL con fakeroot, sin SSH, sin red)

- **Carpeta aislada:** `artifacts/canary_panel1_guarida/cpe_200_80/`.
- **Resultado:** 22 de 22 chequeos. Los 11 artefactos de .200.41, .200.223 y el banco quedaron sin cambios.
- **Imagen:** 7077888 B, sha256 `52740fd69ab02bd3d53f5fbe1a756cd253c764d23458ac61641948957ebeb742`, SquashFS 4308992 B.
- **Writer:** sha256 `1896b2750db77c2f332950a904a3e106daae1e496beb700be270599df80e4e8a`. Fija `BOARD_SHA`, `IMAGE_SHA`,
  la guarda de 75000 ms y el CLI solo lowram.
- **Reproducibilidad:** las sustituciones regeneran byte a byte el fuente del writer de .200.41, y el toolchain recompila
  su binario idéntico.

## 8. Wave 328: cutover en vivo de .200.80 (con orden del operador)

Recibo `PASS_…_OPENWRT_STA_WDS_ROUTER_LIVE_VERIFIED` en `artifacts/canary_panel1_guarida/cpe_200_80/` (el nombre del
archivo lleva el apellido del abonado). Telemetría After: `telemetry.db` seq 2404.

| fase (UTC, 28/10) | resultado |
|---|---|
| 22:55:00 a 22:55:23 | staging de la imagen en `/tmp`; preflight stock OK; MemFree 16940 KiB con la imagen cargada (la proyección era 15420) |
| 22:55:26 | `memory_preflight`: `MEMORY_PREFLIGHT_ONLY`, 16472 KiB antes y 16268 bloqueados, `device_write false` |
| 22:55:27 | hook en inittab verificado, HUP a PID 1, reinicio |
| 22:55:35 | writer: `board_sha256` d093e094… y candidato 52740fd6… aceptados; 16188 / 15980 KiB |
| 22:56:51 | `INIT_QUIESCED_WATCHDOG_GUARD_PASSED`: **75792 ms**, 84 s después del traspaso (.200.41: 75969 ms y 84 s) |
| 22:59:40 | SSH de OpenWrt a los **252,88 s** (.200.41: 266 s) |
| 22:59:42 a 22:59:44 | identidad y mac80211 verificados; sha256 de mtd0, mtd1 y mtd7 registrados |
| 23:00:06 a 23:00:14 | LuCI y concesión DHCP configurados; cutover completo |
| 23:03:46 (seq 2404) | OpenWrt 24.10.4, `ubnt,nanostation-ac-loco`, canal 48 (5240 MHz), -55 dBm; MemFree 16276 kB, MemAvailable 8624 kB |

- **Enlace en el cutover (lado CPE):** -59 dBm, rx MCS6 117 Mbit/s y tx MCS4 78 Mbit/s. El gateway respondió 4 de 4
  (0 % de pérdida).
- **Ping a un equipo de la LAN del abonado:** 0 de 3. Puede ser el firewall del cliente; conviene confirmarlo si el
  abonado reporta algo.
- **Red:** la imagen copia la de .200.41 (router con NAT y LAN propia). La LAN del abonado cambió respecto de airOS
  stock.
- **Siguiente paso:**
  - Seguir la telemetría de .200.80 y comparar antes y después en la misma ventana.
  - Para los 3 restantes, visita a campo antes de cualquier build.
