<!-- doc-head: UBIQUITI_AIRMAX_AC_UPH_BUG_DISCLOSURE_REPORT.md preserved document content -->
<!-- /doc-head -->



# Coordinated Technical Bug Disclosure: Ubiquiti `airMAX AC` (`ubnt_poll_host.ko` & `/bin/ubntbox` `v8.7.25`)

- **Report ID**: `FMX-DISC-S73B-AIRMAX-AC-UPH-20261026` (`T-S73B-UPH-BUG01-TO-08-DISCLOSURE-AND-BINARY-PATCH-SYNTHESIS`)
- **Affected Firmware / Modules**: `airOS 8` `WA.v8.5.12..v8.7.25` (`AR9342`) & `XC.v8.7.4-cs..v8.7.25` (`QCA9558`) — `ubnt_poll_host.ko` (`189,880` B; `WA` SHA256 `bfc3f499...`, `XC` SHA256 `d327c4c8...`) & `/bin/ubntbox` (`ubntconf` radio plugin)
- **Verification Status**: **`CONFIRMED`** (`100%` Offline Binary Dissection + Surgical ELF32 Patch Verification via [`tools/re/patch_stage73b_uph_bugs_and_atomic_helper.py`](../tools/re/patch_stage73b_uph_bugs_and_atomic_helper.py))

---

## 1. Bilingual Executive Summary (English & Español)

- **English Summary**: Static ELF32 MIPS32 big-endian reverse engineering of `ubnt_poll_host.ko` (`WA.v8.7.25` and `XC.v8.7.25`) and `/bin/ubntbox` identified seven actionable software defects and suboptimal defaults (`UPH-BUG-02` through `UPH-BUG-08`) in the host-side airMAX AC TDMA control plane. These include an unbounded `sscanf("%s")` 32-byte kernel stack buffer overflow in `/proc/sys/dev/uph/addradio` (`UPH-BUG-02`), a register-clobber bug (`slti $v1, $v1, 0x19`) in the `fixed_frame` `ff_dl_alloc` quantizer that forces inputs `< 25%` up to `50%` (`UPH-BUG-03`), shared `ctl_table.data` aliasing across all 21 integer sysctls (`UPH-BUG-04`), an inverted `min_power`/`max_power` parameter order in `atpc` (`UPH-BUG-05`), an unnecessary `radio->uph_dev != NULL` runtime lockout on `noack_mode`/`daprot`/`enable` (`UPH-BUG-06`), and disabled default collision/VoIP biases (`cms_bias=0`, `voip_bias=0`) with `10%` multicast airtime cap (`UPH-BUG-07..08`). Exact MIPS32 offsets, binary patches (`0` relocation overlaps), and C fixes are provided below.
- **Resumen Ejecutivo (Español)**: La disección binaria ELF32 MIPS32 BE de `ubnt_poll_host.ko` (`WA.v8.7.25` y `XC.v8.7.25`) y `/bin/ubntbox` reveló siete defectos de software y constantes subóptimas (`UPH-BUG-02` a `UPH-BUG-08`) en el plano de control TDMA de `airMAX AC`. Se documentan: un desbordamiento de pila de 32 bytes vía `sscanf("%s")` en `/proc/sys/dev/uph/addradio` (`UPH-BUG-02`), corrupción del registro `$v1` (`slti $v1, $v1, 0x19`) en el cuantizador `ff_dl_alloc` de `fixed_frame` que salta de `< 25%` a `50%` (`UPH-BUG-03`), aliasing del vector compartido `.bss+0x09a8` entre 21 sysctls enteros y lectura nula en `ro` (`UPH-BUG-04`), inversión entre `min_power` y `max_power` en `atpc` (`UPH-BUG-05`), bloqueo en caliente de `noack_mode`/`daprot`/`enable` cuando `radio->uph_dev != NULL` (`UPH-BUG-06`), y valores por defecto `cms_bias=0`/`voip_bias=0` en `.rodata` junto con `ff_mcast_airtime_limit=10%` (`UPH-BUG-07..08`), incluyendo parches binarios verificados y correcciones en C.

---

## 2. Summary Matrix of `UPH-BUG-02..08` (`CONFIRMED`)

