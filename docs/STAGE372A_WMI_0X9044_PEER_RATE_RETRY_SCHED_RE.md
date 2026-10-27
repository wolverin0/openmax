<!-- doc-head: STAGE372A_WMI_0X9044_PEER_RATE_RETRY_SCHED_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 372A — `WMI_PEER_RATE_RETRY_SCHED_CMDID` (0x9044) and the 4-series retry table

- **Receipt**: [`artifacts/autoresearch/stage372a_wmi_0x9044_peer_rate_retry_sched_re.json`](../artifacts/autoresearch/stage372a_wmi_0x9044_peer_rate_retry_sched_re.json)
- **Tool**: [`tools/re/wmi_0x9044_peer_rate_retry_sched_re.py`](../tools/re/wmi_0x9044_peer_rate_retry_sched_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. The command name exists, and it is spelled out in full

The first probe looked for `PEER_RATE_RETRY`. One hit in each AC `umac.ko`, in `.rodata.str1.4`
at `0x01683c`, and the surrounding bytes give the **complete** name:

```
...WMI_AP_PS_PEER_UAPSD_COEX_CMDID . WMI_PEER_RATE_RETRY_SCHED_CMDID . WMI_WLAN_PROFILE_TRIGGER_CMDID...
```

**`CONFIRMED`**: `WMI_PEER_RATE_RETRY_SCHED_CMDID` is a real string in the UI-command name
table of `umac.ko` (ordinal **7485** of **8295** NUL-separated strings in that section). That is
the exact identifier the stage names.

`ubnt_poll_host.ko` has **zero** WMI surface: no `PEER_RATE_RETRY`, no field names, nothing. The
`uph` TDMA module does not carry WMI command handling, which is consistent with its role as the
polling/TDMA scheduler rather than the host-command transport.

## 1. The numeric id is a table literal, not an instruction immediate

Two independent searches, and they disagree in a way that matters:

| Search | Result |
| :--- | :--- |
| `lui rX,0x0009` + `ori rX,rX,0x0044` in `.text` | **0 sites** |
| raw 32-bit word `0x00009044`, summed over the four modules | **162 hits** |
| — of which offset ≡ 0 (mod 4) | **2** (one per `umac.ko`) |
| — of which offset ≠ 0 (mod 4) | **160** (11 per `umac.ko`, 69 per `ubnt_poll_host.ko`) |

**`REFUTED`**: the id is *not* materialised by an instruction pair. The compiler never builds
`0x9044` at runtime.

**`REFUTED`**: the 160 unaligned hits are not ids. `0x00009044` decodes as `sll $s2,$zero,1`, and
at an offset that is not a multiple of four the four bytes straddle two instructions. They are
coincidences of adjacent code, and treating them as command ids would be exactly the kind of
false positive this project exists to avoid.

Note that `ubnt_poll_host.ko` carries **69** of them per image and **zero** aligned, so on raw
word-count alone it would look like the busiest WMI module of all four. It is the opposite: it has
no WMI surface. The alignment split is the only thing that separates signal from noise here.

## 2. The two aligned hits are a dense command-slot array

Both aligned literals land inside an `[id][trailing]` run, 8 bytes per entry:

| Image | Run start | Entries captured | Trailing word |
| :--- | :--- | :-: | :--- |
| `WA.v8.7.25` | `0x239f70` | **32** (cap) | `0x00000102` |
| `XC.v8.7.25` | `0x23a890` | **32** (cap) | `0x00000102` |

The entries are not arbitrary:

```
0x239f70  0x9000  0x00000102
0x239f78  0x9004  0x00000102
0x239f80  0x9008  0x00000102
...
0x239ff0  0x9040  0x00000102
0x239ff8  0x9044  0x00000102   <-- the command
0x23a000  0x9048  0x00000102
...
```

**`CONFIRMED`**: the stride is exactly 4 in the id field and exactly 8 bytes per entry, starting
at `0x9000`. This is a **dense enumeration of command slots**, not a sparse dispatch table with
per-command payloads. `0x9044` occupies **index 17** (`(0x9044 - 0x9000) / 4`).

**`CONFIRMED`**: the trailing word is `0x00000102` for every captured entry across 32+ slots.

**Not claimed.** Because the trailing word never varies, it cannot be a per-command length. It is
a common attribute — a group id, a service class, or a fixed flag pair — and this stage does not
determine which. No handler pointer was found adjacent to the run, so **dispatch is unproven**.

## 3. The retry-series field names are present; `series_bw` is not

| Token | `umac.ko` hits | `ubnt_poll_host.ko` |
| :--- | :-: | :-: |
| `LDPC` | **5** | 0 |
| `STBC` | **9** | 0 |
| `SGI` | **3** | 0 |
| `txchainmask` | **2** | 0 |
| `2x2` | **2** | 0 |
| `CDD` | **7** | 0 |
| **`series_bw`** | **0** | 0 |
| `retry_sched` | 0 | 0 |
| `peer_rate_retry` (lower-case) | 0 | 0 |

**`CONFIRMED`**: five of the six schema tokens the stage names are real strings in `umac.ko`, and
`series_bw` is genuinely absent.

**This does not recover the table.** A field name appearing somewhere in a 2.3 MB module says
nothing about the order, width or packing of the struct that carries it. The stage asked for a
4-series table with per-series `series_bw`, `LDPC`, `STBC`, `SGI` and a `txchainmask` fallback of
2x2 VHT to 1x2 STBC/CDD on retry #2. **None of that structure is reconstructed here**, and
`retry_table_recovered = 0` in the receipt says so.

Note the inversion of the working hypothesis: before running, the expectation was that all five
field names would count zero. Four of five count non-zero. Running the tool rather than trusting
the prediction is what caught it.

## 4. What the stage establishes vs. what it does not

| Claim | Status |
| :--- | :--- |
| `WMI_PEER_RATE_RETRY_SCHED_CMDID` is a real named command in `umac.ko` | **CONFIRMED** |
| id `0x9044` exists as an aligned literal at index 17 of a slot array | **CONFIRMED** |
| the slot array's trailing word is a common attribute, not a length | **CONFIRMED** (it never varies) |
| the id is built by `lui`+`ori` at runtime | **REFUTED** (0 sites) |
| the 160 unaligned hits are command ids | **REFUTED** (they straddle instructions) |
| `ubnt_poll_host.ko` carries WMI command handling | **REFUTED** (zero surface) |
| a handler is bound to `0x9044` | **UNKNOWN** |
| the 4-series retry table with `txchainmask` fallback | **UNKNOWN / not recovered** |

## 5. Gaps

- **`UNKNOWN`** — which code path consumes slot index 17, and what the trailing `0x102` means.
- **`UNKNOWN`** — the struct layout of `WMI_PEER_RATE_RETRY_SCHED_CMDID`: series order, widths,
  packing.
- **`UNKNOWN`** — whether the 2x2-VHT-to-1x2-STBC/CDD fallback on retry #2 exists at all. The
  tokens `2x2` and `CDD` are present as strings, but no code was traced from the command to a
  rate-selection branch.
- **`CONFIRMED ABSENT`** — `series_bw` and any lower-case spelling.
- **Known limit** — a command name, an id and a field-name vocabulary are three separate facts.
  Together they still do not make a schema.
- **Not attempted** — dynamic validation.
