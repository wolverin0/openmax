<!-- doc-head: STAGE359A_GUARIDA_OL_ATH_STATS_AND_UPH_STAINFO.md preserved document content -->
<!-- /doc-head -->


# Stage 359A — Complete `athstats -ol` (`struct ol_ath_stats` `0x0310` B) & `wal_dbg_stats` / `ubnt_poll` Per-Peer Read-Only Radiography Across `.60`, `.61`, `.82`, `.83`

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` `0x018750`) + `ath10k` / `QCA firmware` (`wal_dbg_stats`)
- **Safety Boundary**: `0` writes performed (`SG-01..05` compliant)
- **Script**: [`tools/re/audit_stage359a_guarida_ol_ath_stats_and_uph_stainfo.py`](../tools/re/audit_stage359a_guarida_ol_ath_stats_and_uph_stainfo.py)
- **Receipt**: [`artifacts/autoresearch/stage359a_guarida_ol_ath_stats_and_uph_stainfo.json`](../artifacts/autoresearch/stage359a_guarida_ol_ath_stats_and_uph_stainfo.json)

---

## 1. `struct ol_ath_stats` (`0x0310` = `784` B) & `ubnt_poll` Per-Peer Export Architecture (`CONFIRMED`)

1. **`athstats -ol` (`0x00401930` in `bin/athbox` $\rightarrow$ `umac.ko:ol_ath_ioctl` `0x000bcc40`)**:
   - Populates `784` bytes (`0x0310`) across 3 contiguous kernel substructures:
     - `ol_txrx_stats` (`312` B at `user_buf + 0x0008..0x013f` via `ol_txrx_stats_publish` `0x000d31b8`): host `tx.sent`, `tx.dropped`, `multiqueue_sent[0..4]`, `multiqueue_compl[0..4]`, and `multiqueue_stopped_cnt[0..4]`.
     - `wal_dbg_stats` (`208` B at `user_buf + 0x0140..0x020f` via `ol_get_wal_dbg_stats` `0x000bcd30`): `QCA9882` target WAL `HWQ[0..9]`, `comp_queued`, `comp_delivered`, `msdu_enqued`, `mcast_dropped`, `local_enqued`, `hw_queued`, `underrun`, `tx_abort`, `mpdus_requed`, `excess_retries`, `sched_self_trig`, `phy_errs`, and `mpdu_errs`.
     - `ol_ath_radio_stats` (`256` B at `user_buf + 0x0210..0x030f` via `ol_get_radio_stats` `0x000bcd40`): `ast_be_nobuf`, `ast_tx_buf_count`, `ast_rxorn`, `ast_txurn`, `ast_txto`, per-chain RSSI, and `Rx/Tx MCS STATS` (`MCS 0..9`).
2. **`ubnt_poll_host.ko` Procfs vs `/dev/ubnt_poll_host` `ku_comm` Per-Peer Export**:
   - `/proc/1/net/uph_wifi0/` exposes `info` (`ubnt_poll_log_buffer_read_ex` `0x005c58`) and `noack_info`.
   - Per-peer `sta_info` (`actual_priority`, `desired_priority`, `cb_capacity`, `dl_capacity`, `ul_capacity`, `rx/tx usage`, `rx/tx cinr`, and 64-sample `rx/tx evm` vectors) is exported via `/dev/ubnt_poll_host` ioctl handlers `ubnt_poll_ku_comm_get_stalist` (`0x0185b8`) and `ubnt_poll_ku_comm_get_stainfo` (`0x018750`), read in userland by `wstalist`.

---

## 2. Complete 4-Radio `athstats -ol` & `uph_wifi0` Matrix (`.60`, `.61`, `.82`, `.83`) (`CONFIRMED`)

| Counter / Metric (`athstats -ol` & `uph_wifi0`) | `.60` (`Ap.Guarida` AP) | `.61` (`St.Guarida` STA) | `.82` (`Panel2` AP) | `.83` (`Panel3` AP) |
| :--- | :---: | :---: | :---: | :---: |
| `comp_queued` / `comp_delivered` | `532,983,085` | `499,572,567` | `688,050,121` | `185,361,171` |
| `msdu_enqued` | `538,690,342` | `510,094,897` | `964,912,338` | `859,862,347` |
| **`mcast_dropped`** (`wal_dbg_tx`) | `0` | `0` | **`2,795,044`** | `0` |
| **`local_enqued`** (`ast_tx_mgmt`) | `5,707,259` | `10,522,352` | `279,657,329` | **`674,501,176` (`78.4%`!)** |
| **`mpdus_requed`** (`tx_retries`) | `31,055,822` | `18,966,607` | **`139,746,042`** | `4,901,895` |
| **`excess_retries`** (`ast_tx_xretries`) | `4,195,957` | `10,515,619` | `23` | **`9,518,931`** |
| `underrun` (`ast_txurn`) / `tx_abort` | `457` / `10` | `1,062` / `42` | `0` / `2` | `0` / `0` |
| `ast_txto` (`pdev_tx_timeout`) | `0` | **`20`** | `0` | `0` |
| **`ast_rxorn`** (RX FIFO overrun) | `67,212,506` | **`230,744,054`** | `92,974,076` | `26,279,330` |
| `phy_errs` / `phy_errs_dropped` | `0` / `19,259` | `0` / `1,986` | **`2,261,415` / `3,624,684`** | `2` / `39,994` |
| **`mpdu_errs`** (RX FCS/CRC errors) | `3,360,576` | **`47,070,035`** | **`16,309,936`** | `5,496,587` |
| `multiqueue Q1` (`sent` / `compl` / `stops`) | `525.81M` / `525.81M` / `24` | `491.64M` / `491.64M` / `0` | `672.40M` / `672.40M` / **`2,214`** | `181.11M` / `181.11M` / **`1,896`** |
| `ast_be_nobuf` / `ast_tx_buf_count` | `0` / `1,290` | `0` / `1,424` | `0` / `1,332` | `0` / `1,424` |
| `ast_rx_rssi_chain0 / chain1` (dB SNR) | `35` / `35` (`0 dB` $\Delta$) | `34` / `36` (`2 dB` $\Delta$) | `31` / `30` (`1 dB` $\Delta$) | **`37` / `31` (`6 dB` $\Delta$)** |
| `uph_wifi0/info` `TXPER / RXPER` (‰) | `150` / `165` | `165` / `154` | `183` / `168` | `119` / `119` |

---

## 3. New Diagnostic Insights from Full `athstats -ol` Dissection (`CONFIRMED`)

1. **`230,744,054` `ast_rxorn` (RX Overruns) & `20` `ast_txto` on `Guarida (.61)`**:
   - Because `.61` suffers `46.1%` CPU `sirq` under the `IRQ 33` (`ath-spectral-filter`) storm plus `1,435M` packets forwarded to `.201`, the `QCA9882` RX ring experienced **`230.74 Million` `ast_rxorn` overruns**, `47.07 Million` `mpdu_errs`, `1,062` `tx_underrun`, and `20` `ast_txto` TX watchdog timeouts.
2. **`2,795,044` `mcast_dropped` & `139,746,042` `mpdus_requed` on `Panel2 (.82)`**:
   - With `ff_mcast_airtime_limit = 10%` and `22` CPEs, `QCA9882` dropped `2.80 Million` multicast MSDUs in the WAL while requeuing `139.75 Million` unicast MPDUs (`tx_retries = 139,746,042`) due to TDMA deferred-list churn.
3. **`674,501,176` `local_enqued` (`78.4%` of all TX) on `Panel3 (.83)`**:
   - On `.83` (`polling=disabled`), `674.50 Million` management/control frames (`MCS 2` count = `669,086,302`) were locally enqueued by the target firmware alongside `9,518,931` `excess_retries`.
