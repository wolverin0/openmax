<!-- doc-head: Stage 1059A builds the debugfs write-syntax dictionary every PtP knob citation has to come from, with each literal byte-verified inside the extracted mac80211.ko, zero ath10k entries and zero umac entries; CONFIRMED_STATIC_BINARY, static only, no radio -->
<!-- /doc-head -->
# Stage 1059A - the debugfs write-syntax dictionary for the PtP knob set

Evidence class: `CONFIRMED_STATIC_BINARY`. `radio_safety: static only`. Scope: static only; offline byte re-read of the extracted mac80211.ko plus the 1031A and 1032A receipts, no module loaded, no debugfs file opened, no radio contacted.

- **Receipt**: [`artifacts/autoresearch/stage1059a_ptp_ko_debugfs_write_syntax_dictionary.json`](../artifacts/autoresearch/stage1059a_ptp_ko_debugfs_write_syntax_dictionary.json)
- **Tool**: [`tools/verify/build_stage1059a_ptp_ko_debugfs_write_syntax_dictionary.py`](../tools/verify/build_stage1059a_ptp_ko_debugfs_write_syntax_dictionary.py)

## Question

Before a hotplug script may write a PtP knob, three things must hold: the knob exists as a debugfs
file, the writer accepts a specific literal syntax, and that syntax is provable from an artefact
rather than from a field name. A field name alone is not syntax. This stage freezes the provable
set into one dictionary so later audits cite a single receipt instead of re-arguing the question.

## Sources

| Stage | Role here | Receipt |
| :--- | :--- | :--- |
| 1031A | every entry. `sscanf` literals with file offsets, call sites and write handler extents | `stage1031a_mac80211_aql_debugfs_write_syntax_re.json` |
| 1032A | witness only. Confirms each debugfs file name exists as a `.rodata` field name | `stage1032a_mac80211_aqm_and_airtime_check_re.json` |
| 1058A | consumer. Twelve versioned hotplug scripts audited against this dictionary | `stage1058a_hotplug_vs_ko_debugfs_syntax.json` |

Module re-read: `artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/mac80211.ko`, 829464 bytes, sha256
`19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416`. 1031A lists 21 format literals; all
8 were re-read at their recorded offset and matched with a NUL
terminator. 8 of them are `sscanf` write literals, and those are the
dictionary.

## Dictionary

| knob | debugfs file | write syntax (literal) | accepted form | evidence | grade |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `aql_txq_limit` | `aql_txq_limit` | `%u %u %u` | `<u32> <u32> <u32>` | Stage 1031A | CONFIRMED |
| `fq_limit` | `aqm` | `fq_limit %u` | `fq_limit <u32>` | Stage 1031A | CONFIRMED |
| `fq_memory_limit` | `aqm` | `fq_memory_limit %u` | `fq_memory_limit <u32>` | Stage 1031A | CONFIRMED |
| `fq_quantum` | `aqm` | `fq_quantum %u` | `fq_quantum <u32>` | Stage 1031A | CONFIRMED |
| `limit` | `UNRESOLVED` | `limit %u %u %u` | `limit <u32> <u32> <u32>` | Stage 1031A | INFERRED |
| `mcast` | `aql_txq_limit` | `mcast %u` | `mcast <u32>` | Stage 1031A | CONFIRMED |
| `strict` | `UNRESOLVED` | `strict=%d` | `strict=<int>` | Stage 1031A | INFERRED |
| `timeout` | `UNRESOLVED` | `timeout=%d` | `timeout=<int>` | Stage 1031A | INFERRED |

`entries_total` = 8, `from_mac80211` = 8,
`from_umac_proxy` = 0, `ath10k_sourced` = 0.

## How a file is bound

The call site of each literal is compared against the 4
write-side extents that 1031A enumerated. Containment inside an extent is the binding rule; the
handler label carried by 1031A is recorded but not trusted. 5
literals land inside `aqm.write` or `aql_txq_limit.write` and are `CONFIRMED`.
3 land outside every enumerated extent and stay `INFERRED` with
`debugfs_file` `UNRESOLVED`: `limit`, `strict`, `timeout`. Calling those bound would be a fabrication.

## What this dictionary refuses

- **ath10k**: `ath10k_sourced` is 0. `ath10k_core.ko` does not exist in the
  1,169 module corpus, so an ath10k write syntax cannot be cited from this bench and is not.
- **umac proxy**: `from_umac_proxy` is 0 across
  8 umac receipts, of which 0 carry
  `debugfs` vocabulary and 0 carry `sscanf` vocabulary. Stage
  1055A reports 31 umac `.rodata` literals; those are message
  text with printf conversions attributed to a symbol stem, not a `sscanf` write format, so none is
  promoted here.
- **duplicate knobs**: 0.

## Contradictions

- none. No entry contradicts another, and no literal failed the byte re-read.

## Consumer

Stage 1058A receipt `stage1058a_hotplug_vs_ko_debugfs_syntax.json` reports `scripts_found=12`, `writes_total=36`, `writes_to_aqm=0` and `aqm_is_file=1`. Its `proven_syntax` quotes 5 literals, 5 of which this dictionary carries verbatim, and it cites Stage 1031A at `evidence_stage`. The citation is not accepted on faith: the literal set is the tie.

## Gaps

- The dictionary is built from the Stage 1031A extraction: each format literal is re-read byte for byte from the module, but the relocation walk that produced the call sites and the handler extents was not repeated here.
- Three sscanf literals (strict=, limit, timeout=) have no write handler range containing their call site in the 1031A enumeration, so their debugfs file stays UNRESOLVED and they are graded INFERRED rather than CONFIRMED.
- The aql_txq_limit access-category bound of 4 is carried from the 1031A sltiu decode and is not re-decoded in this stage.
- from_umac_proxy is 0 because no umac receipt in the corpus carries debugfs or sscanf vocabulary; absence across the receipt corpus is not proof that umac.ko has no debugfs writer, which only a direct umac.ko scan could settle.
- ath10k_core.ko is absent from the 1,169 module corpus, so no ath10k debugfs write syntax can exist in this dictionary; the absence is inherited from Stage 1055A..1057A and is not re-swept here.
- The optional Stage 1058A cross reference records what that receipt reports. It does not re-audit the twelve hotplug scripts and it does not re-derive their write tokens.
- No dynamic validation: nothing was loaded, no debugfs file was opened, no radio or host was contacted.

## Claim boundary

The dictionary binds literals to files by extent containment inside one extracted module. It does
not prove that any device exposes those files, that any value is safe, or that a hotplug script
uses the right form. No radio, host or firmware image was touched.
