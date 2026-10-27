<!-- doc-head: STAGE325A_WA_XC_UMAC_NODE_AID_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 325A — WA/XC `umac.ko` node lifecycle and AID bitmap

- **Receipt**: [`artifacts/autoresearch/stage325a_wa_xc_umac_node_aid_re.json`](../artifacts/autoresearch/stage325a_wa_xc_umac_node_aid_re.json)
- **Tool**: `tools/re/wa_xc_umac_ieee80211_node_and_aid_bitmap_re.py`
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Modules

| Image | `umac.ko` bytes |
| :--- | :-: |
| `WA.v8.7.25` | 2,356,432 |
| `XC.v8.7.25` | 2,358,768 |

MIPS32 big-endian `ET_REL`. The WA and XC builds differ in size, so they are two builds of the
same module, not one shared binary.

## 1. Symbol surface

| Bucket | WA | XC |
| :--- | :-: | :-: |
| **node** (`ieee80211_node|node_|peer|sta_|vap`) | **277** | **277** |
| **auth** (`auth|acl|deny|allow`) | **46** | **46** |
| **aid** (`aid|bitmap|assoc|max_sta`) | **48** | **48** |
| **pspoll** (`pspoll|uapsd|power_save|sleep|ps_`) | **38** | **38** |
| **inactivity** (`inactiv|idle|timeout|age_|expire`) | **22** | **22** |

Identical counts in both images. The node bucket dominates as expected for an upper-MAC module.

## 2. AID ceiling immediates

The 32 / 64 / 128 / 256 candidates were searched as MIPS `addiu $zero,N` immediates inside the
48 AID-named functions.

| Value | WA | XC | Interpretation |
| :-: | :-: | :-: | :--- |
| 32 | **2** | **2** | candidate |
| **64** | **absent** | **absent** | **not materialised** |
| **128** | **1** | **1** | candidate, matches the 128-CPE ceiling |
| 256 | **2** | **2** | candidate |

**`CONFIRMED`**: 128 is present as an immediate, once per image. **64 is absent.**

That is the most useful single fact in this stage. The deployment question was whether the AID
bitmap scales to 64 or 128 CPEs; the code materialises **128** and never **64**. Combined with
the Stage 81A-W2 finding that the PtMP client ceiling is a **104-element pool** of
`sizeof(struct sta) = 2440`, the picture is consistent: there is no 64-AP boundary in the code.

**`UNKNOWN`** what the single 128 site actually bounds. It could be an AID mask width, a loop
bound, or an unrelated array size. One site is too few to generalise.

## 3. What is not decoded

**No `ieee80211_node` lifecycle.** 277 node-named symbols are a surface. The alloc/ref/free
transition graph is not traced.

**No PS-Poll or U-APSD handshake.** 38 pspoll-named symbols are a bucket. The actual trigger
frame handling was not reconstructed.

**No inactivity timing value.** 22 inactivity-named symbols exist, but no numeric seconds or
tick count was attributed to them.

## 4. String evidence

40 `.rodata` literals mention aid/assoc/pspoll/uapsd/inactiv. They are recorded in the receipt as
a bucket, not decoded into a configuration table.

## 5. Cross-reference

| Prior result | This stage |
| :--- | :--- |
| Stage 81A-W2: PtMP ceiling is a **104-element pool**, not a policy of 32/64 | consistent: **64 absent**, **128 present** |
| Stage 81A-W2: no `too many clients` constant in `.rodata` | consistent: no 64 boundary in code |

## 6. Gaps

- **`UNKNOWN`** — what the single 128 immediate bounds.
- **`UNKNOWN`** — node alloc/ref/free lifecycle.
- **`UNKNOWN`** — PS-Poll and U-APSD trigger handling.
- **`UNKNOWN`** — inactivity timeout values.
- **`KNOWN LIMIT`** — an immediate inside an AID-named function is a candidate, not proof.
- **Not attempted** — dynamic validation.
