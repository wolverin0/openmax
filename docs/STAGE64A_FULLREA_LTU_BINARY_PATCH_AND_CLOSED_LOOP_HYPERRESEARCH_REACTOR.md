<!-- doc-head: STAGE64A_FULLREA_LTU_BINARY_PATCH_AND_CLOSED_LOOP_HYPERRESEARCH_REACTOR.md preserved document content -->
<!-- /doc-head -->



# Stage 64A — `/fullrea` LTU Binary Patcher & Closed-Loop `HYPERRESEARCH V8` + `scholar-mcp` (`jev-1.14.0`) Reactor

- **Task ID**: `T-S64A-FULLREA-GHIDRA-KUNA-LTU-BINARY-PATCH-AND-CLOSED-LOOP-HYPERRESEARCH-REACTOR`
- **Status**: `CONFIRMED`
- **Safety Boundary**: `CONFIRMED` — 100% offline `/fullrea` (`REA MCP` + `fullrea_helper.py` + ARM32 relocation-aware decoder) + live `scholar-mcp` (`jev-1.14.0`) + `HYPERRESEARCH` vault (`0` live radio SSH sessions).
- **Primary Deliverables**:
  - Surgical Patcher: [`tools/ltu/patch_ltu_ame_core_binary.py`](../tools/ltu/patch_ltu_ame_core_binary.py)
  - Closed-Loop Reactor: [`tools/research/closed_loop_research_reactor.py`](../tools/research/closed_loop_research_reactor.py)
  - Stage 64A Receipt: [`artifacts/autoresearch/stage64a_fullrea_ltu_patch_and_reactor_20261026.json`](../artifacts/autoresearch/stage64a_fullrea_ltu_patch_and_reactor_20261026.json)
  - `HYPERRESEARCH` Scholar Vault: [`artifacts/hyperresearch_vault/stage64a_scholar_jev_verified_papers_20261026.json`](../artifacts/hyperresearch_vault/stage64a_scholar_jev_verified_papers_20261026.json)
  - Verification Suite: [`tests/test_stage64a_fullrea_ltu_patch_and_reactor.py`](../tests/test_stage64a_fullrea_ltu_patch_and_reactor.py)

---

## 1. Mission 1 — `/fullrea` Binary Reverse Engineering & Surgical `.ko` Patching (`ame_core.ko` & `ame_dev.ko`)

### 1.1 `REA MCP` Entropy & Adversarial String Audit
| Binary (`AF-LTU v2.4.2`) | Size (B) | Original SHA-256 | `REA MCP` Evidence ID | Entropy | Adversarial Strings (`arXiv:2605.30667`) |
| :--- | ---: | :--- | :--- | ---: | ---: |
| `afltu_2.4.2/ame_core.ko` (CPE) | `3,282,052` | `fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2` | `ev_05400f9f3764695ae865c79d43bbd1f0c1cf9d003f5f9e39e3e2c5e51c808247` | `6.1170` | `0 / 7,513` (`CONFIRMED`) |
| `aflturocket_2.4.2/ame_core.ko` (AP) | `3,318,764` | `a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af` | `ev_05400f9f3764695ae865c79d43bbd1f0c1cf9d003f5f9e39e3e2c5e51c808247` | `6.1182` | `0 / 7,584` (`CONFIRMED`) |
| `afltu_2.4.2/ame_dev.ko` (CPE/AP) | `298,760` | `912a7c1923aad381ac38ae922b78f69888cec0bd1558c09abf2de68657c8b955` | `ev_7ab7c16f41790531cfd0c2cb817a6355e3efd52e557854aa1bf198cc77607839` | `5.7218` | `0 / 1,113` (`CONFIRMED`) |

### 1.2 Four Exact Instruction & Relocation Discoveries (`CONFIRMED`, Attribution: `proprietary airMAX/LTU module`)

