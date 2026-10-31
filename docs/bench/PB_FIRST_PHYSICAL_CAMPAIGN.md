<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# First Physical-Boundary Bench Campaign Plan (`PB-020` / `PB-023` & `PB-021` / `PB-022`)

> [!IMPORTANT]
> **DO NOT EXECUTE ON HARDWARE WITHOUT EXPLICIT OPERATOR GATE APPROVAL (`operator_gate_approved = True`)**.
> During Phase 0, all hardware-touching gates in [`research/physical_boundary/ladder.yaml`](../../research/physical_boundary/ladder.yaml) enforce `automatic_execution_allowed: false` and are guarded by [`controller/pb_campaign_preflight_verifier.py`](../../controller/pb_campaign_preflight_verifier.py).

---

## 1. Campaign Scope & Branch-Elimination Objective

Before investing engineering effort into target-resident schedulers (`PB-051`) or custom PHY signaling (`PB-070`), the first physical bench campaign resolves the two highest-information-gain questions on sacrificial QCA988x hardware:

1. **Track 1 — Exact AR9888 UTF Read-Only Qualification (`PB-020` & `PB-023`)**:
   - Can an isolated sacrificial QCA988x board (`LAP-120` or `NanoStation 5AC Loco` bench unit) safely boot exact `AR9888` UTF (`utf.bin`) in RAM-only testmode, respond to read-only capability/version/status queries, enumerate whether `ADCCAPTURE` (`ID 59`), `GENWAVEFORM` (`ID 61`), and `PHYDBGDUMP` handlers exist in the compiled target, and cleanly reload normal production WLAN firmware?
2. **Track 2 — Channel-Capture Path Qualification (`PB-021` & `PB-022`)**:
   - When `bb_capture_channel` is requested on a cabled QCA988x pair (`50-60 dB` inline 5 GHz coaxial attenuation), does the RX PPDU completion descriptor assert `bb_captured_channel=1` with a non-zero `bb_length` (or `txbf_h_info` / compressed-V payload), and does target DRAM / BB debug SRAM contain a packet-correlated complex channel dump?

---

## 2. Mandatory Prerequisites & Safety Checklist

Both tracks are **BLOCKED** by [`verify_campaign_preflight()`](../../controller/pb_campaign_preflight_verifier.py) unless every item below is satisfied:

1. **Completed Phase 0 Offline Gates**:
   - `PB-000` (`PASSED`): Exact-family claim and register/descriptor inventory completed.
   - `PB-001` (`PASSED`): Explicit `channel_width_mhz` validation and paired `A/B/A/B` gatekeeper null-replay calibration verified (`11/11` pytest pass).
   - `PB-010` (`PASSED`): Static WMI/HTT dispatch and `rx_ppdu_end` strip-site map completed.
2. **Sacrificial Bench Isolation**:
   - Target IP must belong to `ALLOWED_SACRIFICIAL_BENCH_IPS` (`198.18.0.50/21` or `198.18.0.153/21`).
   - Any IP in `198.18.0.93/24` (Guarida / Almafuerte / production network) is strictly rejected.
3. **Zero Persistent Flash Modification**:
   - `ram_only_target_load = True` (firmware loaded into target DRAM via BMI/testmode only; zero SPI NOR writes).
   - Protected partitions (`u-boot`, `u-boot-env`, `art`, `factory`, `eeprom`, `board-data`) are SHA-256 hashed before and after every session and never opened for writing.
4. **Verified Recovery Harness**:
   - `serial_console_attached = True` (wired UART logging boot and target host-interest pointers).
   - `tftp_recovery_verified = True` (verified u-boot TFTP recovery image staged on bench host).
   - `poe_power_relay_verified = True` (automated cold power-cycle rollback on watchdog timeout).
5. **RF Containment**:
   - `execution_mode = "cabled_bench"`.
   - Track 1 requires `rf_terminated_50ohm = True` (50-ohm dummy loads on all RF ports) or `coaxial_attenuation_db >= 50.0`.
   - Track 2 requires `coaxial_attenuation_db >= 50.0` (`50-60 dB` rated 5 GHz coaxial attenuators between the sacrificial pair, with unused chains terminated in 50 ohms).

---

## 3. Track 1 Specification: Exact AR9888 UTF Read-Only Qualification (`PB-020` / `PB-023`)

