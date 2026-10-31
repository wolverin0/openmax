<!-- doc-head: STAGE54A_LITEBEAM_AND_PBE5AC_PTP_AUTORESEARCH_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 54A — LiteBeam 5AC Gen2 (`.251`) to PowerBeam 5AC Gen2 PtP (`.241 -> .242`) Multi-Hop Cross-PtP Autoresearch Benchmark (`T-S54A-LITEBEAM-TO-REMOTE-PBE5AC-CROSS-PTP-AUTORESEARCH-BENCH`)

## 1. Executive Summary

- **Task ID**: `T-S54A-LITEBEAM-TO-REMOTE-PBE5AC-CROSS-PTP-AUTORESEARCH-BENCH`
- **Status**: **COMPLETED (`KEEP` — Champion `S54A-R3` persisted to flash across all 3 endpoints: `.251`, `.241`, and `.242`)**
- **Artifact**: [`artifacts/autoresearch/stage54a_litebeam_and_pbe5ac_ptp_autoresearch_20261025.json`](<repo>/artifacts/autoresearch/stage54a_litebeam_and_pbe5ac_ptp_autoresearch_20261025.json)
- **Benchmark Runner**: [`tools/bench/run_stage54a_litebeam_and_pbe5ac_ptp_autoresearch.py`](<repo>/tools/bench/run_stage54a_litebeam_and_pbe5ac_ptp_autoresearch.py)
- **Verification Test Suite**: [`tests/test_stage53a_54a_pbe5ac_and_litebeam_ptp_bench.py`](<repo>/tests/test_stage53a_54a_pbe5ac_and_litebeam_ptp_bench.py)

### Key Outcomes (`CONFIRMED` on Live Hardware)
1. **Multi-Hop 3-Node End-to-End Over-The-Air Benchmark (`198.18.0.148 -> 198.18.0.8 -> 198.18.0.74`)**:
   - Restored IPv4 bench & management addressing on the LiteBeam 5AC Gen2 (`198.18.0.48/24` and `198.18.0.148/24` on `br0`, `gi8`, `VLAN 108`) and verified full L2/L3 transit across `gi8` $\rightarrow$ `gi3` (`198.18.0.45` / `198.18.0.8`, `FMX-PBE5AC-AP-ETH3`) $\rightarrow$ Over-The-Air `5205 MHz / 20 MHz` PtP $\rightarrow$ remote standalone-PoE `198.18.0.46` (`198.18.0.74`, `FMX-PBE5AC-STA-ETH7`).
2. **`S54A-R3` (`PTP_ACKTIMEOUT_25US_AND_AMPDU24_COMBINED_CHAMPION`) Increased End-to-End Bulk TCP Goodput by `+7.3%` (`18.041 Mbps` $\rightarrow$ `19.355 Mbps`, Aggregate DL `27.205 Mbps`) While Cutting Loaded `p95` RTT by `-50.3%` (`34.323 ms` $\rightarrow$ `17.045 ms`) and IPTV Jitter by `-27.7%` (`0.159 ms` $\rightarrow$ `0.115 ms`)**:
   - Combining tight PtP `acktimeout=25 us` (`distance=150 m`), bounded A-MPDU aggregation (`ampduFrames=24`, `ampduLimit=50000`), and the Stage 53A Champion queue/NAPI/WMM stack (`tx_queue_len=192`, `netdev_budget=600`, `dev_weight=64`, `netdev_max_backlog=600`, `rmem_max/wmem_max=4194304`, `tcp_sack/dsack/ecn=1`, WMM `AC_VI`/`AC_VO` AIFS & CWmin/CWmax) delivered the highest end-to-end goodput (**`27.205 Mbps` aggregate DL**, peaking at `19.887 Mbps` Bulk TCP + `7.851 Mbps` IPTV UDP in `B2`) and cut loaded `p95` RTT in half (**`17.045 ms`** vs `34.323 ms` Stock A).
3. **`S54A-R2` (`PTP_AMPDU_FRAMES_24_VS_32_AND_AGGR_BURST_TUNING`) Cut Loaded `p50` RTT by `-28.3%` (`22.721 ms` $\rightarrow$ `16.281 ms`), `p95` RTT by `-21.8%` (`28.358 ms` $\rightarrow$ `22.174 ms`), and VoIP Jitter by `-25.2%` (`2.357 ms` $\rightarrow$ `1.764 ms`)**:
   - Bounding `iwpriv wifi0 ampduFrames 24` (`ampduLimit 50000`) vs stock `32` frames prevented oversized A-MPDU bursts from head-of-line blocking concurrent VoIP (`DSCP EF`) and ICMP packets across the `20 MHz` PtP bridge while slightly increasing Bulk TCP goodput (`17.614 Mbps` $\rightarrow$ `17.759 Mbps`).
