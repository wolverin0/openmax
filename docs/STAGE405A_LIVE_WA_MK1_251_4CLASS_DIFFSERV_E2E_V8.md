<!-- doc-head: STAGE405A_LIVE_WA_MK1_251_4CLASS_DIFFSERV_E2E_V8.md preserved document content -->
<!-- /doc-head -->


# Stage 405A — Live End-to-End `CPE .250 -> AP .20 -> Boca 7 MK1-251` 4-Class DiffServ QoE Audit (`S405A-E2E-R4`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `Stage 405A` (`S405A-E2E-R4`)
- **4-Class DiffServ Architecture Verified**:
  1. **`CS0` (`0x00`, `AC_BE` / `TID 0`)**: Bidirectional Bulk TCP (`iperf3 -P 4 --bidir`).
  2. **`AF21` / `CS6` (`0x48` / `0xc0`, `TID 7` / `AC_VO` Control)**: Low-latency transactional / E2E control probes (`23` packets/window explicitly steered into `TID 7` `AC_VO` in `Arm B` vs `0` in `Arm A`).
  3. **`AF41` (`0x88`, `AC_VI` / `TID 4`)**: IPTV multicast/video stream (`4.91 Mbps`, `1,422` packets/window in `TID 4`, `0.0%` loss).
  4. **`EF` (`0xb8`, `AC_VO` / `TID 6`)**: VoIP real-time voice stream (`0.123 Mbps`, `294–301` packets/window in `TID 6`, `0.0%` loss).
- **Primary Artifact**: [`artifacts/autoresearch/stage405a_live_wa_mk1_251_4class_diffserv_e2e_v8.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage405a_live_wa_mk1_251_4class_diffserv_e2e_v8.json)

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` 4-Class DiffServ Comparison

| Metric | `Arm A`: Stock `OpenWrt 24.10.4` (`A1`, `A2`) | `Arm B`: Universal `WA` Champion `v8` (`B1`, `B2`) | Delta (`Arm B` vs `Arm A`) |
| :--- | :---: | :---: | :---: |
| **Mean Total Goodput (`Mbps`)** | `74.578 Mbps` (`74.693`, `74.464`) | `70.875 Mbps` (`71.278`, `70.472`) | `-4.97%` (airtime reserved for `AC_VO`/`AC_VI`) |
| **Wireless Hop `RF_p50` (`CS0` Bulk Load)** | `34.596 ms` (`32.348`, `36.845`) | **`24.538 ms`** (`28.918`, **`20.158`**) | **`-29.07%` (`-10.058 ms`)** |
| **End-to-End `MK1_p50` (`AF21`/`CS6` + `EF`)** | `12.284 ms` (`11.142`, `13.425`) | **`5.621 ms`** (**`3.613`**, `7.628`) | **`-54.24%` (`-6.663 ms`)** |
| **End-to-End `MK1_p95` (`AF21`/`CS6` + `EF`)** | `26.914 ms` (`32.585`, `21.242`) | **`20.963 ms`** (`31.661`, **`10.264`**) | **`-22.11%` (`-5.951 ms`)** |
| **`AF41` IPTV (`TID 4` `AC_VI`) Loss / Jitter** | `0.0%` / `1.441 ms` | **`0.0%` / `1.701 ms`** (`1,422` `TID 4` pkts) | `100%` Loss-Free IPTV Delivery |
| **`EF` VoIP (`TID 6` + `TID 7` `AC_VO`) Steering** | `0` `TID 7` pkts (unclassified control) | **`23` `TID 7` + `301` `TID 6` pkts (`0.0%` loss)** | **Hardware WMM `AC_VO` Isolation Proven** |
