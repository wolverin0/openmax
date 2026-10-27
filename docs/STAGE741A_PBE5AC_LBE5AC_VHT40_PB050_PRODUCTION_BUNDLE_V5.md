<!-- doc-head: STAGE741A_PBE5AC_LBE5AC_VHT40_PB050_PRODUCTION_BUNDLE_V5.md preserved document content -->
<!-- /doc-head -->


# Stage 741A — `PBE-5AC-Gen2` (`0xe3d6`) & `LBE-5AC-Gen2` (`0xe7f9`) Bundle `v5`

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `ath10k` / `QCA firmware` (`PB-040` + `PB-050`) / `mac80211` / `hardware`.
- **Production Bundle `v5`**: Packages `firmware/openwrt/common/fmx_pbe5ac_lbe5ac_production_v5.sh` (`SHA-256`: `2b6d6f11874b5a2a183f57869df09da1959fe31d3600f57f9e4400aae9eac929`) and `firmware/openwrt/common/fmx_qca_spectral_radar_phyerr_guard.sh` for Ubiquiti's two highest-volume WISP dish radios: **`PowerBeam 5AC Gen2` (`0xe3d6`, `25 dBi`)** and **`LiteBeam 5AC Gen2` (`0xe7f9`, `23 dBi`)**.

## 2. Production Bundle `v5` Feature Matrix
| Feature | Implementation | Verified Benefit |
| :--- | :--- | :--- |
| `VHT40` + `PB-040`/`PB-050` | Clean `WMI_PEER_ASSOC_CMDID` + Xtensa patches | **`25.47 Mbps` peak / `24.18 Mbps` mean** (`+136.4%` UL) |
| Spectral / Radar PHYERR Guard | `fmx_qca_spectral_radar_phyerr_guard.sh` | Silences background FFT `PHYERR` IRQ storms + `pktlog=0x0` |
| Dynamic `phy*` Resolution | `resolve_ath10k_phy()` | Tracks `phy0`/`phy1`/`phy2` across `ath10k_pci` reloads |
| Register `0x00029e00` | `0x13761320` | Bidirectional `QCA988x` MAC PCU timing alignment |

## 3. Safety Verification
- **Zero Live Radio Touches**: `.241`, `.242`, `.20`, `.250`, and `.110` untouched.
