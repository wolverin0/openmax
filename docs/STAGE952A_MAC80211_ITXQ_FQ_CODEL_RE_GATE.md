<!-- doc-head: Stage 952A - offline gate over 947A..951A that asserts the eight-symbol mac80211 iTXQ API, the header-inline fair queue, the absent ath10k module, mac80211 ownership of AQL, the ubnt_poll_host TDMA slot model and eleven divergences, with three named cross-stage checks, eighty-seven passing checks and compliant set to one -->
# Stage 952A — gate over 947A..951A

- **Receipt**: [`artifacts/autoresearch/stage952a_mac80211_itxq_fq_codel_re_gate.json`](../artifacts/autoresearch/stage952a_mac80211_itxq_fq_codel_re_gate.json)
- **Tool**: [`tools/verify/verify_stage952a_mac80211_itxq_fq_codel_re_gate.py`](../tools/verify/verify_stage952a_mac80211_itxq_fq_codel_re_gate.py)
- **Scope**: offline static verification. Reads five JSON receipts and six markdown docs. No module is
  loaded, no radio is contacted, nothing is written to a device.

## 0. Result

```
[952A] stages=5/5 docs=5/5 checks=87/87 cross=3 failures=0 compliant=1
```

| Metric | Value |
| :--- | :-: |
| stages expected / present | **5 / 5** |
| upstream docs found | **5 / 5** |
| checks run | **87** |
| checks passed | **87** |
| cross-stage checks | **3** |
| failures | **0** |
| `compliant` | **1** |

`compliant` is the emptiness of a named `failures` list. A receipt that drifted by one field fails the
gate and produces a printed line, rather than degrading the report quietly.

## 1. What each stage has to prove

| Stage | Asserted |
| :--- | :--- |
| **947A** | 1,012 module symbols; 8 of 8 iTXQ symbols; four presence flags at 1; `fq_tin_dequeue` absent; zero FQ symbols; zero `codel` strings; `fq_prefix_hits` above zero; internal FQ confirmed; independent of `tc` |
| **948A** | zero ath10k modules over 1,163 scanned `.ko` files; 8 of 8 contract symbols; zero driver symbols; push path not recovered; mac80211 side documented |
| **949A** | at least three layers; at least one measured; AQL owned by mac80211; zero ath10k modules; boundary documented; interaction not recovered |
| **950A** | two modules compared and not identical; declared queue model; no fair queue, no codel, no deficit; mac80211 iTXQ present |
| **951A** | at least two layers; no equivalence claim; boundary documented; at least one divergence |

Every receipt additionally has to declare `meta.radio_safety` as `static only`, a `meta.scope`
containing the word `static`, a non-empty `gaps` array and a non-empty `evidence_provenance_class`.

## 2. The three cross-stage checks, by name

The gate emits exactly three checks with `stage` set to `cross`, plus one structural check that the
count and the names are what they claim to be. They are asserted by name in
`tests/test_stage947a_to_952a_suite.py`, so a rename fails rather than silently reducing coverage.

**`mac80211_itxq_agrees`** — 947A reports `itxq_symbols_present == 8`, counting the eight exported
iTXQ symbols in `mac80211.ko`; 950A reports `mac80211_itxq_present == 1`, the same stack expressed as a
presence flag over the two compared modules. The units differ, the referent does not: one is a symbol
census, the other a boolean that the census was found. The check detail carries that mapping, so the
receipt states the conversion instead of leaving two numbers to be compared by eye.

**`ath10k_absent_agrees`** — 948A's `ath10k_modules_found` and 949A's `ath10k_modules` are both **0**.
One stage swept every extracted module; the other rests on the layering table. Agreement here means the
synthesis did not invent a driver that the sweep could not find.

**`queue_models_differ`** — 950A reports `fair_queue_present == 0` and `codel_present == 0` for the two
`ubnt_poll_host.ko` images, while 947A reports `internal_fq_codel_confirmed == 1` for mac80211. The two
stacks therefore do not share a queue discipline: mac80211 carries an internal fair queue, and the
airOS module carries neither a fair queue nor codel, which is what makes the divergence count in 951A a
measurement rather than a stylistic difference.