| Bug ID | Severity | Subsystem | ELF Section & Offset | Summary of Defect & Operational Impact (`CONFIRMED`) |
| :--- | :--- | :--- | :--- | :--- |
| **`UPH-BUG-02`** | **HIGH** | `ubnt_poll_host.ko` | `.text+0x01c78..0x01cf0` & `0x052ec..0x05300` | Unbounded `sscanf(buf, "%s %d %d %d %d", sp+0x20, ...)` from 100B `.bss+0x0118` into a 32B stack buffer (`sp+0x20..0x3f`) overflows `$s0`, `$s1`, `$ra` if token 1 > 31 bytes. |
| **`UPH-BUG-03`** | **MEDIUM** | `ubnt_poll_host.ko` | `.text+0x02fc4..0x02ffc` | `slti $v1, $v1, 0x19` at `0x02fcc` overwrites `$v1`, and `0x02fe0..0x02fe4` (`bnez $v1, 0x2ff8; addiu $v1, $zero, 0x32`) forces `ff_dl_alloc < 25` to **`50%` (`0x32`)** instead of `25%` (`0x19`). |
| **`UPH-BUG-04`** | **MEDIUM** | `ubnt_poll_host.ko` | `.bss+0x09a8..0x09e7` & `.text+0x02258` / `0x0276c` | All 21 per-radio integer sysctls alias `.bss+0x09a8` (`int sysctl_vec[16]`); writing `ro` (`0x0276c`) sends WMI `0x901f` `msg_type=0x1e` without updating `uph_dev+0x15e..0x166` (readback always `0`). |
| **`UPH-BUG-05`** | **MEDIUM** | `ubnt_poll_host.ko` + `/bin/ubntbox` | `.text+0x02320`, `0x02990`, `0x0dac8` & `ubntbox` `0x004217ac` | `atpc` sysctl stores `vec[2]` -> `radio+0xd1` -> `netconf+100` (`atpc_max_power`) and `vec[3]` -> `radio+0xd0` -> `netconf+101` (`atpc_min_power`), while `atpc` readback (`0x02320`) prints `radio+0xd1` as `min` and `radio+0xd0` as `max`. |
| **`UPH-BUG-06`** | **LOW/MED** | `ubnt_poll_host.ko` | `.text+0x024e8`, `0x0288c`, `0x02d20` | `enable`, `noack_mode`, and `daprot` reject writes whenever `radio->uph_dev != NULL` (`lw $v0, 0xe4($radio); bnez $v0, reject`), preventing live updates while `ath0` is up. |
| **`UPH-BUG-07`** | **MEDIUM** | `ubnt_poll_host.ko` | `.rodata+0x0b28..0x0e67` (`+75`, `+84`) | All 8 `.rodata` `ptmp_netconf` profiles initialize `cms_bias=0` (`+75`) and `voip_bias=0` (`+84`), leaving hidden-node retry suppression and VoIP dynamic slot duration disabled by default. |
| **`UPH-BUG-08`** | **MEDIUM** | `/bin/ubntbox` + `ubnt_poll_host.ko` | `ubntbox` `0x0041ef2c` & `.text+0x02c8c` | `ubntbox` defaults `polling_ff_mcast_airtime` to `10%` (`addiu $a1, $zero, 0x0a`) with `tx_queue_len=50`, causing multicast airtime bloat or burst tail-drop under TDMA aggregation. |

---

## 3. Detailed Technical Analysis, MIPS32 Disassembly & Suggested C Fixes

### 3.1 `UPH-BUG-02` — 32-Byte Kernel Stack Buffer Overflow in `/proc/sys/dev/uph/addradio` (`.text+0x01c78..0x01cf0`)
- **Disassembly (`ubnt_poll_host.ko` `.text+0x01c98..0x01cf0` & `0x052ec..0x05300`, `CONFIRMED`)**:
  - `.data+0x00d0` configures `/proc/sys/dev/uph/addradio` with `data = .bss+0x0118` and `maxlen = 100` (`0x64`).
  - `ubnt_poll_host_sysctl_addradio` allocates a 72-byte stack frame (`addiu $sp, $sp, -0x48`), saves `$s0`, `$s1`, `$ra` at `sp+0x40..0x48`, and calls `sscanf(.bss+0x0118, "%s %d %d %d %d", sp+0x20, &ptp, &compat, &flex, &ax)` (`0x01ce8`). A first token `>= 32` bytes overflows `sp+0x20..0x3f` directly into `$s0`, `$s1`, and `$ra`. In addition, `ubnt_poll_host_radio_add` (`0x052ec..0x05300`) copies `phy_name` into `radio_entry+0x00` (`char name[32]`) with an unbounded byte loop.
