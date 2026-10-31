<!-- doc-head: Stage 1190A ubnt_poll_host.ko PtMP rate collapse, silent stall and mixed-mode static RE; 100% offline, static binary only -->

# Stage 1190A - `ubnt_poll_host.ko` rate collapse, silent stall and mixed mode

`evidence_provenance_class`: `CONFIRMED_STATIC_BINARY`. `radio_safety`: `static only`.
No target was contacted, no firmware was written.

## 1. Why two premises had to be corrected first

The brief's own framing was checked against the filesystem before any analysis.

| Premise | Measured | Verdict |
| :--- | :--- | :--- |
| `ubnt_poll_host.ko` is available for real analysis | 10 loose artifacts (7 named exactly, 3 renamed), 6 distinct stock binaries, 141 archives / 209121 members scanned | `CONFIRMED` |
| `eab_driver.ko` is analysable | 0 loose, 0 archive members | `REFUTED` |

`eab_driver.ko` does not exist anywhere in this repository, as a loose file or as a tar
member. Both counts are measured by this stage's own census, over
141 archives and 209121 members, so nothing about its
internals is stated here. That premise was measured, refuted and dropped, not worked around.

## 2. Byte order is the trap in this module

`ubnt_poll_host.ko` is `EM_MIPS`, `ELFCLASS32`, `EI_DATA = 2`. It is **big-endian** MIPS32.
A little-endian decoder turns valid code into plausible nonsense - `syscall`, `ldc2`,
`rscslt` - which reads like a successful disassembly and teaches nothing. The verifier
refuses to decode unless `EI_DATA == 2`, and every offset below comes from a guarded run.

## 3. Versions actually under analysis

| Label | Attestation | Grade |
| :--- | :--- | :--- |
| `WA.v8.7.25` | lib/version = WA.ar934x.v8.7.25.48568.260730.1010 | `CONFIRMED` |
| `XC.v8.7.25` | lib/version = XC.qca955x.v8.7.25.48568.260730.1009 | `CONFIRMED` |
| `XC.v8.7.4-cs` | lib/version = XC.qca955x.v8.7.4-cs.45112.210415.1103 | `CONFIRMED` |
| `WA.v8.7.4-cs` | directory name wa874cs_modules; no version file on disk | `INFERRED` |
| `2XC.v8.7.11` | directory name 2xc_8711_modules; 2XC.v8.7.11 is the Rocket 2AC Prism image per repo knowledge docs | `INFERRED` |
| `unlabelled.build_rootfs` | firmware/build/codex-analysis-20261006/rootfs carries no version file | `UNKNOWN` |

6 distinct stock binaries were analysed, one per distinct SHA-256.
The Stage 73B patched copies in `artifacts/curation/` were excluded: they are not stock
images and must not be cited as evidence.

## 4. Symptom 1 - single-CPE TX rate collapse to 1x

`symptom_support`: `UNKNOWN`.

- `mcs` tokens across all analysed binaries: **0**
- `1x` tokens: **0**
- `vht` tokens: **0**

Those counts are taken over whole files, so they include `strtab`. A zero is a real zero:
this module has no vocabulary for a modulation at all. It therefore cannot select a rate,
cannot lock a rate, and cannot clear a lock. What it does have is a forwarding path:

| Symbol | Mechanism measured |
| :--- | :--- |
| `ubnt_poll_host_set_rate_override` | packs width/retry bitfields (40 MHz selector 0x28, 80 MHz selector 0x50) into an HT-comm message and hands it to ubnt_poll_host_ht_comm_tx |
| `ubnt_poll_host_set_tid5_rate_war` | sets or clears bit 1 (selector 0) or bit 2 (selector 1) in a per-STA byte, and returns immediately for any other selector |

Neither is a rate selector. Rate selection lives outside this module. The honest verdict is
`UNKNOWN`: the binary neither supports nor contradicts a 1x lockup, and saying otherwise
would be invention.

## 5. Symptom 2 - silent stall while associated

`symptom_support`: `INFERRED`.

`ubnt_poll_host_check_sta` contains a bounded inactivity expiry:

- offset `0x1860`, full extent consumed
- threshold `120000 ms` (exactly 120 s)
- action on expiry: `ieee80211_free_node`

The age is formed as `jiffies - node->field_0x40`, scaled by the `*125 << 3 == *1000`
idiom, then compared against a `lui`/`addiu` pair. Past the threshold the function frees
the node and prints a `NOT AUTHORIZED AID ... since ...` diagnostic. It does **not** call
`ieee80211_kick_node` and does **not** call `ath_kickout_node_notify` - both of those live
in the sibling kick path instead. So local state disappears while the peer may still
believe it is associated. That is the shape of a silent stall, but the peer-visible half
is outside this module, so the symptom stays `INFERRED`.

Adjacent finding: `ubnt_poll_host_sta_remove_oldest` is a **capacity** eviction, not an
ageing one. It walks the list, skips nodes whose flags byte matches a mask, keeps the
maximum `jiffies - sta->field_0x70`, and removes that one by MAC. Association loss on this
path is capacity-driven, which argues against a pure staleness model.

## 6. Symptom 3 - mixed M5-on-AC TDMA slot starvation

`symptom_support`: `INFERRED`. Mechanism: `CONFIRMED`.

