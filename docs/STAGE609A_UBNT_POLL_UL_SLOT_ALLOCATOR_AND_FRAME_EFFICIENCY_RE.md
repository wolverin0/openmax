<!-- doc-head: STAGE609A_UBNT_POLL_UL_SLOT_ALLOCATOR_AND_FRAME_EFFICIENCY_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 609A — `ubnt_poll_host.ko` UL Slot Time Allocator (`0x00d244..0x00d950`) & `150 us` vs `Flexible` Frame Efficiency Dissection (`WA` & `XC`)

## 1. Classification & Attribution
- **Claim Classification**: `CONFIRMED`
- **Layer Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` on `WA` `AR9342` + `XC` `QCA9880` `tx_bd_ExchangeHandler`)
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.
- **Receipt**: [`stage609a_ubnt_poll_ul_slot_allocator_and_frame_efficiency_re.json`](../artifacts/autoresearch/stage609a_ubnt_poll_ul_slot_allocator_and_frame_efficiency_re.json)
- **Dissector Script**: [`dissect_stage609a_ubnt_poll_ul_slot_allocator_and_frame_efficiency_re.py`](../tools/re/dissect_stage609a_ubnt_poll_ul_slot_allocator_and_frame_efficiency_re.py)

## 2. Binary Dissection of `ubnt_poll_host_init_ptmp_netconf` (`0x0000d244..0x0000d950`)
Static MIPS32 MSB disassembly of `ubnt_poll_host.ko` (`v8.7.11`) on `WA` (`Panel2-Guarida .82` and `Panel3-Guarida .83`) proves the exact fixed-frame duration and UL poll cap math inside `ubnt_poll_host_init_ptmp_netconf`:

1. **Bitfield Extraction (`0x00d764..0x00d840`)**:
   - `0x00d764: lhu $v1, 0x10c($s0)` loads the packed `netconf` control word.
   - `0x00d76c: ext $a3, $v1, 9, 7` extracts `ff_dl_alloc` (bits `9..15`, 7-bit integer: `25`, `33`, `50`, `67`, or `75`).
   - `0x00d840: ext $a2, $v1, 4, 4` extracts `ff_cbp_slots` (bits `4..7`, equal to `3` in Fixed Frame mode on `.82`).
2. **Gross DL/UL Split Branches (`0x00d768..0x00d834`)**:
   - `33%` (`0x21`): `0x00d7c4` multiplies `ff_frame_dur * 33` by fixed-point reciprocal `0x51eb851f >> 37` (`÷ 100`).
   - `67%` (`0x43`): `0x00d7e8` multiplies `ff_frame_dur * 67` by `0x51eb851f >> 37` (`6,700 us` for `10,000 us` frame; `5,360 us` for `8,000 us` frame).
   - `25%` (`0x19`): `0x00d7b8: srl $a1, $a0, 2` (`frame_dur >> 2`).
   - `75%` (`0x4b`): `0x00d820` computes `(frame_dur >> 2) + (frame_dur >> 1)` (`7,500 us` for `10,000 us` frame; `6,000 us` for `8,000 us` frame).
   - `50%` (default): `0x00d798 / 0x00d7b4: srl $a1, $a0, 1` (`5,000 us` for `10,000 us` frame).
3. **Gap Subtractions (`0x00d848..0x00d884`)**:
   - `down_dur` (`0xa6($s0)`): `0x00d850: subu $a1, gross_dl, down_dur_gap` (`0x40($v0)` = `120 us` on `.82`) $\rightarrow$ `5000 - 120 = 4,880 us`.
   - `cbp_dur` (`0xaa($s0)`): `0x00d864: mul $t0, ff_cbp_slots, cbp_dur_slot` (`0x3e($v0)` = `60 us` on `.82`) $\rightarrow$ `3 * 60 = 180 us`.
   - `up_dur` (`0xa8($s0)`): `0x00d87c..0x00d880: gross_ul - up_dur_gap (450 us) - cbp_dur (180 us)` $\rightarrow$ `5000 - 450 - 180 = 4,370 us`.
4. **Hard UL Max Polled Stations Cap (`0xfe($s0)` at `0x00d888..0x00d924`)**:
   - `0x00d888: sltiu $t0, $a1, 0x1f41` tests `up_dur <= 8,000 us`:
     - If `up_dur > 8,000 us`: `0x00d894: addiu $a0, $zero, 6; sb $a0, 0xfe($s0)` (`6` polled STAs/frame, active on `.83` Flexible where `up_dur = 30,000 us`).
     - If `4,001 <= up_dur <= 8,000 us` (`0x00d90c: sltiu $a1, $a1, 0xfa1 == 0`): `0x00d918: addiu $v0, $zero, 5; sb $v0, 0xfe($s0)` (`5` polled STAs/frame, active on `.82` `10ms 50/50` where `up_dur = 4,370 us`).
     - If `up_dur <= 4,000 us`: `0x00d920: addiu $v0, $zero, 4; sb $v0, 0xfe($s0)` (`4` polled STAs/frame, active on `10ms 67/33` and `75/25`).

## 3. Live `/proc/sys/dev/uph_wifi0/netconf` & Frame Efficiency Matrix
| Config Profile | `ff_frame_dur` (`us`) | `ff_dl_alloc` (`%`) | `down_dur` (`us`) | `cbp_dur` (`us`) | `up_dur` (`us`) | Max UL STAs (`0xfe`) | UL `slot_guard` Total (`us`) | Net UL Payload (`us`) | Useful Frame Efficiency (`%`) | DL Airtime Gain vs `.82` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Fixed_10ms_50_50` (`.82` Live)** | `10,000` | `50%` | `4,880` | `180` | `4,370` | `5` | `750` (`5×150`) | `3,620` | `85.00%` | `0.00%` (baseline) |
| **`Fixed_10ms_67_33` (Candidate)** | `10,000` | `67%` | `6,580` | `180` | `2,670` | `4` | `600` (`4×150`) | `2,070` | `86.50%` | **`+34.84%`** |
| **`Fixed_10ms_75_25` (Candidate)** | `10,000` | `75%` | `7,380` | `180` | `1,870` | `4` | `600` (`4×150`) | `1,270` | `86.50%` | **`+51.23%`** |
| **`Fixed_8ms_67_33` (Candidate)** | `8,000` | `67%` | `5,240` | `180` | `2,010` | `4` | `600` (`4×150`) | `1,410` | `83.12%` | **`+7.38%`** |
| **`Fixed_8ms_75_25` (Candidate)** | `8,000` | `75%` | `5,880` | `180` | `1,370` | `4` | `600` (`4×150`) | `770` | `83.12%` | **`+20.49%`** |

## 4. Key Architectural Implications (`FMX-DISC-51`)
1. **Why `.82` (`10ms 50/50`) Starves Downlink Under 22-CPE Load**:
   - On `.82`, `down_dur = 4,880 us` (`48.8%` of the frame) while `up_dur = 4,370 us` polls up to `5` stations per frame (`750 us` burned purely in `slot_guard = 150 us` + `750 us` in fixed frame gaps = `1,500 us` total overhead per `10 ms` frame).
2. **Why `10ms 67/33` Dominates `8ms 67/33` and `10ms 75/25` for 22-CPE Mixed Traffic**:
   - `10ms 67/33` boosts net DL airtime (`down_dur`) from `4,880 us` to **`6,580 us` (`+34.84%`)**, trims UL poll cap `0xfe($s0)` from `5` to `4` STAs/frame (saving `150 us` of `slot_guard` waste every frame), and preserves **`2,070 us` (`20.7%`)** of net UL payload airtime—whereas `10ms 75/25` leaves only `1,270 us` (`12.7%`) of net UL payload after subtracting `630 us` fixed UL gaps + `600 us` `slot_guard`.