- **Suggested C Fix for Ubiquiti Engineering**:
```c
char dev_name[32];
if (sscanf(uph_addradio_buf, "%31s %d %d %d %d", dev_name, &ptp, &compat, &flex_new, &ax_compat) < 1)
    return -EINVAL;
strlcpy(radio->name, dev_name, sizeof(radio->name));
```

### 3.2 `UPH-BUG-03` — `fixed_frame` `ff_dl_alloc` Register Clobber Jumping `< 25%` to `50%` (`.text+0x02fc4..0x02ffc`)
- **Disassembly (`ubnt_poll_host.ko` `.text+0x02fbc..0x02ffc`, `CONFIRMED`)**:
```mips
0x02fbc: 5080000e  beql   $a0, $zero, 0x2ff8   ; if (ff_dl_alloc >= 50) { $v1 = 50; goto store; }
0x02fc0: 24030032  addiu  $v1, $zero, 0x32     ; (likely delay slot: only executes when $a0 == 0)
0x02fc4: 28640021  slti   $a0, $v1, 0x21       ; $a0 = ($v1 < 33)
0x02fc8: 14800005  bnez   $a0, 0x2fe0          ; if ($v1 < 33) goto 0x2fe0
0x02fcc: 28630019  slti   $v1, $v1, 0x19       ; BUG: overwrites $v1 with boolean ($v1 < 25)!
0x02fd0: 24030021  addiu  $v1, $zero, 0x21     ; 33 <= input < 50 -> $v1 = 33
...
0x02fe0: 14600005  bnez   $v1, 0x2ff8          ; BUG: when input < 25 ($v1 == 1), jumps to 0x2ff8...
0x02fe4: 24030032  addiu  $v1, $zero, 0x32     ; ...executing delay slot $v1 = 50 (0x32) instead of 25 (0x19)!
0x02fe8: 24030019  addiu  $v1, $zero, 0x19     ; 25 <= input < 33 -> $v1 = 25 (0x19)
```
- **Binary Patch (`0` `.rel.text` overlaps) & Suggested C Fix**:
  - Patching `.text+0x02fe4` from `24 03 00 32` (`addiu $v1, $zero, 0x32`) to `24 03 00 19` (`addiu $v1, $zero, 0x19`) ensures all `ff_dl_alloc < 33` inputs clamp monotonically to `25%` (`0x19`).
```c
static u8 quantize_ff_dl_alloc(int dl_pct) {
    if (dl_pct >= 75) return 75;
    if (dl_pct >= 67) return 67;
    if (dl_pct >= 50) return 50;
    if (dl_pct >= 33) return 33;
    return 25; /* Fixed: previously returned 50 whenever dl_pct < 25 */
}
```

### 3.3 `UPH-BUG-04` — Shared `.bss+0x09a8` `sysctl_vec[16]` Aliasing & Unsaved `ro` Readback (`.text+0x02258` / `0x0276c`)
- **Root Cause (`CONFIRMED`)**:
  1. All 21 integer `ctl_table` entries in `.rodata+0x00b0..0x0527` share `data = .bss+0x09a8` (`int sysctl_vec[16]`). Because read handlers and multi-int parsers share this global scratch array without per-knob storage, writing multi-int sysctls overwrites `sysctl_vec[0..9]`.
  2. Writing `/proc/sys/dev/uph_wifi0/ro` (`0x0276c..0x027f4`) calls `ubnt_poll_host_set_rate_override` (`0x0b2d4`, WMI `0x901f` `msg_type=0x1e`) using `sysctl_vec[0..8]` but never persists them into `uph_dev+0x15e..0x166`, so reading `/proc/sys/dev/uph_wifi0/ro` (`0x02258..0x022e4`) always prints `0 0 0 0 0 0 0 0 0`.
- **Suggested C Fix**: Store `sysctl_vec[0..8]` into `uph_dev->ro_cfg[0..8]` (`uph_dev+0x15e..0x166`) inside `ubnt_poll_host_set_rate_override()`, and use a stack-local `int local_vec[16]` with a temporary `ctl_table` copy inside `ubnt_poll_host_sysctl_int_handler`.