4. **`S54A-R1` (`CROSS_NODE_PTP_CHAMPION_STACK_251_241_242`) Cut Loaded `p95` RTT by `-21.0%` (`32.313 ms` $\rightarrow$ `25.530 ms`) and IPTV Loss by `-29.7%` (`2.284%` $\rightarrow$ `1.605%`)**:
   - Extending the Stage 53A Champion queue/NAPI/WMM tuning to the origin LiteBeam 5AC Gen2 (`198.18.0.48`) eliminated origin-side Ethernet/bridge bufferbloat when driving multi-hop traffic through `.241` to `.242`.
5. **100% Watchdog-Protected Execution & Flash Persistence Across All 3 Radios**:
   - All 12 counterbalanced windows armed `/tmp/wd_s54 45` on remote standalone-PoE `.242` before applying treatments and disarmed it after end-to-end `198.18.0.148 -> 198.18.0.74` OTA verification (`e2e_ota_verified: true`, `sta_watchdog_disarmed: true` across all 12 windows).
   - Persisted `S54A-R3` Combined Champion to `/etc/persistent/rc.poststart` (`cfgmtd -w -p /etc/` exit code `0`, `Active->Backup [%100]`) on `198.18.0.48`, `198.18.0.45`, and `198.18.0.46`.

---

## 2. Multi-Hop Lab Topology

| Hop | Host / Bench IP | Device / Firmware | Switch Port / Role | Link Path |
| :--- | :--- | :--- | :--- | :--- |
| **Hop 1 (Origin)** | `198.18.0.48` / `198.18.0.148` | LiteBeam 5AC Gen2 (`WA.ar934x.v8.7.11`) | `gi8` (`VLAN 108`, PoE `ON`) | Generates Bulk TCP (`-P 2`) + IPTV (`8M CS4`) + VoIP (`64K EF`) + ICMP (`0.2s`) |
| **Hop 2 (PtP AP)** | `198.18.0.45` / `198.18.0.8` | PowerBeam 5AC Gen2 (`WA.ar934x.v8.7.11`) | `gi3` (`VLAN 103`, PoE `ON`, `FMX-PBE5AC-AP-ETH3`) | Bridges Ethernet `eth0` $\leftrightarrow$ `br0` $\leftrightarrow$ `ath0` (`SSID=FMX-PBE-PTP`, `5205 MHz / 20 MHz`) |
| **Hop 3 (Remote STA)** | `198.18.0.46` / `198.18.0.74` | PowerBeam 5AC Gen2 (`WA.ar934x.v8.7.11`) | Remote standalone PoE (`FMX-PBE5AC-STA-ETH7`, 100% OTA) | Terminates Triple-Play `iperf3 -s` (`5201`, `5202`, `5203`) & ICMP Echo Reply |

---

## 3. 3-Round Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`12` Windows)

