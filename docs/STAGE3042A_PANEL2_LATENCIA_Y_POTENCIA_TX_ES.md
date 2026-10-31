<!-- doc-head: Stage 3042A (W382) ES: Panel2-Guarida latencia por CPE con la sonda del colector de W377 (30 min, 18 nodos a la vez) y lectura de potencia TX en Panel1/2/3 y PtP-Colo, solo lectura. El tramo de radio de Panel2 tiene mediana 40 ms frente a 3 ms en Panel1 y 12 ms en Panel3. La potencia efectiva es igual a la configurada y a la de airOS, asi que no explica el salto de senal de W377; el salto es de escala de reporte (INFERRED) -->
Que cubre: latencia p50/p95/p99 y perdida de las 7 CPE de Panel2 contra Panel1 y Panel3, y potencia configurada contra efectiva con dominio regulatorio.
Estado: solo lectura. ICMP del colector; 17 sesiones SSH con la clave de host fijada, una por nodo; cpe_200_169 sin SSH. 0 escrituras de config.
Datos maquina: artifacts/autoresearch/wave382_panel2_latency_txpower.json. Informe: artifacts/2026-10-30-panel2-latencia-txpower.html.
Leer cuando: antes de tocar el control de tasa o la potencia de Panel2, o de citar mejoras de senal por OpenWrt.
<!-- /doc-head -->
# Stage 3042A: Panel2 latencia y potencia TX (W382)

## 1. Metodo

- **Sonda:** `local_ping` del daemon (API ICMP de Windows, 1000 ms de espera), 1 eco por segundo, 30 min, los 18 nodos a la vez.
- **Salto de radio:** RTT de la CPE menos RTT de su AP en el mismo segundo.
- **Potencia:** un comando de lectura por nodo con el `SshPool` del daemon: `iw dev info`, `iwinfo`, `uci show wireless`, `iw reg get`, `iw phy` del canal en uso y `survey dump`.
- **Antes:** `radio.1.txpower` de los respaldos airOS del 18 al 28/10 en `artifacts/backups/` y `artifacts/canary_panel1_guarida/`.

## 2. Latencia (MEASURED, 30/10)

| Celda | CPE | p50 CPE | p95 CPE | p50 radio | p95 radio |
| :-- | --: | --: | --: | --: | --: |
| Panel1 | 3 | 15 | 54,5 | 3 | 24 |
| Panel2 | 7 | 53 | 146,5 | 40 | 132,2 |
| Panel3 | 3 | 25 | 74 | 12 | 57,5 |

- Las CPE de Panel2 tienen p50 de 44 a 102,5 ms; cpe_200_169 pierde 55 % y cpe_210_21 24 %.
- Panel2 ya es OpenWrt: esto es estado actual con referencia cruzada, no un antes y despues.
- Confusores: 7 estaciones en Panel2 contra 3; cerca de 4 % de perdida comun en todos los nodos por el camino al colector.
- Las CPE de Panel2 transmiten en MCS 0 a 3; las de Panel1 en MCS 4 a 6.

## 3. Potencia TX (MEASURED salvo que diga otra cosa)

- **Efectiva = configurada** en los 17 nodos leidos.
- **Contra airOS:** Panel2 y PtP 24 a 24 dBm; Panel3 AP 24 a 20; Panel1 AP 24 a 23; cpe_210_239 20 a 24; cpe_200_41 21 a 23; cpe_200_223 20 a 23.
- En Panel3 la potencia bajo 4 dB y la senal reportada subio 10 a 13 dB: **la potencia no explica el salto de W377 (CONFIRMED)**.
- **Dominio:** uci AR en Panel2, Panel3 y PtP; US en Panel1. El phy queda en US (dominio propio). Limite 30 dBm en 5,7-5,8 GHz y 23 dBm en el canal de Panel1. Ninguno fija antenna_gain.

## 4. Escala de senal (INFERRED)

- ath10k-ct con debugfs usa el ruido medido por cadena: -101 a -109 dBm. airOS reportaba -93 (Panel2) y -99 (PtP).
- Estaciones con -55 a -64 dBm reportados siguen en MCS 0, lo que no cuadra con 15 dB reales de mejora.
- Los dBm de airOS y OpenWrt no son comparables entre si. Confirmarlo exige el banco con la misma atenuacion.

## 5. Contrato Karpathy: TARGET_NOT_MET

- panel3_admitter_running: true (MEASURED).
- cpe_210_9_tx_failed_delta_pct: UNKNOWN; el contador acumulado subio 54409 y el contrato no define linea de base.
- fq_overmemory_delta: 1132 en panel3_ap durante la ventana (MEASURED), no 0.
