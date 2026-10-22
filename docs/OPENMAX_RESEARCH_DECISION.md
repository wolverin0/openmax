<!-- doc-head: Executive decision matrix (DO NOW / LAB NEXT / CONDITIONAL / NO-GO) integrating all OpenMax findings through Step 1C run17 PASS -->
Consolidates hardware-verified truths across 1,800 WISP radios (airOS 8 WA/XC, LTU amesoc3/Arria10, OpenWrt 24.10.4).
Separates immediate zero-risk NOC deployments (DO NOW) from high-ROI bench experiments (LAB NEXT), gated compute/relay options (CONDITIONAL), and refuted paths (NO-GO).
Identifies FMX-0016 (passive fleet sensor roll-up) and FMX-0017 (Step 1D multi-CPE OTA discovery-IE qualification) as top next steps.
<!-- /doc-head -->

# OpenMax Master Research Decision Matrix (`DO NOW / LAB NEXT / CONDITIONAL / NO-GO`)

**Date**: 2026-10-22  
**Parent Deliverable**: [`docs/OPENMAX_MASTER_RESEARCH_PROMPT.md`](OPENMAX_MASTER_RESEARCH_PROMPT.md) §§10–11  
**Baseline Anchor**: Incorporates all verified static reverse engineering and physical bench milestones through **October 22 (`Step 1C` / `FMX-0015` `run17` `PASS`)**.

---

## 1. Top 5 Confirmed Engineering Discoveries in OpenMax (Grounded in Binary & Hardware Evidence)

1. **`Step 1C` (`run17` `PASS` — `2026-10-22`, `CONFIRMED` on Bench)**:
   - An OpenWrt `24.10.4` AP (`LAP-120`, `0xe8e5`) achieved **100% AP-side zero-touch association, WPA2-PSK CCMP 4-way handshake authorization (`authorized=true`), and bidirectional IPv6 data transfer (`71.735s` stable, `0%` loss)** with a **100% unmodified Stock `airOS WA.v8.7.25` CPE (`Loco195`, `0xe7fa`)** by combining:
     - **Discovery Gate (`Gates 1–3`)**: Broadcasting Ubiquiti's `msg_type=1` Vendor IE until the CPE's broadcast Probe Request arrives, then withdrawing the IE after `0.5s` so `ubnt_poll_host_on_beacon_rx` (`0x88b0` $\to$ `0x8b60`) clears the BSSID from `handle->sta_list` (`0x10ec`) prior to `Assoc Req`, routing the Stock CPE into **`Path B` (`Normal AP` CSMA/CA, `polling_enable=0`, `handle->connected_ap == NULL`)** so all TDMA poll-timeout watchdogs remain inert.
     - **Datapath & EAPOL Gate (`run17` Root Cause)**: Setting `wds=1` on the OpenWrt AP (`uci set wireless.default_radio0.wds=1`) so the AP accepts the Stock CPE's 4-address WDS EAPOL 2/4 and data frames (with `mac80211.ko` `sha256: 19a8fde6...` stripping inner `0x6558` `ETH_P_TEB` headers when present).
2. **`F01` Relocation Hazard Caught & Solved (`CONFIRMED` in Kernel RAM via `/dev/mem`)**:
   - In `ubnt_poll_host.ko` (`ET_REL` MIPS ELF), zeroing the 4-byte `jal ubnt_poll_host_sta_bmiss_ind` instruction at `.text+0x7800` (`file offset 30784`) without zeroing its 8-byte `.rel.text` entry (`R_MIPS_26` at `file offset 168536`) causes the MIPS kernel loader (`0x8000c99c`) to write the target symbol's low 26 bits into the zeroed word. Zeroing **both** `30784` and `168536` (`R_MIPS_NONE`) produces a true `0x00000000` (`nop`) in live kernel RAM (`MD5: 077d151e0055f198609dc761a39207b3` on `WA.v8.7.25`, `7b490ac4d9573dab010b5f4fb95c3765` on `XC.v8.7.25`), surviving 35s AP outages with zero panics.
