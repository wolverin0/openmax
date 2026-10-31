<!-- doc-head: Stage 1035A - measured mac80211 fair-queue defaults against classic Linux fq_codel defaults; states the implementation boundary and forbids numeric contamination -->
<!-- /doc-head -->
# Stage 1035A - mac80211 Fair Queue versus Classic fq_codel

Companion to Stage 1034A. The measured side is consumed from that stage's
receipt and admitted only where a store-level measurement was recorded. The
classic side is an external reference to the Linux `sch_fq_codel` module
defaults and is never read out of the analysed binary.

## Verdict

mac80211's fair queue in this build is a **different implementation with
different defaults**. It is not fq_codel, and it is not fq_codel with tuned
constants. All five shared parameters diverge.

| Parameter | Unit | mac80211 (measured) | classic fq_codel (reference) | classic / mac80211 |
| :--- | :--- | ---: | ---: | ---: |
| `fq_limit` | packets | 8192 | 10240 | 1.25 |
| `fq_flows_cnt` | flows | 4096 | 1024 | 0.25 |
| `fq_quantum` | bytes | 300 | 1514 | 5.046667 |
| `codel_target_us` | microseconds | absent | 5000 | n/a |
| `codel_interval_us` | microseconds | absent | 100000 | n/a |

`divergence_count = 5` over 5 shared parameters. Two further parameters are
asymmetric and are reported separately so they cannot inflate the count:

| Parameter | Side | Value | Note |
| :--- | :--- | ---: | :--- |
| `fq_memory_limit` | mac80211 only | 16777216 bytes | byte-budget cap with no fq_codel counterpart |
| `ecn_toggle` | classic only | present | the ECN marking half that mac80211 does not implement |

## There is no codel component at all

This is not an inference from defaults. The module was searched for the tokens
such a component would necessarily carry.

| Token | Occurrences in 829,464 bytes |
| :--- | ---: |
| `codel` | 0 |
| `CODEL` | 0 |
| `ecn` | 0 |
| `ECN` | 0 |
| `interval` | 0 |
| `target` | 0 |
| `codel_should_drop` | 0 |

No symbol in `.symtab` contains `codel` either, out of 1,974 symbols scanned.
A fair queue with no drop controller, no target, no interval and no ECN is a
plain byte-limit fair queue. Calling it fq_codel is a category error.

## The classic constants are not bound to anything here

Presence of an integer somewhere in a 829 KB object file means very little, so
each classic constant was censused and then checked against the four fq store
sites measured in Stage 1034A.

| Constant | Total hits | 4-byte hits | Matches a measured fq default |
| :--- | ---: | ---: | :--- |
| 10240 | 2899 | 43 | no |
| 1024 | 17004 | 288 | no |
| 1514 | 9 | 0 | no |
| 5000 | 12 | 1 | no |
| 100000 | 0 | 0 | no |

1514 has no 32-bit occurrence at all: all nine hits are 16-bit coincidences
inside relocation entries. 100000 has no occurrence in any encoding. The
initialiser stores exactly 4096, 8192, 16777216 and 300 into the four fq
fields, so none of the classic values reaches an fq control field. Runtime
writes go through `ieee80211_txq_set_params`, which copies from hw struct
fields rather than literals.

## The absent-name trap

`fq_init` and `fq_tin_dequeue` do not exist as names in this module. Reporting
that as "the fair queue is absent" would be wrong: the code is header-inline and
compiled into `ieee80211_txq_setup_flows`, where a `memset` of 52 bytes, two
`kvmalloc_node` calls, a `bitmap_zalloc` and four literal stores constitute the
initialiser. `fq_inline_confirmed` is therefore true.

Absence of a symbol is evidence about linking, not about features.

## Boundary

Permitted: comparing the two implementations as algorithmic families, and
explaining why a 300 byte quantum against a 8192 packet limit produces a
different drop profile from fq_codel.

Forbidden:

- quoting 10240, 1024, 1514, 5 ms or 100 ms as mac80211 fair-queue defaults;
- describing this build as fq_codel, or as fq_codel with tuned constants;
- carrying a live `sch_fq_codel` qdisc reading into a mac80211 `fq` claim;
- assuming tuning advice written for fq_codel transfers unchanged to these knobs.

The third item is the one that has bitten this project before, because both
subsystems expose a knob family and the numbers look interchangeable.

## Claims

| Id | Label | Claim |
| :--- | :--- | :--- |
| D1 | CONFIRMED | defaults are 8192 / 16777216 / 4096 / 300 |
| D2 | CONFIRMED | no codel component exists in this module |
| D3 | CONFIRMED | all five shared parameters diverge |
| D4 | CONFIRMED | the fair queue is inline code, absent by name only |
| D5 | CONFIRMED | classic constants present in the module are bound to no fq field |

## Gaps

- No live target execution. The comparison says nothing about measured drop
  behaviour on hardware.
- The classic column was not verified against the target's own `sch_fq_codel`
  build, which was not in the analysed artefact set. It is an external
  reference and is labelled as one.
- Quantum is compared in bytes on both sides, but mac80211's quantum interacts
  with airtime and aggregation accounting, so equal units do not imply
  comparable scheduling.
- Whether userspace rewrites these knobs at runtime is `UNKNOWN`; one such
  runtime deviation was observed in Stage 955A with unrecorded origin.
- No claim is made for backports versions other than 6.12.52 on kernel 6.6.110.

## Reproduction

```
python tools/re/dissect_stage1035a_fq_vs_codel_defaults_comparison_re.py
```

Requires the Stage 1034A receipt and exits non-zero without it rather than
emitting a comparison with an empty measured side. Writes
`artifacts/autoresearch/stage1035a_fq_vs_codel_defaults_comparison_re.json`
(12,867 bytes, sha256 `039a315002e3db4c...`), sorted keys, LF endings, no
wall-clock: two consecutive runs byte-identical, verified across processes.
