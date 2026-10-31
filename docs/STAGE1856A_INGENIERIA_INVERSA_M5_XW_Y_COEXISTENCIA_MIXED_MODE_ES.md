<!-- doc-head -->
*STAGE1856A — Ingeniería inversa de M5 XW y coexistencia mixed-mode con airMAX AC*
# STAGE 1856A — M5 XW y mixed-mode

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0` en los tres recibos.
- Todo se midió sobre siete módulos ELF32 MIPS big-endian que ya estaban en el repositorio. Nada se cargó, nada se ejecutó y no hubo captura en vuelo.
- Etiquetas `CONFIRMED`, `INFERRED`, `INFERRED_ANALYTIC`, `UNKNOWN` y `REFUTED`. Identificadores de CPE con prefijo `cpe_`; no se usan apellidos.

## 1. Stage 1854A — el driver M5
- `CONFIRMED`: `ubnt_poll.ko` de XW 6.1.4 mide **539424** bytes, conserva **553** funciones y **312112** bytes de `.text`. No tiene sección `__param`.
- `CONFIRMED`: contiene una capa de compatibilidad **`_11ac_compat_lmac_*`** de **43 funciones** y **9208** bytes, el **2.95 %** de `.text`.
- `CONFIRMED`: los puntos de entrada de esa capa son `_11ac_compat_lmac_on_classify`, `_11ac_compat_lmac_on_find_rate`, `_11ac_compat_lmac_on_set_rate_series`, `_11ac_compat_lmac_on_before_ppdu_tx`, `_11ac_compat_lmac_on_tx_ppdu_done` y `_11ac_compat_lmac_get_sta_capacity`.
- `CONFIRMED`: el driver M5 expone la superficie de sincronización TDMA como cadenas de `.rodata.str1.4`: `tx_sync_master`, `tx_sync_mode`, `tx_sync_udp_port`, `tx_sync_down_slot`, `tx_sync_up_slot`, `tx_sync_slot_unit` y `tx_sync_act_thresh`.
- `CONFIRMED`: existe un contador por cliente en la cadena `Total clients : %d Legacy : %d Active : %d Downlink Active: %d` y una etiqueta `Legacy` independiente.
- `CONFIRMED`: el módulo importa `ieee80211_set_assoc_req_rx_vendor_ie_hook`, `ieee80211_set_assoc_req_tx_vendor_ie_hook`, `ieee80211_notify_node_join` y `ieee80211_chan2mode`.

## 2. Stage 1854A — el contraste con AC
- `CONFIRMED`: `ubnt_poll_host.ko` de XC 8.7.25 conserva **154** funciones y **0** funciones `_11ac_compat_lmac_*`.
- `INFERRED`: la asimetría es el hallazgo. El AP M5, que es 802.11n, necesita una LMAC de compatibilidad para atender peers 11ac; el AP AC no la necesita porque ya es 11ac nativo.
- `CONFIRMED`: el `umac.ko` de M5 publica los nombres de opmode heredados `11nght20`, `11nght40plus`, `11naht20`, `11naht40plus` y sus variantes, y símbolos como `ieee80211_get_vap_opmode_count` y `wlan_vap_get_opmode`.
- `CONFIRMED`: el `ath_dev.ko` de M5 conserva `ath_set_tx_chainmasklegacy`, `ath_set_rx_chainmasklegacy`, `ath_rate_tx_complete_11n` y `ath_setslottime`.

## 3. La compuerta mixed-mode
- `REFUTED`: `allow_80211` aparece **0 veces** en los siete módulos medidos. No es un símbolo ni una cadena de este conjunto, así que la compuerta de interoperabilidad del lado AC vive fuera de esta evidencia.
- `INFERRED`: la coexistencia medible no está en un knob llamado `allow_80211`, sino en la capa `_11ac_compat_lmac_*` del driver M5, que clasifica, elige tasa y construye el PPDU de los peers 11ac.
- `UNKNOWN`: el camino de ejecución que enruta un peer heredado por esa capa. Los nombres y el contador lo sugieren; no se trazó.

## 4. Penalización de airtime (modelo analítico)
- `INFERRED_ANALYTIC`: `airtime_us = 40 + ((bytes + 36) * profundidad * 8) / tasa_mbps`. Preámbulo fijo de **40 µs**, sobrecarga de **36 bytes** y tasas PHY de tabla, no medidas.
- `CONFIRMED` como aritmética del modelo, `INFERRED_ANALYTIC` como conclusión, para 1500 bytes:

| Caso | Profundidad 1 | Profundidad 16 | Profundidad 64 |
| :--- | ---: | ---: | ---: |
| 2x2 n 300 vs 2x2 ac 866.7 | 1.494 | 2.606 | 2.809 |
| 3x3 n 450 vs 4x4 ac 1733.3 | 1.429 | 3.108 | 3.621 |

- `INFERRED_ANALYTIC`: en el conjunto completo de casos el rango es **1.028 a 1.719** con profundidad 1 y **1.618 a 5.391** con profundidad 64.
- `INFERRED`: con tramas pequeñas manda el preámbulo y la penalización casi desaparece; con agregación profunda manda la tasa y la penalización se multiplica. Por eso un solo número sería engañoso.
- `UNKNOWN`: el MCS, NSS y ancho de canal reales de cada peer, la profundidad de agregación real y el airtime efectivamente concedido por el planificador.

## 5. Stage 1855A — cobertura del catálogo
- `CONFIRMED`: **11 objetivos**. **8** quedan en solo binario, **2** en binario más catálogo y **1** queda refutado (`allow_80211`).
- `CONFIRMED`: la cobertura del catálogo de 571 sobre la superficie M5 medida es **2 de 10**, ratio **0.20**.
- `CONFIRMED`: la familia TDMA/mixed-mode del catálogo tiene **3** knobs y **1** no aparece en ningún binario medido.
- `CONFIRMED`: solo `tx_sync_slot_unit` encuentra una contraparte (`WMI_10X_VDEV_PARAM_SLOT_TIME`, frontera QCA 10.1) y `opmode_11n` encuentra `opmode_notify`. El resto de la sincronización TDMA no está catalogada.

## 6. Stage 1857A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax` y `source_agent=opencode-session`.
- `CONFIRMED`: la lectura de ida y vuelta por `list_claims` devolvió los **3** con estado `candidate` y alcance `project:futuramax`.
- `CONFIRMED`: ambos recibos llevan los identificadores en `pillar_e_memory_master_claim_id`.

## 7. Lo que no se prueba
- `UNKNOWN`: cualquier penalización medida en el aire. El modelo es aritmética declarada, no un experimento.
- `UNKNOWN`: el reparto real de airtime entre peers n y ac en un panel mixto.
- `UNKNOWN`: el valor y la unidad de `tx_sync_slot_unit` en el equipo.
- `UNKNOWN`: el efecto de la capa de compatibilidad sobre la latencia p95 de un CPE heredado.

## 8. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1854A` | `tools/re/extract_stage1854a_m5_xw_legacy_tdma_and_mixed_mode_re.py` y su recibo |
| `1855A` | `tools/re/reconcile_stage1855a_m5_xw_and_mixed_mode_knobs.py` y su recibo |
| `1857A` | `tools/verify/record_stage1857a_memorymaster_ingest.py` y su recibo |
| `1858A` | `tests/test_stage1854a_to_1859a_suite.py` |
| `1859A` | `tools/verify/verify_stage1859a_wave136_opencode_gate.py` y la compuerta de la wave |
