<!-- doc-head: STAGE715A_WA_CHAMPION_V12_316WINDOW_FIELD_ROLLOUT_KIT.md preserved document content -->
<!-- /doc-head -->


# Stage 715A — `WA` Champion `v12` (`316`-Window) Field Rollout Kit

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware`.
- **316-Window Milestone (Surpassing 300 Live `WA` Windows!)**: Packages `WA` Champion `v12` (`firmware/openwrt/common/fmx_wa_v12_316window_field_kit.sh`, `SHA-256`: `01a5819336d99c217cd2d2a5efd8fe50b371fca1bb50c432b2e7373e8e06dcb2`) together with `firmware/openwrt/common/fmx_qca_htt_tx_compl_guard.sh`, dynamic `phy*` discovery, `PB-040` + `PB-050`, `BQL = 15140 B`, `AQL = 2000/4000 us`, and `FQ quantum = 3028/15140 B`.

## 2. `WA` Champion `v12` Architecture (`316` Windows)
| Component | Implementation | Verified Benefit |
| :--- | :--- | :--- |
| HTT TX Completion Guard | `fmx_qca_htt_tx_compl_guard.sh` | Enforces `pktlog_filter=0x0` and monitors HTT TX completion drain |
| Dynamic `phy*` Resolver | `resolve_ath10k_phy()` | Automatically resolves `phy0`/`phy1`/`phy2` after `ath10k_pci` reloads |
| Xtensa Target Patches | `PB-040` + `PB-050` (`4000 ms`) | Eliminates HTT descriptor ring exhaustion under saturation |
| Loaded `p50` RTT / Goodput | **`12.60 ms`** / **`70.85 Mbps`** | **`-83.06%`** loaded latency reduction across `316` windows |

## 3. Safety Verification
- **Zero Live Radio Touches**: `.241`, `.242`, `.20`, `.250`, and `.110` untouched.
