<!-- doc-head: Stage 1105A - the two v17 kits checked write by write against the mac80211 debugfs grammar Stage 1031A recovered; static only, no radio, findings are a provenance over-citation and two recovery-path gaps -->
# Stage 1105A - v17 kits versus the kernel debugfs handlers

Auditor: `tools/re/audit_stage1105a_v17_kits_vs_ko_debugfs_handlers.py`
Receipt: `artifacts/autoresearch/stage1105a_v17_kits_vs_ko_debugfs_handlers.json`
Provenance class: `CONFIRMED_STATIC_BINARY` (static text and byte reading only).

## 1. Why this stage exists

Both v17 kits carry the same header claim:

```
# write_syntax_source: Stage 1031A (aql_txq_limit "<ac-idx 0..3> <low> <high>", aql_threshold plain u32,
#   aqm "fq_limit N" / "fq_memory_limit N" / "fq_quantum N"). Read-table format: Stage 955A.
```

A citation in a comment is not evidence. A debugfs file has one handler, and that handler decides
what a payload may be; a payload it cannot parse is rejected inside the kernel, and because every
write is followed by `2>/dev/null || true` the rejection is silent. The stage therefore resolves every
write in both kits from the kits' own `case` tables and constants, then asks the receipt the header
cites whether that write is in it.

## 2. Measured kit identity

| kit | path | bytes | expected |
| :--- | :--- | ---: | ---: |
| `pbe5ac-v17` | `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh` | 12,029 | 12,029 |
| `wa-v17` | `firmware/openwrt/common/fmx_wa_v17_pareto_aqm_aql_busybox_kit.sh` | 10,160 | 10,160 |

The two differ only by the pbe5ac watchdog: `operstate` and `carrier` preflight checks, a bounded
wait, and an auto-rollback when the link does not come up. The write path is byte-identical, so every
grammar verdict below applies to both. CONFIRMED.

## 3. The writes, resolved

Ten write intents per kit, resolved against the kit's own tables (`idx_of` maps VO 0, VI 1, BE 2,
BK 3; `target` maps those to the constants).

| # | line (wa / pbe) | file | payload | verdict |
| ---: | :--- | :--- | :--- | :--- |
| 1 | 178 / 209 | `aql_txq_limit` | `0 500 1000` | CONFIRMED_VALID |
| 2 | 178 / 209 | `aql_txq_limit` | `1 1500 3000` | CONFIRMED_VALID |
| 3 | 178 / 209 | `aql_txq_limit` | `2 3000 6000` | CONFIRMED_VALID |
| 4 | 178 / 209 | `aql_txq_limit` | `3 1500 3000` | CONFIRMED_VALID |
| 5 | 180 / 211 | `aql_threshold` | `12000` | UNKNOWN |
| 6 | 182 / 213 | `aqm` | `fq_limit 2048` | CONFIRMED_VALID |
| 7 | 183 / 214 | `aqm` | `fq_memory_limit 4194304` | CONFIRMED_VALID |
| 8 | 184 / 215 | `aqm` | `fq_quantum 1514` | CONFIRMED_VALID |
| 9 | 186 / 217 | `tcp_notsent_lowat` | `131072` | INFERRED_VALID |
| 10 | 187 / 218 | `default_qdisc` | `fq_codel` | INFERRED_VALID |

Summary: `writes_total=20`, `valid=18`, `invalid=0`, `unknown=2`, with
`writes = valid + invalid + unknown` stated in the receipt so the identity is not left to guesswork.
Per kit: 10 writes, 9 valid (7 confirmed, 2 inferred), 0 invalid, 1 unknown. `invalid_lines` is empty.

## 4. What Stage 1031A actually proves

Two grammars, transcribed from the receipt rather than re-derived:

- `aql_txq_limit` write parses `sscanf(buf, "%u %u %u")`, tests the returned count equal to 3, and
  bounds the first value with `sltiu` against 4; the same handler also accepts `"mcast %u"`.
- `aqm` write parses `"fq_limit %u"`, `"fq_memory_limit %u"` and `"fq_quantum %u"`, so the knob name
  travels inside the payload.

Its `debugfs_bindings` list has five entries: `aql_enable`, `aql_pending`, `aqm`, `airtime_flags`,
`aql_txq_limit`. `aql_threshold` is not among them, and neither Stage 1032A nor Stage 1033A closes
that. Stage 1104A, present at generation time, attributes handlers for `airtime_flags` (`kstrtou16`),
`aql_enable` (`copy_from_user` plus an ASCII compare) and `aql_pending` (read-only, no write handler)
- and mentions `aql_threshold` zero times. So the `aql_threshold` write is UNKNOWN, and the kits'
blanket citation is wider than the evidence it names. That is the only defect present in both kits.

## 5. The hypotheses, separately