3. **`Rocket Prism 5AC Gen2` (`0xe7e9`) Dual-Radio AirPrism & `IRQ 64` TX-Blanking Architecture (`CONFIRMED` Static + Live Bench)**:
   - `Rocket Prism 5AC Gen2` (`BOM 13-00545-14`) uses `QCA9558` (`720 MHz`, `128 MB` RAM) + `QCA9880v2` (`wifi0`), switches its 2-stage active RF filter via **`GPIO 13..16`** using `ubnt_prism_hook`'s **band-edge (`center ± width/2`) 6-entry table**, and synchronizes its dedicated `wifi1` (`ath_ahb`) AirView scanner via hardware **`GPIO 21` / `IRQ 64` (`ath-spectral-filter`, `1,415` live interrupts observed)**.
4. **`LTU` (`amesoc3` + `AD9361` + `Arria 10` on Rocket) `4096-QAM` (`12X`) & `OFDMA` Silicon Capability (`CONFIRMED` on Live `LTU-Lite` `0xae08`)**:
   - Live `/sys/class/ame/ame_ctrl_dev/hw_features` on retail `LTU-Lite` (`0xae08`) confirmed **`NO_LDPC: 0` and `NO_OFDMA: 0`**. Setting `autoMcsCeiling = 31` (`0x1f`) in sysfs transitions the scheduler (`sched_mcs`) to **`MIMO MCS:FB:4096l`** (`12x`, **`560.64 Mbps` aggregate capacity on a single `40 MHz` channel** in `ameeng.cgi` `frmcfg`), awaiting only a 2nd LTU unit (`LTU-Rocket`) for over-the-air RF constellation verification.
5. **Upstream `CAKE` + `VHT20/40` + `AQL/ATF` + `CoTSQ` Deliver Immediate Proven Multi-Station Gains (`CONFIRMED` Stages 4–9)**:
   - On 3-station heterogeneous PtMP sectors, upstream `CAKE` + AP `AQL 1500/3000` + `ATF` + CPE `CoTSQ`/`fq_codel` + `VHT20/40` width optimization reduced loaded `p95` latency by **`9x–47x`** and boosted obstructed-station goodput by **`3.05x`** (`3.342 bit/s/Hz` DL / `3.656 bit/s/Hz` UL).

---

## 2. Master Decision Matrix: `DO NOW` / `LAB NEXT` / `CONDITIONAL` / `NO-GO`

