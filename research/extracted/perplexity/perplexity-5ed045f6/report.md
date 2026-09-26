# FuturaMAX: Evidence-Based Limits and Opportunities on Ubiquiti airMAX AC (QCA988x) Hardware

## 1. Executive assessment

FuturaMAX asks whether existing Ubiquiti airMAX AC hardware (LiteAP GPS/LAP‑GPS, LiteBeam 5AC Gen2, NanoStation 5AC and Loco 5AC) can materially improve PtMP capacity, spectral efficiency, latency, fairness and stability using newer software, firmware and network‑wide algorithms, without changing PHY capabilities. The available evidence shows large, reproducible gains from modern Linux/mac80211 queueing (AQL, FQ‑CoDel, airtime fairness, above‑driver schedulers) on ath9k/ath10k‑class radios, but also clear structural limits imposed by Qualcomm and Ubiquiti firmware on QCA988x that likely prevent fully matching proprietary airMAX TDMA behavior for long‑range hidden‑node PtMP sectors.[^1][^2][^3][^4][^5]

The most robust improvements come from:
- Replacing unmanaged queues at multiple layers with integrated FQ‑CoDel and airtime‑aware scheduling directly in mac80211/driver.
- Applying Airtime Queue Limits (AQL) and fq_codel inside ath10k/ath10k‑ct to prevent firmware over‑buffering.
- Using above‑driver scheduling overlays (e.g., STPP/WL4) and hybrid TDMA/CSMA approaches (hMAC) that cooperate with, rather than replace, underlying CSMA/CA.

On adjacent hardware (ath9k and reference ath10k systems), these techniques achieve:
- 5× aggregate throughput gains in mixed‑rate, many‑station scenarios.
- Order‑of‑magnitude latency reductions under load.
- Well‑behaved fairness with one or more very slow stations present.[^6][^1]

On QCA988x specifically, OpenWrt and ath10k‑ct deployments confirm major latency improvements via AQL/FQ‑CoDel, but they usually fall short of vendor airMAX AC firmware in peak PtP throughput and PtMP long‑range behavior. Ubiquiti’s proprietary TDMA, GPS sync and a “custom IC” handle time‑slot allocation and hidden‑node avoidance at a layer inaccessible to OpenWrt, and no public work demonstrates open‑stack QCA988x matching airMAX TDMA in realistic WISP PtMP conditions.[^7][^8][^9][^10][^11][^12]

**High‑level conclusions for FuturaMAX:**
- **Latency and fairness improvements via Linux/mac80211/ath10k‑ct (AQL, fq_codel, smarter queueing): DEMONSTRATED on adjacent hardware and CONFIRMED on some QCA988x devices.**
- **Full airMAX‑class TDMA for PtMP on QCA988x with only open components: INFERRED unlikely, given firmware‑owned MAC, hidden queues, limited telemetry, and lack of scheduling hooks.**
- **Spectral efficiency and sector capacity gains are possible but are likely modest compared to the jump from FIFO to FQ‑CoDel/airtime fairness themselves, and will depend heavily on physical network design and above‑driver coordination rather than deep firmware changes.**


## 2. Hardware and software control‑boundary map

### 2.1 airMAX AC hardware family and RF/MAC composition

The target devices (LiteAP GPS/LAP‑GPS, LiteBeam 5AC Gen2, NanoStation 5AC, Loco 5AC) are based on Qualcomm Atheros 802.11ac “Wave 1” chipsets such as QCA988x/QCA9882, combined with MIPS‑class SoCs and, in some models, a distinct “airMAX engine” custom IC. Ubiquiti documentation for airMAX AC emphasizes that TDMA scheduling, QoS, and GPS‑based synchronization for multi‑AP coordination are handled by the proprietary airMAX engine and custom silicon, not by generic 802.11ac MAC.[^8][^11][^13][^14]

The core RF/MAC blocks in these devices are:
- **QCA988x/QCA9882 11ac 2×2 chipset:** Provides the physical layer (modulation, coding, beamforming where present), base 802.11 DCF/EDCA MAC, aggregation (A‑MPDU/A‑MSDU), and rate adaptation logic when used with standard firmware.[^15][^16]
- **Custom “airMAX engine” IC (airMAX AC models):** Advertised as implementing hardware‑accelerated TDMA, frame aggregation, priority handling and GPS‑driven time synchronization for PtP/PtMP, but with no public programming interface or open driver documentation.[^14][^8]

### 2.2 Firmware and driver layers (ath10k/ath10k‑ct)

On non‑Ubiquiti reference hardware, QCA988x uses an offloaded MAC/PHY design with:
- **Closed firmware blobs (firmware‑5.bin series):** Implement rate control, per‑station queues, aggregation, and transmit scheduling; Linux sends frames and metadata, firmware chooses aggregates and reports completions through HTT (Host Target Transport) and WMI (control) channels.[^16][^15]
- **ath10k driver (Linux/mac80211):** A softMAC driver that exposes a `cfg80211`/`mac80211` interface but ultimately relies on firmware for most MAC functions. ath10k provides TX queues to firmware, handles control messages, and surfaces limited statistics; it cannot fully inspect or manage per‑frame retries, queue depths or aggregation decisions.[^15][^16]
- **ath10k‑ct firmware and driver:** Candela Technologies’ fork that adds features (IBSS support, extra debug telemetry, special modes) and sometimes different buffering strategies; OpenWrt ships both CT and non‑CT variants for QCA988x.[^17][^18]

This architecture imposes hard boundaries:
- MAC scheduler, NAV, retry timing, detailed aggregation, and internal queues are **firmware‑owned**; driver sees only high‑level completions and limited aggregate stats.[^16][^15]
- Driver/mac80211 can:
  - Decide which frames to enqueue for which station/TID.
  - Apply airtime‑aware queue limits (AQL) to control how much data is “in flight” in firmware.
  - Use per‑station/TID hash queues with FQ‑CoDel to shape traffic before it enters firmware.[^2][^1]

### 2.3 Linux/mac80211 queueing and scheduling

The modern Linux Wi‑Fi stack integrates queue management directly into mac80211 and driver layers:
- **mac80211 TXQ and FQ‑MAC:** The airtime fairness paper introduced a new queueing structure that brings per‑TID/per‑station queues into mac80211, allowing FQ‑CoDel to operate on Wi‑Fi traffic before driver/firmware, and implementing a deficit‑based airtime scheduler (currently only fully implemented for ath9k).[^1]
- **Airtime fairness scheduler:** On ath9k, the kernel enforces per‑station airtime budgets so that one slow 1 Mbps station cannot consume most channel time; this is crucial for dense PtMP sectors.[^1]
- **Airtime Queue Limits (AQL):** For offloaded devices like ath10k, AQL limits the amount of in‑flight airtime the driver can hand to firmware, preventing enormous internal buffers from creating multi‑second latency; it works in tandem with driver‑level FQ‑CoDel.[^19][^7]

These mechanisms are implemented in:
- **mac80211 (Linux kernel):** Core TXQ, FQ‑CoDel integration and airtime accounting.[^1]
- **ath9k driver:** Full airtime fairness scheduler and integrated queueing.[^1]
- **ath10k/ath10k‑ct driver:** AQL and FQ‑CoDel integration for QCA988x, but missing the full airtime fairness scheduler used on ath9k due to lack of hooks.[^7][^1]

### 2.4 Higher‑layer overlays (STPP/WL4, hMAC, etc.)

Several projects implement advanced MAC‑like behavior entirely above existing drivers:
- **hMAC:** Hybrid TDMA/CSMA scheduler on ath9k that uses standard power‑save (PS) mechanisms to pause/unpause per‑link queues and schedule downlink transmissions in time slots, while leaving CSMA/CA active in hardware.[^20]
- **STPP/WL4:** Soft Scheduling via Token Passing (STPP) and WL4 system that implements a centralized or distributed overlay above drivers, coordinating who transmits when at millisecond timescales, without modifying Wi‑Fi firmware or drivers (only small mac80211 patches).[^21]

