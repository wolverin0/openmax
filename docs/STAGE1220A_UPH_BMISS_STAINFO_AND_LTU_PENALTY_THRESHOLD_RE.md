<!-- doc-head: Stage 1220A — missing-poll timeout and 4096-QAM penalty thresholds settled from measured bytes (static only) -->
# Stage 1220A — `ubnt_poll_host` missing-poll deadline and `ame_core` 4096-QAM penalty threshold

Status: `CONFIRMED_STATIC_BINARY`. Scope: static only. No SSH, no live radio, no firmware write,
no network. Both contradictions are settled by decoded instructions and symbol-table values, not by
preferring one prose source over another.

Verifier: [`tools/re/uph_bmiss_stainfo_and_ltu_penalty_threshold_re_verifier.py`](../tools/re/uph_bmiss_stainfo_and_ltu_penalty_threshold_re_verifier.py)
Receipt: [`artifacts/verification/stage1220a_uph_bmiss_and_ltu_penalty_re.json`](../artifacts/verification/stage1220a_uph_bmiss_and_ltu_penalty_re.json)

| Input | Bytes | Type | SHA-256 |
| :--- | ---: | :--- | :--- |
| `ubnt_poll_host.ko` (`WA.v8.7.25`) | `189880` | ELF32 `ET_REL`, **big-endian**, MIPS | `bfc3f499a086766917fcbbf1a52d0fac496ad237ae1671c4e640cccdd122c2b5` |
| `ame_core.ko` (`afltu_2.4.2`, CPE) | `3282052` | ELF32 `ET_REL`, **little-endian**, ARM | `fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2` |
| `ame_core.ko` (`aflturocket_2.4.2`, AP) | `3318764` | ELF32 `ET_REL`, **little-endian**, ARM | `a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af` |

## 1. The two disputes

| Pair | Quantity | Claim A | Claim B |
| :--- | :--- | :--- | :--- |
| Stage 10 vs Stage 70A | missing-poll timeout | `~30 s` (`STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md:45`) | `1,800,000 ms` = `0x001b7740` (`STAGE70A_..._DISSECTION.md:99`) |
| Stage 12 vs Stage 249A | `4096-QAM` penalty threshold | `penaltyThreshold = 25` (`..._dfb5467f5c_002.md:139`) | `penaltyThreshold = 60` (`STAGE249A_...:20`) |

## 2. `ubnt_poll_host_sta_bmiss_ind` is an 8-byte thunk

`st_value` resolves from `.symtab` to `.text+0x167c`, `st_size = 8`, file offset `0x16bc`. Its whole body:

| Offset | Word | Meaning |
| :--- | :--- | :--- |
| `.text+0x167c` | `0x08000000` | `j <target>` (`R_MIPS_26`, reloc file offset `160632`) |
| `.text+0x1680` | `0x8c840004` | `lw $a0, 4($a0)` (delay slot) |

The relocation target is the undefined symbol `ieee80211_mlme_sta_bmiss_ind`. The function is therefore a
tail-call trampoline that reports a station miss into `mac80211`; it holds **no timer and no timeout**.
That single fact already removes Stage 70A's attribution of a "2000 jiffies (20 s)" watchdog to this symbol.

Its one caller sits at `.text+0x7800` (file offset `30784`, reloc file offset `168536`), which reproduces
the Stage 10 site `S1` exactly.

## 3. The timer chain in `ubnt_poll_host.ko`

| Element | `.text` offset | File offset | Evidence |
| :--- | ---: | ---: | :--- |
| `ubnt_poll_host_start_os_timer` | `0x1468` (size `228`) | `0x14a8` | `.symtab` |
| `init_timer_key` call | `0x14f0` | `0x1530` | `R_MIPS_26`, reloc `160520` |
| `jiffies` load (expires base) | `0x14f8` / `0x1500` | `0x1538` / `0x1540` | `R_MIPS_HI16` / `R_MIPS_LO16`, relocs `160528` / `160536` |
| **`add_timer` call** | **`0x151c`** | **`0x155c`** | `R_MIPS_26`, reloc `160560` |
| generic timer wrapper | `0xf90` | `0xfd0` | `timer->function` set to `.text+0xf90` at `0x1510` |
| **`mod_timer` call (re-arm)** | **`0x102c`** | **`0x106c`** | `R_MIPS_26`, reloc `160296` |
| `ubnt_poll_host_data_create` | `0x7170` (size `488`) | `0x71b0` | `.symtab` |

