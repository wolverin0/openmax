<!-- doc-head: STAGE360A_UBNT_POLL_DEFERRED_STA_STATE_MACHINE.md preserved document content -->
<!-- /doc-head -->


# Stage 360A — Binary Dissection of `ubnt_poll_host.ko` Deferred-STA State Machine (`STA <MAC> added to deferred list` & `mpdus_requed` Storm on `Panel2 .82`)

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`) + `QCA firmware` (`wal_dbg_stats`)
- **Safety Boundary**: `0` writes performed (`SG-01..05` compliant)
- **Script**: [`tools/re/dissect_stage360a_ubnt_poll_deferred_sta_state_machine.py`](../tools/re/dissect_stage360a_ubnt_poll_deferred_sta_state_machine.py)
- **Receipt**: [`artifacts/autoresearch/stage360a_ubnt_poll_deferred_sta_state_machine.json`](../artifacts/autoresearch/stage360a_ubnt_poll_deferred_sta_state_machine.json)

---

## 1. Exact MIPS32 Disassembly of the `deferred_list` State Machine in `ubnt_poll_host.ko` (`CONFIRMED`)

In `WA.v8.7.25` `ubnt_poll_host.ko`, the strings:
- `$LC11` (`.rodata.str1.4 + 0x14e4`): `"<7>ubnt_poll_host: STA %02X:%02X:%02X:%02X:%02X:%02X added to deferred list\n"`
- `$LC12` (`.rodata.str1.4 + 0x1534`): `"<7>ubnt_poll_host: STA %02X:%02X:%02X:%02X:%02X:%02X not added to deferred list\n"`

are referenced exclusively inside **`ubnt_poll_host_on_sta_connect` (`.text + 0x008134`, size `1,316` B)**:

1. **Entry & `sta_hash_table` Lookup (`0x008134..0x0081cc`)**:
   - Checks `host_data->op_mode == 1` (`lw $v1, 0x0118($s0)` at `0x008170`, AP mode).
   - Calls `ubnt_poll_host_sta_hash_find(host_data->sta_hash_table [0x10f0($s0)], mac)` (`0x0081b4`).
   - `sta_hash_table` (`host_data + 0x10f0`) is populated when `ubnt_poll_host_on_probe_req_rx` (`0x00910c`) or `ubnt_poll_host_on_beacon_rx` (`0x008afc`) parses the Ubiquiti `00:27:22` airMAX Vendor IE.
   - If the associating STA is **not present in `sta_hash_table`** (`0x0081cc: beql $v0, $zero, 0x00826c`, e.g., when its ProbeReq was missed inside the narrow `180` $\mu\text{s}$ `cbp_dur` contention window or after a poll-timeout kick), execution branches to `0x00826c`.
2. **Deferral Gate & `ubnt_poll_host_create_sta_def` (`0x0082b4..0x00837c`)**:
   - Checks `host_data->flags & 0x2000` (`0x0082b4: lw $v0, 0x001c($s0); andi $v0, $v0, 0x2000`).
   - Removes any stale node for `mac` from `host_data->deferred_list` (`$s0 + 0x10fc`) via `ubnt_poll_host_sta_list_remove($s0, $s0 + 0x10fc, mac)` (`0x0082dc`).
   - Calls **`ubnt_poll_host_create_sta_def($s0, mac)` (`0x0082f8 -> 0x00cc7c`)**, which allocates a **`24`-byte (`0x18`) `struct ubnt_poll_sta_def`** from `host_data->sta_def_pool` (`0x1198($a0)`):
     - `+0x00`: `uint32_t flags` (`0x40` = `STA_DEF_ACTIVE`, `| 0x80` if `$a2 != 0` at `0x008318`)
     - `+0x04`: `uint32_t timestamp_jiffies` (`sw $v1, 0x0004($v0)` at `0x008310`)
     - `+0x08`: `uint8_t mac[6]` (`0x00ccb0..0x00ccd0`)
     - `+0x10`: `struct ubnt_poll_sta_def *next`
   - Appends the node to `host_data->deferred_list` (`$s0 + 0x10fc`) via `ubnt_poll_host_sta_list_add_tail` (`0x008330 -> 0x00cd1c`), logs `$LC11` (`"added to deferred list"`, `0x008364..0x008374`), and **returns `1` (`0x00837c: addiu $s1, $zero, 1`)** to intercept/hold association completion!
3. **Deferred Timer Drain (`0x0062fc..0x0064e0`)**:
   - The periodic OS timer callback at `.text + 0x0062fc` inspects `host_data->deferred_list` (`lw $s1, 0x10fc($a0)` at `0x006338`), computes elapsed ms `(jiffies - sta_def->timestamp_jiffies) * 1000 / HZ` (`0x00635c..0x006390`), and waits until `elapsed_ms >= host_data->defer_timeout_ms` (`0x0220($s0)`, default **`20,000 ms` = `0x4e20`** at `0x006388`) before popping the node (`0x0063a8`), calling `ubnt_poll_host_indicate_assoc` (`0x006420`, if `sta_hash_find` now succeeds) and freeing the node via `ubnt_poll_host_destroy_sta_def` (`0x006484 -> 0x00ccf8`).

---

## 2. How `deferred_list` Churn Causes `139,746,042` `mpdus_requed` (`20.31%`) on `Panel2 (.82)` (`CONFIRMED`)

| `Panel2 (.82)` TDMA Knob / Counter | Live Value | Interaction with `deferred_list` (`0x10fc`) & `QCA9882` WAL |
| :--- | :---: | :--- |
| `ff_frame_dur` | `10,000` $\mu\text{s}$ (`10 ms`) | Fixed-Frame superframe duration |
| `down_dur` / `up_dur` | `4,880` $\mu\text{s}$ / `4,370` $\mu\text{s}$ | Active DL/UL TDMA data windows |
| **`cbp_dur`** (Contention-Based Period) | **`180` $\mu\text{s}$ (`1.8%` of frame)** | Only `180` $\mu\text{s}$ per `10 ms` frame for unpolled ProbeReq/Auth/Assoc & wakeups across `22` CPEs |
| `sta_priority` | `1 2 0` | Weak CPEs default to priority `2` (or `0` lowest), receiving last poll slots |
| `defer_timeout_ms` (`0x006388`) | `20,000 ms` (`20 s`) | Holds deferred STA in `host_data->deferred_list` (`0x10fc`) for up to `20 s` |
| **`mpdus_requed` / `comp_queued`** | **`139,746,042` / `688,050,121` (`20.31%`)** | While the 4 weak CPEs (`-69` to `-75 dBm`, `19.5%–25.0%` PER) stall or cycle through `deferred_list`, `QCA9882` WAL requeues their buffered DL MPDUs on every missed TDMA poll burst |
