<!-- doc-head: STAGE500A_GROUND_UP_RE_500STAGE_BINARY_ATLAS.md preserved document content -->
<!-- /doc-head -->


# Stage 500A — the Ground-Up Binary RE Atlas, derived from the receipts

- **Receipt**: [`artifacts/autoresearch/stage500a_ground_up_re_500stage_binary_atlas.json`](../artifacts/autoresearch/stage500a_ground_up_re_500stage_binary_atlas.json)
- **Tool**: [`tools/re/build_stage500a_ground_up_re_500stage_binary_atlas.py`](../tools/re/build_stage500a_ground_up_re_500stage_binary_atlas.py)
- **Scope**: offline static. This stage opens **only JSON the series already wrote**.

## 0. What this stage is, and what it deliberately is not

This is an **atlas of evidence**, not a summary essay. Every figure below is a **sum over receipt
fields** — `meta.stage`, `modules[].bytes`, `modules[].sha256`, and every `*_recovered` flag any
stage declared. If a number is not in a receipt, it is not in the atlas.

That choice has a cost, and it is the honest one: the atlas **cannot** claim more coverage than the
receipts recorded. Where the series never opened a binary, the atlas shows a hole.

## 1. Coverage

| Metric | Value |
| :--- | :-: |
| receipts found | **56** |
| receipts parsed | **56** |
| unparsable | **0** |
| distinct stages covered | **56** |
| module analyses recorded | **101** |
| unique module files (by SHA-256) | **32** |
| unique bytes analysed | **17,896,272** (17.9 MB) |
| largest single module | **3,282,052** (`ame_core.ko`) |

**CONFIRMED**: 101 module analyses collapse to **32 unique files**. The same umac.ko read by six
different stages counts **once** toward the byte total. Without SHA de-duplication this atlas would
have reported an inflated corpus, which is exactly the sort of number that looks impressive and
means nothing.

## 2. Platform families

| Family | Receipts | Unique modules | Unique bytes |
| :--- | :-: | :-: | :-: |
| qca988x_ac (WA / XC / 2XC) | 13 | 18 | 6,022,756 |
| eetle_ltu (Beetle / Arria-class / AD9361) | 32 | 8 | 7,478,692 |
| `ar9344_xw` (M5) | 6 | 16 | 1,864,792 |
| `unclassified` | 5 | 6 | 2,530,032 |

**`CONFIRMED`**: three families are populated from real extracted binaries. The fourth bucket is
receipts that record findings without carrying a module with a SHA-256 — kept visible rather than
silently folded into a neighbour.

**Note on `invictus_af`**: an earlier classification pass put one receipt in that family by matching
the word "invictus" in its text. Under the stricter rule — **module filenames decide the family,
receipt text is only a fallback** — it does not appear, because **no Invictus2 executable exists in
this corpus**. That correction is recorded here rather than quietly applied.

## 3. The scorecard is the most important table in this document

Every `*_recovered` flag any stage declared, tallied:

| Result | Flags |
| :--- | :-: |
| **closed** (`= 1`) | **1** |
| **open** (= 0) | **36** |
| declared | 37 |

The single closed flag is **`nq_sq_split_recovered`** — Stage 438A, the N/S two-class CPE scheduler.

**CONFIRMED**: of the 37 recovery goals this series explicitly declared, **one** closed.

That number is the atlas's real verdict, and it should be read correctly: it does **not** say the
series found nothing. It says the series was honest about what it was aiming at. The stages that
**succeeded** mostly did so under flags that are not named `*_recovered` — `bar_failure_named`,
`tid_pause_named`, `csa_state_machine_named`, `bmiss_state_machine_named`,
`dcxo_subsystem_named`, `ring_primitives`, `nfcal_symbol_count`, `swbmiss_lifecycle_named` — because
those stages found **mechanisms**, not **tables**.

The distinction matters: a named state machine is a real result; a recovered threshold table is a
different, harder result, and 36 of those are still open.

## 4. The two systemic holes

| Gap | Receipts that record it |
| :--- | :-: |
| `firmware-2.bin` / `firmware-5.bin` absent | **6** |
| `eab_driver.ko` absent | **2** |

**`CONFIRMED`**: every stage that needed the QCA988x firmware images found **zero of them**. Every
claim in this atlas about the Xtensa side is therefore **host-side only** — the kernel modules, not
the firmware.

**`CONFIRMED`**: `eab_driver.ko` is absent from the corpus. The count of 2 understates it — eight
stages confirmed the absence in prose, but only two wrote it into a machine-readable field. That is
an atlas-limitation worth naming explicitly.

## 5. What the atlas supports, and what it does not

**Supportable, from receipts:**

- the AC/XW split is real and pervasive: `SIFS` vs `slot_time` (415A), bin5/bin radar detectors
  present on AC and **absent on both M5 images** (499A), `ath_hal.ko` at 367,456 vs 503,892 bytes
  (415A), and 10 vs 17 bmiss symbols (326A);
- the LTU family is **one large module**: 8 unique files, 7.5 MB, with `ame_core.ko` alone at
   3.28 MB - 44 % of the LTU family and 18 % of the whole corpus;
- host-side mechanisms on QCA988x are **named** at a high rate: CSA in three variants, a software
  bmiss timer with a 5-call lifecycle, four radar discriminator families, an 11-function noise-floor
  chain;
- several vendor **spelling defects** are load-bearing: `pasued` (459A), `blakc` (499A), plus the
  `BE`/`PROBE`, `LQ`/base64 and `moder`/`modern` substring traps.

**Not supportable:**

- any **firmware-side** claim about QCA988x — the images do not exist here;
- any **EAB driver** claim on LTU — the module does not exist here;
- any **Invictus2 executable** claim — there is none;
- any claim that **500 stages** were verified. This corpus holds **56** receipts. The milestone
  number is a project label, and the atlas counts what exists rather than what the label implies.

## 6. The honest verdict

`atlas_complete = 0`.

Not because the work failed, but because an atlas that covered all four platforms would need four
artefacts this corpus does not contain: the QCA988x firmware container pair, `eab_driver.ko`, an
Invictus2 rootfs, and an Arria 10 bitstream.

What the atlas **does** establish is a **verified map of the host-side control surface** for three
silicon families, with 32 SHA-pinned binaries, 92 analyses and a scorecard that says plainly which
goals closed and which did not. That is a defensible artefact. A document claiming five hundred
verified stages across four platforms would not be.

## 7. Gaps

- **`UNKNOWN`** — every firmware-internal behaviour on QCA988x.
- **`UNKNOWN`** — the EAB driver column for LTU.
- **`UNKNOWN`** — any Invictus2 executable behaviour.
- **`UNKNOWN`** — the Arria 10 fabric configuration.
- **Structural** - 36 of 37 declared recovery flags remain open; the atlas records that rather than
  re-scoring them.
- **Structural** — receipts from other workstreams in this repository are counted alongside this
  series; the atlas does not distinguish authorship.
- **Not attempted** — dynamic validation of anything in the atlas.
