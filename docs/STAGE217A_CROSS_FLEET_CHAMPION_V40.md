<!-- doc-head: STAGE217A_CROSS_FLEET_CHAMPION_V40.md preserved document content -->
<!-- /doc-head -->


# Stage 217A — Cross-Fleet Mode B (`rc.poststart v39`) & Mode A (`OpenWrt 24.10.4`) Champion Matrix `v40.0`

## 1. Executive Summary
Stage 217A consolidates the Round-4 live stability, memory/softirq, and 32 MB OOM-immunity proofs from **Stage 215A** (`XC` `.198` + `2XC` `.253`) and **Stage 216A** (`XM` `192.168.1.20`) with **Stage 202A** (`Mode B rc.poststart v39`) and **Mode A** (`OpenWrt 24.10.4` `99-fmx-wa-universal-champion` + `mac80211_teb_4addr_v3_6.6.110.ko`) into **Master Curation `v40.0`**.

## 2. Unified Cross-Fleet Champion Matrix (`v40.0`)
| Family | Mode | OS / Kernel | RAM | Key Validated Knobs & Guarantees | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `WA` | **Mode A** (`OpenWrt`) | OpenWrt 24.10.4 (`6.6.110`) | 64 MB | `ap_fq_quantum=3028`, `aql_threshold=4500`, `eth0_bql=4542/36288/600`, `mac80211_teb_4addr_v3_6.6.110.ko` (`13/13` bridges) | `CONFIRMED` |
| `WA` | **Mode B** (`airOS 8`) | `WA.v8.7.x` (`2.6.32.68`) | 64 MB | `min_free=2048`, `txq=192`, `budget=480`, `daprot=2` before `mcast=5`, `swr=3`, `ff_cap_rep=2` | `CONFIRMED` |
| `XC` | **Mode B** (`airOS 8`) | `XC.v8.7.25` (`2.6.32.68`) | 128 MB | `min_free=4096`, `txq=192`, `budget=480`, `coal=24/48 us`, `tso_div=8`, `daprot=2` before `mcast=5` (`MemFree ~85 MB` stable) | `CONFIRMED` |
| `2XC` | **Mode B** (`airOS 8`) | `2XC.v8.7.11` (`2.6.32.68`) | 128 MB | `min_free=4096`, `txq=192`, `budget=480`, `coal=24/48 us`, `tso_div=8`, `daprot=2` before `mcast=5` (`MemFree ~88 MB` stable) | `CONFIRMED` |
| `XW` | **Mode B** (`airOS 6`) | `XW.v6.x` (`2.6.32.71`) | 64 MB | `min_free=2048`, `txq=64`, `tcp_limit=65536`, `AMPDU=28/40960`, `ewma_delegate_on=1`, `AC*Minfree=0/16/32/48` | `CONFIRMED` |
| `XM` | **Mode B** (`airOS 6`) | `XM.v6.1.12` (`2.6.32.x`) | 32 MB | `min_free=1536`, `txq=48`, `tcp_limit=32768`, `rmem<=128K`, `wmem<=64K`, `backlog=512`, `ACBKMinfree=64` (`0` OOM) | `CONFIRMED` |
| `LTU` | **Mode B** (`LTU Safe`) | `AF-LTU v2.3.1` | 128 MB | `min_free=4096`, `eth0 txq=256`, `budget=300`, `backlog=1000`, `S102E` Tail-Guard Safe Mode | `CONFIRMED` |

## 3. Hard Safety Invariants (`CONFIRMED`)
- `touched_241_or_242 = False`
- `touched_20_or_250 = False`
- `touched_production_guarida = False` (`3` panels / `32` CPEs preserved)
- `flash_writes = 0`

## 4. Verification Artifacts
- Verifier: [`tools/verify/verify_stage217a_cross_fleet_champion_v40.py`](../tools/verify/verify_stage217a_cross_fleet_champion_v40.py)
- Receipt: [`artifacts/autoresearch/stage217a_cross_fleet_champion_v40_receipt.json`](../artifacts/autoresearch/stage217a_cross_fleet_champion_v40_receipt.json)
- Suite: [`tests/test_stage215a_to_217a_multi_radio_v40.py`](../tests/test_stage215a_to_217a_multi_radio_v40.py)
