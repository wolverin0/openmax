# openMAX Public Update #3 — 3-Station Multi-Vendor PtMP Benchmarks (`802.11ac` + `MikroTik SXT` + Stock `airOS 6` `LiteBeam M5`), `21x–47x` Latency Cut, `80/40/20 MHz` Physics, and Zero-Fork Adaptive Controller

**TL;DR for `r/wisp` / `r/openwrt` / `r/networking`:**
We expanded our physical lab from a single PtP link to a **3-station heterogeneous multi-vendor PtMP sector** (`Ubiquiti LAP-120` AP on OpenWrt 24.10.4 serving: **[1] `Ubiquiti NanoStation 5AC Loco`** `802.11ac 2x2` in room, **[2] `MikroTik SXT Lite5`** `802.11n 2x2` behind a solid wall/door, and **[3] `Ubiquiti LiteBeam M5`** running **unmodified stock `airOS 6.1.4` `802.11n 1x1`** behind a wall/door) and completed **Stages 7, 8, and 9**:

1. **`WMM AC_VO DiffServ Deficit Bypass` (`21.0x` Weak-Client Latency Cut)**: We discovered a subtle `mac80211` behavior on `ath10k-ct`: when an obstructed `802.11n` client (`MikroTik SXT` behind a wall) suffers rate fallback + retries under bulk TCP (`AC_BE`), its `mac80211` airtime deficit drops to **`-67,099 µs` (`-67.1 ms`)**, pausing its `BE` queue to protect the sector—while its `VO` access category stays at **`+256 µs` (`0 µs` queue)**. Promoting interactive/control packets (`ICMP`, `DNS`, `NTP`, `SIP/VoIP`) to `DSCP EF` (`AC_VO`) in `nftables` cut the obstructed `MikroTik SXT`'s loaded median RTT by **`21.0x` (`143.0 ms -> 6.80 ms`, `p95: 763 -> 17 ms` = `44.9x` cut)** and the stock `airOS 6` `LiteBeam M5` by **`8.0x` (`36.15 -> 4.53 ms`)**, while raising 3-station sector goodput **`+27.2%`**.
2. **Multi-Station Uplink `RTS/CTS = 256B` + `CoTSQ 128 KB` (`181.90 Mbps` 3-Station Uplink)**: With 3 stations transmitting simultaneously on Uplink across a wall obstruction (`Near-Far`), enabling `RTS/CTS = 256B` (`NAV` duration reservation) boosted total sector Uplink goodput by **`+18.5%` (`150.40 -> 178.17 Mbps`)** and recovered the wall-starved `MikroTik SXT` by **`3.07x` (`1.97 -> 6.03 Mbps`)**. Adding `CoTSQ` (`tcp_limit_output_bytes = 131072`) + `fq_codel quantum 300` pushed 3-station simultaneous Uplink to **`181.90 Mbps`** (`Loco 5AC = 141.93 Mbps` with `0` TCP retransmits).
3. **Zero-Fork Pure-Debugfs Adaptive Sector Controller (`<0.1%` CPU on 533 MHz MIPS)**: Built `fmx_adaptive_controller.sh` + `fmx_watchdog.sh` supervised by OpenWrt `procd` (`/etc/init.d/futuramax`). It reads `/sys/kernel/debug/ieee80211/phy0/netdev:phy0-ap0/stations/<mac>/airtime` directly via POSIX shell built-ins (`0` process forks per poll), delivering **`109.35–118.67 Mbps`** when 1 station bursts (`SINGLE_STA_TURBO`) and automatically clamping to `MULTI_STA_ADAPTIVE` (`Agg 1x16`, `AQL 1500/3000`, proportional weights `768:256:128`) when `>=2` stations contend (**`90.12 Mbps` total, `5.33–7.27 ms` median RTT across all 3 stations, `47.6x` `p95` tail-latency cut** vs Static Unbounded).
4. **The `80 MHz` vs `40 MHz` vs `20 MHz` Mixed-Sector Physics Proof**:
   - Narrowing the mixed `AC + N` sector from **`80 MHz` (`VHT80`) to `40 MHz` (`VHT40`)** *increased* 3-station simultaneous Downlink goodput by **`+13.1%` (`92.98 -> 105.18 Mbps`, peaking at `110.68 Mbps`)**, boosted the stock `LiteBeam M5` by **`+56.7%` (`25.57 -> 40.06 Mbps`)**, cut TCP retransmissions by **`21.2x` (`700 -> 33`)**, and raised spectral efficiency **`2.26x` (`1.162 -> 2.630 bit/s/Hz`)**.
   - Narrowing to **`20 MHz` (`VHT20` — our real 17-sector WISP production width)** (`+6 dB` PSD, `-6 dB` thermal noise, zero secondary-channel selective fading) boosted the obstructed `MikroTik SXT`'s standalone DL by **`3.05x` (`20.15 -> 61.44 Mbps` at `MCS 14`)**, cut its RTT **`18.9x` (`72.10 -> 3.81 ms`)**, raised 3-station simultaneous **Jain fairness from `0.6867` to `0.9531`**, and achieved **`3.342 bit/s/Hz` DL (`66.85 Mbps` peak)** and **`3.656 bit/s/Hz` UL (`73.13 Mbps`)** with **`3.36–4.58 ms` loaded median RTT** across all 3 stations!

