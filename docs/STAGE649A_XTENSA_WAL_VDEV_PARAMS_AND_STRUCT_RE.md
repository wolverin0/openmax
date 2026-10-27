<!-- doc-head: STAGE649A_XTENSA_WAL_VDEV_PARAMS_AND_STRUCT_RE.md preserved document content -->
<!-- /doc-head -->



# Stage 649A — `QCA988x` Xtensa `wal_vdev` (`WMI_VDEV_SET_PARAM_CMDID`) Jump-Table & Struct Dissection

- **Claim Status**: `CONFIRMED` (`100%` static binary instruction disassembly across `OpenWrt 10.1.467-ct` `IE 3`, `WA.v8.7.25`, and `XC.v8.7.25`; `live_devices_touched = False`).
- **Subsystem Attribution**: `QCA firmware` (`QCA988x` Xtensa `WMI` VDEV dispatcher & `WAL` `wal_vdev` struct).
- **Generator & Receipt**:
  - [`dissect_stage649a_xtensa_wal_vdev_params_and_struct_re.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/re/dissect_stage649a_xtensa_wal_vdev_params_and_struct_re.py)
  - [`stage649a_xtensa_wal_vdev_params_and_struct_re.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage649a_xtensa_wal_vdev_params_and_struct_re.json)
  - [`test_stage649a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage649a.py)

---

## 1. Executive Summary & Architectural Comparison

In `QCA988x` Xtensa firmware, `WMI_VDEV_SET_PARAM_CMDID` (`0x900a`, `min_len = 8` bytes at `0x0040cf50` in `WA`/`XC` and `0x0040bf30` in `OpenWrt 10.1.467-ct`) translates host WMI VDEV parameters into internal `wal_vdev_set_param` IDs:

| Firmware | `wmi_vdev_set_param` VA | WMI Dispatch Mechanism | `wal_vdev_set_param` VA | `wal_vdev` Jump Table | Substruct Addend (`a10`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`WA.v8.7.25` (`10.2.4`)** | `0x0098916c` | `54`-slot Jump Table `@ 0x0098918c` (`29` active) | `0x0098e218` | `23`-slot JT `@ 0x0098e239` (`23` active) | `+128` (`0x80`) |
| **`XC.v8.7.25` (`10.2.4`)** | `0x0098916c` | `54`-slot Jump Table `@ 0x0098918c` (`29` active, 100% byte-identical to `WA`) | `0x0098e218` | `23`-slot JT `@ 0x0098e239` (`23` active) | `+128` (`0x80`) |
| **`OpenWrt 10.1.467-ct`** | `0x009890a4` | Binary search tree $\rightarrow$ `call8 0x0098ec38` | `0x0098ec38` | `33`-slot JT `@ 0x0098ec53` (`27` active) | `+156` (`0x9c`) |

---

## 2. Complete 23-Slot `wal_vdev_set_param` Table (`WA.v8.7.25` / `XC.v8.7.25` vs `OpenWrt 10.1.467-ct`)

| Slot | Parameter Name | `WA` Handler | `WA` `wal_vdev` Offset | `OpenWrt` Offset | Hardware / WHAL Target & Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | `WAL_VDEV_PARAM_NON_AGG_SW_RETRY_TH` | `0x0098e288` | `0x122` (`290`, `u8`) | `0x102` (`258`) | Clamped `<= 31` (`minu a8, a4, a12`); non-agg MPDU SW retry limit |
| `1` | `WAL_VDEV_PARAM_AGG_SW_RETRY_TH` | `0x0098e27e` | `0x121` (`289`, `u8`) | `0x101` (`257`) | Clamped `<= 31` (`minu a14, a4, a12`); A-MPDU SW retry limit |
| `2` | `WAL_VDEV_PARAM_FRAG_THRESHOLD` | `0x0098e40d` | `0x124` (`292`, `u16`) | `0x11c` (`284`) | Clamped `<= 0xfff7`; fragmentation threshold (`s16i`) |
| `3` | `WAL_VDEV_PARAM_AMPDU_SUBFRAMES_PER_AC` | `0x0098e3fe` | `0x126 + ac` (`u8`) | `0x103 + ac` | Stores `val >> 8` at `vdev + 0x126 + (val & 0xff)` |
| `4` | `WAL_VDEV_PARAM_AMPDU_DEFAULT_SUBFRAMES` | `0x0098e3f7` | `0x12a` (`298`, `u8`) | `0x10b` (`267`) | Default per-VDEV A-MPDU subframe ceiling |
| `5` | `WAL_VDEV_PARAM_TX_ENCAP_TYPE` | `0x0098e3ed` | `WHAL+0x278` | `WHAL+0x278` | Calls `*(0x004062dc + 0x278)` (Raw / Native Wi-Fi / Ethernet) |
| `6` | `WAL_VDEV_PARAM_RX_DECAP_OR_AP_INACTIVITY` | `0x0098e3e6` | `0x15f` (`351`, `u8`) | `0x110` (`272`) | Stores RX decap / AP sleeping-STA timeout |
| `7` | `WAL_VDEV_PARAM_RTS_THRESHOLD` | `0x0098e3d6` | `0x160` (`352`, `u32`) | Slot `9` (`0x0098eda3`) | Calls `*(0x004062dc + 0x200)` (`whalSetRtsThreshold`, `agg=1`) |
| `8` | `WAL_VDEV_PARAM_NON_AGG_RTS_THRESHOLD` | `0x0098e3c6` | `0x164` (`356`, `u32`) | Slot `10` (`0x0098ed96`) | Calls `*(0x004062dc + 0x200)` (`whalSetRtsThreshold`, `agg=0`) |
| `9` | `WAL_VDEV_PARAM_SLOT_TIME` | `0x0098e3bf` | `pdev+0x160` | Slot `11` (`0x0098ed8f`) | Calls `0x00984fb4` $\rightarrow$ `MAC_D_GBL_IFS_SLOT` (`9 us` / `20 us`) |
| `10` | `WAL_VDEV_PARAM_PREAMBLE` | `0x0098e3b2` | `WHAL+0x00` | Slot `12` (`0x0098ed81`) | Calls `**(0x004062dc)` $\rightarrow$ `MAC_PCU` barker preamble |
| `11..14` | `WAL_VDEV_PARAM_SGI / LDPC / STBC` | `0x0098e38c..a7` | `0x009bab5c..74` | Slots `13..16` | Calls rate-control SGI/LDPC/TX-STBC/RX-STBC helpers |
| `15` | `WAL_VDEV_PARAM_CABQ_MAXDUR` | `0x0098e387` | `0x9c` (`156`, `u32`) | `0xac` (`172`, Slot 17) | CABQ multicast max burst duration (init `26 ms` `@ 0x00983cc0`) |
| `16` | `WAL_VDEV_PARAM_MFPTEST_OR_PROT_MODE` | `0x0098e37d` | `0x174` (`372`, `u32`) | `0x164` (`356`, Slot 18) | Boolean `(val != 0)` protection flag |
| `17` | `WAL_VDEV_PARAM_BURST_ENABLE` | `0x0098e371` | `*(0x00410930)` | `*(0x0040db04)` (Slot 19) | Global TXOP frame burst flag (`*(0x00410930) = (val != 0)`) |
| `18` | `WAL_VDEV_PARAM_FIXED_OR_MCAST_RATE` | `0x0098e355` | `0x130` (`304`, `u16`) | `0x122` (`290`, Slot 20) | Multicast/fixed rate code (`s16i`) |
| `19` | `WAL_VDEV_PARAM_TX_POWER` | `0x0098e337` | `0x132` (`306`, `u8`) | `0x10c` (`268`, Slot 21) | Stores TX power (0.5 dBm steps) & calls `0x00983d3c` |
| `20` | `WAL_VDEV_PARAM_WMM_TXOP_AND_CW_TABLE` | `0x0098e2b0` | `0x1cc..0x204` | — | Copies 14 `u32` WMM/TXOP params & calls `0x0098ada8` |
| `21..22` | `WAL_VDEV_PARAM_DTIM / BEACON_INT` | `0x0098e292..a1` | `0x00988008..14` | — | Updates DTIM / beacon interval & notifies beacon gen |
| `26..32` | `CT_CUSTOM_VDEV_EXTENSIONS` (`OpenWrt` only) | — | — | `0x188, 0x28c, 0x290, 0x294` | Candela Technologies rate/TXOP (`0x009b2490`) & MTU `>1584` (`0x294`) |
