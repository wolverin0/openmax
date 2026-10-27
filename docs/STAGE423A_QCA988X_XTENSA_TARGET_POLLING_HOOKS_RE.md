<!-- doc-head: STAGE423A_QCA988X_XTENSA_TARGET_POLLING_HOOKS_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 423A — the claimed 32 target polling hook pointers at `0x0040f688`

- **Receipt**: [`artifacts/autoresearch/stage423a_qca988x_xtensa_target_polling_hooks_re.json`](../artifacts/autoresearch/stage423a_qca988x_xtensa_target_polling_hooks_re.json)
- **Tool**: [`tools/re/build_stage423a_qca988x_xtensa_target_polling_hooks_re.py`](../tools/re/build_stage423a_qca988x_xtensa_target_polling_hooks_re.py)
- **Scope**: offline static. No firmware loaded, no radio contacted.

## 0. Neither named file exists

| Filename | Files in corpus |
| :--- | :-: |
| `firmware-2.bin` | **0** |
| `firmware-5.bin` | **0** |
| `firmware-*.bin` | **0** |

The only QCA988x container is `openwrt_qca988x_hw20_firmware_2_ct.bin`, **204,796 bytes**, version
`10.1-ct-8x-__fW-022-ecad3248`, 2 `SGMT` segments. That is what this stage parses.

**`REFUTED`**: the stage names two filenames that do not exist. Anything said about them would be
about a different file.

## 1. The address resolves — but only under one base

`0x0040f688` was tested against five candidate load bases, across both segments:

| Base | Segment 4 | Segment 3 |
| :--- | :-: | :-: |
| **`0x00400000`** | out of range | **inside, rel `0xf688`** |
| `0x00980000` (header, LE) | out | out |
| `0x00009800` (header, BE) | out | out |
| `0x00000000` | out | out |
| `0x00e00000` | out | out |

**`CONFIRMED`**: `0x0040f688` is exactly **DRAM base `0x00400000` + `0xf688`**, the QCA988x DRAM
base used by ath10k, and under that base it lands inside segment 3 at **file offset `0x0112e0`**.

That is a real result: the stage's address arithmetic is consistent with ath10k's memory map, even
though the `SGMT` header field reads `0x00980000`. **The true load base remains unresolved** — but
one candidate makes the claim addressable, and it is the candidate used here.

## 2. What is actually at `0x0040f688`

The 32 words, verbatim:

```
0x71a91f4a  0x400006f2  0x3f56c0ff  0x010682aa
0xa872049f  0x020692a9  0x1972049f  0x0306a2a9
...
```

| Property | Value |
| :--- | :-: |
| words read | **32** |
| distinct words | **32** |
| words inside the firmware range | **0** |
| aligned (4-byte) | **0** |

**`REFUTED`**: this is **not** a table of 32 function pointers. A pointer table would be 32
in-range, 4-aligned values; none of these are. The words read as **Xtensa instruction encodings**
(the `0x00`/`0x3f`/`0x40` high bytes and the repeated `...049f`/`...a2a9` suffixes are
characteristic of 16/24-bit Xtensa instruction packing, not addresses).

So the address is **code**, and the "32 hooks" are 32 instructions.

## 3. The scan: no 32-entry pointer table exists anywhere

Rather than assert absence from one address, both segments were scanned for runs of consecutive
4-aligned words pointing into `0x00400000..0x004303a1`:

| Metric | Value |
| :--- | :-: |
| runs of ≥ 8 pointers | **1** |
| runs of exactly **32** pointers | **0** |
| longest run | **9** words |
| where | segment 3, offset `0x001144` |

**`CONFIRMED`**: the longest pointer run in the entire firmware payload is **9 words**. There is
no 32-entry table of that shape, at `0x0040f688` or anywhere else.

`hook_table_recovered = 0`.

## 4. What would make target-assisted polling real

The stage's architecture — schedule ticks running inside Xtensa IRAM without host PCIe interrupts —
needs, at minimum:

1. a **table of entry points** the host can populate → **absent** (0 of 32, no 32-run);
2. a **doorbell or shared-memory slot** the host writes → not looked for here;
3. firmware code that **polls** that slot → not identified here.

Only (1) is refuted, and it is refuted hard. (2) and (3) remain open: a shared-memory polling
channel could exist without any pointer table, exactly as `uhp` does on the M5 line. This stage
does not claim target polling is impossible — it claims the **table address is wrong**.

## 5. What is established

| Claim | Status |
| :--- | :--- |
| `firmware-2.bin` / `firmware-5.bin` exist in the corpus | **REFUTED** (0 files) |
| `0x0040f688` is reachable under DRAM base `0x00400000` | **CONFIRMED** (file `0x0112e0`) |
| `0x0040f688` holds 32 function pointers | **REFUTED** (0 of 32 in range) |
| the bytes there are Xtensa code | **INFERRED** (0 pointers, instruction-shaped words) |
| a 32-entry pointer table exists elsewhere in the payload | **REFUTED** (0 runs of 32; best is 9) |
| target-assisted polling exists at all | **UNKNOWN** |

## 6. Gaps

- **`UNKNOWN`** — the real `SGMT` load base. Three of five candidates place the address outside
  the image; only `0x00400000` works, and that reading contradicts the header field.
- **`UNKNOWN`** — whether a host-populated schedule slot exists in firmware DRAM.
- **`UNKNOWN`** — what the 32 instructions at `0x0040f688` actually do; no Xtensa disassembly was
  performed.
- **`UNKNOWN`** — whether the 9-word pointer run at segment 3 `0x001144` is meaningful.
- **Known limit** — a wrong address is not proof of a wrong idea.
- **Not attempted** — Xtensa disassembly, dynamic validation.