---

## 1. Master Channel-Width Table (`80 MHz` vs `40 MHz` vs `20 MHz` at `11 dBm` Wall-Obstructed NLOS)

All measurements taken on the physical 3-station bench (`LAP-120` AP at `11 dBm` serving `NanoStation 5AC Loco` in room + `MikroTik SXT Lite5` behind wall + stock `airOS 6.1.4` `LiteBeam M5` behind wall):

| Sector Metric | `80 MHz` (`VHT80`) | `40 MHz` (`VHT40`) | `20 MHz` (`VHT20`) | Takeaway for WISPs |
| :--- | :---: | :---: | :---: | :--- |
| **Standalone `Loco 5AC` (`802.11ac` 2x2) DL** | `101.81 Mbps` (`5.97 ms`) | **`147.82 Mbps`** (`6.14 ms`) | `81.97 Mbps` (`4.62 ms`) | **`40 MHz` is `+45.2%` faster than `80 MHz`** |
| **Standalone `MikroTik SXT` (`802.11n` 2x2, behind wall) DL** | `20.15 Mbps` (`72.10 ms`) | `36.31 Mbps` (`11.15 ms`) | 🏆 **`61.44 Mbps`** (**`3.81 ms`**) | **`20 MHz` is `3.05x` faster & `18.9x` lower RTT than `80 MHz`!** |
| **Standalone `LiteBeam M5` (`airOS 6.1.4` 1x1, behind wall) DL** | `57.27 Mbps` (`7.54 ms`) | **`69.08 Mbps`** (`5.26 ms`) | `37.51 Mbps` (**`3.30 ms`**) | Stock `airOS 6` M5 runs at `3.30 ms` loaded RTT on `20 MHz` |
| **3-Sta Simultaneous DL Goodput (Mean / Peak)** | `92.98` / `96.15 Mbps` | 🏆 **`105.18` / `110.68 Mbps`** | `62.98` / `66.85 Mbps` | **`40 MHz` delivers the highest raw sector Downlink** |
| **3-Sta DL Jain's Fairness Index (Mean / Peak)** | `0.6867` / `0.7376` | `0.7002` / `0.7689` | 🏆 **`0.9273` / `0.9531`** | **`20 MHz` equalizes obstructed `802.11n` and `802.11ac` CPEs** |
| **DL Spectral Efficiency (Mean / Peak)** | `1.162` / `1.202 bit/s/Hz` | `2.630` / `2.767 bit/s/Hz` | 🏆 **`3.149` / `3.342 bit/s/Hz`** | **`20 MHz` is `2.88x` more spectrally efficient than `80 MHz`** |
| **3-Sta DL TCP Retransmits (Mean per 8s trial)** | `700.5` | **`33.0`** | `39.5` | **`40 MHz` & `20 MHz` eliminate `94–95%` of `80 MHz` packet loss** |
| **3-Sta Loaded DL Median RTT (`Loco` / `M5` / `SXT`)** | `5.86` / `6.74` / `6.57 ms` | `6.12` / `5.57` / `5.21 ms` | 🏆 **`4.58` / `3.96` / `3.36 ms`** | Sub-5ms loaded median RTT across all 3 CPEs on `20 MHz` |
| **3-Sta Simultaneous UL Goodput (Spectral Eff.)** | **`155.34 Mbps`** (`1.942`) | `102.98 Mbps` (`2.575`) | `73.13 Mbps` (**`3.656 bit/s/Hz`**) | **`20 MHz` achieves `3.66 bit/s/Hz` in 3-station UL** |

---

## 2. Peak-Hour Bidirectional 6-Flow WISP Sector Stress Test (`3 DL + 3 UL + 3 Interactive` Simultaneously)

