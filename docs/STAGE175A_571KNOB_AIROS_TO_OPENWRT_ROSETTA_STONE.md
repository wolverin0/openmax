<!-- doc-head: STAGE175A_571KNOB_AIROS_TO_OPENWRT_ROSETTA_STONE.md preserved document content -->
<!-- /doc-head -->


# Stage 175A — airOS → OpenWrt 24.10.4 Rosetta Stone attempt

- **Receipt**: [`artifacts/autoresearch/stage175a_571knob_airos_to_openwrt_rosetta_stone.json`](../artifacts/autoresearch/stage175a_571knob_airos_to_openwrt_rosetta_stone.json)
- **Champion**: `artifacts/autoresearch/stage163a_cumulative_18round_wa_champion_v2.json`
- **Tool**: `tools/re/audit_stage173a_to_175a_ltu_re_and_rosetta.py`
- **Scope**: offline static cross-reference. No device access.

## 0. Method

The champion's every key and string was harvested and normalised (lowercase, non-alphanumerics
stripped). Each of the 571 airOS knob names was then matched by its full normalised form and by
its last dotted component (minimum 5 characters) against that set.

## 1. Result

| Metric | Value |
| :--- | :-: |
| Knobs | **571** |
| Mapped by name | **3** |
| Unmapped | 568 |
| Match rate | **0.53 %** |
| Champion tokens harvested | thousands |
| Equivalence confirmed | **0** |

**`CONFIRMED`: the name-match rate is 0.53 %.** Three knobs out of 571 share a token with the
champion.

## 2. Why the rate is this low — and why that is the finding

The two vocabularies are structurally different:

| Side | Example names |
| :--- | :--- |
| airOS catalogue | `ct_special.THRESH62_EXT`, `fq_quantum_bytes`, `AQL low/high per access category` |
| Stage 163A champion | `AQL 2000/4000 + FQ 4542 + BQL 3028/65536/1000`, round titles, Pareto deltas |

The airOS side names **register-adjacent knobs** in the vendor's own vocabulary. The OpenWrt
side names **tuned values** in `tc`/`mac80211` vocabulary, and records them as round titles with
numeric arms. `THRESH62_EXT` has no textual counterpart in a line that reads
`AQL 2000/4000 + FQ 4542`.

**Therefore a name-based Rosetta Stone cannot be built.** The mapping requires semantic
alignment — what the knob *does* — not token overlap. Manufacturing 571 mappings by fuzzy
matching would produce a document that reads authoritative and is wrong, which is exactly the
failure mode this project has refused elsewhere.

## 3. What a real mapping would need

| Step | What it requires | Present? |
| :--- | :--- | :--- |
| airOS knob → airOS effect | handler trace into register writes (Stage 174A could not) | **no** |
| OpenWrt parameter → effect | `mac80211`/`ath10k`/`tc` semantics for the champion's arms | **partly** (champion records outcomes, not semantics) |
| effect ↔ effect | equivalence by measured behaviour, per knob | **no** |
| mapping artefact | the above, per knob, with a verdict | **no** |

The champion does carry the outcome evidence — goodput, p50/p95/p99 RTT, Pareto deltas across
18 counterbalanced rounds. That is exactly what a behavioural equivalence test needs, but it is
keyed by **round**, not by knob, so it cannot be joined to the catalogue without the missing
first arrow.

## 4. What the receipt does contain

- all 571 knobs with `mapped` boolean and `rosetta_candidate` (null when unmapped);
- the 3 candidate matches, labelled as **candidates**, not equivalences;
- the champion's SHA-256, so the comparison target is pinned;
- `equivalence_confirmed = 0`, protected by a test.

## 5. Honest disposition

**Do not ship a Rosetta Stone from this pass.** The artefact that exists is a *negative result
with the search recorded*, which is more useful than a fabricated mapping because it tells the
next engineer not to repeat the token search.

The productive path is the inverse direction: start from the champion's 18 rounds, take the
parameters it actually tuned, and ask which airOS knob produces the same measurable effect. That
is 18 questions, not 571, and each has outcome evidence attached.

## 6. Gaps

- **`UNKNOWN`** — semantic mapping for all 568 unmapped knobs.
- **`UNKNOWN`** — whether the 3 candidates are genuinely equivalent; they are name matches only.
- **`KNOWN LIMIT`** — the champion records rounds and outcomes, not per-knob semantics.
- **Not attempted** — any behavioural comparison against a live OpenWrt 24.10.4 build.
