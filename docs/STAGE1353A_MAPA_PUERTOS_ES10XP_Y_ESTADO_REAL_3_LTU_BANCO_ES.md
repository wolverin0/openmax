<!-- doc-head: SUPERSEDED (W435, 31/10): 72 C / 68 C / 180 s were agent-invented limits, removed by the operator on 30/10; temperature is telemetry only (orchestration/thresholds.json). Wave52: mapa REST ES-10XP, helper RAM verificado y parada térmica real al superar72 grados -->
Ocho puertos y VLAN observados; PVID y Rocket desconocidos. El AP pasó90s y después se detuvo por rtemp1=73°C.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1353A — Mapa del banco y estado real LTU

## Mapa fresco del ES-10XP

Destino: `PUBLIC_DEVICE_0052%29`; captura1351A del27/10/2026 a19:28:23UTC.
Un pase, una conexión TLS reutilizada: interfaces, VLAN, estadísticas y `/tools/mac-table` devolvieron HTTP200.
El login fue exclusivamente autenticación. No se modificaron switch, PoE, VLAN o radios durante este mapa.

| Puerto | Enlace observado | VLAN sin etiqueta | VLAN con etiqueta | MAC LTU exacta visible |
|---|---|---|---|---|
| gi1 | UP /1000-full | 1 | Ninguna | Ninguna |
| gi2 | UP /100-full | 1 | 99 | Ninguna |
| gi3 | UP /1000-full | 1 | 99,107 | Ninguna |
| gi4 | UP /1000-full | 1 | 107 | Ninguna |
| gi5 | UP /100-full | 1 | Ninguna | `PUBLIC_DEVICE_0045` |
| gi6 | UP /1000-full | 1 | Ninguna | Ninguna |
| gi7 | UP /1000-full | 107 | Ninguna | `PUBLIC_DEVICE_0043`, fila FDB en VLAN1 |
| gi8 | UP /1000-full | 1 | Ninguna | Ninguna |

El **PVID de los ocho puertos permanece UNKNOWN**: no estaba expuesto de forma inequívoca.
Una membresía sin etiqueta no se convirtió automáticamente en PVID.
VLAN107 se llama `mkt_boca7_lab`. La fila MAC de Lite #2 en VLAN1 no coincide con esa membresía sin etiqueta de gi7.
Puede haber diferencias de clasificación de ingreso, caché u otra causa; ninguna quedó demostrada.
No se borraron FDB/ARP ni se cambió VLAN para resolver esa discrepancia.

Los endpoints opcionales `/mac-table`, `/arp`, `/lldp`, `/status` y `/routing/arp` devolvieron404 y se conservaron.
La tabla MAC válida procede de `/api/v1.0/tools/mac-table`.
Los contadores son acumulados del puerto; no se interpretan como un benchmark ni como tráfico OTA.

## Estado de los tres equipos

| Equipo | Evidencia | Estado aceptado |
|---|---|---|
| LTU-Lite #1 `.110` | MAC5399 en gi5; activación AP y ejecución verificadas por1352A | **Actualmente detenido por guard térmico**; antes AP5500/20/FMX-LTU, potencia−4/ganancia26 |
| LTU-Lite #2 | MAC exacta58cc aprendida en gi7/VLAN1; link-local `PUBLIC_DEVICE_0063` | Presencia FDB; identidad de modelo, acceso y asociación OTA actuales no confirmados |
| LTU-Rocket | No aparecen `PUBLIC_DEVICE_0061` ni `PUBLIC_DEVICE_0050` | Puerto y estado físico UNKNOWN; ausencia de FDB no significa apagado |

Ningún prefijo `78:8a:20:*` o `e0:63:da:*` se promovió por sí solo a identidad Rocket.
También hay filas distintas de la MAC local `PUBLIC_DEVICE_0062` en gi7, con direcciones `198.18.0.118` y `198.18.0.50`.
Son candidatos de gestión observados; no se fusionaron con la identidad física exacta ni se contactaron en esta ola.
Wave47 midió45s con0 estaciones/0 enlaces y no confirmó OTA. Wave52 no presenta esa captura histórica como una medición nueva.

## Helper determinista de RAM

Archivo: [`ensure_ltu110_ram_ap_ptmp.py`](../tools/bench/ensure_ltu110_ram_ap_ptmp.py).

```powershell
python tools/bench/ensure_ltu110_ram_ap_ptmp.py
python tools/bench/ensure_ltu110_ram_ap_ptmp.py --live
python tools/bench/ensure_ltu110_ram_ap_ptmp.py --live --ensure
```

