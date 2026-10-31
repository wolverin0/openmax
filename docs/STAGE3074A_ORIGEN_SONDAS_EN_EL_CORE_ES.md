<!-- doc-head: Stage 3074A (W414) ES: el origen de las sondas pasa al RB1100AHx4 (ping por API, fila origin=core) y la PC queda como serie origin=office; el UTP RB4011→RB1100 no pierde (0 de 900, 0 errores FCS, 1 Gbps full), la perdida nace en el propio RB1100 (rx-drop ~2 % en todos sus puertos) y desde el core los PtP pierden lo mismo que los nodos sin radio -->
Que cubre: medicion del tramo oficina, cambio del origen del sidecar, etiqueta origin en todas las filas y nuevo ranking de los PtP de W412/W413.
Estado: solo lectura en equipos (ping desde el core y lectura de contadores). Sidecar reiniciado con el codigo nuevo; filas previas etiquetadas office.
Datos maquina: artifacts/autoresearch/wave414_probe_origin.json. Codigo: tools/observability/sidecar_e2e/collector.py y schema.py.
Leer cuando: antes de usar cualquier latencia o perdida del sidecar, y antes de culpar al cable de la oficina.
<!-- /doc-head -->
# Stage 3074A: origen de las sondas en el core (W414)

## 1. El tramo de la oficina (15 min, 1/s)

| Camino | Enviados | Perdida % (IC95) | p50 ms | p95 ms | p99 ms |
| :-- | --: | --: | --: | --: | --: |
| PC → RB4011 | 900 | 0,0 (0,0-0,43) | 0,0 | 0,0 | 0,0 |
| PC → RB1100 | 900 | 4,67 (3,47-6,25) | 0,0 | 11,0 | 229,0 |
| RB1100 → RB4011 (API, cada 2 s) | 355 | 5,07 (3,23-7,87) | 0,59 | 0,92 | 0,98 |
| RB1100 → RB4011 (/ping 600, 10 min) | 600 | 5,67 (4,08-7,81) | 0,81 | 16,36 | 718,98 |

- **CONFIRMED:** el RB4011 contesta siempre a la PC (0 perdidas). Las perdidas aparecen al llegar al RB1100 y tambien en los pings que salen del RB1100: no estan en el cable.
- **CONFIRMED:** puerto ether1-WAN1-750 del RB1100 (donde llega el UTP): enlace 1Gbps full-duplex, autonegociacion completa, 0 caidas, 0 errores FCS/alineacion/fragmentos en 15 min. Unico contador que crece: rx-drop, 2,15 % de lo recibido; los otros puertos con trafico descartan lo mismo (2,15, 2,55, 1,97, 2,31, 2,12 %).
- **INFERRED:** la perdida del tramo es descarte en recepcion del RB1100 (CPU, W413), no el UTP. Atribucion: external controller (core).
- Las 95 llamadas API fallidas del primer control fueron por compartir una sesion entre hilos; no cuentan como perdida. El control de 10 min uso una sesion por destino: 0 errores.

## 2. Cambio del origen (sidecar)

- Cada fila de latencia lleva `origin`: `office` (PC, como siempre) o `core` (el RB1100 hace `/ping count=1 interval=1` por API: mismo 1 s de espera). No se toca configuracion.
- Ritmo desde el core (decision de diseno, no umbral medido): registro y tramo cada 10 s, resto del mapa cada 60 s, 4 sesiones API.
- Series del tramo: `seg_rb4011` (PC y core) y `seg_rb1100` (PC). Desde el reinicio: PC→RB4011 0,0 %, PC→RB1100 4,29 %, core→RB4011 1,59 %.
- Migracion atomica: las 8284 filas office (desde 2026-10-30T14:27) quedaron con origin=office; copia previa en `%LOCALAPPDATA%/FuturaMAX/sidecar_e2e/telemetry_pre_w414.db`. Tabla delta separada por origen. Metricas y alerta de nodo caido llevan la etiqueta origin.
- En vivo: core 72 nodos, office 73. Tests: 25 passed in 1.06s.

## 3. PtP de W412/W413 re-rankeados con origen core (10 min, 600 ecos por punta)

| # | Punta | Perdida core % (IC95) | p50 | p95 | p99 ms | Perdida office % | W412 office % |
| :-- | :-- | --: | --: | --: | --: | --: | --: |
| 1 | ptp_e0e0b1b6_sta | 6,17 (4,51-8,38) | 0,94 | 11,73 | 527,57 | 5,0 | - |
| 2 | ptp_e8eabc59_ap | 5,83 (4,22-8,0) | 7,17 | 28,99 | 652,06 | 6,0 | 10,7 |
| 3 | ptp_c44af853_ap | 5,67 (4,08-7,81) | 1,05 | 17,89 | 160,16 | 6,33 | 6,9 |
| 4 | ptp_9f29f65d_ap | 5,5 (3,94-7,62) | 0,93 | 21,16 | 668,92 | 6,17 | 3,4 |
| 5 | ptp_357e700d_sta | 5,33 (3,8-7,43) | 8,46 | 42,39 | 300,2 | 6,5 | - |
| 6 | ptp_8871fc9c_sta | 4,67 (3,25-6,66) | 3,12 | 26,31 | 730,07 | 6,17 | - |

- Referencia (4 nodos del sitio del core sin radio, desde el core): 5,46 % (4,62-6,44), p99 596,75 ms.
- **CONFIRMED:** con origen core los 6 extremos pierden 4,7-6,2 %, igual que la referencia: los IC95 se solapan. El orden de la tabla no es significativo. Ningun PtP tiene perdida propia medible.
- **REFUTED:** que mover el origen a la oficina explicara la perdida. Desde el core se ve lo mismo, porque nace en el core.

## 4. Siguiente

- Dueño del RB1100 (infra/operador): el descarte en recepcion de ~2 % y las rafagas de cpu0 (W413). FuturaMAX no toca el core.
- Las cifras de antes y despues de un cambio en un PtP deben compararse contra la referencia del mismo origen y ventana, no en absoluto.
- Karpathy: daemon vivo True, nodos observados desde el core 72, tabla delta poblada True: PASS.