`start_os_timer(a0 = interval, a1 = callback, a2 = dev)` allocates `0x28` bytes, converts `a0` to a jiffies
delta, stores `timer->expires = jiffies + delta` at `0x1508`, sets `timer->function` and calls `add_timer`.
The wrapper at `.text+0xf90` invokes `callback(dev, &out)`; on return code `-1` it frees the timer
(`afree_private`), and on return code `2` it converts `out` with the same scaling and re-arms through
`mod_timer` at `0x102c`. That is a self-re-arming timer, not a one-shot.

### 3.1 Arming sites of `start_os_timer`

| Call site | Interval argument | Callback | Kind |
| :--- | ---: | ---: | :--- |
| `.text+0x72c8` (inside `data_create`) | `0x000f4240` = `1,000,000` | `.text+0x7bd8` | immediate (`lui 0xf` @`0x72b4` + `addiu 0x4240` @`0x72c0`) |
| `.text+0x7768` | `0x000493e0` = `300,000` | `.text+0x62fc` | immediate |
| `.text+0x79cc` | runtime `dev+0x214`, default `0x9c40` = `40,000` | `.text+0x60d8` | `movz` override, not a constant |

Only the first site arms the callback that contains the panic path, so only that chain is relevant here.

### 3.2 The deadline constant

Inside the callback at `.text+0x7bd8`:

| Offset | Instruction | Effect |
| :--- | :--- | :--- |
| `0x7bdc` | `lw $v0, 0x288($a0)` | last-refresh stamp (set in `data_create` just before arming) |
| `0x7be0` | `lw $a1, (jiffies)` | now |
| `0x7be4` | `subu` | `elapsed_jiffies` |
| `0x7bf8` | `lui $a1, 0x01c9` | high half |
| `0x7bfc` | `sll $v0, $v0, 3` | part of `*125 << 3` = `*1000` |
| `0x7c00` | `ori $a1, $a1, 0xc768` | low half, value `0x01c9c768` |
| `0x7c04` | `sltu $v0, $v0, $a1` | `elapsed_us < 30,001,000` |
| `0x7c08` | `bnez $v0, 0x7c24` | below deadline, skip the panic |
| `0x7c1c` | `jal panic` | otherwise panic |

`0x01c9c768` = **30,001,000**. The guarded string resolves through `$LC7` (`.rodata.str1.4+0x13e0`,
file offset `0x20d8c`) to `ubnt-poll-host: #8e511820`, which matches Stage 70A's own description of the
panic site. The branch word `14400006` reproduces Stage 10's patch site byte for byte.

## 4. Unit derivation: why the constant is microseconds

No unit is assumed. `start_os_timer` converts the interval with `delta = mulhi(a0*1000, 0x431bde83) >> 18`,
and `0x431bde83 >> 18` is proved numerically by the verifier to be division by `10**6` (5014 samples,
0 mismatches, including `0xffffffff`). The conversion is therefore `usecs_to_jiffies`:
`(us * 1000) / 10**6 = us / 1000`.

The callback performs the inverse with `elapsed * 125 << 3`, i.e. `elapsed_jiffies * 1000`. Both directions
share the factor `1000`, which is `HZ = 1000`; the two conversions corroborate each other.

The load-bearing argument does not even need that inference. The deadline is expressed in the same unit as
the arming interval, so

```
deadline / arming_interval = 30,001,000 / 1,000,000 = 30.001
```

a ratio that is independent of `HZ`. With the arming interval at one second the deadline is `30.001 s`.

| Quantity | Value |
| :--- | ---: |
| `add_timer` interval immediate | `1,000,000` us (`0x000f4240` @ `.text+0x72c0`) |
| derived jiffies | `1000` (= 1 s at `HZ = 1000`) |
| deadline immediate | `30,001,000` us (`0x01c9c768` @ `.text+0x7bf8`) |
| `timeout_ms` | `30001` |
| `deadline / period` | `30.001` |

## 5. Resolution of the first dispute

`timeout_resolves_to = "30s"`. Stage 10 is confirmed; Stage 70A's `1,800,000 ms` is refuted.

Three independent measurements support this:

1. The only deadline comparison in the module is `0x01c9c768` = `30,001,000` us = `30.001 s`.
2. `1,800,000` (`0x001b7740`) occurs **zero** times as a stored word in this build, and zero times in the
   other three builds scanned (`XC.v8.7.25`, `XC.v8.7.4-cs`, `2XC.v8.7.11`).
3. `0x01c9c768` appears exactly **two** times per build, in all four builds:
   `0x7020`/`0x7bf8` (`8.7.25`) and `0x6d58`/`0x7930` (`8.7.4-cs`, `8.7.11`). A dead or version-specific
   constant would not survive that.