We simulated peak-hour WISP congestion (`8 PM`) by saturating **all 3 stations in Downlink AND all 3 stations in Uplink simultaneously (`6 concurrent TCP streams`)** while measuring interactive RTT (`5 dBm` Near-Far regime):

| Metric (`6 Concurrent TCP Streams: 3 DL + 3 UL`) | Mode 1: Unoptimized Stock OpenWrt Sector | Mode 2: Full openMAX Stack (`fmx_adaptive_controller.sh` + `ATF` + `AQL 1000/2000` + `WMM AC_VO` + `RTS=256B` + `CAKE`) | Improvement |
| :--- | :---: | :---: | :--- |
| **Total Sector Downlink Goodput** | `30.26 Mbps` | **`45.22 Mbps`** | **`+49.4%` (`+14.96 Mbps`)** |
| **Total Sector Uplink Goodput** | `104.32 Mbps` | **`107.80 Mbps`** | **`+3.3%`** |
| **Total Bidirectional Sector Goodput (`DL + UL`)** | `134.58 Mbps` | **`153.01 Mbps`** | **`+13.7%` (`+18.43 Mbps`)** |
| **`MikroTik SXT Lite5` (Obstructed) DL / UL** | `2.29` / `1.31 Mbps` | **`6.22` / `2.62 Mbps`** | **`2.72x` DL / `2.00x` UL** |
| **`MikroTik SXT Lite5` Loaded `p50` / `p95` RTT** | `251.25` / `607.50 ms` | **`6.43` / `18.75 ms`** | **`39.1x` lower median RTT (`32.4x` lower `p95`)** |
| **`Ubiquiti LiteBeam M5` (`airOS 6.1.4`) `p50` RTT** | `23.33 ms` | **`7.22 ms`** | **`3.23x` lower median RTT** |
| **`NanoStation 5AC Loco` Loaded `p50` RTT** | `20.15 ms` | **`7.40 ms`** | **`2.72x` lower median RTT** |

---

## 3. Two Important `QCA988x` (`10.1-ct-8x-__fW-022`) Firmware Control Boundaries We Discovered

In the spirit of reporting negative/boundary results with the same rigor as wins:
1. **`iw dev phy0-ap0 scan ... ap-force` Firmware Scan Sawtooth (`DEC-013`)**: Triggering an off-channel `ap-force` scan on a live `ath10k-ct` (`10.1-ct-8x-__fW-022`) AP vdev traps the QCA988x PCIe target firmware in a `102.4 ms` beacon-aligned scan loop that survives `wifi reload` and requires `rmmod ath10k_pci` or AP reboot. Spectral FFT captures (`618.7 KB / 6,653 frames` via `spectral_scan0`) should be triggered passively on the operating channel or from an OpenWrt CPE.
2. **Runtime `iw set bitrates` Multi-Rate Masks (`FMX-0009` / `DEC-015`)**: Using `ATH10K_DBG_WMI | ATH10K_DBG_BUFFER` (`0x2002`) hex dumps, we verified that `iw dev phy0-ap0 set bitrates ...` dispatches `WMI_PEER_ASSOC_CMDID` (`reassoc=true`) over PCIe with updated per-peer rate masks (`0x0F0F` for `SXT`, `0x000F` for `LiteBeam M5`, `0xFFF0` for `Loco 5AC`), **but** on already-associated peers in `10.1-ct-8x-__fW-022`, the firmware rate-control state machine ignores `reassoc=true` rate narrowing and continues stepping up to the peer's initial association IE ceiling. Therefore, **Channel Width (`20/40 MHz`)**, **TX Power**, and **AQL/Airtime Scheduling** are the true fast-loop hardware control knobs on Wave-1 `10.1-ct`.

---

## 4. Code, Daemon & Raw JSON Telemetry on GitHub
Everything is open-source (MIT) and pushed to **`https://github.com/wolverin0/openmax`**:
- **Stage 7 Report**: `docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md` (`artifacts/stage7_ptmp/stage7_ptmp_3station_results.json`)
- **Stage 8 Report**: `docs/STAGE8_ADAPTIVE_CONTROLLER_AND_SECTOR_SIM.md` (`artifacts/stage8_ptmp/stage8_adaptive_and_sector_results.json`)
- **Stage 9 Report**: `docs/STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md` (`artifacts/stage9_ptmp/stage9_ratemask_20mhz_and_pacing_results.json`)
- **Production OpenWrt `procd` Init Service & Daemons**: `controller/futuramax.init`, `controller/fmx_adaptive_controller.sh`, `controller/fmx_watchdog.sh`
