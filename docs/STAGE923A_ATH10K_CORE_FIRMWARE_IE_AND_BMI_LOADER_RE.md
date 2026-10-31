<!-- doc-head: Stage 923A - ath10k_core.ko and firmware-5.bin are both absent from the corpus so the IE validator cannot be documented from a binary, while the one QCA-ATH10K container carries a 98-byte header holding the build string 10.1-ct-8x-fW-022-ecad3248 and no TLV IE table at all -->
# Stage 923A — ath10k firmware IE validation versus the embedded SGMT container

- **Receipt**: [`artifacts/autoresearch/stage923a_ath10k_core_firmware_ie_and_bmi_loader_re.json`](../artifacts/autoresearch/stage923a_ath10k_core_firmware_ie_and_bmi_loader_re.json)
- **Tool**: [`tools/re/dissect_stage923a_ath10k_core_firmware_ie_and_bmi_loader_re.py`](../tools/re/dissect_stage923a_ath10k_core_firmware_ie_and_bmi_loader_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. Two absent premises, stated first

```
ath10k_core files: 0        firmware-5 files: 0
container: present          segments: 2
```

**`REFUTED`**: `ath10k_core_present = 0`, `firmware5_present = 0`.

A case-insensitive sweep of `artifacts/` and `firmware/` returns **zero** files matching either name. So
`ath10k_core_fetch_firmware_api_n` cannot be documented from a binary here, and neither can the TLV IE
container it validates, because `firmware-5.bin` is not in the corpus either.

This is the eighth stage blocked by the same absent module. Recording it again is the point: a reader
of a later summary must not assume the validator was ever read.

## 1. What the container actually is

```
path    artifacts/firmware_re_xc_ltu/openwrt_qca988x_hw20_firmware_2_ct.bin
bytes   204,796
magic   QCA-ATH10K
SGMT    at 0x0000006c and 0x000001c58
```

**`CONFIRMED`**: `container_segments = 2`, and the first `SGMT` sits at **offset 108**.

## 2. The header is a build string, not an IE table

Between the magic and the first `SGMT` there are **98 bytes**. The TLV probe starts at offset 14 and
covers **94** of them:

| Probe | Result |
| :--- | :-: |
| region bytes | 94 |
| records parsed | 1 |
| first "tag" | 1,835,008 |
| chains exactly to the region end | **0** |

**`REFUTED`**: `tlv_chains_exactly = 0`.

A tag of 1,835,008 with a length of 808,517,632 is not a header entry, it is the first four ASCII bytes
of a string read as an integer. The region is a **build identifier**:

```
10.1-ct-8x-__fW-022-ecad3248
```

Stage 925A extracts the same string and confirms the same 98-byte extent, which is why the gate
cross-checks the two.

## 3. What is established

| Claim | Status |
| :--- | :-: |
| `ath10k_core.ko` is in the corpus | **REFUTED** (0 files) |
| `firmware-5.bin` is in the corpus | **REFUTED** (0 files) |
| the IE validator was recovered | **REFUTED** (`ie_validator_recovered = 0`) |
| the BMI loader was recovered | **REFUTED** |
| one `QCA-ATH10K` container exists | **CONFIRMED** (204,796 bytes) |
| it carries two SGMT segments | **CONFIRMED** |
| its 98-byte header is a TLV IE table | **REFUTED** (`tlv_chains_exactly = 0`) |
| its header holds a build string | **CONFIRMED** (`10.1-ct-8x-__fW-022-ecad3248`) |
| any IE tag value is confirmed by a binary | **REFUTED** (`binary_evidence_for_ie_tags = 0`) |

## 4. The operational reading

1. **Do not cite this stage for ath10k validation logic.** It has none, and it says so.
2. **The container is a wrapper with a version header**, not a TLV IE firmware file. Reading its first
   eight bytes as `(tag, length)` produces garbage, which is what a real parse would also do.
3. **Documentary mentions are not evidence.** The tool counts them (1 for the whole symbol set) and
   records `binary_evidence_for_ie_tags = 0` beside the count, so the two cannot be confused.

## 5. Gaps

- **`UNKNOWN`** — how `ath10k_core_fetch_firmware_api_n` validates `ATH10K_FW_IE_FW_IMAGE`, OTP and
  `WMI_OP_VERSION`.
- **`UNKNOWN`** — whether the 98-byte header has a structured prefix before the build string.
- **Blocked** — both binaries are absent; the stage cannot be completed offline with this corpus.
- **Known limit** — a mention in a receipt is documentation, not a disassembly.
- **Not attempted** — any acquisition, any dynamic validation.
