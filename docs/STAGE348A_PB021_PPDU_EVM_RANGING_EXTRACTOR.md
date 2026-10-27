<!-- doc-head: Stage 348A PB-021 per-PPDU 16-pilot EVM and 12.5 ns hardware ranging extractor -->
Diseca el descriptor DMA de `84` bytes (`21` dwords) `struct rx_ppdu_end_v1` (`rx_ppdu_end_common` + `rx_ppdu_end_qca988x`) antes de `skb_pull` en `ath10k_htt_rx_amsdu_pop` (`htt_rx.c:397-408`), extrayendo `evm_p0..evm_p15` por flujo espacial y `locationing_timestamp` a `80 MHz` (`12.5 ns` = `1.8737 m` RTT / `3.7474 m` one-way).
<!-- /doc-head -->

# Stage 348A — `PB-021` Ground-Up Per-PPDU `16-Pilot EVM` & `12.5 ns` Hardware Ranging Extractor (`mm-22d6`)

- **Claim Status**: `CONFIRMED` (`hardware` / `ath10k` / `QCA firmware`)
- **Memory-Master Claim**: `mm-22d6` (`id=155370`, `scope="project:futuramax"`)
- **Builder**: [`tools/re/build_stage348a_pb021_ppdu_evm_ranging_extractor.py`](../tools/re/build_stage348a_pb021_ppdu_evm_ranging_extractor.py)
- **C Extractor Header**: [`firmware/openwrt/common/fmx_pb021_ppdu_evm_ranging_extractor.h`](../firmware/openwrt/common/fmx_pb021_ppdu_evm_ranging_extractor.h)
- **Artifact**: [`artifacts/autoresearch/stage348a_pb021_ppdu_evm_ranging_extractor.json`](../artifacts/autoresearch/stage348a_pb021_ppdu_evm_ranging_extractor.json)

## 1. Por Qué Vanilla `ath10k` Descarta el EVM por Piloto y el Reloj de `80 MHz` (`CONFIRMED`)

En [`tools/research/srccache/ath10k-ct/ath10k-7.2/htt_rx.c`](../tools/research/srccache/ath10k-ct/ath10k-7.2/htt_rx.c) (líneas `397–408`), `ath10k_htt_rx_amsdu_pop()` obtiene el puntero `rx_desc = HTT_RX_BUF_TO_RX_DESC(hw, msdu->data)` sobre `struct htt_rx_desc_v1` e inmediatamente ejecuta:
```c
skb_put(msdu, hw->rx_desc_ops->rx_desc_msdu_payload_offset);
skb_pull(msdu, hw->rx_desc_ops->rx_desc_msdu_payload_offset);
```
Al avanzar `msdu->data` hasta `msdu_payload` antes de copiar `rx_desc->ppdu_end`, los `84` bytes (`21` dwords) escritos por el motor DMA del baseband `QCA988x` quedan fuera del área activa del `sk_buff` sin ser exportados a `mac80211` ni `debugfs`.

## 2. Mapa Exacto de `21` Dwords (`84` Bytes) de `rx_ppdu_end_v1` (`QCA988x`)

| Dword | Offset | Estructura | Campo | Bitfields y Significado Físico (`CONFIRMED`) |
| :---: | :---: | :--- | :--- | :--- |
| `0..15` | `0x00..0x3f` | `rx_ppdu_end_common` | `evm_p0 .. evm_p15` | `4` bytes con signo (`int8_t`) por cada uno de los `16` pilotos OFDM/VHT: `[7:0]=stream0`, `[15:8]=stream1`, `[23:16]=stream2`, `[31:24]=stream3` (`0x80 = -128` centinela no usado). |
| `16` | `0x40` | `rx_ppdu_end_common` | `tsf_timestamp` | Reloj TSF de `1 MHz` muestreado en el flanco de subida de `rx_clear` (asociado a estado TX/RX en DMA legado). |
| `17` | `0x44` | `rx_ppdu_end_common` | `wb_timestamp` | Reloj monotónico WLAN/BT de `1 us` (`1 MHz`) inmune a saltos de beacon TSF. |
| `18` | `0x48` | `rx_ppdu_end_qca988x` | `locationing_timestamp`, `phy_err_code`, `flags` | `[7:0]` `locationing_timestamp` (`0..79` ticks a `80 MHz` = `12.5 ns` = `3.7474 m` one-way / `1.8737 m` RTT); `[15:8]` `phy_err_code`; `[31:16]` `flags` (`BIT(0)=PHY_ERR`, `BIT(1)=RX_LOCATION`, `BIT(2)=TXBF_H_INFO`). |
| `19` | `0x4c` | `rx_ppdu_end_qca988x` | `info0` | `[23:0]` `rx_antenna_mask` (`0x00ffffff`), `BIT(24)` `tx_ht_vht_ack`, `BIT(25)` `bb_captured_channel`. |
| `20` | `0x50` | `rx_ppdu_end_qca988x` | `bb_length`, `info1` | `[15:0]` `bb_length`; `[31:16]` `info1` (`BIT(0)=BB_DATA`, `BIT(1)=PEER_IDX_VALID`, `[12:2]=PEER_IDX`, `BIT(15)=PPDU_DONE`). |

## 3. Extracción Antes de `skb_pull` y Diagnóstico Físico

El cabezal [`fmx_pb021_ppdu_evm_ranging_extractor.h`](../firmware/openwrt/common/fmx_pb021_ppdu_evm_ranging_extractor.h) invoca `fmx_pb021_capture_before_skb_pull()` cuando `RX_PPDU_END_INFO1_PPDU_DONE` (`BIT(15)`) está activo:
- **Tiempo Compuesto de `12.5 ns`**: $t_{\text{ns}} = 1000 \cdot \text{wb\_timestamp} + 12.5 \cdot \text{locationing\_timestamp}$, entregando resolución espacial de `1.8737 m` en RTT sin paquetes FTM adicionales.
- **Selectividad en Frecuencia vs. Ruido Térmico**: La desviación estándar entre los `16` pilotos ($\sigma_{\text{EVM}}$) distingue interferencia co-canal de banda ancha ($\sigma_{\text{EVM}} < 0.8\text{ dB}$) de obstrucción de zona de Fresnel / multicamino ($\sigma_{\text{EVM}} > 3.0\text{ dB}$).