### 3.4 `UPH-BUG-05` — `atpc` `min_power` / `max_power` Inversion (`0x02320`, `0x02990`, `0x0dac8`)
- **Root Cause (`CONFIRMED`)**:
  - In `ubnt_poll_host_sysctl_int_handler` (`0x02990..0x0299c` & `0x02a44..0x02a58`), `vec[2]` is stored into `radio+0xd1` (`uph_dev+0x106`) and `vec[3]` into `radio+0xd0` (`uph_dev+0x107`).
  - `ubnt_poll_host_init_ptmp_netconf` (`0x0dac8..0x0dae0`) copies `uph_dev+0x106` (`vec[2]`) into `netconf.atpc_max_power` (`+100`) and `uph_dev+0x107` (`vec[3]`) into `netconf.atpc_min_power` (`+101`), matching `/bin/ubntbox` (`0x004217ac`: `<en> <target> <maxpower> <minpower> <defpower>`).
  - However, the `atpc` sysctl readback handler (`0x022e8..0x02378`) loads `radio+0xd1` (`vec[2]`) into `min_power` and `radio+0xd0` (`vec[3]`) into `max_power`, inverting `min` and `max` on readback.
- **Suggested C Fix**: Align `atpc` readback (`0x02320..0x02338`) with `init_ptmp_netconf` so `vec[2]` is consistently `atpc_max_power` and `vec[3]` is `atpc_min_power`.

### 3.5 `UPH-BUG-06` — Runtime Lockout on `enable` (`0x024e8`), `noack_mode` (`0x0288c`), & `daprot` (`0x02d20`)
- **Root Cause & Binary Patch (`CONFIRMED`)**:
  - `enable` (`0x024e8`: `54 40 00 12` `bnel $v0, $zero, 0x2534`), `noack_mode` (`0x0288c`: `14 40 00 0a` `bnez $v0, 0x28b8`), and `daprot` (`0x02d20`: `14 40 00 0c` `bnez $v0, 0x2d54`) reject writes whenever `radio->uph_dev != NULL` (`0xe4($radio)`).
  - Replacing those 3 branch instructions with `00 00 00 00` (`nop`, `0` `.rel.text` overlaps) allows runtime updates without tearing down `ath0`.

### 3.6 `UPH-BUG-07` & `UPH-BUG-08` — Suboptimal `.rodata` `cms_bias=0, voip_bias=0` & `ubntbox` `ff_mcast_airtime_limit=10%`
- **Root Cause & Binary Patch (`CONFIRMED`)**:
  - All 8 `.rodata` `ptmp_netconf` templates (`0x0b28..0x0e67`, stride `104` B) set `cms_bias` (`+75`) = `0` and `voip_bias` (`+84`) = `0`. Patching `+75` and `+84` to `0x06` (`6`, `0` `.rel.rodata` overlaps) activates `_retr_supression_levels[6]` and `_voip_dynamic_duration_levels[6]` by default.
  - On unmodified stock `airOS 8`, apply `cms_bias=6`, `voip_bias=6`, `daprot=2`, and write `ff_mcast_airtime_limit=5` **last** (via `render_uph_atomic_apply_sequence()`).

---

## 4. Stage 75A/78B Addendum — `umac.ko` (`UMAC-BUG-01..05`) & `ath_dev.ko` (`ATHDEV-BUG-01..04`) (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`umac.ko` `2,356,432` B `WA` / `2,358,768` B `XC` & `ath_dev.ko` `287,216` B) — verified via [`dissect_stage75a_umac_and_ath_dev_ko.py`](../tools/re/dissect_stage75a_umac_and_ath_dev_ko.py) & [`patch_stage78b_umac_and_ath_dev_bugs.py`](../tools/re/patch_stage78b_umac_and_ath_dev_bugs.py) (`0` relocation overlaps).

