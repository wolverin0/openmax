<!-- doc-head: STAGE45B_LTU_16BYTE_SSID_TRUNCATION_AND_OTA_PROVISIONING.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 45B: LTU 16-Byte Hardware Beacon SSID Truncation Fix (`FMX-LTU`), Full DCXO Alternating Scan List (`5500 5520`), `+15 dBm` Distance Power & `Boca 7` Auto-Provisioner

- **Task ID**: `T-S45B-LTU-16BYTE-SSID-FMX-LTU-AND-BOCA7-AUTO-PROVISIONER`
- **Date**: 2026-10-25
- **Scripts & Artifacts**:
  - [`tools/bench/deploy_stage40a_ltu_poststart.py`](<repo>/tools/bench/deploy_stage40a_ltu_poststart.py)
  - [`tools/bench/run_stage45b_ltu_16byte_ssid_and_boca7_provisioner.py`](<repo>/tools/bench/run_stage45b_ltu_16byte_ssid_and_boca7_provisioner.py)
  - [`artifacts/autoresearch/stage45b_ltu_16byte_ssid_fmx_ltu_provision_20261025.json`](<repo>/artifacts/autoresearch/stage45b_ltu_16byte_ssid_fmx_ltu_provision_20261025.json)
  - [`tests/test_stage45b_ltu_16byte_ssid_provision.py`](<repo>/tests/test_stage45b_ltu_16byte_ssid_provision.py)

---

## 1. Root Causes Identified in `ame_core.ko` & Fixed in Stage 45B (`CONFIRMED`)

1. **16-Byte Hardware Beacon SSID Truncation (`ame_core_beacon_update` @ `0x007008` vs `slm_find_preferred_record` @ `0x045e20`)**:
   - In `ame_core.ko`, the hardware beacon frame stores the SSID in `[s_beacon, #0x0e..0x1d]`, which is **strictly 16 bytes max** (four 32-bit words).
   - When `SSID = "FuturaMAX-LTU-Bench"` (`19` bytes) was configured, the AP transmitted the truncated 16-byte string `"FuturaMAX-LTU-Be"` in every beacon (as visible in `amecli get_common_info`: `SSID:FuturaMAX-LTU-Be Security:NONE`).
   - On the CPE side, `slm_find_preferred_record` (`0x045e20`) compares the received 16-byte beacon SSID against the full `prefer_ssid` from `/tmp/ame.cfg` (`strcmp("FuturaMAX-LTU-Be", "FuturaMAX-LTU-Bench")`), which failed on every single beacon (`16 != 19`).
   - **Fix**: Replaced the SSID across `/tmp/system.cfg`, `/tmp/ame.cfg`, `/tmp/ame.ini`, and `/etc/persistent/rc.poststart` with **`"FMX-LTU"`** (**7 bytes**, strictly $\le 16$ bytes). Verified live on `LTU-Lite #1` (`Boca 5`): `amecli get_common_info` now reports `SSID:FMX-LTU Security:NONE` with zero truncation.

2. **`Quick TCXO` vs Full DCXO Crystal Calibration (`cpeFsmStart` @ `0x048000`)**:
   - When the CPE scans identical consecutive frequencies (`5500 5500 5500 5500`), `cpeFsmStart` skips full DCXO frequency-offset calibration and falls back to `Quick TCXO` (`DCXO coarse=40, fine=32767`).
   - **Fix**: Configured `LTU2_RC_POSTSTART` and `/tmp/system.cfg` with alternating scan frequencies (`amecli freq_list 5500 5520 5500 5520` and `radio.1.freq_scan_list=5500 5520`) so every scan hop transitions frequency (`5520 -> 5500`) and executes a full DCXO lock.

3. **Distance TX Power (`+15 dBm` / `powerout = 28`) & Target RX (`-60 dBm`)**:
   - Updated both `LTU1_RC_POSTSTART` and `LTU2_RC_POSTSTART` (and `/tmp/system.cfg` persisted via `cfgmtd -w -p /etc/`) from the 30 cm desk thermal guard (`-26 dBm`) to indoor/outdoor distance parameters:
     - `txpwr = 15`, `antenna_gain = 13` (`powerout = 28` dBm EIRP)
     - `rx_target_pwr = 600` (`-60 dBm`), `rx_target_pwr_auto_en = 1`
     - `board_ssid = 0xae08` (`intmode = 1` on `LTU-Lite #1`)

---

## 2. Live Provisioning Status

| Unit | Port / Host | Status | Verified `amecli get_common_info` |
| :--- | :--- | :--- | :--- |
| **`LTU-Lite #1`** | `Boca 5 / gi5` (`PUBLIC_DEVICE_0046%27`) | **PROVISIONED & PERSISTED (`cfgmtd -w -p /etc/`)** | `AP-PTMP(Run) [PUBLIC_DEVICE_0045] \| BW: 20Mhz, Freq: rx(5500Mhz) tx(5500Mhz) \| Txpower: 15,15, Antenna Gain: 13 \| SSID: FMX-LTU Security: NONE \| AutoLink: 1` |
| **`LTU-Lite #2`** | `Boca 7 / gi7` (`PUBLIC_DEVICE_0076%27`) | **AUTO-PROVISIONER ARMED** (`run_stage45b_ltu_16byte_ssid_and_boca7_provisioner.py`) | Ready to push `SSID="FMX-LTU"`, `txpwr=15`, `freq_list 5500 5520 5500 5520`, and `cfgmtd -w -p /etc/` the instant `LTU-Lite #2` is plugged into `Boca 7` |