These overlays belong to an “external controller” layer: they control Linux/mac80211/driver behavior through timers and Netlink, but do not change the firmware or PHY behavior.[^20][^21]

### 2.5 Control boundary summary for FuturaMAX

For LiteAP GPS/LAP‑GPS, LiteBeam 5AC Gen2, NanoStation 5AC and Loco 5AC when flashed with OpenWrt:
- **Fully controllable:**
  - Linux userspace (controllers, schedulers, traffic engineering).
  - Linux qdisc (CAKE/fq_codel) for WAN/bridge points.
  - mac80211 TXQ and FQ‑CoDel configuration.
  - ath10k/ath10k‑ct driver code and configuration.
  - Firmware selection (CT vs non‑CT) but not contents.
- **Partly controllable:**
  - Airtime Queue Limits (AQL) thresholds.
  - Some rate‑control hints and aggregation thresholds (limited by firmware APIs).[^7][^15]
- **Not controllable (without NDA/closed tools):**
  - Internal firmware queues, per‑slot TDMA scheduling, GPS time alignment, and hidden‑node resolution logic in airMAX engine/custom IC.
  - Detailed TX completion timestamps and retry outcomes for each frame.
  - Hardware‑level ANI (adaptive noise immunity) tuning beyond exposed knobs.


## 3. The 20 strongest positive findings

This section lists the most compelling, reproducible results from literature and real‑world tests, each annotated with a conclusion label relevant to FuturaMAX.

### 3.1 Queueing and airtime fairness

1. **Integrated FQ‑CoDel + airtime fairness (FQ‑MAC) delivers 5× throughput and 10× lower latency in mixed‑rate Wi‑Fi.**
   - **Source:** “Ending the Anomaly: Achieving Low Latency and Airtime Fairness in WiFi” (USENIX ATC 2017).[^1]
   - **Setup:** AR9580/ath9k AP, 3 STAs (two fast, one slow), HT20 5 GHz; later extended to 30 STAs with one 1 Mbps node.[^1]
   - **Baseline:** Standard Linux qdisc (pfifo_fast) and unmanaged driver queues.
   - **Modification:** Integrated FQ‑CoDel into mac80211 and ath9k plus airtime fairness scheduler (FQ‑MAC).
   - **Result:** Throughput in a 30‑station scenario (1 slow, 29 fast) from 3.3 Mbps to 17.7 Mbps (5.4×); median latency reduced by roughly an order of magnitude; station performance depends primarily on number of active stations rather than single slow link.[^1]
   - **Stats:** Multiple 5‑minute runs, error bars, fairness indices; open source code and datasets published.[^1]
   - **Portability:** DEMONSTRATED on adjacent hardware (ath9k). Queueing structure is in mac80211 and partially used by ath10k; full airtime scheduler is blocked by missing hooks.

2. **FQ‑MAC stabilizes latency across a wide rate range (6–150 Mbps) with near‑constant ~20 ms under load.**
   - **Source:** CeroWrt blog “Finally… the real net‑next 4.8 fq_codel/airtime‑fair ath9k results.”[^6]
   - **Setup:** ath9k AP, ath10k clients, HT20 5 GHz; mixed rate tests from 6 to 150 Mbps; flent RRUL and RTT_fair.
   - **Baseline:** pfifo_fast; large queueing delays and unfairness.
   - **Modification:** FQ‑MAC + airtime fairness as per USENIX paper.
   - **Result:** Latency under load kept below ~20 ms median for all tested link rates; two clients share bandwidth almost perfectly.[^6]
   - **Portability:** DEMONSTRATED on adjacent hardware; points to realistic latency targets for QCA988x.

3. **AQL + FQ‑CoDel on ath10k‑ct reduces bufferbloat from multi‑second to sub‑60 ms on Ubiquiti APs.**
   - **Source:** OpenWrt thread “AQL and the ath10k is *lovely*”.[^7]
   - **Setup:** Ubiquiti UAP Mesh/Mesh Pro (ath10k QCA988x), OpenWrt master with ath10k‑ct‑smallbuffers, purposely bad ~12 Mbps Wi‑Fi link; flent RRUL tests.[^7]
   - **Baseline:** No AQL; ath10k firmware over‑buffers; ping under load spikes above 4 s and breaks routing.[^7]
   - **Modification:** Enable AQL and native FQ‑CoDel in ath10k‑ct.
   - **Result:** Latency under load is “well below 60 ms” with similar throughput; routing remains stable.[^7]
   - **Stats:** Before/after flent plots, multiple runs shared in thread.
   - **Portability:** CONFIRMED on target‑class hardware; directly applicable to FuturaMAX.

4. **AQL is integrated into modern OpenWrt and Linux for ath10k, with near‑zero CPU overhead.**
   - **Source:** OpenWrt discussions and Reddit threads explaining AQL.[^22][^19]
   - **Finding:** AQL is implemented in the driver and relies on airtime accounting to limit firmware queue depth; it is now available for ath10k‑ct and non‑CT in recent OpenWrt, and is reported to have minimal CPU impact.[^23][^7]
   - **Portability:** CONFIRMED available; major practical tool for FuturaMAX.

5. **Deficit‑based airtime fairness improves throughput fairness even with one very slow station present.**
   - **Source:** USENIX airtime fairness tests with 30 STAs and one forced 1 Mbps station.[^1]
   - **Finding:** With FQ‑MAC and airtime fairness, aggregate throughput is 5.4× higher, and each station’s performance depends mainly on number of active stations; the 1 Mbps station no longer drags everyone down.
   - **Portability:** DEMONSTRATED on adjacent hardware; conceptually relevant but blocked by missing hooks on ath10k.

### 3.2 Hybrid MAC overlays and TDMA‑like systems

6. **hMAC’s hybrid TDMA/CSMA doubles aggregate throughput vs classical TDMA in hidden‑node scenarios.**
   - **Source:** “hMAC: Enabling Hybrid TDMA/CSMA on IEEE 802.11 Hardware”.[^20]
   - **Setup:** 2 APs + 3 STAs built on ath9k hardware; APs wired and PTP‑synchronized; hidden‑node scenario where STA2 is hidden from AP2 but interferes with STA1.[^20]
   - **Baseline:** 802.11 DCF (hidden STA2 starves). Classical TDMA per‑node scheduling severely restricts STA3.
   - **Modification:** hMAC’s per‑link TDMA scheduling using ath9k power‑save queues; CSMA/CA remains active.
   - **Result:** Aggregate downlink throughput increases from ~4.2 Mbps (classical TDMA) to ~8.8 Mbps with hMAC; hidden node STA2 gets stable throughput while STA3 retains most of its capacity.[^20]
   - **Portability:** DEMONSTRATED on adjacent hardware; conceptually shows benefit of per‑link scheduling, but implementation is tied to ath9k PS queues.

7. **hMAC works with unmodified clients and commodity NICs.**
   - **Finding:** hMAC operates only on the AP side; STAs remain standard 802.11 clients; CSMA/CA is left intact at hardware level to preserve interoperability.[^20]
   - **Portability:** DEMONSTRATED on adjacent hardware; suggests that some scheduling gains are possible without modifying CPE firmware.

8. **STPP/WL4 above‑driver scheduler reduces local‑link latency over Wi‑Fi by up to 40% with modest throughput cost.**
   - **Source:** “If you can’t beat them, augment them” (ICNP 2019).[^21]
   - **Setup:** 5‑node testbed with commodity Wi‑Fi NICs, Linux kernel patched with STPP macros and WL4 controller; multiple local links in same collision domain.[^21]
   - **Baseline:** Plain DCF/EDCA.
   - **Modification:** Token‑passing overlay that controls when each node transmits at millisecond timescales without driver/firmware changes.[^21]
   - **Result:** Local‑link latency improved by 40%; average network latency improved by 38%; throughput loss ≤9% on tested scenarios.[^21]
   - **Portability:** DEMONSTRATED on adjacent hardware; design is hardware‑agnostic, thus likely portable to QCA988x with appropriate kernel patches.

