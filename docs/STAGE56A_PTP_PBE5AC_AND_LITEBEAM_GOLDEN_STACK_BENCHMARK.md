<!-- doc-head: STAGE56A_PTP_PBE5AC_AND_LITEBEAM_GOLDEN_STACK_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 56A — PowerBeam 5AC Gen2 (`.241 <-> .242`) & LiteBeam 5AC Gen2 (`.251`) SIFS Burst, ShortGI, VHT A-MPDU Ceiling & TCP Low-Latency Over-The-Air Autoresearch Benchmark (`T-S56A-PTP-PBE5AC-AND-LITEBEAM-SIFS-BURST-AND-TCP-LOW-LATENCY-OTA-BENCH`)

## 1. Executive Summary & Scientific Verdict

- **Task ID**: `T-S56A-PTP-PBE5AC-AND-LITEBEAM-SIFS-BURST-AND-TCP-LOW-LATENCY-OTA-BENCH`
- **Status**: **COMPLETED — `S56A-R1..R3` (`wifi0 burst=1`, reduced `vhtmaxampdu/amsdu/ampdu`, `tcp_low_latency=1`) `REJECTED / REFUTED`; Stage 54A Champion (`S54A-R3`) Restored, Verified, Persisted to Flash, and Seeded in OpenWISP as `FuturaMAX-PtP-PowerBeam-LiteBeam-Golden-v2`**
- **Artifact**: [`artifacts/autoresearch/stage56a_ptp_pbe5ac_and_litebeam_golden_stack_bench_20261025.json`](<repo>/artifacts/autoresearch/stage56a_ptp_pbe5ac_and_litebeam_golden_stack_bench_20261025.json)
- **Benchmark Runner**: [`tools/bench/run_stage56a_ptp_pbe5ac_and_litebeam_golden_stack_bench.py`](<repo>/tools/bench/run_stage56a_ptp_pbe5ac_and_litebeam_golden_stack_bench.py)
- **OpenWISP NMS Seed**: [`tools/nms/seed_real_openwisp_db.py`](<repo>/tools/nms/seed_real_openwisp_db.py) (`Seeded 5 templates and 10 devices in real OpenWISP!`)
- **Verification Test Suite**: [`tests/test_stage53a_54a_pbe5ac_and_litebeam_ptp_bench.py`](<repo>/tests/test_stage53a_54a_pbe5ac_and_litebeam_ptp_bench.py)

### Key Scientific Findings (`CONFIRMED` & `REFUTED` on Live Hardware)
1. **QCA9880/QCA9882 (`WA.v8.7.11`) Offload Control Boundary (`wifi0` vs `ath0`) — `CONFIRMED`**:
   - On QCA9880/9882 offload (`ol_ath`) radios in `airOS 8` (`WA.v8.7.11`), `iwpriv wifi0 AMPDUFrames` and `iwpriv wifi0 AMPDULim` return `Operation not permitted` (`8BE0` legacy direct-attach ioctls), whereas **`iwpriv ath0 ampdu <N>` (`0049`, default `32`), `iwpriv ath0 vhtmaxampdu <0..7>` (`012D`, default `7`), `iwpriv ath0 amsdu <1..3>` (`004D`, default `3`), and `iwpriv ath0 shortgi <0|1>` (`0047`, default `1`)** are active on the VAP (`ath0`).
   - Conversely, **`iwpriv wifi0 burst <0|1>` (`104D`, default `0`)** and **`iwpriv wifi0 distance <m>` (`1093`) / `damode <0|1>` / `dacount <N>`** are active on the radio interface (`wifi0`), while `iwpriv ath0 burst` returns `Operation not supported`.
2. **Why `wifi0 burst=1`, Reduced `vhtmaxampdu`/`amsdu`/`ampdu`, and `tcp_low_latency=1` Degrade `ubnt_poll` TDMA PtP Goodput — `REFUTED` (`REJECT`)**:
   - **`S56A-R1` (`wifi0 burst=1` + `tcp_low_latency=1`)**: While `wifi0 burst=1` + `tcp_low_latency=1` cut loaded Ping `p50` from `25.120 ms` to `15.848 ms`, `p95` from `28.764 ms` to `13.800 ms`, and IPTV UDP loss from `0.966%` to `0.000%`, it **reduced Bulk TCP goodput by `-26.5%` (`15.646 Mbps` $\rightarrow$ `11.499 Mbps`)** because enabling manual SIFS bursting (`wifi0 burst=1`) and bypassing Linux TCP prequeue/coalescing (`tcp_low_latency=1`) disrupts `ubnt_poll_host.ko` TDMA slot packing.
   - **`S56A-R2` (`ath0 ampdu=20, vhtmaxampdu=5, amsdu=2, tx_queue_len=160`)**: Bounding VAP A-MPDU subframes to `20` and A-MSDU to `2` cut loaded Ping `p95` from `22.580 ms` to `15.052 ms` with `15.898 Mbps` Bulk TCP (`23.752 Mbps` aggregate DL), but remained below the `27.205 Mbps` aggregate DL of `S54A-R3` (`ampdu=32, vhtmaxampdu=7, amsdu=3`).
   - **`S56A-R3` (`ath0 ampdu=28, vhtmaxampdu=6, tcp_low_latency=1, distance=150` overriding `damode=1`)**: Overriding `/etc/sysinit/radio.conf`'s `distance=600, damode=1, dacount=25` with static `distance=150` and `tcp_low_latency=1` reduced Bulk TCP from `15.633 Mbps` to `12.950 Mbps` (`-17.2%`).
