<!-- doc-head: Stage 924A - no Xtensa ROM image exists so the BMI decompressor cannot be read, but all 140 SGMT segments conform to the BCL LZ77 grammar with exact lengths, valid back-references measured up to 99,973 bytes and a full literal-only re-encode that decodes back identically -->
# Stage 924A — BCL LZ77 stream conformance against the BMI grammar

- **Receipt**: [`artifacts/autoresearch/stage924a_xtensa_bmi_lz_stream_and_crc_check_re.json`](../artifacts/autoresearch/stage924a_xtensa_bmi_lz_stream_and_crc_check_re.json)
- **Tool**: [`tools/re/dissect_stage924a_xtensa_bmi_lz_stream_and_crc_check_re.py`](../tools/re/dissect_stage924a_xtensa_bmi_lz_stream_and_crc_check_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. The premise that fails, and the one that holds

```
rom_images_found = 0
segments = 140   errors = 0   exact = 140   roundtrip = 140
```

**`REFUTED`**: the BMI LZ77 decompressor lives in masked ROM, and **no ROM image exists** in this
corpus. A token-aware sweep for `.bin`/`.img`/`.dump` files whose stem contains `rom` returns **zero**.
So the implementation cannot be read, and this stage does not claim to have read it.

What it proves instead is **grammar conformance**, and that is a real, falsifiable property.

## 1. The invariants, all satisfied

| Check | Result |
| :--- | :-: |
| segments decoded | **140 / 140** |
| decode errors | **0** |
| produced length equals declared length | **140 / 140** |
| every back-reference inside already-produced bytes | **140 / 140** |
| marker escape never ambiguous | **140 / 140** |
| byte accounting closes at the segment end | **140 / 140** |
| literal-only re-encode decodes back identically | **140 / 140** |

**`CONFIRMED`**: `all_lengths_exact = 1`, `all_roundtrip = 1`.

## 2. The window assumption I had to retract

My first version rejected any back-reference beyond **65,536 bytes**, on the assumption that a 64 KiB
window was implied. That produced **7 spurious decode errors** on real segments, with offsets such as
65,658 and 66,727.

The decoder in Stage 891A never enforced that limit, and it was right not to. The measured maximum:

**`CONFIRMED`**: `observed_max_backref_offset = 99,973` bytes.

So the decoder needs a window of at least **97.6 KiB**, and a 64 KiB assumption is simply wrong. The
check was replaced by a measurement, which is the only defensible form: the number is now reported, not
assumed.

## 3. Why a literal-only round-trip is a real test

The payload of each segment is decoded, then **re-encoded from first principles** as a BCL stream that
uses literals only — marker byte chosen as the least frequent value in the payload, marker escaped as
`marker 0x00`, every other byte emitted as itself. The result is decoded again with the same decoder and
must reproduce the payload byte for byte.

That proves three things and not a fourth:

- the **grammar** is fully understood, because a stream written by this tool is accepted;
- the decoder is **not tuned** to the vendor encoder's choices;
- the payload is **canonically representable**, so nothing in it is unreachable.

It does **not** prove the ROM's decoder agrees with ours. That residual is exactly what the absent ROM
image costs.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| a ROM image was analysed | **REFUTED** (0 files) |
| the BMI decompressor implementation was read | **REFUTED** |
| our segments match the BCL LZ77 grammar | **CONFIRMED** (140 of 140) |
| every back-reference is valid | **CONFIRMED** |
| the required window is 64 KiB | **REFUTED** (99,973 bytes observed) |
| the payloads round-trip through an independent encoder | **CONFIRMED** (140 of 140) |
| a CRC was verified | **REFUTED** (`crc_check_available = 0`) |

## 5. The operational reading

1. **Our patches are structurally admissible**: 140 of 140 segments satisfy every grammar invariant, so
   a decoder that implements BCL LZ77 as documented will accept them.
2. **Do not size a buffer at 64 KiB.** The measured back-reference distance is 99,973 bytes; a 64 KiB
   window would corrupt real segments.
3. **Conformance is not execution.** Nothing here says the target accepts the image or runs the patched
   site; Stage 892A owns that question and answers it with zero.

## 6. Gaps

- **`UNKNOWN`** — whether the ROM decoder matches this grammar in every corner.
- **`UNKNOWN`** — whether a checksum accompanies the stream on the BMI path.
- **Blocked** — no ROM image, so implementation-level equivalence cannot be tested.
- **Known limit** — the vendor stream uses back-references; our re-encode does not, so byte equality of
  the compressed form is not expected and was never asserted.
- **Not attempted** — any dynamic validation.
