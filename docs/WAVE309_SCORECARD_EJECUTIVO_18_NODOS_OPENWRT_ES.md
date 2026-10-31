<!-- doc-head: Wave 309 v6 (Wave 329) ES: scorecard ejecutivo de los 18 nodos OpenWrt 24.10.4 tras 10 ciclos solo-lectura mas; cpe_200_80 con 12 muestras Despues, profundidad de MemFree/MemAvailable, canal IW, RTT mediana de ventana + ultima -->
Wave 329 corrio 10 ciclos solo-lectura del colector (seq 2415-2594, 180 filas, 0 escrituras en radio y flash) y regenero el reporte oficial (seq 2610). cpe_200_80 llega a 12 muestras Despues: mediana 15/23.9 ms contra 9/13.5 ms airOS (239).
MemFree/MemAvailable con 12 o mas lecturas en 16 de 18 nodos. No llegan cpe_200_169 (10) ni cpe_210_21 (7): su SSH falla intermitente y 8 reintentos dirigidos dieron ERROR, asi que se cortaron.
Memoria Despues (mediana): MemFree 6.8-15.4 MiB. MemAvailable baja en cpe_200_223 (2.3 MiB), cpe_210_235 (2.5) y cpe_210_9 (2.8), ahora con 12-14 lecturas: es estable, no un dato aislado.
Las medianas de memoria coinciden con el reporte oficial en 18/18. El p50 difiere en 1-2 ms en 4 nodos porque el scorecard incluye las muestras OBSERVED_AP_ASSOCIATION.
<!-- /doc-head -->
# Wave 309 v6 - Scorecard ejecutivo de 18 nodos (profundidad de memoria y cpe_200_80)

Version 6, actualizada en Wave 329.
- **Datos:** `tools/observability/telemetry.db`, todas las filas hasta seq 2610, con `mode=ro` y sha256 recalculado.
- **Reporte oficial:** regenerado con `python tools/observability/generate_full_before_after_report_20261028.py`
  (`artifacts/observability/full_before_after_report_20261028.json/.md`, seq 2610, 18/18 OpenWrt).
- **Datos maquina:** `artifacts/observability/wave309_18node_executive_scorecard_20261028.json` (schema 6.0.0).

## Ciclos de Wave 329 (solo lectura)

- **Colector:** `tools/observability/fmx_persistent_before_after_openwrt_daemon.py --once`, sha256 57413a24... (actualizado
  por otra lane desde la W320).
  - Antes de correrlo se verifico que sus comandos remotos solo leen: `cat` de /proc (incluido /proc/meminfo) y /sys,
    `iw dev`/`station dump`, `ip ... show`, `brctl showmacs` y pings.
  - No habia otro colector corriendo.
- **10 ciclos principales** cada ~10 s (23:10-23:22 UTC): 180 filas (168 OBSERVED + 12 OBSERVED_AP_ASSOCIATION),
  0 escrituras en radio y flash. rc por ciclo 2,2,0,0,0,2,0,0,2,2: el colector cuenta errores de SSH, pero todas las
  filas se guardaron.
- **Reintentos dirigidos:** 8, con `--hosts` limitado a cpe_200_169 y cpe_210_21 (seq 2595-2610). Dieron 16 filas ERROR
  (AuthenticationException / SSHException) y 0 observaciones. Se detuvieron para no insistir contra esos equipos.

## Tabla consolidada 18/18 (OpenWrt 24.10.4, todos de 20 MHz)

- RTT E2E en ms, como p50/p95 de la mediana de ventana; n = muestras con E2E.
- Memoria en KiB: mediana de las muestras que traen el campo (n entre parentesis).
- MCS Despues como rx/tx mediano.

| Nodo | Canal IW | RTT Antes mediana (n) | RTT Desp. mediana (n) | Desp. ultima | Senal | MCS | MemFree / MemAvail (n) |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| panel1_ap .84 | ch48 5240 | backfill s/RTT | 8/11 (273) | 16/18.7 | -50 | 5/7 | 7288 / 7064 (13) |
| cpe_200_41 | ch48 5240 | backfill s/RTT | 9/14.1 (272) | 26/61.1 | -45 | 7/4 | 10876 / 4636 (13) |
| cpe_200_223 | ch48 5240 | backfill s/RTT | 9/13.9 (270) | 19/23.5 | -42 | 7/5 | 10764 / **2380** (14) |
| cpe_200_80 | ch48 5240 | 9/13.5 (239, airOS) | 15/23.9 (11) | 24/30.3 | -56 | 6/4 | 14036 / 6384 (12) |
| panel2_ap .82 | ch161 5805 | 8/11.2 (21) | 14/17.8 (23) | 15/18.6 | -48 | 3.5/7 | 14712 / 12828 (13) |
| cpe_200_213 | ch161 5805 | n/d | 22/38 (25) | 32/46.4 | -54 | 6/1 | 11308 / 5808 (13) |
| cpe_210_166 | ch161 5805 | n/d | 16/22.8 (25) | 5/5 | -46 | 8/4 | 12276 / 6796 (13) |
| cpe_200_169 | ch161 5805 | n/d | 33/48.8 (25) | **206.5/241.1** | -55 | **0/0** | 15784 / 8288 (**10**) |
| cpe_210_239 | ch161 5805 | n/d | 19.5/32 (24) | 63/75.6 | -31 | 8/5 | 11648 / 5936 (14) |
| cpe_200_183 | ch161 5805 | n/d | 19/28.4 (25) | 67/76.9 | -51 | 7/0 | 10692 / 5280 (14) |
| cpe_210_21 | ch161 5805 | n/d | 24/32.4 (24) | 67/81.4 | -63 | **0/0** | 11648 / 5212 (**7**) |
| cpe_210_83 | ch161 5805 | n/d | 21.5/28.6 (24) | 58/65.2 | -49 | 7/0 | 12008 / 6612 (14) |
| panel3_ap .83 | ch149 5745 | backfill s/RTT | 9/11.6 (278) | 15/18.6 | -44 | 5/7 | 8656 / 13352 (13) |
| cpe_210_9 | ch149 5745 | backfill s/RTT | 23.2/30.1 (196) | 32/41 | -53 | **0/0** | 11210 / **2912** (12) |
| cpe_210_235 | ch149 5745 | backfill s/RTT | 15/22.7 (273) | 28/34.3 | -38 | 8/7 | 10828 / **2608** (14) |
| cpe_210_238 | ch149 5745 | backfill s/RTT | 14/24.8 (240) | 35/38.6 | -44 | 7/5 | 11160 / 4568 (14) |
| ptp_colo_ap .62 | ch153 5765 | 0/0 (9) | 0/0.9 (24) | 0/0 | -36 | 7.5/8 | 6964 / 10168 (13) |
| ptp_colo_sta .54 | ch153 5765 | 3/5.9 (9) | 3/3.9 (24) | 6/8.7 | -34 | 8/7 | 7672 / 10548 (13) |

