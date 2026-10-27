<!-- doc-head: STAGE12_CROSS_PLATFORM_HARDWARE_AND_FIRMWARE_ATLAS.md preserved document content -->
<!-- /doc-head -->

# Stage 12: Cross-Platform Firmware & Hardware Capability Atlas (`WA`, `XC`, `2WA`, `XW/XM`, `LTU`, `RouterOS`)

## 1. Executive Summary

This document synthesizes the unified hardware, silicon control boundary, and firmware capability atlas implemented in [`analysis/cross_platform_hardware_atlas.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/analysis/cross_platform_hardware_atlas.py) and materialized in [`artifacts/qca988x/cross_platform_hardware_atlas_20261024.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/qca988x/cross_platform_hardware_atlas_20261024.json) (`atlas_sha256: c796020c6985d90be27935f2745f7c858e3bb02041d8df39e9057c4d97ea9380`).

---

## 2. Unified Platform Capability Matrix (`6` Families, `1,058` Cataloged Knobs)

| Platform ID | Host SoC | Radio Silicon & Architecture | Channel Widths (MHz) | Max Modulation | Per-Frame Host Rate Control? | Native TDMA / Interop Stack |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **`UBNT_AIRMAX_AC_WA`** | `AR9342` (`535 MHz`, `64 MB`) | `QCA9882 / AR9888 v2.0` (`88 MHz` PCU clock, Xtensa RAM `@ 0x00400000`) | `5, 10, 20, 30, 40, 80` | `256-QAM 5/6` (`MCS 9`) | No (WMI/HTT offloaded) | `ubnt_poll_host.ko` (`Mode B`) or OpenWrt `ath10k` + `ETH_P_TEB` + Two-Stage IE (`Mode A/A+`) |
| **`UBNT_AIRMAX_AC_XC`** | `QCA9558` (`720 MHz`, `128 MB`) | `QCA9880 / AR9888 v2.0` + `AirPrism` RF pre-selector + `AirView` | `10, 20, 30, 40, 50, 60, 80` | `256-QAM 5/6` (`MCS 9`) | No (WMI/HTT offloaded) | `ubnt_poll_host.ko` (`allow_80211=1`, `ubnt_op_mode=0`, `addmtikie=1` for multi-vendor AP) |
| **`UBNT_AIRMAX_AC_2WA`** | `QCA9558 / AR9342` | 2.4 GHz `VHT20/40` + `AirPrism` 2.4 GHz active filter | `10, 20, 40` | `256-QAM 5/6` (TurboVHT) | No | `ubnt_poll_host.ko` (`cms_bias`, `voip_bias`, `daprot`) |
| **`UBNT_AIRMAX_M5_XW_XM`** | `AR9342` (`XW`) / `AR7241` (`XM`) | Integrated `AR9300` / `AR9280` 802.11n 2x2 Host-MAC | `5, 8, 10, 20, 30, 40` | `64-QAM 5/6` (`MCS 15`) | **Yes (`ath9k` DMA)** | `ubnt_poll.ko` (`XW.v6.3.2`) or standard `802.11n` WDS (`polling=disabled`) |
| **`UBNT_LTU_AMESOC3`** | `amesoc3` ARM + FPGA/ASIC | Proprietary LTU custom OFDM/TDMA silicon | `10..100` | `4096-QAM` (`12x`, `97%/90%` gate) | No | Proprietary LTU TDMA (`afltu.v2.4.0`; non-802.11) |
| **`MIKROTIK_ROUTEROS_80211_AND_BNG`** | `AR9344` (`SXT Lite5`) / `ARM64` (`BNG`) | Integrated `AR9344` 802.11a/n (`SXT`) + RouterOS v7 BNG | `5, 10, 20, 40` | `64-QAM 5/6` (`MCS 15`) | No | `802.11n` `station-wds` / `station-pseudobridge` + BNG Hierarchical `CAKE` |

---

## 3. Verification

```powershell
python analysis/cross_platform_hardware_atlas.py
python -m pytest tests/test_cross_platform_hardware_atlas.py -v
```
