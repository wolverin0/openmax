<!-- doc-head: October22 exact-device compatibility alignment and historical scope -->
Stock WA8/XC8 and four-generation PtMP confirmed by run17/run25/run8.
Original dated benchmarks/static findings keep their hardware and firmware scope.
No new performance, TDMA/GPS, relay, production or E2 acceptance follows.
Current authoritative state and source receipts are linked below.
<!-- /doc-head -->

## October22 evidence alignment - current bench scope

The accepted exact-device receipts supersede any universal present-tense reading
of older incompatibility or topology statements below: run17 establishes stock
WA.v8.7.25 Loco195 bidirectional association with the held LAP-120 OpenWrt AP;
run25 adds stock XC.v8.7.25 Rocket198 concurrently (61.031s authorization,
64/64 radio-qualified pings each); FMX-0016 run8 adds SXT OpenWrt/ath9k and
stock airOS6 M5 concurrently (60.5s,64/64 each,256 matched radio echo pairs).
All modified state was restored and the AP radio disabled. These are exact
bench compatibility results; they do not establish capacity, performance gain,
TDMA/GPS, all-revision support, physical relay or production acceptance.

Sources: [current state](CURRENT_STATE.md),
[run8 receipt](../artifacts/canary_panel1_guarida/root_four_cpe_result_20261022.json),
[Oct22 scoped evidence alignment](../artifacts/canary_panel1_guarida/fmx_docs_alignment_20261022.json).
Existing E2 remains `NOT_ACCEPTED` with its original gates. Original dated
measurements, failures, static control limits and firmware scopes remain
historical evidence, not permission to resume those recipes.
The Stage7-9 Loco-OpenWrt topology and adaptive-controller recipes below belong to their Oct17 measurements. Loco195 is stock WA8 in the Oct22 fixture; no optimizer/procd service is being accepted or resumed by the newer compatibility result.



# Stage 8 — Closed-Loop Adaptive Sector Controller, Live Hardware Spectral FFT & Channel-Width Optimizer, and Peak-Hour Bidirectional WISP Sector Stress Test

**Date**: 2026-10-17  
**Status**: **CONFIRMED ON LIVE 3-STATION HETEROGENEOUS BENCH**  
**Raw Data Artifact**: [`artifacts/stage8_ptmp/stage8_adaptive_and_sector_results.json`](../artifacts/stage8_ptmp/stage8_adaptive_and_sector_results.json)  
**Controller Daemon**: [`controller/fmx_adaptive_controller.sh`](../controller/fmx_adaptive_controller.sh)  
**Benchmark Harness**: [`tools/bench/stage8_adaptive_and_sector_bench.py`](../tools/bench/stage8_adaptive_and_sector_bench.py)

---

## 1. Executive Summary

Stage 8 transitions our open-source **OpenMAX / FuturaMAX** findings from static kernel/driver parameters into an **autonomous, closed-loop WISP sector control stack** executing directly on the `Ubiquiti LiteAP AC (LAP-120)` AP (`533 MHz MIPS 74Kc`, `OpenWrt 24.10.4`, `ath10k-ct`) across the 3-station multi-vendor, mixed-generation bench (`NanoStation 5AC Loco` in-room `~3m`; `MikroTik SXT Lite5` and stock `airOS 6.1.4` `Ubiquiti LiteBeam M5` obstructed behind a wall/door `~6m`):

