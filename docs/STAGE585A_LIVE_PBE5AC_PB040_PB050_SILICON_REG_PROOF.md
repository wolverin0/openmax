<!-- doc-head: STAGE585A_LIVE_PBE5AC_PB040_PB050_SILICON_REG_PROOF.md preserved document content -->
<!-- /doc-head -->



# Stage 585A — Live 3-Segment Patched `SGMT` Xtensa Firmware (`PB-040` + `PB-050`, `athwlan=12b29d01`, `0x29e00=0x13761320`) Bind-Mount Proof on `.241` & `.242`

## 1. Surgical 3-Segment `SGMT` Patch Composition (`CONFIRMED`, attribution: `QCA firmware` + `ath10k` + `hardware`)
- Constructs `/tmp/firmware-2-pb050.bin` (`SHA-256 = a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f`) in volatile RAM (`/tmp/fmx_xtensa_pb050/firmware-2.bin`) from stock `/rom/lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin` (`SHA-256 = 398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e`) on BOTH `.241` (`AP`) and `.242` (`STA`, OTA):
  1. **Segment 1 (`.rodata` `0x0040bc30`, file offset `0x37c4` = `14276`) — `PB040-CANARY-RODATA`**: Patches `'SM: %d:%p : invalid event %d'` $\rightarrow$ `'SM: %d:%p : Invalid Event %d'`.
  2. **Segment 2 (`.data` `0x0040c140`, file offset `0x3b1d` = `15133`) — `PB050-RC-PROBE-DAMPEN`**: Dampens the upward MCS probe timer from `0x07d0` (`2000 ms`) to `0x0fa0` (`4000 ms`).
  3. **Segment 3 (`.text` `0x009b7584`, file offset `0x31b14` = `203540`) — `PB040-CCA-AGC-OVERRIDE`**: Patches the modal INI shadow for baseband register `0x00029e00` (`BB_timing_controls_1`) from `0x13721320` to `0x13761320`.

---

## 2. Live Silicon & Checksum Readback (`0` Flash Writes)
- Bind-mounted `/tmp/fmx_xtensa_pb050` over `/lib/firmware/ath10k/QCA988X/hw2.0`, reloaded `ath10k_pci` (`rmmod ath10k_pci && modprobe ath10k_pci && wifi up`), and verified live on both `.241` and `.242`:
  - `sha256sum`: `a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f`
  - `/sys/kernel/debug/ieee80211/phy0/ath10k/fw_checksums`: `firmware-N.bin = 92363606`, `athwlan = 12b29d01`, `otp = 4c4fd0bc`
  - `/sys/kernel/debug/ieee80211/phy0/ath10k/reg_value` (`0x00029e00`): `0x13761320`
  - Post-reload full-MTU `1472B` ping: `0.0%` packet loss.

---

## 3. Artifacts & Verification
- Script: [`run_stage585a_live_pbe5ac_pb040_pb050_silicon_reg_proof.py`](../tools/benchmarks/run_stage585a_live_pbe5ac_pb040_pb050_silicon_reg_proof.py)
- Receipt: [`stage585a_live_pbe5ac_pb040_pb050_silicon_reg_proof.json`](../artifacts/autoresearch/stage585a_live_pbe5ac_pb040_pb050_silicon_reg_proof.json)
- Test: [`test_stage585a.py`](../tests/test_stage585a.py)
