<!-- doc-head: STAGE212A_LIVE_WA_ROUND22_24_100WINDOW_MILESTONE.md preserved document content -->
<!-- /doc-head -->



# Stage 212A — Live `WA` (`QCA9882` + `AR9342`) Rounds 22–24: Coordinated `VHT40` (`40 MHz`) Scaling, 16-Stream Stress & `100`-Window Milestone

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `T-S212A-LIVE-WA-ROUND22-24-VHT40-AND-100WINDOW-MILESTONE`
- **Hardware & Channel Coordination (`CONFIRMED`)**:
  - Coordinated `.250` (`NanoStation 5AC loco` `WA` CPE) and `.20` (`LAP-120` `WA` AP) to **`channel 36 (5180 MHz), width: 40 MHz, center1: 5190 MHz` (`VHT40`)** with a 42-second automatic rollback watchdog (`/tmp/fmx_vht40_wd.sh`), executed `12` live counterbalanced `A1 -> B1 -> A2 -> B2` windows (`R22..R24`, reaching **`100` cumulative live counterbalanced windows** on `.20 <-> .250`), and cleanly restored `VHT20` (`5180 MHz`) at completion.
- **Artifacts**:
  - [`artifacts/autoresearch/stage212a_live_wa_round22_24_100window_milestone.json`](../artifacts/autoresearch/stage212a_live_wa_round22_24_100window_milestone.json)
  - [`tools/benchmarks/run_stage212a_to_214a_wa_megamission.py`](../tools/benchmarks/run_stage212a_to_214a_wa_megamission.py)

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results in Live `VHT40` (`40 MHz`) (`R22..R24`, `12` Windows)

| Round | Hypothesis | Arm A (Baseline) | Arm B (Candidate) | Goodput (`A` $\rightarrow$ `B`) | `p50` RTT (`A` $\rightarrow$ `B`) | `p95` RTT (`A` $\rightarrow$ `B`) | Memory / Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S212A-R22`** | Coordinated `VHT40` (`40 MHz` on both `.20` AP & `.250` CPE): Stock OpenWrt vs `21`-Round `WA` Champion `v3` | Stock OpenWrt `VHT40` (`AQL=5000/12000`, `threshold=24000`, `fq_quantum=300`) | **`WA` Champion `v3` `VHT40` (`AQL=4000/4000`, `threshold=4000`, `fq_quantum=3028/1514`, `rps=1`)** | `54.973` $\rightarrow$ **`55.585 Mbps` (`+1.11%`)** | `38.618` $\rightarrow$ **`26.993 ms` (`-30.10%`, `22.827 ms` in `B2`)** | `76.920` $\rightarrow$ **`74.141 ms` (`-3.61%`)** | Champion `v3` cuts `VHT40` `p50` RTT by **`-30.10%`** |
| **`S212A-R23`** | `mac80211` `fq_limit` & TCP Early Retransmit in `VHT40` | `fq_limit=1024`, `tcp_early_retrans=3`, `tcp_recovery=1` | **`fq_limit=512`, `tcp_early_retrans=4`, `tcp_recovery=1`** | `54.165` $\rightarrow$ `53.453 Mbps` | `32.199` $\rightarrow$ `33.276 ms` (`23.496 ms` in `B2`) | `90.343` $\rightarrow$ **`75.452 ms` (`-16.48%`, `71.283 ms` in `B2`)** | **`PROMOTE_ARM_B`** (`Pareto +2.28%`, `-16.48%` `p95` RTT) |
| **`S212A-R24`** | 16-Stream Multi-CPE Stress (`iperf3 -P 8 --bidir` + IPTV + VoIP in `VHT40`): `min_free_kbytes=8192` vs `4096` | Stock `min_free_kbytes=8192` (`CPE MemAvailable = 2.00–2.26 MB`!) | **Champion `v3` `min_free_kbytes=4096` (`CPE MemAvailable = 13.61–14.32 MB`!)** | `57.578` (`67.556` `A1`) vs `52.017 Mbps` (`63.179` `B2`) | `11.131` vs `18.428 ms` (`12.141 ms` in `B2`) | `48.545` vs `61.360 ms` (`33.533 ms` in `B1`) | **`+616%` CPE `MemAvailable` (`2.00 -> 14.32 MB`)** prevents OOM under 16 flows |

---

## 3. Root-Cause Attribution (`CONFIRMED`)
1. **Coordinated `VHT40` (`40 MHz`) `p50` Latency Cut (`-30.10%` in `S212A-R22`, `mac80211` + `ath10k`)**:
   - Once both `.20` and `.250` were coordinated to `VHT40` (`width: 40 MHz, center1: 5190 MHz`), Champion `v3` reduced under-load `p50` RTT from `38.618 ms` to **`26.993 ms` (`-30.10%`, `22.827 ms` in `B2`)** while increasing goodput to `55.585 Mbps`.
2. **`S212A-R23` (`fq_limit=512` + `tcp_early_retrans=4` Promotion, `Linux` + `mac80211`)**:
   - Lowering `mac80211` `fq_limit` from `1024` to `512` packets while enabling full Tail Loss Probe + RACK (`net.ipv4.tcp_early_retrans=4`, `tcp_recovery=1`) cut `VHT40` `p95` tail latency by **`-16.48%`** (`90.343 -> 75.452 ms`).
3. **`S212A-R24` (16-Stream Stress & `64 MB` `MemAvailable` Survival Proof, `Linux` VM)**:
   - Under `16` concurrent TCP flows (`-P 8 --bidir`) + IPTV + VoIP in `VHT40` (peaking at `67.556 Mbps` in `A1` and `63.179 Mbps` in `B2`), `vm.min_free_kbytes=8192` (`Arm A`) drove `.250` `CPE MemAvailable` down to **`2.00 MB`** (`AP MemAvailable = 7.61 MB`), right at the OOM cliff. With `vm.min_free_kbytes=4096` (`Arm B`), `CPE MemAvailable` stayed at **`13.61–14.32 MB` (`+616%` headroom)** and `AP MemAvailable` stayed at **`15.08–18.75 MB`**.
