<!-- doc-head: STAGE681A_UBNT_POLL_DL_SCHEDULER_AND_AGGR_BUDGET_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 681A — `ubnt_poll_host.ko` Downlink Scheduler (`0x00b400..0x00c800`) & Per-Node Aggregation Budget (`aggr_limit` / `quantum`) Dissection

## 1. Classification & Attribution
- **Claim Classification**: `CONFIRMED`
- **Layer Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` `v8.7.11` + `QCA988x` `ptmp_ap_bin` target TDMA scheduler)
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.
- **Receipt**: [`stage681a_ubnt_poll_dl_scheduler_and_aggr_budget_re.json`](../artifacts/autoresearch/stage681a_ubnt_poll_dl_scheduler_and_aggr_budget_re.json)
- **Dissector Script**: [`dissect_stage681a_ubnt_poll_dl_scheduler_and_aggr_budget_re.py`](../tools/re/dissect_stage681a_ubnt_poll_dl_scheduler_and_aggr_budget_re.py)

## 2. Disassembly of `0x00b400..0x00c800` & `0x00dc38..0x00e658` in `ubnt_poll_host.ko`
Static MIPS32 MSB disassembly of `ubnt_poll_host.ko` across `.text + 0x00b400..0x00c800` and `ubnt_poll_host_send_ptmp_netconf` (`0x00dc38..0x00e658`) maps the exact host-to-target control path governing Downlink TDMA scheduling, retry caps, EVM measurement packets, and the `104`-byte (`0x68`) `struct uph_ptmp_netconf` template in `.rodata + 0x09f0..0x0e67`:

| Symbol | VA Range | `HT_COMM` / Table | Core Downlink & Per-Node Scheduler Mechanism |
| :--- | :---: | :---: | :--- |
| **`ubnt_poll_host_set_swr_limit`** | `0x00b404..0x00b46b` | `0x001f` (`31`) | Sets `ff_dl_swr_count` (`0x1c($sp)`) and `ff_ul_swr_count` (`0x1d($sp)`), defaulting to `10` software retries on Fixed Frame `.82`. |
| **`ubnt_poll_host_set_evm_meas_config`** | `0x00b46c..0x00b4fb` | `0x0028` (`40`) | Configures target EVM reporting (`0x1c..0x1f($sp)`) and zeroes `sta + 0xa4` (`sb $zero, 0xa4($v0)`) across `sta_list` (`0x10ec($s0)`) and `sta_hash_table` (`0x10f0($s0)`). |
| **`ubnt_poll_host_debug_tid`** | `0x00b4fc..0x00b5db` | `0x0029` (`41`) | Per-STA TID pause/resume (`0x1c..0x23($sp)`) inside the target TDMA DL/UL queues. |
| **`ubnt_poll_host_debug_block_sta`** | `0x00b5dc..0x00b7db` | `HT_COMM` block | Suspends or unblocks a station in the target TDMA loop while checking `opmode` (`0x118($a0)`). |
| **`ubnt_poll_host_proto_insert_ie`** | `0x00b950..0x00c437` | `00:27:22` IE | AES-128 + HMAC-SHA1 encryption/parsing of Ubiquiti Vendor IE carrying `sta_priority` (`0..2`) and TDMA capabilities. |
| **`ubnt_poll_host_setup_packet`** | `0x00c438..0x00c8e7` | `.rodata + 0x0650` | Jump table for packet types `5..10`; type `6` (`0x00c4f8..0x00c5b8`) packs `4 × 64B` (`0x40` at `+0x03/+0x43/+0x83/+0xc3`, stride `0x103 = 259B`) per-chain RX/TX EVM arrays. |
| **`ubnt_poll_host_send_ptmp_netconf`** | `0x00dc38..0x00e657` | `.rodata + 0x09f0` | Builds the `104B` (`0x68`) `ptmp_netconf` payload: `down_dur` (`0x26($sp)`), `up_dur` (`0x28($sp)`), `cbp_dur` (`0x2a($sp)`), `high_contention_min_down_dur` (`0x54($sp)=5000 us`), `ff_unit_shift=4` (`16 us` unit). |

## 3. `104`-Byte (`0x68`) `struct uph_ptmp_netconf` Layout (`.rodata + 0x09f0..0x0e67`)
- **`0x00` (`flags`)**: `137` (`0x89`) on `.82` (`Fixed 10ms 50/50`); `14,864` (`0x3a10`) on `.83` (`Flexible`).
- **`0x04..0x10` (Window Durations)**: `down_dur_min = 900 us` (`2,200 us = 0x898` in `40 MHz` Fixed at `0x00e268`), `cfp_dur_min = 180 us` (`.82`) / `10,000 us` (`.83`), `cbp_dur_slot = 60 us` (`.82`) / `300 us` (`.83`), `down_dur = 4,880 us` (`.82` `50/50`) $\rightarrow$ **`6,580 us` (`67/33`)**, `up_dur = 4,370 us` $\rightarrow$ **`2,670 us` (`67/33`)**, `cbp_dur = 180 us`.
- **`0x1c..0x37` (Aging & Reporting Timers)**: `activity_aging = 3,000,000 us` (`3.0 s`), `activity_aging_da = 10,000,000 us` (`10.0 s`), `eval_report_interval = 5,000,000 us` (`5.0 s`), `usage_report_interval = 1,000,000 us` (`1.0 s`).
- **`0x58..0x65` (Fixed-Frame & Quantum Scalars)**: `ff_frame_dur = 10,000 us`, `ff_dl_alloc = 50%` (`67%` target), `ff_dl_swr_count = 10`, `ff_ul_max_polled_stas = 5` (`4` at `67/33`), `ff_unit_shift = 4` (`1 << 4 = 16 us` quantum granularity), `ff_mcast_airtime_limit = 10%` (`5%` in Champion `v22`).

## 4. Per-Node DL Aggregation Budget (`aggr_limit_bytes`) & EVM/SISO Penalty
For a `600 us` per-station DL TXOP quantum (`556 us` net payload after `44 us` PLCP + SIFS + BlockAck overhead):

| Station Profile | Effective PHY Rate | Spatial Streams | Net Byte Budget (`aggr_limit_bytes`) | Max `1500B` A-MPDU Subframes | DL Airtime Cost (`us / Mbit`) | Penalty vs Healthy `MCS15` |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Healthy `2x2 MIMO MCS15` (`20 MHz`)** | `144.4 Mbps` | `2x2` | **`10,035 B`** | `6` subframes | **`7.47 us/Mbit`** | `1.00x` (baseline) |
| **`Rocio Belen DURAN` (`.82`, `11.61 dB` EVM Gap)** | `86.7 Mbps` | `2x2` (degraded) | **`6,025 B`** | `4` subframes | **`12.44 us/Mbit`** | **`-40.0%` byte quota / `1.67x` airtime** |
| **`SOSA_Joaquin` (`.83`, `16.26 dB` TX EVM Gap)** | `78.0 Mbps` | `2x2` (degraded) | **`5,421 B`** | `3` subframes | **`13.83 us/Mbit`** | **`-46.0%` byte quota / `1.85x` airtime** |
| **`RODRIGUEZ_Marina` (`.82`, `tx_nss=1` SISO)** | `39.0 Mbps` | `1x1 SISO` | **`2,710 B`** | `1` subframe | **`27.66 us/Mbit`** | **`-73.0%` byte quota / `3.70x` airtime** |
