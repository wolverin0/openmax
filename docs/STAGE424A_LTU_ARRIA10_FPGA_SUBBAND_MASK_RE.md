<!-- doc-head: STAGE424A_LTU_ARRIA10_FPGA_SUBBAND_MASK_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 424A — Arria 10 subband masks and tone-nulling ioctls in the LTU fabric

- **Receipt**: [`artifacts/autoresearch/stage424a_ltu_arria10_fpga_subband_mask_re.json`](../artifacts/autoresearch/stage424a_ltu_arria10_fpga_subband_mask_re.json)
- **Tool**: [`tools/re/build_stage424a_ltu_arria10_fpga_subband_mask_re.py`](../tools/re/build_stage424a_ltu_arria10_fpga_subband_mask_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Five absences, one near-miss

| Named artefact | Found |
| :--- | :-: |
| `eab_driver.ko` | **0 files** |
| `libltu` | **0 files** |
| `af-ltu` **firmware tree / rootfs dir** | **0 dirs** |
| FPGA bitstream (`.rbf`, `.sof`) | **0 files** |
| `*af-ltu*` anything | **36 files — all device profile configs** |

The 36 near-misses are `system-af-ltu*.cfg` (3,489–3,689 bytes each), duplicated under `usr/etc`
and `var/etc` across the `afltu` and `aflturocket` trees — product variant profiles
(`-ltu6r`, `-ltur`, `-ltuxr`, `-ltupro`, …), not a firmware directory.

**`CONFIRMED`**: those 36 configs contain **0** `subband` keys and **0** `fpga` keys. They carry
device identity and radio defaults, nothing about fabric masking.

**`CONFIRMED`**: this is the **fifth independent confirmation** that `eab_driver.ko` does not exist
in this corpus.

## 1. The EAB interface is inside `ame_core.ko`

Since there is no driver module, the EAB logic is compiled into the main one. `ame_core.ko`
(3,282,052 bytes) carries:

| Token | Hits |
| :--- | :-: |
| `eab` | **359** |
| `EAB` | **208** |
| `subband` | 17 |
| `mask` | 2 |
| `null` | 11 |
| **`tone`** | **0** |
| **`notch`** | **0** |
| **`punctur`** | **0** |
| **`arria`** | **0** |
| **`fpga`** | **0** |

**23 defined symbols** carry `eab` in the name. Representative:

```
air_data_handler_test_eab_many_cpes
ame_core_dump_eab_qstatus
ame_core_eab_get_total_frag_num_in_tx_q_w_lock
ame_core_eab_read_tx_resend_w_lock
ame_modem_bbp_eab_testmode_handler
```

**`CONFIRMED`**: the EAB surface is real, named, and substantial — it owns queue status, TX resend
accounting, fragment counting and a BBP test-mode handler.

**`REFUTED`**: the words `tone`, `notch`, `punctur`, `arria` and `fpga` appear **nowhere** in the
module. The stage's framing — "Arria 10 subband puncturing mask registers and tone-nulling ioctl
handlers" — has no lexical anchor here at all.

## 2. The three vocabulary traps, with context

**`subband` is OFDMA.** Every occurrence sits in one log format string:

```
%s(%d): ofdma_en:%d, ofdma_subband_type:%d, ofdma_start:%d, ofdma_len:%d
```

`ofdma_subband_type` alone accounts for **6** of the 17 hits. This is OFDMA resource-unit
allocation, **not** an FPGA puncturing mask.

**`mask` is interrupt masking.** Both hits read `GEM queue intr mask` — the GEM (Gigabit Ethernet
MAC) interrupt mask, not a spectral mask.

**`null` is null-CPE scheduling.** All 11 hits read:

```
null cpe %u qid %u sym %d last_cpe_null %u
```

That is a scheduler diagnostic about a CPE with no data, **not** tone nulling.

**`REFUTED`**: none of the three tokens supports the stage's reading. This is the same failure mode
as Stage 387A's dense command array: a token that matches is not a token that means.

## 3. Where the fabric control actually lives

Stage 376A already established the answer, and this stage cross-references it rather than
re-deriving it:

| Property | Value |
| :--- | :--- |
| FPGA mailbox symbols | **195** |
| architecture | amesoc3 dual-core ARMv7 HPS + Arria-class fabric (`air_fpga`) |
| partition blobs inspected | 4+ |
| sample symbol | `AME_EAB_EnableDMAMonitor` (`STT_FUNC`, `0x12d078`) |

**`CONFIRMED`**: the FPGA is controlled through a **mailbox symbol family** in the `ame_*` modules,
not through subband mask registers and not through `eab_driver.ko`.

That reframes the stage's question usefully: if subband puncturing exists, it would be a message
over that mailbox, and the 195 symbols are where to look — not a mask register.

## 4. What is established

| Claim | Status |
| :--- | :--- |
| `eab_driver.ko` exists | **REFUTED** (0 files, 5th confirmation) |
| `libltu` exists | **REFUTED** (0 files) |
| an `af-ltu` firmware tree exists | **REFUTED** (0 dirs; 36 configs only) |
| an FPGA bitstream exists | **REFUTED** (0 `.rbf`, 0 `.sof`) |
| the 36 `system-af-ltu*.cfg` carry subband/fpga keys | **REFUTED** (0 / 0) |
| the EAB surface is real in `ame_core.ko` | **CONFIRMED** (359 tokens, 23 symbols) |
| `subband` means a puncturing mask | **REFUTED** (`ofdma_subband_type`) |
| `mask` means a spectral/puncturing mask | **REFUTED** (`GEM queue intr mask`) |
| `null` means tone nulling | **REFUTED** (`null cpe … last_cpe_null`) |
| the fabric is driven by a mailbox symbol family | **CONFIRMED** (Stage 376A, 195 symbols) |
| the subband mask register values | **UNKNOWN / not recoverable** |

## 5. Why no register was recovered

A mask register needs three things, and the corpus supplies none:

1. a **bitstream** to read the register map from — **0 files**;
2. a **driver** that writes it — `eab_driver.ko` **absent**;
3. a **symbol or string** naming it — `punctur`, `tone`, `notch`, `arria`, `fpga` all **0**.

`subband_mask_registers_recovered = 0` and `tone_null_ioctl_recovered = 0` are therefore the
correct state of the evidence, not a shortfall of effort.

## 6. Gaps

- **`UNKNOWN`** — whether the Arria-class fabric supports subband puncturing at all.
- **`UNKNOWN`** — the mailbox message set behind the 195 symbols; only the names are known.
- **`UNKNOWN`** — what `ofdma_subband_type` values are legal, and how they map to resource units.
- **`UNKNOWN`** — whether `AME_EAB_EnableDMAMonitor` and peers expose any mask write.
- **Blocked** — any bitstream-level answer, until an `.rbf`/`.sof` exists in the corpus.
- **Not attempted** — dynamic validation, JTAG/fabric access.
