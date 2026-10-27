<!-- doc-head: STAGE198A_18EFFECT_EMPIRICAL_ROSETTA_STONE.md preserved document content -->
<!-- /doc-head -->


# Stage 198A — the 18-effect empirical Rosetta Stone

- **Receipt**: [`artifacts/autoresearch/stage198a_18effect_empirical_rosetta_stone.json`](../artifacts/autoresearch/stage198a_18effect_empirical_rosetta_stone.json)
- **Champion**: `artifacts/autoresearch/stage163a_cumulative_18round_wa_champion_v2.json`
- **Tool**: `tools/re/audit_stage197a_to_199a_hal_and_xw_delta.py`
- **Scope**: offline static cross-reference. No device access.

## 0. Why this is the right shape

Stage 175A established that a name-based Rosetta Stone over 571 knobs fails: 3 of 571 matched
(0.53 %), because airOS names register-adjacent knobs and the OpenWrt champion names tuned
values. The productive inverse is **18 questions** — one per champion round — each with measured
outcome evidence already attached.

This stage runs that inversion.

## 1. Method

For each of the 18 rounds in `rounds_r1_to_r18_ledger`:

1. tokenise the round title (`[a-z0-9]{4,}`);
2. tokenise each catalogue knob name the same way;
3. a knob is a **candidate** when its token set overlaps the round's tokens by at least
   `min(2, |knob tokens|)`;
4. record the round's own outcome metrics (arm B goodput, arm B p95, Pareto delta) alongside.

## 2. Result

| Metric | Value |
| :--- | :-: |
| Rounds | **18** |
| Rounds with at least one candidate | **12** |
| Rounds with no candidate | **6** |
| Total candidate pairs | **16** |
| Equivalences confirmed | **0** |

**`CONFIRMED`**: 12 of 18 rounds produce at least one candidate airOS knob. **Six produce
none.**

## 3. The six empty rounds are the interesting ones

A round with no token overlap is one whose title describes an intervention in vocabulary the
catalogue does not use. Those are the rounds where a name-based join is structurally impossible,
and where a behavioural join is the only option — the champion has the measured outcome, the
catalogue has the knob, and nothing textual connects them.

Reporting them as empty is more useful than forcing a match: it says exactly which six questions
need a bench answer rather than a grep.

## 4. Why zero equivalences are confirmed

The champion records **per-round** outcomes, not per-knob effects. A round may tune four
parameters at once:

```
AQL 2000/4000 + FQ 4542 + BQL 3028/65536/1000 vs 9
```

Even a perfect name join to a catalogue knob would not establish that *that knob* produced the
measured goodput delta — the delta belongs to the **combination**. Isolating a per-knob effect
requires one round per knob, which the champion does not provide.

So the candidate sets are a question list, not an answer key.

## 5. What the receipt contains

- all 18 rounds with `round_id`, `title`, `decision`, arm B goodput and p95, Pareto delta;
- the token overlap used for each round, so the match is auditable;
- the candidate knob list per round (max 12), with `candidate_count`;
- `equivalence_confirmed = 0`, protected by a test.

## 6. Disposition

**Do not publish this as a mapping.** It is a prioritised question list: 12 rounds with a
starting hypothesis and 6 rounds with nothing. The next step is a bench run per round, not more
scanning.

Ranking for that bench work: the rounds with the largest `pareto_score_delta_pct` and a single
candidate knob are the cheapest to isolate; the six empty rounds need the effect described
first, before any knob can be named.

## 7. Gaps

- **`UNKNOWN`** — which specific knob caused each round's delta. Not isolable from the champion.
- **`UNKNOWN`** — the six rounds with no textual candidate.
- **`KNOWN LIMIT`** — the champion's rounds are multi-parameter by design (counterbalanced
  arms), so per-knob attribution is out of reach without new measurements.
- **Not attempted** — any live OpenWrt 24.10.4 or airOS measurement.