9. **STPP/WL4 uses only ~300 LoC of mac80211 changes and user‑space controller.**
   - **Finding:** Minimal kernel changes (307 lines) plus user‑space Click/Python controller implement STPP; rest is generic infrastructure.[^21]
   - **Portability:** DEMONSTRATED on adjacent hardware; low barrier to trial on FuturaMAX.

10. **OpenTDMF and related TDMA architectures show 30%+ throughput gains in controlled lab setups.**
   - **Source:** “Enabling TDMA for Today’s Wireless LANs” and references cited by hMAC/STPP.[^24][^20]
   - **Finding:** TDMA frameworks like OpenTDMF on 802.11 hardware can achieve substantial throughput and fairness gains versus plain DCF in controlled topologies, but require heavy driver/firmware cooperation and often modified clients.
   - **Portability:** DEMONSTRATED on adjacent hardware; direct application to offloaded QCA988x is difficult.

### 3.3 ath10k behavior and improvements

11. **Early FQ‑CoDel integration into ath10k demonstrated clean 6 Mbps throughput with <20 ms latency on problematic link.**
   - **Source:** CeroWrt “FQ_codel on ath10k”.[^2]
   - **Setup:** ath10k AP, 4 upload streams over problematic link; flent RTT_fair tests.
   - **Baseline:** Standard ath10k driver (no FQ‑CoDel), showing high latency and jitter.
   - **Modification:** Prototype FQ‑CoDel in ath10k driver.
   - **Result:** 6 Mbps of “clean throughput” with latency below 20 ms across 4 flows; fairness still imperfect but bufferbloat largely gone.[^2]
   - **Portability:** DEMONSTRATED on adjacent hardware; later generalized via AQL and FQ‑CoDel in mainstream ath10k.

12. **Analyzing ath10k’s baseline behavior reveals up to 2.5 s latency spikes and unstable queues.**
   - **Source:** CeroWrt “Analyzing ath10k’s current behavior”.[^4]
   - **Finding:** ath10k devices, including QCA988x, can exhibit up to 2.5 s of latency under load due to large, unmanaged buffers and firmware queueing; similar behavior observed on other consumer APs.
   - **Portability:** DEMONSTRATED on adjacent hardware; motivates AQL/FQ‑CoDel for FuturaMAX.

13. **OpenWrt on NanoStation 5AC Loco provides ~300 Mbps TCP in 80 MHz “normal Wi‑Fi” mode.**
   - **Source:** OpenWrt forum discussion on OpenWrt on Ubiquiti airMAX devices.[^25]
   - **Setup:** Ubiquiti NS5AC Loco with OpenWrt, 80 MHz 5 GHz link to 2×2 client (phone), iperf3 tests.
   - **Finding:** User reports ~300 Mbps TCP throughput in normal 802.11ac mode without airMAX TDMA.[^25]
   - **Portability:** CONFIRMED on target hardware; establishes an open‑stack PtP baseline.

14. **ath10k‑ct firmware and driver are well supported in OpenWrt, enabling IBSS and extra debug knobs.**
   - **Source:** CandelaTech user guide and OpenWrt package docs.[^18][^17]
   - **Finding:** CT firmware enables additional features (IBSS, special modes) and is widely used for QCA988x devices; includes debug options and some queue control flags.
   - **Portability:** CONFIRMED; provides an experimental platform for FuturaMAX.

15. **OpenWrt AQL explanations emphasize that AQL runs in the driver, not as heavy qdisc logic, and scales well.**
   - **Source:** OpenWrt/Reddit discussions on AQL.[^22][^23][^7]
   - **Finding:** AQL is described as a driver‑level extension with minimal CPU cost, suitable for embedded platforms and high client counts.
   - **Portability:** CONFIRMED; key building block for FuturaMAX sectors.

### 3.4 airMAX TDMA and proprietary features

16. **airMAX TDMA eliminates client contention on the air and reallocates unused slots, improving hidden‑node behavior and noise immunity.**
   - **Source:** Ubiquiti airMAX TDMA datasheet and training guides.[^26][^27][^8]
   - **Finding:** airMAX AP divides airtime into slots assigned to each CPE; unused slots are reassigned to active clients; TDMA and GPS produce “collision‑free” scheduling for PtMP, mitigating hidden‑node issues and improving spectral efficiency.
   - **Evidence quality:** Vendor documentation and large WISP deployments; no detailed public lab measurements.
   - **Portability:** DEMONSTRATED on proprietary adjacent MAC; no open implementation.

17. **airMAX AC products reach 450–500+ Mbps TCP throughput with 80 MHz channels, 2×2 MIMO and airMAX AC MAC.**
   - **Source:** Ubiquiti datasheets (e.g., Rocket 5AC Lite, LiteBeam 5AC).
   - **Finding:** Data sheets claim TCP throughput >500 Mbps for airMAX AC Point‑to‑Point links, leveraging 256‑QAM 2×2 MIMO and custom MAC/IC.[^11][^14]
   - **Portability:** DEMONSTRATED on target RF, but proprietary MAC.

### 3.5 General insights and reproducibility

18. **The Wi‑Fi queueing and airtime fairness work provides public code, data and scripts (flent, etc.), enabling straightforward reproduction.**
   - **Source:** USENIX paper online appendix and associated code repository.[^1]
   - **Finding:** Datasets and scripts for key experiments (throughput, latency, fairness, VoIP, web browsing) are public, providing a strong methodological basis for FuturaMAX experiments.

19. **Flent RRUL and related tests are established tools for evaluating Wi‑Fi latency under load.**
   - **Source:** Flent documentation and network testing blogs.[^28][^29][^30]
   - **Finding:** RRUL uses ping and UDP RTT together with multiple TCP flows to measure latency, throughput and queuing effects; recommended by bufferbloat researchers and implemented in multiple guides.

20. **Linux/open‑source community has converged on FQ‑CoDel/CAKE + airtime fairness as the default approach for Wi‑Fi latency and fairness.**
   - **Source:** LWN’s “Making WiFi fast”, OpenWrt bufferbloat discussions, and kernel documentation.[^31][^32]
   - **Finding:** These mechanisms are mainstream, relatively stable, and have broad support, making them safe bets for FuturaMAX rather than experimental one‑offs.


## 4. The 20 strongest blockers or negative findings

1. **Firmware‑owned MAC and hidden queues in ath10k restrict host‑side control.**
   - **Source:** ath10k documentation and analysis.[^15][^16]
   - **Finding:** Firmware implements deeper MAC queues, aggregation and rate/retry control; host can only influence these indirectly. Telemetry is limited and does not expose per‑frame completion timing or per‑queue occupancy.
   - **Consequence:** Strong blocker for implementing tight TDMA or per‑slot rate control on QCA988x.

2. **ath10k lacks the airtime fairness scheduler hooks present in ath9k.**
   - **Source:** USENIX airtime fairness paper and kernel discussions.[^1]
   - **Finding:** The airtime scheduler is implemented for ath9k; ath10k is explicitly listed as lacking required scheduling hooks; enabling identical logic would require new driver/firmware interfaces.

3. **Baseline ath10k exhibits multi‑second latency spikes and unstable queuing under load.**
   - **Source:** “Analyzing ath10k’s current behavior” blog.[^4]
   - **Finding:** On multiple chipsets including QCA988x, ath10k without AQL/FQ‑CoDel showed 2.5 s latency under load and erratic behavior, similar to other consumer APs.

4. **OpenWrt on QCA9888 11ac module maxes out at ~130–210 Mbps vs OEM’s ~320–340 Mbps.**
   - **Source:** OpenWrt archived thread “Openwrt build: low bandwidth on 11ac radio module”.[^9]
   - **Finding:** QCA9888 module hits ~320–340 Mbps under OEM firmware, but only 130–210 Mbps with OpenWrt and ath10k; tuning attempts (HT/VHT, channels) did not fully close the gap.

