<!-- doc-head: STAGE652A_XW_ATH_DEV_MIXED_MODE_TDMA_TRANSLATOR_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 652A — `XW` M5 `ath_dev.ko` + `ubnt_poll.ko` vs `WA`/`XC` Mixed-Mode TDMA Translator RE

- **Status**: `CONFIRMED` (100% offline static MIPS32 Big-Endian ELF32 dissection across `XW.v6.3.6`, `XW.v6.1.4`, `WA.v8.7.25`, and `XC.v8.7.25`; `live_devices_touched = False`)
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll.ko`, `ath_dev.ko`, `ubnt_poll_host.ko`)
- **Tool**: [`dissect_stage652a_xw_ath_dev_mixed_mode_tdma_translator_re.py`](../tools/re/dissect_stage652a_xw_ath_dev_mixed_mode_tdma_translator_re.py)
- **Artifact**: [`stage652a_xw_ath_dev_mixed_mode_tdma_translator_re.json`](../artifacts/autoresearch/stage652a_xw_ath_dev_mixed_mode_tdma_translator_re.json)

## 1. Architectural Discovery: Why `XW` `ubnt_poll.ko` Embeds `_11ac_compat_*`
On `airMAX AC` (`WA`/`XC`), the TDMA Contention-Free Period (`CFP`) / `TXOP` scheduler executes inside the `QCA988x` Xtensa target RAM (`vmlinux.bin`), leaving host `ubnt_poll_host.ko` (`358` symbols) as a lightweight IE parser/container proxy (`ubnt_poll_host_proto_insert_ie` / `parse_ie`).
Conversely, `airOS 6` `XW` (`QCA9558`/`AR9344` M5 `11n`) is a Direct-Attach AHB radio with no Xtensa offload processor. To allow an `M5` STA to associate with an `airMAX AC` AP in Mixed Mode (`AC AP + M5 STA`), Ubiquiti compiled **56+ `_11ac_compat_*`, `ubnt_poll_11ac_*`, and `hybrid` CFP/TXOP functions** directly into `XW` `ubnt_poll.ko` (`1,148` symbols in `XW.v6.3.6`):

| Function (`XW.v6.3.6` `ubnt_poll.ko`) | `.text` Offset / Size | Verified MIPS32 Instruction / Mechanism |
| :--- | :---: | :--- |
| `ubnt_poll_set_11ac_mode_authorized` | `0x019200` (`32` B) | Atomic `ll v1, 0x20(a0); ins v1, v0, 14, 1 (0x7c437384); sc v1, 0x20(a0)` sets bit `14` (`11ac_mode_authorized`) |
| `_11ac_compat_lmac_should_aggr` | `0x02cb34` (`92` B) | Checks bit `19` (`ext v0, v0, 19, 1`, `0x7c4204c0`) at `+0x98(a0)` and gates A-MPDU aggregation by TID/AC |
| `_11ac_compat_lmac_on_before_ppdu_tx` | `0x02cda8` (`920` B) | Checks bits `19` & `4` (`0x7c4204c0`, `0x7c420100`) at `+0x98(a0)` and deducts PPDU airtime (`+0x74`) from the `v8` `TXOP` budget |
| `ubnt_poll_hybrid_txop_evaluate` | `0x0368c8` (`148` B) | Computes remaining slot microseconds `(txop_limit_0x10c + guard_0x114) - (accum_0x110 + next_ppdu_0x74)` |
| `ubnt_poll_sta_sm_do_hybrid_cfp` | `0x03a5c8` (`144` B) | Atomic `ll v0, 0x98(a0); ins v0, zero, 1, 1 (0x7c020844); sc v0, 0x98(a0)` clears hybrid CFP active bit `1` upon slot expiry |
| `ubnt_poll_sta_recv_txop_info` | `0x0388b8` (`1168` B) | Parses dynamic `airMAX AC` (`v8`) `TXOP` grants on the `M5` STA |
| `ubnt_poll_sta_recv_ff_txop_info` | `0x038260` (`1624` B) | Parses Fixed-Frame (`FF`) `airMAX AC` `TXOP` grants on the `M5` STA |

## 2. `ath_pkt_duration` & `ath_pkt_duration_to_len` (`XW` `ath_dev.ko`)
When the `airMAX AC` AP grants a microsecond `TXOP` window (`txop_limit_0x10c`), the `XW` M5 STA translates between byte length and airtime microseconds via two functions in `ath_dev.ko`:
1. **`ath_pkt_duration` (`0x01a478`, `240` B)**:
   - Checks `IS_HT_RATE(rateCode)` (`seb t0, v1`, `0x7c034420`), computes `nsyms = ((pktlen * 8) + 21) / bits_per_symbol`, and converts symbols to microseconds via `nsyms * 4` (Long GI `4.0 us`) or `(nsyms * 18 + 4) / 5` (Short GI `3.6 us`, `li a1, 18` `0x24050012`; `li a2, 5` `0x24060005`).
   - Adds the **802.11n HT-mixed PLCP preamble**:
     $$\text{preamble}_{\text{HT-mixed}} = \left(9 + \left(\text{rateCode} \gg 3\right) \& \text{0xf}\right) \times 4\;\mu\text{s} = \begin{cases} 36\;\mu\text{s} & \text{1x1 SISO (MCS0..7)} \\ 40\;\mu\text{s} & \text{2x2 MIMO (MCS8..15)} \end{cases}$$
2. **`ath_pkt_duration_to_len` (`0x01cb48`, `196` B)**:
   - Performs the exact inverse for TDMA slot packing: subtracts the `36 us` / `40 us` HT-mixed preamble (`li a0, -9`, `0x2404fff7`), computes `nsyms = (rem_us * 5 - 4) / 18` (Short GI) or `rem_us / 4` (Long GI), and returns `(nsyms * bits_per_symbol) >> 3`.

## 3. Mixed-Mode Aggregation Ceilings (`_ht40_aggr_len` & `_ht20_aggr_len`)
In `XW` `ubnt_poll.ko` (`.rodata+0x001c38` & `.rodata+0x001c48`):
- `_ht40_aggr_len` = `[12, 60156, 22, 120240]` (caps `HT40` A-MPDUs at `12` or `22` subframes vs `26..32` subframes on `VHT`).
- `_ht20_aggr_len` = `[12, 19304, 20, 38600]` (caps `HT20` A-MPDUs at `12` or `20` subframes).
