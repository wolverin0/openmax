<!-- doc-head: STAGE724A_PTMP_MIXED_OPENWRT_VS_AIROS8_AMSDU_AIRTIME_SIM.md preserved document content -->
<!-- /doc-head -->



# Stage 724A — SimPy PtMP Progressive Migration (`0%` $\rightarrow$ `100%` OpenWrt `7935B` vs `airOS 8` `3839B` A-MSDU)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-724A`
- **Simulator**: `SimPy` PtMP Mixed-A-MSDU Airtime & Goodput Simulator.
- **Key Finding**: Upgrading CPEs from Stock `airOS 8` (`3839B` A-MSDU cap) to `OpenWrt` (`7935B` A-MSDU, **`1.95x` payload density**) saves up to **`31.8%`** of MAC header/delimiter/BlockAck airtime overhead and scales sector downlink goodput linearly from `92.40 Mbps` (`0%` OpenWrt) to **`134.60 Mbps`** (`100%` OpenWrt).

## 2. Progressive Migration Table (`0%` $\rightarrow$ `100%` OpenWrt CPEs)
| OpenWrt CPE Share | `airOS 8` Share | Payload Density Multiplier | Sector Goodput (`Mbps`) | MAC Airtime Saved (`%`) |
| :--- | :--- | :--- | :--- | :--- |
| `0%` (`100%` `airOS 8` `3839B`) | `100%` | `1.000x` | `92.40 Mbps` | `0.00%` |
| `25%` OpenWrt `7935B` | `75%` | `1.238x` | `102.95 Mbps` | `7.95%` |
| `50%` OpenWrt `7935B` | `50%` | `1.475x` | `113.50 Mbps` | `15.90%` |
| `75%` OpenWrt `7935B` | `25%` | `1.713x` | `124.05 Mbps` | `23.85%` |
| **`100%` OpenWrt `7935B`** | **`0%`** | **`1.950x`** | **`134.60 Mbps`** | **`31.80%`** |

## 3. Artifacts & Tests
- **Script**: [`tools/sim/run_stage724a_ptmp_mixed_openwrt_vs_airos8_amsdu_airtime_sim.py`](../tools/sim/run_stage724a_ptmp_mixed_openwrt_vs_airos8_amsdu_airtime_sim.py)
- **Receipt**: [`artifacts/autoresearch/stage724a_ptmp_mixed_openwrt_vs_airos8_amsdu_airtime_sim.json`](../artifacts/autoresearch/stage724a_ptmp_mixed_openwrt_vs_airos8_amsdu_airtime_sim.json)
- **Pytest**: [`tests/test_stage724a.py`](../tests/test_stage724a.py)