| Bug ID | Module & Offset | Severity | Defect Summary & Verified Stage 78B Binary / Runtime Fix (`CONFIRMED`) |
| :--- | :--- | :--- | :--- |
| **`UMAC-BUG-01`** | `umac.ko` `.text+0x0a2874`, `0x0a2984`, `0x09e9a4`, `0x0d0e08` | **HIGH** | `osif_vap_init` initializes `osifp->osif_is_multiq` (`dev+0x3dc`) to `1` (`0x24020001`, bit 0 only), leaving bit 1 (`0x2`, deep `802.1Q` `0x8100` / `PPPoE` `0x8864` inner-DSCP classifier at `0x09e9a4`) disabled. **Patch**: `0x24020001 -> 0x24020003` (`set_multiq=3`). |
| **`UMAC-BUG-02`** | `umac.ko` `.bss+0x01bca0`, `.text+0x0bc1e8` (`WA`) / `0x0bc1ec` (`XC`) | **HIGH** | `enable_tx_tcp_cksum` defaults to `0`, skipping `dev->features \|= 0x12` (`NETIF_F_IP_CSUM \| NETIF_F_IPV6_CSUM`) while `ol_tx_desc_ll` (`0x0d189c`) still runs descriptor checksum logic. **Patch**: `0x10400004 -> 0x00000000` (`nop`). |
| **`UMAC-BUG-03`** | `umac.ko` `.text+0x0bc1c4` (`WA`) / `0x0bc1c8` (`XC`), `0x0a2960` | **MEDIUM** | `enable_tx_tcp_cksum` is read only once during `ol_ath_linux_attach`; post-boot `sysfs` writes do not update `wifi0->features` or `ath0->features` (`+0x44`). **Runtime Fix**: `ethtool -K ath0 tx on` or Stage 78B binary patch. |
| **`UMAC-BUG-04`** | `umac.ko` `.text+0x0b36fc..0x0b3710` | **MEDIUM** | When `scn->burst_dur` (`-0x1f76($s0)`) is `0`, `ol_ath_set_config_param` sends WMI `0x28` (`0x1fe0 = 8160` us) but delay slot `0x0b3710` (`sh $s1, -0x1f76($s0)`) writes the 1-bit flag `$s1` instead of `0x1fe0`. **Patch**: `0x0b3704 -> 0x144001e5`, `0x0b3708 -> 0x24111fe0`. |
| **`UMAC-BUG-05`** | `umac.ko` `.text+0x0b37f4..0x0b3808`, `0x0914ec` | **MEDIUM** | `AMPDULim` (`0x1007`) and `AMPDUFrames` (`0x1008`) write only host memory (`-0x1d3c($s0)` / `-0x1d40($s0)`) without WMI sync; `__ath_attach` (`0x0914ec`) has a `3x msleep(1000)` loop when `ubnthal_GetSystemId` fails. |
| **`ATHDEV-BUG-01`** | `ath_dev.ko` `.text+0x016728..0x016774`, `0x0199c8` | **HIGH** | `addiu $a1, $v1, -1; sltiu $a1, $a1, 0x1c0` underflows when `Minfree=0` (`0xFFFFFFFF >= 448`) and forces `48/32/16` fallbacks; `ath_txq_set_minfree` (`0x0199c8`) ignores `CABQ` (`2`). **Patch**: `0x24650000; 0x2ca501c1`. |
| **`ATHDEV-BUG-02`** | `ath_dev.ko` `.text+0x016908..0x016914` | **MEDIUM** | `ath_cabq_update` hard-clamps `CABlevel` (`0x1012`) to `[15%, 96%]` (`0x0f..0x60`). **Patch**: `0x016908 -> 0x2c430002`, `0x016914 -> 0x24020002` (`2%` floor). |
| **`ATHDEV-BUG-03`** | `ath_dev.ko` `.text+0x01b9fc..0x01ba04` | **HIGH** | `ath_tx_start_dma` (`0x01ba00: 2c420030 sltiu $v0, $v0, 0x30`) aborts **all** A-MPDU queues (including `AC_VI` `Minfree=16` and `AC_VO` `Minfree=0`) when `sc_txbuf_free < 48`. **Patch**: `0x2c420030 -> 0x2c420010` (`16`). |
| **`ATHDEV-BUG-04`** | `ath_dev.ko` `.text+0x027c00..0x027c78` | **LOW** | `ath_spectral_filter_init` unconditionally registers GPIO `1` (`WA`) / `21` (`XC`) and threaded IRQ `0x21` (`WA`) / `0x40` (`XC`). |

---

