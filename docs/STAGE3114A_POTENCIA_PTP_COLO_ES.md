<!-- doc-head: Stage 3114A (W452 + W452b) ES: canario de potencia del PtP-Colo para llevar la senal a cerca de -45 dBm; W452 ABORTED (escalera agotada); W452b con escalera nueva hallo STA 9 / AP 8 dBm = -45/-46 dBm pero dio NO_GO (retries de subida x4,6 y MCS de subida 8 a 7); W452c en el punto intermedio STA 13 / AP 12 (-42/-41 dBm) tambien NO_GO (retries de subida x3,1); vuelta a 24 dBm verificada, nada persistido, /tmp limpio -->
Que cubre: hechos del enlace, W452 (resumen), regla W452b, ventanas, escalera, veredicto y siguiente paso.
Estado: CLOSED. W452 ABORTED; W452b NO_GO. Potencia final 24 dBm en las dos puntas (uci e iw); no hay backup ni rollback en /etc.
Datos maquina: artifacts/autoresearch/wave452b_colo_txpower.json (regla sha256 531f82a38f51..., preregistro 2026-10-31T09:25:15Z, AA1 09:25:23Z) y wave452_colo_txpower.json.
Leer cuando: antes de bajar potencia en el PtP-Colo o en otro enlace OpenWrt ath10k.
<!-- /doc-head -->
# Stage 3114A: potencia del PtP-Colo (W452 y W452b)

## 1. Hechos del enlace (CONFIRMED, leidos en los equipos)

- **Potencia:** 24 dBm en las dos puntas, desde `uci wireless.radio0.txpower=24`. No hay kit `99-fmx-*`; la regdomain es AR.
- **Tasa:** VHT20 2x2, VHT-MCS 8 NSS 2 con SGI = 173,3 Mbit/s en los dos sentidos. En VHT20 no existe MCS 9 para NSS 1 y 2, asi que el enlace ya esta en su techo. Que se pueda subir a MCS 9 queda REFUTED por norma.
- **Expected throughput:** ath10k no lo publica; las reglas usan tx bitrate.
- **Senal a 24 dBm:** el AP recibe -35/-36 dBm (cadenas -38/-40), la STA recibe -32/-33 dBm (cadenas -36/-37).
- **OpenWrt no tiene ATPC como airMAX** (INFERRED: mac80211 solo da potencia fija o el maximo regulatorio). Por eso se buscan valores fijos por punta.

## 2. W452 (resumen, ABORTED)

- **Escalera:** STA en 21, 18, 15, 13 y 12 dBm, y el AP en los mismos pasos, cortando en -42.
- **Resultado:** la STA a 13 dBm dejo al AP en -42; el AP a 12 dBm dejo a la STA en -41. La escalera se agoto, no hubo ventanas B y la vuelta a 24 se verifico.
- **Aprendizaje (CONFIRMED):** la potencia configurada no baja la senal 1:1. De 24 a 21 no cambia nada; los primeros dB del tope no actuan. Causa probable (INFERRED): la tabla por tasa ya transmite MCS 8 por debajo de 24.

## 3. Regla W452b (hasheada antes de AA1)

- **Ventanas:** AA1-AA3 y A1 a 24 dBm, B1 al par objetivo, A2 a 24, B2 al par objetivo; 5 min cada una, 60 s de asentamiento tras cada cambio.
- **Escalera (solo B1):** STA en 13, 12, 11, 10 y 9 dBm, leyendo en el AP. Despues, AP en 12, 11, 10, 9, 8 y 7 dBm, leyendo en la STA.
- **Lectura y corte:** mediana de 3 `signal avg`. Corta en el primer escalon con mediana entre -50 y -45 dBm. Por debajo de -50, o con la escalera agotada, aborta.
- **GO solo si en B1 y B2:**
  - tasa, MCS y NSS por sentido, al menos en el minimo A/A;
  - retries por paquete hasta el maximo A/A;
  - p95 y perdida core del sidecar hasta el maximo A/A;
  - asociacion nunca perdida.
  - La senal se informa, no se usa como gate.
- **Seguridad:** mismo motor que W452. Watchdog compartido `fmx_watchdog.sh` en cada punta, lease de 240 s renovado cada 60 s; vuelve a 24 dBm.
- **Abort:** se pierde la asociacion, hay reasociacion, cambia el boot id, la potencia leida no coincide o MemAvailable baja de 3072 kB.
- **Si GO:** persistir solo `wireless.radio0.txpower` con `uci commit`, con backup en `/etc/fmx_rollback/` y script de vuelta atras.
- **Si NO_GO:** volver a 24 y verificar.