1. **Stage 8A — Zero-Fork Closed-Loop Adaptive Sector Controller (`fmx_adaptive_controller.sh`)**:
   - **Static Policy Dilemma**: A static unbounded configuration (`Policy 1: ATF=Off, AQL=24000/48000, Agg=3x64`) achieves high single-station burst speed (`110.94–111.05 Mbps`), but when all 3 stations contend in Phase 2 (`5 dBm` near-far regime), the wall-obstructed `MikroTik SXT` is **completely starved (`0.00 Mbps`)** and its `p95` RTT explodes to **`942.0 ms`** (`1,157 ms p99`). Conversely, a static conservative multi-station configuration (`Policy 2: Equal ATF, AQL=1000/2000, Agg=1x8`) protects `SXT` during contention (`11.00 Mbps`), but permanently throttles single-station burst throughput by **`-34.2%` (`73.57 / 72.40 Mbps`)** and caps 3-station total goodput at `62.19 Mbps`.
   - **Closed-Loop Solution (`Policy 3`)**: Using a **zero-fork pure-debugfs daemon** (`controller/fmx_adaptive_controller.sh`) that reads `/sys/kernel/debug/ieee80211/phy0/netdev:phy0-ap0/stations/<mac>/airtime` directly via POSIX shell built-ins (`<0.1%` AP CPU overhead), the AP automatically switches between `SINGLE_STA_TURBO` (`active_count <= 1`) and `MULTI_STA_ADAPTIVE` (`active_count >= 2`).
   - **Measured Result**: `Policy 3` achieves **`109.35 Mbps`** in Phase 1 (`SINGLE_STA_TURBO`), automatically switches to `MULTI_STA_ADAPTIVE` in Phase 2 when all 3 stations burst (`90.12 Mbps` total sector goodput, keeping `SXT` alive at `3.67 Mbps` and `LiteBeam M5` at `21.74 Mbps` while holding loaded median RTT to **`5.36 ms`** on `SXT`, **`5.33 ms`** on `LiteBeam M5`, and **`7.27 ms`** on `Loco 5AC` — a **`47.6x` `p95` tail-latency reduction** on `SXT` vs `Policy 1`), and immediately recovers to **`118.67 Mbps`** (`+63.9%` over `Policy 2`) in Phase 3 (`SINGLE_STA_TURBO`).

2. **Stage 8B — Live Hardware Spectral FFT & Channel-Width Optimizer (`VHT80` vs `VHT40`)**:
   - Captured **`618,729` bytes (`6,653` FFT frames)** from the `LAP-120` QCA9882 baseband spectral scanner (`/sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan0`), confirming a **`-105 dBm` hardware noise floor** (`CLEAN_CHANNEL`).
   - **Critical Firmware Control-Boundary Discovery**: Triggering an off-channel AP scan via `iw dev phy0-ap0 scan ... ap-force` on `ath10k-ct` (`10.1-ct-8x-__fW-022`) leaves the QCA988x PCIe target firmware in a persistent beacon-aligned (`102.4 ms`) scan sawtooth that is **not** cleared by `echo disable > spectral_scan_ctl` or `wifi reload` (`hostapd` restart), requiring an `ath10k_pci` module reload or reboot.
   - **`VHT40` (40 MHz) Outperforms `VHT80` (80 MHz) in Mixed `802.11ac + 802.11n` Downlink Contention**: Narrowing the sector AP from `VHT80` (`80 MHz`) to `VHT40` (`40 MHz`) **increased 3-station simultaneous Downlink goodput by `+13.1%` (`92.98 -> 105.18 Mbps`, peaking at `110.68 Mbps`)**, boosted the stock `airOS 6` `LiteBeam M5` by **`+56.7%` (`25.57 -> 40.06 Mbps`)**, cut 3-station loaded median RTT by **`3.1x` (`27.9 -> 9.1 ms`)**, and increased **downlink spectral efficiency by `2.26x` (`1.162 -> 2.630 bit/s/Hz`)** and **uplink spectral efficiency by `1.52x` (`1.946 -> 2.953 bit/s/Hz`)**.

3. **Stage 8C — Peak-Hour Bidirectional 6-Flow WISP Sector Stress Test (`3 DL + 3 UL + 3 Interactive`)**:
   - Under simultaneous 6-flow bidirectional TCP saturation (`3 Downlink + 3 Uplink` streams across all 3 stations at once), **Unoptimized Stock OpenWrt** suffers severe Downlink collapse (`30.26 Mbps` average total DL) and massive bufferbloat on the obstructed `MikroTik SXT` (**`251.3 ms` median RTT / `607.5 ms p95` / `904.0 ms p99`**).
   - Activating the **Full FuturaMAX Stage 8 Sector Stack** (`fmx_adaptive_controller.sh` + `ATF` + `AQL 1000/2000` + `WMM AC_VO DiffServ Bypass` + Station `RTS/CTS = 256B` + Gateway `CAKE diffserv4 nat ack-filter`) **increases total sector Downlink goodput by `+49.4%` (`30.26 -> 45.22 Mbps`)**, raises total bidirectional sector throughput from **`134.58 -> 153.01 Mbps` (`+13.7%`)**, and **crushes `MikroTik SXT` loaded median RTT by `39.1x` (`251.3 ms -> 6.43 ms`, `p95` `607.5 ms -> 18.75 ms`)** while holding `Loco 5AC` at **`7.40 ms`** and `LiteBeam M5` at **`7.22 ms`**.