## 5. Stage 84B/88A Addendum — `airOS 6` `XW` (`AR934x` `M5`) `ath_rate_atheros.ko`, `ubnt_ewma_ht.ko`, `ath_dev.ko` & `umac.ko` (`XW-BUG-01..03`) (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`ath_rate_atheros.ko` `152,816` B, `ubnt_ewma_ht.ko` `22,652` B, `ath_dev.ko` `436,552` B, `umac.ko` `915,640` B on `XW.v6.1.4` `Linux 2.6.32.71`) — verified via [`dissect_stage84b_xw_m5_ath_rate_and_ubnt_poll.py`](../tools/re/dissect_stage84b_xw_m5_ath_rate_and_ubnt_poll.py) & [`STAGE84B_XW_M5_ATH_RATE_ATHEROS_AND_UBNT_POLL_FULLREA_DISSECTION.md`](STAGE84B_XW_M5_ATH_RATE_ATHEROS_AND_UBNT_POLL_FULLREA_DISSECTION.md) (`0` relocation overlaps).

| Bug ID | Module & Offset | Severity | Defect Summary & Verified Stage 84B/88A Binary / Runtime Fix (`CONFIRMED`) |
| :--- | :--- | :--- | :--- |
| **`XW-BUG-01`** | `ath_rate_atheros.ko` `.text+0x00e6c..0x00ebc` (`rcRateFind_11n`) vs `.text+0x02970` (`rcRateFind_11nViVo`) | **HIGH** | On `WME_AC_BE`/`AC_BK`, `rcRateFind_11n` computes `delta_ms = now_ms - rc->rssiTime` (`0x5c8($s1)`). When `delta_ms >= 185 ms` (`sltiu $v0, $v1, 0xb9` at `0x00e88`), `0x00e90` (`2404000a`) subtracts **`10 dB`** from ACK RSSI (`$s0 - 10`), and for `25..185 ms` (`0x00ea8: 7c022420`) subtracts `(delta_ms - 25) >> 4` dB, collapsing idle stations to `MCS0 (6.5 Mbps)` (`FMX-DISC-18`). Crucially, `rcRateFind_11nViVo` (`.text+0x02970`, used for `AC_VI` IPTV `CS4` & `AC_VO` VoIP `EF`) **omits this `-10 dB` idle penalty (`0 dB` cliff)**. **Patch**: `0x00e90 -> 0x24040000`, `0x00ea8 -> 0x00002021`. |
| **`XW-BUG-02`** | `ath_rate_atheros.ko` `.data+0x0444`/`.data+0x046c` (`ar5416_11na/ng_ratetable`) & `ath_dev.ko` `.text+0x1fa30` (`ath_lookup_rate`) | **MEDIUM** | `probeInterval = 50 ms` (`+0x08`) and `rssiReduceInterval = 50 ms` (`+0x0c`) cause `rcUpdate_ht` (`.text+0x00ab4..0x00b5c`) to decay `rssiAckValidMin` by `2 dB` every `50 ms` down to `initialRateMax = 0x08` (`MCS0/8`), while `*isProbe = 1` (`0x01020`) forces `ath_lookup_rate` (`0x1fa30`) to return `aggr_limit = 0` (single unaggregated MPDU at `0x204ec`, `FMX-DISC-22`). **Patch**: `.data+0x044c/0x0474 -> 20 ms`, `.data+0x0450/0x0478 -> 500 ms`. |
| **`XW-BUG-03`** | `ath_rate_atheros.ko` `.text+0x13550..0x13558` (`ath_rate_findrate`) & `.text+0x12c68..0x12c70` (`ath_rate_tx_complete_11n`) | **HIGH** | Even though `ubnt_ewma_delegate_on=1` (`ubnt_ewma_delegate_in_use=1` at `.bss+0x0004`) and `ath_rate_node_alloc` (`0x13d40`) initializes `ubnt_ewma_ht.ko` (`0x3220($s0)`), both functions test bit `0x10` (`IEEE80211_FEXT_UPOLL`) of `0x3c(avp)`. On standard `802.11n` CSMA/CA associations (`OpenWrt` AP or `allow_80211=1`), bit `0x10 == 0`, completely bypassing `ubnt_ewma_ht.ko`. **Patch**: `0x13558 -> 0x00000000` (`nop`), `0x12c70 -> 0x00000000` (`nop`). |
| **`XW-Q-INV`** | `ath_dev.ko` `.data+0x0140..0x014c`, `.text+0x1d3a8..0x1d560` & `umac.ko` `.text+0x6ce30` | **INFO** | Unlike `WA`/`XC` (`ATHDEV-BUG-03`), `XW` `ath_dev.ko` preserves `AC*Minfree = 0/16/32/48`, `axq_depth <= 48` watchdog threshold (`0x1d484`), and `<= 16` unconditional fast-admit (`0x1d534`). Because `umac.ko` `osif_vap_hardstart_generic` has no `set_multiq` and never calls `netif_stop_queue`, `ath0 txqueuelen=64` (`48 + 16`, `FMX-DISC-24` / `Stage 81C Champion v21`) is exact. |

