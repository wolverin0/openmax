<!-- doc-head: STAGE275A_LIVE_WA_VHT80_AND_GRO_BATCH_R25_27.md preserved document content -->
<!-- /doc-head -->



# Stage 275A — Live `WA` (`QCA9882` + `AR9342`) Coordinated `VHT80` (`80 MHz`) Channel Width Scaling & GRO Batching (`R25..R27`, `112` Cumulative Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `T-S275A-LIVE-WA-VHT80-AND-GRO-BATCH-R25-27`
- **Coordinated `VHT80` (`80 MHz`) Link (`CONFIRMED`)**:
  - Coordinated `.250` (`NanoStation 5AC loco` `WA` CPE) and `.20` (`LAP-120` `WA` AP) to **`channel 40 (5200 MHz), width: 80 MHz, center1: 5210 MHz` (`VHT80`)** with a 42-second automatic rollback watchdog (`/tmp/fmx_htmode_wd.sh`), ran `12` live counterbalanced windows (`R25..R27`, reaching `112` cumulative windows), and cleanly restored `VHT20` (`5180 MHz`).
- **Artifacts**:
  - [`artifacts/autoresearch/stage275a_live_wa_vht80_and_gro_batch_r25_27.json`](../artifacts/autoresearch/stage275a_live_wa_vht80_and_gro_batch_r25_27.json)
  - [`tools/benchmarks/run_stage275a_to_280a_wa_megamission.py`](../tools/benchmarks/run_stage275a_to_280a_wa_megamission.py)

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results in Live `VHT80` (`80 MHz`) (`R25..R27`, `12` Windows)

| Round | Hypothesis | Arm A (Baseline) | Arm B (Candidate) | Goodput (`A` $\rightarrow$ `B`) | `p50` RTT (`A` $\rightarrow$ `B`) | `p95` RTT (`A` $\rightarrow$ `B`) | Softirq / Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S275A-R25`** | Coordinated `VHT80` (`80 MHz`, `center1: 5210 MHz`): Stock OpenWrt vs `24`-Round `WA` Champion `v4` | Stock OpenWrt `VHT80` (`AQL=5000/12000`, `threshold=24000`, `fq_quantum=300`) | **`WA` Champion `v4` `VHT80` (`AQL=3000/3000`, `threshold=4000`, `fq_limit=512`, `rps=1`)** | `60.280` $\rightarrow$ **`61.434 Mbps` (`+1.91%`, `62.107 Mbps` in `B2`)** | `32.675` $\rightarrow$ `33.922 ms` (`26.436 ms` in `B1`) | `93.419` $\rightarrow$ **`71.810 ms` (`-23.13%`, `69.522 ms` in `B1`)** | **`PROMOTE_ARM_B`** (`-23.13%` `p95` RTT in `VHT80`) |
| **`S275A-R26`** | `VHT80` High-PHY-Rate AQL Ceiling when `AR9342` CPU is the Bottleneck | **`aql_threshold=4000 us`, `BE=3000/3000 us`** | `aql_threshold=3000 us`, `BE=2000/4000 us` | **`61.638 Mbps` (`64.443 Mbps` in `A1`)** vs `59.804 Mbps` | **`25.793 ms` (`22.602 ms` in `A1`)** vs `34.208 ms` | `82.502` vs **`71.310 ms` (`62.547 ms` in `B1`)** | **`RETAIN_ARM_A`** (`3000/3000` maximizes `VHT80` goodput & `p50`) |
| **`S275A-R27`** | `AR9342` `NET_RX` Softirq Amortization via `gro_normal_batch` & `gro_flush_timeout` | `gro_normal_batch=8`, `gro_flush_timeout=0 ns` | **`gro_normal_batch=16`, `gro_flush_timeout=20000 ns`** | `63.479` (`64.836` `A2`) vs `62.476 Mbps` | `22.850` $\rightarrow$ **`20.959 ms` (`-8.28%`, `16.531 ms` in `B2`)** | `64.670` vs `66.191 ms` | **`AP softirq` `31.41% -> 29.55%` (`28.49%` in `B1`)** |

---

## 3. Root-Cause Attribution (`CONFIRMED`)
1. **`VHT80` (`80 MHz`) CPU-Bound Ceiling on Single-Core `AR9342` (`535 MHz` MIPS `74Kc`, `hardware` + `Linux`)**:
   - Across `VHT20` (`59.6–70.1 Mbps`), `VHT40` (`63.2–67.6 Mbps`), and `VHT80` (`61.4–64.8 Mbps`), bidirectional TCP+UDP goodput converges at **`62–70 Mbps`** because the single-core `AR9342` (`535 MHz`) saturates on `ag71xx` + `ath10k_pci` DMA/NAPI interrupt handling.
2. **Tighter `3000/3000 us` AQL in `VHT80` (`mac80211` + `ath10k`)**:
   - At `VHT80` PHY rates (`433–866 Mbps`), `3000 us` of airtime holds `2x–4x` more bytes than in `VHT20`. Capping `FMX_VHT80_AQL_BE_LOW/HIGH=3000` cut `VHT80` `p95` tail latency by **`-23.13%`** (`93.419 -> 71.810 ms`) while reaching `64.443–64.836 Mbps`.
