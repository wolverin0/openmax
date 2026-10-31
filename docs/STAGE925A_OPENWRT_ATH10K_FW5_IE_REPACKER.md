<!-- doc-head: Stage 925A - the corpus magic is QCA-ATH10K and the stage's QCA-ATH10K-FW string occurs nowhere in it, the source container has no TLV IE table, and the repacker builds a canonical two-record IE container that re-parses to exact EOF with its tag numbers declared unverified because ath10k_core.ko is absent -->
# Stage 925A — fail-closed ath10k container repacker

- **Receipt**: [`artifacts/autoresearch/stage925a_openwrt_ath10k_fw5_ie_repacker.json`](../artifacts/autoresearch/stage925a_openwrt_ath10k_fw5_ie_repacker.json)
- **Tool**: [`tools/qca988x/build_stage925a_openwrt_ath10k_fw5_ie_repacker.py`](../tools/qca988x/build_stage925a_openwrt_ath10k_fw5_ie_repacker.py)
- **Output container**: `artifacts/autoresearch/stage925a/fw5_ie_rebuilt.bin`
- **Scope**: offline static. Writes a container under `artifacts/`. No firmware loaded, no radio contacted.

## 0. Three measurements before any packaging

```
magic QCA-ATH10K      occurrences = 1
magic QCA-ATH10K-FW   occurrences = 0
source header bytes   = 98
source TLV table      = absent
```

**`REFUTED`**: `QCA-ATH10K-FW` appears **nowhere** in `artifacts/` or `firmware/`. The stage's filename
for the magic does not exist in this corpus; the magic that does exist is the ten-byte `QCA-ATH10K`.

**`REFUTED`**: `source_has_tlv_table = 0`. As Stage 923A established, the 98 bytes between the magic and
the first `SGMT` hold a build string, not `(tag, length)` records.

## 1. What the repacker builds

A canonical IE container, from parts, around the two SGMT payloads already present:

```
magic  QCA-ATH10K
u32    record count            = 2
record u32 tag, u32 length, payload padded to 4 bytes
```

Records: `tag 0` carrying the first SGMT container, `tag 1` carrying the second.

**`CONFIRMED`**: the tool re-parses **its own output** and reports:

| Check | Result |
| :--- | :-: |
| records written | 2 |
| records parsed back | 2 |
| magic accepted | 1 |
| payload lengths exact | 1 |
| 4-byte alignment honoured | 1 |
| chain reaches exact end of file | **1** |

`rebuilt_parse_ok = 1`, `rebuilt_exact_eof = 1`.

## 2. The tag numbers are a contract, not a constant

**`CONFIRMED`**: `ie_tags_confirmed = 0`, and every tag carries the status
**`UNVERIFIED_PARAMETER`**.

The values used are `IE_FW_IMAGE = 0`, `IE_OTP_IMAGE = 1`, `IE_WMI_OP_VERSION = 8`. They come from
this tool's declared interface, **not** from a binary: `ath10k_core.ko` is absent, so nothing in the
corpus can confirm them.

That distinction is the whole point of the stage. A repacker that labelled these as recovered constants
would hand a downstream consumer a firmware image built on invented numbers. Here the numbers are
declared, versioned as unverified, and counted as zero confirmations.

## 3. What the rebuild preserves and what it loses

| Property | State |
| :--- | :-: |
| SGMT byte ranges | **preserved** (both payloads copied verbatim) |
| record count and lengths | **exact**, verified by re-parse |
| the original 98-byte header | **not reproduced**, format unknown |
| the vendor's own wrapping | **unknown**, no `firmware-5.bin` to compare |
| acceptance by the target loader | **unproven** |

The last row matters: a container that parses with **our** parser proves self-consistency, which is the
same limit Stage 891A documented. It is not equivalence with the device loader.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| the corpus contains `QCA-ATH10K-FW` | **REFUTED** (0) |
| it contains `QCA-ATH10K` | **CONFIRMED** (1) |
| the source has a TLV IE table | **REFUTED** |
| the source header holds a build string | **CONFIRMED** (`10.1-ct-8x-__fW-022-ecad3248`) |
| a two-record IE container was built | **CONFIRMED** |
| the rebuild re-parses to exact EOF | **CONFIRMED** |
| the IE tag values are confirmed by a binary | **REFUTED** (`ie_tags_confirmed = 0`) |
| the target loader accepts the rebuild | **UNKNOWN** |

## 5. The operational reading

1. **Use the observed magic.** `QCA-ATH10K`, ten bytes. Anything longer is an invention of the stage
   title, not a property of the corpus.
2. **Do not ship the rebuilt container to a device** on the strength of this stage. It is structurally
   valid and unverified against any loader.
3. **Read `tag_contract` before consuming the file.** It states the parameter status in one field.

## 6. Gaps

- **`UNKNOWN`** — the real IE tag numbering, blocked by the absent module.
- **`UNKNOWN`** — the format of the original 98-byte header.
- **`UNKNOWN`** — whether a real `firmware-5.bin` would accept this layout.
- **Known limit** — structural validity is not loader acceptance.
- **Not attempted** — any flash, any load, any dynamic validation.
