<!-- doc-head: Stage 1222A RE reconciliation matrix over Wave 30 receipts 1218A..1221A: settles radar-symbol ownership from the pinned umac.ko/ath_dev.ko images, adjudicates the 4096-QAM penalty offset, delegates the bmiss timeout value to 1220A, and reports measured coverage instead of assuming completeness. Static only, no radio. -->
# Stage 1222A: RE Reconciliation Matrix

- **Claim status**: `CONFIRMED` for the static dimensions; `UNKNOWN` where the bytes do not discriminate
- **Attribution**: `external controller (offline static binary RE)`; no radio, no SSH, no firmware write
- **Tool**: `tools/verify/verify_stage1222a_re_reconciliation_matrix.py`
- **Receipt**: `artifacts/verification/stage1222a_re_reconciliation_matrix.json`
- **Evidence class**: `CONFIRMED_STATIC_BINARY`
- **Suite**: `tests/test_stage1218a_to_1223a_suite.py`

## 1. Charter

Wave 30 carried four RE stages. Two historical contradictions had survived
several waves without a decision:

1. the `ubnt_poll_host` bmiss / missing-poll timeout, quoted as `30 s` in one
   lineage and as `1,800,000 ms` in another;
2. the 4096-QAM penalty thresholds, attributed to Stage 12 in one lineage and
   to Stage 249A in another (Stage 1214A had already recorded the numeric pair
   as `25` vs `60` without deciding the assignment).

This stage adds two further contradictions. One is settled directly by the
module images: which module owns the `ubnt_radar_mode` symbol, `umac.ko` or
`ath_dev.ko`. The other is a receipt-contract mismatch inside this wave: 1219A
carries the correct LTU census value as `ko_count = 154` under a non-contract
key and never states the `eab_driver.ko` absence, so the pinned contract cannot
consume it even though the measurement agrees. The matrix records that as
unresolved rather than treating agreement of values as agreement of schema.

The matrix is a reconciliation layer, not a second measurement wave. It
re-measures only the dimensions that the local pinned images can decide
unaided, and it delegates value-level questions to the stage that owns them.
That split is deliberate: a reconciliation artefact that re-derives everything
would hide upstream disagreement instead of exposing it.

## 2. Method

| Step | Rule |
| :--- | :--- |
| Serialisation | every payload passes through `decase()`, which lowercases mapping keys and raises on any case-insensitive sibling collision, so a colliding receipt is never written |
| Upstream lookup | `find_all` / `scalar` walk the receipt tree; a key that appears more than once with different values returns `AMBIGUOUS` instead of picking one |
| Image identity | a candidate `.ko` is accepted only when its byte size equals the pinned size; a differently sized image is refused, never silently substituted |
| Independent probe | radar ownership and QAM symbol multiplicity are measured here from the pinned images |
| Delegation | the bmiss value and the penalty offset are read from 1220A and echoed as `resolved_to`; they are never invented |
| Determinism | no wall-clock field is written, so repeated runs are byte-identical |

## 3. Measured static facts

All values below were measured on this workstation against files already on
disk. They are reproducible with the commands in section 7.

| Fact | Value | Method |
| :--- | :--- | :--- |
| `umac.ko` size | `2,356,432` B | `wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko` |
| `umac.ko` ELF class | MIPS32 big-endian | ELF header |
| `ubnt_radar_mode` offset in `umac.ko` | `952628` | `bytes.find(b"ubnt_radar_mode\x00")` |
| `ubnt_radar_mode` in `ath_dev.ko` | `0` occurrences | same probe over the `287,216` B image |
| `ame_core.ko` `penaltyThreshold` | `1` occurrence | `afltu_2.4.2` tree |
| `ame_core.ko` `startThrd_4096` | `1` occurrence | same image |
| `ame_core.ko` `stayThrd_4096` | `1` occurrence | same image |
| LTU `2.4.2` tree | `154` `.ko` modules | `rglob("*.ko")` |
| `eab_driver.ko` | absent: `0` loose, `0` tar members | tree and tar scan |
| `ubnt_poll_host_sta_bmiss_ind` | `1` occurrence | `ubnt_poll_host.ko`, `189,880` B |
| `add_timer` / `mod_timer` | `1` / `1` | same image |

