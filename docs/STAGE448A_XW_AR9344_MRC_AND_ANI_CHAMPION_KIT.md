<!-- doc-head: Stage 448A XW (M5 AR9344) Maximum Ratio Combining (MRC) & Adaptive Noise Immunity (ANI) Champion Kit -->
Documents the `XW` (`M5` `AR9344`) MRC, asymmetric chainmask, and Adaptive Noise Immunity (`ANI`) kit (`fmx_xw_ar9344_mrc_ani_champion.sh`) built from Stage 396A's 8-module binary RE of `XW.v6.1.4` and `XW.v6.3.6`.
<!-- /doc-head -->

# Stage 448A — `XW` (`M5` `AR9344`) `MRC` & `ANI` Immunity Champion Kit

- **Epistemic Status**: `CONFIRMED` (`Stage 396A` 8-module ELF symbol & string RE + live `PowerBeam M5` `.144` bench anchor)
- **Attribution**: `proprietary airMAX/LTU module` (`ath_hal.ko`, `ath_dev.ko`, `ubnt_poll.ko`, `ubnt_ewma_ht.ko`) · `Linux` (`ath9k` `AR9300`/`AR9344`)
- **Kit Script**: [`fmx_xw_ar9344_mrc_ani_champion.sh`](../firmware/openwrt/common/fmx_xw_ar9344_mrc_ani_champion.sh) (`SHA-256: 9a4ed1e1c6194ec1...`, strict `LF`)
- **JSON Receipt**: [`stage448a_xw_ar9344_mrc_and_ani_champion_kit.json`](../artifacts/autoresearch/stage448a_xw_ar9344_mrc_and_ani_champion_kit.json)

---

## 1. Stage 396A Binary RE Ground Truth (`XW.v6.1.4` & `XW.v6.3.6`)

Stage 396A dissected `8` kernel modules (`580` defined symbols in `ath_hal.ko`, `572` in `ath_dev.ko`, `62` in `ubnt_ewma_ht.ko`) across both `XW.v6.1.4` and `XW.v6.3.6`:
1. **`ath_hal.ko` (`SHA-256: 880183f0...`)**: Exports `ar9300_is_ani_noise_spur` and `ath_hal_log_ani_callback_register`, driving the `AR9344` baseband `firstep` and `cycpwr` Adaptive Noise Immunity (`ANI`) state machine.
2. **`ath_dev.ko` (`SHA-256: ece709ec...`)**: Exports the 9-symbol dynamic chainmask selection engine (`ath_chainmask_sel_logic`, `ath_chainmask_sel_up_rssi_thres`, `ath_chainmask_sel_down_rssi_thres`, `ath_set_rx_chainmask`, `ath_set_tx_chainmask`, `ath_txchainmask_reduction`).
3. **`ubnt_poll.ko` & `ubnt_ewma_ht.ko` (`SHA-256: a967dd7a...`)**: Exports `ubnt_ewma_delegate_on` (`__param_str_ubnt_ewma_delegate_on`) and `ewma_ht_get_rate` / `ewma_ht_tx_status`, controlling TDMA rate delegation between `ubnt_poll` and the `EWMA-HT` rate table.

---

## 2. Dual-Stack Runtime Tuning Architecture (`airOS 6 XW` + `OpenWrt ath9k`)

| Layer | Knob / Symbol Hook | Setting | Engineering Purpose |
| :--- | :--- | :---: | :--- |
| **Layer 1 (RX `MRC`)** | `rxchainmask` (`ath_set_rx_chainmask` / `ath9k/rx_chainmask`) | **`0x3` (`2x2`)** | Preserves full `2x2` Maximum Ratio Combining (`+3 dB` coherent aperture gain) on RX at all times |
| **Layer 2 (Asymmetric TX)** | `txchainmask` (`ath_set_tx_chainmask`) | **`0x3` $\leftrightarrow$ `0x1`** | Drops to single-chain TX (`0x1`) when polarization delta `>= 6 dB` (`+5 dB` RSSI, `-68%` `p95` RTT on `.144`) |
| **Layer 3 (`ANI` Spur Filter)** | `ar9300_is_ani_noise_spur` / `ath9k/ani` | **`1` (`Enabled`)** | Adapts `firstep` and `cycpwr` thresholds against non-802.11 RF spurs |
| **Layer 4 (`EWMA-HT` Rate)** | `ubnt_ewma_delegate_on` | **`1`** | Enables `ubnt_ewma_ht.ko` airtime-aware HT rate selection inside `ubnt_poll` TDMA slots |