La primera orden muestra el plan; la segunda verifica; la tercera permite una única activación RAM si hace falta.
Con AP sano devuelve `VERIFIED_NO_CHANGE`, sin lock remoto ni escrituras de configuración.
Acepta `powerout` entre−4y0 inclusive, ganancia26 y cuatro sensores válidos ≤72°C.
Si hace falta activar, selecciona−4 y configuración nominal conducida−30; un AP sano en0 tampoco se reinicia.
Exige rol/AP, frecuencia, ancho, SSID, `ath0`, AME y SHA256 del ejecutable de los PID reales.
Un error IPC o una lectura ambigua no autoriza por sí solos reiniciar una radio sana.

El monitor normaliza decimales y CRLF;255 y errores nativos son datos inválidos, no temperaturas aceptadas.
Una temperatura válida superior a72°C detiene inmediatamente. Una lectura inválida se confirma tras1s;
dos ciclos inválidos consecutivos detienen el servicio. Cada ciclo publica un frame RAM fijo con motivo y contador.

La reparación usa lock atómico, vuelve a comprobar el estado dentro del lock y permite como máximo una activación.
El lock de otro proceso no se elimina. Un lock propio cuya limpieza falla se informa como fallo.
Cada activación tiene namespace y directorio de evidencia propios; no sobrescribe Wave47.
No hay escrituras MTD, persistencia, cambios de switch ni instalación de un servicio host por este helper.

## Ejecución real de1352A

Entre19:53:14y19:54:12UTC el helper encontró el ASIC detenido; no provocó una parada de prueba.
Realizó **una activación RAM** y devolvió `RAM_ACTIVATED_AND_VERIFIED`; lock propio liberado.
Readbacks: AP-PTMP,5500/20,FMX-LTU,powerout−4,gain26; `ath0` arriba y AME activo.
PID10009 ejecutaba SHA256 `264165b450bc72a5223942f657cf34b1b2d478a32401780fc49a26aa693fd37a`.
Máxima térmica observada69°C; mtd0/1/4/5 sin cambios. El monitor RAM de72°C quedó activo.
La primera aceptación de19:36:49UTC fue puntual: después el guard anterior detuvo el servicio.
El log conservado no identificó qué lectura lo disparó; no se atribuye sin prueba a calor ni a formato decimal.
El guard nuevo registra la lectura y el motivo. La captura anterior y sus53tests están conservados como historia.
El ensayo posterior capturó cuatro muestras en90,25s, entre19:54:54y19:56:25UTC, todas aceptadas.
Conservó el PID10009 y observó avance de ciclos del monitor10,15,20,25; máxima térmica71°C.
Esa ventana tiene su propia evidencia; no se presenta una activación ni cuatro muestras como continuidad indefinida.

## Estado final y límite físico observado

A19:59:47UTC la confirmación posterior encontró `ath0` y AME sin servicio.
El log del monitor registra `THERMAL_TRIP_OVER_72`, ciclo47: temp0=72,temp1=72,rtemp0=72 y **rtemp1=73°C**, todos rc0.
Después ejecutó `RADIO_STOPPED_BY_SAFETY_GUARD`. El watchdog de arranque ya estaba desarmado; no fue quien paró.
73°C es la última lectura válida antes de la parada, no una temperatura actual medida con el ASIC detenido.
La consigna−4 redujo potencia RF, pero no garantizó mantener los cuatro sensores por debajo del límite72.
No se volvió a arrancar ni se elevó el umbral. La preparación operativa para mantener AP activo queda **INCOMPLETE**.
La suite y la captura pueden pasar mientras el guard informa correctamente este límite físico.

## Reconciliación y evidencia

Stage1350A verificó los seis recibos1320A..1325A y el replay de **93 pytest PASS** de Wave47.
Los recibos1323/1324 son metadatos suplementarios generados ahora; las pruebas conservan su fecha original.
No se afirmó una nueva adquisición RF ni una nueva ejecución de esos93tests.

- [1350: reconciliación](../artifacts/verification/stage1350a_wave47_reconciliation_receipt.json).
- [1351: mapa y respuestas nativas](../artifacts/verification/stage1351a_es10xp_full_port_vlan_and_ltu_mac_map.json).
- [1352: helper y activación real](../artifacts/verification/stage1352a_ltu110_ram_ap_helper_receipt.json).
- [1352: verificación posterior de90s](../artifacts/verification/wave52/1352/stability90.json).
- [Estado final y evento térmico](../artifacts/verification/wave52/final_live_confirmation.json).
- [1355: gate y pytest nuevos](../artifacts/verification/stage1355a_wave52_codex1_gate.json).

Captura completa de interfaces/VLAN no equivale a ubicación física confirmada del Rocket ni a conectividad OTA.
El PVID y la identidad/ubicación del tercer equipo siguen pendientes; `.110` queda **detenido por protección térmica**.