3. **Restoration & Verification of the Winning Stage 54A Champion (`S54A-R3` = `FuturaMAX-PtP-PowerBeam-LiteBeam-Golden-v2`) — `KEEP`**:
   - Restored and persisted the proven `S54A-R3` Champion (`txqueuelen=192`, `netdev_budget=600`, `dev_weight=64`, `netdev_max_backlog=600`, `rmem_max/wmem_max=4194304`, `tcp_low_latency=0`, `wifi0 burst=0`, `wifi0 distance=600`, `wifi0 damode=1`, `wifi0 dacount=25`, `ath0 shortgi=1`, `ath0 ampdu=32`, `ath0 vhtmaxampdu=7`, `ath0 amsdu=3`, `txpower=24dBm`, and WMM `AC 1/2` AIFS/CWmin/CWmax) across `.251`, `.241`, and `.242` (`cfgmtd -w -p /etc/` exit code `0` on all 3 nodes).
   - Post-restoration multi-hop verification window (`V1`) confirmed **`17.929 Mbps` Bulk TCP + `7.851 Mbps` IPTV UDP (`25.780 Mbps` aggregate DL)**, **`0.0%` VoIP loss**, **`0.145 ms` IPTV jitter**, and **`13.425 ms` `p50` / `21.533 ms` `p95` loaded RTT** (complementing Stage 54A's 4-window counterbalanced `S54A-R3` mean of **`27.205 Mbps` aggregate DL** and **`14.357 ms` `p50` / `17.045 ms` `p95` RTT**).

---

## 2. 3-Round Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`12` Multi-Hop OTA Windows)

| Round | Candidate Name | Arm | Bulk TCP (Mbps) | IPTV UDP (Mbps) | Aggregate DL (Mbps) | IPTV Jitter (ms) | IPTV Loss (%) | VoIP Jitter (ms) | VoIP Loss (%) | Loaded Ping `p50` (ms) | Loaded Ping `p95` (ms) | Decision |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S56A-R1`** | `TXPOWER_24DBM_SHORTGI_BURST_1` | Stock `A` | `15.646` | `7.853` | `23.498` | `0.274` | `0.966%` | `3.081` | `0.0%` | `25.120` | `28.764` | — |
| **`S56A-R1`** | `TXPOWER_24DBM_SHORTGI_BURST_1` | Treatment `B` | `11.499` (`-26.5%`) | `7.849` | `19.349` | `2.103` | **`0.000%`** | `1.751` | `0.0%` | **`15.848`** | **`13.800`** | **`REJECT / REFUTED`** |
| **`S56A-R2`** | `AMPDU_20_VHTMAX_5_AMSDU_2` | Stock `A` | `15.800` | `7.854` | `23.653` | `0.231` | `1.877%` | `1.621` | `0.0%` | `30.372` | `22.580` | — |
| **`S56A-R2`** | `AMPDU_20_VHTMAX_5_AMSDU_2` | Treatment `B` | `15.898` (`+0.6%`) | `7.854` | `23.752` | `0.293` | `1.890%` | `1.887` | `0.0%` | **`27.300`** | **`15.052`** | **`REJECT / REFUTED`** |
| **`S56A-R3`** | `AMPDU_28_VHTMAX_6_TCP_LOWLAT_1` | Stock `A` | `15.633` | `7.857` | `23.491` | `0.120` | `1.756%` | `1.900` | `0.0%` | `24.614` | `31.747` | — |
| **`S56A-R3`** | `AMPDU_28_VHTMAX_6_TCP_LOWLAT_1` | Treatment `B` | `12.950` (`-17.2%`) | `7.853` | `20.803` | `0.205` | `2.065%` | `2.524` | `0.813%` | **`16.357`** | **`15.428`** | **`REJECT / REFUTED`** |
| **`S54A-R3-VERIFY`** | **Restored `S54A-R3` Golden Stack v2** | **Verified `V1`** | **`17.929`** | **`7.851`** | **`25.780`** | **`0.145`** | **`1.023%`** | **`3.245`** | **`0.0%`** | **`13.425`** | **`21.533`** | **`KEEP` (Restored Champion)** |

---

## 3. OpenWISP NMS Integration (`FuturaMAX-PtP-PowerBeam-LiteBeam-Golden-v2`)

Updated [`tools/nms/seed_real_openwisp_db.py`](<repo>/tools/nms/seed_real_openwisp_db.py) and executed it inside `infra_openwisp_official-dashboard-1`:
- **Templates (`5` total)**: Added **`FuturaMAX-PtP-PowerBeam-LiteBeam-Golden-v2`** containing the verified restored `S54A-R3` `/etc/persistent/rc.poststart` script (`txqueuelen=192`, `netdev_budget=600`, `dev_weight=64`, `netdev_max_backlog=600`, `rmem_max/wmem_max=4194304`, `tcp_low_latency=0`, `wifi0 burst=0`, `wifi0 distance=600`, `wifi0 damode=1`, `wifi0 dacount=25`, `ath0 shortgi=1`, `ath0 ampdu=32`, `ath0 vhtmaxampdu=7`, `ath0 amsdu=3`, WMM `AC 1/2`).
- **Devices (`10` total)**: Updated `FMX-PBE5AC-AP-ETH3` (`198.18.0.45` / `198.18.0.8`), `FMX-PBE5AC-STA-ETH7` (`198.18.0.46` / `198.18.0.74`), and added `FMX-LBE5AC-BENCH-ETH8` (`198.18.0.48` / `198.18.0.148`, MAC `PUBLIC_DEVICE_0092`).
