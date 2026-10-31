<!-- doc-head: STAGE283A_PANEL2_PANEL3_UBNT_POLL_PROC_AND_ETH_AUDIT.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 283A — Read-Only Audit of `Panel2 (.82)` & `Panel3 (.83)` `/proc/1/net/uph_wifi0/*`, TDMA Internals & Ethernet Statistics

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`) + `QCA firmware` (`wal_dbg_stats`) + `Linux` (`eth0`/`ath0`)
- **Safety Boundary**: `0` writes performed (`SG-01..05` compliant)
- **Receipt**: [`artifacts/autoresearch/stage283a_panel2_panel3_ubnt_poll_proc_and_eth_audit.json`](../artifacts/autoresearch/stage283a_panel2_panel3_ubnt_poll_proc_and_eth_audit.json)

---

## 1. `/proc/1/net/uph_wifi0/info` & `set_remote_host_diag` Comparison (`.82` vs `.83`)

| Parameter / Counter | `198.18.0.5` (`Panel2-Guarida`, `22` CPEs) | `198.18.0.6` (`Panel3-Guarida`, `6` CPEs) | Architectural Explanation |
| :--- | :---: | :---: | :--- |
| `Channel / Mode` | `5765 MHz [HT20]` (`polling=enabled`) | `5730 MHz [HT40-]` (`polling=disabled`) | `.82` uses `ubnt_poll` TDMA; `.83` uses legacy CSMA/CA |
| `DISTANCE` (`uph_wifi0/info`) | `1,500 m` | `6,150 m` | `.83` ack timeout stretched to `6.15 km` |
| `set_remote_host_diag` `flags` | `137` (`0x89`: TDMA active + FF) | `14864` (`0x3a10`: CSMA compat mode) | Contrasts active TDMA scheduler vs CSMA fallback |
| `down_dur / up_dur / cbp_dur` ($\mu	ext{s}$) | `4880` / `4370` / `180` | `30000` / `30000` / `900` | `.82` runs `10 ms` FF frame (`ff_frame_dur=10000`, `50%` DL) |
| `ff_mcast_airtime_limit` | `10%` | `10%` | Stock `10%` mcast airtime cap (Stage 73A champion = `5%`) |
| `eth0` `rx_packets / tx_packets` (to `.201`) | `684,445,454` / `209,982,451` | `185,219,902` / `59,268,307` | Clean switch links on `.201` (`rx_crc_errors = 0`) |
| `eth0` `rx_errors / tx_dropped` | `1` / `1` | `1` / `1` | **Zero physical Ethernet degradation on `.201`** |
| `ath0` `tx_dropped` | `467` | `115` | Minimal netdev drops compared to `qdisc mq` drops |

---

## 2. Mechanistic Contrast in True `QCA9882` `wal_dbg_stats` (`athstats -ol`) (`CONFIRMED`)

Comparing `athstats -ol` between `Panel2 (.82)` (`polling=enabled`) and `Panel3 (.83)` (`polling=disabled`) reveals how `ubnt_poll_host.ko` interacts with the `QCA9882` firmware WAL:

| True `wal_dbg_stats` Metric (`athstats -ol`) | `Panel2-Guarida (.82)` (`polling=enabled`, `21/22` CPEs) | `Panel3-Guarida (.83)` (`polling=disabled`, `5/6` CPEs) | Root Cause Attribution |
| :--- | :---: | :---: | :--- |
| `mpdus_queued` | `686,772,512` | `62,912,432` | `10.9x` higher MPDU volume on `Panel2` (`22` CPEs) |
| **`mpdus_requed`** | **`139,634,216` (`20.33%` of queued!)** | `4,896,555` (`7.78%` of queued) | On `.82`, `ubnt_poll_host.ko` defers weak CPEs and requeues `20.33%` of all MPDUs in the WAL |
| **`excess_retries`** | `23` (`0.000003%`) | **`9,506,061` (`15.11%` of queued!)** | On `.83` (`polling=disabled`), CSMA/CA hidden-node collisions (`150 deg` arc) exhaust hardware retry limits `9.51M` times |
| `tx_underrun` | `0` | **`2,124`** | DMA/WAL underruns under `33%` `sirq` + `2,285/s` `IRQ 33` storm |
| `q1_stopped_cnt` (`BE` stops) | **`2,214`** | **`1,894`** | Host TX ring backpressure events |

---

## 3. `Panel2 (.82)` `ubnt_poll_host: STA added to deferred list` Churn (`CONFIRMED`)

`dmesg` on `Panel2 (.82)` shows continuous TDMA scheduler deferral churn:
- `ubnt_poll_host: STA PUBLIC_DEVICE_0031 added to deferred list` (`LEDESMA_Maria`, `-75 dBm`, `TXPER = 195‰` / `19.5%`)
- `ubnt_poll_host: STA PUBLIC_DEVICE_0034 added to deferred list` (`SANCHEZ_Stella`, `-70 dBm`, `TXPER = 250‰` / `25.0%`)
- `ubnt_poll_host: STA PUBLIC_DEVICE_0029 added to deferred list` (`BENITEZ_Fabiola`, `-71 dBm`, `TXPER = 200‰` / `20.0%`)
- `ubnt_poll_host: STA PUBLIC_DEVICE_0028 added to deferred list` (`OCAMPO_Marcela`, `-69 dBm`, `TXPER = 200‰` / `20.0%`)

When `ubnt_poll_host.ko` moves these 4 weak/high-PER CPEs to the TDMA deferred list while `IRQ 33` (`1,150/s`) consumes `26.8%` `sirq` CPU, `139.63M` MPDUs are requeued inside `QCA9882` (`20.33%`) and `189,296` packets drop at the Linux `qdisc mq` layer.