Stage 70A appears to have folded two different quantities into one row: the 1 s re-arm period of the
watchdog and the 30 s deadline it compares against. The `2000 jiffies (20 s)` figure it attributes to
`ubnt_poll_host_sta_bmiss_ind` is not in that thunk at all; the single `li 2000` (`addiu $rt, $zero, 0x7d0`)
in `.text` sits at `0x2f30`, outside both the thunk (`0x167c`) and its caller (`0x7800`), and what it gates
is `UNKNOWN`.

## 6. `ame_core.ko`: the 4096-QAM thresholds

A methodological correction first: `startThrd_4096`, `stayThrd_4096` and `penaltyThreshold` occur **once
each**, and each occurrence is inside `.strtab` (file offsets `0x230876`, `0x235b88`, `0x23aa88`). They are
symbol names, not `.rodata` strings, so the values must be read from the section each `st_value` points into.

| Symbol | Section | Section offset | File offset | Size | Value |
| :--- | :--- | ---: | ---: | ---: | ---: |
| `startThrd_4096` | `.rodata` | `0xd4c0` | `0x1a3f54` | 4 | **97** (`0x61`) |
| `stayThrd_4096` | `.rodata` | `0xd4c4` | `0x1a3f58` | 4 | **90** (`0x5a`) |
| `penaltyThreshold` | `.data` | `0x12d2` | `0x20077a` | 1 | **60** (`0x3c`) |

Adjacent fields of the same rate-adaptation vector, for context:

| Symbol | Section offset | Value |
| :--- | ---: | ---: |
| `ackAccuulateCnt` | `.data+0x12d1` | `25` |
| `cont1024Threshold` | `.data+0x12d4` | `1` |
| `penaltyTime` | `.data+0x12a8` | `4` |
| `smallTrafficTimer` | `.data+0x129e` | `1` |
| `mcsDownThreshold` | `.data+0x12e0` | `10` |
| `mcsUpThreshold` | `.data+0x12e4` | `7` |
| `avgWeight` | `.rodata+0xd4a2` | `20` |
| `mcsUpThrd_1024` | `.rodata+0xd4b4` | `93` |

AP build `aflturocket_2.4.2` agrees: `.rodata+0xd5dc` = `97`, `.rodata+0xd5e0` = `90`,
`.data+0x12ee` = `60`.

## 7. Resolution of the second dispute

`penaltyThreshold` resolves to **60**. Stage 249A is confirmed; Stage 12's `25` is refuted for this build.

The `25` is not invented. It is `ackAccuulateCnt` at `.data+0x12d1`, **one byte before** `penaltyThreshold`
at `.data+0x12d2`. Stage 12 also states `penaltyTime = 4`, `mcsUpThreshold = 7` and `mcsDownThreshold = 10`,
all of which measure correctly, so the vector was read with a one-field shift at this position rather than
fabricated wholesale.

On `startThrd_4096` and `stayThrd_4096` the two stages do not actually disagree: both say `97` and `90`, and
the binary returns `97` and `90`. Only `penaltyThreshold` required adjudication.

## 8. Cross-build corroboration

| Build | `0x01c9c768` sites | `1,800,000` words |
| :--- | :--- | ---: |
| `WA.v8.7.25` | `0x7020`, `0x7bf8` | 0 |
| `XC.v8.7.25` | `0x7020`, `0x7bf8` | 0 |
| `XC.v8.7.4-cs` | `0x6d58`, `0x7930` | 0 |
| `2XC.v8.7.11` | `0x6d58`, `0x7930` | 0 |

The `8.7.25` pair is byte-identical to `8.7.4-cs` in this respect; only the offsets drift with the build.

## 9. What remains open

- `HZ = 1000` is inferred from the paired `x1000` / `/1000` conversions, not read from a kernel config or
  `vmlinux`. The `30.001` ratio is `HZ`-independent, which is why the resolution does not rest on it.
- The deadline is tested once per 1 s expiry, so the first firing instant is quantised to roughly `31 s`.
  No runtime instant was measured.
- `dev+0x288` is read as the last-poll jiffies stamp because it is stored immediately before arming and
  subtracted in the callback. The struct layout is not documented in the binary, so the field's name is
  `INFERRED`.
- The `li 2000` at `.text+0x2f30` is unlocated semantically (`UNKNOWN`).
- `4096-QAM` thresholds are asserted for `afltu_2.4.2` and `aflturocket_2.4.2` only.
- Static evidence only: no claim about runtime behaviour, causality, or any live radio.

## 10. Reproduce

```powershell
python tools/re/uph_bmiss_stainfo_and_ltu_penalty_threshold_re_verifier.py --check-determinism
```

Two consecutive runs are byte-identical. Receipt SHA-256:
`eeef07fabe51af7d4639695c8da743d28e623806093f140ab92bb4113e74bfb2`. The payload is serialised through
`decase()` and contains no wall-clock, so regeneration is reproducible.
