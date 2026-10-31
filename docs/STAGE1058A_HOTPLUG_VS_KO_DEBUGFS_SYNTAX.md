<!-- doc-head: Stage 1058A audits all 12 versioned WA champion hotplug scripts against the Stage 1031A binary-proven debugfs write grammar, refutes the brief's aqm/fq_quantum hypothesis as absent, and finds a silent aql_txq_limit defect in 12 of 12 -->
<!-- /doc-head -->
# Stage 1058A - hotplug script debugfs writes versus the kernel's own grammar

Static only. The twelve scripts were read as text and `mac80211.ko` as bytes. Nothing was executed, no
radio was contacted, no device was written. Source of record:
`artifacts/autoresearch/stage1058a_hotplug_vs_ko_debugfs_syntax.json`
(`evidence_provenance_class` = `CONFIRMED_STATIC_BINARY`).

## 1. Corpus reality

Twelve versioned files exist, `v9` through `v20`, contiguous, totalling **29,485 bytes**.

**CONFIRMED**: the unversioned `99-fmx-wa-universal-champion` does **not** exist
(`unversioned_target_present = 0`). Any audit keyed to that filename audits nothing.

## 2. The brief's hypothesis is not the defect present here

The brief proposed that a write such as `echo 300 > .../aqm/fq_quantum` fails because `aqm` is a file,
not a directory.

**REFUTED as a description of this corpus**: no script references `aqm` or `fq_quantum` at all.

- `writes_to_aqm = 0`
- `aqm_as_directory_writes = 0`

The hypothesised failure mode is real in principle but absent in fact. Reporting it as the finding
would have been a fabricated defect.

## 3. `aqm` is a FILE - settled from the binary, not from the brief

Three independent observations, all measured:

1. **Name table.** `aqm` survives as a NUL-delimited standalone string at `.rodata.str1.4+622224`. Its
   positional neighbours in the same string run are:
   `hw_conf, force_tx_status, aql_enable, aql_pending, `**`aqm`**`, airtime_flags, aql_txq_limit,
   aql_threshold, statistics`. That is a flat list of debugfs **filenames**, all siblings.
2. **`fq_quantum` is not a name.** It has **zero** standalone occurrences in the module. It appears
   only inside the read display format (`RW fq_quantum %u`) and the write `sscanf` format
   (`fq_quantum %u`). A directory's members must be names; this never is one.
3. **`aqm` owns a `file_operations`.** Stage 1031A bound it at `.rodata` offset 17852 with a non-null
   read handler (457808) and a non-null write handler (461392). `debugfs_create_dir` takes no `fops`.

A control ruling out an artefact: `debugfs_create_dir` **does** occur in `mac80211.ko` (1 hit), so the
module is capable of creating directories. The absence of a `fq_quantum` name is therefore a property
of how `aqm` was registered, not a limitation of the module.

**CONFIRMED**: `aqm_is_file = 1`. The correct form is the knob name **inside** the payload, not a path
component:

```
echo "fq_quantum 1514" > /sys/kernel/debug/ieee80211/phy0/aqm
```

## 4. The defect that is actually present, in 12 of 12 scripts

Every version writes a **single bare integer** to `aql_txq_limit`. Stage 1031A proved from the binary
that this handler parses `sscanf(buf, "%u %u %u", &ac, &low, &high)` and tests the returned count
`== 3` at `.text+0x70e3c`, bounding the first value with `sltiu` against 4 at `.text+0x70e48`, with one
alternative literal branch `mcast %u`.

A single integer satisfies neither branch: the parse yields count 1, and `"3000"` does not begin with
the literal `mcast`. **The write is rejected inside the handler.** The scripts mask it: every affected
line ends `2>/dev/null || true`, so the handler error and the shell's write error are both discarded
and the script still exits 0.

Exact lines, `v9` line 5 and `v20` line 23:

```
echo 3000 > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit 2>/dev/null || true
echo 4000 > "/sys/kernel/debug/ieee80211/${p}/aql_txq_limit" 2>/dev/null || true
```