- Brief: an invalid `echo 300 > .../aqm/fq_quantum` directory-style write. Measured: zero occurrences.
  Neither kit addresses `aqm` as a directory; both send the knob name inside the payload, which is the
  form the handler parses. REFUTED.
- Brief: `aql_threshold` plain u32 belongs to the proven grammar. Measured: it is not in the receipt
  and not in 1104A. The write may well be accepted, but no artefact in this corpus says so. UNKNOWN,
  not confirmed.

## 6. Findings that are not grammar errors

1. Provenance over-citation, both kits, line 4: the header block claims `aql_threshold plain u32`
   under a `Stage 1031A` citation that does not contain it. Documentation defect, no runtime effect,
   and it is the reason a later reader could believe an unproven write is proven.
2. Recovery-path asymmetry, `wa-v17` line 250: `do_writes || fail 'write failed; run --rollback'`.
   The pbe5ac kit instead rolls back automatically; the write path is identical, so the wa kit leaves
   a partially applied profile in place and relies on the operator reading the exit code.
3. Readback mismatch is not rolled back, both kits (`do_verify` at wa 251, pbe 299): the non-zero
   return propagates under `set -e` and exits, with the new profile still applied. INFERRED from shell
   semantics; nothing was executed in this stage.
4. Rollback coverage, both kits (`aqm` restore at wa 202, pbe 233): rollback re-emits the four per-AC
   rows and the three `aqm` knobs, and never re-emits the BC/MC row, although the BC/MC value is
   captured in the snapshot and printed by the read table.

## 7. Which binary the grammar belongs to

`firmware/` ships 13 `mac80211*.ko` artefacts across 7 distinct sha256 values. Exactly one of them,
`mac80211_teb.ko`, is byte-identical to the module Stage 1031A analysed
(`19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416`). The other twelve, including
the 4-address and `6.6.110` variants, are different binaries whose handler set was not measured here.
Quoting a grammar proven on one binary for a kit that ships several is a provenance risk worth stating
plainly.

## 8. AC index mapping

The kits assert VO 0, VI 1, BE 2, BK 3. That matches the order of the read table (`VO`, `VI`, `BE`,
`BK`) and the upstream enum, but Stage 1031A records that the per-AC array stride was not proven. If
the array were ordered differently, every limit would land on the wrong AC while still passing the
`0..3` bound. INFERRED, and listed as a gap rather than a finding.

## 9. Claims

| id | label | claim |
| :--- | :--- | :--- |
| C1 | CONFIRMED | both kits exist at the briefed byte counts and share a byte-identical write path |
| C2 | CONFIRMED | the four `aql_txq_limit` writes satisfy the proven three-decimal form with the index in 0..3 |
| C3 | CONFIRMED | the three `aqm` writes carry the knob name in the payload, as the handler parses |
| C4 | REFUTED | no kit writes `aqm` as a directory |
| C5 | UNKNOWN | the `aql_threshold` write has no proven grammar in this corpus |
| C6 | CONFIRMED | both headers cite Stage 1031A for a write Stage 1031A does not bind |
| C7 | CONFIRMED | the two kits recover differently from a failed write |
| C8 | CONFIRMED | rollback never restores the BC/MC row |
| C9 | INFERRED | a readback mismatch exits without rolling back |
| C10 | INFERRED | the AC index to AC name mapping is assumed, not proven |
| C11 | CONFIRMED | the grammar is proven for one shipped artefact, not for the twelve others |
| C12 | CONFIRMED | Stage 1104A does not bind `aql_threshold`, so the UNKNOWN verdict survives it |

## 10. Gaps

- `aql_threshold` write syntax unproven: binding its `file_operations` addend, or disassembling its
  store handler, would settle whether `12000` is accepted.
- The two proc targets are INFERRED_VALID on payload shape only; the kernel proc handlers are not in
  this corpus, and whether `sch_fq_codel` is loaded when `default_qdisc` is written is not measured.
- No script was executed and no radio contacted: a rejected debugfs write returning a non-zero errno
  to `echo` is an inference from the parse test, not a traced return path.
- The AC array order is assumed; Stage 1031A leaves the stride open.
- The Pareto vector is operator-supplied and traces to no receipt in this corpus; this stage audits
  the grammar, not whether those numbers are the right tuning.
- Rollback was read, not exercised; the BC/MC row is not restored at all.
- Stage 1104A is cited for its handler inventory only and was not re-derived here.

## 11. Reproduction

```
python tools/re/audit_stage1105a_v17_kits_vs_ko_debugfs_handlers.py --print-summary
STAGE1105A kits_found=2 writes_total=20 valid=18 invalid=0 unknown=2 aql_threshold_bound=0 stage1104a_present=1 corrected_lines=7
```

Two consecutive runs produce a byte-identical receipt
(`b6fabeea760c85c87c2dced7a6777b27ea16300e93dbbd878d66795ab9dff330` at generation).
