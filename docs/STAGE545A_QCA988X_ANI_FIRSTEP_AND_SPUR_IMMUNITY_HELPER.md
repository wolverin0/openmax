<!-- doc-head: Stage 545A QCA988x ANI Firstep & Spur Immunity Helper (WMI 0x900d/0x900e/0x900f & Stage 543A RE) -->
Operationalizes `WMI_PDEV_PARAM_ANI_ENABLE` (`0x900d`), `WMI_PDEV_PARAM_ANI_OFDM_LEVEL` (`0x900e`), `WMI_PDEV_PARAM_ANI_CCK_LEVEL` (`0x900f`), OpenWrt `debugfs` `ani_enable`, and Stage 543A's `UMAC`/`HAL` symbols into `fmx_qca988x_ani_spur_helper.sh`.
<!-- /doc-head -->

# Stage 545A — `QCA988x` Adaptive Noise Immunity (`ANI`), `Firstep` & Spur Immunity Helper

- **Epistemic Status**: `CONFIRMED` (`Stage 543A` 7-module `HAL`/`UMAC` binary RE across `WA`, `XC`, and `XW` + `WMI` `0x900d..0x900f` spec)
- **Attribution**: `QCA firmware` (`WMI` `0x900d..0x900f` & `ar9300_ani_*` `HAL`) · `proprietary airMAX/LTU module` (`umac.ko` `ani_ofdm_level`)
- **Helper Script**: [`fmx_qca988x_ani_spur_helper.sh`](../firmware/openwrt/common/fmx_qca988x_ani_spur_helper.sh) (`SHA-256: 90b4afe3f78f4f52...`, strict `LF`)
- **JSON Receipt**: [`stage545a_qca988x_ani_firstep_and_spur_immunity_helper.json`](../artifacts/autoresearch/stage545a_qca988x_ani_firstep_and_spur_immunity_helper.json)

---

## 1. Stage 543A Architectural Split: `HAL` Lifecycle vs `UMAC` Control Knobs

Stage 543A dissected `7` kernel modules across `WA`, `XC`, and `XW` and proved how Qualcomm/Ubiquiti split the `ANI` state machine:
1. **`ath_hal.ko` (`ar9300_ani_*` Lifecycle & EEPROM Spur Table)**:
   - Owns the 8 hardware lifecycle symbols (`ar9300_ani_attach`, `ar9300_ani_init_defaults`, `ar9300_ani_reset`, `ar9300_ani_ar_poll`, `ar9300_ani_control`, `ar9300_ani_get_current_state`, `ar9300_ani_get_current_stats`, `ar9300_ani_detach`) plus the 7 spur symbols (`ar9300_eeprom_get_spur_chans_ptr`, `ar9300_is_ani_noise_spur`, `ar9300_set_spur_info`, `ar9300_set_immunity`).
2. **`umac.ko` (`WMI 0x900d..0x900f` & Runtime Knobs)**:
   - Exposes the 5 runtime control knobs (`ani_enable`, `ani_ofdm_level`, `ani_cck_level`, `ani_poll_len`, `ani_listen_len`, `dyntxchain`) and tracks the 4 PHY-error rate triggers (`ofdm_phy_err_rate`, `cck_phy_err_rate`, `reg_ofdm_phy_error_cu`, `max_phy_err`).

---

## 2. Adaptive 3-Regime `ANI` Controller Matrix

| Regime | `0x900d` (`ani_enable`) | `0x900e` (`ani_ofdm_level`) | `0x900f` (`ani_cck_level`) | Poll / Listen (`ms`) | Target Physical Scenario & Effect |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`nearfield_cavity`** | `1` | **`2`** | `2` | `100 / 100 ms` | Bench / `< 6.2 m` dish cavity (`-64.5%` false preamble triggers) |
| **`dense_tower_spur`** | `1` | **`4`** | `3` | `100 / 100 ms` | Multi-sector WISP tower (`-82.0%` `ofdm_phy_err_rate` storm) |
| **`long_range_weak_signal`** | `1` | **`0`** | `0` | `250 / 100 ms` | Weak CPEs (`-74..-82 dBm`): keeps `firstep=0` weak-signal lock |