1. **Why `ame_bbp_set_autoMcsCeiling` Resets `adj_mcs` to `0x20` (`32` = Auto MCS)**:
   - At `.text` `0x1919b8` (`afltu_2.4.2`) / `0x196af0` (`aflturocket_2.4.2`), size `36` bytes:
     - `+4..+8`: `movw/movt r3, system_config` (`[REL:system_config+2492844 sh=34]`)
     - `+12`: `strb r0, [r3, #0x174]` (writes `autoMcsCeiling` to `system_config + 0x174`)
     - `+16`: `bl mcs_ceiling_toggle_txpwr` (`[REL:mcs_ceiling_toggle_txpwr+225056 sh=1]`)
     - **`+20`: `mov r0, #0x20` (`20 00 a0 e3`, `rel=null`)**
     - **`+24`: `bl ame_bbp_set_Param_mcs` (`[REL:ame_bbp_set_Param_mcs+1635600 sh=1]`)**
     - `+28`: `mov r0, #0` (`rel=null`)
   - Calling `ame_bbp_set_Param_mcs(0x20)` restarts `autoMCS_start` and overwrites `system_config + 0x121` (`adj_mcs`) with `0x20` (`32`).
   - Similarly, `cpeFsmStop` (`.text` `0x4d870`) calls `ame_bbp_set_Param_mcs(0x20)` at `+780` (`0x4db7c`) on link drop so re-association starts in Auto-MCS mode.
   - **Surgical Patch (`0` `.rel.text` overlaps)**: Replacing `+20` (`mov r0, #0x20`, `20 00 a0 e3`, where `rel=null`) with `b +8` (`00 00 00 ea`) branches directly to `+28` (`mov r0, #0; pop {r3, pc}`), skipping `+24` without touching the `R_ARM_CALL` relocation at `+24`.

2. **Why Writing `frame_len` Clobbers `duty_cycle` in `ame_dev.ko` (`g_core_hooks` Offset Bug)**:
   - In `ame_core.ko`, `.rel.data` proves the `g_core_hooks` function pointer table (base `.data + 0x544` in `afltu_2.4.2`) maps:
     - `+0x54` (`.data` `0x598`): `ame_bbp_set_duty_cycle` (`0x191990`)
     - `+0x58` (`.data` `0x59c`): `ame_bbp_get_duty_cycle` (`0x18ae40`)
     - **`+0x5c` (`.data` `0x5a0`): `ame_bbp_set_frame_len` (`0x1919a4`)**
     - `+0x60` (`.data` `0x5a4`): `ame_bbp_get_frame_len` (`0x18ba64`)
     - `+0x68` (`.data` `0x5ac`): `ame_bbp_set_autoMcsCeiling` (`0x1919b8`)
     - `+0x90` (`.data` `0x5d4`): `ame_core_set_maxBD` (`0x2e80`)
   - In `ame_dev.ko`, **both** `duty_cycle_store` (`0x12380`, at `+48` `0x123b0`) **and** `frame_len_store` (`0x1233c`, at `+48` `0x1236c`) execute `ldr r3, [r2, #84 (0x54)]` (`54 30 92 e5`)!
   - **Surgical Patch (`0` `.rel.text` overlaps)**: Patching `frame_len_store + 48` (`0x1236c`, `rel=null`) from `54 30 92 e5` (`#0x54`) to `5c 30 92 e5` (`#0x5c`) routes `/sys/class/ame/ame_ctrl_dev/frame_len` to `ame_bbp_set_frame_len`.

3. **LDPC `4096-QAM` (`12x`) Thresholds (`startThrd_4096` / `stayThrd_4096`) & `table_ptpPwrRange` (`60/80/100 MHz`)**:
   - In `.rodata` (`0xd4c0`/`0xd4c4` in `afltu_2.4.2`; `0xd5dc`/`0xd5e0` in `aflturocket_2.4.2`), `startThrd_4096` is patched from `97% -> 90%` and `stayThrd_4096` from `90% -> 82%`.
   - In `.data` (`0x1ec` in `afltu_2.4.2`; `0x1f8` in `aflturocket_2.4.2`), `table_ptpPwrRange` (`448` B) has `(0, 0)` at modulation index `6` (`4096-QAM` `12x`) for `60 MHz` (`bw=5`), `80 MHz` (`bw=6`), and `100 MHz` (`bw=7`). All `12` entries (`4` profiles $\times$ `3` bandwidths) are unlocked to `(20, 50)`, `(20, 55)`, `(20, 55)`, `(20, 52)` half-dBm (`10.0..25.0/27.5/26.0 dBm`).