---

## 2. Stage 8A — Closed-Loop Adaptive Sector Controller vs Static Policies (`AP TX Power = 5 dBm`)

### 2.1 Architecture of `controller/fmx_adaptive_controller.sh`
An early prototype that spawned `iw dev phy0-ap0 station dump` and `awk` every second caused measurable CPU and netlink contention on the single-core 533 MHz MIPS 74Kc (`AR9342`) AP. We redesigned [`controller/fmx_adaptive_controller.sh`](../controller/fmx_adaptive_controller.sh) as a **zero-fork pure-debugfs daemon**:
- Every 1 second, it reads `/sys/kernel/debug/ieee80211/phy0/netdev:phy0-ap0/stations/<mac>/airtime` and `vht_capa` using only POSIX shell built-in `read` and integer arithmetic (`0` subshell forks per station poll, `<0.1%` CPU usage).
- If `DELTA_TX_US >= 15000` (at least `15 ms` of airtime consumed in the last 1s), the station is counted as active.
- **State Machine**:
  - `SINGLE_STA_TURBO` (`active_count <= 1`): Unlocks full aggregation (`htt_max_amsdu_ampdu = 3 64`) and `AQL = 3000/6000 us` (`threshold = 12000 us`) so a single active subscriber can burst at full line rate (`109–119 Mbps`).
  - `MULTI_STA_ADAPTIVE` (`active_count >= 2`): Clamps aggregation (`htt_max_amsdu_ampdu = 1 16`) and tightens `AQL = 1500/3000 us` (`threshold = 6000 us`) while enforcing proportional airtime weights (`768` for `VHT80` 802.11ac, `256` for healthy `HT40` 802.11n, `128` SLA floor for deep negative `BE`-deficit stations) and `WMM AC_VO DiffServ Deficit Bypass`.

### 2.2 3-Phase Dynamic Workload Results (`5 dBm` Near-Far Contention Regime)

| Policy | Phase 1: Single-Station Burst (`Loco 5AC` Alone, 6s) | Phase 2: All-3 Simultaneous Contention (`Loco + SXT + LBM5`, 8s) | Phase 2 Loaded RTT `p50 / p95` (`Loco` \| `LBM5` \| `SXT`) | Phase 3: Single-Station Recovery (`Loco 5AC` Alone, 6s) | Controller State Transitions |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`Policy 1`: Static Unbounded (`ATF=Off`, `AQL 24k/48k`, `Agg 3x64`, `No AC_VO`)** | `110.94 Mbps` (`p50: 30.8 ms`) | **`92.16 Mbps`** (`Loco`: `73.83`, `LBM5`: `18.33`, **`SXT`: `0.00 Mbps` STARVED**) | `43.2 / 74.2 ms` \| `31.6 / 78.1 ms` \| **`62.4 / 942.0 ms`** (`1157 ms p99`) | `111.05 Mbps` (`p50: 30.6 ms`) | *None (Static)* |
| **`Policy 2`: Static Conservative (`Equal ATF`, `AQL 1k/2k`, `Agg 1x8`, `No AC_VO`)** | **`73.57 Mbps`** (`-33.7%` loss, `p50: 6.53 ms`) | **`62.19 Mbps`** (`Loco`: `32.85`, `LBM5`: `18.34`, `SXT`: `11.00`, Jain `0.8391`) | `14.0 / 22.7 ms` \| `12.1 / 120.0 ms` \| `31.4 / 281.0 ms` | **`72.40 Mbps`** (`-34.8%` loss, `p50: 7.27 ms`) | *None (Static)* |
| **`Policy 3`: FuturaMAX Closed-Loop Adaptive Daemon (`fmx_adaptive_controller.sh`)** | **`109.35 Mbps`** (`p50: 23.85 ms` / `7.43 ms` tuned) | **`90.12 Mbps`** (`Loco`: `64.71`, `LBM5`: `21.74`, `SXT`: `3.67 Mbps`) | **`7.27 / 19.7 ms`** \| **`5.33 / 15.8 ms`** \| **`5.36 / 19.8 ms`** | **`118.67 Mbps`** (`p50: 23.55 ms` / `6.96 ms` tuned) | `SINGLE_STA_TURBO (1)` $\to$ `MULTI_STA_ADAPTIVE (3)` $\to$ `SINGLE_STA_TURBO (1)` |

