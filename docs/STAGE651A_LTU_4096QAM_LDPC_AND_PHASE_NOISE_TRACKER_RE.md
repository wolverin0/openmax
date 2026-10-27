<!-- doc-head: STAGE651A_LTU_4096QAM_LDPC_AND_PHASE_NOISE_TRACKER_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 651A — LTU 4096-QAM (`12x`) LDPC & Phase-Noise Tracker Dissection

- **Status**: `CONFIRMED` (100% offline static ELF32 ARM dissection across `afltu_2.4.2` & `aflturocket_2.4.2`; `live_devices_touched = False`)
- **Attribution**: `proprietary airMAX/LTU module` (`ame_core.ko` + `ame_dev.ko`) & `hardware` (`AF-LTU` Beetle + `ame_ASIC0`)
- **Tool**: [`dissect_stage651a_ltu_4096qam_ldpc_and_phase_noise_tracker_re.py`](../tools/re/dissect_stage651a_ltu_4096qam_ldpc_and_phase_noise_tracker_re.py)
- **Artifact**: [`stage651a_ltu_4096qam_ldpc_and_phase_noise_tracker_re.json`](../artifacts/autoresearch/stage651a_ltu_4096qam_ldpc_and_phase_noise_tracker_re.json)

## 1. Rate Tables & `10x` (`1024-QAM`) / `12x` (`4096-QAM`) Promotion Hysteresis
In `autoMCS_get_rate_table` (`0x151194` in `afltu_2.4.2`, `0x156098` in `aflturocket_2.4.2`, `264` bytes), `ame_core.ko` selects between three `.rodata` `uint16_t` rate tables where the upper byte indicates `MIMO` (`0x00` = `1x1 SISO`, `0x01` = `2x2 MIMO`) and the lower byte encodes the constellation:
- `autoMcsAllSisoTbl` (`.rodata+0x00d25c`, `10` bytes): `[0x0007, 0x000b, 0x000f, 0x0013, 0x0017]` (`QPSK` `2x` through `1024-QAM` `10x`; caps SISO below `4096-QAM`).
- `autoMcsUseSisoTbl` (`.rodata+0x00d268`, `14` bytes): `[0x0007, 0x000b, 0x000f, 0x010f, 0x0113, 0x0117, 0x011f]`.
- `autoMcsOthersTbl` (`.rodata+0x00d278`, `14` bytes): `[0x0007, 0x0107, 0x010b, 0x010f, 0x0113, 0x0117, 0x011f]`, where `0x0117` is `2x2 MIMO 1024-QAM` (`10x`) and `0x011f` is `2x2 MIMO 4096-QAM` (`12x`).

| Symbol | Section / Offset (`afltu_2.4.2`) | Default Value | Role in `autoMCS_step` / `autoMCS_updateDL` / `autoMCS_updateUL` |
| :--- | :--- | :---: | :--- |
| `mcsUpThrd_lowqam` | `.rodata+0x00d4ac` | `95` (`95%`) | Clean codeword/ACK ratio required to step up across `QPSK..64-QAM` |
| `mcsUpThrd_256` | `.rodata+0x00d4b0` | `96` (`96%`) | Clean codeword/ACK ratio required to step up from `256-QAM` (`8x`) to `1024-QAM` (`10x`) |
| `mcsUpThrd_1024` | `.rodata+0x00d4b4` | `93` (`93%`) | Baseline `1024-QAM` (`10x`) stability gate (`cont1024Threshold = 1` in `.data+0x0012d4`) |
| `startThrd_4096` | `.rodata+0x00d4c0` | `97` (`97%`) | Entry hysteresis gate to promote from `1024-QAM` (`10x`) into `4096-QAM` (`12x` `0x011f`) |
| `stayThrd_4096` | `.rodata+0x00d4c4` | `90` (`90%`) | Retention gate to remain in `4096-QAM` (`12x`) before stepping back to `1024-QAM` (`10x`) |
| `ra_offset_table` | `.data+0x0012c0` | `[0, 9, 18, 25, 30]` | Rate-adaptation CINR/backoff offsets (dB $\times 1$) across modulation tiers |

