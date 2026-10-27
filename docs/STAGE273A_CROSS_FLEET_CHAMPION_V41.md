<!-- doc-head: STAGE273A_CROSS_FLEET_CHAMPION_V41.md preserved document content -->
<!-- /doc-head -->


# Stage 273A — Cross-Fleet Mode B (`rc.poststart`) & Mode A (`OpenWrt 24.10.4`) Champion Matrix `v41.0`

## 1. Executive Summary
Stage 273A updates the FuturaMAX Cross-Fleet Champion Matrix to **`v41.0`**, integrating the Round-5 live counterbalanced benchmarks from **Stage 269A** (`.198` `XC`), **Stage 270A** (`.253` `2XC` 2.4 GHz), and **Stage 271A** (`192.168.1.20` `XM` 32 MB RAM) along with the **Stage 272A** SimPy + Pymoo NSGA-II 2.4 GHz / 5 GHz Dual-Band NLOS Failover & Band-Steering policy.

## 2. Master Matrix `v41.0` Highlights
| Family | Mode | OS / Kernel | RAM | Round-5 / `v41.0` Validated Profile | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `WA` | **Mode A + B** | OpenWrt 24.10.4 / `WA.v8.7.25` | 64 MB | `ap_fq_quantum=3028`, `aql=4500`, `eth0_bql=4542/36288/600`, `mac80211_teb_4addr_v3_6.6.110.ko` | `CONFIRMED` |
| `XC` | **Mode B** | `XC.v8.7.25` (`.198`) | 128 MB | `netdev_budget=480`, `dev_weight=48`, `tx_queue_len=192`, `tcp_limit=65536`, `coal=24/48 us`, `daprot=2` before `mcast=5` | `CONFIRMED` |
| `2XC` | **Mode B + DualBand** | `2XC.v8.7.11` (`.253`) | 128 MB | `swr_limit=3`, `ff_cap_rep=2`, `cms/voip_bias=6`, `daprot=2` before `mcast=5` + NLOS steering (`RSSI <= -73.25 dBm`, `retry >= 14.02%`, `holddown = 34.83s`, `2.4GHz floor = 30.69%`) | `CONFIRMED` |
| `XW` | **Mode B** | `XW.v6.x` | 64 MB | `min_free=2048`, `txq=64`, `tcp_limit=65536`, `AMPDU=28/40960`, `ewma_delegate_on=1`, `AC*Minfree=0/16/32/48` | `CONFIRMED` |
| `XM` | **Mode B** | `XM.v6.1.12` (`192.168.1.20`) | 32 MB | `min_free=1536`, `AMPDU=28/40960`, `AC*Minfree=0/16/32/64`, `txq=48`, `ewma_delegate_on=1`, `cwmin_be=3/cwmax_be=6` | `CONFIRMED` |
| `LTU` | **Mode B** | `AF-LTU v2.3.1` | 128 MB | `min_free=4096`, `eth0 txq=256`, `budget=300`, `backlog=1000`, `S102E` Tail-Guard Safe Mode | `CONFIRMED` |

## 3. Hard Safety Invariants (`CONFIRMED`)
- `touched_241_or_242 = False`
- `touched_20_or_250 = False`
- `touched_production_guarida = False`
- `flash_writes = 0`

## 4. Verification Artifacts
- Verifier: [`tools/verify/verify_stage273a_cross_fleet_champion_v41.py`](../tools/verify/verify_stage273a_cross_fleet_champion_v41.py)
- Receipt: [`artifacts/autoresearch/stage273a_cross_fleet_champion_v41_receipt.json`](../artifacts/autoresearch/stage273a_cross_fleet_champion_v41_receipt.json)
- Dedicated Pytest: [`tests/test_stage273a_cross_fleet_champion_v41.py`](../tests/test_stage273a_cross_fleet_champion_v41.py)
