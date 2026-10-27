<!-- doc-head: STAGE12_OPENWRT_FUTURA_QOE_PROCD_DAEMON_SPEC.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — Production OpenWrt `/etc/init.d/futura-qoe` `procd` Daemon & Dynamic Autopilot Specification

**Status**: `CONFIRMED` (Physical Bench Anchors `R76..R120` + Unit Verified)  
**Deliverables**:
- [`controller/openwrt_futura_qoe_daemon_generator.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/openwrt_futura_qoe_daemon_generator.py)
- [`artifacts/canary_panel1_guarida/openwrt_futura_qoe_procd_bundle_20261024.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/canary_panel1_guarida/openwrt_futura_qoe_procd_bundle_20261024.json)
- [`tests/test_openwrt_futura_qoe_daemon_generator.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_openwrt_futura_qoe_daemon_generator.py)

---

## 1. Executive Summary & Control Boundary

Across physical bench rounds `R76..R120` (`LAP-120` AP `192.168.1.210` $\leftrightarrow$ `NanoStation 5AC Loco` CPE `192.168.1.195`, OpenWrt `24.10.4` `r28959`, `6.6.110`, `ath10k-ct` `10.1.467-ct-com-full-015-96146b`, `VHT20` `5800 MHz`), we proved (`CONFIRMED`) that static `mac80211` AQL limits cannot simultaneously optimize bidirectional 8-flow congestion, pure downlink bulk, and long-distance (`1..14 km`) pure uplink bulk:

1. **Bidirectional Congestion (`BIDIR_CONGESTED`, `CONFIRMED` `R97..R102`)**:
   - Tight asymmetric AQL (`AP BE = 1550/3100 us`, `CPE BE = 2100/4200 us`, `codel = 8/40 ms`, `RC = 24%`, `TSQ = 256 KB`) eliminates TCP DATA/ACK head-of-line queuing across `3..14 km`, improving aggregate goodput by `+4.0%..+8.2%` while cutting `p95` loaded RTT by `-78%..-83%` (`74..85 ms` $\rightarrow$ `9.96..16.59 ms`, `0%` packet loss).
2. **Unidirectional Downlink Dominant (`UNIDIR_DL_DOMINANT`, `CONFIRMED` `R103..R107`)**:
   - Raising `AP BE` from `1550/3100 us` to `1900/3800 us` (`thresh = 7600 us`) while keeping `CPE BE = 2100/4200 us` eliminates the `-7.9%` long-slot turnaround TXQ starvation dip at `3..14 km`, preserving `98.3%..101.4%` of Stock DL goodput while cutting `p95` RTT from `33..40 ms` to `9.06..14.21 ms` (`-64%..-77%`).
3. **Unidirectional Uplink Dominant (`UNIDIR_UL_DOMINANT`, `CONFIRMED` `R82`, `R108..R109`, `R116..R120`)**:
   - Under pure UL at `1..12 km` (`coverage_class = 2..26`), static `CPE BE = 2100/4200 us` + `TSQ = 256 KB` starved the QCA988x DMA ring during long-slot ACK turnarounds (`R108` `-7.31%`, `R109` `-8.44%`).
   - Applying the **Concave-Logarithmic UL Distance Law**:
     $$\text{CPE\_BE\_LOW}(c) = \text{round}_{50}\!\left(2100 + 646 \cdot \ln(1 + 0.65 \cdot c)\right)$$
     paired with `AP BE = 1900/3800 us` (`1520/3040` at `c=0`), `CPE TSQ = 1 MB` (`1048576`), `CPE RC = 50%`, `CPE codel = 16/80 ms`, and `retry = 7/4` recovered **100% of Stock UL goodput (`-1.72%..+3.56%`)** while cutting `p95` loaded RTT by **`-74.8%..-84.7%` (`42.9..69.5 ms` $\rightarrow$ `10.64..11.00 ms`)** across `1 km`, `3 km`, `6 km`, `9 km`, and `12 km` (`R116..R120` all `KEEP`).
4. **Multi-Uploader Uplink Hammering Protection (`INFERRED` from Stage 7 `CONFIRMED` `RTS=256B` + Mission 3 Soft-TDMA Return-ACK Pacing)**:
   - When `N_ul >= 2` stations simultaneously transmit $\ge 250\text{ kbps}$ uplink, the AP dynamically enables `iw phy phy0 set rts 256` (switching back to `iw phy phy0 set rts off` when `N_ul <= 1` to preserve single-link overhead efficiency).

---

## 2. Verified Physical Bench Anchor Table (`CONFIRMED`)

| Round | Regime | Distance ($m$) | `coverage_class` ($c$) | Slot / ACK ($\mu\text{s}$) | AP BE ($\mu\text{s}$) | CPE BE ($\mu\text{s}$) | Stock Goodput (Mbps) | FMX Goodput (Mbps) | $\Delta$ Goodput | Stock `p95` (ms) | FMX `p95` (ms) | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `R82` | `UNIDIR_UL_DOMINANT` | $100\text{ m}$ | `0` | `9 / 18` | `1520/3040` | `2100/4200` | `66.49` | `66.23` | `-0.39%` | `15.84` | `9.16` | **KEEP** (`CONFIRMED`) |
| `R98` | `BIDIR_CONGESTED` (8-flow) | $3000\text{ m}$ | `6` | `27 / 54` | `1550/3100` | `2100/4200` | `59.60` | `63.83` | **`+7.09%`** | `79.16` | `15.39` | **KEEP** (`CONFIRMED`) |
| `R103..R107` | `UNIDIR_DL_DOMINANT` | $3..14\text{ km}$ | `6..31` | `27..102` | `1900/3800` | `2100/4200` | `52.9..68.8` | `53.6..68.7` | `-1.74%..+1.38%` | `33.1..39.9` | `9.06..14.21` | **KEEP** (`CONFIRMED`) |
| `R116` | `UNIDIR_UL_DOMINANT` | $1000\text{ m}$ | `2` | `15 / 30` | `1900/3800` | `2650/5300` | `59.19` | `59.26` | **`+0.12%`** | `43.64` | `10.98` | **KEEP** (`CONFIRMED`) |
| `R117` | `UNIDIR_UL_DOMINANT` | $3000\text{ m}$ | `6` | `27 / 54` | `1900/3800` | `3150/6300` | `60.46` | `59.43` | `-1.70%` | `42.86` | `10.64` | **KEEP** (`CONFIRMED`) |
| `R118` | `UNIDIR_UL_DOMINANT` | $6000\text{ m}$ | `13` | `48 / 96` | `1900/3800` | `3550/7100` | `53.14` | `52.23` | `-1.72%` | `60.30` | `10.96` | **KEEP** (`CONFIRMED`) |
| `R119` | `UNIDIR_UL_DOMINANT` | $9000\text{ m}$ | `20` | `69 / 138` | `1900/3800` | `3800/7600` | `48.30` | `50.02` | **`+3.56%`** | `69.52` | `10.66` | **KEEP** (`CONFIRMED`) |
| `R120` | `UNIDIR_UL_DOMINANT` | $12000\text{ m}$ | `26` | `87 / 174` | `1900/3800` | `3950/7900` | `47.40` | `47.68` | **`+0.59%`** | `61.07` | `11.00` | **KEEP** (`CONFIRMED`) |

---

## 3. Daemon Architecture (`/etc/init.d/futura-qoe` + `/usr/sbin/futura-qoe-autopilot`)

1. **Zero External Dependencies (`CONFIRMED`)**:
   - Written in pure POSIX `/bin/sh` + BusyBox `awk` so it executes natively on any OpenWrt `24.10.4` `ath79/generic` image (`64 MB` or `128 MB` RAM) without Python or Lua runtime overhead.
2. **2-Second Closed-Loop Control Cycle**:
   - Reads `/sys/kernel/debug/ieee80211/phy0/ath10k/coverage_class` (`0..31`).
   - Computes 2-second TX/RX byte deltas across `/sys/class/net/phy0-ap0/statistics/{tx,rx}_bytes` (or `phy0-sta0` on CPE) and per-station RX byte deltas across `/sys/kernel/debug/ieee80211/phy0/netdev:phy0-ap0*/stations/*/rx_bytes`.
   - Classifies regime (`UNIDIR_DL_DOMINANT`, `UNIDIR_UL_DOMINANT`, `BIDIR_CONGESTED`) and active uploading station count `N_ul` ($\ge 250\text{ kbps}$).
   - Writes sysfs/debugfs/sysctl/iw updates **only when the state signature `${ROLE}_${REGIME}_${COV}_${BE_LOW}_${RTS_MODE}` changes** (zero unnecessary sysfs churn).
   - Exports live telemetry snapshot to `/tmp/futura_qoe_state.json`.
3. **Mandatory Safety & OOM Watchdogs (`CONFIRMED`)**:
   - Pins `/proc/<pid>/oom_score_adj = -900` on `hostapd` and `wpa_supplicant`.
   - Bounds `mac80211` FQ memory to `fq_memory_limit = 4194304` (`4 MB`) and `fq_limit = 2048`.
   - Touching `/tmp/futura_qoe_disable` or invoking `/etc/init.d/futura-qoe stop` immediately restores Stock `5000/12000` (`aql_threshold = 24000`, `rts off`, `tcp_limit_output_bytes = 1048576`).
