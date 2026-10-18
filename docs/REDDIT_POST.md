# openMAX Master Reddit Post (Consolidated Highlight Snippets + GitHub Deep-Dive Links)

> **Ready to copy-paste into Reddit (`r/wisp`, `r/openwrt`, `r/ubiquiti`, `r/networking`).**  
> Uses standard Reddit Markdown (`[Text](URL)`) so the post stays short and readable while linking every claim directly to the full technical documentation and raw JSON benchmarks on GitHub.

---

## Suggested Title
**openMAX: What we found reverse-engineering & benchmarking Ubiquiti airMAX AC (WA/XC) and LTU firmware (Stock airOS 8 <-> OpenWrt live interop, 21x latency cuts, AirPrism hardware filters, and why LTU 4096-QAM has been greyed out for 5 years)**

---

## Post Body (Copy-Paste in Reddit Markdown Mode)

Hey everyone,

I run a small fixed-wireless ISP (`Punto Futura`) with ~640 deployed Ubiquiti radios (`airMAX AC` `WA`/`XC`, legacy `M5`, and `LTU`). Over the past few weeks, working alongside AI research agents on a physical lab bench, we built an open-source research project (**[openMAX on GitHub](https://github.com/wolverin0/openmax)**) to find out how much real-world performance, multi-vendor interoperability, and hidden hardware functionality is locked inside Ubiquiti's existing silicon.

Instead of dropping a 10,000-word wall of assembly dumps and benchmark tables here, below are the **short highlight snippets grouped by hardware/technology**, with direct links to each full technical report in our GitHub repo:

---

### 1. Stock `airOS 8` (`v8.5.12` – `v8.7.25`) $\leftrightarrow$ OpenWrt AP Live Interoperability (Zero Truck-Rolls)
* **What we solved (Tested on Bench):** Normally, a stock `airOS 8` (`5AC`) CPE refuses to connect to a standard OpenWrt `802.11ac` AP—or disconnects after exactly 30 seconds and drops all Layer-2 traffic. We traced and solved all **4 independent locks**:
  1. `ubnt_poll_host_is_ap_valid` vendor-IE check in `ubnt_poll_host.ko`.
  2. The 30-second missing-TDMA-poll watchdog reset timer in `ubnt_poll_host.ko`.
  3. `/bin/wpa_supplicant` ignoring standard `802.11ac` `WPA2-PSK` scan results unless `allow_80211=1` is injected.
  4. `QCA988x` radio firmware wrapping every data packet in RFC 1701 Transparent Ethernet Bridging (`ETH_P_TEB` `0x6558` + 14-byte inner Ethernet header), which we decapsulate at line rate with a 21-instruction hook in OpenWrt's `mac80211.ko`.
* **Zero-Truck-Roll Migration (`system.cfg` `cron` Persistence):** Standard `airOS 8` runs `/sbin/uav` at boot to delete custom scripts in `/etc/persistent/`. We built a self-contained `cron.1.job.1.cmd` one-liner in `system.cfg` that survives `/sbin/uav` and reboots on official `v8.7.25`: the CPE stays connected to a stock `airMAX` AP, automatically unlocks itself into standard `802.11ac` when the AP switches to OpenWrt, and automatically reverts if the AP rolls back to stock `airOS`.
* **Bench Result (`WA.v8.7.25` `Loco 5AC` $\leftrightarrow$ OpenWrt `LAP-120` AP):**
  * **`20 MHz` (`VHT20`) + `WPA2-PSK`:** Associates at `173.3 MBit/s` (`VHT-MCS 8 SGI 2x2`), **`78.7 Mbps` TCP Uplink (`93.2 Mbps` peak, `0` retransmits = `3.94 bit/s/Hz`)**, **`63.6 Mbps` TCP Downlink (`74.2 Mbps` peak = `3.18 bit/s/Hz`)**, **`1.48 ms` RTT**.
  * **`80 MHz` (`VHT80`):** **`147.0 Mbps` TCP Uplink (`152 Mbps` peak)**, **`1.23 ms` RTT**, plus proven 1-command `mtd3` rollback from OpenWrt back to stock `airOS 8`.
* 📄 **Full Technical Doc & Offsets:** **[STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md)**

---

### 2. `airMAX AC` (`WA`: `LAP-120`, `LAP-GPS`, `LiteBeam 5AC Gen2`, `Loco 5AC`) — Multi-Vendor PtMP & Latency
* **Solved the 64 MB RAM OOM Crash & Hit the 535 MHz CPU Ceiling (Tested on Bench):** OpenWrt's default `vm.min_free_kbytes=8192` + `watermark_boost_factor=15000` causes OOM kills on 64 MB `WA` radios under 200 Mbps load. Fixing the VM watermarks (`2048`/`0`) + `AQL` (`2000/4000 µs`) + `CAKE` freed **`22.4 MB` RAM (`0` OOMs)** and pushed our `LAP-120` link to **`223.53 Mbps` UDP (`0.21%` loss) / `154.58 Mbps` TCP (`0` retransmits) at `1.35 ms p50 / 1.83 ms p95` loaded latency**.
  * 📄 **Doc:** **[UMAC_DATAPATH.md](https://github.com/wolverin0/openmax/blob/main/docs/UMAC_DATAPATH.md)** & **[CURRENT_STATE.md](https://github.com/wolverin0/openmax/blob/main/docs/CURRENT_STATE.md)**
* **3-Station Multi-Vendor & Mixed-Gen PtMP (`Ubiquiti 5AC` + `MikroTik SXT Lite5` + Stock `airOS 6` `LiteBeam M5`):**
  * **`WMM AC_VO` Deficit Bypass (`21x–45x` Latency Cut):** When a wall-obstructed client (`MikroTik SXT`) suffers rate fallback, `mac80211` drives its `BE` airtime deficit to `-67.1 ms` while `VO` stays at `+256 µs`. Routing interactive packets (`ICMP/DNS/NTP/VoIP`) to `DSCP EF` cut obstructed-client loaded RTT from **`143.0 ms` $\to$ `6.80 ms` (`21.0x` cut)** while boosting sector goodput **`+27.2%`**.
  * **3-Station Uplink `RTS/CTS = 256B` + `CoTSQ 128 KB`:** Boosted 3-station simultaneous Uplink to **`181.90 Mbps` (`+18.5%`)** and recovered the wall-starved `MikroTik SXT` by **`3.07x`**.
  * **Full Report:** **[STAGE7_MULTIVENDOR_PTMP_REPORT.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md)**
* **`80 MHz` vs `40 MHz` vs `20 MHz` Sector Physics & Zero-Fork Adaptive Controller (`<0.1%` CPU):**
  * Narrowing our mixed `AC + N` sector from `80 MHz` to `40 MHz` **increased** 3-station Downlink goodput by **`+13.1%` (`105.18 Mbps` mean / `110.68 Mbps` peak)** and cut TCP retransmits **`21.2x`**.
  * Narrowing to **`20 MHz` (`VHT20`)** made the obstructed `MikroTik SXT` **`3.05x` faster (`20.15` $\to$ `61.44 Mbps`)** with **`18.9x` lower RTT (`3.81 ms`)**, raised 3-station **Jain fairness from `0.6867` to `0.9531`**, and hit **`3.34 bit/s/Hz` DL / `3.66 bit/s/Hz` UL**.
  * 📄 **Full Reports:** **[STAGE8_ADAPTIVE_CONTROLLER_AND_SECTOR_SIM.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE8_ADAPTIVE_CONTROLLER_AND_SECTOR_SIM.md)** & **[STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md)**

---

### 3. `XC` Series (`Rocket Prism 5AC Gen2` & `PrismStation 5AC`) — AirPrism Hardware Reversal
* **What we discovered inside `XC-8.7.25` (Static RE complete, bench test next):**
  * **AirPrism is actually TWO separate hardware filter stages:**
    1. **Stage 1/2 Bandpass Bank (`ubnt_prism_hook` in `umac.ko`):** Driven by 4 host `QCA9558` GPIO pins (`GPIO 13, 14, 15, 16`) across a 6-entry frequency lookup table.
    2. **Stage 3 Tunable Active Filter ASIC (`hsr` — High-Selectivity Receiver):** Tuned dynamically over the shared `QCA9558` SPI bus (`0xbf000000` + `GPIO 11, 12, 17` with `hsr_param = 31` on `RP-5AC-Gen2` / `PS-5AC`), exposing live diagnostics at `/proc/sys/dev/uph_wifi0/hsr_status`.
  * **Surprise Board Finding (`PowerBeam 5AC ISO`):** Decompiling all 34 `XC` board definitions in `ubnthal.ko` revealed that `PowerBeam 5AC ISO` (`0xe835`) has **neither** `prism` nor `hsr` active filters (`radios=1`)—only `RP-5AC-Gen2` (`0xe7e9`), `PS-5AC` (`0xe7e8`), and `R5AC-PRISM` (`0xe7e5`) have both active filter stages (`caps = 0xfce00814`, `28 dBm` max TX power).
  * **Hardware TX-Blanking Wire on `wifi1` (`SPECTRAL-XMIT-FILTER GPIO`):** The dedicated 5 GHz AirView radio (`wifi1`, internal `QCA9558` AHB radio) has a physical GPIO interrupt that blanks FFT samples during the exact microseconds `wifi0` (`QCA9880`) transmits, so `wifi1` measures external interference without self-saturation.
  * **100% Unlock Parity:** `ubnt_poll_host.ko` in `XC-8.7.25` (`189,880 B`) has the **exact same 3 patch byte offsets (`30784`, `31816`, `41976`)** as `WA-8.7.25`, and setting `radio.1.polling=disabled` in AP mode keeps both AirPrism hardware stages and `wifi1` 100% natively active!
* 📄 **Full Technical Doc:** **[STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md)**

---

### 4. Ubiquiti `LTU` (`LTU-Rocket` / `LTU-Lite` `v2.4.2`) — Why `4096-QAM` (`12X`) Was Greyed Out for 5+ Years & Hidden `OFDMA`
* **What we discovered unpacking `aflturocket-2.4.2` & `afltu-2.4.2` (Static RE complete, bench test next):**
  * **Hardware Architecture:** Every LTU radio runs on Ubiquiti's custom `amesoc3` (dual-core ARM Cortex-A9, `Linux 3.14.65 PREEMPT RT`) paired with an **Analog Devices `AD9361` 2x2 agile SDR transceiver** (`ame_ad9361` on SPI0; dual independent TX/RX PLL synthesizers are how LTU does `Split-Frequency` `TX != RX`). On top of that, **`LTU-Rocket` (`aflturocket`) embeds a SECOND complete computer inside**: an **Intel/Altera Arria 10 SoC FPGA (`HPS`)** running its own `Linux 4.14.0 SMP` kernel + `5.49 MB` `.rbf` FPGA bitstream over an internal IPv6 bridge (`br2`, `fe80::a00:1ff:fe02:304%br2`).
  * **The "Abandoned `4096-QAM` (`12X`)" Mystery Solved:** For 5+ years, `12X (4096QAM)` has appeared in the LTU WebUI dropdown permanently greyed out. We found that **`4096-QAM` (internal rate index `31` / `0x1f`, `4096qam LDPC 5/6` MIMO 2x2) is 100% implemented** in the kernel driver (`ame_core.ko`), the `AD9361` RFIC (`bbp_rf_set_super4096`), the Auto-MCS tables (`startThrd_4096 = 97`, `stayThrd_4096 = 90`), and the **PtMP Downlink Scheduler (`AME_Scheduler_AutoMCS_GetPtmpDLCeiling`)**!
  * **How It Was Blocked & How to Unlock It:** It is blocked **only** in the WebUI JavaScript (`getAvailableDataRates(isPtmp)` sets `disabled: true`) and UISP Lua validator (`ltuWireless.lua`). The C binary `/sbin/ubntconf` **does not check `ptpmode`**: setting `wireless.1.rate.mcs=5` in `system.cfg` (or running `echo 31 > /sys/class/ame/ame_ctrl_dev/autoMcsCeiling` / `ame_adj.sh cpe_mcs <id> 4096l 0`) unlocks `4096-QAM` (`0x1f`) directly in PtMP mode!
  * **Hidden Capabilities Left Inside the LTU Firmware (Not in the WebUI):**
    * **Multi-Subband `OFDMA` (`2, 4, or 8 subbands`) + Interference Subband Notching:** `radio.1.ofdma_mode = 0..3` and `/sys/class/ame/ame_ctrl_dev/ofdma_subbands` (8-bit subband mask `"11111111"` to notch out narrowband noise inside a wide channel).
    * **Built-In Real-Time WebSocket TDMA Scheduler & Queue Visualizer:** Hidden inside `/lib/ame-debug/www/sched.html` and `ctrl.html` (powered by `/bin/ame-debug-sched`).
    * **Hidden Engineering Mode & Per-CPE Tuning:** `eng.mode.status=enabled` (`/usr/www/ameeng.cgi`), per-CPE uplink digital gain (`ame_adj.sh cpe_ul_dgain`), mixed-MCS queue portioning (`ame_adj.sh mix_mcs`), and automatic high-QAM TX power backoff (`radio.1.autopwr_backoff.status`).
* 📄 **Full Technical Doc & Portability Matrix (`LTU` $\to$ `airMAX AC`):** **[STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md)**

---

### 5. What We Are Testing Next on the Bench
1. **Bench `Rocket Prism 5AC Gen2` (`XC`) Bring-Up:** Testing hybrid `XC.v8.7.25` + OpenWrt interop with both hardware AirPrism stages (`prism` + `hsr`) and TX-blanked `wifi1` (`airview1`) active, and porting LTU's coordinated **Auto-Frequency (`Find My AP`)** to `airMAX AC` using `wifi1` continuous background scanning.
2. **Bench `LTU` `4096-QAM` (`12X`) & Hidden `OFDMA` Live RF Tests:** Measuring real-world CINR/EVM thresholds required to sustain rate `31` (`4096-QAM`) and testing subband interference notching (`ofdma_subbands`) on physical LTU hardware.
3. **External `ESP32-C5` (`5 GHz` Raw I/Q SDR Observer):** Using the newly discovered `ESP-SDR` / `ESPsoup` raw I/Q capture mode on dual-band `ESP32-C5` (`4.79–5.99 GHz`) as an independent out-of-band spectrum/envelope sniffer on the bench.

Everything (scripts, kernel patches, daemons, and raw JSON datasets) is MIT-licensed in the repo:  
👉 **[https://github.com/wolverin0/openmax](https://github.com/wolverin0/openmax)**

If anyone has tested `autoMcsCeiling = 31` or `ofdma_mode` on LTU links, or wants to collaborate on the `Rocket Prism` / `LTU` bench tests, let us know!