4. **`AME_EAB_SetupQueues` (`0x12305c`) & `maxBD` (`.data + 0x0`)**:
   - `ame_core_get_maxBD` (`0x2e68`) and `ame_core_set_maxBD` (`0x2e80`) read/write `.LANCHOR4` (`.data + 0x0`), which defaults to `0x31` (`49` descriptors). Writing `0` to `/sys/class/ame/ame_ctrl_dev/adj_maxBD` unlocks full EAB hardware ring depth in `pAMEeab_Cb` (`.bss` `0x2b4dac`).

### 1.3 `fullrea_helper.py elf-verify-patch` Verification Summary
| Patched Module | Patched SHA-256 | Size Preserved | Diff Spans | `.rel.text` Overlaps |
| :--- | :--- | :---: | ---: | ---: |
| `ame_core_fmx_afltu_2.4.2.ko` | `42874aede3b2cdc1069d8cffb56ad2e2d05d20894a81f66595ae72fc477d1ee6` | `true` (`3,282,052` B) | `16` | **`0`** (`CONFIRMED`) |
| `ame_core_fmx_aflturocket_2.4.2.ko` | `e783d33c3a8da9ca44399734152d0f053b1f4d2ab5068fad36282a4e0fc0cda0` | `true` (`3,318,764` B) | `16` | **`0`** (`CONFIRMED`) |
| `ame_dev_fmx_afltu_2.4.2.ko` | `37eea1f7ee1b29bcdf59648191cabe729110377898413fb4a930a46c236daec2` | `true` (`298,760` B) | `1` | **`0`** (`CONFIRMED`) |
| `ame_dev_fmx_aflturocket_2.4.2.ko` | `37eea1f7ee1b29bcdf59648191cabe729110377898413fb4a930a46c236daec2` | `true` (`298,760` B) | `1` | **`0`** (`CONFIRMED`) |

---

## 2. Mission 2 — Closed-Loop `HYPERRESEARCH V8` + `scholar-mcp` (`jev-1.14.0`) Synthesis

### 2.1 Live `scholar-mcp` (`jev-1.14.0`) Verified Papers Ingested into Vault
| Paper ID | Title & Category | `jev-1.14.0` Status & Prob | Verified Span (`start_char..end_char`) | Synthesized Mutation |
| :--- | :--- | :---: | :--- | :--- |
| `2509.03855v7` | *Towards Deterministic Sub-0.5 us Response on Linux through Interrupt Isolation* (`cs.OS`) | `supported` (`0.99`) | `Abstract [0..165]`: *"Interrupt handling introduces arbitrary latencies in an OS, which makes deterministic response almost impossible to achieve on traditional systems such as Linux."* | **`M36`** (`IRQ 33` `ath-spectral-filter` `1,640 Hz` GPIO storm mask + deterministic PCIe NAPI/BQL) |
| `2608.01555v1` | *Sensitivity-driven Adaptive Contention Window Optimization for IEEE 802.11 based V2I Networks* (`cs.NI`) | `supported` (`0.88`) | `Abstract [790..1135]`: *"Compared against standard binary exponential backoff (BEB)... achieves up to 50.8% higher goodput, 66% higher system utility, and 26% lower delay..."* | **`M37`** (2-node PtP WMM EDCA `CWmin=1/3, CWmax=3/7` + Stage 55A Champion v19 BQL `hold_time=800ms`) |
| `0711.1273v1` | *Practical Resource Allocation Algorithms for QoS in OFDMA-based Wireless Systems* (`cs.NI`) | `supported` (`0.99`) | `Abstract [255..413]`: *"Each class is characterized by its own bit error rate threshold, minimum rate constraint (when elastic), and queuing delay constraint (when real-time)."* | **`LTU-M1`** (Surgical `ame_core_fmx.ko` + `ame_dev_fmx.ko` `4096-QAM` `90%/82%` LDPC hysteresis + `adj_maxBD=0`) |
