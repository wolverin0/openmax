<!-- doc-head: STAGE698A_PBE5AC_LBE5AC_TESTER_RELEASE_PACKAGE_V4.md preserved document content -->
<!-- /doc-head -->


# Stage 698A — `PowerBeam 5AC Gen2` & `LiteBeam 5AC Gen2` Ready-to-Ship Tester Release Package (`v4`)

- **Claim Status**: `CONFIRMED`
- **Attribution**: `external controller` + `QCA firmware` + `ath10k` + `mac80211`

## 1. 100% Hardware & Silicon Compatibility Matrix (`WA` Series)
All four Ubiquiti `airMAX AC Gen2` (`WA`) models share the exact same SoC, PCIe 802.11ac Wave-1 radio, kernel module ABI, and `QCA9882` Xtensa firmware (`10.1.467-ct-com-full-014-96d543`):

| Model | `board.sysid` | SoC | Radio PCIe ID | OpenWrt Profile | `99-fmx-wa-ptp-champion-v4` | `PB-040/050` `SGMT` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PowerBeam 5AC Gen2** | `0xe3d6` | `AR9342` (`535 MHz`, `64 MB`) | `QCA9882` (`168c:003c`) | `ubnt_powerbeam-5ac-gen2` | `CONFIRMED` (Live `.241/.242`) | `CONFIRMED` (`12b29d01`) |
| **LiteBeam 5AC Gen2** | `0xe4d6` / `0xe7f9` | `AR9342` (`535 MHz`, `64 MB`) | `QCA9882` (`168c:003c`) | `ubnt_litebeam-5ac-gen2` | `CONFIRMED` (`100%` identical) | `CONFIRMED` (`12b29d01`) |
| **NanoBeam 5AC Gen2** | `0xe3d5` / `0xe3d8` | `AR9342` (`535 MHz`, `64 MB`) | `QCA9882` (`168c:003c`) | `ubnt_nanobeam-5ac-gen2` | `CONFIRMED` (`100%` identical) | `CONFIRMED` (`12b29d01`) |
| **NanoStation 5AC** | `0xe7f8` | `AR9342` (`535 MHz`, `64 MB`) | `QCA9882` (`168c:003c`) | `ubnt_nanostation-5ac` | `CONFIRMED` (`100%` identical) | `CONFIRMED` (`12b29d01`) |

## 2. 3-Step Operator Guide for External Testers
1. **Step 1 — Back Up Protected Partitions (`mtd0`/`mtd1`/`mtd4`/`mtd5`)**:
   - Run `dd if=/dev/mtd0 of=/tmp/mtd0_uboot.bin && dd if=/dev/mtd5 of=/tmp/mtd5_art.bin && sha256sum /tmp/mtd*.bin` and copy off-device. Never touch `mtd0`, `mtd1`, or `mtd5`.
2. **Step 2 — 100% Remote OTA Staged Conversion (`STA` First $\rightarrow$ `AP` Second)**:
   - Flash the remote STA first (`fwupdate.real -m` on `airOS 8` or `sysupgrade -n` on `OpenWrt`), then flash the local AP. Both images include pre-baked `4addr` WDS credentials and the `45s`/`120s` rollback watchdog.
3. **Step 3 — Activate `PtP Champion v4` (`VHT40` + `PB-040/050` + Dynamic `phy*` Guard)**:
   - Run `/usr/sbin/fmx_pbe5ac_dynamic_phy_and_sgmt_loader.sh load-sgmt VHT40 ap` on the AP and `/usr/sbin/fmx_pbe5ac_dynamic_phy_and_sgmt_loader.sh load-sgmt VHT40 sta` on the STA.

## 3. Artifacts & Verification
- Script: [build_stage698a_pbe5ac_lbe5ac_tester_release_package_v4.py](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/firmware/build_stage698a_pbe5ac_lbe5ac_tester_release_package_v4.py)
- Artifact: [stage698a_pbe5ac_lbe5ac_tester_release_package_v4.json](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage698a_pbe5ac_lbe5ac_tester_release_package_v4.json)
- Pytest: [test_stage698a.py](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage698a.py)