| Category | Initiative / Technique | Target Scope | Prerequisites / Dependencies | Expected Impact / ROI | Primary Blocker / Risk |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **`DO NOW`** | **1. Passive Cooperative Fleet Sensor Observatory (`FMX-0016`, `FMX-0018`)** | All `1,800` radios (Read-only from NOC) | None (uses existing `mca-status`, `wstalist`, `ameeng.cgi`, `controller/advisory_mode.py`) | **High**: Automatic detection of airtime-tax culprits, chain imbalance (`>= 6 dB`, e.g., `GALEANO` `10 dB`), localized interference vs AP faults, and PoE/Ethernet 10Mbps downshifts. | Zero RF/device risk. Must keep poll rate `<= 1 poll / 60s` per CPE. |
| **`DO NOW`** | **2. Upstream POP/Core `CAKE diffserv4 nat ack-filter` + Per-Sector Capacity Forecasting** | NOC / Core Routers (`MK2-RS` / Linux Gateway) | None (zero radio changes required; 100% compatible with Stock `airMAX` & `LTU` TDMA) | **Very High**: Proven `18.97 ms -> 2.00 ms` loaded `p95` RTT reduction and `+49.4%` bidirectional TCP sector goodput (`FMX-0006`). | Requires CPU headroom at POP router/gateway (`omarchygwy`). |
| **`DO NOW`** | **3. Central NOC `ZeroClaw` / Deterministic Controller (Architecture B Control Plane)** | NOC Server (`omarchygwy`) | `controller/distributed_compute.py` + `controller/advisory_mode.py` (`22/22` tests passing) | **High**: Automated anomaly triage, conflict-graph channel/width recommendations, and canary plan generation with zero rooftop credential exposure. | LLM stays strictly advisory; deterministic gates own execution. |
| **`LAB NEXT`** | **4. `Step 1D` (`FMX-0017`): Multi-CPE OTA Discovery-IE Pulse & Loaded Soak on Unmodified Stock `airOS 8`** | Isolated Bench (`LAP-120` OpenWrt `wds=1` $\leftrightarrow$ 2x Stock `WA.v8.7.25` CPEs) | Operator authorization for next bench RF window (following `Step 1C` `run17` `PASS`) | **Critical**: Proves that pulsing the `msg_type=1` Beacon IE for `0.5s` to onboard a 2nd Stock CPE does not disturb an already-associated Stock CPE (`Path B`). | Must pass before any production AP migration is considered. |
| **`LAB NEXT`** | **5. `Rocket Prism 5AC Gen2` (`0xe7e9`) `wifi1` + `IRQ 64` Continuous Spectrum Observatory (`FMX-0019`)** | Isolated Bench (`Rocket198` + `Loco195`) | Bench authorization | **High**: Enables continuous 5 GHz interference mapping without the `102.4 ms` single-radio off-channel scan sawtooth (`DEC-013`). | None on bench. |
| **`LAB NEXT`** | **6. `LTU-Rocket` $\leftrightarrow$ `LTU-Lite` Over-the-Air `4096-QAM` (`12X`) & `OFDMA` Subband Qualification (`FMX-0021`)** | Isolated Bench (`LTU-Rocket` + `LTU-Lite` `0xae08`) | Physical connection of `LTU-Rocket` (or 2nd LTU unit) on bench | **High**: Up to **`+20%` goodput (`560.64 Mbps` @ `40 MHz`)** on short/high-SNR LTU links via RAM/sysfs `autoMcsCeiling=31` (`zero` flash writes). | Requires 2nd LTU radio on bench to establish RF link. |
| **`LAB NEXT`** | **7. Bench Qualification of `/tmp/fmx_micro_worker` Idle-Window Compute (`FMX-0020`)** | Isolated Bench (`Loco195` `AR9342` & `LTU-Lite` `amesoc3`) | Cross-compile `controller/fmx_micro_worker.c` (`< 48 KB` static ELF) | **Medium-High**: Validates `< 200 ms` traffic preemption, `5%/10%` duty-cycle accuracy, and zero RTT impact on real hardware. | Must pass bench preemption gate before any fleet pilot. |
| **`CONDITIONAL`** | **8. Fleet Idle-Window (`02:00–07:00`) Distributed Batch Compute (`Section 5`)** | Up to `~1,400` idle CPEs (never APs) | Passing `FMX-0020` bench gate + explicit operator authorization | **Conditional GO ONLY for**: (a) distributed network/DNS/CDN edge tomography, (b) local RF/spectral digest compression, and (c) integer/combinatorial Monte Carlo sweeps (`~3.5–7.0` modern cores equivalent at `5–10%` duty). | **Inferior to 1 NOC server (`Ryzen 9 7950X`) per watt** (`6.4x–9.5x` worse energy efficiency) for pure CPU crunching. |
| **`CONDITIONAL`** | **9. Cooperative CPE Assistance via Alternate-Sector Re-Parenting or Dual-Radio Ethernet Relay (`FMX-0024`)** | Obstructed CPEs with neighbor visibility | `FMX-0016` scan matrix / `$49` auxiliary `Loco5AC` | **High for Obstructed Links**: Solves tree/building blockage without halving primary sector airtime. | Requires either overlapping secondary AP coverage or a 2nd radio at relay site. |
| **`NO-GO`** | **10. Running `ZeroClaw v0.8.6` (or Full Rust/LLM Agents) Directly on `1,800` CPEs (`Section 6` Arch A)** | Stock `airOS 8` (`64 MB` RAM, Linux `2.6.32.68`) & Customer Rooftops | — | **Zero / Negative** | **`HARD NO-GO`**: Kernel `2.6.32.68` syscall incompatibility, `3.4–6.8 MB` binary / `7.5–14 MB` `/tmp` RAM tax on `64 MB` radios, and unacceptable rooftop API key / shell security risk. |
| **`NO-GO`** | **11. Crypto Mining, Distributed LLM Inference, or Dense FP64 Linear Algebra on CPEs (`Section 5`)** | `AR9342` (`MIPS 74Kc`, no FPU, `64 MB` RAM) | — | **Negative ROI** | **`HARD NO-GO`**: `MIPS 74Kc` lacks FPU (`56,470:1` slower per core than AVX-512 at 10% duty) and `64 MB` RAM cannot hold LLM weights or RandomX scratchpads. |
| **`NO-GO`** | **12. `2.4 GHz` Management Radio (`wifi1`) Mesh Backhaul Across Customer Homes (`Section 2.B`)** | `WA` / `XC` / `LTU` `2.4 GHz` Setup Radio | — | **Negligible** | **`NO-GO`**: `~1.5 dBi` internal PCB antenna + high urban `2.4 GHz` noise floor fails link budget beyond `< 25–50 m`. |
| **`NO-GO`** | **13. Cooperative PHY / Joint Decoding / Distributed MIMO Across Unsynchronized CPEs (`Section 2.A`)** | `QCA988x` / `AD9361` CPEs | — | **Impossible on Target Silicon** | **`HARD NO-GO`**: No sub-nanosecond carrier-phase synchronization or raw IQ sample backhaul between customer CPEs. |