---

## 3. Stage 8B — Live Hardware Spectral FFT & Channel-Width Optimizer (`VHT80` vs `VHT40`)

### 3.1 Live Hardware Baseband Spectral FFT Capture (`LAP-120` QCA9882)
Using `/sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan_ctl` (`background` + `trigger`) and [`telemetry/spectral_fft/parser.py`](../telemetry/spectral_fft/parser.py):
- **Total Capture**: **`618,729` bytes** across **`6,653` parsed Type-3 TLV FFT frames**.
- **Measured Noise Floor & Classification**:
  - `5200 MHz` (`Channel 40`, `VHT80` primary/secondary): `126` FFT frames, mean hardware noise floor **`-105.0 dBm`**, mean RSSI `28.96 dB`, classified as **`CLEAN_CHANNEL`** (`0.0%` non-Wi-Fi jammer occupancy).
  - `5865 MHz`: `6,527` FFT frames, mean hardware noise floor **`-105.0 dBm`**, mean RSSI `5.82 dB`, classified as **`CLEAN_CHANNEL`**.
- **Operational Boundary (`CONFIRMED`)**: Calling `iw dev phy0-ap0 scan ... ap-force` on an active `ath10k-ct` (`10.1-ct-8x-__fW-022`) AP vdev triggers a persistent beacon-aligned (`102.4 ms`) target firmware scan state that survives `echo disable > spectral_scan_ctl` and `wifi reload` (`hostapd` restart), requiring `rmmod ath10k_pci && modprobe ath10k_pci` or AP reboot to clear. On active PtMP sectors, spectral FFT must be triggered passively on the operating channel without `ap-force` off-channel scanning, or executed from an OpenWrt CPE (`Loco 5AC`).

### 3.2 `VHT80` (80 MHz) vs `VHT40` (40 MHz) Across the Heterogeneous 3-Station Sector (`11 dBm`)

| Metric | `VHT80` (80 MHz Channel Width) | `VHT40` (40 MHz Channel Width) | Impact of Narrowing Sector `80 MHz -> 40 MHz` |
| :--- | :---: | :---: | :---: |
| **3-Station Simultaneous Downlink Goodput (Mean / Peak)** | `92.98 Mbps` (`90.98`, `94.98 Mbps`) | **`105.18 Mbps` (`99.68`, `110.68 Mbps`)** | **`+13.1%` Higher Total Sector DL Goodput (`+16.5%` peak)** |
| **Downlink Per-Station Breakdown (`Loco 5AC` / `LiteBeam M5` / `SXT`)** | `58.91` / `25.57` / `8.51 Mbps` | **`60.42` / `40.06` / `4.71 Mbps`** | **`+56.7%` boost on `LiteBeam M5`**, `+2.6%` on `Loco 5AC` |
| **Downlink TCP Retransmits (3-Station Sum per 8s Trial)** | `700.0` (`681`, `719`) | **`33.0` (`51`, `15`)** | **`21.2x` Reduction in Downlink TCP Retransmits** |
| **Downlink Loaded Median RTT (`Loco 5AC` / `LiteBeam M5` / `SXT`)** | `27.88 ms` / `26.75 ms` / `26.18 ms` | **`8.29 ms` / `9.41 ms` / `9.39 ms`** | **`3.1x` Lower Loaded Median RTT across all 3 stations** |
| **Downlink Spectral Efficiency ($\text{bit/s/Hz}$)** | `1.162 bit/s/Hz` | **`2.630 bit/s/Hz` (`2.767` peak)** | **`2.26x` (`+126.3%`) Higher Downlink Spectral Efficiency** |
| **3-Station Simultaneous Uplink Goodput (Mean)** | **`155.70 Mbps` (`155.71`, `155.69`)** | `118.09 Mbps` (`122.94`, `113.23`) | `-24.2%` raw UL (`Loco 5AC` capped at `2x2 HT40` `300 Mbps` PHY) |
| **Uplink Spectral Efficiency ($\text{bit/s/Hz}$)** | `1.946 bit/s/Hz` | **`2.953 bit/s/Hz` (`3.074` peak)** | **`1.52x` (`+51.7%`) Higher Uplink Spectral Efficiency** |

