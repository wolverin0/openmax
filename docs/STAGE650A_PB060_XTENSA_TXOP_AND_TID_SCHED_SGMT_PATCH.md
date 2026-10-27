<!-- doc-head: STAGE650A_PB060_XTENSA_TXOP_AND_TID_SCHED_SGMT_PATCH.md preserved document content -->
<!-- /doc-head -->



# Stage 650A — `PB060-TXOP-CABQ-SCHED` Surgical `SGMT` Binary Patcher (`QCA988x` Xtensa)

- **Claim Status**: `CONFIRMED` (`7` `SGMT` firmware binaries patched and verified offline; `live_devices_touched = False`).
- **Subsystem Attribution**: `QCA firmware` (`QCA988x` Xtensa `wal_vdev_attach`, `wal_vdev_set_param`, and `ubnt_poll` `g_dbg_max_sw_retry`).
- **Generator, Binaries & Receipt**:
  - [`build_stage650a_pb060_xtensa_txop_and_tid_sched_sgmt_patch.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/firmware/build_stage650a_pb060_xtensa_txop_and_tid_sched_sgmt_patch.py)
  - [`stage650a_pb060_xtensa_txop_and_tid_sched_sgmt_patch.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage650a_pb060_xtensa_txop_and_tid_sched_sgmt_patch.json)
  - [`test_stage650a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage650a.py)

---

## 1. Mechanism & Surgical Patch Specification (`PB060-TXOP-CABQ-SCHED`)

Building on Stage 649A's dissection of `wal_vdev_attach` and `wal_vdev_set_param`, `PB060-TXOP-CABQ-SCHED` eliminates Head-of-Line (HoL) software-retry stalls (`31` / `41` software retries per MPDU causing `> 45 ms` `p99` latency spikes under interference) while raising the default A-MPDU subframe ceiling from `26` to `32` subframes:

| Patch Site | Segment | Target Virtual Address | Original Bytes / Instruction | Patched Bytes / Instruction | Effect |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`wal_vdev_attach` (`OpenWrt 10.1.467-ct`)** | `seg[3]` (`.text`) | `0x00983d5b` | `5caa 0c03 3cfb` (`movi.n a10,26; movi.n a3,0; movi.n a11,31`) | `2c0a 0c03 0cab` (`movi.n a10,32; movi.n a3,0; movi.n a11,10`) | Default A-MPDU subframes `26 -> 32`; per-AC SW retries `31 -> 10` |
| **`wal_vdev_attach` (`WA`/`XC` `v8.7.25` all)** | `seg[3]` (`.text`) | `0x00983c94` | `5caa 3cfb` (`movi.n a10,26; movi.n a11,31`) | `2c0a 0cab` (`movi.n a10,32; movi.n a11,10`) | Default A-MPDU subframes `26 -> 32`; per-AC SW retries `31 -> 10` |
| **`wal_vdev_set_param` (`OpenWrt` / `WA` / `XC`)** | `seg[3]` (`.text`) | `0x0098ec41` / `0x0098e227` / `0x0098e323` | `1cfc` (`movi.n a12, 31`) | `0ccc` (`movi.n a12, 12`) | Clamps runtime `WMI_VDEV_SET_PARAM` `AGG/NON_AGG_SW_RETRY_TH <= 12` |
| **`g_dbg_max_sw_retry` (`WA` / `XC` `v8.7.25`)** | `seg[2]` (`.data`) | `0x0040d364` / `0x0040d828` / `0x0040d8d8` (`+0x20` XC) | `29000000` (`uint32_t 41`) | `0c000000` (`uint32_t 12`) | Bounds `ubnt_poll` target-side software retry ceiling `41 -> 12` |

---

## 2. Verified `SGMT` Output Images & `PB-040 + PB-050 + PB-060` Composability

All 7 patched `SGMT` binaries in `artifacts/autoresearch/xtensa_ram_patch_poc/stage650a_pb060/` preserve exact segment sizes, entry point `0x00983c00`, `0` signature bytes, and 100% disjoint virtual address ranges when combined with `PB-040` (`0x009b7584`) and `PB-050` (`0x0040c24c`/`0x0040d4e0`, `0x0098a3eb`/`0x0098a028`, `0x0040da78`).
