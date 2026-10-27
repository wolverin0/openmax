<!-- doc-head: WISP_EDGE_SCRIPTS_AND_INTELLIGENCE.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE.md) | Part 2/2
<a id="openmax--futuramax--cooperative-cpe-sensor-intelligence--edge-script-specification"></a> [OpenMax / FuturaMAX — Cooperative CPE Sensor Intelligence & Edge Script Specification](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#openmax--futuramax--cooperative-cpe-sensor-intelligence--edge-script-specification) | <a id="1-architectural-principle-central-controller-polling-vs-on-cpe-edge-scripts"></a> [1. Architectural Principle: Central Controller Polling vs. On-CPE Edge Scripts](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#1-architectural-principle-central-controller-polling-vs-on-cpe-edge-scripts) | <a id="2-cooperative-cpe-sensor--wisp-intelligence-engine"></a> [2. Cooperative CPE Sensor & WISP Intelligence Engine](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#2-cooperative-cpe-sensor--wisp-intelligence-engine) | <a id="21-per-cpe-airtime-tax-detector--the-qca988x-estimation-boundary"></a> [2.1 Per-CPE Airtime Tax Detector & The `QCA988x` Estimation Boundary](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#21-per-cpe-airtime-tax-detector--the-qca988x-estimation-boundary) | <a id="accounting-for-qca988x-wave-1-telemetry-limits-confirmed-in-knowledgeqca988x_control_boundarymdfileg_onedriveonedrivedesktoppy20appsfuturamaxknowledgeqca988x_control_boundarymdl73-l141"></a> [Accounting for `QCA988x` Wave-1 Telemetry Limits (`CONFIRMED` in \[`knowledge/QCA988X_CONTROL_BOUNDARY.md`\](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/knowledge/QCA988X_CONTROL_BOUNDARY.md#L73-L141))](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#accounting-for-qca988x-wave-1-telemetry-limits-confirmed-in-knowledgeqca988x_control_boundarymdfileg_onedriveonedrivedesktoppy20appsfuturamaxknowledgeqca988x_control_boundarymdl73-l141) | <a id="22-spatial-differential-fault-localizer-controllercooperative_sensorpy"></a> [2.2 Spatial Differential Fault Localizer (`controller/cooperative_sensor.py`)](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#22-spatial-differential-fault-localizer-controllercooperative_sensorpy) | <a id="concrete-real-fleet-examples-validated-by-this-logic"></a> [Concrete Real-Fleet Examples Validated by This Logic](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#concrete-real-fleet-examples-validated-by-this-logic) | <a id="23-sector-re-association-recommender--closed-loop-controls"></a> [2.3 Sector Re-Association Recommender & Closed-Loop Controls](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#23-sector-re-association-recommender--closed-loop-controls) | <a id="3-prioritized-catalog-of-the-10-edge-scripts-airos-8-openwrt-ltu"></a> [3. Prioritized Catalog of the 10 Edge Scripts (`airOS 8`, `OpenWrt`, `LTU`)](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#3-prioritized-catalog-of-the-10-edge-scripts-airos-8-openwrt-ltu) | <a id="31-critical-safety--platform-invariants-mandatory-for-all-scripts"></a> [3.1 Critical Safety & Platform Invariants (Mandatory for All Scripts)](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#31-critical-safety--platform-invariants-mandatory-for-all-scripts) | <a id="32-master-priority-table-of-the-10-edge-scripts"></a> [3.2 Master Priority Table of the 10 Edge Scripts](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#32-master-priority-table-of-the-10-edge-scripts) | <a id="33-detailed-implementation-recipes--code-for-all-10-scripts"></a> [3.3 Detailed Implementation Recipes & Code for All 10 Scripts](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#33-detailed-implementation-recipes--code-for-all-10-scripts) | <a id="script-1-script-07-poe-ethernet-link-flap-duplex--reboot-cause-auditor"></a> [Script #1 (`SCRIPT-07`): PoE, Ethernet Link-Flap, Duplex & Reboot-Cause Auditor](WISP_EDGE_SCRIPTS_AND_INTELLIGENCE_CONTINUATION_65f944f065_001.md#script-1-script-07-poe-ethernet-link-flap-duplex--reboot-cause-auditor)

<!-- stage822a-payload-begin -->

#### Script #2 (`SCRIPT-04`): L2-Scoped RF Association & Hybrid Interop Watchdog
* **Problem Solved**: Ensures hands-free association recovery without false reboots during upstream router maintenance or `countrycode=511` boot scans.
* **Platform Variants**:
  1. **OpenWrt AP (`LAP-120` / `LAP-GPS`) — `CONFIRMED ON BENCH` (`FMX-0014`)**:
     - Supervised by `/etc/init.d/futuramax` (`procd`) running [`controller/fmx_watchdog.sh`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/fmx_watchdog.sh) and [`controller/fmx_adaptive_controller.sh`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/fmx_adaptive_controller.sh). Automatically rolls back experimental bitrates/AQL/aggregation to safe defaults (`2 32` A-MPDU, `2000/4000 µs` AQL) if `MemAvailable < 8192 kB` or `phy0-ap0` goes down for 3 consecutive checks.
  2. **Stock `airOS 8` CPE (`WA` / `XC`) — Hardened Recipe (`<= 2,000` bytes)**:
     - Incorporates the `[ $(cut -d. -f1 /proc/uptime) -lt 180 ] && exit 0;` boot-scan guard, atomic `/tmp/uph.l` lock, L2 `iwconfig ath0` check, MD5 allowlist (`5bb5c...`, `7c76c...`, `5b26b...`), 4-site relocation-safe `/tmp/uph.ko` splice (`F01`), and scoped `sed` edits (`STAGE10` Section 4).

---

#### Script #3 (`SCRIPT-06`): Read-Only Calibration (`ART`/`EEPROM`) & Config Drift Verifier
* **Problem Solved**: Verifies that `u-boot` (`mtd0`), `u-boot-env` (`mtd1`), and `EEPROM/ART` (`mtd5` on `WA`/`XC`, `mtd4` `@0x00240000` on `LTU`) have 100% intact cryptographic hashes and detects unauthorized configuration drift.
* **Read-Only Audit Command**:
  ```sh
  # Strictly read-only: computes SHA256/MD5 of protected partitions and running config
  awk -F: '/mtd[0-9]+/{gsub(/"/,"",$2); print $1,$2}' /proc/mtd | while read dev name; do
    case "$name" in
      u-boot|uboot|EEPROM|ART)
        h=$(md5sum "/dev/$dev" 2>/dev/null | awk '{print $1}')
        printf '{"mtd":"%s","name":"%s","md5":"%s"}\n' "$dev" "$name" "$h"
        ;;
    esac
  done > /tmp/fmx_partition_audit.jsonl
  ```

---

#### Script #4 (`SCRIPT-01`): Compact Enriched Heartbeat Emitter (`/tmp/fmx_hb.json`)
* **Problem Solved**: Provides a unified `< 256`-byte JSON telemetry record across `airOS 8`, `OpenWrt`, and `LTU` containing timestamp, uptime, RSSI, per-chain power (`Chain 0` vs `Chain 1`), CINR/SNR, TX/RX MCS, TX retries, `eth0` state, and free RAM.
* **Platform Commands**:
  - **Stock `airOS 8`**: Parses `mca-status` (single fork, `< 15 ms` on `AR9342`) + `/sys/class/net/eth0/speed`.
  - **OpenWrt (`ath10k-ct`)**: Pure shell `read` of `/sys/kernel/debug/ieee80211/phy0/netdev:phy0-ap0/stations/<mac>/airtime` (`0` forks per station, as proven in [`controller/fmx_adaptive_controller.sh`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/fmx_adaptive_controller.sh#L34-L40)).
  - **Stock `LTU` (`afltu`)**: Reads `/usr/www/ameeng.cgi` (`bbp.currentMcs`, `frmcfg.rate_cur`) and `/sys/kernel/debug/ame/automcs`.

---

#### Script #5 (`SCRIPT-08`): Dual-DSCP (`EF` vs `CS0`) Differential Queue-Delay Micro-Probe
* **Problem Solved**: Passively separates **RF channel degradation** from **bufferbloat / `Deficit: BE` queuing delay** using only 4 tiny ICMP packets per minute!
* **Mechanism (`CONFIRMED` via Stage 7.4 Discovery)**:
  - Sends 2 ICMP echo probes to the sector AP IP with **`TOS = 0x00` (`DSCP CS0` -> `WMM AC_BE`)** (`ping -c 2 -W 1 -Q 0x00 <AP_IP>`) and 2 probes with **`TOS = 0xb8` (`DSCP EF` -> `WMM AC_VO`)** (`ping -c 2 -W 1 -Q 0xb8 <AP_IP>`).
  - **Diagnostic Signature**:
    - If $\text{RTT}_{\text{AC\_BE}} - \text{RTT}_{\text{AC\_VO}} \ge 25\text{ ms}$ while $\text{RTT}_{\text{AC\_VO}} < 10\text{ ms}$: The RF link is alive, but `AC_BE` is suffering bufferbloat or negative `Deficit: BE` starvation! Fix via `CoTSQ 128 KB` + `fq_codel quantum 300` + `fmx_fastpath` `DSCP EF` promotion.
    - If **both** $\text{RTT}_{\text{AC\_BE}}$ and $\text{RTT}_{\text{AC\_VO}}$ jump above `40 ms` with packet loss: True RF layer contention, hidden-node collision (enable `RTS/CTS = 256B`), or backhaul congestion.

---

#### Script #6 (`SCRIPT-02`): Local Edge Anomaly Summarizer (Delta-Only Ringbuffer)
* **Problem Solved**: Avoids polling 1,800 CPEs every 5 seconds over the air by maintaining a 16-entry circular buffer in `/tmp/fmx_ring.log` (`< 16 KB` RAM) and emitting an alert line **only** when a metric crosses a hysteresis threshold ($\Delta\text{RSSI} \ge 4\text{ dB}$, $|\text{Chain}_0 - \text{Chain}_1| \ge 6\text{ dB}$, `eth0` flap, or `tx_retries` jump $> 15\%$).

---

#### Script #7 (`SCRIPT-05`): Event-Triggered Flight Recorder (Pre/Post Drop Snapshot in `/tmp`)
* **Problem Solved**: When a CPE briefly disassociates at 03:15 AM and reassociates at 03:16 AM, central polling misses the transient cause.
* **Mechanism**: When `SCRIPT-04` or `SCRIPT-02` detects an association drop or `bmiss`, it snapshots the last 30 lines of `dmesg`, `/var/log/messages` (`wpa_supplicant` reason codes), `mca-status`, and `iwconfig ath0` into `/tmp/fmx_blackbox_last.txt` (capped at `32 KB` in `/tmp`, overwriting any older snapshot so `/tmp` never fills). When the CPE reconnects, the central controller fetches `/tmp/fmx_blackbox_last.txt` to see the exact deauth/beacon-miss/DFS-CSA sequence.

---

#### Script #8 (`SCRIPT-09`): Non-Disruptive Auxiliary RF / Spectral Snapshot (`XC` `wifi1` & `LTU` Subbands)
* **Problem Solved**: Captures real-time interference without interrupting customer traffic on the primary radio.
* **Strict Platform Rules**:
  - **On `Rocket Prism 5AC Gen2` (`XC` `0xe7e9`)**: Uses the dedicated `wifi1` (`ath_ahb`) AirView scanner (`ubntspecd` / `ath-spectral-filter` `IRQ 64`), which is hardware TX-blanked via `GPIO 21` and causes **0% throughput loss** on `wifi0`.
  - **On `LTU` (`0xae08` / `0xea10`)**: Reads `/sys/kernel/debug/ame/automcs` (`SB0..SB7` per-subband DL quality across the 8 OFDMA subbands) at zero RF cost.
  - **On Single-Radio `WA` / OpenWrt (`0xe7f9`, `0xe7fa`, `0xe8e5`)**: **NEVER** run `iw dev phy0-ap0 scan ap-force` during customer service (triggers the Stage 9A `102.4 ms` beacon sawtooth bug!). Instead, read passive `ath10k` spectral FFT background bins or schedule scans strictly during maintenance windows.

---

#### Script #9 (`SCRIPT-03`): Idle-Window (`02:00–07:00`) Batch Compute Lease Runner & Preemption Guard
* **Problem Solved**: Safely executes a signed, RAM-only micro-worker binary (`/tmp/fmx_worker`) during verified off-peak hours (`02:00–07:00` local time) **only** when the CPE and sector are genuinely idle, and terminates within `< 100 ms` the instant subscriber traffic appears.
* **Hard Preemption Guards (Evaluated Every `1s` by Local Wrapper)**:
  1. **Lease TTL Check**: Worker lease expires automatically after `300s` if the central controller stops renewing it (fail-safe stop on controller outage).
  2. **Subscriber Traffic Guard**: Reads `/sys/class/net/eth0/statistics/rx_bytes` and `tx_bytes`. If subscriber throughput exceeds **`64 kbps` (`8 KB/s`)**, sends `SIGKILL` (`kill -9`) to `/tmp/fmx_worker` immediately.
  3. **Memory & Load Guard**: Requires `MemFree >= 16384 kB` (`16 MB`) on `64 MB` `WA` CPEs (`>= 65536 kB` on `256 MB` `LTU`).
  4. **CPU Quota Enforcement**: Because `nice -n 19` alone does not cap thermal/power dissipation on an idle single-core `AR9342`, the wrapper enforces explicit duty-cycle throttling (`SIGSTOP` / `SIGCONT` duty cycle or internal batch sleep) to cap wall-clock CPU at `5%–20%`.

---

#### Script #10 (`SCRIPT-10`): Isolated Bench Micro-Benchmark Harness (`CPU / Memory / Crypto`)
* **Problem Solved**: Measures deterministic work-per-device-hour and latency impact on isolated bench hardware (`Loco195`, `LAP-120`, `Rocket198`, `LTU-Lite`) before sizing any distributed compute workload.
* **Safety Gate**: Refuses to execute unless `/tmp/BENCH_AUTHORIZED` exists and `ip route` confirms the isolated lab subnet.
<!-- stage822a-payload-end -->