---

## 6. Stage 90B/93A Addendum — `airOS 8` `WA`/`XC` `ath_pktlog.ko` (`PKTLOG-BUG-01`) & `ath_hal.ko` (`31` Total Bugs, `13` Patched Binaries) (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`ath_pktlog.ko` `20,680` B, `ath_dev.ko` `287,216` B) & `QCA firmware / HAL` (`ath_hal.ko` `367,456` B `WA` / `360,896` B `XC`) — verified via [`dissect_stage90b_ath_hal_and_pktlog_ko.py`](../tools/re/dissect_stage90b_ath_hal_and_pktlog_ko.py) & [`STAGE90B_ATH_HAL_AND_PKTLOG_FULLREA_BINARY_DISSECTION.md`](STAGE90B_ATH_HAL_AND_PKTLOG_FULLREA_BINARY_DISSECTION.md) (`0` relocation overlaps).

| Bug ID | Module & Offset | Severity | Defect Summary & Verified Stage 90B/93A Binary / Runtime Fix (`CONFIRMED`) |
| :--- | :--- | :--- | :--- |
| **`PKTLOG-BUG-01`** | `ath_pktlog.ko` `.init.text+0x00118..0x00138`, `.exit.text+0x00000..0x00040` & `ath_dev.ko` `42` `.rel.text` sites | **MEDIUM/HIGH** | On stock `airOS 8` (`WA` & `XC`), `ath_pktlog.ko` `init_module` unconditionally registers `pktlog_ani` (`ath_hal_log_ani_callback_register` at `0x00120`) and populates `g_pktlog_funcs` (`ath_dev.ko` `.bss+0x0000` at `0x00128`) and `g_pktlog_rcfuncs` (`0x00138`). Because `WA`/`XC` `ath_dev.ko` has **`42` `.rel.text` references to `g_pktlog_funcs`** (vs **`0`** in `XW.v6.1.4`), every direct-attach TX/RX descriptor executes an indirect `jalr` into `pktlog_txctl` (`.text+0x00ab8`, `152`-byte stack frame + 10 saved registers `$s0..$s7, $ra`), `pktlog_txstatus` (`.text+0x00e84`), or `pktlog_rx` (`.text+0x0108c`) before checking `log_state & 1`. **Runtime Fix**: `rmmod ath_pktlog 2>/dev/null \|\| true` triggers `cleanup_module` (`.exit.text+0x00000..0x00040`), zeroing `g_pktlog_funcs`, `g_pktlog_rcfuncs`, and `ath_hal_log_ani_callback_register(NULL)`. **Binary Patch**: `wa_8725_ath_pktlog_stage90b_patched.ko` & `xc_8725_ath_pktlog_stage90b_patched.ko` (`6` sites, `0` relocation overlaps). |
| **`HAL-REG-AUDIT`** | `ath_hal.ko` `.text+0x11904`, `0x119a8`, `0x23fb8`, `0x25cb0` (`WA`) | **INFO** | Dissects `ar9300_set_slot_time` (`AR_D_GBL_IFS_SLOT = 0x1070`, `us >= 9`), `ar9300_set_ack_timeout` (`AR_TIME_OUT = 0x8014` 14-bit `0x3fff` mask, proving `acktimeout=25` in `PtP Champion v8`), `ar9300_adjust_difs` (`AR_DLCL_IFS = 0x1040..0x104c`), and `ar9300_ani_init_defaults` (`0x9810..0x9e10`, `spurImmunityLevel=3`, `firstepLevel=2`). |