## 4. Ventanas W452b

Columnas: potencia STA/AP (dBm) · senal en AP / STA (dBm) · tasa subida / bajada (Mbit/s, mediana) · MCS x NSS subida / bajada · retries por paquete subida / bajada · p95 core STA / AP (ms) · perdida core STA / AP (%).

| Ventana | Potencia | Senal | Tasa | MCSxNSS | Retries/paq | p95 core | Perdida |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| AA1 | 24/24 | -35 / -32 | 173,3 / 173,3 | 8x2 / 8x2 | 0,0055 / 0,0001 | 2,22 / 0,94 | 0,0 / 0,0 |
| AA2 | 24/24 | -35 / -33 | 173,3 / 173,3 | 8x2 / 8x2 | 0,0059 / 0,0 | 2,15 / 0,90 | 0,0 / 0,0 |
| AA3 | 24/24 | -36 / -32 | 173,3 / 173,3 | 8x2 / 8x2 | 0,0053 / 0,0 | 1,92 / 1,16 | 0,0 / 0,0 |
| A1 | 24/24 | -35 / -33 | 173,3 / 173,3 | 8x2 / 8x2 | 0,0057 / 0,0 | 3,11 / 1,12 | 0,0 / 0,0 |
| B1 | 9/8 | -46 / -46 | 144,4 / 173,3 | 7x2 / 8x2 | 0,0267 / 0,0003 | 3,41 / 1,13 | 0,0 / 0,0 |
| A2 | 24/24 | -35 / -33 | 144,4 / 173,3 | 7x2 / 8x2 | 0,0055 / 0,0001 | 2,12 / 0,97 | 0,0 / 0,0 |
| B2 | 9/8 | -45 / -45 | 144,4 / 173,3 | 7x2 / 8x2 | 0,0252 / 0,0001 | 3,16 / 0,96 | 0,0 / 0,0 |

- **tx_failed:** subida 36 en B1 y 0 en el resto; bajada 14 en AA3 y 0 en el resto.
- **Cadenas en B:** el AP recibe -49/-48 y la STA -50/-48, contra -38/-40 a 24 dBm.

## 5. Escalera W452b (B1)

| Escribe | dBm | Lee | Mediana (dBm) | Lecturas |
| :-- | --: | :-- | --: | :-- |
| ptp_colo_sta | 13 | ptp_colo_ap | -42 | -42, -43, -42 |
| ptp_colo_sta | 12 | ptp_colo_ap | -43 | -42, -43, -43 |
| ptp_colo_sta | 11 | ptp_colo_ap | -43 | -43, -43, -43 |
| ptp_colo_sta | 10 | ptp_colo_ap | -44 | -45, -44, -44 |
| ptp_colo_sta | 9 | ptp_colo_ap | -45 | -45, -47, -45 |
| ptp_colo_ap | 12 | ptp_colo_sta | -41 | -41, -41, -40 |
| ptp_colo_ap | 11 | ptp_colo_sta | -42 | -42, -42, -42 |
| ptp_colo_ap | 10 | ptp_colo_sta | -44 | -44, -43, -44 |
| ptp_colo_ap | 9 | ptp_colo_sta | -44 | -44, -44, -44 |
| ptp_colo_ap | 8 | ptp_colo_sta | -45 | -45, -45, -46 |

- **Par objetivo:** STA 9 dBm y AP 8 dBm.
- **Asociacion:** no se perdio en ningun escalon ni ventana.
- **Potencia:** ath10k acepto 8 y 9 dBm, y la lectura coincidio exacta.

## 6. Veredicto W452b: NO_GO

| Clausula | Banda A/A | B1 / B2 | Resultado |
| :-- | :-- | :-- | :-- |
| Retries de subida | max 0,0059 | 0,0267 / 0,0252 (x4,6) | Falla |
| Tasa de subida | min 173,3 (MCS 8) | 144,4 (MCS 7) / 144,4 | Falla |
| Retries de bajada | max 0,00006 | 0,0003 / 0,0001 | Falla |
| p95 core de la STA | max 2,22 ms | 3,41 / 3,16 ms | Falla |
| NSS, tasa y MCS de bajada, p95 core del AP | dentro de banda | dentro de banda | Cumple |
| Perdida core en las dos puntas | 0 % | 0 % | Cumple |

