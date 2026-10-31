<!-- doc-head: Stage 993A atlas of all 1169 .ko modules with measured identity-level provenance coverage; 129 confirmed (0.110351) against 1040 gaps enumerated in the receipt by path and attested here by digest; offline, no radio -->
# Stage 993A - `.ko` Module Atlas & Measured Provenance Coverage

- **Claim status**: `CONFIRMED_STATIC_BINARY` for the inventory and the
  measurement; `UNKNOWN` for how any module behaves on a radio.
- **Attribution**: `static binary corpus (offline)`. No device, controller or
  firmware attribution is made by this stage.
- **Scope**: read-only. No SSH, no radio, no module loaded, no firmware read or
  write, and no edit to `tools/qca988x/sgmt_container_inspector.py` or
  `firmware/xtensa_sgmt_surgical_patcher.py`.
- **Receipt**: `artifacts/autoresearch/stage993a_ko_modules_atlas_re.json`
- **Tool**: `tools/verify/verify_stage993a_ko_modules_atlas_re.py`

## 1. What was measured

Every file ending in `.ko` under `artifacts/` and `firmware/` was enumerated:
1169 modules, 96,706,820 bytes (92.23 MiB), of which 698 distinct sha256 values
means 471 files are byte-identical duplicates of another path. For each module
the atlas records the repository-relative path, the real byte length, the
sha256, the architecture read from the ELF `e_machine` header field, the kernel
version implied by its containing `/lib/modules/<version>/` tree (falling back
to the module's own `vermagic` token, with the source recorded per row), and
whether a provenanced receipt references it.

The provenance field used, here and in Stage 992A, is
`evidence_provenance_class`, accepted value `CONFIRMED_STATIC_BINARY`.

**Identity link rule.** A module counts only when the exact
repository-relative path or the exact sha256 of that module appears in the
string pool of a receipt carrying that provenance class. Basename matching is
explicitly rejected: one mention of a generic name such as `cfg80211.ko` would
otherwise mark every copy across a dozen firmware trees as covered, which is
exactly the false 100 percent this stage exists to prevent. Basename-only
matches are counted as a diagnostic and total 810 modules.

## 2. Measured versus missing

| Quantity | Measured | Missing | Total | Fraction |
| :--- | ---: | ---: | ---: | ---: |
| Modules with any receipt reference | 197 | 972 | 1169 | 0.16852 |
| Modules with provenanced reference | 129 | 1040 | 1169 | 0.110351 |
| Distinct binaries (sha256) covered | 87 | 611 | 698 | 0.12464 |
| MIPS modules covered | 92 | 749 | 841 | 0.10939 |
| ARM modules covered | 37 | 291 | 328 | 0.11280 |
| Modules in `firmware/` tree covered | 16 | 0 | 16 | 1.00000 |
| Modules in `artifacts/` tree covered | 113 | 1040 | 1153 | 0.09801 |

Arithmetic: `197 + 972 = 1169` and `129 + 1040 = 1169`. Coverage is
`129 / 1169 = 0.110351`, which is `11.04` percent. The first partition answers
"does any receipt mention this exact file", the second answers "does a receipt
with `CONFIRMED_STATIC_BINARY` provenance do so", and both are asserted inside
the verifier.

This coverage figure is measured, and it is not a guarantee of correctness. It
is 11.04 percent, not 100 percent, and the 1040 shortfall modules are enumerated
by full path in `gaps.items` of the receipt.

## 3. The gap is real, and the naive count is much worse

| Bucket | Modules |
| :--- | ---: |
| Provenanced by identity (path or sha256) | 129 |
| Basename mentioned but no identity match | 810 |
| Never named by any provenanced receipt | 230 |
| **Total** | **1169** |

`129 + 810 + 230 = 1169`. The 810 middle bucket is the trap: a basename-only
count would have reported `129 + 810 = 939` of 1169, or 80.33 percent, and that
number would have been inflated by generic names shared across parallel firmware
trees. It is reported here so the difference is auditable, and it is not used.

| Kernel version | Modules | Provenanced | Gap |
| :--- | ---: | ---: | ---: |
| 2.6.32.68 | 622 | 51 | 571 |
| 2.6.32.71 | 198 | 20 | 178 |
| 3.14.65 | 316 | 34 | 282 |
| 4.14.0 | 12 | 3 | 9 |
| 6.6.110 | 21 | 21 | 0 |
| **Total** | **1169** | **129** | **1040** |

The 16 modules in `firmware/` are all covered because they are the build outputs
sibling stages cite directly. The `artifacts/` tree holds 1153 extracted copies,
of which 113 are named by a provenanced receipt; the rest are unexamined
rootfs extractions.

## 4. Coverage is concentrated, not distributed

Only 16 of the 52 provenanced receipts in the corpus reference any module. One
receipt, `stage990a_ath10k_htt_tx_credit_flow_re.json`, accounts for 99 of the
129 covered modules, a share of 0.767442; `stage989a_ath10k_pci_ce_rings_re.json`
adds 35 and `stage698a_pbe5ac_lbe5ac_tester_release_package_v4.json` adds 21.
That pattern matters: those receipts enumerate module paths, so the modules are
named rather than individually disassembled. Identity-level reference proves the
exact file was named by a provenanced receipt; it does not prove the module was
decompiled, its symbols enumerated, or any patch validated.

## 5. Exhaustive enumeration and its attestation

Inlining 1040 paths of up to 150 characters would exceed this document's
180-line budget and would be unreadable, so the receipt is authoritative and
this document attests it cryptographically. The 129 covered paths and the 1040
gap paths are each listed in full in the receipt, and their sorted newline-joined
digests are:

- Covered paths (129), sha256 `7fba2c53270f86b2b90813de181effe9999ec0070f1e0eb59f52a9c120f2a6d8`
- Gap paths (1040), sha256 `0a9bce3275be6414b1a5fd78726a0570ec26671ab6b75efdd26e81e8890884b8`

An operator can recompute either digest from the receipt and confirm it matches,
so the enumeration is complete and checkable even though it is not inlined here.
No module is invented and none is silently dropped: the counts above are derived
from the same arrays the digests cover.

## 6. What would close a gap

A gap closes only when a receipt carrying `CONFIRMED_STATIC_BINARY` names that
module's exact path or exact sha256 after actually inspecting it. Relabelling an
existing `SIMULATED_MODEL_ONLY` receipt, adding a prose cross-reference, or
counting basenames does not close a gap and would misrepresent provenance. The
810 basename-only modules are the cheapest legitimate target: most are already
on disk and await a first real inspection pass rather than more extraction.

## 7. Reproduction

```
python tools/verify/verify_stage993a_ko_modules_atlas_re.py
python tools/verify/verify_stage993a_ko_modules_atlas_re.py --check
python tools/verify/verify_stage993a_ko_modules_atlas_re.py --check-bytes
```

`--check` re-measures, compares every finding, and distinguishes a moved receipt
corpus from a changed result instead of conflating them, because sibling stages
write to `artifacts/autoresearch` concurrently. `--check-bytes` demands exact
byte identity and is the command used to prove two consecutive runs agree. The
receipt carries no wall-clock field by design.