## 2. EVM-to-MCS Mapping & Hardware EVM Registers (`rxTopB`)
- `ame_bbp_op_evm_mcs_map` (`0x189148`, `88` bytes) negates `evm_db_x100` (`rsb r0, r4, #0`) and compares against three hardware immediate thresholds:
  - `abs_evm > 2230` (`EVM < -22.30 dB`, `e30038b6`): returns `0x1c` (`28`, high-order QAM ceiling for coarse EVM bootstrap).
  - `abs_evm > 1623` (`EVM < -16.23 dB`, `e3003657`): returns `0x1b` (`27`, `64-QAM`).
  - `abs_evm > 1000` (`EVM < -10.00 dB`, `e3500ffa`): returns `0x1a` (`26`, `16-QAM`), else `0x19` (`25`, `QPSK`).
- `bbp_mrx_evm_result` (`0x1751bc`, `184` bytes) reads `ame_ASIC0` `rxTopB` MMIO (`*(*pAMEbbp_Cb) + 0x00048000`):
  - `0x00048434` (`tst r4, #0x300000`, status bits `[21:20]`),
  - `0x0004843c` (Pilot EVM word for Chain 0/1),
  - `0x00048440` (`ldr r4, [ip, #0x440]`, Data EVM Chain 0),
  - `0x00048444` (Data EVM Chain 1).

## 3. `bbp_rf_set_super4096` & `rxTopB` LDPC Iteration Register
- **`bbp_rf_get_super4096` (`0x171550`, `52` B) & `bbp_rf_set_super4096` (`0x171584`, `348` B)**:
  - Reads RFIC registers `0x0351` (Chain 0) and `0x03d1` (Chain 1) via `bbp_rf_get_register`, checking bits `[10:8]` (`tst r0, #0x700`, `e3100c07`).
  - When enabled across both chains (`mode=3`), packs `0x0707` (`movw r4, #0x707`, `e3004707`) and invokes `ame_rfic_req(0x56, r4)` (`e3a00056`) to switch the RFIC fractional-N synthesizer and driver stages into ultra-low phase-noise / high-linearity mode for `4096-QAM` (`-41.4 dB` composite EVM).
- **`bbp_mrx_util_set_rxTopB_ldpcIteration` (`0x178594`, `92` B) & `get` (`0x1785f0`, `48` B)**:
  - Computes `r4 = *(*pAMEbbp_Cb) + 0x00048000` (`add r4, r4, #0x48000`, `e2844912`), executes `dmb sy` (`f57ff04f`), inserts the 5-bit LDPC iteration ceiling into bits `[8:4]` via `bfi r3, r0, #4, #5` (`e7c83210`, range `0..31` iterations), and flushes via `dsb st` (`f57ff04e`) + `outer_cache.sync`.
  - `ame_check_hw_NoLDPC` (`0x0044f4`, `28` B) inspects `*(uint8_t *)(system_config + 8)` bit `3` (`ubfx r0, r0, #3, #1`, `e7e001d0`).

## 4. Pilot Common Phase Error (`CPE`) & FOE/CIR Phase-Noise Tracker
- `ame_bbp_ap_pilot_eval_rt` (`0x18587c`, `128` B) checks `*(base + 0x001010b4) == 1`, calls `bbp_mrx_foe_cir_get_intp_result(cir_record)` (`0x180a80`), disables CIR capture (`ame_bbp_op_set_cir_record_enable(0)`), and when `ame_bbp_op_get_pilot_eval()` (`.data+0x2ef4`) is active, executes `ame_bbp_op_pilot_eval` (`0x18a9b4`, `1148` B) $\rightarrow$ `ame_bbp_op_interp_for_pilot_eval` (`0x18a86c`, `328` B) + `ame_bbp_op_nearestindex` (`0x18a810`) to interpolate phase error across scattered pilots (`ame_bbp_set_scatter_pilot` at `system_config + 0x124`, with `pb_cfo_apply=1` and `cfo_pass_threshold=400` at `.data+0x2d84..0x2d88`).