---

## 3. Preliminary Decisions by Research Pillar (`Section 11.5` Summary)

1. **5 GHz Same-Radio Cooperative Relay (`CPE-A` helping `CPE-B` on the same radio)**:
   - **Verdict**: **`SKEPTICAL / LAB FALSIFICATION ONLY (`FMX-0022`)`**. Stock `airOS 8` TDMA (`ubnt_poll_host.ko`) blocks STA-to-STA forwarding completely. Under OpenWrt (`ath10k-ct`), `STA + AP` (or `STA + 802.11s`) on a single `QCA988x` radio faces two severe physical barriers: (a) directional CPE antennas (`10°–45°` beamwidth pointed at the AP) suffer `15–28 dB` sidelobe attenuation toward neighboring CPEs unless nearly collinear, and (b) two-hop half-duplex transmission on the same channel doubles MAC overhead and only reduces net sector airtime if **both** hops run at `> 2x` the direct `B -> AP` PHY rate. Test strictly on the bench (`FMX-0022`); for production obstructed links, prefer **Dual-CPE Ethernet Relay (`FMX-0024`)** or **Alternate-Sector Re-Parenting (`FMX-0016`)**.
2. **2.4 GHz Management Radio (`wifi1`)**:
   - **Verdict**: **`NO-GO` for Data Mesh**; **`CONDITIONAL` for `< 25 m` Emergency Local Access / Co-Located Sensor Telemetry (`FMX-0023`)**.
3. **Extra Dedicated Radio / Ethernet Back-to-Back Relay**:
   - **Verdict**: **`GO` (`FMX-0024`)** when physical obstruction blocks direct LOS to all existing APs. A second `$49` `Loco 5AC` on a non-overlapping frequency connected back-to-back via Ethernet completely eliminates same-channel airtime doubling.
4. **Cooperative CPE Sensors (Network-Wide RF & Health Observatory)**:
   - **Verdict**: **`IMMEDIATE GO (`DO NOW` — `FMX-0016`, `FMX-0018`, `FMX-0019`)`**. Highest immediate commercial ROI for the WISP with zero customer risk.
5. **Distributed Idle-Window Compute (`02:00–07:00`)**:
   - **Verdict**: **`GO` for Network-Local Edge Probing, Spectral Compression & Integer/Combinatorial Sweeps (`FMX-0020`)** using the `< 48 KB` RAM-only C micro-worker (`controller/fmx_micro_worker.c`) and deterministic NOC controller (`controller/distributed_compute.py`); **`HARD NO-GO` for dense FP64, LLM inference, or crypto mining**.
6. **`ZeroClaw` (`v0.8.6`) on CPEs vs Central NOC**:
   - **Verdict**: **`HARD NO-GO` on Edge CPEs (Architecture A)**; **`GO` at Central NOC (Architecture B)**.

---

## 4. Single Next Action with Maximum Information-to-Risk Ratio (`Section 11.6`)

- **Offline / Zero-Risk Immediate Action (`Executed Today`)**:
  - Run the automated verification suite (`pytest tests/test_distributed_compute.py`) validating the deterministic idle-window compute controller (`controller/distributed_compute.py`), HMAC-SHA256 manifest signing, `< 200 ms` preemption logic, and fleet power/throughput economics model.
- **Next Authorized Bench Action (When Operator Opens Next Bench Session)**:
  - Execute **`FMX-0017` (`Step 1D` — Multi-CPE OTA Discovery-IE Pulse & Loaded Soak Qualification)** on the isolated bench (`LAP-120` OpenWrt `wds=1` $\leftrightarrow$ unmodified Stock `WA.v8.7.25` `Loco195`) to prove that an already-associated Stock `airOS 8` CPE (`Path B`, `connected_ap == NULL`) remains `100%` stable (`0` disconnects, `0%` packet loss) when the AP pulses its `0.5s` Ubiquiti discovery IE to onboard a second Stock CPE.
