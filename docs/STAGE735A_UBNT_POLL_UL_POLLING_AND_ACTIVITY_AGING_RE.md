<!-- doc-head: STAGE735A_UBNT_POLL_UL_POLLING_AND_ACTIVITY_AGING_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 735A — `ubnt_poll_host.ko` Uplink Polling Scheduler (`0x00e67c` & `0x014894`) & Inactive-STA Airtime Tax Dissection

## 1. Classification & Attribution
- **Claim Classification**: `CONFIRMED`
- **Layer Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` `v8.7.11` + `QCA988x` `ptmp_ap_bin` UL polling ring)
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.
- **Receipt**: [`stage735a_ubnt_poll_ul_polling_and_activity_aging_re.json`](../artifacts/autoresearch/stage735a_ubnt_poll_ul_polling_and_activity_aging_re.json)
- **Dissector Script**: [`dissect_stage735a_ubnt_poll_ul_polling_and_activity_aging_re.py`](../tools/re/dissect_stage735a_ubnt_poll_ul_polling_and_activity_aging_re.py)

## 2. Disassembly of `ubnt_poll_host_ht_comm_rx` (`0x00e67c`) & `ubnt_poll_ht_comm_parse` (`0x014894`)
Static MIPS32 MSB disassembly of `ubnt_poll_host.ko` proves how the AP host and `QCA988x` target coordinate station activity aging and UL polling rings:

1. **`ubnt_poll_host_ht_comm_rx` (`0x00e67c..0x00f69f`, `4,124` bytes)**:
   - Dispatches `40` target-to-host message types (`msg_id 3..42` via jump table at `.rodata + 0x0690`, `0x00e6c4: sltiu $v1, $v0, 0x28`).
   - At `0x00e7e4..0x00e8a8`, inspects channel bandwidth `0x26c($sp)` (`0x14 = 20 MHz`, `0x28 = 40 MHz`, `0x50 = 80 MHz`) and binds the per-bandwidth MCS rate/airtime lookup tables (`.rodata + 0x02c0 / 0x02d8` for `20 MHz`, `max_mcs_idx = 10`; `.rodata + 0x02e4 / 0x02fc / 0x02f0` for `40 MHz`, `max_mcs_idx = 12`).
2. **`ubnt_poll_ht_comm_parse` (`0x014894..0x015e4f`, `5,564` bytes)**:
   - Dispatches `46` message parsers via `.rodata + 0x5fec` (`0x0148f0: sltiu $v1, $v0, 0x2e`).
   - At `0x0149b0..0x014a00`, unpacks the 3-tier station activity timers from the `104`-byte `ptmp_netconf` payload into the runtime scheduler state (`$s0`):
     - **`0x1c($s0)` (`activity_aging` = `3,000,000 us` = `3.0 s`)**: Duration a station stays in the high-priority `ACTv` polling ring after transmitting/receiving `>= downlink_active_thresh` (`100`).
     - **`0x20($s0)` (`activity_aging_da` = `10,000,000 us` = `10.0 s`)**: Warm direct-access / CBP contention window (`3.0 s .. 10.0 s` after last burst).
     - **`0x24($s0)` (`activity_aging_hb` = `1,000,000 us` = `1.0 s`)**: Deep-idle heartbeat poll interval (`1` poll per `1.0 s`, paired with `sounding_interval = 1,000,000 us`).

## 3. Live `Panel2-Guarida (.82)` Activity Snapshot & Empty-Poll Airtime Tax
Live `/proc/net/uph_wifi0/stats` on `.82` (`|STAs=0007|ACTv=0001|TXUSE=00793|RXUSE=00012|TLUSE=00805|`) reveals that while Downlink is `79.3%` busy (`TXUSE=793‰`), Uplink is only `1.2%` busy (`RXUSE=12‰`) with `ACTv = 1` truly active station. However, whenever short web/DNS/ACK bursts wake multiple CPEs, `activity_aging = 3,000,000 us` (`3.0 s`) keeps each awakened station in the `ACTv` ring for `300` consecutive `10 ms` frames (`~186 us` wasted per empty poll: `36 us` poll at `ff_ul_ctrl_rate=12` + `150 us` `slot_guard_us`):

| UL Polling & Aging Profile | `ff_dl_alloc` | `up_dur` (`us`) | Max Polled STAs (`0xfe`) | `activity_aging` (`us`) | Mean False-Active STAs / Frame | Empty-Poll Waste / Frame (`us`) | Share of `up_dur` Wasted (`%`) | Net Active UL Payload (`us`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Current_82_10ms_50_50_Aging_3000ms`** | `50%` | `4,370` | `5` | `3,000,000` (`3.0s`) | `3.2` | `595.2 us` | `13.62%` | `3,024.8 us` |
| **`Candidate_10ms_67_33_Aging_3000ms`** | `67%` | `2,670` | `4` | `3,000,000` (`3.0s`) | `2.4` | `446.4 us` | `16.72%` | `1,623.6 us` |
| **`Champion_10ms_67_33_Aging_1500ms`** | **`67%`** | **`2,670`** | **`4`** | **`1,500,000` (`1.5s`)** | **`1.1`** | **`204.6 us`** | **`7.66%`** | **`1,865.4 us` (`+14.89%`)** |
