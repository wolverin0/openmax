<!-- doc-head: STAGE533A_UBNT_POLL_SWR_LIMIT_AND_SLOT_GUARD_RE.md preserved document content -->
<!-- /doc-head -->



# Stage 533A — `ubnt_poll_host.ko` `swr_limit` (`0x00b404`) & Dynamic UL Slot Guard-Time (`rtt_us + 21 us`) Binary Dissection (`WA` & `XC`)

- **Claim Classification**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` `0x001790..0x00185c`, `0x00b404..0x00b468`, `0x014f7c..0x015024`) + `QCA firmware` (`QCA988x` `HT_COMM` msg `0x1f` / `0x0c` / `0x0d`)
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.

---

## 1. `ubnt_poll_host_set_node_rtt` (`0x001790..0x00185c`): Exact Distance & UL Slot Guard Formulas

In both `WA.v8.7.25` and `XC.v8.7.25` `ubnt_poll_host.ko`, `ubnt_poll_host_set_node_rtt` (`.text + 0x001790`, `208 B`) converts the measured round-trip propagation time `$s0` (`rtt_us`, gated by `slt $v0, $a2, 0xffff` at `0x001794..0x001798`) into physical distance (`ni + 0x23a0`) and per-station UL TDMA slot guard time (`ni + 0x2394`):

```assembly
0x0017d8: sll   $a0, $s0, 3        ; $a0 = 8 * rtt_us
0x0017dc: sll   $v1, $s0, 1        ; $v1 = 2 * rtt_us
0x0017e0: addu  $v1, $v1, $a0      ; $v1 = 10 * rtt_us
0x0017e4: sll   $a0, $v1, 4        ; $a0 = 160 * rtt_us
0x0017e8: subu  $v1, $a0, $v1      ; $v1 = 150 * rtt_us (c/2 = 150 m/us)
0x0017ec: addiu $a0, $s0, 0x15     ; $a0 = rtt_us + 21 us (0x15 SIFS + PHY turnaround)
0x0017f0: sw    $v1, 0x23a0($v0)   ; ni->ni_distance_m = 150 * rtt_us
0x0017f4: sw    $a0, 0x2394($v0)   ; ni->ni_slot_guard_us = rtt_us + 21
```

When `$a1 == NULL` (broadcast/sector-wide path at `0x001808..0x001834`), `150 * rtt_us` is written to `ic + 0x1e5d8` (`-0x1a28($s2)` where `$s2 = ic + 0x20000`) and bit `0` is set at `ic + 0x1e5ce` (`-0x1a32($s2)`).

---

## 2. `ubnt_poll_host_set_swr_limit` (`0x00b404..0x00b468`) & `ubnt_poll_ht_comm_parse` (`0x014f7c..0x015024`)

1. **`ubnt_poll_host_set_swr_limit` (`0x00b404`, `104 B`, `HT_COMM` Msg `0x1f = 31`)**:
   - Masks unicast retry limit `$a1 & 0xff` (`0x1c($sp)`) and multicast retry limit `$a2 & 0xff` (`0x1d($sp)`), sets `msg.type = 0x001f` (`0x00b408: addiu $v1, $zero, 0x1f; 0x00b420: sh $v1, 0x16($sp)`), and dispatches `ubnt_poll_host_ht_comm_tx` (`0x00b454`) over `WMI 0x9065`.
2. **`ubnt_poll_ht_comm_parse` (`0x014f7c..0x015024`) Slot Geometry Struct (`host_data`)**:
   - `0x0200($s0)`: `down_slot_dur_us` (`6,700 us` on `Panel2 .82`; `30,000 us` on `Panel3 .83`)
   - `0x0204($s0)`: `up_slot_dur_us` (`3,300 us` on `Panel2 .82`; `30,000 us` on `Panel3 .83`)
   - `0x0208($s0)`: `cbp_dur_us` (`180 us` on `Panel2 .82` vs `900 us` on `Panel3 .83`)
   - `0x020a($s0)`: `ul_slot_guard_us` (`sh $t1, 0x20a($s0)` at `0x014fcc`)
   - `0x0220($s0)`: `defer_timeout_ms` (`20,000 ms` = `0x4e20` at `0x015024`).

---

## 3. Impact on `Panel2 (.82)` (`Fixed 10 ms 67/33`) vs `Panel3 (.83)` (`Flexible`)

- On **`Panel2 (.82)`** (`22` CPEs, max distance `2,674 m` $\rightarrow$ `rtt_us = 18 us`, `slot_guard_us = 18 + 21 = 39 us`), `3,300 us` of total UL time divided across `22` CPEs yields `150 us` per CPE, of which **`39 us` (`26.0%`)** is consumed by the `rtt_us + 21` guard time and `cbp_dur` is compressed to `180 us`. A-MPDU subframes exceeding the remaining `111 us` payload window are preempted at slot expiry into `mpdus_requed` (`139.75M = 20.31%`).
- On **`Panel3 (.83)`**, `polling=disabled` in `system.cfg` while `uph_wifi0/enable=1` leaves frames unscheduled across `30,000 us` slots until they exhaust `swr_limit` (`HT_COMM` `0x1f`), driving `9.52M` `excess_retries` (`24.84%`).

---

## 4. Reproducible Verification
- Tool: [`dissect_stage533a_ubnt_poll_swr_limit_and_slot_guard_re.py`](../tools/re/dissect_stage533a_ubnt_poll_swr_limit_and_slot_guard_re.py)
- Artifact: [`stage533a_ubnt_poll_swr_limit_and_slot_guard_re.json`](../artifacts/autoresearch/stage533a_ubnt_poll_swr_limit_and_slot_guard_re.json)
- Test Suite: [`test_stage533a.py`](../tests/test_stage533a.py)