The `952628` offset is a string-table offset, not a virtual address. It is the
position of the NUL-terminated symbol name in the file image, which is why it is
comparable across the binaries only when the image size matches.

## 4. Reconciliation rows

| Conflict | Claim A | Claim B | Resolved to | Adjudication |
| :--- | :--- | :--- | :--- | :--- |
| `bmiss_timeout_value_30s_vs_1800000ms` | `30 s` | `1,800,000 ms` (`1,800 s` or `30 min`) | value reported by 1220A, or `UNKNOWN` | delegated to 1220A |
| `qam4096_penalty_threshold_offset_stage12_vs_stage249a` | Stage 12 lineage | Stage 249A lineage | `ame_core.ko@<1220A offset>` when the symbol is single-instance | symbol multiplicity plus 1220A offset |
| `radar_mode_owning_module_ath_dev_vs_umac` | `ath_dev.ko` / DFS | `umac.ko` | `umac.ko@952628` | independent static probe |
| `ltu_module_census_contract_keys_missing` | Contract keys and envelope | 1219A `ko_count = 154` only | `UNRESOLVED` until 1219A conforms | receipt key contract |

Two limits are recorded in the receipt rather than papered over:

- the arithmetic identity `1,800,000 ms = 1,800 s = 30 min` means claim A and
  claim B cannot both be the same constant unless a factor-of-60 unit error is
  involved. Which side carries the unit error is not decidable from strings and
  symbol tables, so the matrix does not decide it;
- the `25` vs `60` numeric assignment is not decidable from symbol tables. Only
  the offset dimension is adjudicated: a symbol present exactly once cannot
  legitimately carry two different offsets, so any second offset claim is
  refuted even while the numeric value stays `UNKNOWN`.

## 5. Coverage semantics

`coverage_measured` is defined in the receipt itself as:

```
coverage_measured = conflicts resolved with static evidence / conflicts_total
```

It is a measurement, not a target. The gate verifies only `0 <= coverage <= 1`
and the presence of the definition string. Nothing in the toolchain requires
`1.0`, and a deliberately unresolved conflict lowers the number instead of
being dropped from the denominator. `receipts_found` is reported separately and
is never folded into the ratio.

When a pinned image is missing or a size differs from the pin, the dependent
dimension stays unresolved. That is the intended failure mode.

## 6. Gaps and known absences

- the bmiss constant is not re-derived here; MIPS delay-slot analysis remains
  1220A ownership;
- `eab_driver.ko` is absent from the LTU `2.4.2` tree, so no eab offset can be
  cross-checked against any image in this wave;
- `ath_dev.ko` ships no `ubnt_radar_mode` symbol, so radar-mode DFS behaviour
  cannot be attributed to that module from this corpus;
- the `aflturocket_2.4.2` tree carries `166` `.ko` while `afltu_2.4.2` carries
  `154`; the census contract pins the `154` tree, and the other is not used as a
  denominator;
- upstream receipt shapes are read tolerantly, so a missing field degrades to
  `null` in `upstream` rather than crashing the matrix.

## 7. Reproduction

```
python tools/verify/verify_stage1222a_re_reconciliation_matrix.py
python tools/verify/verify_stage1223a_wave30_opencode_gate.py
python -m pytest tests/test_stage1218a_to_1223a_suite.py -q
```

A one-off probe of the two pinned images, equivalent to the tool's own:

```
python -c "from pathlib import Path; b=Path('artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko').read_bytes(); print(len(b), b.find(b'ubnt_radar_mode\x00'))"
```

## 8. Safety

Read-only over local files. No socket is opened, no IP is contacted, no firmware
is written, no module is loaded. The receipt pins
`meta.radio_safety = "static only"`, a `static` scope and a non-empty `gaps`
list, and the Wave 30 gate re-asserts all three independently.
