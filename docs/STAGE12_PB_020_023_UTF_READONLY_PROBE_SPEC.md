<!-- doc-head: STAGE12_PB_020_023_UTF_READONLY_PROBE_SPEC.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — PB-020 & PB-023 Runner Specification: `AR9888` UTF Read-Only Capability Enumerator & `ADCCAPTURE` / `GENWAVEFORM` / `PHYDBGDUMP` Probe Harness

## 1. Executive Summary

This document defines the bounded read-only qualification harness, preflight safety gates, watchdog rollback verifiers, and tone-correlated sample-RAM validators for gates **`PB-020`** and **`PB-023`** of the Physical-Boundary Experimental Ladder ([`research/physical_boundary/ladder.yaml`](<repo>/research/physical_boundary/ladder.yaml)).

All logic and deterministic fixtures are implemented in:
- [`tools/qca988x/utf_readonly_probe_harness.py`](<repo>/tools/qca988x/utf_readonly_probe_harness.py)
- [`artifacts/qca988x/pb_020_023_utf_probe_fixture.json`](<repo>/artifacts/qca988x/pb_020_023_utf_probe_fixture.json)
- [`tests/test_pb_020_023_utf_readonly_probe_harness.py`](<repo>/tests/test_pb_020_023_utf_readonly_probe_harness.py)

---

## 2. Hard Preflight & Safety Invariants (`automatic_execution_allowed = False`)

Before any `ath10k` testmode / `utf.bin` operation is permitted on a cabled bench radio, [`verify_utf_bench_preflight()`](<repo>/tools/qca988x/utf_readonly_probe_harness.py#L106-L125) enforces five mandatory conditions:
1. **`is_production_network_device == False`**: Production APs/CPEs (`198.18.0.2`, `198.18.0.3`, `198.18.0.4`, `Panel1..3`) are strictly off-limits.
2. **`is_sacrificial_bench_unit == True`**: Only explicitly designated sacrificial bench units may enter UTF testmode.
3. **`rf_ports_terminated_50ohm_or_attenuated_50db == True`**: All RF ports must be terminated into $50\,\Omega$ dummy loads or $\ge 50\text{ dB}$ coaxial attenuators.
4. **`serial_and_tftp_recovery_verified == True`**: Wired UART console and TFTP/power-cycle recovery must be pre-verified.
5. **Immutable SHA-256 Provenance**: Exact 64-hex-character SHA-256 digests recorded for `board.bin`, `utf.bin`, and production `firmware-5.bin`.

---

## 3. Gate `PB-020` — Read-Only TLV2 Capability Enumeration & `<30s` Reload Watchdog

### 3.1 Strictly Enforced Read-Only Command Allowlist (`Q07`, `Q08`)

| Command ID | Symbol | Handler in `cmdProcessTlv2.c` (`Q08`) | Why Allowed in `PB-020` |
| ---: | :--- | :--- | :--- |
| **`9`** | `CMD_REGREAD` | `regReadHandler` (`line 147`) | Passive 4-byte-aligned 32-bit register read (`hwMemRead32`). |
| **`15`** | `CMD_TXSTATUS` | `txStatusHandler` (`line 331`) | Passive TX status/thermal counter read (`stopTx = 0`). |
| **`18`** | `CMD_RXSTATUS` | `rxStatusHandler` (`line 547`) | Passive RX packet/RSSI/pilot-EVM counter read (`stopRx = 0`). |
| **`42`** | `CMD_MEMREAD` | `memReadHandler` (`line 68`) | Passive target DRAM/BB read (`<= 255` bytes per call). |
| **`76`** | `CMD_LMQUERY` | `LMQueryHandler` (`line 963`) | Passive Link-Maintenance state query. |

### 3.2 Explicitly Forbidden Commands in `PB-020`
- `CMD_REGWRITE` (`11`), `CMD_MEMWRITE` (`40`), `CMD_WRITECUSTOTPSPACE` (`26`), `CMD_COMMITOTPSTREAM` (`36`), `CMD_SETREGDMN` (`38`), `CMD_TX` (`14`), `CMD_RX` (`17`), `CMD_HWCAL` (`20`), and **`CMD_NOISEFLOORREAD` (`102`)** (forbidden in `PB-020` because `noiseFloorReadHandler` in `Q08:901` invokes `whalReset(..., WHAL_RESET_CAUSE_FULL_RESET)`).

### 3.3 Acceptance & Watchdog Rollback Rules
- **Cycles Required**: $\ge 5$ consecutive cycles (`utf_boot_success_rate == 1.0`, `wlan_reload_success_rate == 1.0`).
- **Command Latency Watchdog**: Any command exceeding `5.0 s` triggers `UNLOAD_TESTMODE_AND_COLD_POWER_CYCLE_RECOVERY`.
- **Production WLAN Reload Watchdog**: Clean reload back to normal production firmware must complete in `<= 30.0 s` (`4.8..5.6 s` in the baseline fixture).

---

## 4. Gate `PB-023` — `ADCCAPTURE` (`59`), `GENWAVEFORM` (`61`) & `SYSCMD_PHYDBGDUMP` (`10009`) Probe & Sample-RAM Tone Validator

### 4.1 Bounded `3.0 s` Watchdog Probe
- Issues single-shot bounded TLV2 requests for `CMD_ADCCAPTURE` (`59`), `CMD_GENWAVEFORM` (`61`), and `SYSCMD_PHYDBGDUMP` (`10009`) with a hard `3.0 s` timeout (`UNLOAD_UTF_AND_POWER_CYCLE_RADIO` if target hangs).

### 4.2 Complex DFT Tone-Correlation Validator (`dataI[2048]`, `dataQ[2048]`)
If a candidate `UTF` binary returns a `CMD_ADCCAPTURERSP` (`60`) payload (`2048` complex samples at $f_s = 80\text{ MHz}$), [`compute_iq_tone_correlation_and_snr()`](<repo>/tools/qca988x/utf_readonly_probe_harness.py#L244-L282) projects $z[n] = I[n] + j Q[n]$ onto the injected cabled reference tone $e^{-j 2\pi (f_{\text{tone}}/f_s) n}$:
$$\rho_{\text{tone}} = \sqrt{\frac{\left|\sum_{n=0}^{N-1} z[n] e^{-j 2\pi (f_{\text{tone}}/f_s) n}\right|^2}{N \sum_{n=0}^{N-1} |z[n]|^2}} \ge 0.90$$

### 4.3 Decision Branch Outcome
- **`FALSIFIED_STANDARD_TLV2_ADC_ABI`** (Expected for stock `AR9888` UTF per `Q08` static link audit): Closes the standard TLV2 `ADCCAPTURE` branch and routes all sub-packet channel sensing through `PB-021` (`PHY_BB_CHAN_INFO_CHAN_TAB_B0/B1` at `0x00009b00`/`0x0000ab00` + `CMD_MEMREAD` ID `42`).
- **`VERIFIED_TONE_CORRELATED_SAMPLE_RAM`**: Unlocks offline learned/neural receiver analysis on raw `QCA988x` ADC captures.
