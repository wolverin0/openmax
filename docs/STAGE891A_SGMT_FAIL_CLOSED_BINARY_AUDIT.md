<!-- doc-head: Stage 891A - every SGMT container in the corpus parses fail-closed with zero failures, 35 containers and 140 segments all carrying file_flags 1, twelve patch artefacts valid, three of three PB-040 RAM offsets matched to a byte range, and the field offset four called version by the inspector is the same field the patcher calls file_flags -->
# Stage 891A — fail-closed SGMT binary audit

- **Receipt**: [`artifacts/autoresearch/stage891a_sgmt_fail_closed_binary_audit.json`](../artifacts/autoresearch/stage891a_sgmt_fail_closed_binary_audit.json)
- **Tool**: [`tools/qca988x/verify_all_sgmt_patches_fail_closed_audit.py`](../tools/qca988x/verify_all_sgmt_patches_fail_closed_audit.py)
- **Audit reference**: `artifacts/chatgpt_audit_1afaeb7/AUDITORIA_2026-10-27.md` section A09
- **Scope**: offline static. No firmware written, no flash touched, no radio contacted.

## 0. Result

```
files=34 containers=35 ok=35 failed=0 segments=140
flags={'1': 35} patches=12/12 ram=3/3 fail_closed=1
```

**`CONFIRMED`**: all 35 container occurrences parse and pass every check. Zero failures. Zero failure
records. `fail_closed = 1`.

The tool implements its **own** BCL LZ77 decoder. It reads
`tools/qca988x/sgmt_container_inspector.py` and `firmware/xtensa_sgmt_surgical_patcher.py` for the
format only, and **does not import or edit either**, so a defect in the inspector cannot mask a defect
in the artefact.

## 1. The field at offset 4 has two names, and that resolves an A09 question

A09 asks for an explicit distinction between `file_flags` 0 (uncompressed) and 1 (compressed).

```
offset 0   "SGMT"
offset 4   uint32 LE   inspector: file_type_version, requires 1
                       patcher:   file_flags, 1 means compressed
```

**`CONFIRMED`**: "version equals 1" and "file_flags equals 1" are **the same assertion on the same
field**. The corpus contains **35 containers, all value 1**, and **zero** containers with value 0.

So the uncompressed branch A09 warns about is **never exercised by any artefact here**. That is a
statement about the corpus, not about the patcher: the code path may exist and remains untested, which
is exactly what A09 said.

## 2. Structural checks, all passing

| Check | Result |
| :--- | :-: |
| magic `SGMT` | 35 / 35 |
| begin sentinel `0xFFFFFFFD` exactly once | 35 / 35 |
| end sentinel `0xFFFFFFFF` exactly once | 35 / 35 |
| every segment decodes to its declared length | 140 / 140 |
| segment ranges pairwise disjoint | 35 / 35 |
| no duplicate segment start | 35 / 35 |
| decoder never reads past the buffer | 35 / 35 |
| no unknown trailing bytes | 35 / 35 |
| exact end-of-file | 34 / 35 |

**`CONFIRMED`**: two invariants that look like one are not.

- **Disjointness is a format rule** and holds everywhere.
- **Ascending file order is not a rule**, and holds **nowhere**: the four segments of a typical image
  load at `0x00980000`, `0x0040b000`, `0x0040d1a0`, `0x00983c00` — grouped by memory region, not sorted
  by address. My first run failed all 35 containers by conflating the two, which was my defect, not
  the corpus's.

The one non-exact-EOF container is the wrapper
`openwrt_qca988x_hw20_firmware_2_ct.bin`, which holds **two** containers separated by an **8-byte
descriptor** `03000000a1030300`; its last container ends with three NUL padding bytes at exactly
204,796. Both containers were audited independently and both pass.

## 3. The twelve patch artefacts

**`CONFIRMED`**: `patches_audited = 12`, `patches_ok = 12`.

These are the PB-040 variants under `firmware/openwrt/xtensa_ram_patches_stage347a`:
`ALL3-COMBINED`, `CANARY-RODATA`, `CCA-AGC-OVERRIDE` and `SUB20MHZ-PLL-DIV` for each of the three
roles. Each carries four segments and passes every check above.

## 4. Exact RAM offset correspondence

A09 asks for offsets that correspond exactly, not approximately. Stage 891A checks the three PB-040
roles against the segments themselves:

| Role | Virtual address | Declared offset | Offset in segment | Inside a segment |
| :--- | :--- | :-: | :-: | :-: |
| `ptmp_ap` | `0x0040c39c` | 5020 | **5020** | yes |
| `ptmp_sta` | `0x0040c37c` | 4988 | **4988** | yes |
| `ptp` | `0x0040c460` | 5216 | **5216** | yes |

**`CONFIRMED`**: `ram_roles_matched = 3 / 3`.

Each address lands inside a DRAM segment starting at `0x0040b000`, the difference equals the recorded
offset **exactly**, and four bytes fit inside the segment. The judgement is a byte-range membership
test, not a string comparison.

## 5. What this proves and what it does not

| Claim | Status |
| :--- | :-: |
| every SGMT container in the corpus is structurally valid | **CONFIRMED** |
| every container declares file_flags 1 | **CONFIRMED** (35 of 35) |
| any container declares file_flags 0 | **REFUTED** (0) |
| segment ranges overlap anywhere | **REFUTED** (0) |
| segments are stored in ascending address order | **REFUTED** (0 of 35) |
| the 12 patch artefacts are byte-valid containers | **CONFIRMED** |
| PB-040 offsets match base plus offset exactly | **CONFIRMED** (3 of 3) |
| the target loader accepts these files | **UNKNOWN / not tested** |
| the patched site executes on target | **UNKNOWN / not tested** |

## 6. Why the last two rows stay unknown

A09 makes the point directly: a roundtrip with our own compressor and decompressor proves
**self-consistency**, not equivalence with the device decoder. This audit is self-consistency at the
container level, executed with an independent decoder — stronger than a roundtrip, and still not the
target.

So the SGMT patches are **proven at container level** and **pending execution** with `caldata` and
`board-2.bin` reloaded on a live target. Stage 892A carries that statement per gate.

## 7. Gaps

- **`UNKNOWN`** — whether the target loader accepts the containers.
- **`UNKNOWN`** — whether the patched instruction is reached.
- **`UNKNOWN`** — the file_flags 0 branch, untested because no artefact uses it.
- **Known limit** — container integrity is orthogonal to behavioural effect.
- **Not attempted** — any write, any flash operation, any dynamic validation.
