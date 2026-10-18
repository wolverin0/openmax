# Reddit Master Post (`r/wisp` / `r/Ubiquiti`) — Eye-Friendly WISP Edition + Technical Spoilers (Adversarially Audited)

> **How to use this file**: Copy everything below the line (`---`) and paste it into Reddit's **Markdown Editor**.
> - The main body is written in **plain WISP operator language** so anyone scrolling can see at a glance what we proved on the bench, what we uncovered inside the firmware, and where the project is going.
> - All deep technical details (incorporating corrections from our `gpt-6-astra` `xhigh` adversarial audit) are tucked inside Reddit **`>! Spoiler !<` blocks** plus direct links to the full engineering reports on GitHub.

---

**Title:** `OpenMAX / FuturaMAX: What we achieved on Ubiquiti airMAX AC & what we uncovered inside Rocket Prism + LTU (Zero-Reflash CPEs, Auto-Frequency, 4096-QAM & OFDMA Firmware Paths)`

Hey `r/wisp`,

Instead of dropping another giant wall of assembly and kernel logs, we put together a **clean, at-a-glance summary** of what we have built and bench-tested in the **OpenMAX / FuturaMAX** project (`https://github.com/wolverin0/openmax`), what our static firmware reverse-engineering just uncovered on **Rocket Prism** and **LTU**, and what is going on the physical test bench next.

If you just want the practical WISP takeaways, read the bullet points. If you want the deep reverse-engineering details (and the caveats our adversarial code audit caught), click the **Technical Spoiler** under each section or open the linked GitHub docs.

---

### 🎯 Our North Star (Why we are doing this)

Ubiquiti's `airMAX AC` (`LiteAP`, `Rocket Prism`, `LiteBeam`, `Loco 5AC`) and `LTU` hardware is physically much more capable than what the stock UI exposes — and WISPs still have tens of thousands of these radios deployed on towers and roofs.

