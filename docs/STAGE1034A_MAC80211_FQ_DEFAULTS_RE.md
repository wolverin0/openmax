<!-- doc-head: Stage 1034A - mac80211 fair-queue defaults measured from static bytes and audited against the Stage 955A attribution; static-binary evidence only, no live execution -->
<!-- /doc-head -->
# Stage 1034A - mac80211 Fair-Queue Defaults

Static reverse engineering of
`artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/mac80211.ko`:
829,464 bytes, sha256 `19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416`,
ELF32 big-endian MIPS, `ET_REL`, 32 sections, 1,974 symbols,
`vermagic=6.6.110 mod_unload MIPS32_R2 32BIT`, build root
`backports-6.12.52/net/mac80211/main.c`.

Scope was 100% offline: one `.ko` read, one existing receipt read, one receipt
written. No SSH, no radio, no firmware write, no debugfs access.

## Verdict

The three integers attributed to Stage 955A are **not** the compiled defaults of
this build. One of the three matches.

| Knob | Claimed as default | Measured static default | Match |
| :--- | ---: | ---: | :--- |
| `fq_limit` | 512 | **8192** | no |
| `fq_memory_limit` | 3145728 (3 MiB) | **16777216** (16 MiB) | no |
| `fq_flows_cnt` | 4096 | **4096** | yes |

`matches_expected` is therefore `1` of `3`, and it is a measured count, not an
assumption. A fourth default, `fq_quantum = 300`, was measured while traversing
the same initialiser and is recorded even though it was not part of the claim.

## The three named functions do not exist

`fq_init`, `fq_tin_dequeue` and `codel_should_drop` each occur **zero** times as
byte strings and zero times in `.symtab`. There are no `fq_`-prefixed symbols at
all. This is `REFUTED` for the names and says nothing about the feature:
mac80211 ships its fair queue as header-inline code, so the bodies are compiled
into their callers and the names never survive.

The feature itself is `CONFIRMED` by two independent artefacts: a nine-knob AQM
readout format string, and a store-level initialiser inside
`ieee80211_txq_setup_flows`.

## Knob surface, read out of the binary

One format blob at file offset 621,636 reproduces the whole surface. Modes are
taken from the blob, not from documentation.

| Knob | String offset | Mode |
| :--- | ---: | :--- |
| `fq_flows_cnt` | 621,656 | R |
| `fq_backlog` | 621,674 | R |
| `fq_overlimit` | 621,690 | R |
| `fq_overmemory` | 621,708 | R |
| `fq_collisions` | 621,727 | R |
| `fq_memory_usage` | 621,746 | R |
| `fq_memory_limit` | 621,768 | RW |
| `fq_limit` | 621,790 | RW |
| `fq_quantum` | 621,805 | RW |

`fq_flows_cnt` being read-only is consistent with it being a constructor
argument rather than a tunable, which is what the store analysis then found.

## The mandated adjacency probe returned nothing

Adaptive window search, **4,096 bytes per side** of each knob-name occurrence,
every candidate integer in little- and big-endian, 2-byte and 4-byte encodings:
**zero hits** for 512, 3,145,728 and 4,096, across all five name occurrences.

The reason is structural, not accidental. Every knob name sits in
`.rodata.str1.4` (600,656 to 635,880), a string-only section with flags `0x32` =
`SHF_ALLOC | SHF_MERGE | SHF_STRINGS`. Each window is therefore 8.2 KB of pure
string bytes. There is also **no** `.rel.rodata.str1.4` relocation section, so
no pointer or relocation can bind a value to these names anywhere in the module.

The zero is reported as `UNKNOWN` for adjacency. Whole-file census shows why a
proximity hit would have been weak even if one had appeared: 512 occurs 808
times file-wide as LE32, 4,096 occurs 1,548 times, 3,145,728 occurs 21 times.
A single neighbour would have been noise.

A concrete warning from the same function: the value 512 **does** appear at file
offset 274,284 inside `ieee80211_txq_setup_flows`, as
`addiu $a1, $zero, 0x200`, the `SOFTIRQ_DISABLE_OFFSET` argument of a
`local_bh_enable`. Proximity within the same function would have "confirmed"
`fq_limit = 512` and been completely wrong.

## How the defaults were actually measured

`fq_init` is inline, so its body is compiled into `ieee80211_txq_setup_flows`
(symbol at `.text` offset 273,584, size 608 bytes, file offset 273,696). The
function was decoded instruction by instruction and every literal load was
paired with the store that consumes it.

The fq base is derived, not assumed: `memset(&local->fq, 0, sizeof)` is emitted
as `addiu $s1, $a0, 0xa0` at file 273,708 feeding the `memset` call at 273,732,
so `&local->fq = local + 0xa0` and `sizeof(struct fq) = 0x34 = 52`.

