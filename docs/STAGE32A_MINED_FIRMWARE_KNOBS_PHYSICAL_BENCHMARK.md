<!-- doc-head: STAGE32A_MINED_FIRMWARE_KNOBS_PHYSICAL_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 32A: Physical Benchmark of Mined Firmware & Driver Knobs (`M10`, `M11`, `M14`) Across 5 GHz PtMP, LTU AME SoC, and 2.4 GHz AirPrism

- **Task ID**: `T-S32A-LIVE-MINED-KNOBS-M10-M11-M14-PHYSICAL-BENCH`
- **Completed UTC**: `2026-10-25T18:23:08Z`
- **Source Census Artifact**: [`artifacts/autoresearch/stage29a_mined_knobs_and_hypotheses_20261025.json`](../artifacts/autoresearch/stage29a_mined_knobs_and_hypotheses_20261025.json) (`1,269` protocol declarations, `145` controls, ranked `M9..M15` candidates)
- **Physical Bench Receipt**: [`artifacts/autoresearch/stage32a_mined_knobs_bench_20261025.json`](../artifacts/autoresearch/stage32a_mined_knobs_bench_20261025.json)
- **Bench Runner**: [`tools/bench/run_stage32a_mined_knobs_bench.py`](../tools/bench/run_stage32a_mined_knobs_bench.py)
- **Test Suite**: [`tests/test_stage32a_mined_knobs_bench.py`](../tests/test_stage32a_mined_knobs_bench.py) (`4 passed in 0.40s`)
- **Safety Policy**: Strictly RAM-only (`0` flash writes, `cfgmtd -w` and `uci commit` forbidden).

---

## 1. Executive Summary

Stage 32A bridged `Codex`'s offline Stage 29A protocol/knob census (`artifacts/autoresearch/stage29a_mined_knobs_and_hypotheses_20261025.json`) into live physical verification across three distinct hardware families on the FuturaMAX bench:
1. **Qualification of Setter/Getter & Binary Calling Conventions**:
   - **`M10` (`HTT_H2T_MSG_TYPE_AGGR_CFG` — A-MSDU ceiling `3 -> 2` with A-MPDU held fixed at `64`)**: Qualified via `/sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu` on `LAP-120` and `Loco 5AC` (`OpenWrt 24.10.4` `ath10k-ct`), which dispatches `HTT_H2T_MSG_TYPE_AGGR_CFG` (`0x5`) and provides an exact readback getter (`"3 64"` vs `"2 64"`).
   - **`M11` (`AME do_lotto` — DL Lottery Scheduling Isolation)**: Qualified via `/sys/module/ame_core/parameters/do_lotto` on `LTU-Lite #1` (`PUBLIC_DEVICE_0046%27`, `LTU.afltu.v2.4.0` unlocked in `ap-ptmp` SQ mode), with exact readback getter (`"0"` vs `"1"`).
   - **`M14` (`UPH swr_limit` — Host TDMA Software Retry Limit)**: Resolved the missing vector semantics noted in Stage 29A by disassembling `ubnt_poll_host_sysctl_int` (`0x2834..0x2844`) and `ubnt_poll_host_set_swr_limit` (`0x0b404`, `104` bytes) in `ubnt_poll_host.ko`. Proven that `swr_limit` takes a 2-integer vector `<enable_flag> <limit>` (`lbu $a1, intvec[0]`; `lbu $a2, intvec[1]`), sends message subtype `0x001f` (`31`) via `ubnt_poll_host_ht_comm_tx` (`0x0b454`), and emits kernel log confirmation `<7>ubnt_poll_host: SWR Limit enabled at set to %d` (`$LC59`) or `<7>ubnt_poll_host: SWR Limit disabled` (`$LC60`).
2. **Physical Bench Results (`A1 -> B1 -> A2 -> B2` Counterbalanced Starting Strictly from Current Champions)**:
   - **`S32A-R1` (`M10`: `htt_max_amsdu_ampdu = '2 64'` vs `'3 64'` on 3-CPE 5 GHz Sector from `Stage 31A Champion v8`)**:
     - `Stage 31A Champion v8` (`Arm A`, `'3 64'`) achieved **`62.323 Mbps` (`3.116 Mbps/MHz`, peaking at `64.760 Mbps` / `3.238 Mbps/MHz` in `A1`)** and **`63.888 ms` `p95` RTT** (`0.00%` loss).
     - Lowering A-MSDU subframes from `3` to `2` (`Arm B`, `'2 64'`) increased MPDU delimiter overhead at high VHT20 MCS8 rates (`117..173.3 Mbps`), reducing goodput by `-0.789%` (`61.831 Mbps`) and **increasing sector `p95` RTT by `+11.600%` (`63.888 -> 71.299 ms`)** -> **`RETAIN_CURRENT_CHAMPION` (`Stage 31A Champion v8`)**.
   - **`S32A-R2` (`M11`: `AME do_lotto = 1` vs `0` on `LTU-Lite #1` `ap-ptmp` SQ mode from `S24F-R1` Champion)**:
     - Enabling stochastic lottery DL scheduling (`do_lotto = 1`) nudged goodput by `+0.451%` (`32.581 -> 32.728 Mbps`) but **spiked `p95` RTT by `+74.539%` (`47.006 -> 82.044 ms`: `80.630 ms` in `B1`, `83.458 ms` in `B2`)** due to geometric waiting-time variance across TDD frames -> **`RETAIN_CURRENT_CHAMPION` (`S24F-R1` Champion `do_lotto=0`)**.
   - **`S32A-R3` (`M14`: `UPH swr_limit = '1 6'` vs `'0 0'` on `Rocket 2AC Prism` under live 2.4 GHz `NanoLoco M2` `-59 dBm` load from `S27-R2AC-R2` Champion)**:
     - Because `S27-R2AC-R2` Champion already bounds `nonaggr_swretry=4` and `aggr_swretry=6` at the radio driver layer, enabling redundant `uph_wifi0/swr_limit = '1 6'` changed goodput by `-1.449%` (`27.812 -> 27.409 Mbps`) and `p95` RTT by `+2.246%` (`20.618 -> 21.081 ms`) -> **`RETAIN_CURRENT_CHAMPION` (`S27-R2AC-R2` Champion `swr_limit='0 0'`)**.