Our goal is simple:
1. **Extract maximum real-world sector capacity, lower latency, and automatic interference avoidance** from the hardware we already own.
2. **Avoid truck rolls to reflash customer CPEs** when upgrading tower sectors.
3. **Audit and unlock hardware capabilities already present in the silicon/drivers** (like hybrid AP/CPE interop, active RF filtering, and LTU's `4096-QAM` & subband `OFDMA` code paths).

---

### ✅ Win #1 (Bench-Proven): Stock `airOS 8` Customer CPEs Connect to an OpenWrt AP (Zero Reflash)

* **What we achieved:** A customer CPE running official **stock `airOS 8` (`WA.v8.5.12` and `WA.v8.7.25`)** connects on our test bench to an **OpenWrt AP** (`LiteAP AC`) with `WPA2-CCMP` encryption and Layer-2 traffic forwarding.
* **Why it matters for WISPs:**
  * **Zero customer reflashing:** The customer radio stays on its official Ubiquiti firmware image (`mtd` flash partitions untouched).
  * **Keep your management stack:** The stock `airOS 8` WebUI and **UNMS / UISP** agent binary remain intact on the CPE.
  * **Real bench throughput:**
    * On a **`20 MHz`** channel (`WA.v8.7.25` `Loco 5AC` <-> OpenWrt `LAP-120`), we measured **`78.7 Mbps` sustained TCP upload (`93.2 Mbps` peak, `0` retransmits)** and **`63.6 Mbps` TCP download** at **`1.48 ms` RTT**.
    * On a **`40 MHz`** channel, we measured **`147 Mbps` TCP upload** on `WA.v8.5.12` and **`134 Mbps` plain / `120 Mbps` WPA2-CCMP** on `WA.v8.7.25`.
  * **Automatic fallback:** A boot/watchdog script can revert the CPE back to stock `airMAX` polling mode if it cannot reach the hybrid AP.

>! **Technical Spoiler (Audited):** Official `WA.v8.5.12` through `WA.v8.7.25` hide `ptpmode` in the WebUI, but `/sbin/ubntconf` still honors `wireless.1.ptpmode=disabled` and generates `/etc/crontabs/ubnt` from `cron.1.job.1.cmd` before `init` starts `crond`. A boot script patches 3 instructions (6 changed bytes) in a `/tmp` RAM copy of `/lib/modules/2.6.32.68/ubnt_poll_host.ko` (`file offsets 30784, 31816, 41976` on `8.7.25`) and sets `allow_80211=1`. **Adversarial Audit Catch (`F01`):** Because `ubnt_poll_host.ko` is a relocatable MIPS ELF (`ET_REL`), zeroing the `jal` at offset `30784` (`0x00000000`) without stripping its `R_MIPS_26` relocation entry causes the kernel module loader to write the low 26 target address bits into the instruction word; the production-hardened recipe must either neutralize the `.rel.text` entry or use a relocation-safe branch override (`0x10000001`).!<

📄 **Full Technical Doc:** [STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md) · [ADVERSARIAL_REVIEW_STAGE10_11.md](https://github.com/wolverin0/openmax/blob/main/docs/ADVERSARIAL_REVIEW_STAGE10_11.md)

---

### ✅ Win #2 (Bench-Proven): Decoupling the Proprietary Framing & Multi-MHz Channel Agility (`10 / 20 / 40 / 80 MHz`)

* **What we achieved:** We mapped and bridged the exact frame encapsulation difference between stock `airOS 8` CPEs (`ETH_P_TEB` `0x6558`) and open `mac80211` APs.
* **Why it matters for WISPs:**
  * **Gradual sector migrations:** Instead of climbing 30 roofs on the same day you swap a tower AP to an OpenMAX/OpenWrt sector, existing `5AC` CPEs can associate over standard `20 / 40 / 80 MHz` VHT channels.
  * **Narrow-channel options:** When both ends run the open stack, `5 MHz` and `10 MHz` narrow channels are also available for high-noise links.

>! **Technical Spoiler (Audited):** When a stock `airOS 8` CPE runs with `ptpmode=disabled` (`wds=disabled`), it encapsulates outbound data frames with a 14-byte outer Ethernet header carrying EtherType `0x6558` (`ETH_P_TEB`). On our OpenWrt AP (`mac80211.ko`), a lightweight 21-instruction RX hook checks `skb->protocol == htons(0x6558)` and strips the 14-byte outer header so inner Ethernet frames bridge cleanly. (Note: third-party APs without this `0x6558` decapsulation hook or 4-address WDS parity require a separate bridge helper).!<

📄 **Full Technical Doc:** [STAGE6_HYBRID_POLL_HOST_BYPASS.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE6_HYBRID_POLL_HOST_BYPASS.md) · [STAGE9_HYBRID_80211_BENCH_TRUTH.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE9_HYBRID_80211_BENCH_TRUTH.md)

---

### ✅ Win #3 (Bench-Proven): Automatic Clean-Frequency Scoring & Smart Per-Client Queueing (Fixing Loaded Latency)

* **What we achieved:** Our external **OpenMAX Controller** works on **both untouched stock `airOS 8` sectors and OpenWrt sectors** to score spectrum cleanliness and shape traffic per subscriber based on real-time link quality.
* **Why it matters for WISPs:**
  * **Stops one weak client from ruining sector ping:** By combining core `CAKE` / `FQ-CoDel` pacing with `mac80211` `AQL` airtime limits, loaded ping under saturation dropped on our bench from `40–90 ms` down to **`~6–9 ms`**.
  * **Continuous background FFT scanning:** On OpenWrt (`ath10k-ct`), the main radio captures 56-bin FFT spectrum sweeps in the background without dropping the link.

>! **Technical Spoiler:** On OpenWrt (`ath10k-ct`), we combine background debugfs `spectral_scan_ctl` FFT sweeps with `mac80211` `TXQ` + `AQL` (`aql_txq_limit = 1500/2500 us`). On untouched stock `airOS 8` sectors, the controller polls `status.cgi` / `brmacs` / `airview` over SSH and dynamically adjusts upstream `CAKE` bandwidth tinning per CPE.!<

📄 **Full Technical Doc:** [STAGE1_CONTROLLER.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE1_CONTROLLER.md) · [STAGE2_3_ATH10K_LAB.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE2_3_ATH10K_LAB.md) · [STAGE4_CUSTOM_MAC_GATE.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE4_CUSTOM_MAC_GATE.md)

---

### 🔬 Win #4 (Firmware RE Discovery — Next on Bench): `Rocket Prism 5AC Gen2` & How **AirPrism** Hardware Filtering Works

* **What we uncovered:** We unpacked `XC.v8.7.25` to see how `Rocket Prism 5AC Gen2` (`0xe7e7`/`0xe7e9`) and `PrismStation 5AC` (`0xe7e6`/`0xe7e8`) control their **2nd radio (`wifi1`)** and their **AirPrism active RF filter** when changing channels.
* **Why it matters for WISPs:**
  * Putting generic third-party firmware on a `Rocket Prism` without driving its RF filter hardware risks leaving the filter bank in the wrong band state.
  * Our static disassembly found two concrete things:
    1. **Stock `XC.v8.7.25` `ubnt_poll_host.ko` has 100% instruction parity with `WA.v8.7.25`** around all 3 hybrid patch sites — meaning we can test hybrid mode on stock `XC` while keeping Ubiquiti's native `umac.ko` / `ath_dev.ko` filter tuning intact.
    2. **We extracted the exact Stage-1/Stage-2 GPIO band-edge filter selector (`GPIO 13..16`) and spectral-filter interrupt (`GPIO 21` / `IRQ 64`)** from `umac.ko` and `ath_dev.ko`.

>! **Technical Spoiler (Audited):** In `XC.v8.7.25`: (1) `umac.ko:ubnt_prism_hook` (`.text+0xac874`) checks both the **lower and upper channel edges** (`center ± width/2`) and `width <= max_width` against a **6-entry (44 bytes/entry)** band table to drive Stage-1 (`GPIO 15, 16`) and Stage-2 (`GPIO 13, 14`) via `gpio_line_set`; (2) `ubnthal.ko` (`.data+0x570`, 12,000-byte board records, 3,780-byte radio stride) sets both `prism` (bit 30) and `hsr` (bit 28, `hsr_param=31`) on `RP-5AC-Gen2` (`0xe7e7`/`0xe7e9`) and `PS-5AC` (`0xe7e6`/`0xe7e8`), queried at `umac.ko:.text+0xbbf64`; and (3) `ath_dev.ko:ath_spectral_filter_init` (`.text+0x27c00`) hooks `GPIO 21` (`IRQ 64`, `ath-spectral-filter`). Completing the full `hsr` parameter consumer call chain and live bench verification is our next step.!<

📄 **Full Technical Doc:** [STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md) · [ADVERSARIAL_REVIEW_STAGE10_11.md](https://github.com/wolverin0/openmax/blob/main/docs/ADVERSARIAL_REVIEW_STAGE10_11.md)

---

### 🚀 Win #5 (Firmware RE Discovery — Next on Bench): Ubiquiti **LTU** (`v2.4.2`) — Inside the "Abandoned" **`4096-QAM` (`12X`)** & Hidden **`OFDMA`** Code Paths

* **What we uncovered:** For years, WISP operators have seen the greyed-out **`4096-QAM` (`12X`)** option on `LTU` PtMP sectors. We unpacked `LTU-Rocket` (`aflturocket-2.4.2`) and `LTU-Lite/LR/Pro` (`afltu-2.4.2`) to see if `4096-QAM` was just a fake UI button or if real driver code exists underneath.
* **What we found inside the firmware binaries:**
  * **`4096-QAM` (`12X`) has real driver, rate-table, and RF routines compiled into `v2.4.2`:** It is not just a label in the web page. The config parser (`/sbin/ubntconf`), the PtMP downlink ceiling function (`AME_Scheduler_AutoMCS_GetPtmpDLCeiling`), the MIMO rate tables (`autoMcsOthersTbl`), and the RF setup routine (`bbp_rf_set_super4096`) all contain explicit code paths for internal rate **`31` (`0x1f`, `4096-QAM LDPC 5/6`)**.
  * **Hardware/driver guards we still need to test on the bench:** Our adversarial audit also found a hardware capability check (`ame_check_hw_NoLDPC` inside `ame_bbp_set_Param_mcs`), plus separate CPE `ame_core.ko` builds and an **Intel Arria 10 SoC FPGA** companion processor on `LTU-Rocket` — so live RF bench testing is required to see if `4096-QAM` actually modulates on-air in PtMP mode or hits a hardware/FPGA guard.
  * **Hidden Subband `OFDMA` hooks:** We also discovered `radio.1.ofdma_mode` (`sched_ofdma_available`, `ame_check_hw_NoOFDMA`) and an 8-bit subband register mask (`ofdma_subbands`) inside `ame_core.ko` / `ame_dev.ko`.

>! **Technical Spoiler (Audited):** `LTU` runs on an `amesoc3` Dual Cortex-A9 + Analog Devices **`AD9361` 2x2 agile SDR transceiver** (`40 MHz` SPI bus in DTB, independent TX/RX LO synthesizers — which is why LTU supports split TX!=RX frequencies and custom channel widths that fixed `802.11ac` `QCA988x` silicon cannot do), plus an **Intel Arria 10 SoC FPGA** (`altr,socfpga-arria10`, dual Cortex-A9 + 128 MB RAM + `5.49 MB` `.rbf` bitstream) on `LTU-Rocket`. In `ubntbox` (`VA 0xd4b28`), `wireless.1.rate.mcs=0..5` maps directly to LDPC rate codes `[7, 11, 15, 19, 23, 31]` (`QPSK` through `4096-QAM`). And in `ame_dev.ko:ofdma_subbands_store` (`.text+0x1154c`), the sysfs handler parses a **numeric byte (`0..255` / `0x00..0xff` via `simple_strtol(..., 0)`)**, NOT a binary string (passing `"11111111"` parses as decimal `11,111,111` -> `0xc7`!), writing bits `12..19` of the BBP MRX register.!<

📄 **Full Technical Doc:** [STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md) · [ADVERSARIAL_REVIEW_STAGE10_11.md](https://github.com/wolverin0/openmax/blob/main/docs/ADVERSARIAL_REVIEW_STAGE10_11.md)

---

### 🧭 Where We Are Heading Next (Bench Proven vs Next on Bench)

We strictly separate **what is already measured on physical radios** from **what static reverse-engineering uncovered for our next bench tests**:

| Milestone | Status | Summary |
| :--- | :--- | :--- |
| **Stock `airOS 8` (`v8.5.12–v8.7.25`) + OpenWrt AP Interop** | ✅ **Proven on Bench** (`Stage 10`) | `78.7 Mbps` UL / `63.6 Mbps` DL in `20 MHz` (`147 Mbps` in `40 MHz`), `1.48 ms` RTT, zero CPE flash modification. Next: hardening the `R_MIPS_26` relocation-safe patch & full L2 frame matrix. |
| **Smart Per-CPE Airtime Pacing & Continuous FFT Scanner** | ✅ **Proven on Bench** (`Stages 1–4`) | Cuts loaded PtMP ping spikes from `40–90 ms` down to `~6–9 ms` while maintaining sector throughput. |
| **`Rocket Prism 5AC Gen2` Bench Validation** | 🔜 **Next on Bench** (`Stage 11A`) | Connecting a physical `Rocket Prism 5AC Gen2` on the bench to trace the remaining `hsr_param=31` consumer path and measure AirPrism adjacent-channel rejection. |
| **`LTU` Live RF Test of `4096-QAM` (`12X`) & `OFDMA` Hooks** | 🔜 **Next on Bench** (`Stage 11B`) | Testing `autoMcsCeiling=31`, `adj_mcs`, and `ofdma_subbands=0xff` on a physical LTU bench link to verify whether `ame_check_hw_NoLDPC` / FPGA bitstreams allow `4096-QAM` on air. |

---

### 🔗 All Documentation & Open Repository

Everything — including our independent **Adversarial Engineering Audit** (`gpt-6-astra` `xhigh`) that stress-tested every binary offset and claim — is in our GitHub repository:
* **Main Repository:** [github.com/wolverin0/openmax](https://github.com/wolverin0/openmax)
* **Independent Adversarial Audit (`Stages 10 & 11`):** [docs/ADVERSARIAL_REVIEW_STAGE10_11.md](https://github.com/wolverin0/openmax/blob/main/docs/ADVERSARIAL_REVIEW_STAGE10_11.md)
* **Stock `airOS 8` Zero-Reflash Interop (`Stage 10`):** [docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md)
* **`Rocket Prism 5AC Gen2` & AirPrism RE (`Stage 11A`):** [docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md)
* **`LTU` `4096-QAM` (`12X`) & `OFDMA` RE (`Stage 11B`):** [docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md](https://github.com/wolverin0/openmax/blob/main/docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md)
* **Full Research Ledger (`FMX-0001` to `FMX-0017`):** [docs/RESEARCH_LEDGER.md](https://github.com/wolverin0/openmax/blob/main/docs/RESEARCH_LEDGER.md)

Happy to answer any questions from fellow WISPs!