| Field | fq-relative | Value | Immediate at | Store at |
| :--- | ---: | ---: | ---: | ---: |
| `fq_flows_cnt` | 0x10 | 4096 | 273,764 | 273,776 |
| `fq_limit` | 0x14 | 8192 | 273,760 | 273,768 |
| `fq_memory_limit` | 0x18 | 16777216 | 273,772 | 273,780 |
| `fq_quantum` | 0x20 | 300 | 273,752 | 273,756 |

Surrounding call sites resolved through `.rel.text` confirm the identification:
`memset`, `kvmalloc_node`, `bitmap_zalloc`, `kvmalloc_node`, then
`ieee80211_txq_set_params`, then `kvfree`, `kvfree`, `bitmap_free`.

Field order is cross-checked independently by `ieee80211_txq_set_params`, which
copies three tunables from the hw struct into the same three consecutive fields
(hw +0x234 into +0xb4, +0x238 into +0xb8, +0x23c into +0xc0) and copies them
back on the read path. Because the two candidate fields hold two different
values, 8192 and 16777216, the live readout recorded in Stage 955A distinguishes
them without ambiguity. Three consistent sources, so `CONFIRMED`.

## The Stage 955A attribution, audited

`artifacts/autoresearch/stage955a_live_panel1_three_cpe_readonly_audit.json`
(54,908 bytes) declares stage `955A`, provenance
`CONFIRMED_LIVE_HARDWARE`, status
`READ_ONLY_AUDIT_WITH_PARTIAL_CAPTURES_RETAINED`, `target_configuration_writes`
false.

It does contain all three numbers. It contains them in **one** of five AQM
readout blocks.

| Block | `fq_limit` | `fq_memory_limit` | `fq_flows_cnt` | `fq_quantum` |
| :--- | ---: | ---: | ---: | ---: |
| `/ap/snapshots[0]` | 512 | 3145728 | 4096 | absent, capture truncated |
| CPE snapshot 0, phy0 | 8192 | 16777216 | 4096 | 300 |
| CPE snapshot 0, phy1 | 8192 | 4194304 | 4096 | 300 |
| CPE snapshot 1, phy0 | 8192 | 16777216 | 4096 | 300 |
| CPE snapshot 1, phy1 | 8192 | 4194304 | 4096 | 300 |

The 512 and 3,145,728 values exist only on the access-point block, where they
are runtime AQM state captured at audit time. The four CPE blocks record 8192
and 16,777,216, which are exactly the compiled defaults measured here. The
Stage 955A access-point capture is also truncated mid-token after
`RW fq_quantum `, so its quantum value is unrecoverable from that receipt.

Containment is `CONFIRMED`. Attribution as a *default* is `REFUTED`.

## Claims

| Id | Label | Claim |
| :--- | :--- | :--- |
| C1 | REFUTED | `fq_init`, `fq_tin_dequeue`, `codel_should_drop` exist as strings or symbols |
| C2 | CONFIRMED | the fair queue is present as a feature with nine knobs and an initialiser |
| C3 | CONFIRMED | defaults are 8192 / 16777216 / 4096 / 300 |
| C4 | REFUTED | 512 / 3145728 / 4096 is the compiled default set |
| C5 | CONFIRMED | Stage 955A literally contains 512, 3145728 and 4096 in the AP block |
| C6 | UNKNOWN | adjacency can resolve these defaults |

## Gaps

- No live target execution. Every integer is static and labelled
  `CONFIRMED_STATIC_BINARY` only.
- The mapping of 0xb4 and 0xb8 to `fq_limit` and `fq_memory_limit` rests on two
  distinct live values plus the copy order in `ieee80211_txq_set_params`. A
  direct debugfs fops walk from name string to struct field was not performed.
- Origin of the runtime 512 and 3,145,728 on the access point is `UNKNOWN`. The
  receipt records values, not the writer, and no init-script capture exists
  offline.
- `fq_flows_cnt` is read-only in the surface, so no runtime write path exists to
  compare against.
- These defaults are asserted only for `backports-6.12.52` on `6.6.110`.

## Reproduction

```
python tools/re/dissect_stage1034a_mac80211_fq_defaults_re.py
```

Writes `artifacts/autoresearch/stage1034a_mac80211_fq_defaults_re.json`
(16,634 bytes, sha256 `ee4168726f397ab6...`). No wall-clock, no PID, sorted keys,
LF endings: two consecutive runs are byte-identical, verified across processes
and asserted by the script itself. Standard library only, no capstone.
