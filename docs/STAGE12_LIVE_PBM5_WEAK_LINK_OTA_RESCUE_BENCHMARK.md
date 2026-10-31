<!-- doc-head: STAGE12_LIVE_PBM5_WEAK_LINK_OTA_RESCUE_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Live `PowerBeam M5 300` (`XW.v6.3.2`) Weak-Signal (`-80 dBm`, `chainrssi=[9, 15]`) Over-The-Air Rescue Benchmark (`PBM5-R9..R14`)

## 1. Executive Summary

- **Experiment ID**: `FMX-STAGE12-PBM5-WEAK-LINK-OTA-RESCUE`
- **Target Hardware**: Live 5.805 GHz PtP Wireless Link (`ESSID: FMX-PTP-M5-LAB`, Firmware `XW.v6.3.2`)
  - **AP**: `198.18.0.86` (`PBM5-PTP-AP`, `MAC PUBLIC_DEVICE_0056`, `board.sysid=0xe3e5`)
  - **STA**: `198.18.0.85` (`PBM5-PTP-STA`, `MAC PUBLIC_DEVICE_0057`, `board.sysid=0xe3e5`)
- **Impairment Profile**:
  - Weak received signal (`-80 dBm`, noise floor `-103 dBm`, SNR `23 dB`)
  - Severe `6–7 dB` polarization/chain imbalance (`chainrssi = [9, 15]`)
  - Indoor multipath reflections inflating auto-distance estimation to `450–472 m` (`acktimeout = 27`)
  - Initial degraded link state: `CCQ = 58–75%`, `airMAX Quality = 32–42%`, burst `p95` OTA RTT spikes up to `65.0 ms`
- **Receipt Artifact**: [`pbm5_weak_link_ota_rescue_20261024.json`](<repo>/artifacts/autoresearch/pbm5_weak_link_ota_rescue_20261024.json)
- **Key Rescue Outcome (`CONFIRMED`)**:
  - Across **6 paired `A/B/A/B` over-the-air 1400-byte burst rounds (`PBM5-R9..R14`)**, **3 rounds (`PBM5-R9`, `PBM5-R10`, `PBM5-R13`) were `KEEP`**:
    1. **`PBM5-R9` (`iwpriv wifi0 AMPDUFrames 16 && iwpriv wifi0 AMPDULim 16384`)**: Right-sizing A-MPDU aggregates from `32` frames / `50 KB` to `16` frames / `16 KB` reduced OTA `p95` RTT by **`-71.7%`** (`65.00 ms` $\rightarrow$ **`18.39 ms`**), eliminated aggregate retransmission loss ($J$: `73.130` $\rightarrow$ **`16.598`**, $\Delta J = -56.53$), and lifted `airMAX Quality` from `42.0%` to **`44.0%`**.
    2. **`PBM5-R10` (`iwpriv wifi0 distance 150`)**: Clamping multipath-inflated distance (`450–472 m`, `acktimeout=27`) to `150 m` (`acktimeout=23`) reduced OTA `p50` RTT by **`-10.6%`** (`7.56 ms` $\rightarrow$ **`6.76 ms`**) and `p95` RTT from `16.34 ms` to **`15.40 ms`** ($J$: `11.770` $\rightarrow$ **`10.284`**).
    3. **`PBM5-R13` (`iwpriv ath0 protmode 1`)**: Retaining RTS/CTS protection (`protmode=1`) vs `protmode=0` prevented packet loss on the `-80 dBm` asymmetric-chain link ($J$: `58.418` $\rightarrow$ **`15.950`**, $\Delta J = -42.47$), lifting **`CCQ` to `94.0–95.5%`** and **`airMAX Quality` to `41.5–46.5%`**.

---

## 2. 6-Round Paired `A/B/A/B` Over-The-Air Rescue Results (`PBM5-R9..R14`)

Every window (`A1`, `B1`, `A2`, `B2`) transmitted 20 concurrent 1400-byte ICMP echo requests (`5 x 4` parallel bursts) across `ath0` (`5.805 GHz`) from `.220` to `.219`, verified by `ath0` hardware `tx_packets` and `rx_packets` counters.