Paridad 18/18 VERIFIED. `n/d` = el dato no existe en la fuente. Las CPE de Panel2 tienen Antes airOS sin RTT.

## Lectura ejecutiva

1. **cpe_200_80 (n=12 Despues):** 15/23.9 ms en OpenWrt contra 9/13.5 ms en airOS (239 muestras). Sube unos 6 ms de
   p50 y 10 de p95, sin causa atribuida. Senal -56 dBm, MCS 6/4, MemAvailable 6.2 MiB.
2. **Memoria con profundidad:**
   - MemFree 6.8-15.4 MiB en todos los nodos.
   - MemAvailable baja y estable (12-14 lecturas) en tres LiteBeam: cpe_200_223 2.3 MiB, cpe_210_235 2.5 MiB y
     cpe_210_9 2.8 MiB. Es el margen a vigilar antes de sumar servicios en esos equipos.
   - En panel1_ap, MemAvailable (6.9 MiB) queda apenas debajo de MemFree (7.1 MiB).
3. **SSH intermitente en cpe_200_169 y cpe_210_21:** ambos estan en MCS 0/0. En W329 sus fallos fueron
   AuthenticationException y SSHException, con 33-66% de perdida de ping.
   - La ultima muestra de cpe_200_169 da 206.5 ms, contra 33 ms de mediana.
   - Son los otros dos enlaces degradados de la red, ademas de cpe_210_9.
4. **Panel2 sin mejora de RTT demostrada:** el AP pasa de 8/11.2 ms (21, airOS) a 14/17.8 ms (23).
   Las CPE estan en 16-33 ms de mediana.
5. **Panel1, Panel3 y PtP-Colo** se mantienen en 0-15 ms de mediana. La excepcion es cpe_210_9 (23 ms, Wave 324).
6. **Ultimas muestras altas en varias CPE** (58-206 ms) contra medianas de 16-33 ms: la mediana de ventana sigue
   siendo la referencia.

## Coherencia con el reporte oficial (seq 2610)

- MemFree y MemAvailable mediana: iguales en 18/18.
- p50 mediana: igual en 14/18. Difiere en 1-2 ms en cpe_210_166, cpe_200_169, cpe_210_21 y cpe_210_9, porque el
  scorecard incluye las muestras OBSERVED_AP_ASSOCIATION y el reporte no.

## Cobertura Antes (18/18)

| Origen | Nodos |
| :-- | :-- |
| Muestras vivas airOS | panel2_ap (21), ptp_colo_ap (9), ptp_colo_sta (9), 7 CPE de Panel2 (1 c/u), cpe_200_80 (239) |
| Backfill historico (1 fila, sin RTT, no causal) | panel1_ap, cpe_200_41, cpe_200_223, panel3_ap, cpe_210_9, cpe_210_235, cpe_210_238 |

## Historial de versiones

- **v1 (W309):** ultima muestra; su -77.5% en panel2_ap fue retirado.
- **v2 (W317):** mediana de ventana.
- **v3/v4 (W318/W320):** +10 ciclos frescos.
- **v5 (W326):** 18/18 OpenWrt, canal IW y memoria.
- **v6 (W329):** +10 ciclos; cpe_200_80 n=12; memoria con 12 o mas lecturas en 16/18.
- **Detalle:** Wave 312 (atipicos) y Wave 324 (diagnostico RF de cpe_210_9).

## Limites

- cpe_200_169 (10) y cpe_210_21 (7) no llegan a 12 lecturas de memoria por fallos de SSH.
- Todas las muestras frescas son de la tarde-noche del 28/10.
- Sin afirmacion causal, de QoE ni de champion.
- Fuera del registro: 3 CPE de Panel3 sin Despues y 3 conflictos de roster (wave295).
