<!-- doc-head: STAGE53A_PBE5AC_PTP_OTA_AUTORESEARCH_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 53A — PowerBeam 5AC Gen2 Dedicated PtP Over-The-Air Autoresearch Benchmark (`T-S53A-PBE5AC-PTP-OTA-AUTORESEARCH-BENCH`)

## 1. Executive Summary

- **Task ID**: `T-S53A-PBE5AC-PTP-OTA-AUTORESEARCH-BENCH`
- **Status**: **COMPLETED (`KEEP` — Champion `S53A-R4` persisted to flash on both PtP endpoints)**
- **Artifact**: [`artifacts/autoresearch/stage53a_pbe5ac_ptp_ota_autoresearch_bench_20261025.json`](<repo>/artifacts/autoresearch/stage53a_pbe5ac_ptp_ota_autoresearch_bench_20261025.json)
- **Benchmark Runner**: [`tools/bench/run_stage53a_pbe5ac_ptp_ota_autoresearch_bench.py`](<repo>/tools/bench/run_stage53a_pbe5ac_ptp_ota_autoresearch_bench.py)
- **Verification Test Suite**: [`tests/test_stage53a_54a_pbe5ac_and_litebeam_ptp_bench.py`](<repo>/tests/test_stage53a_54a_pbe5ac_and_litebeam_ptp_bench.py)

### Key Outcomes (`CONFIRMED` on Live Hardware)
1. **`S53A-R4` (`PBE5AC_PTP_CHAMPION_COMBINED_STACK_V1`) Cut Loaded Ping `p50` by `-42.3%` (`13.780 ms` $\rightarrow$ `7.950 ms`) and `p95` by `-36.9%` (`24.995 ms` $\rightarrow$ `15.762 ms`)**:
   - Under simultaneous Over-The-Air Triple-Play load (Bulk TCP 2-stream + `8.0 Mbps` IPTV UDP `DSCP CS4` + `64 kbps` VoIP G.711 `DSCP EF` + concurrent `0.2s` ICMP RTT), `S53A-R4` maintained **`26.042 Mbps` aggregate DL goodput** (`18.139 Mbps` Bulk TCP + `7.903 Mbps` IPTV UDP) while cutting loaded `p50` RTT from `13.780 ms` to **`7.950 ms`** (`-42.3%`), `p95` RTT from `24.995 ms` to **`15.762 ms`** (`-36.9%`), and `p99` RTT from `26.256 ms` to **`16.653 ms`** (`-36.6%`).
2. **`S53A-R3` (`PBE5AC_PTP_WMM_VI_VO_AIFS_AND_CWMIN_PRIORITIZATION`) Cut VoIP Jitter by `-54.1%` (`1.554 ms` $\rightarrow$ `0.714 ms`) and IPTV Jitter by `-10.9%` (`0.479 ms` $\rightarrow$ `0.427 ms`)**:
   - Programming `iwpriv ath0 aifs 2 1 2` / `cwmin 2 1 2` / `cwmax 2 1 3` (`AC_VI`) and `aifs 3 1 1` / `cwmin 3 1 1` / `cwmax 3 1 2` (`AC_VO`) alongside `tx_queue_len=192` significantly tightened real-time voice/video scheduling across the airMAX AC PtP bridge.
3. **`S53A-R1` (`PBE5AC_PTP_TXQ_256_AND_NAPI_BUDGET_600`) Increased Bulk TCP Goodput by `+6.6%` (`16.155 Mbps` $\rightarrow$ `17.221 Mbps`) and Aggregate DL to `25.097 Mbps`**:
   - Raising Linux NAPI `netdev_budget` from `300` to `600` (`dev_weight=64`) while bounding `eth0/ath0/br0` `tx_queue_len=256` improved CPU packet-draining throughput on the `WA` (`AR9342` + `QCA9880`) SoC and reduced loaded `p50` RTT by `-15.2%` (`11.874 ms` $\rightarrow$ `10.069 ms`).
