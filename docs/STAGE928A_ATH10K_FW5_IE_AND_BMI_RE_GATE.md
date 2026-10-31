<!-- doc-head: Stage 928A - the gate passes fifty-six of fifty-six checks with three cross-stage agreements and compliant set to one, asserting that three of the five stages are dominated by absent premises and that no stage claims to have read ath10k_core.ko, a ROM image or a firmware-5.bin -->
# Stage 928A — fail-closed gate over 923A..927A

- **Receipt**: [`artifacts/autoresearch/stage928a_ath10k_fw5_ie_and_bmi_re_gate.json`](../artifacts/autoresearch/stage928a_ath10k_fw5_ie_and_bmi_re_gate.json)
- **Tool**: [`tools/verify/verify_stage928a_ath10k_fw5_ie_and_bmi_re_gate.py`](../tools/verify/verify_stage928a_ath10k_fw5_ie_and_bmi_re_gate.py)
- **Scope**: offline static verification. Reads five JSON receipts only.

## 0. Result

```
[928A] stages=5/5 checks=56/56 cross=3 failures=0 compliant=1
```

| Metric | Value |
| :--- | :-: |
| stages present | **5 / 5** |
| checks run | **56** |
| checks passed | **56** |
| cross-stage checks | **3** |
| failures | **0** |
| `compliant` | **1** |

## 1. What the gate asserts per stage

| Stage | Asserted |
| :--- | :--- |
| **923A** | core absent, firmware-5 absent, one container, two segments, first SGMT at 108, TLV region 94, no TLV chain, validator not claimed |
| **924A** | 140 segments, zero decode errors, 140 exact lengths, 140 round-trips, **no ROM image**, window above 64 KiB |
| **925A** | `QCA-ATH10K-FW` absent, observed magic present, no TLV table in source, rebuild parses, exact EOF, tags unconfirmed |
| **926A** | 50 dumps, 10 unique, both blocks everywhere, header invariant **refuted**, no `.20`, no `board.bin` |
| **927A** | both sides present, partition mismatch, 6 and 4 differing bytes, both blocks present |

Every stage also asserts `evidence_provenance_class = CONFIRMED_STATIC_BINARY`, `static only` radio
safety and at least one declared gap.

## 2. The three cross-stage checks

**`header_size_agrees`** — 923A and 925A both measure the header, from **different origins**: 923A's TLV
region starts after the four-byte field at offset 10, giving **94** bytes, while 925A measures from the
end of the magic, giving **98**. The check derives both from the container rather than comparing two
constants, and requires `98` and `94` to hold together with a first `SGMT` at offset **108**.

This was a real defect the gate caught: my first version compared 94 against 98 and failed.

**`window_assumption_refuted`** — 924A must report a maximum back-reference **above 65,536** while its
decode error count is **zero**. That combination is what proves the 64 KiB assumption was mine and not
the format's: with the limit enforced there were 7 errors, and with it removed there are none.

**`caldata_blocks_agree`** — 926A's `with_both_blocks` must equal its `dumps_found` (50 of 50) and
927A's `both_blocks_present` must be 1. Two different tools, two different file sets, same structural
conclusion.

## 3. What the gate cannot do

**`REFUTED`**: it cannot prove any of the five stages read what its title names.

Three of the five are dominated by **absent premises** — no `ath10k_core.ko`, no `firmware-5.bin`, no ROM
image — and the gate asserts the **absences**, not a discovery. A green gate here means "the refusals are
consistent and nothing was over-claimed", which is exactly the property worth gating in a batch like
this.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| all five receipts are present and declare static scope | **CONFIRMED** |
| `ath10k_core.ko` and `firmware-5.bin` are absent | **CONFIRMED** (asserted as zero) |
| no ROM image exists | **CONFIRMED** (asserted as zero) |
| our segments conform to the BCL grammar | **CONFIRMED** (140 of 140) |
| the required decode window exceeds 64 KiB | **CONFIRMED** (99,973 bytes) |
| the rebuilt IE container parses to exact EOF | **CONFIRMED** |
| IE tag values are confirmed by a binary | **REFUTED** (asserted as zero) |
| the `.20` caldata exists | **REFUTED** (asserted as zero) |
| the gate proves binary truth | **REFUTED** |

## 5. The operational reading

1. **A compliant gate on a batch of absences is still useful**, because it locks the wording: nobody can
   later cite 923A as an ath10k analysis or 924A as a ROM dump.
2. **The two real discoveries are 924A's 99,973-byte window and 925A's build string.** Both are
   measurements of files that exist, not readings of files that do not.
3. **The gate is a floor.** Passing it means no over-claim was made, not that any artefact works.

## 6. Gaps

- **`UNKNOWN`** — whether the absent binaries exist anywhere outside this corpus.
- **`UNKNOWN`** — whether the IE tag contract matches the real numbering.
- **Blocked** — implementation-level equivalence for BMI and the loader.
- **Known limit** — self-consistency across five receipts is necessary and not sufficient.
- **Not attempted** — any acquisition, any dynamic validation.