**Why `VHT40` Beats `VHT80` on Downlink in a Mixed `802.11ac + 802.11n` Sector (`CONFIRMED`)**:
1. **`+3 dB` Power Spectral Density (PSD) & `-3 dB` Thermal Noise Floor**: Halving the channel width from `80 MHz` to `40 MHz` improves `Loco 5AC` RSSI from `-50 dBm` to **`-47 dBm` (`+3 dB`)** and eliminates primary/secondary 40 MHz CCA mismatch when `HT40` stations (`LiteBeam M5`, `MikroTik SXT`) transmit alongside `VHT80` frames.
2. **Elimination of `VHT80` Rate Instability Under Multi-Station Contention**: On `VHT80`, `Loco 5AC` DL rate oscillates (`VHT-MCS 4 80MHz`, `351 Mbps` with `332` TCP retransmits/trial). On `VHT40`, `Loco 5AC` locks solidly at `VHT-MCS 5 40MHz` (`216 Mbps`) with **21x fewer TCP retransmits** (`33` total across the entire sector), freeing airtime (`38.1%` share) for `LiteBeam M5` to jump from **`25.57 Mbps -> 40.06 Mbps` (`+56.7%`)**!

---

## 4. Stage 8C — Peak-Hour Bidirectional 6-Flow WISP Sector Stress Test (`3 DL + 3 UL + 3 Interactive`)

Simultaneous 8-second bidirectional saturation (`3 Downlink TCP` flows on port `5201` + `3 Uplink TCP` flows on port `5202` + `3 Interactive Ping/VoIP` probes across `Loco 5AC`, `MikroTik SXT`, and `LiteBeam M5` at `11 dBm`):

| Metric | Mode 1: Unoptimized Stock OpenWrt Sector (`ATF=Off`, `AQL 24k`, `Agg 3x64`, `RTS=Off`, `No CAKE`) | Mode 2: FuturaMAX Full Stage 8 Stack (`Adaptive Daemon` + `ATF` + `AQL 1k/2k` + `AC_VO Bypass` + `RTS=256B` + `Gateway CAKE`) | Improvement (`Mode 2` vs `Mode 1`) |
| :--- | :---: | :---: | :---: |
| **Total Sector Downlink Goodput (Mean of 2 Trials)** | `30.26 Mbps` (`36.08`, `24.43 Mbps`) | **`45.22 Mbps` (`47.39`, `43.05 Mbps`)** | **`+49.4%` Higher Sector Downlink Goodput** |
| **Total Sector Uplink Goodput (Mean of 2 Trials)** | `104.32 Mbps` (`89.90`, `118.74 Mbps`) | **`107.79 Mbps` (`106.94`, `108.64 Mbps`)** | **`+3.3%` Higher & Consistent Uplink Goodput** |
| **Total Bidirectional Sector Goodput (`DL + UL`)** | `134.58 Mbps` (`125.98`, `143.17 Mbps`) | **`153.01 Mbps` (`154.33`, `151.69 Mbps`)** | **`+13.7%` (`+18.43 Mbps`) Total Sector Capacity** |
| **Wall-Obstructed `MikroTik SXT` BiDir Goodput (`DL / UL`)** | `2.29 Mbps DL` / `1.31 Mbps UL` | **`6.22 Mbps DL` / `2.62 Mbps UL`** | **`2.72x` Higher DL & `2.00x` Higher UL on Weakest CPE** |
| **`Loco 5AC` Loaded RTT (`p50` / `p95` / `p99`)** | `20.15 ms` / `38.45 ms` / `50.75 ms` | **`7.40 ms` / `14.70 ms` / `19.75 ms`** | **`2.7x` Lower `p50` (`2.6x` Lower `p95`)** |
| **`LiteBeam M5` (airOS 6) Loaded RTT (`p50` / `p95` / `p99`)** | `23.33 ms` / `46.00 ms` / `51.45 ms` | **`7.22 ms` / `16.15 ms` / `21.85 ms`** | **`3.2x` Lower `p50` (`2.8x` Lower `p95`)** |
| **`MikroTik SXT` Loaded RTT (`p50` / `p95` / `p99`)** | **`251.25 ms` / `607.50 ms` / `797.50 ms`** | **`6.43 ms` / `18.75 ms` / `44.55 ms`** | **`39.1x` Lower `p50` (`32.4x` Lower `p95`)** |