5. **WS‑AP3825i (QCA988x) on OpenWrt 23.05.3 caps around 460 Mbps even with strong client.**
   - **Source:** OpenWrt forum “WS‑AP3825i 5GHz Throughput Limitation on OpenWrt 23.05.3”.[^10]
   - **Finding:** With 80 MHz and an iPhone 15 Pro, iperf3 tests yield ~460 Mbps despite high link rates; wired tests show higher throughput, indicating a Wi‑Fi path bottleneck.

6. **airOS/airMAX has long‑distance optimizations not reproduced in OpenWrt.**
   - **Source:** “Long distance link optimization” discussion.[^12]
   - **Finding:** Users attribute better long‑distance behavior in airOS to proprietary optimizations (ACK timing, contention windows, frame size) that OpenWrt does not replicate.

7. **airMAX TDMA and custom IC behavior is proprietary and undocumented.**
   - **Source:** airMAX datasheets and training guides.[^8][^26][^14]
   - **Finding:** Ubiquiti describes TDMA and GPS sync behavior in high‑level terms; internal registers and control APIs are not public.

8. **hMAC’s slot timing is limited by non‑deterministic user‑space scheduling, requiring coarse slots and guard times.**
   - **Source:** hMAC paper.[^20]
   - **Finding:** On loaded CPUs, Netlink and timer jitter cause slot drift; reliable scheduling requires relatively large slots with guard intervals, reducing TDMA “sharpness”.

9. **hMAC only addresses downlink, and assumes wired PTP synchronization between APs.**
   - **Source:** hMAC paper.[^20]
   - **Finding:** hMAC is designed for enterprise APs with wired coordination; it does not manage uplink scheduling or full WISP PtMP scenarios.

10. **OpenTDMF and similar TDMA frameworks require deep kernel/driver changes and often modified clients.**
   - **Source:** OpenTDMF paper and hMAC references.[^24][^21][^20]
   - **Finding:** These systems manipulate hardware‑specific HCF registers and rely on precise timing and known client behavior; unsuitable for large heterogeneous deployments.

11. **STPP/WL4’s benefits diminish as node count increases; at scale, behavior approaches DCF.**
   - **Source:** STPP/WL4 paper.[^21]
   - **Finding:** The soft scheduling overlay shows largest gains for small clusters (2–10 nodes); beyond that, token passing and overhead limit improvement.

12. **OpenWrt users often report lower 5 GHz coverage/throughput or instability on ath10k vs OEM firmware.**
   - **Source:** Multiple forum threads and bug reports.[^33][^34][^35][^36]
   - **Finding:** Common issues include lower throughput, Wi‑Fi “conking out” after some hours, and differences between CT vs non‑CT firmware.

13. **Airtime fairness and AQL have triggered kernel oopses and require careful configuration.**
   - **Source:** OpenWrt bug tracker logs and mailing lists.[^37][^31]
   - **Finding:** Certain combinations of kernel, MTU, and airtime fairness led to kernel crashes or fairness anomalies; fixes are ongoing.

14. **ath10k‑ct queue flush behavior is complex, and CVE‑related workarounds can reduce throughput.**
   - **Source:** ath10k‑ct GitHub issue #195 and OpenWrt issue #13065.[^38][^39]
   - **Finding:** To mitigate CVE‑2022‑47522, some devices need altered flush behavior; recommended config may reduce maximum bandwidth by ~25% while improving stability.

15. **Airtime fairness support flags and debugfs entries are missing on several ath10k‑ct platforms.**
   - **Source:** ath10k‑ct GitHub and user reports.[^40]
   - **Finding:** QCA9980 and related chips lack proper NL80211 airtime fairness feature bits; enabling them manually reveals incomplete implementation.

16. **OpenWrt dumb AP deployments cannot leverage firewall/NAT offload to mask Wi‑Fi MAC inefficiencies.**
   - **Source:** WS‑AP3825i thread.[^10]
   - **Finding:** In pure AP/bridge mode, acceleration features don’t help Wi‑Fi; path is limited by radio/driver only.

17. **airMAX marketing does not provide reproducible experimental conditions or statistics.**
   - **Source:** airMAX datasheet and training slides.[^27][^41][^8]
   - **Finding:** Claims of “collision‑free” operation and high throughput aren’t backed by public experimental details; they cannot serve as scientific benchmarks.

18. **No strong Ubiquiti‑assigned patents were found that fully describe airMAX AC TDMA implementation details.**
   - **Source:** Patent search (TDMA, hidden node, collision avoidance).[^42][^43][^44]
   - **Finding:** Many generic MAC patents exist, but none give a blueprint for airMAX AC internals; these remain effectively trade secrets.

19. **Pure 802.11e access category tuning (VO/VI) is insufficient to fix latency without fair queueing.**
   - **Source:** USENIX airtime fairness paper; VoIP/web experiments.[^1]
   - **Finding:** With FQ‑MAC and airtime fairness, VoIP in Best Effort AC performs as well or better than in Voice AC on an unmodified kernel; access categories are a second‑order lever.

20. **There is no public demonstration of open‑stack QCA988x matching airMAX TDMA PtMP performance in real WISP deployments.**
   - **Source:** Literature review and forum search.[^9][^12][^10]
   - **Finding:** Despite rich open‑source work, no convincing report shows QCA988x with OpenWrt + ath10k/ct matching airMAX TDMA for many‑CPE sectors with hidden nodes and interference.


## 5. Table of measured performance improvements and exact conditions

The following table summarizes representative experiments with quantitative improvements; percentage gains are not aggregated across rows.

