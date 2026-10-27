<!-- doc-head: STAGE297A_CROSS_FLEET_CHAMPION_V42.md preserved document content -->
<!-- /doc-head -->


# Stage 297A — Cross-Fleet Mode B (`rc.poststart`) & Mode A (`OpenWrt 24.10.4`) Champion Matrix `v42.0`

## 1. Executive Summary
Stage 297A promotes the FuturaMAX Cross-Fleet Champion Matrix to **`v42.0`**, incorporating the Round-6 live counterbalanced benchmarks from **Stage 293A** (`.198` `XC` Memory Watermark, Conntrack & Bridge Fast-Path), **Stage 294A** (`.253` `2XC` 256 KB Socket Buffers & `24/48 us` Coalescing), **Stage 295A** (`192.168.1.20` `XM` 32 MB TCP Pacing & Bufferbloat Control), and the **Stage 296A** 6-Round (`24-Window` / `72` Cumulative Windows per radio) Scorecard.

## 2. Master Matrix `v42.0` Highlights
| Family | Mode | OS / Kernel | RAM | `v42.0` Validated Profile | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `WA` | **Mode A + B** | OpenWrt 24.10.4 / `WA.v8.7.25` | 64 MB | `ap_fq_quantum=3028`, `aql=4500`, `eth0_bql=4542/36288/600`, `mac80211_teb_4addr_v3_6.6.110.ko` | `CONFIRMED` |
| `XC` | **Mode B** | `XC.v8.7.25` (`.198`) | 128 MB | `min_free=4096`, `vfs=150`, `nf_conntrack_max=16384`, `bridge-nf-call-iptables=0`, `br0 forward_delay=0`, `txq=192`, `daprot=2` before `mcast=5` | `CONFIRMED` |
| `2XC` | **Mode B + DualBand** | `2XC.v8.7.11` (`.253`) | 128 MB | `rmem_max/wmem_max=262144`, `tcp_limit=65536`, `tso_div=8`, `coal=24/48 us`, `swr=3`, `ff_cap_rep=2`, `daprot=2` before `mcast=5` | `CONFIRMED` |
| `XW` | **Mode B** | `XW.v6.x` | 64 MB | `min_free=2048`, `txq=64`, `tcp_limit=65536`, `AMPDU=28/40960`, `ewma_delegate_on=1`, `AC*Minfree=0/16/32/48` | `CONFIRMED` |
| `XM` | **Mode B** | `XM.v6.1.12` (`192.168.1.20`) | 32 MB | `min_free=1536`, `tcp_limit=32768`, `tso_div=8`, `txq=48`, `backlog=512`, `dev_weight=32`, `AMPDU=28/40960`, `AC*Minfree=0/16/32/64` | `CONFIRMED` |
| `LTU` | **Mode B** | `AF-LTU v2.3.1` | 128 MB | `min_free=4096`, `eth0 txq=256`, `budget=300`, `backlog=1000`, `S102E` Tail-Guard Safe Mode | `CONFIRMED` |

## 3. Hard Safety Invariants (`CONFIRMED`)
- `touched_241_or_242 = False`
- `touched_20_or_250 = False`
- `touched_production_guarida = False`
- `flash_writes = 0`

## 4. Verification Artifacts
- Verifier: [`tools/verify/verify_stage297a_cross_fleet_champion_v42.py`](../tools/verify/verify_stage297a_cross_fleet_champion_v42.py)
- Receipt: [`artifacts/autoresearch/stage297a_cross_fleet_champion_v42_receipt.json`](../artifacts/autoresearch/stage297a_cross_fleet_champion_v42_receipt.json)
- Dedicated Pytest: [`tests/test_stage297a_cross_fleet_champion_v42.py`](../tests/test_stage297a_cross_fleet_champion_v42.py)