`ubnt_poll_host_init_ptmp_netconf` selects the PTMP network-configuration profile as
`idx = bw_mhz - 10`, gates it with `sltiu idx, 0x1f`, and otherwise falls to a default. The
31-entry pointer table sits at `.rodata+0x8a4` and its entries are `R_MIPS_32`
relocations, so the mapping is recovered from the relocations rather than guessed from
zeroed in-place words:

| Bandwidth | Profile |
| :--- | :--- |
| 10 MHz | `_ht10_ptmp_netconf` |
| 11-28 MHz | `_ht20_ptmp_netconf` |
| 29-30 MHz | `_ht30_ptmp_netconf` |
| 31-39 MHz | `_ht20_ptmp_netconf` |
| 40 MHz | `_ht40_ptmp_netconf` |
| 80 MHz (any value outside 10..40) | `_ht20_ptmp_netconf` (default) |

The map is not monotone. 29 and 30 MHz select `_ht30`, but 31 MHz falls back to `_ht20`,
so `_ht30` sits at 29-30 rather than at a 30 MHz centre. That is reproduced verbatim from
the relocations, not smoothed over.

There is no 80 MHz profile and no 80 MHz table entry. An AC radio at 80 MHz derives its
slot and duration geometry from the 20 MHz table, while a mixed M5 peer derives its own
from a narrowband table. The selector is `CONFIRMED`; that this is what the field reports
call starvation needs a live slot trace and stays `INFERRED`.

## 7. What 8.7.25 added that older builds do not have

Against the 189880-byte 8.7.25 baseline (154 `STT_FUNC` symbols), every smaller build is a strict subset:

| Function | Present in 8.7.25 | Present in smaller builds |
| :--- | :--- | :--- |
| `ubnt_poll_host_get_fwname` | yes | no |
| `ubnt_poll_host_get_txpower` | yes | no |
| `ubnt_poll_host_set_txpower` | yes | no |
| `ubnt_poll_host_sta_remove_oldest` | yes | no |

4 of the 5 non-baseline builds lack these functions; the remaining 1 (the XC 8.7.25 sibling) carries the same 154 symbols but is not byte-identical.

`sta_remove_oldest` is the only capacity-eviction path in the module and it does not exist on
8.7.4-cs or 8.7.11. Those builds combine a 120 s inactivity expiry with no capacity relief,
so a full STA table has no way to make room. Both versions are still in the field.

## 8. Slot and guard surface that does exist
38 slot-related tunables are exposed as sysctl attribute names:

`cbp_dur`, `cbp_dur_slot`, `cbp_duty_cycle_hwm`, `cbp_duty_cycle_thresh`, `cbp_usable_dur`, `cbp_use_allowed_in_window`, `cbp_use_sta_count_limit`, `cbp_use_txop_cycle_window`, `cfp_dur_min`, `down_dur`, `down_dur_gap`, `down_dur_min`, `duty_cycle_metric_maws`, `duty_cycle_metric_sms`, `ff_cap_rep`, `ff_cbp_slots`, `ff_dack_arbit_max`, `ff_dl_alloc`, `ff_dl_ctrl_rate`, `ff_dl_swr_count`, `ff_frame_dur`, `ff_guard_units`, `ff_mcast_airtime_limit`, `ff_sta_rx_rssi_th`

## 9. Hypotheses

| ID | Claim | Supported |
| :--- | :--- | :--- |
| `H1` | ubnt_poll_host.ko implements a per-STA MCS rate-control algorithm | `no` |
| `H2` | a 1x lockup can be produced or cleared by this module | `no` |
| `H3` | the module forwards a packed rate-class override to the peer | `yes` |
| `H4` | a per-STA inactivity expiry around 120 s frees local node state | `yes` |
| `H5` | association loss is signalled to the peer on that expiry path | `no` |
| `H6` | STA eviction is age-driven rather than capacity-driven | `no` |
| `H7` | the PTMP slot geometry profile is selected from a bandwidth table bounded to 10..40 MHz | `yes` |
| `H8` | an 80 MHz AC radio gets a dedicated 80 MHz PTMP profile | `no` |
| `H9` | TDMA slot and guard geometry is exposed as tunable fields | `yes` |
| `H10` | the module exposes an ATPC surface | `yes` |

5 of 10 hypotheses survived the binary.
The three that failed on the rate question are the three worth naming: no rate algorithm,
no 1x lock, no dedicated 80 MHz profile.

## 10. Gaps

- ubnt_poll_host.ko contains no rate-control algorithm: 0 mcs and 0 1x tokens across every analysed binary, so the 1x-lockup symptom cannot be adjudicated from this module and is reported UNKNOWN rather than forced to a conclusion.
- The rate actually used is chosen outside this module (ath_dev / ath_rate_atheros / QCA firmware), none of which were in scope for this stage.
- The inactivity expiry in ubnt_poll_host_check_sta frees local node state and prints a diagnostic; whether the peer is ever told is decided by the caller, which is outside this module, so the stall symptom stays INFERRED.
- Slot starvation in a mixed M5/AC sector is a runtime airtime question; this stage decodes the profile selector but takes no slot trace, so it cannot confirm that the decoded wrong-profile mechanism is the one the field reports.
- Reasons and enum values passed across module boundaries (for example the literal 0x1b handed to ath_kickout_node_notify) are recorded as literals; their semantic mapping lives in the driver and is left UNKNOWN here.
- Two Stage 73B patched ubnt_poll_host copies exist in artifacts/curation and were deliberately excluded from evidence; they are not stock images.
- No target was executed. Every verdict in this receipt is static-binary only and is labelled CONFIRMED_STATIC_BINARY, never live.