---

## 2. Summary Comparison Table (`A1 -> B1 -> A2 -> B2`)

| Round ID | Mined ID | Target Radio / Sector | Control Arm (`A` = Current Champion) | Treatment Arm (`B`) | Arm A Goodput | Arm B Goodput | $\Delta$ Goodput | Arm A `p95` RTT | Arm B `p95` RTT | $\Delta$ `p95` RTT | Decision |
| :--- | :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S32A-R1`** | **`M10`** | 3-CPE 5 GHz Sector (`LAP-120` `.20` + `Loco5AC` `.250` + `Rocket5AC` `.198` + `LiteBeamM5` `.251`) | `Stage 31A Champion v8` (`htt_max_amsdu_ampdu = '3 64'`) | `Stage 31A Champion v8` + **`htt_max_amsdu_ampdu = '2 64'`** | **`62.323 Mbps`** (`64.76 Mbps` peak) | `61.831 Mbps` | `-0.789%` | **`63.888 ms`** | `71.299 ms` | `+11.600%` | **`RETAIN_CURRENT_CHAMPION`** |
| **`S32A-R2`** | **`M11`** | `LTU-Lite #1` (`PUBLIC_DEVICE_0046%27`, `ap-ptmp` SQ mode) | `S24F-R1` Champion (`sym 12..62/72`, `do_lotto = 0`) | `S24F-R1` Champion + **`do_lotto = 1`** | `32.581 Mbps` | `32.728 Mbps` | `+0.451%` | **`47.006 ms`** | `82.044 ms` | **`+74.539%`** | **`RETAIN_CURRENT_CHAMPION`** |
| **`S32A-R3`** | **`M14`** | `Rocket 2AC Prism` (`198.18.0.65` + `NanoLoco M2` `-59 dBm` 2.4 GHz) | `S27-R2AC-R2` Champion (`swr_limit = '0 0'`) | `S27-R2AC-R2` Champion + **`swr_limit = '1 6'`** | **`27.812 Mbps`** | `27.409 Mbps` | `-1.449%` | **`20.618 ms`** | `21.081 ms` | `+2.246%` | **`RETAIN_CURRENT_CHAMPION`** |

---

## 3. Binary & Hardware Qualification Details

### 3.1 `M14` (`UPH swr_limit`) MIPS32 Disassembly & `dmesg` Getter Proof
In `artifacts/firmware_re_xc_ltu/xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko`:
- **Dispatcher (`ubnt_poll_host_sysctl_int` at `.text+0x2834..0x2844`)**:
  - `0x2834: addiu $v1, $v0, 0x09a8` (base of `intvec` scratch array in `.bss`)
  - `0x2838: lbu $a1, 0x09ab($v0)` (`$a1 = intvec[0] & 0xff` = `enable_flag`)
  - `0x2840: jal ubnt_poll_host_set_swr_limit` (`0x0b404`)
  - `0x2844: lbu $a2, 7($v1)` (`$a2 = intvec[1] & 0xff` = `swr_limit_val`)
- **Handler (`ubnt_poll_host_set_swr_limit` at `.text+0x0b404`, `104` bytes)**:
  - Packs `msg_type = 0x001f` (`31`), `payload[0] = enable_flag`, `payload[1] = swr_limit_val`, logs `<7>ubnt_poll_host: SWR Limit enabled at set to %d` (`$LC59`) when `enable_flag != 0` or `<7>ubnt_poll_host: SWR Limit disabled` (`$LC60`) when `enable_flag == 0`, and transmits to the radio via `ubnt_poll_host_ht_comm_tx` (`0x0b454`).
- **Live Verification on `Rocket 2AC Prism` (`198.18.0.65`)**:
  - `A1`: `[103273.278000] ubnt_poll_host: SWR Limit disabled`
  - `B1`: `[103278.802000] ubnt_poll_host: SWR Limit enabled at set to 6`
  - `A2`: `[103284.355000] ubnt_poll_host: SWR Limit disabled`
  - `B2`: `[103289.925000] ubnt_poll_host: SWR Limit enabled at set to 6`