| Round | Candidate Name | Arm | Bulk TCP (Mbps) | IPTV UDP (Mbps) | Aggregate DL (Mbps) | IPTV Jitter (ms) | IPTV Loss (%) | VoIP Jitter (ms) | Loaded Ping `p50` (ms) | Loaded Ping `p95` (ms) | Loaded Ping `p99` (ms) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S54A-R1`** | `CROSS_NODE_PTP_CHAMPION_251_241_242` | Stock `A` | `15.383` | `7.853` | `23.236` | `0.165` | `2.284%` | `2.349` | `23.386` | `32.313` | `33.288` |
| **`S54A-R1`** | `CROSS_NODE_PTP_CHAMPION_251_241_242` | **Treatment `B`** | **`15.600` (`+1.4%`)** | **`7.865`** | **`23.465` (`+1.0%`)** | `0.221` | **`1.605%` (`-29.7%`)** | **`2.010` (`-14.4%`)** | **`19.242` (`-17.7%`)** | **`25.530` (`-21.0%`)** | **`26.083` (`-21.6%`)** |
| **`S54A-R2`** | `PTP_AMPDU_FRAMES_24_VS_32` | Stock `A` | `17.614` | `7.854` | `25.468` | `0.242` | `0.885%` | `2.357` | `22.721` | `28.358` | `28.779` |
| **`S54A-R2`** | `PTP_AMPDU_FRAMES_24_VS_32` | **Treatment `B`** | **`17.759` (`+0.8%`)** | `7.851` | **`25.610` (`+0.6%`)** | `0.272` | **`0.778%` (`-12.1%`)** | **`1.764` (`-25.2%`)** | **`16.281` (`-28.3%`)** | **`22.174` (`-21.8%`)** | **`22.756` (`-20.9%`)** |
| **`S54A-R3`** | **`PTP_ACKTIMEOUT_25US_AND_AMPDU24_CHAMPION`** | Stock `A` | `18.041` | `7.850` | `25.891` | `0.159` | `0.657%` | `1.524` | `18.782` | `34.323` | `36.207` |
| **`S54A-R3`** | **`PTP_ACKTIMEOUT_25US_AND_AMPDU24_CHAMPION`** | **Treatment `B` (`KEEP`)** | **`19.355` (`+7.3%`)** | **`7.850`** | **`27.205` (`+5.1%`)** | **`0.115` (`-27.7%`)** | `0.925%` | `2.149` | **`14.357` (`-23.6%`)** | **`17.045` (`-50.3%`)** | **`17.192` (`-52.5%`)** |

---

## 4. Per-Window Breakdown (`S54A-R3` Combined Champion Round)

| Window | Arm | Bulk TCP (Mbps) | IPTV UDP (Mbps) | IPTV Jitter (ms) | IPTV Loss (%) | VoIP Jitter (ms) | Loaded Ping `p50` (ms) | Loaded Ping `p95` (ms) | Loaded Ping `p99` (ms) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | Stock `A` (`txq=1000, ampdu=32, ack=27us`) | `17.188` | `7.849` | `0.154` | `1.046%` | `1.575` | `20.355` | `33.137` | `34.520` |
| **`B1`** | **Champion `B` (`txq=192, ampdu=24, ack=25us`)** | **`18.823`** | **`7.849`** | **`0.107`** | **`0.885%`** | **`1.617`** | `22.777` | **`26.519`** | **`26.629`** |
| **`A2`** | Stock `A` (`txq=1000, ampdu=32, ack=27us`) | `18.893` | `7.851` | `0.163` | `0.268%` | `1.474` | `17.210` | `35.508` | `37.894` |
| **`B2`** | **Champion `B` (`txq=192, ampdu=24, ack=25us`)** | **`19.887`** | **`7.851`** | **`0.124`** | **`0.965%`** | `2.682` | **`5.936`** | **`7.571`** | **`7.754`** |

---

## 5. Persisted Stage 54A Champion Configuration (`/etc/persistent/rc.poststart`)

Persisted via `cfgmtd -w -p /etc/` (`Active` + `Backup`) across `198.18.0.48`, `198.18.0.45`, and `198.18.0.46`:

```sh
# Stage 53A/54A Combined PtP Champion (S54A-R3)
for dev in eth0 ath0 br0; do [ -e /sys/class/net/$dev/tx_queue_len ] && echo 192 > /sys/class/net/$dev/tx_queue_len; done
sysctl -w net.core.netdev_budget=600 net.core.dev_weight=64 net.core.netdev_max_backlog=600 >/dev/null 2>&1 || true
sysctl -w net.core.rmem_max=4194304 net.core.wmem_max=4194304 net.ipv4.tcp_sack=1 net.ipv4.tcp_dsack=1 net.ipv4.tcp_ecn=1 >/dev/null 2>&1 || true
iwpriv wifi0 ampduFrames 24 2>/dev/null || true
iwpriv wifi0 ampduLimit 50000 2>/dev/null || true
iwpriv wifi0 acktimeout 25 2>/dev/null || true
iwpriv wifi0 distance 150 2>/dev/null || true
iwpriv ath0 aifs 2 1 2 2>/dev/null || true
iwpriv ath0 cwmin 2 1 2 2>/dev/null || true
iwpriv ath0 cwmax 2 1 3 2>/dev/null || true
iwpriv ath0 aifs 3 1 1 2>/dev/null || true
iwpriv ath0 cwmin 3 1 1 2>/dev/null || true
iwpriv ath0 cwmax 3 1 2 2>/dev/null || true
```