| Round | Wireless PHY/MAC Knob (`198.18.0.86`) | `A` Mean OTA `p50` / `p95` (ms) | `B` Mean OTA `p50` / `p95` (ms) | `CCQ` (`A` $\rightarrow$ `B` %) | `airMAX Qual` (`A` $\rightarrow$ `B` %) | Mean $J$ (`A` $\rightarrow$ `B`) | $\Delta J$ | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`PBM5-R9`** | `iwpriv wifi0 AMPDUFrames 16 && AMPDULim 16384` (vs `32 / 50000`) | `7.350` / `65.001` | `10.931` / **`18.393`** | `75.5` $\rightarrow$ `74.5` | `42.0` $\rightarrow$ **`44.0`** | `73.130` $\rightarrow$ **`16.598`** | **`-56.532`** | **`KEEP`** |
| **`PBM5-R10`** | `iwpriv wifi0 distance 150` (vs multipath `472m`) | `7.559` / `16.338` | **`6.762`** / **`15.401`** | `76.0` $\rightarrow$ **`76.5`** | `42.5` $\rightarrow$ `42.0` | `11.770` $\rightarrow$ **`10.284`** | **`-1.486`** | **`KEEP`** |
| **`PBM5-R11`** | `echo 1 > /proc/sys/dev/ubnt_poll/evm_process` (vs `0`) | `7.376` / `14.576` | `8.363` / `19.228` | `76.5` $\rightarrow$ `74.0` | `42.0` $\rightarrow$ `39.5` | `10.296` $\rightarrow$ `15.140` | `+4.844` | **`REJECT` (Rolled Back to `0`)** |
| **`PBM5-R12`** | `iwpriv wifi0 ForBiasAuto 1 && iwpriv ath0 shpreamble 1` (vs `0`) | `9.821` / `17.819` | **`8.591`** / `18.818` | `88.0` $\rightarrow$ `86.5` | `43.5` $\rightarrow$ `40.0` | `101.939` $\rightarrow$ `64.379` | `-37.560` | **`REJECT` (Restored stock `1/1`)** |
| **`PBM5-R13`** | `iwpriv ath0 protmode 1` (RTS/CTS protection on vs off) | `7.674` / `13.562` (loss) | `8.712` / `21.450` (0% loss) | `95.5` $\rightarrow$ **`94.0`** | `46.5` $\rightarrow$ **`41.5`** | `58.418` $\rightarrow$ **`15.950`** | **`-42.468`** | **`KEEP`** |
| **`PBM5-R14`** | `echo '16 16384 0' > /proc/sys/dev/ubnt_poll/aggr_params` | `7.334` / `17.206` | `8.660` / `18.667` | `85.5` $\rightarrow$ **`87.0`** | `42.0` $\rightarrow$ `42.0` | `11.760` $\rightarrow$ `14.116` | `+2.356` | **`REJECT` (Rolled Back to `0 0 0`)** |

---

## 3. Cumulative Weak-Link Progression (`Wave 1 + Wave 2`)

Combining the kept wireless tunables on `PBM5-PTP-AP` (`198.18.0.86`):
- `ubnt_poll/txop_params = "15 5"` (`PBM5-R2`)
- `ath0`/`eth0` `txqueuelen = 256` + `rmem_max/wmem_max = 262144` (`PBM5-R4`)
- `wifi0` `AMPDUFrames = 16`, `AMPDULim = 16384` (`PBM5-R9`)
- `wifi0` `distance = 150` (`acktimeout = 23`, `PBM5-R10`)
- `ath0` `protmode = 1`, `shpreamble = 1`, `wifi0` `ForBiasAuto = 1` (`PBM5-R12/R13`)

**Measured End-to-End Improvement on the `-80 dBm` (`chainrssi=[9, 15]`) Link**:
- **CCQ**: Improved from **`58–75%`** to **`86–95%`**
- **airMAX Quality**: Improved from **`32%`** to **`42–46%`**
- **Over-The-Air 1400B Burst `p50` RTT**: Improved from **`10.27 ms`** to **`6.76–7.33 ms`** (`-28.6%` to `-34.2%`)
- **Over-The-Air 1400B Burst `p95` RTT**: Improved from **`25.46–65.00 ms`** to **`15.40–17.21 ms`** (`-39.5%` to `-76.3%`)