- **Lectura (INFERRED):** la subida empeora de verdad. Los retries se multiplican por 4,6 solo en B, y A2 a 24 dBm vuelve a 0,0055.
- **Fallas menos limpias:** la caida a MCS 7 de subida, porque A2 a 24 dBm tambien dio 144,4 de mediana. Tambien el p95 de la STA: A1 a 24 dBm dio 3,11 ms.
- **Hipotesis de saturacion: no sostenida.** A 24 dBm el enlace va mejor que a -45 dBm; bajar potencia no aporto nada medible.
- **Estado final (CONFIRMED, readback):** uci 24 e iw 24,00 dBm en las dos puntas, mismo boot id, una estacion asociada, senal -35/-33.
- **Limpieza:** `/tmp/fmx452` y los handles `/tmp/fmx_wd.*` de W452 y W452b quedaron borrados (0 restos). No hay lock del watchdog ni `/etc/fmx_rollback`.

## 7. Siguiente

- **Dejar el PtP-Colo en 24 dBm.** Con potencia fija, llegar a -45 dBm cuesta retries de subida y MCS. Con esta regla no se puede cumplir el objetivo del operador sin degradar el enlace.
- **Si se insiste:** probar un punto intermedio, STA 13 / AP 12 (cerca de -42/-41), con regla nueva hasheada y las mismas ventanas. Es UNKNOWN si ahi los retries siguen dentro de la banda.
- **UNKNOWN:** si el aumento de retries viene solo de la potencia de la STA o tambien de interferencia en el canal 153 a esa hora; no se midio espectro.

## 8. W452c: punto intermedio STA 13 / AP 12 (orden del operador 31/10)

- **Regla:** misma que W452b pero con el par fijo 13/12 (sin escalera); sha256 `41f3eda1...`, preregistrada antes de AA1. Datos: `artifacts/autoresearch/wave452c_colo_txpower.json`.
- **Senal en B:** -42 / -41 dBm (AP / STA), contra -35 / -33 a 24 dBm.

| Ventana | Potencia | Senal | Tasa | MCSxNSS | Retries/paq | p95 core | Perdida |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| AA1 | 24/24 | -36 / -33 | 173,3 / 173,3 | 8x2 / 8x2 | 0,0052 / 0,0001 | 2,13 / 1,19 | 0,0 / 0,0 |
| AA2 | 24/24 | -35 / -33 | 173,3 / 173,3 | 8x2 / 8x2 | 0,0058 / 0,0001 | 3,12 / 1,05 | 0,0 / 0,0 |
| AA3 | 24/24 | -36 / -33 | 173,3 / 173,3 | 8x2 / 8x2 | 0,0054 / 0,0001 | 2,64 / 1,26 | 0,0 / 0,0 |
| A1 | 24/24 | -35 / -33 | 144,4 / 173,3 | 7x2 / 8x2 | 0,0062 / 0,0001 | 3,7 / 1,69 | 0,0 / 0,0 |
| B1 | 13/12 | -42 / -41 | 144,4 / 173,3 | 7x2 / 8x2 | 0,0183 / 0,0002 | 3,75 / 1,75 | 0,0 / 0,0 |
| A2 | 24/24 | -34 / -33 | 173,3 / 173,3 | 8x2 / 8x2 | 0,0066 / 0,0002 | 2,92 / 1,17 | 0,0 / 0,0 |
| B2 | 13/12 | -42 / -41 | 144,4 / 173,3 | 7x2 / 8x2 | 0,0193 / 0,0002 | 3,23 / 1,03 | 0,0 / 0,0 |

- **Veredicto NO_GO.** Retries de subida 0,0183 / 0,0193 contra un maximo A/A de 0,0058 (x3,1) y subida en MCS 7 en las dos B; tambien fallan retries de bajada (0,0002 vs 0,0001) y el p95 core (AP 1,75 vs 1,26 ms; STA 3,75 vs 3,13 ms). Perdida 0 % en todo.
- **Lectura (INFERRED):** la caida de MCS de subida tambien aparece en A1 a 24 dBm, asi que esa clausula es menos limpia; los retries de subida son la senal clara, igual que en W452b.
- **Estado final (CONFIRMED):** uci 24 e iw 24,00 dBm en las dos puntas, mismo boot id, una estacion, senal -34/-33; 0 restos en /tmp.
- **Conclusion:** con potencia fija, cualquier baja (12-13 o 8-9 dBm) sube los retries de subida. El PtP-Colo queda en 24 dBm; no hay punto intermedio que mejore.