| version | line | payload | verdict |
| :--- | ---: | :--- | :--- |
| v9..v15 | 5..8 | `3000` | INVALID - count 1, no `mcast` prefix |
| v16..v20 | 8..23 | `4000` | INVALID - count 1, no `mcast` prefix |

**CONFIRMED**: all twelve versions contain a write the Stage 1031A grammar cannot accept, so the AQL
limit the champion intends to set is never applied. **CONFIRMED**: the rejection is silent by
construction. **CONFIRMED**: v16 raised the payload from 3000 to 4000 and v17 added an
`aql_threshold` write, so the scripts were edited repeatedly without the write *form* ever being
corrected.

## 5. Write verdict census

40 debugfs writes across 12 scripts:

| verdict | count | meaning |
| :--- | ---: | :--- |
| INVALID | 12 | `aql_txq_limit`, proven wrong by Stage 1031A |
| UNPROVEN | 24 | `ath10k`-namespaced, no module in corpus (Stage 1057A) |
| UNKNOWN | 4 | `aql_threshold`, file exists but no fops attributed |

`UNPROVEN` covers `pktlog_filter` (9), `htt_max_amsdu_ampdu` (12), `spectral_scan_ctl` (2) and
`ani_enable` (1). These live under `/ath10k/`, and `ath10k_core.ko` is absent from the corpus, so no
handler exists here to accept or reject them. They are **not** cleared - they are simply unmeasurable
in this stage.

`UNKNOWN` covers the four `aql_threshold` writes. **UNKNOWN**: whether
`echo 24000 > .../aql_threshold` is accepted. The name exists in the table, but Stage 1031A did not
attribute a `file_operations` to it. Binding its fops addend or disassembling its write handler would
settle it.

## 6. What a corrected script would write

From the proven grammar only:

```
# per-AC, one write per index (0..3); the handler rejects any count other than 3
echo "0 4000 4000" > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo "1 4000 4000" > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo "2 4000 4000" > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo "3 4000 4000" > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
# broadcast/multicast branch
echo "mcast 4000" > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
```

**INFERRED**: `mcast %u` sets the BC/MC limit that the read table prints as its final `BC/MC` row.
Stage 1031A proved the literal branch exists but did not follow its store to confirm the target field.

**CONFIRMED**: none of these forms appears in any version. `corrected_versions = []` and
`first_corrected_version = null`.

## 7. Verdict table

| claim | verdict |
| :--- | :--- |
| 12 versioned scripts, v9..v20, no unversioned file | **CONFIRMED** |
| some script writes `.../aqm/fq_quantum` | **REFUTED** - zero references |
| `aqm` is a file, not a directory | **CONFIRMED** - name table, no `fq_quantum` name, fops with r+w |
| all 12 write an unparseable payload to `aql_txq_limit` | **CONFIRMED** - Stage 1031A grammar |
| those rejections are silent | **CONFIRMED** - stderr discarded, exit forced to 0 |
| `aql_threshold` write form is correct | **UNKNOWN** - no attributed handler |
| `ath10k`-namespaced writes are correct | **UNPROVEN** - module absent |
| a rejected write returns an errno to the shell | **INFERRED** - from the parse test |

## 8. Residual gaps

- The accept syntax is proven for two mac80211 files only; everything else is UNKNOWN or UNPROVEN.
- `aql_threshold` has no attributed fops, so its write grammar is open.
- `ath10k`-namespaced writes cannot be validated without the module or matching source.
- Whether the analysed `mac80211.ko` is the module installed on every unit these scripts run on is not
  established: it is the panel1 cutover artefact.
- The claim that a rejected write surfaces an errno is an inference from the parse test, not a traced
  return path.
- Extraction is line oriented: a write split by line continuation, built by command substitution, or
  emitted by a helper script would not be captured.
- The corrected form is derived from the binary's grammar and was **not** verified against a live
  kernel here. Closing that needs an offline replay against a bench unit, which is out of scope.
