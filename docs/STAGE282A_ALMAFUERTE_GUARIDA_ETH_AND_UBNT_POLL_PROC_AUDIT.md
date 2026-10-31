<!-- doc-head: STAGE282A_ALMAFUERTE_GUARIDA_ETH_AND_UBNT_POLL_PROC_AUDIT.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 282A — Read-Only Audit of `Almafuerte (.60)` & `Guarida (.61)` `/proc/1/net/uph_wifi0/*`, `/proc/sys/dev/uph_wifi0/*` & Ethernet Statistics

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`) + `QCA firmware` (`wal_dbg_stats`) + `Linux` (`eth0`/`br0`)
- **Safety Boundary**: `0` writes performed (`SG-01` Guarida Backbone Rule strictly enforced)
- **Receipt**: [`artifacts/autoresearch/stage282a_almafuerte_guarida_eth_and_ubnt_poll_proc_audit.json`](../artifacts/autoresearch/stage282a_almafuerte_guarida_eth_and_ubnt_poll_proc_audit.json)

---

## 1. `/proc/1/net/uph_wifi0/info` & `/proc/sys/dev/uph_wifi0/*` Live State (`CONFIRMED`)

In `WA.v8.7.25`, `ubnt_poll_host.ko` registers its procfs tables under `/proc/<pid>/net/uph_wifi0/` (`info`, `noack_info`, `sta_Scale`, `atpc`) and its sysctl knobs under `/proc/sys/dev/uph_wifi0/`.

| Metric / Knob | `198.18.0.3` (`Ap.Guarida`, Almafuerte AP) | `198.18.0.4` (`St.Guarida`, Guarida STA) | Diagnostic Assessment |
| :--- | :---: | :---: | :--- |
| `Channel / Width` | `5355 MHz [HT20]` (DFS) | `5355 MHz [HT20]` (DFS) | Vulnerable to DFS CAC & adjacent bleed |
| `NOACK` (`noack_info`) | `disabled` (`noack_mode=1`) | `disabled` (`noack_mode=1`) | Normal ACK mode |
| `DISTANCE` (`uph_wifi0/info`) | `3750 m` | `3750 m` (`ACK=47` $\mu	ext{s}$) | Clamped `18%` above true `3.19 km` (`ACK=39` $\mu	ext{s}$) |
| `DCAP / UCAP` | `72%` (`93.60 Mbps`) / `73%` (`113.88 Mbps`) | `72%` (`112.32 Mbps`) / `73%` (`113.88 Mbps`) | Asymmetric DL MCS drop on AP (`93.6 Mbps`) |
| `TXPER / RXPER` (per-mille) | `130` (`13.0%`) / `135` (`13.5%`) | `130` (`13.0%`) / `145` (`14.5%`) | High RF packet error rate (`13.0%–14.5%`) |
| `TXUSE / RXUSE / TLUSE` | `351` / `53` / `404` (`40.4%` airtime) | `44` / `186` / `230` (`23.0%` airtime) | `40.4%` total airtime utilization at `20 MHz` |
| `ptp_xmit` (`/proc/sys/dev/uph_wifi0`) | `0` (Disabled) | `0` (Disabled) | Unoptimized (Stage 73A/79A champion = `1`) |
| `daprot` (`/proc/sys/dev/uph_wifi0`) | `0` (Disabled) | `0` (Disabled) | Unoptimized dynamic airMAX protection (`2`) |
| `sta_priority` | `1 2 0` | `1 2 0` | Stock default |

---

## 2. Bridge (`br0`) & Ethernet (`eth0` to `.200` / `.201`) Counters (`CONFIRMED`)

| Interface Counter | `198.18.0.3` (`eth0` $\leftrightarrow$ `.200` Almafuerte) | `198.18.0.4` (`eth0` $\leftrightarrow$ `.201` Guarida) | Finding |
| :--- | :---: | :---: | :--- |
| `eth0 rx_packets` | `526,215,905` | `496,282,134` | Clean gigabit copper link on both ends |
| `eth0 tx_packets` | `178,897,533` | `1,435,677,434` | High multicast/DL forwarding toward `.201` |
| `eth0 rx_crc_errors` / `rx_frame_errors` | `0` / `0` | `0` / `0` | **Zero Ethernet physical layer CRC/FCS faults** |
| `eth0 rx_length_errors` | `0` | `1` | Negligible (`1` packet over `44.7` days) |
| `eth0 tx_dropped` | `1` | `42` | Negligible on `eth0` |
| `ath0 tx_dropped` | `3` | `128` | Low netdev drops; queuing occurs inside WAL |
| `br0` MAC table (`brctl showmacs br0`) | `42` MAC entries | `42` MAC entries | Carries full Guarida tower L2 domain (`32` CPEs + infra) |

---

## 3. True `QCA9882` `wal_dbg_stats` (`athstats -ol`) & `521.1s` DFS Outage Proof (`CONFIRMED`)

1. **True `QCA9882` WAL Retries & Requeues (`athstats -ol`)**:
   - **`.60` (`Almafuerte` AP)**: `mpdus_queued = 340,395,119`, **`mpdus_requed = 30,900,030` (`9.08%`)**, **`excess_retries = 4,170,241`**, `tx_underrun = 2,124`, `q1_stopped_cnt = 24`.
   - **`.61` (`Guarida` STA)**: `mpdus_queued = 389,389,903`, **`mpdus_requed = 18,934,701` (`4.86%`)**, **`excess_retries = 10,495,377`**, `tx_underrun = 0`, `q1_stopped_cnt = 0`.
2. **`dmesg` Proof of `521.13s` (`8m 41s`) `DFS 5355 MHz` Beacon-Miss Outage on `.61`**:
   - Kernel log on `.61` records:
     - `[333360.337000] wmi_unified_roam_event_handler: Regular sta bmiss:4`
     - `[333361.999000] br0: port 2(ath0.100) entering disabled state`
     - `[333881.469000] PEER ADD PUBLIC_DEVICE_0078 ... [333883.621000] br0: port 2(ath0.100) entering forwarding state`
   - Because `.60 <-> .61` runs on `DFS 5355 MHz`, a single `Regular sta bmiss` event caused a **`521.13-second` (`8m 41s`) total Guarida tower blackhole** (`FMX-DISC-24`), reinforcing the Stage 180A/211A recommendation to pair Stage 0 `IRQ 33` neutralization (`Mode B`: `irq33` + `ptp_xmit=1` + `daprot=2`) with a coordinated non-DFS channel plan.
