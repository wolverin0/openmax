<!-- doc-head: STAGE418A_PANEL3_LOCAL_ENQUED_MCS2_STORM_RE.md preserved document content -->
<!-- /doc-head -->



# Stage 418A — Binary Dissection of `Panel3 (.83)` `674,501,176` `local_enqued` (`ast_tx_mgmt` `78.44%` at `MCS 2`) Storm in `umac.ko` & `ubnt_poll_host.ko`

## 1. Executive Summary (`CONFIRMED`)
- **Claim**: `CONFIRMED` (`QCA firmware` + `proprietary airMAX/LTU module`, `0` writes performed).
- **Binary Artifacts**:
  - `artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko` (`ol_get_radio_stats` at `.text + 0x000bcd40`)
  - `artifacts/firmware_re_xc_ltu/wa_8725_rootfs/bin/athbox` (`-ol` handler at `0x00401930`)
  - `artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko`
- **Root Cause**:
  1. In `umac.ko:ol_get_radio_stats` (`.text + 0x000bcd40`, `280` B) and `bin/athbox` (`0x00401930`), the counter printed as `tx management frames` (`ast_tx_mgmt`) is **copied 1:1 from `wal_dbg_stats.tx.local_enqued`** (`674,501,176` on `Panel3 .83`).
  2. Inside the `QCA9882` offload target firmware (`athwlan.bin`), `wal_dbg_stats.tx.local_enqued` counts every MSDU generated locally inside the target WAL (target-generated airMAX TDMA poll/sync frames, beacons, ProbeResp frames, and local control/BAR bursts), whereas `host_IS_enqued` (`185,361,171` on `.83`) counts host-originated data frames arriving over `HTT`.
  3. On `Panel3 (.83)`, even though `system.cfg` specifies `radio.1.polling=disabled`, `/proc/sys/dev/uph_wifi0/enable` is still `1` with `flags = 14864` (`0x3a10`) and `down_dur = 30,000 us / up_dur = 30,000 us / cbp_dur = 900 us`.
  4. The `QCA9882` target transmits these locally enqueued poll/beacon/ProbeResp frames at fixed base rate **`MCS 2`**: on `Panel3 (.83)`, `Tx MCS 2 = 669,086,302` frames, matching `local_enqued = 674,501,176` to **`99.20%`**, while `Rx MCS 1 = 293,763,641` matches `rx.loc_msdus = 295,340,061` (`99.47%`) from co-located `Panel2 (.82)` (`30 MHz` / `50 MHz` guard) and scanning STAs.

---

## 2. Guarida 4-Radio `local_enqued` vs `Tx MCS 2` & `rx.loc_msdus` Comparison

| Radio | Role & `uph_wifi0` State | `msdus_enqued` | `host_IS_enqued` | `local_enqued` (`ast_tx_mgmt`) | `local_enqued` Share | `Tx MCS 2` Frames | `rx.loc_msdus` |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `Almafuerte (.60)` | PtP AP (`ff=0`, `30/30 ms`) | `635,235,403` | `629,528,144` | `5,707,259` | **`0.90%`** | `300,163` | `1,579,410` |
| `Guarida-BH (.61)` | PtP STA (`ff=0`, `30/30 ms`) | `530,633,229` | `520,110,877` | `10,522,352` | **`1.98%`** | `313,257` | `9,687,312` |
| `Panel2 (.82)` | PtMP AP (`ff=10 ms`, `4.88/4.37 ms`) | `538,642,074` | `258,984,745` | `279,657,329` | **`51.92%`** | `310,265,864` | `236,835,699` |
| **`Panel3 (.83)`** | **PtMP AP (`polling=disabled`, `uph=1`)** | **`859,862,347`** | **`185,361,171`** | **`674,501,176`** | **`78.44%`** | **`669,086,302`** | **`295,340,061`** |

---

## 3. Binary & Telemetry Proof Points
1. **`ast_tx_mgmt == wal_dbg_stats.tx.local_enqued`**:
   - Verified across all 4 live radios:
     - `.60`: `5,707,259 == 5,707,259`
     - `.61`: `10,522,352 == 10,522,352`
     - `.82`: `279,657,329 == 279,657,329`
     - `.83`: `674,501,176 == 674,501,176`
2. **Why `Panel3 (.83)` Has `2.41x` More `local_enqued` Than `Panel2 (.82)`**:
   - Because `Panel3 (.83)` runs in hybrid `polling=disabled` + `uph_wifi0/enable=1` (`flags=0x3a10`) mode with only `3` online CPEs (`3` offline) and `30 MHz` edge-to-edge proximity to `Panel2 (.82)`, the target WAL continuously emits unacknowledged local poll/sync and ProbeResp frames at **`MCS 2`** (`669.09M` frames = `77.8%` of all transmitted frames on `.83`), consuming airtime even when payload demand (`185.36M` `host_IS_enqued`) is low.

---

## 4. Verification & Reproducibility
- **Script**: [`dissect_stage418a_panel3_local_enqued_mcs2_storm_re.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/re/dissect_stage418a_panel3_local_enqued_mcs2_storm_re.py)
- **Artifact**: [`stage418a_panel3_local_enqued_mcs2_storm_re.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage418a_panel3_local_enqued_mcs2_storm_re.json)
- **Test Suite**: [`test_stage418a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage418a.py)
