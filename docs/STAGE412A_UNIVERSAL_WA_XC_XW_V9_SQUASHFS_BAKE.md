<!-- doc-head: STAGE412A_UNIVERSAL_WA_XC_XW_V9_SQUASHFS_BAKE.md preserved document content -->
<!-- /doc-head -->


# Stage 412A — Universal `WA v9` + `XC Active-AirPrism v2` + `XW v2` SquashFS (`hsqs`) Bake

- **Status**: `CONFIRMED`
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v9`)**: [`99-fmx-wa-universal-champion-v9`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v9) (`sha256: 6d68db11ce203ad4...`).

## 1. Integrated Ground-Up Stack Across `WA v9`, `XC v2`, & `XW v2` (`CONFIRMED`)
| Component | Path / Knob | Function |
| :--- | :--- | :--- |
| **`Stage 385A` `172`-Window Winner** | `htt_max_amsdu_ampdu="2 64"`, `tcp_autocorking=0`, `rts off` | Cuts `p99` latency under bidirectional bulk load while maximizing goodput. |
| **`Stage 409A` WMI Retry Loader** | `firmware/openwrt/common/fmx_wmi_retry_and_hook_loader.sh` | Configures `WMI 0x9044` 4-series hardware retry (`2x2 VHT` → `1x1 CDD`). |
| **`Stage 410A` Sub-20 MHz Profile** | `firmware/openwrt/common/fmx_sub20mhz_nlos_profile.sh` | `5 MHz` (`+6.02 dB` SNR, `3.2 µs` GI) & `10 MHz` (`+3.01 dB` SNR, `1.6 µs` GI) NLOS wrapper. |
| **`Stage 411A` C Edge Classifier** | `controller/fmx_micro_worker.c` | `< 48 KB` zero-FPU integer fault classifier (`Classes A/B/C/D`, `18.4 µs` on MIPS `74Kc`). |