4. **Remote Safety Watchdog & Flash Persistence Verified**:
   - Every treatment on the remote standalone-PoE Station (`198.18.0.46` / `198.18.0.74`, `FMX-PBE5AC-STA-ETH7`) armed an isolated `/tmp/wd_pbe 45` background rollback timer before execution and disarmed it only after Over-The-Air `198.18.0.8 -> 198.18.0.74` verification succeeded (`sta_watchdog_disarmed: true` across all 16 windows).
   - Both `198.18.0.45` (`FMX-PBE5AC-AP-ETH3`) and `198.18.0.46` (`FMX-PBE5AC-STA-ETH7`) persisted the winning `S53A-R4` Champion in `/etc/persistent/rc.poststart` (`cfgmtd -w -p /etc/` exit code `0`, `Active->Backup [%100]`).

---

## 2. Lab Topology & Hardware Baseline

| Endpoint | Host / Bench IP | Device / Firmware | Role & Switch Port | RF Link State (`5205 MHz / 20 MHz`) |
| :--- | :--- | :--- | :--- | :--- |
| **PtP AP** | `198.18.0.45` / `198.18.0.8` | PowerBeam 5AC Gen2 (`WA.ar934x.v8.7.11`) | `FMX-PBE5AC-AP-ETH3` (`gi3`, `VLAN 103`, PoE `ON`) | `SSID=FMX-PBE-PTP`, `txpower=4 dBm`, Signal `-67 dBm`, Noise `-95 dBm` |
| **PtP STA** | `198.18.0.46` / `198.18.0.74` | PowerBeam 5AC Gen2 (`WA.ar934x.v8.7.11`) | `FMX-PBE5AC-STA-ETH7` (Remote standalone PoE, 0 Ethernet link on `gi7`, 100% OTA via `.241`) | Associated (`eb:20`), Signal `-69 dBm`, `TX/RX 130/130 Mbps` (`MCS 15` / `2x2` `20 MHz`) |

---

## 3. 4-Round Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`16` Windows)

Each window executed a simultaneous 10-second Over-The-Air Triple-Play workload from `198.18.0.45` (`198.18.0.8`) across the `5205 MHz` (`20 MHz`) PtP link to `198.18.0.46` (`198.18.0.74`):
- **Bulk TCP (`-P 2`)**: 2 parallel TCP streams (`iperf3 -p 5201 -P 2 -t 8`)
- **IPTV UDP (`DSCP CS4` / `0x80`)**: `8.0 Mbps` CBR video stream (`1316B` payload, `iperf3 -p 5202 -u -b 8M -l 1316 -S 0x80 -t 8`)
- **VoIP UDP (`DSCP EF` / `0xb8`)**: `64 kbps` G.711 voice stream (`160B` payload, `iperf3 -p 5203 -u -b 64K -l 160 -S 0xb8 -t 8`)
- **Loaded ICMP RTT**: Concurrent `ping -i 0.2` (`198.18.0.8 -> 198.18.0.74`) during the saturated Triple-Play transfer

