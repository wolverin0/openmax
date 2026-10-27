<!-- doc-head: STAGE417A_UBNT_POLL_CBP_DUR_AND_PROBEREQ_HASH_RE.md preserved document content -->
<!-- /doc-head -->



# Stage 417A — Binary Dissection of `ubnt_poll_host.ko` `cbp_dur` (`180 us` vs `900 us`), `AssocReq` Vendor IE `00:27:22` Hash Population, & `20,000 ms` Deferred Timeout

## 1. Executive Summary (`CONFIRMED`)
- **Claim**: `CONFIRMED` (`proprietary airMAX/LTU module` + `QCA firmware`, `0` writes performed).
- **Binary Artifact**: `artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko` (`WA.v8.7.25`, MIPS32 MSB).
- **Core Mechanism**:
  1. `ubnt_poll_host_on_probe_req_rx` (`.text + 0x00910c`, `1,160` B) checks and parses the Ubiquiti OUI `00:27:22` Vendor IE (`ubnt_poll_host_proto_check_ie` at `0x009188`, `ubnt_poll_host_proto_parse_ie` at `0x009260`), **but never inserts the station into `host_data->sta_hash_table` (`0x10f0($s1)`)**.
  2. Only `ubnt_poll_host_on_assoc_req_rx` (`.text + 0x009594`, `2,340` B), when invoked at `stage == 1` (`0x0095c0`) with a valid `00:27:22` Vendor IE (`0x00967c -> 0x009760`), allocates the `sta` entry (`ubnt_poll_host_create_sta` at `0x009b94`) and populates `host_data->sta_hash_table` via `ubnt_poll_host_sta_add(0x10f0($s1), 0x10ec($s1), sta)` at `0x009c8c`.
  3. On `Panel2 (.82)` (`ff_frame_dur = 10,000 us`), the Contention-Based Period `cbp_dur` (`host_data + 0x0208`) is compressed to **`180 us`** (`1.80%` of the frame), compared to **`900 us`** (`5.0x` wider contiguous contention slot) on `Panel3 (.83)` (`down_dur = 30,000 us`, `up_dur = 30,000 us`).
  4. When high-PER CPEs on `Panel2 (.82)` (`-69` to `-75 dBm`) suffer contention collisions inside the narrow `180 us` `cbp_dur` or miss the `stage == 1` `00:27:22` Vendor IE insertion in `0x009594`, `ubnt_poll_host_on_sta_connect` (`0x008134`) fails `ubnt_poll_host_sta_hash_find(0x10f0($s0))` (`0x0081b4`), checks `host_data->flags & 0x2000` (`0x0082b4`, where live `flags = 14864 = 0x3a10`), and locks the CPE into `host_data->deferred_list` (`0x10fc($s0)`) for `host_data->defer_timeout_ms = 20,000 ms` (`0x0220($s0)`, default `0x4e20` at `0x006388`).

---

## 2. Dissected Function Table (`ubnt_poll_host.ko`)

| Symbol | `.text` Offset | Size (B) | Exact Assembly Call / Offset & Role |
| :--- | :--- | ---: | :--- |
| `ubnt_poll_host_on_probe_req_rx` | `0x00910c` | `1,160` | Calls `ubnt_poll_host_proto_check_ie` (`0x009188`) and `ubnt_poll_host_proto_parse_ie` (`0x009260`), but **does not** call `ubnt_poll_host_sta_add`. |
| `ubnt_poll_host_on_assoc_req_rx` | `0x009594` | `2,340` | At `stage == 1` (`0x0095c0`), validates `00:27:22` IE (`0x00967c`, `0x009760`), calls `ubnt_poll_host_create_sta` (`0x009b94`), and calls `ubnt_poll_host_sta_add(0x10f0($s1), 0x10ec($s1), sta)` at `0x009c8c`. |
| `ubnt_poll_host_proto_check_ie` | `0x00bd9c` | `72` | Verifies Vendor IE length (`>= 10` B) and Ubiquiti OUI header before parsing. |
| `ubnt_poll_host_proto_parse_ie` | `0x00bde4` | `216` | Extracts airMAX protocol version, capability flags, and station subtype from the `00:27:22` Vendor IE. |
| `ubnt_poll_host_sta_add` | `0x00ce9c` | `92` | Inserts `sta` into `host_data->sta_hash_table` (`0x10f0`) and `host_data->sta_list` (`0x10ec`). |
| `ubnt_poll_host_init_ptmp_netconf` | `0x00d244` | `832` | Loads default PtMP netconf timing from `.rodata + 0x0190..0x01ac` and dispatches via `ubnt_poll_ht_comm_send` (`0x00d55c -> 0x0144bc`). |
| `ubnt_poll_ht_comm_parse` | `0x014894` | `2,672` | Populates `down_dur` (`0x0200($s0)` at `0x014fb4`), `up_dur` (`0x0204($s0)` at `0x014fc0`), `cbp_dur` (`0x0208($s0)` at `0x014fcc`), and `defer_timeout_ms` (`0x0220($s0)` = `byte[0x01ed($s1)] * 1000` at `0x015014..0x015024`). |
| `ubnt_poll_host_set_remote_host_diag` | `0x007df0` | `60` | Validates `reg_id < 32` (`0x007e08: sltiu $v0, $a2, 32`) and sends `HT_COMM` msg `7` (`0x007e14`) via `ubnt_poll_ht_comm_send` (`0x007e1c`). |

---

## 3. Live `Panel2 (.82)` vs `Panel3 (.83)` `cbp_dur` & `flags` Comparison

| Parameter (`host_data` Offset) | `Panel2 (.82)` (Fixed-Frame `10 ms`) | `Panel3 (.83)` (Flexible `30/30 ms`) | Physical / Scheduler Consequence |
| :--- | ---: | ---: | :--- |
| `ff_frame_dur` | `10,000 us` | `0` (Flexible) | Fixed `10 ms` frame forces hard CBP truncation on `.82`. |
| `down_dur` (`0x0200($s0)`) | `4,880 us` | `30,000 us` | Downlink burst window per frame. |
| `up_dur` (`0x0204($s0)`) | `4,370 us` | `30,000 us` | Uplink polled window per frame. |
| **`cbp_dur` (`0x0208($s0)`)** | **`180 us`** | **`900 us`** | **`5.0x` narrower contention slot on `.82` (`180 us` vs `900 us`)**. |
| `flags` (`0x001c($s0)`) | `14864` (`0x3a10`) | `14864` (`0x3a10`) | Bit `0x2000` (`allow_80211` / deferred gate) is `1` on both APs. |
| `defer_timeout_ms` (`0x0220($s0)`) | `20,000 ms` (`0x4e20`) | `20,000 ms` (`0x4e20`) | `.82` suffers continuous `20 s` deferred-STA lockouts; `.83` has `0`. |

---

## 4. Verification & Reproducibility
- **Script**: [`dissect_stage417a_ubnt_poll_cbp_dur_and_probereq_hash_re.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/re/dissect_stage417a_ubnt_poll_cbp_dur_and_probereq_hash_re.py)
- **Artifact**: [`stage417a_ubnt_poll_cbp_dur_and_probereq_hash_re.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage417a_ubnt_poll_cbp_dur_and_probereq_hash_re.json)
- **Test Suite**: [`test_stage417a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage417a.py)
