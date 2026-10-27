<!-- doc-head: STAGE823A_AIROS_UBNT_POLL_AIRMAGIC_SPECTRAL_CHANNEL_SCORING_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 823A — airMagic spectral-efficiency channel scoring

- **Receipt**: [`artifacts/autoresearch/stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re.json`](../artifacts/autoresearch/stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re.json)
- **Tool**: [`tools/re/dissect_stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re.py`](../tools/re/dissect_stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, **no channel changed**.

## 0. airMagic is a product name, not a symbol

| Token | `ubnt_poll_host.ko` |
| :--- | :-: |
| `airmagic`, `airMagic`, `AIRMAGIC` | **0** |
| `efficien` | **0** |
| `score` | **0** |
| `magic` | **1** |

**`REFUTED`**: the airMagic scoring is **not a kernel function**. `ubnt_poll_host.ko` carries one
`magic` hit and no efficiency vocabulary at all.

The mechanism is in the **userspace daemon `ubntspecd`** — **47,192 bytes**, a real binary, not one
of this corpus's zero-byte stubs.

## 1. The scoring interface is printed tier by tier

`ubntspecd` emits, per candidate channel:

```
Find best channel for BW %d:
Checking %d : . %d [%d] BPS=%d SCORE=%d RATING=%d
*** BEST : %d BPS=%d SCORE=%d RATING=%d*
```

**`CONFIRMED`**: `scoring_tier_count = 3` — **BPS**, **SCORE**, **RATING** — and the selection runs
**per bandwidth** (`per_bandwidth_selection = 2` hits of `Find best channel for BW`).

That three-tier structure is the formula's **shape**:

| Tier | Must be |
| :--- | :--- |
| **BPS** | the raw throughput estimate for the candidate |
| **SCORE** | BPS after weighting by interference and the CPE histograms |
| **RATING** | the rank used to choose `*** BEST` |

Three named tiers is stronger than a single opaque "score": it tells you the vendor separates the
**raw estimate** from the **weighted figure** from the **ordering**.

## 2. What the formula consumes

```
Airmagic channels (total %d):     BW : %d |     %d : MIN LT=%d MAX LT=%d CONTROL : [
Number of channels exceeds AMG_MAX_CHANS        Number of channels exceeds AMG_NUM_CONTROL
c = %d MHZ=%u CHZ=%u CNTR=%d EDGE [Min = %d Max = %d] VALID [Min=%d Max=%d] MODE %d
Freq = %u Hz start_tone=%u tones_per_chan=%u
```

**`CONFIRMED`**: `capacity_guards = [AMG_MAX_CHANS, AMG_NUM_CONTROL]` — **two** limits, so airMagic
caps the channel list and the control list separately.

**`CONFIRMED`**: each channel carries **`MIN LT` and `MAX LT`** limits, plus `CHZ` (channel width?),
`CNTR` (centre), and `EDGE [Min, Max]` — centre and edges as **independent fields**, which is what a
5 MHz sub-portion of a 20/40/80 MHz channel requires.

**`CONFIRMED`**: `tone_to_freq_mapping = 1`. `Freq = %u Hz  start_tone=%u  tones_per_chan=%u` gives
the **tone→frequency mapping**. This is the missing link the spectral stages could never close
(327A, 451A, 727A all failed to decode the FFT bin format): a channel's power is a **sum over a known
tone range**, not over an opaque bin array.

## 3. What the formula's arithmetic is not

**`REFUTED`**: `bps_per_hz_expression_recovered = 0`, `formula_coefficients_recovered = 0`.

There is no `efficien`, no `score =`, no `BPS/Hz` expression, and no weight constant anywhere in the
daemon's strings. The **tiers** are named; the **transformation between them** is code, not text.

**This is the honest limit of the stage.** The stage asked for "the exact formula" for Guarida's
autonomous selector. What is available is the **interface**: three ordered tiers, per bandwidth, over
a candidate list bounded by two caps, each channel described by centre/edges/validity, fed by a known
tone→frequency map.

That is enough to **reproduce the pipeline's shape** and not enough to **reproduce its numbers**.

## 4. The CPE-histogram combination is not located

**`REFUTED`**: no `histogram` aggregation over associated CPEs appears by name. The daemon does
receive a **STA list** (`Receiving STA list: FAILURE` is a real error string) and does report
per-channel limits, so the plumbing exists — but the **combination rule** across CPEs was not
recovered.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| airMagic exists as a kernel symbol | **REFUTED** (0 hits) |
| the mechanism lives in `ubntspecd` | **CONFIRMED** (47,192-byte binary) |
| scoring is per-channel and per-bandwidth | **CONFIRMED** |
| the output has three tiers BPS / SCORE / RATING | **CONFIRMED** |
| two capacity guards bound the candidate set | **CONFIRMED** |
| each channel has independent centre and edge fields | **CONFIRMED** |
| a tone→frequency mapping exists (`tones_per_chan`) | **CONFIRMED** |
| the arithmetic between the tiers | **UNKNOWN / code, not text** |
| the bps/Hz expression | **REFUTED** (no such string) |
| the CPE-histogram combination rule | **UNKNOWN / not recovered** |

## 6. What Guarida's selector can and cannot take from this

**Can take:** the pipeline shape (raw estimate → weighted score → ranking, per bandwidth), the two
caps, and the tone→frequency map that turns spectral samples into a per-channel power figure.

**Cannot take:** the weights. Any selector built from this must **choose its own** BPS→SCORE
weighting, and must say so — presenting a computed weight as "airMagic's formula" would be a
fabrication.

## 7. Gaps

- **`UNKNOWN`** — how BPS is computed from the interference histogram.
- **`UNKNOWN`** — how SCORE weights BPS, and whether CPE count enters.
- **`UNKNOWN`** — how RATING orders candidates, and whether hysteresis applies.
- **`UNKNOWN`** — the numeric values behind `MIN LT` / `MAX LT` / `VALID`.
- **`UNKNOWN`** — whether the 5 MHz portioning is a constant or derived from `tones_per_chan`.
- **Known limit** — three named tiers are not a formula.
- **Not attempted** — dynamic validation, live scan capture.