### 3.1 Command Allowlist vs Blocklist
- **Permitted Read-Only Commands (`TRACK1_READONLY_UTF_ALLOWLIST`)**:
  - `UTF_GET_VERSION`: Query target UTF build version and ABI revision.
  - `UTF_GET_STATUS`: Query target task health and host-interest status (`0x00400800` region).
  - `UTF_ENUM_CAPABILITIES`: Non-destructive TLV command table probe.
  - `UTF_READ_HOST_INTEREST`: Read-only snapshot of target DRAM host-interest table (`0x400000..0x44ffff`).
  - `UTF_QUERY_TLV_SUPPORT_ADCCAPTURE`: Check handler registration/response code for `ADCCAPTURE` (`ID 59`) with RF terminated.
  - `UTF_QUERY_TLV_SUPPORT_GENWAVEFORM`: Check handler registration/response code for `GENWAVEFORM` (`ID 61`).
  - `UTF_QUERY_TLV_SUPPORT_PHYDBGDUMP`: Check handler registration/response code for `PHYDBGDUMP`.
  - `UTF_READ_BB_CAPTURE_STATUS`: Read-only status of baseband capture indicators.
- **Strictly Forbidden Commands (`TRACK1_DESTRUCTIVE_UTF_BLOCKLIST`)**:
  - `UTF_CONT_TX`, `UTF_TX_TONE`, `UTF_WRITE_OTP`, `UTF_WRITE_EFUSE`, `UTF_WRITE_CALDATA`, `UTF_COMMIT_ART`, `UTF_FLASH_WRITE`, `UTF_SET_REGULATORY_BYPASS`.

### 3.2 Execution & Rollback Sequence (Once Operator Gate Is Granted)
1. Hash all MTD partitions (`/proc/mtd`) and verify `art` / `EEPROM` SHA-256 match baseline inventory.
2. Unbind normal WLAN VIFs, load `utf.bin` into target RAM via `ath10k_testmode`, and start a 5-second hardware watchdog timer.
3. Issue `UTF_GET_VERSION`, `UTF_GET_STATUS`, and `UTF_ENUM_CAPABILITIES`.
4. Probe `ADCCAPTURE`, `GENWAVEFORM`, and `PHYDBGDUMP` read-only status codes with RF ports terminated into 50 ohms.
5. Unload testmode, reload production WLAN firmware, verify normal association and ping within 30 seconds, and repeat for 5 consecutive cycles.

### 3.3 Interpretation of Outcomes
- **Success (`PASSED`)**: 5/5 clean UTF boot -> read-only query -> production WLAN reload cycles, yielding a definitive bitmap of which TLV commands exist in `AR9888` UTF.
- **Falsification (`FAILED`)**: If `ADCCAPTURE` / `PHYDBGDUMP` return unsupported/absent and static symbol tables confirm no handler compiled into `AR9888`, the on-chip raw-IQ capture branch via standard TLV is closed (`PB-023` falsified).

---

## 4. Track 2 Specification: Channel-Capture Path Qualification (`PB-021` / `PB-022`)

### 4.1 Inspected Descriptor & Memory Fields (`TRACK2_CHANNEL_CAPTURE_FIELDS`)
- `bb_capture_channel` (TX/RX PCU/BB descriptor request bit)
- `bb_captured_channel` (`rx_ppdu_end` completion indicator bit)
- `bb_length` (`rx_ppdu_end` appended BB debug byte length)
- `txbf_h_info` (`rx_ppdu_end` beamforming H-matrix debug structure)
- `compressed_v_svd` (TXBF SVD / compressed-V DMA output buffer)

### 4.2 Cabled Bench Procedure (Once Operator Gate Is Granted)
1. Connect sacrificial AP and CPE via `55 dB` 5 GHz coaxial attenuation on Chain 0 and Chain 1.
2. Enable non-destructive raw HTT RX PPDU completion logging (`rx_ppdu_end` pre-strip inspection) and set `bb_capture_channel=1`.
3. Send bounded cabled VHT NDP/data bursts across 3 known cabled attenuation/phase settings (`Symmetric 55/55 dB`, `Asymmetric 55/70 dB`, `Single-Chain Terminated`).
4. Record `bb_captured_channel` assertion rate, `bb_length` distribution, `txbf_h_info` bytes, and differential target DRAM snapshots (`0x400000..0x44ffff`).

### 4.3 Expected Artifacts
- `artifacts/pb_bench/pb_020_utf_readonly_capability_report.json`
- `artifacts/pb_bench/pb_021_channel_dump_qualification.json`
- `artifacts/pb_bench/pb_022_txbf_h_info_probe.json`
- `artifacts/pb_bench/pb_023_adccapture_genwaveform_probe.json`
