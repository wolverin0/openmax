<!-- doc-head: Stage 469A Universal WA/XC/XW v10 SquashFS (hsqs) Bake (<220 lines) -->
`Stage 469A` empaqueta las `180` imágenes universales `WA/XC/XW v10` SquashFS (`hsqs`) integrando `fmx_xtensa_cca_agc_daemon.sh` (`Stage 445A`), el detector ToF `1.87m` (`Stage 446A`), el kit `PtP Champion v2` (`Stage 430A`) y `fmx_qca988x_spectral_nf_helper.sh` (`Stage 468A`).
<!-- /doc-head -->

# Stage 469A — Universal `WA/XC/XW v10` SquashFS (`hsqs`) Bake (`mm-953f`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-953f`, `id=155428`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v10`)**: [`99-fmx-wa-universal-champion-v10`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v10) (`sha256: 738b60d751991af25fb8307a62d71c6e5ed8796d3d4884e8ef5297a3a6a5516c`).

## 1. Integrated Ground-Up `v10` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 445A` CCA/AGC & Sub-20 Guard** | `firmware/openwrt/common/fmx_xtensa_cca_agc_daemon.sh` | Applies `PB040-CCA-AGC-OVERRIDE` (`+4 dB`) with hysteretic Sub-20 MHz guard. |
| **`Stage 446A` `1.87m` ToF Detector** | `artifacts/autoresearch/stage446a_hardware_tof_187m_thermal_fresnel_detector.json` | Separates thermal cable/clock drift from Fresnel multipath reflections at `80 MHz` (`12.5 ns`). |
| **`Stage 430A` PtP Champion `v2`** | `artifacts/autoresearch/stage430a_pbe5ac_lbe5ac_ptp_champion_v2_kit.json` | `PBE-5AC-Gen2` (`0xe3d6`) & `LBE-5AC-Gen2` (`0xe7f9`) PtP WDS + `gro_normal_batch=16`. |
| **`Stage 468A` Spectral FFT & NF Helper** | `firmware/openwrt/common/fmx_qca988x_spectral_nf_helper.sh` | Hitless 64-bin background FFT (`WMI 0x905b/0x905c`) + Noise Floor survey dump. |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