| ID | Source & URL | Date | Hardware / Chipset / FW | APs / STAs / Topology & RF | Traffic / Workload | Baseline | Modification | Measured Gain / Regression | Reps / Stats | Code/Data Availability | Portability & Control Layer |
|----|--------------|------|-------------------------|----------------------------|---------------------|----------|-------------|----------------------------|--------------|------------------------|-----------------------------|
| R1 | Ending the Anomaly (USENIX ATC) [link](https://www.usenix.org/system/files/conference/atc17/atc17-hoiland-jorgensen.pdf)[^1] | 2017 | AP: AR9580/ath9k; clients: x86; Linux 4.6 | 1 AP, 3 STAs (2 fast, 1 slow), HT20 5 GHz, 30‑station extension (1 slow at 1 Mbps, 29 fast) | UDP/TCP downlink, ping under load | pfifo_fast, unmanaged queues | FQ‑MAC + airtime fairness | 3.3 → 17.7 Mbps aggregate throughput with one slow STA (5.4×); latency reduced ~10×; fairness index ~1 | 30× 5 min runs with error bars | Yes (paper + code) | DEMONSTRATED on adjacent hardware; mac80211/ath9k |
| R2 | CeroWrt “real results” [link](https://blog.cerowrt.org/post/real_results/)[^6] | 2016 | AP: ath9k; clients: ath10k | 1 AP, 2 STAs, HT20 5 GHz, mixed link rates | Flent RRUL, ping under load | pfifo_fast | FQ‑MAC + airtime fairness | ~90 Mbps at ~20 ms latency; median latency <20 ms from 6–150 Mbps | Multiple runs with flent plots | Plots and settings available | DEMONSTRATED on adjacent hardware; mac80211/ath9k |
| R3 | CeroWrt “FQ_codel on ath10k” [link](https://blog.cerowrt.org/post/fq_codel_on_ath10k/)[^2] | 2016 | AP: ath10k; clients: PCs | 1 AP; 4 upload streams; problematic link | flent RTT_fair | Standard ath10k | Prototype FQ‑CoDel in ath10k | 6 Mbps throughput with <20 ms latency vs much higher latency before | Multiple flent runs | PoC patches | DEMONSTRATED on adjacent hardware; ath10k driver |
| R4 | OpenWrt “AQL and the ath10k is lovely” [link](https://forum.openwrt.org/t/aql-and-the-ath10k-is-lovely/59002)[^7] | 2020–2022 | Ubiquiti UAP Mesh/Mesh Pro (QCA988x), ath10k‑ct‑smallbuffers, OpenWrt master | 1 AP, multiple STAs, ~12 Mbps problematic link | flent RRUL (ping + 4 TCP flows) | No AQL, default ath10k | AQL + native FQ‑CoDel in ath10k‑ct | Ping under load from >4 s to <60 ms with similar throughput | Multiple before/after plots | Configs shared, standard OpenWrt builds | CONFIRMED on target‑class hardware; ath10k‑ct + mac80211 |
| R5 | hMAC paper [link](https://www.tkn.tu-berlin.de/bib/zehl2016hmac/zehl2016hmac.pdf)[^20] | 2016 | APs & STAs: ath9k; Ubuntu | 2 APs + 3 STAs; hidden‑node scenario; wired PTP sync | TCP downlink via iperf | DCF and classical TDMA | hMAC per‑link TDMA/CSMA | Aggregate throughput ~4.2 Mbps (classical TDMA) → 8.8 Mbps (hMAC); hidden STA maintains throughput | Multiple runs, error bars | Research code | DEMONSTRATED on adjacent hardware; user‑space controller + ath9k |
| R6 | STPP/WL4 (ICNP 2019) [link](https://saeed.github.io/files/stpp-icnp19.pdf)[^21] | 2019 | Commodity Wi‑Fi NICs; Linux | 5‑node WLAN, multiple local links | Synthetic microbenchmarks & AR app | Plain DCF/EDCA | STPP/WL4 overlay | Local‑link latency −40%; avg latency −38%; throughput cost ≤9% | Multiple experiments | Patch + Click/py code (per paper) | DEMONSTRATED on adjacent HW; above‑driver Linux overlay |
| R7 | QCA9888 OpenWrt vs OEM [link](https://forum.archive.openwrt.org/viewtopic.php?id=67633)[^9] | 2016 | QCA9888 11ac module | 1 AP, 1 STA, 5 GHz, 80 MHz | iperf3 TCP | OEM firmware (~320–340 Mbps) | OpenWrt + ath10k (~130–210 Mbps) | Regression: OpenWrt/ath10k significantly lower throughput | Multiple tests | N/A (firmware proprietary) | DEMONSTRATED on adjacent HW; ath10k |
| R8 | WS‑AP3825i throughput cap [link](https://forum.openwrt.org/t/ws-ap3825i-5ghz-throughput-limitation-on-openwrt-23-05-3/198035)[^10] | 2024 | WS‑AP3825i (QCA988x), OpenWrt 23.05.3 | 1 AP, iPhone 15 Pro, 80 MHz 5 GHz | iperf3 TCP | Vendor firmware (not measured here) | OpenWrt + ath10k/ath10k‑ct | ~460 Mbps cap despite high PHY rates | Several runs with different configs | N/A | CONFIRMED on target‑class HW; ath10k |
| R9 | NanoStation 5AC Loco OpenWrt [link](https://www.reddit.com/r/openwrt/comments/ochurr/openwrt_on_ubiquitis_airmax_devices/)[^25] | 2021 | Ubiquiti NS5AC Loco (QCA988x), OpenWrt | 1 AP, 1 phone client, 80 MHz | iperf3 TCP | airOS airMAX (not measured here) | OpenWrt + ath10k | ~300 Mbps TCP in normal Wi‑Fi mode | Multiple user tests | N/A | CONFIRMED on target HW; ath10k |
| R10 | airMAX TDMA datasheet [link](https://dl.ubnt.com/datasheets/airmax/UBNT_DS_airMAX_TDMA.pdf)[^8] | ca. 2013–2015 | airMAX/airMAX AC APs + CPEs | PtMP outdoor, many CPEs, GPS sync | Mixed traffic (vendor description) | 802.11 DCF (implicit) | airMAX TDMA with GPS | Qualitative: hidden‑node mitigation, scalability, noise immunity, higher throughput | Not quantified | N/A | DEMONSTRATED on proprietary MAC; custom IC |


## 6. Ranked list of techniques most likely to transfer to FuturaMAX

Ranking is based on evidence strength, portability to QCA988x, and relevance to WISP PtMP.

1. **Airtime Queue Limits (AQL) + FQ‑CoDel in ath10k/ath10k‑ct**
   - Strong evidence on Ubiquiti QCA988x devices; orders‑of‑magnitude latency reduction at negligible throughput cost.[^7]
   - Fully implementable via OpenWrt snapshots and driver config.

2. **mac80211 TXQ + FQ‑MAC queueing (where available)**
   - Proven on ath9k; partial integration benefits ath10k even without full airtime scheduler.[^6][^1]
   - Prevents hidden driver/firmware queues from dominating behavior.

3. **Upstream CAKE/FQ‑CoDel shaping at WISP edge/router**
   - Avoids WAN‑side bufferbloat and ensures Wi‑Fi hop is not overwhelmed by upstream queues.[^32][^31]

4. **Careful firmware selection and tuning (ath10k vs ath10k‑ct vs smallbuffers)**
   - CT firmware adds useful debug and features; smallbuffers variants can reduce bufferbloat on low‑RAM boards.[^45][^18]
   - Some boards perform better with non‑CT; comparing both in FuturaMAX experiments is critical.[^46][^47]

5. **STPP/WL4‑style above‑driver scheduling for PtP and small PtMP clusters**
   - Hardware‑agnostic; no firmware changes required; proven latency benefit in small node clusters.[^21]

6. **Network‑level design: sector planning, channel reuse, and cell splitting informed by spectral scans**
   - QCA988x spectral scan and Ubiquiti tools support interference mapping, allowing better channel/width choices.[^11]

7. **Hybrid DCF + coarse time‑based downlink scheduling (hMAC‑inspired but simplified)**
   - Use per‑CPE airtime budgeting and transmission grouping at the AP level, without tight slot timing, to approximate fair scheduling.[^20]

8. **Aggressive use of flent RRUL and similar tests in CI to avoid regressions**
   - Many negative results arise from configuration or regressions; systematic testing mitigates this.[^2][^1]

9. **Rate‑control tuning and rate mask stability analysis**
   - Minstrel‑HT and related algorithms have tunables; verifying stable rate masks and avoiding problematic MCS/NSS combinations on specific CPEs is beneficial.[^1]

10. **Long‑distance ACK/CTS timing and coverage‑class tuning where firmware exposes controls**
   - Some drivers allow tuning distance/ACK timing; doing so may modestly improve link stability at long ranges.[^12]


## 7. Techniques likely blocked or severely constrained on QCA988x

1. **Full airMAX‑style TDMA with microsecond‑scale slot control from host side**
   - Blocked by firmware‑owned MAC and hidden queues; no exposed registers for slot scheduling.[^16][^15]

2. **Deficit‑based airtime fairness identical to ath9k implementation**
   - ath10k lacks the required scheduling hooks; patches would need firmware cooperation.[^1]

3. **hMAC‑style precise per‑link TDMA using power‑save queues**
   - Implementation depends on ath9k PS semantics not present in ath10k.[^20]

4. **OpenTDMF/Soft‑TDMAC‑style full TDMA MAC on offloaded 11ac chips**
   - Requires modifying driver and often clients; incompatible with closed‑firmware hardware like QCA988x.[^24][^21]

5. **Sub‑millisecond TDMA overlays from user space on embedded SoCs**
   - hMAC shows timing jitter even on x86; embedded MIPS/ARM will be less deterministic.[^20]

6. **Matching vendor airMAX AC peak throughput in all scenarios under open‑stack**
   - Evidence shows open‑stack often underperforms OEM firmware on throughput, especially with QCA988x/QCA9888.[^9][^10]

7. **Fine‑grained per‑frame TX completion telemetry and aggregation control**
   - ath10k does not expose detailed TX completion or aggregation boundaries to the host.[^15][^16]

8. **Pure 802.11e AC‑based QoS as primary latency solution**
   - VoIP and web browsing experiments show AC changes are minor compared to queueing/fairness changes.[^1]

9. **Relying solely on OpenWrt APs to outperform airMAX TDMA on long‑range PtMP sectors without topology changes**
   - No public evidence exists for such success; likely requires network redesign and above‑driver coordination.[^12]

10. **Using firewall/NAT offload to compensate for Wi‑Fi MAC limitations in pure AP mode**
   - Offload doesn’t affect Wi‑Fi path in bridge/dumb‑AP designs.[^10]


## 8. Important source‑code repositories and maintenance status

1. **Linux kernel (mac80211, ath9k, ath10k)**
   - **Location:** mainline kernel tree (`net/mac80211`, `drivers/net/wireless/ath/`).
   - **Relevance:** Implements TXQ, FQ‑MAC, airtime fairness; ath10k driver and ath9k reference implementation.[^15][^1]
   - **Status:** Actively maintained.

2. **OpenWrt**
   - **Location:** [https://github.com/openwrt/openwrt](https://github.com/openwrt/openwrt).[^46]
   - **Relevance:** Integrates AQL patches, ath10k/ath10k‑ct packaging, Wi‑Fi configs.
   - **Status:** Very active.

3. **ath10k‑ct firmware & driver (CandelaTech)**
   - **Location:** [https://github.com/greearb/ath10k-ct](https://github.com/greearb/ath10k-ct) and firmware downloads.[^17]
   - **Relevance:** Alternative firmware for QCA988x with extra features and debug options; used heavily in OpenWrt.[^18]
   - **Status:** Actively maintained; new features limited.[^46]

4. **hMAC (ath9k-hmac)**
   - **Location:** GitHub repos linked from hMAC paper.
   - **Relevance:** Prototype hybrid TDMA/CSMA MAC on ath9k.[^20]
   - **Status:** Research‑grade, limited recent activity.

5. **STPP/WL4**
   - **Location:** Source code references in ICNP paper (mac80211 patch + Click + Python); not prominently maintained.
   - **Relevance:** Soft scheduling overlay above drivers.[^21]
   - **Status:** Research‑grade.

6. **flent**
   - **Location:** [https://flent.org](https://flent.org).[^30]
   - **Relevance:** Standard tool for RRUL, tcp_nup, tcp_ndown tests.
   - **Status:** Active.


## 9. Patents and proprietary boundaries

The patent landscape around TDMA, hidden‑node mitigation and hybrid MAC schemes is dense.

- **Hidden terminal detection and dynamic protocol switching (IBM)**
  - **Patent:** US5661727A, “Schemes to determine presence of hidden terminals in wireless networks environment and to switch between them”.[^42]
  - **Idea:** Detect hidden nodes and switch between collision sensing and collision avoidance protocols.

- **Receiver‑initiated multiple access (RIMA) and channel hopping (RICH) – UC Regents**
  - **Patents:** US6996074B2, US20020080768A1, US20020141479A1.[^43][^48][^49]
  - **Idea:** Receiver‑initiated collision‑avoidance MACs and multi‑channel hopping schemes that eliminate hidden terminals.

- **Hybrid TDMA/CSMA for interference avoidance**
  - **Patents:** US10972997B2, US20190132878A1 (Benchmark Electronics).[^44][^50]
  - **Idea:** Frames divided into TDMA and contention slots; nodes use TDMA slots if available, otherwise fall back to CSMA.

- **WirelessHART TDMA and contention slots (ABB)**
  - **Patent:** US20130142180A1 and family.[^51]
  - **Idea:** Hybrid TDMA with dedicated and shared slots in industrial wireless.

- **Spatial TDMA and scheduling for mesh networks (Motorola)**
  - **Patent:** US20070133592A1.[^52]

- **airMAX TDMA internals**
  - No clearly identified patents from Ubiquiti describing the full airMAX AC protocol; instead, technology is described in datasheets and training guides without algorithmic detail.[^26][^27][^8]

**Implication for FuturaMAX:**
- Implementing generic features like AQL, FQ‑CoDel, and mac80211 airtime fairness uses existing open infrastructure and is low‑risk.
- Designing a new proprietary TDMA/CSMA hybrid may cross into existing patent territory; caution and legal review would be needed.
- Re‑implementing a protocol that “looks like” airMAX TDMA without knowledge of internals is both technically hard and potentially risky; treating airMAX only as an empirical benchmark is safer.


## 10. Ten highest‑value questions for physical experiments

1. **How close can AQL + FQ‑CoDel + ath10k‑ct come to airMAX TDMA in long‑range PtMP hidden‑node scenarios on identical hardware?**
2. **What is the maximum sustainable PtMP sector capacity (sum Mbps and per‑CPE QoE) for each firmware/driver stack (airOS TDMA, OpenWrt + ath10k, OpenWrt + ath10k‑ct) under realistic WISP loads?**
3. **How do latency and jitter for VoIP and gaming flows behave on FuturaMAX vs airMAX TDMA sectors over weeks, not just minutes, including during peak evening load?**
4. **What CPU and RAM headroom remain on LiteAP/LiteBeam/NanoStation devices when AQL, FQ‑CoDel, and a light STPP‑style scheduler are all active?**
5. **How sensitive is QCA988x performance to slot timing jitter if a coarse user‑space scheduler is introduced (e.g., hMAC‑lite), and at what granularity do benefits vanish?**
6. **How do different ath10k firmware variants (CT vs non‑CT vs smallbuffers) affect aggregation depth, retry behavior, and fairness on your exact boards and topologies?**
7. **How stable are rate masks and MCS/NSS selections under real interference on FuturaMAX vs airMAX TDMA, and can host‑side modeling or ML improve rate decisions without firmware changes?**
8. **What are the real‑world gains from combining sector redesign (channel width, reuse, antenna patterns) with FuturaMAX queueing improvements vs queueing alone?**
9. **To what extent can QCA988x spectral scanning and interference classification be incorporated into cross‑layer controllers that adapt channels, widths and power in response to measured interference?**
10. **In PtP backhaul scenarios, what is the best achievable trade‑off between throughput and latency on FuturaMAX compared to airMAX AC, across a range of distances and SNRs?**


## 11. Complete source ledger (direct links)

Key primary sources and discussions:

- **Ending the Anomaly: Achieving Low Latency and Airtime Fairness in WiFi (USENIX ATC 2017):** https://www.usenix.org/system/files/conference/atc17/atc17-hoiland-jorgensen.pdf[^1]
- **FQ_codel on ath10k (CeroWrt):** https://blog.cerowrt.org/post/fq_codel_on_ath10k/[^2]
- **Finally… the real net‑next 4.8 fq_codel/airtime‑fair ath9k results (CeroWrt):** https://blog.cerowrt.org/post/real_results/[^6]
- **Analyzing ath10k’s current behavior (CeroWrt):** https://blog.cerowrt.org/post/rtt_fair_on_wifi/[^4]
- **AQL and the ath10k is *lovely* (OpenWrt forum):** https://forum.openwrt.org/t/aql-and-the-ath10k-is-lovely/59002[^7]
- **WS‑AP3825i 5GHz Throughput Limitation on OpenWrt 23.05.3:** https://forum.openwrt.org/t/ws-ap3825i-5ghz-throughput-limitation-on-openwrt-23-05-3/198035[^10]
- **Openwrt build: low bandwidth on 11ac radio module:** https://forum.archive.openwrt.org/viewtopic.php?id=67633[^9]
- **OpenWrt installation on Ubiquiti airMAX AC devices:** https://openwrt.org/toh/ubiquiti/common[^5]
- **OpenWrt on Ubiquiti’s AirMax devices (discussion including NS5AC Loco):** https://www.reddit.com/r/openwrt/comments/ochurr/openwrt_on_ubiquitis_airmax_devices/[^25]
- **ath10k driver documentation:** https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k.html[^15]
- **ath10k firmware documentation:** https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/firmware.html[^16]
- **CandelaTech ath10k‑ct firmware user guide:** https://www.candelatech.com/ath10k-ug.php[^17]
- **OpenWrt ath10k‑firmware‑qca988x‑ct package:** https://openwrt.org/packages/pkgdata/ath10k-firmware-qca988x-ct[^18]
- **OpenWrt issue: Switch back to ath10k firmware instead of ath10k‑ct:** https://github.com/openwrt/openwrt/issues/14089[^46]
- **airMAX TDMA Technology Datasheet:** https://dl.ubnt.com/datasheets/airmax/UBNT_DS_airMAX_TDMA.pdf[^8]
- **UBWA/UEWA training guides (hidden node, CSMA/CA):** https://dl.ubnt.com/guides/training/courses/UBWA_Training_Guide.pdf and https://dl.ubnt.com/guides/training/courses/UEWA_Training_Guide_V2.1.pdf[^27][^26]
- **hMAC: Enabling Hybrid TDMA/CSMA on IEEE 802.11 Hardware:** https://www.tkn.tu-berlin.de/bib/zehl2016hmac/zehl2016hmac.pdf[^20]
- **If you can’t beat them, augment them (STPP/WL4):** https://saeed.github.io/files/stpp-icnp19.pdf[^21]
- **Enabling TDMA for Today’s Wireless LANs (OpenTDMF):** https://www.yangzhice.com/docforweb/TDMA/TDMA_INFOCOM.pdf[^24]
- **Long distance link optimization (OpenWrt forum):** https://forum.archive.openwrt.org/viewtopic.php?id=45539[^12]
- **Belkin RT3200/Linksys E8450 - AQL and WiFi Latency:** https://forum.openwrt.org/t/belkin-rt3200-linksys-e8450-aql-and-wifi-latency/155930[^23]
- **Flent tests documentation:** https://flent.org/tests.html[^30]
- **Using Flent to Generate Traffic (CandelaTech):** https://www.candelatech.com/cookbook/wifire/UE_Testing_Using_flent_to_Generate_Traffic[^28]
- **Making WiFi fast (LWN):** https://lwn.net/Articles/705884/[^32]
- **Various OpenWrt and Reddit Wi‑Fi latency/bufferbloat discussions:** examples at https://forum.openwrt.org/t/bufferbloat-does-airtime-fq-replace-the-need-to-shape-per-client/189074, https://www.reddit.com/r/openwrt/comments/1ap1jgj/now_that_internet_connection_is_faster_than_wifi/[^31][^22]
- **Patent examples for hidden terminals and hybrid TDMA/CSMA:** US5661727A, US6996074B2, US20130142180A1, US10972997B2 (URLs via patent corpus).[^43][^51][^44][^42]

---

## References

1. [[PDF] Achieving Low Latency and Airtime Fairness in WiFi - USENIX](https://www.usenix.org/system/files/conference/atc17/atc17-hoiland-jorgensen.pdf) - Achieving airtime fairness also has the desirable property that it makes a station's performance dep...

2. [FQ_codel on ath10k - https://blog.cerowrt.org/](https://blog.cerowrt.org/post/fq_codel_on_ath10k/) - Vs today: 6mbits of clean throughput (4 streams going here), with less than 20ms latency. First ever...

3. [Ath10k (5GHz card) after upgrade to 3.3](https://forum.turris.cz/t/ath10k-5ghz-card-after-upgrade-to-3-3/2146) - Ath10k (5GHz card) after upgrade to 3.3 /ath10k/QCA988X/hw2.0/ is installed on root and has the foll...

4. [Analyzing ath10k's current behavior - https://blog.cerowrt.org/](https://blog.cerowrt.org/post/rtt_fair_on_wifi/) - Ath10k Wifi: Peaks at 2.5 sec of latency before going haywire ... Please note that every AP and chip...

5. [[OpenWrt Wiki] Common Procedures for Ubiquiti Products](https://openwrt.org/toh/ubiquiti/common) - OpenWrt installation on Ubiquiti AirMAX AC Devices (WA and/or XC boards). The following method has b...

6. [Finally... the real net-next 4.8 fq_codel/airtime-fair ath9k results](https://blog.cerowrt.org/post/real_results/) - We are finally holding latencies below 20ms at the median for Wifi rates varying from 6mbits to 150m...

7. [AQL and the ath10k is *lovely* - For Developers](https://forum.openwrt.org/t/aql-and-the-ath10k-is-lovely/59002) - AQL keeps the firmware from overbuffering, and more important is the fq_codel algo on top that which...

8. [airMAX TDMA Technology Datasheet](https://dl.ubnt.com/datasheets/airmax/UBNT_DS_airMAX_TDMA.pdf) - The TDMA protocol dynamically allocates time to active clients and provides greater noise immunity p...

9. [Topic: Openwrt build: low bandwidth on 11ac radio module](https://forum.archive.openwrt.org/viewtopic.php?id=67633) - Hi,. I am experiencing a limited bandwidth issue related with an QCA9888 802.11 Wifi module (b/g/n/a...

10. [WS-AP3825i 5GHz Throughput Limitation on OpenWrt ...](https://forum.openwrt.org/t/ws-ap3825i-5ghz-throughput-limitation-on-openwrt-23-05-3/198035) - Tested with ath10k-firmware-qca988x and … the throughput remains capped at about 460Mbps. You must t...

11. [DATASHEET](https://www.microcom.com.ar/fotos/7409_1721048760337.pdf) - airMAX ac Technology for up to 500+ Mbps Throughput Superior Processing by airMAX Engine with Custom...

12. [Topic: Long distance link optimization](https://forum.archive.openwrt.org/viewtopic.php?id=45539) - Not a general firmware issue, simply airOS has some optimization for long distance link that openwrt...

13. [Ubiquiti Networks airCube AC - WikiDevi.Wi-Cat.RU](https://wikidevi.wi-cat.ru/Ubiquiti_Networks_airCube_AC) - LAN ports: 3 WAN speed: 802.11b/g/n Power Amplifier, The Ubiquiti WiFi chip appears to be a custom Q...

14. [airMAX ac Products - NetWifiWorks.com](https://www.netwifiworks.com/airMAX-ac.asp) - Ubiquiti's airMAX engine with custom IC dramatically improves TDMA latency and network scalability. ...

15. [About ath10k](https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k.html) - ath10k is the mac80211 wireless driver for Qualcom Atheros QCA988x family of chips, which support IE...

16. [ath10k firmware - Linux Wireless documentation](https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/firmware.html) - Because firmware changes between versions we have introduced firmware API concept to ath10k. This ma...

17. [Ath10k Candela Technologies (CT) Firmware User Guide](https://www.candelatech.com/ath10k-ug.php) - Ath10k Candela Technologies (CT) Firmware User Guide. This documents some of the features of the Ath...

18. [package: ath10k-firmware-qca988x-ct](https://openwrt.org/packages/pkgdata/ath10k-firmware-qca988x-ct) - Version: 2020-11-08-1 ; Description: Alternative ath10k firmware for QCA988X from Candela Technologi...

19. [[Feature request] backport support AQL for ath10k and ...](https://forum.turris.cz/t/feature-request-backport-support-aql-for-ath10k-and-ath10k-ct/12613) - Dear team, this year patches landed in OpenWrt master that implemented AQL (airtime queue limits) fo...

20. [[PDF] hMAC: Enabling Hybrid TDMA/CSMA on IEEE 802.11 Hardware](https://www.tkn.tu-berlin.de/bib/zehl2016hmac/zehl2016hmac.pdf) - ATH9K device driver to enable control of the software packet queues. ... The most recent work on TDM...

21. [[PDF] If you can't beat them, augment them - Ahmed Saeed](https://saeed.github.io/files/stpp-icnp19.pdf) - We pick two examples that can be deployed on commodity devices. Clock synchronization-based protocol...

22. [Now that internet connection is faster than wifi I need sqm ...](https://www.reddit.com/r/openwrt/comments/1ap1jgj/now_that_internet_connection_is_faster_than_wifi/) - AQL is an fq_codel driver implementation that has virtually zero effect on CPU load, it's all run on...

23. [Belkin RT3200/Linksys E8450 - AQL and WiFi Latency](https://forum.openwrt.org/t/belkin-rt3200-linksys-e8450-aql-and-wifi-latency/155930) - AQL and WiFi Latency Installing and Using OpenWrt Network and Wireless Configuration. Provides a gre...

24. [Enabling TDMA for Today's Wireless LANs](https://www.yangzhice.com/docforweb/TDMA/TDMA_INFOCOM.pdf) - by Z Yang · Cited by 40 — In this paper we present OpenTDMF, an architecture to enable TDMA on commo...

25. [OpenWRT on Ubiquiti's AirMax devices](https://www.reddit.com/r/openwrt/comments/ochurr/openwrt_on_ubiquitis_airmax_devices/) - Ubiquiti says that they've made a special custom radio chip that they're using in these devices and ...

26. [[PDF] UEWA Training Guide - Ubiquiti](https://dl.ubnt.com/guides/training/courses/UEWA_Training_Guide_V2.1.pdf) - Collision Avoidance (CSMA/CA) This is known as the hidden node problem. The 802.11 protocol partiall...

27. [[PDF] UBWA Training Guide - Ubiquiti](https://dl.ui.com/guides/training/courses/UBWA_Training_Guide.pdf) - Even when negotiating at 802.11n data rates, airMAX ac radios often permit higher throughput. Hidden...

28. [Using Flent to Generate Traffic](https://www.candelatech.com/cookbook/wifire/UE_Testing_Using_flent_to_Generate_Traffic) - To run Flent tests by command line: Run netserver. This will start the netserver program which is th...

29. [Flaws and features in the Flent network testing tool - https ...](https://blog.cerowrt.org/post/flaws_in_flent/) - Try the RRUL test on your wifi. You can run rrul with -l 20, and get a good result, in under 20 seco...

30. [Supplied Tests — Flent: The FLExible Network Tester](https://flent.org/tests.html) - The Realtime Response Under Load (RRUL) test¶ It works by running RTT measurement using ICMP ping an...

31. [[bufferbloat] Does Airtime FQ replace the need to shape ...](https://forum.openwrt.org/t/bufferbloat-does-airtime-fq-replace-the-need-to-shape-per-client/189074) - fq_codel/CAKE are easily configured in all modern OpenWrt builds. The airtime FQ algorithm sits at t...

32. [Making WiFi fast - LWN.net](https://lwn.net/Articles/705884/) - I think you'd want to test quite a bit before trying for airtime fairness. I think the interaction o...

33. [Horrible wireless coverage with OpenWRT compared to ...](https://www.reddit.com/r/openwrt/comments/hi0l7r/horrible_wireless_coverage_with_openwrt_compared/) - Horrible wireless coverage with OpenWRT compared to DD-WRT. Ath10k drivers are related to 5GHz radio...

34. [Performance and stability: stock vs flashed : r/openwrt](https://www.reddit.com/r/openwrt/comments/oxsc0v/performance_and_stability_stock_vs_flashed/) - I've seen some stability issues over the 5 GHz WiFi and the Xiaomi AP. With iperf3 I have reached a ...

35. [Wireless instability on ath10k radios after upgrade to 21.02.1](https://forum.openwrt.org/t/wireless-instability-on-ath10k-radios-after-upgrade-to-21-02-1/117396) - rebooting the router always fixes the problem. The issue is finally fixed on upstream and OpenWrt ma...

36. [ESPHome + OpenWRT(ATH10k radio) = ESP8266 ota ...](https://community.home-assistant.io/t/esphome-openwrt-ath10k-radio-esp8266-ota-timed-out/356065?page=2) - Seems to be a problem with ath10k firmware/drivers. It seems to me that the issue can be resolved us...

37. [2020-July.txt - Mailing Lists - OpenWrt](http://lists.openwrt.org/pipermail/openwrt-bugs/2020-July.txt) - THIS IS AN AUTOMATED MESSAGE, DO NOT REPLY. The following task has a new comment added: FS#3215 - Mu...

38. [ath10k: failed to flush transmit queue with buggy client](https://github.com/openwrt/openwrt/issues/13065) - firmware seems to not implement per-client queue flush aka CVE-2022-47522 fix. Try -ct firmware and ...

39. [[PATCH v3 0/2] Improve ath10k flush queue mechanism](https://patchew.org/linux/cover.1729844329.git.repk@triplefau.lt/) - This is due to how the TX queues are flushed in ath10k. effectively blocking the whole queue during ...

40. [qca9980 lacks airtime fariness support indication #195](https://github.com/greearb/ath10k-ct/issues/195) - ath10k-ct driver/firmware for the r7500v2 running openwrt do not indicate airtime fairness support.

41. [airMAX - NetWifiWorks.com](https://www.netwifiworks.com/airMAX.asp) - Unlike standard WiFi protocol, airMAX Time Division Multiple Access (TDMA) protocol allows each clie...

42. [Schemes to determine presence of hidden terminals in wireless networks environment and to switch between them](https://www.perplexity.ai/rest/file-repository/patents/US5661727A?lens_id=080-080-208-352-262) - publication_number: US5661727A
assignee: IBM CORPORATION
abstract: A method of delievering data in a...

43. [Receiver-initiated multiple access for ad-hoc networks (RIMA)](https://www.perplexity.ai/rest/file-repository/patents/US6996074B2?lens_id=199-073-629-372-253) - publication_number: US6996074B2
assignee: THE REGENTS OF THE UNIVERSITY OF CALIFORNIA
abstract: Rece...

44. [Hybrid time division multiple access (TDMA) and carrier sense multiple access (CSMA) for interference avoidance method therefor](https://www.perplexity.ai/rest/file-repository/patents/US10972997B2?lens_id=114-111-643-240-805) - publication_number: US10972997B2
assignee: BENCHMARK ELECTRONICS INC
abstract: A method for interfer...

45. [[OpenWrt-Devel] ath79: use ath10k-ct-smallbuffers for 64 MiB ...](https://patchwork.ozlabs.org/patch/1214770/) - ath10k-ct-smallbuffers for 64 MiB devices … ath10k-ct-smallbuffers for 64 MiB devices. These should ...

46. [Switch back to ath10k firmware instead of ath10k-ct #14089](https://github.com/openwrt/openwrt/issues/14089) - Describe the bug. According to greearb on Issue 81 of ath10k-ct firmware. I am not planning to add a...

47. [Archer C7 with mesh: ath10k and corresponding non-ct ...](https://forum.openwrt.org/t/archer-c7-with-mesh-ath10k-and-corresponding-non-ct-firmware/180748) - Please try ath10k and the corresponding non-ct firmware, iirc -ct doesn't like meshing on wave1 hard...

48. [Receiver-initiated multiple access for AD-HOC networks (RIMA)](https://www.perplexity.ai/rest/file-repository/patents/US20020080768A1?lens_id=049-965-720-915-620) - publication_number: US20020080768A1
assignee: THE REGENTS OF THE UNIVERSITY OF CALIFORNIA
abstract: ...

49. [Receiver-initiated channel-hopping (RICH) method for wireless communication networks](https://www.perplexity.ai/rest/file-repository/patents/US20020141479A1?lens_id=008-899-785-305-17X) - publication_number: US20020141479A1
assignee: REGENTS OF THE UNIVERSITY OF CALIFORNIA THE
abstract: ...

50. [HYBRID TIME DIVISION MULTIPLE ACCESS (TDMA) AND CARRIER SENSE MULTIPLE ACCESS (CSMA) FOR INTERFERENCE AVOIDANCE METHOD THEREFOR](https://www.perplexity.ai/rest/file-repository/patents/US20190132878A1?lens_id=126-849-297-583-763) - publication_number: US20190132878A1
assignee: BENCHMARK ELECTRONICS INC
abstract: A method for inter...

51. [Wireless Communication Method And System With Collision Avoidance Protocol](https://www.perplexity.ai/rest/file-repository/patents/US20130142180A1?lens_id=001-561-016-379-163) - publication_number: US20130142180A1
assignee: ABB RESEARCH LTD, ABB SCHWEIZ AG
abstract: A method fo...

52. [Method for tree-based spatial time division multiple access (TDMA) scheduling in a multi-hop wireless](https://www.perplexity.ai/rest/file-repository/patents/US20070133592A1?lens_id=043-629-366-237-597) - publication_number: US20070133592A1
assignee: MOTOROLA INC
abstract: A method for tree based spatial...

