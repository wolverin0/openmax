<!-- doc-head: STAGE324A_LTU_AME_CORE_SCHEDULER_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 324A — LTU `ame_core.ko` TDD scheduler and UL/DL duty cycle

- **Receipt**: [`artifacts/autoresearch/stage324a_ltu_ame_core_scheduler_re.json`](../artifacts/autoresearch/stage324a_ltu_ame_core_scheduler_re.json)
- **Tool**: `tools/re/ltu_ame_core_scheduler_and_ul_dl_ratio_re.py`
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Modules

Both LTU images, ARM **little-endian** `ET_REL`:

| Module | Bytes |
| :--- | :-: |
| `AF-LTU.v2.4.2:ame_core.ko` | 3,282,052 |
| `AF-LTU-Rocket.v2.4.2:ame_core.ko` | 3,318,764 |

## 1. Symbol surface

| Bucket | Symbols |
| :--- | :-: |
| **grant** (`grant|alloc|contention|sched|slot|queue`) | **314** |
| **modulation** (`qam|mcs|modul|nss|rate_|txpower`) | **151** |
| **frame** (`frame|tdd|superframe|guard`) | **91** |
| **duty** (`duty|ratio|split|flex|fixed|dynamic`) | **28** |
| **duration** (`duration|interval|period|tick|usec|slot_time`) | **22** |

The grant bucket dominating at 314 is consistent with a scheduler that spends most of its
naming on allocation rather than on frame structure.

## 2. Frame duration ladder — four of five recovered

The 1/2/2.5/4/5 ms ladder in microseconds was searched as **ARM `movw` immediates** inside the
22 duration-named functions.

| Value | LTU | Rocket | Interpretation |
| :-: | :-: | :-: | :--- |
| 1000 µs | **absent** | **absent** | 1 ms — not materialised as `movw` |
| **2000 µs** | **12** | **12** | 2 ms |
| **2500 µs** | **11** | **11** | 2.5 ms |
| **4000 µs** | **11** | **11** | 4 ms |
| **5000 µs** | **11** | **11** | 5 ms |

**`CONFIRMED`**: 2000, 2500, 4000 and 5000 appear as immediates, 45 sites total, identically in
both images. **Four of the five advertised frame durations are present in the code.**

**`UNKNOWN`**: 1 ms. It is absent as a `movw`. It may be encoded as a rotated `mov`, derived by
division from 5000, or not exist as a supported mode in this build. Not claimed.

**`INFERRED`**: the 11–12 occurrences per value suggest one materialisation per scheduler
entry point rather than a single shared constant — which is what a per-mode branch arm looks
like.

## 3. What is not decoded

**The duty-cycle state machine is not decoded.** The stage asked for fixed-vs-flexible UL/DL
duty-cycle behaviour. What exists here is 28 duty-named symbols; the branch graph that selects
between fixed and flexible is not traced.

**Contention versus scheduled grant is not decoded either.** 314 grant-named symbols are a
surface, not a policy. No allocation decision was reconstructed.

## 4. A method defect caught in this stage

The first run returned **0** frame-duration constants because the sweep used the **MIPS**
`addiu $zero,N` form. These modules are **ARM little-endian**. Replacing it with the ARM `movw`
(`0xE30?0000`, imm4 in bits 19-16, imm12 in 11-0) and rotated `mov` forms produced 45 sites.

That is the same class of error as Stage 154A's zero-by-construction register count: applying a
MIPS idiom to an ARM module and reading the resulting zero as evidence.

## 5. String evidence

40 `.rodata` literals mention ms/usec/frame/tdd. They were not decoded into a configuration
table; they are recorded in the receipt as a bucket.

## 6. Gaps

- **`UNKNOWN`** — the 1 ms mode.
- **`UNKNOWN`** — fixed vs flexible selection logic.
- **`UNKNOWN`** — contention vs scheduled grant policy.
- **`UNKNOWN`** — `movt` halves of wider constants (only `movw` and rotated `mov` are read).
- **`KNOWN LIMIT`** — a duration constant in a duration-named function is a candidate, not proof
  that it sets the frame length.
- **Not attempted** — dynamic validation.
