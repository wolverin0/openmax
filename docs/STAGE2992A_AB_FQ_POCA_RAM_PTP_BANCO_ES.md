<!-- doc-head: Stage 2992A (W349 P3) ES: A/B en banco PtP .241/.242 (OpenWrt, 56 MB) del set fq actual (4 MiB/2048) contra el set de poca RAM de STAGE2966A (1310720/577/3028, backlog 550), con watchdog compartido y renew; goodput, RTT p50/p95/p99, caidas del fq con etiquetas cruzadas, MemAvailable; resultado: misma capacidad y latencia, +2,2 MiB de memoria libre -->
Que cubre: los dos sets comparados, la carga y por que supera la capacidad, el protocolo de seguridad, los resultados por ventana y que significan.
Estado: ejecutado en banco, solo RAM, restaurado y verificado. Nada persistido. Produccion sin tocar.
Datos maquina: artifacts/autoresearch/wave349_ptp_bench_small_ram_fq_ab.json. Gate: artifacts/verification/wave349_lane3_ptp_small_ram_fq_ab_gate.json.
Horas: Argentina (UTC-3). Leer cuando: antes de llevar el set de STAGE2966A a un AP de 64 MB.
<!-- /doc-head -->
# Stage 2992A: A/B del fq de poca RAM en el banco PtP (W349 P3)

## 1. Sets comparados

| Knob | A (actual .241 / .242) | B (STAGE2966A §6) |
| :-- | --: | --: |
| fq_limit | 2048 / 2048 | 577 |
| fq_memory_limit | 4194304 / 4194304 | 1310720 |
| fq_quantum | 3028 / 1514 | 3028 |
| netdev_max_backlog | 1000 / 1000 | 550 |

- El target de CoDel no se cambio: mac80211 lo fija en 20 ms y no es un knob de debugfs. STAGE2966A no propone otro.
- BQL no se toco: no es parte de esta orden.

## 2. Carga y medicion

- **Capacidad real del enlace:** con carga, el control de tasa baja a MCS3 (52 Mbit/s PHY) y el aire entrega unos 33,5 Mbit/s. El host inyecta mas de 150 Mbit/s en eth0 del AP y la CPU del AP queda bajo 50 %. El cuello es el aire.
- **Carga:** `tools/bench/udp_blast.py`, 2 flujos de 30 Mbit/s hacia .242 (60 Mbit/s, 1,8 veces la capacidad). Llena la cola de bajada del AP.
- **RTT:** ping desde WSL cada 0,2 s a .242. Es un flujo chico que el fq aisla del flujo pesado.
- **Goodput:** delta de `rx_bytes` de la interfaz de .242 (capa 2, no aplicacion).
- **Orden:** A B A B A B, ventanas de 60 s, 10 s de pausa entre ventanas.

## 3. Seguridad

- Watchdog compartido `fmx_watchdog.sh` (el aceptado por lane 1), uno por radio, de 45 s, con renew cada 15 s desde otra sesion. Las escrituras empezaron solo despues de ARMED.
- El archivo de restauracion tenia los originales leidos en vivo y su readback.
- Cada escritura se verifico al aplicarla y otra vez al final de cada ventana; las 6 ventanas fueron validas.
- Al final: `restore` dio RESTORED y `release` dio 0 en las dos radios. El readback final coincide con los originales. Se borro solo lo propio de /tmp despues de 50 s.
- Piso de aborto: MemAvailable 6144 KiB. Nunca se acerco.

## 4. Resultados

| Ventana | Arm | Goodput Mbit/s | RTT p50 / p95 / p99 ms | Caidas totales | Caidas por memoria | Pico de cola (paquetes / bytes) | MemAvailable min .241 KiB |
| :-- | :-- | --: | :-- | --: | --: | :-- | --: |
| 1 | A | 32,83 | 4,96 / 8,46 / 10,4 | 1532 | 1532 | 2047 / 4,19 MB | 11344 |
| 2 | B | 32,81 | 5,39 / 8,76 / 10,1 | 1741 | 0 | 576 / 1,18 MB | 13484 |
| 3 | A | 32,73 | 5,40 / 9,21 / 11,7 | 1529 | 1529 | 2041 / 4,18 MB | 11252 |
| 4 | B | 32,57 | 5,43 / 9,09 / 11,5 | 1808 | 0 | 577 / 1,18 MB | 13496 |
| 5 | A | 32,81 | 5,32 / 8,82 / 10,3 | 1514 | 1514 | 2044 / 4,19 MB | 11208 |
| 6 | B | 32,70 | 5,57 / 9,89 / 11,6 | 1741 | 0 | 577 / 1,18 MB | 13492 |

- Las columnas de caidas ya corrigen las etiquetas cruzadas del debugfs: "totales" es la etiqueta `fq_overmemory`, "por memoria" es la etiqueta `fq_overlimit` (STAGE2966A §5).
- **Por brazo:** goodput A 32,79 y B 32,69 Mbit/s (−0,3 %). RTT p95 agrupado A 9,03 y B 9,38 ms (+3,9 %). Perdida de ping 0-2 % en ambos.
- **Memoria:** con B, .241 conserva unos 2,2 MiB mas en el minimo bajo carga, en los 3 pares.
- **truesize:** 2048 B por paquete en cola en las 6 ventanas, igual que STAGE2966A.

## 5. Que significa

- **A llena el fq hasta su techo de 4 MiB:** todas las caidas de A son por memoria, con la cola en unos 2045 paquetes. El limite en paquetes casi no actua.
- **B esta acotado por paquetes (577):** cero caidas por memoria, y la cola ocupa 1,18 MB en lugar de 4,19 MB.
- **La capacidad no cambia,** y la latencia de un flujo chico tampoco: el fq lo atiende aparte de la cola pesada, asi que el tamaño de esa cola no esta en su camino.
- **Conclusion:** en este hardware, el set B libera unos 3 MB de cola (2,2 MiB medidos en MemAvailable) sin costo de goodput ni de latencia del trafico interactivo. Es el resultado que buscaba STAGE2966A.
- **No se cumplio** el objetivo Karpathy de bajar el p95 un 25 %: no habia margen, porque el ping no pasa por la cola pesada.

## 6. Limites

- Una sola clase de carga (UDP), solo en bajada. No se midio TCP ni la latencia del propio flujo pesado.
- 3 pares de 60 s, n chico. Los deltas de RTT de ±10 % por par estan dentro del ruido.
- Banco, no produccion. Para .84 falta el arreglo del admitter (W344) y la misma prueba con varias CPE.