## 3. The 950A documentation guard

950A is the only stage whose doc is checked for a specific over-claim. The airOS queue folklore names
`uph_Loaded` and `ath_TxQueue` as module symbols, and both are zero in both images. The gate reads the
doc and fails if it asserts either symbol exists while `uph_loaded_present` or `ath_txqueue_present`
is not 1.

The detector is claim-aware, not a substring search. A doc that names an absent symbol in order to
refute it must pass, otherwise the gate would punish the honest phrasing and reward silence. Lines
carrying a refutation cue — `REFUTED`, `absent`, `zero`, `not`, `0` — are not treated as claims.

## 4. The 949A recovery guard

`interaction_recovered` is asserted as **0**, because the driver half of the interaction is not in the
corpus. The flag is not decorative. While this gate was being written, the 949A receipt was regenerated
with `interaction_recovered = 1` at 08:48, computed by a formula whose first clause —
`measured + absent == len(layers)` — is a tautology, so the flag collapsed into `aql_owned and boundary`
and said nothing about the handoff.

The gate rejected it and printed `949A:interaction_not_recovered 1`, leaving `compliant` at 0. The
stage was then revised at 08:50 with the flag recomputed to **0**, and its doc now states that the
interaction was not recovered because the driver half is absent. The gate and the doc agree again.

That episode is the gate doing its only real job: refusing to certify a label that drifted from the
evidence, and naming the field when it happens.

## 5. What the gate cannot do

**`REFUTED`**: it cannot show that any queue ever ran.

Every invariant is a statement about two artefacts and a symbol table. The absent layers are absent
over this corpus, which is a bounded claim. The three cross-stage checks compare receipts to each
other, so a shared upstream error would propagate through all three and still pass.

The gate's value is narrower and real: it makes a silent downgrade fail. If `fq_tin_dequeue_present`
became 1, or `modules_identical` flipped to 1, or `equivalence_claimed` became 1, the batch would stop
being compliant on the next run, and the printed failure names the field.

## 6. Determinism

Both the verifier and the five upstream scripts write with no clock and no network, so a second run
reproduces the same bytes. `test_every_script_is_byte_deterministic` runs all six scripts twice and
compares the receipt bytes, which also catches a gate that embeds an absolute path or a timestamp.

## 7. What is established

| Claim | Status |
| :--- | :-: |
| mac80211 exports the eight-symbol iTXQ API | **CONFIRMED** (asserted 8 of 8) |
| the fair queue is header-inline and has no symbol | **CONFIRMED** (asserted as zero, with positive `fq_` strings) |
| the `tc` binary is independent of mac80211 | **CONFIRMED** (zero references) |
| no ath10k module exists in the corpus | **CONFIRMED** (asserted twice, by name) |
| mac80211 owns the AQL fields | **CONFIRMED** (asserted in 949A) |
| `ubnt_poll_host.ko` holds a TDMA slot model, not a fair queue | **CONFIRMED** (asserted in 950A) |
| the two stacks are not equivalent | **CONFIRMED** (asserted in 951A) |
| the gate proves binary truth | **REFUTED** |

## 8. Gaps

- **`UNKNOWN`** — whether the queue model label matches the mechanism; the gate checks the declared
  string, not the scheduler that the string describes.
- **`UNKNOWN`** — runtime behaviour of either stack: no module is loaded and no traffic is generated.
- **`UNKNOWN`** — whether an ath10k module exists outside the extracted corpus.
- **Known limit** — the queue-model vocabulary is declared inside the verifier, so a new label needs a
  one-line registration and is not accepted by accident.
- **Known limit** — the three cross-stage checks are consistency checks over receipts, not independent
  measurements.
- **Not attempted** — disassembly, any dynamic validation, any firmware write.
