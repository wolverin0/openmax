<!-- doc-head: STAGE455A_UBNT_POLL_UL_SLOT_STARVATION_AND_REQUEUE_RE.md preserved document content -->
<!-- /doc-head -->



# Stage 455A — Binary Dissection of `ubnt_poll` UL Slot Starvation, `BAR`/`BlockAck` Requeue, `139,751,148` `mpdus_requed` (`20.31%` on `.82`), & `9,522,084` `excess_retries` (`24.84%` on `.83`)

## 1. Executive Summary (`CONFIRMED`)
- **Claim**: `CONFIRMED` (`proprietary airMAX/LTU module` + `QCA firmware`, `0` writes performed).
- **Core Dichotomy Between `Panel2 (.82)` and `Panel3 (.83)`**:
  1. **`Panel2 (.82)` — Fixed-Frame TDMA Slot-Expiry Requeue (`139,751,148` `mpdus_requed` = `20.31%`, `excess_retries` = `23`)**:
     - With `ff_frame_dur=10,000 us`, `down_dur=4,880 us`, `up_dur=4,370 us`, `cbp_dur=180 us`, and `cms_bias=0` (where `_retr_supression_levels` at `.rodata + 0x0ea4` sets `dl_per_thresh_nr=100%` and `ul_per_thresh_nr=100%`), the `QCA9882` target polling hooks (`tx_bd_ExchangeHandler` at `0x0099b8d4` and `rx_poll_ExchangeHandler` at `0x0099bd4c` in `athwlan_AR9888v2_ptmp_ap_bin`, `32/32` hooks at `seg[2] .data + 0x29a8`) preempt in-flight A-MPDU subframes whenever a station's TDMA burst slot expires or its `BlockAck` (`SQST/SQEN/RXBITMAP` tracked by `ubnt_poll_host_log_noack_info` at `0x00a7fc`) has holes.
     - Instead of discarding the MPDU, the target WAL returns unacknowledged MPDUs to the software TID queue (`wal_dbg_stats.tx.mpdus_requed = 139,751,148`), preserving delivery (`excess_retries = 23`, `0.000005%` drop rate) at the cost of `20.31%` software requeue overhead and `p99` queue latency.
  2. **`Panel3 (.83)` — Unaligned CSMA/TDMA `swr_limit` Exhaustion (`9,522,084` `excess_retries` = `24.84%` of `hw_queued`)**:
     - Because `Panel3 (.83)` has `radio.1.polling=disabled` in `system.cfg` while `uph_wifi0/enable=1` (`down_dur=30,000 us / up_dur=30,000 us`), transmissions are not bounded by `4.88 ms` TDMA slot preemption; instead, data frames collide repeatedly with co-located `Panel2 (.82)` (`30 MHz` guard) until exhausting `swr_limit` (`ubnt_poll_host_set_swr_limit` at `0x00b404`), incrementing `wal_dbg_stats.tx.excess_retries` to **`9,522,084` (`24.84%` of all `38,337,164` `hw_queued` frames)**!

---

## 2. Dissected Binary Offsets (`ubnt_poll_host.ko`, `umac.ko`, & `athwlan_AR9888v2_ptmp_ap_bin`)

| Binary / Module | Symbol / Table | Offset / VA | Role in Requeue vs Excess-Retry Path |
| :--- | :--- | :--- | :--- |
| `umac.ko` | `ol_get_wal_dbg_stats` | `.text + 0x0b5dbc` (`28` B) | Copies `0xcc` (`204`) B of `wal_dbg_stats` from `scn + 0x1e0a4` into `user_buf + 0x0140..0x020b` (`mpdus_requed` at `0x13bc($sp)`, `excess_retries` at `0x13c0($sp)`). |
| `athwlan_AR9888v2_ptmp_ap_bin` | `tx_bd_ExchangeHandler` / `rx_poll_ExchangeHandler` | `0x0099b8d4` / `0x0099bd4c` | Preempts unacknowledged A-MPDU subframes at TDMA slot boundary and returns them to the software TID queue (`mpdus_requed++`). |
| `ubnt_poll_host.ko` | `ubnt_poll_host_log_noack_info` | `.text + 0x00a7fc` (`852` B) | Formats per-TID `SQST/SQEN/SBIT/SEQR/REGA/REGB/REGC` and 256-bit `RXBITMAP/TXBITMAP` sliding window state. |
| `ubnt_poll_host.ko` | `ubnt_poll_host_set_swr_limit` | `.text + 0x00b404` (`104` B) | Configures target software retry limit (`swr_limit`) before a frame is aborted into `excess_retries`. |
| `ubnt_poll_host.ko` | `_retr_supression_levels` | `.rodata + 0x0ea4` (`70` B) | `10 x 7` `uint8` retry-suppression table indexed by `cms_bias` (`0..9`); at `cms_bias=0`, `dl/ul_per_thresh_nr = 100%` (disabled). |

---

## 3. Live `Panel2 (.82)` vs `Panel3 (.83)` Requeue & Retry Matrix

| Metric (`athstats -ol` / `wal_dbg_stats`) | `Panel2 (.82)` (`Fixed-Frame 10 ms`) | `Panel3 (.83)` (`Unaligned 30/30 ms`) | Architectural Interpretation |
| :--- | ---: | ---: | :--- |
| `comp_queued` | `688,050,121` | `63,008,944` | Total MSDUs/MPDUs queued to target WAL. |
| `hw_queued` | `494,692,787` | `38,337,164` | Total hardware TXOP bursts queued to MAC PCU. |
| **`mpdus_requed` (`tx_retries`)** | **`139,751,148` (`20.31%`)** | `11,524,148` (`18.29%`) | TDMA slot-expiry preemption + deferred-STA WAL requeue on `.82`. |
| **`excess_retries` (`ast_tx_xretries`)** | **`23` (`0.000005%`)** | **`9,522,084` (`24.84%`)** | **`414,003x` more terminal retry drops on unaligned `.83` than TDMA-scheduled `.82`!** |

---

## 4. Verification & Reproducibility
- **Script**: [`dissect_stage455a_ubnt_poll_UL_slot_starvation_and_requeue_re.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/re/dissect_stage455a_ubnt_poll_UL_slot_starvation_and_requeue_re.py)
- **Artifact**: [`stage455a_ubnt_poll_UL_slot_starvation_and_requeue_re.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage455a_ubnt_poll_UL_slot_starvation_and_requeue_re.json)
- **Test Suite**: [`test_stage455a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage455a.py)