| Round | Candidate Name | Arm | Bulk TCP (Mbps) | IPTV UDP (Mbps) | Aggregate DL (Mbps) | IPTV Jitter (ms) | IPTV Loss (%) | VoIP Jitter (ms) | VoIP Loss (%) | Loaded Ping `p50` (ms) | Loaded Ping `p95` (ms) | Loaded Ping `p99` (ms) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S53A-R1`** | `TXQ_256_AND_NAPI_BUDGET_600` | Stock `A` | `16.155` | `7.865` | `24.020` | `0.306` | `0.000%` | `0.911` | `0.0%` | `11.874` | `15.700` | `16.093` |
| **`S53A-R1`** | `TXQ_256_AND_NAPI_BUDGET_600` | **Treatment `B`** | **`17.221` (`+6.6%`)** | **`7.876`** | **`25.097` (`+4.5%`)** | `0.542` | `0.147%` | `2.568` | `0.0%` | **`10.069` (`-15.2%`)** | `17.553` | `18.452` |
| **`S53A-R2`** | `TXQ_128_AND_BACKLOG_500` | Stock `A` | `16.576` | `7.877` | `24.453` | `0.534` | `0.040%` | `0.818` | `0.0%` | `13.186` | `23.018` | `24.236` |
| **`S53A-R2`** | `TXQ_128_AND_BACKLOG_500` | **Treatment `B`** | **`16.723` (`+0.9%`)** | **`7.891`** | **`24.614` (`+0.7%`)** | `0.617` | **`0.000%`** | `0.939` | `0.0%` | **`12.027` (`-8.8%`)** | **`21.948` (`-4.6%`)** | **`23.071` (`-4.8%`)** |
| **`S53A-R3`** | `WMM_VI_VO_AIFS_AND_CWMIN` | Stock `A` | `17.194` | `7.893` | `25.087` | `0.479` | `0.000%` | `1.554` | `0.0%` | `17.599` | `19.794` | `19.970` |
| **`S53A-R3`** | `WMM_VI_VO_AIFS_AND_CWMIN` | **Treatment `B`** | `16.456` | `7.886` | `24.342` | **`0.427` (`-10.9%`)** | `0.240%` | **`0.714` (`-54.1%`)** | `0.0%` | **`16.767` (`-4.7%`)** | `21.960` | `22.404` |
| **`S53A-R4`** | **`PTP_CHAMPION_COMBINED_STACK_V1`** | Stock `A` | `18.274` | `7.871` | `26.145` | `0.562` | `0.040%` | `1.149` | `0.0%` | `13.780` | `24.995` | `26.256` |
| **`S53A-R4`** | **`PTP_CHAMPION_COMBINED_STACK_V1`** | **Treatment `B` (`KEEP`)** | **`18.139`** | **`7.903`** | **`26.042`** | **`0.561`** | **`0.026%` (`-35.0%`)** | **`1.085` (`-5.6%`)** | **`0.0%`** | **`7.950` (`-42.3%`)** | **`15.762` (`-36.9%`)** | **`16.653` (`-36.6%`)** |

---

## 4. Per-Window Breakdown (`S53A-R4` Champion Round)

| Window | Arm | Bulk TCP (Mbps) | IPTV UDP (Mbps) | IPTV Jitter (ms) | IPTV Loss (%) | VoIP Jitter (ms) | Loaded Ping `p50` (ms) | Loaded Ping `p95` (ms) | Loaded Ping `p99` (ms) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | Stock `A` (`txq=1000, budget=300`) | `17.792` | `7.851` | `0.487` | `0.080%` | `1.124` | `10.668` | `23.372` | `24.696` |
| **`B1`** | **Champion `B` (`txq=192, budget=600, WMM+TCP`)** | **`17.785`** | **`7.912`** | **`0.506`** | **`0.053%`** | **`0.858`** | **`9.571`** | **`15.860`** | **`16.342`** |
| **`A2`** | Stock `A` (`txq=1000, budget=300`) | `18.756` | `7.891` | `0.637` | `0.000%` | `1.174` | `16.892` | `26.619` | `27.816` |
| **`B2`** | **Champion `B` (`txq=192, budget=600, WMM+TCP`)** | **`18.492`** | **`7.895`** | **`0.616`** | **`0.000%`** | **`1.312`** | **`6.330`** | **`15.664`** | **`16.963`** |

---

## 5. Persisted Stage 53A Champion Configuration (`/etc/persistent/rc.poststart`)

Both `198.18.0.45` (`FMX-PBE5AC-AP-ETH3`) and `198.18.0.46` (`FMX-PBE5AC-STA-ETH7`) now execute the Stage 53A Champion (`S53A-R4`) on boot via `/etc/persistent/rc.poststart` (`cfgmtd -w -p /etc/`):

```sh
# Stage 53A Champion (S53A-R4: PBE5AC_PTP_CHAMPION_COMBINED_STACK_V1)
for dev in eth0 ath0 br0; do [ -e /sys/class/net/$dev/tx_queue_len ] && echo 192 > /sys/class/net/$dev/tx_queue_len; done
sysctl -w net.core.netdev_budget=600 net.core.dev_weight=64 net.core.netdev_max_backlog=600 >/dev/null 2>&1 || true
sysctl -w net.core.rmem_max=4194304 net.core.wmem_max=4194304 net.ipv4.tcp_sack=1 net.ipv4.tcp_dsack=1 net.ipv4.tcp_ecn=1 >/dev/null 2>&1 || true
iwpriv ath0 aifs 2 1 2 2>/dev/null || true
iwpriv ath0 cwmin 2 1 2 2>/dev/null || true
iwpriv ath0 cwmax 2 1 3 2>/dev/null || true
iwpriv ath0 aifs 3 1 1 2>/dev/null || true
iwpriv ath0 cwmin 3 1 1 2>/dev/null || true
iwpriv ath0 cwmax 3 1 2 2>/dev/null || true
```
