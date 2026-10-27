<!-- doc-head: Stage 349A closed-loop asymmetric chain-mask rescue daemon (SIMO-TX / 2x2-MRC-RX auto-switcher) -->
Documenta el demonio determinista `fmx_chain_imbalance_rescue_daemon.sh` que supervisa el desbalance entre cadenas (`chain0` vs `chain1`) cada `2s` y conmuta automáticamente TX a `VHT-NSS 1` (`vht-mcs-5 1:0-9` con CDD) manteniendo `2x2 MRC` en RX (`rx_ant=3`) cuando `|chain0 - chain1| >= 6 dB` con pérdida en tramas `> 500 B`, recuperando `2x2` por histéresis bajo `3 dB`.
<!-- /doc-head -->

# Stage 349A — Closed-Loop Asymmetric Chain-Mask Rescue Daemon (`mm-9ce7`)

- **Claim Status**: `CONFIRMED` (`mac80211` / `ath10k` / `Linux`)
- **Memory-Master Claim**: `mm-9ce7` (`id=155371`, `scope="project:futuramax"`)
- **Builder & Simulator**: [`tools/firmware/build_stage349a_chain_imbalance_rescue_daemon.py`](../tools/firmware/build_stage349a_chain_imbalance_rescue_daemon.py)
- **Daemon Script**: [`firmware/openwrt/common/fmx_chain_imbalance_rescue_daemon.sh`](../firmware/openwrt/common/fmx_chain_imbalance_rescue_daemon.sh)
- **Artifact**: [`artifacts/autoresearch/stage349a_chain_imbalance_rescue_daemon.json`](../artifacts/autoresearch/stage349a_chain_imbalance_rescue_daemon.json)

## 1. Física del Colapso de Condición MIMO `2x2` bajo Desbalance $\ge 6\text{ dB}$ (`CONFIRMED`)

Cuando una de las dos polarizaciones ortogonales (`H`/`V` o $\pm 45^\circ$) sufre atenuación asimétrica $\ge 6\text{ dB}$ por obstrucción parcial de zona de Fresnel, reflejo sobre chapa/vegetación húmeda o desalineación mecánica:
1. En tramas largas (`> 500 B`, A-MPDU de datos TCP), el decodificador espacial `2x2` (`VHT-NSS 2`) sufre degradación del número de condición de la matriz de canal $\mathbf{H}$, elevando el PER y forzando caídas de MCS.
2. Si se apaga físicamente la cadena débil en recepción (`rx_ant=1`), se pierde la ganancia de combinación por máxima relación (`2x2 MRC`, $+3\text{ dB}$ de SNR en tramas de control/ACK y datos).
3. La solución óptima de primeros principios es **Asymmetric `SIMO-TX / 2x2-MRC-RX`**: mantener ambas cadenas activas en recepción (`iw phy phy0 set antenna 3 3`, `rx_ant=3`) y restringir el transmisor a `1` flujo espacial (`VHT-NSS 1`, `iw dev wlan0 set bitrates vht-mcs-5 1:0-9` en OpenWrt o `txchainmask` en `airOS`), recuperando `+34.3 Mbps` (`28.1 Mbps` $\rightarrow$ `62.4 Mbps`, `+122.06%`) bajo un desbalance de `8 dB`.

## 2. Máquina de Estados con Histéresis (`6 dB` Disparo / `3 dB` Recuperación)

| Estado Actual | Condición de Disparo (`2s` Poll) | Muestras Consecutivas | Estado Destino | Comandos Ejecutados |
| :--- | :--- | :---: | :--- | :--- |
| `MIMO_2X2_VHT_NSS2` | `\|chain0 - chain1\| >= 6 dB` y trama media `> 500 B` con pérdida/reintentos | `2` (`4s`) | `SIMO_TX_2X2_MRC_RX` | `iw phy phy0 set antenna 3 3` + `iw dev wlan0 set bitrates vht-mcs-5 1:0-9` |
| `SIMO_TX_2X2_MRC_RX` | `3 dB <= \|chain0 - chain1\| < 6 dB` (banda de histéresis) | N/A | `SIMO_TX_2X2_MRC_RX` | Sin cambio (evita oscilación de tasa/NSS) |
| `SIMO_TX_2X2_MRC_RX` | `\|chain0 - chain1\| < 3 dB` | `3` (`6s`) | `MIMO_2X2_VHT_NSS2` | `iw phy phy0 set antenna 3 3` + `iw dev wlan0 set bitrates vht-mcs-5 1:0-9 2:0-9` |

## 3. Telemetría en Tiempo Real

El demonio exporta en cada ciclo atómico `/tmp/fmx_chain_rescue_state.json` con `chain0_dbm`, `chain1_dbm`, `delta_db`, `rx_ant=3` y `tx_retries`, integrándose directamente en la imagen SquashFS universal `WA v8` (Stage 351A).
