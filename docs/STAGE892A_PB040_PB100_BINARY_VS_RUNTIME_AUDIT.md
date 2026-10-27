<!-- doc-head: Stage 892A - of the seven gates PB-040 to PB-100 three have container provenance, two are proven present on target with a matching hash and register readback plus a post-reload ping, and zero have any site execution witness because dmesg appears in none of the 333 receipts in the range -->
# Stage 892A — PB-040..PB-100: container proof versus runtime proof

- **Receipt**: [`artifacts/autoresearch/stage892a_pb040_pb100_binary_vs_runtime_audit.json`](../artifacts/autoresearch/stage892a_pb040_pb100_binary_vs_runtime_audit.json)
- **Tool**: [`tools/qca988x/audit_stage892a_pb040_to_pb100_binary_vs_runtime.py`](../tools/qca988x/audit_stage892a_pb040_to_pb100_binary_vs_runtime.py)
- **Audit reference**: section A09
- **Scope**: offline static. Reads receipts. No firmware written, no flash touched, no radio contacted.

## 0. The matrix

```
gates=7 static=3 present=2 readback=2 ping=2 execution=0 runtime=0 pending=7 dmesg=0
```

| Gate | static container | present on target | register readback | post-reload ping | site execution | runtime |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| **PB-040** | 1 | 1 | 1 | 1 | **0** | **0** |
| **PB-050** | 1 | 1 | 1 | 1 | **0** | **0** |
| **PB-060** | 1 | 0 | 0 | 0 | **0** | **0** |
| **PB-070** | 0 | 0 | 0 | 0 | **0** | **0** |
| **PB-080** | 0 | 0 | 0 | 0 | **0** | **0** |
| **PB-090** | 0 | 0 | 0 | 0 | **0** | **0** |
| **PB-100** | 0 | 0 | 0 | 0 | **0** | **0** |

**`CONFIRMED`**: `gates_runtime_proven = 0`, `gates_pending = 7`.

## 1. What the live evidence actually says

Stage **585A** is the strongest live record in the range, and it is worth quoting precisely:

```
ap_241_verified: true          sta_242_verified: true
firmware sha256 readback matches expected on both sides
expected_reg_0x29e00 = 0x13761320, read back as 0x13761320
post_reload_1472b_ping: count 10, loss 0 %, p50 23.575 ms, p99 35.616 ms
```

So for PB-040 and PB-050, on the live pair:

- the patched image is **loaded from the target path** (`/lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin`);
- its **hash matches** the expected patch;
- the **register the patch targets holds the expected value**;
- the radio **passes traffic** after the reload.

That is four real measurements, and each one is more than a file hash.

## 2. Why that is still not execution

A loaded image, a matching hash, a matching register and a healthy ping are all **compatible with the
changed code path never being taken**. None of them observes the patched instruction running.

The witness that would close it is a **target-side signal** tied to the changed site: a `dmesg` line
emitted only by the new branch, or a `debugfs` counter that increments only when it executes.

**`REFUTED`**: no such witness exists in this range.

| Marker | Receipts containing it |
| :--- | :-: |
| `dmesg` | **0** of 333 |
| `post_reload` | 2 of 333 |
| `debugfs` | 6 of 333 |

Zero `dmesg` across 333 receipts is the single most important number in this stage. Whatever the
patches do, the corpus does not contain the evidence that would let anyone say the new code **ran**.

## 3. The explicit pending statement

Every gate carries, in the receipt itself:

> *"static container provenance does not prove execution: no dmesg and no debugfs counter were captured
> after reloading caldata and board-2.bin on a live target, so the effect of this gate on air behaviour
> is unproven"*

**`CONFIRMED`**: `explicit_pending_statement = 1` — the reason is attached **per gate**, not once in
prose, so it survives being quoted as a single row.

## 4. Three different kinds of absence

The four blocked gates are not blocked in the same way, and conflating them misdirects the work:

- **PB-070** — a **policy** decision already taken (`LOCKED_CONCENTRATE_ON_MAC_AND_POLICY`);
- **PB-080** — no queue anchor exists in the corpus;
- **PB-090** — no transfer anchor exists in the corpus;
- **PB-100** — no receive anchor exists in the corpus.

**`CONFIRMED`**: `gates_static_proven = 3` while `gates = 7`. Two of the three columns are empty for
four of the seven gates.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| PB-040 and PB-050 are carried by valid containers | **CONFIRMED** (891A) |
| PB-040 and PB-050 are loaded with matching hashes on target | **CONFIRMED** (585A readback) |
| the targeted register holds the expected value | **CONFIRMED** (`0x29e00`) |
| traffic passes after the reload | **CONFIRMED** (10 probes, 0 % loss) |
| the patched site executed | **REFUTED** (no witness) |
| any gate reaches runtime | **REFUTED** (`runtime_proven = 0`) |
| `dmesg` evidence exists anywhere in range | **REFUTED** (0 of 333) |
| PB-060..PB-100 are present on target | **REFUTED** (0 of 4) |

## 6. What would move a row to runtime

In order, and each is a measurement rather than an argument:

1. load the patch with `caldata` and `board-2.bin` **reloaded** so the calibrated path is the one taken;
2. capture `dmesg` across the reload and across a traffic burst;
3. read a `debugfs` counter that only the patched branch increments;
4. prove the **absence of fallback** — that the driver did not revert to the stock firmware;
5. restore and re-verify the original hashes.

Until step 3 and step 4 exist, the correct phrasing is the one used here: **proven in the container,
pending on target**.

## 7. Gaps

- **`UNKNOWN`** — whether any gate's changed site is reached at runtime.
- **`UNKNOWN`** — whether restoration after the live test left the pair in stock state.
- **Blocked** — no `dmesg` or `debugfs` witness in the corpus for any gate.
- **Known limit** — presence, hashing and ping are necessary and not sufficient.
- **Not attempted** — any live action, any flash, any reload.
