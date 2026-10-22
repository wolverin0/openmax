# Stage 10 & 11 Complete Reverse-Engineering, Architecture & Bench Archive (2026-10-21)

> **Purpose:** Permanent repository archive consolidating all static reverse-engineering proofs, kernel/firmware offsets, hardware experiments, and architectural discoveries generated across the Antigravity (`run:run_458a34fbc172`) and Codex (`run:run_204f7681fd7c`) sessions through **2026-10-21**, ensuring zero knowledge loss across context window compactions or future git commits.

---

## 1. Where Everything Is Stored in the Repository

All artifacts, scripts, receipts, and binary disassembly proofs are now inside the Git working tree:

1. **Core Living Ledger & Logs (`docs/`)**:
   - [`docs/BENCH_PLAN.md`](BENCH_PLAN.md) — Chronological experiment plan, preflight gates, and bench execution log (`FMX-0015`).
   - [`docs/CURRENT_STATE.md`](CURRENT_STATE.md) — Current verified state of all lab and production milestones.
   - [`docs/DECISIONS.md`](DECISIONS.md) — Architectural and safety gate decisions.
   - [`docs/RESEARCH_LEDGER.md`](RESEARCH_LEDGER.md) — Claim-by-claim ledger (`CONFIRMED`, `INFERRED`, `UNKNOWN`, `REFUTED`).
2. **Stage-Specific Technical Reports (`docs/`)**:
   - [`docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md`](STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md) — Stock `airOS 8` (`WA.v8.7.x`) interoperability, `allow_80211`, and revert workflows.
   - [`docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md`](STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md) — Complete reverse engineering of `XC.v8.7.25` (`Rocket Prism 5AC Gen2`, `QCA9558 + QCA9880 + AirPrism HSR` SPI/GPIO tuning, dual-radio `wifi0` + `wifi1`).
   - [`docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md`](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md) — Complete reverse engineering of `LTU v2.4.2` (`aflturocket` & `afltu`), proving why `4096-QAM` (`12x`) is absent from the FPGA/ASIC rate tables (`0..10x` max `1024-QAM`) despite UI/config remnants.
3. **Preserved Scratch Disassemblies, Proofs & Session Reports (`artifacts/re_proofs_and_reports_20261021/`)**:
   - **853 files** copied from the Antigravity conversation brain/scratch directory into [`artifacts/re_proofs_and_reports_20261021/`](../artifacts/re_proofs_and_reports_20261021/):
     - [`como_funciona_futuramax_produccion.md`](../artifacts/re_proofs_and_reports_20261021/como_funciona_futuramax_produccion.md) — End-to-end production architecture & migration guide.
     - [`execution_plan_scorecard.md`](../artifacts/re_proofs_and_reports_20261021/execution_plan_scorecard.md) — Stage scorecard and milestone tracking.
     - [`physical_benchmarks_re1_report.md`](../artifacts/re_proofs_and_reports_20261021/physical_benchmarks_re1_report.md) — Physical benchmark and RE1 synthesis report.
     - [`scratch_proofs/`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/) — 850 JSON disassembly proofs, symbol maps, and verification scripts.
4. **Bench Execution Receipts & Captures (`artifacts/canary_panel1_guarida/`)**:
   - All bench scripts, preflight/postflight receipts, MTD hashes, and PCAP captures (`FMX-0015`).

---

## 2. Summary of Confirmed Static Binary Proofs (`WA.v8.7.25` & `XC.v8.7.25`)

### 2.1 What `mac80211.ko` (`sha256: 19a8fde6...`) on OpenWrt AP Actually Does (`CONFIRMED`)
- **Proof:** [`scratch_proofs/ap_mac80211_eth_p_teb_diff.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/)
- `/lib/modules/6.6.110/mac80211.ko` (`665,308` bytes, `sha256: 19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416`) contains a 71-byte patch in `ieee80211_data_to_8023_exthdr` that strips the inner `ETH_P_TEB` (`0x6558` Transparent Ethernet Bridging) header from 4-address WDS data frames sent by Stock `airOS 8` CPEs (`wds=1`).
- It does **not** inject Ubiquiti Vendor IEs into management frames; management IE injection in OpenWrt is controlled via `hostapd` (`vendor_elements` / `assocresp_elements` and `hostapd_cli set_vendor_elements`).

### 2.2 The 5 Association Gates in a Unmodified Stock `airOS 8` CPE (`CONFIRMED`)
When an unmodified Stock `airOS 8` CPE (`ubnt_op_mode=1`, stock `/etc/wpasupplicant_WPA-PSK.conf`, stock `ubnt_poll_host.ko`, stock `umac.ko`) scans and associates to an AP:

1. **Gate 1 — Userspace `wpa_supplicant` (`scan_UBNT` flag, `CONFIRMED`)**:
   - Stock `/etc/wpasupplicant_WPA-PSK.conf` sets `scan_UBNT=1`.
   - `/bin/wpa_supplicant` filters scan results in `wpa_supplicant_Select_Bss` unless the AP's Beacon/Probe Response includes a valid Ubiquiti Vendor IE (`dd ... 00:15:6d` or `00:27:22`) OR matches the expected Ubiquiti capabilities.
2. **Gate 2 — Kernel `ubnt_poll_host_on_beacon_rx` (`0x88b0`, `CONFIRMED`)**:
   - **Proofs:** [`beacon_rx_full.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/beacon_rx_full.json), [`ie_parse_and_Step1.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/ie_parse_and_Step1.json).
   - Called unconditionally by `umac.ko` (`ieee80211_recv_mgmt` `0x2c1d0` $\to$ `ieee80211_update_beacon` `0x2b8cc` $\to$ `ieee80211_parse_beacon` `0x2ab10`) on every received Beacon (`0x80`) and Probe Response (`0x50`).
   - Parses Ubiquiti IE `msg_type=1` (`ubnt_poll_host_ie_parse_Step1` at `0x4ca8`).
   - Requires `(ie->flags & 0x3) != 0` (`PTP`/`PTMP` capability bits) to add `bssid` to `handle->sta_list` (`0x10ec(handle)`).
   - **Critical behavior when `handle->connected_ap == NULL` (`0x10f0(handle)`):** If a Beacon or Probe Response arrives *without* the `msg_type=1` IE while `connected_ap == NULL`, `step=0` (`0x8b60`) immediately removes `bssid` from `handle->sta_list` (`0x10ec`)!
3. **Gate 3 — Kernel Scan Candidate Selection `ubnt_poll_host_is_ap_valid` (`0xa3a4`, `CONFIRMED`)**:
   - **Proof:** [`umac_45000.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/umac_45000.json).
   - Called from `umac.ko` (`0x45114`) right before sending `802.11 Auth Req`.
   - Checks both `ubnt_poll_host_scan_list_find(handle->scan_list, bssid)` (`0x119c`) AND `ubnt_poll_host_sta_list_find(handle->sta_list, bssid)` (`0x10ec`).
   - If `bssid` is missing from `sta_list`, `0x45114` logs `" - Reject from Airmax\n"` and blocks `802.11 Auth Req`.
4. **Gate 4 — Kernel `ubnt_poll_host_on_assoc_req_tx` (`0x92bc`) & `ubnt_poll_host_on_assoc_resp_rx` (`0xa05c`, `CONFIRMED`)**:
   - **Proof:** [`assoc_resp_rx.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/assoc_resp_rx.json).
   - **Path A (AirMAX TDMA AP — `bssid` present in `sta_list`):**
     - `on_assoc_req_tx` appends Ubiquiti IE `msg_type=2` (`140` bytes) and enables QCA988x firmware polling (`polling_enable=1` via `WMI 0x901f`).
     - `on_assoc_resp_rx` requires a valid `msg_type=3` IE (`140` bytes, valid `aid`, supported MCS mask, matching `ack_timeout`); if missing or invalid, it rejects the `Assoc Resp` (`return 1`).
   - **Path B (Normal AP CSMA/CA — `bssid` NOT in `sta_list` at `Assoc Req`/`Assoc Resp` time):**
     - If `bssid` was removed from `sta_list` (e.g., via a Beacon/Probe Response without Ubiquiti IE after `is_ap_valid` passed), `on_assoc_req_tx` (`0x92bc`) calls `ubnt_poll_host_ht_comm_tx(handle, msg_type=12/13, polling_enable=0)` to disable TDMA polling in the QCA988x radio firmware, logs `"Associating with normal AP"`, and sends a standard `Assoc Req`.
     - `on_assoc_resp_rx` (`0xa05c`) skips the `msg_type=3` requirement, logs `"Associated with Normal AP"`, and returns `0` (`ALLOW`).
5. **Gate 5 — Post-Association Polling & Watchdog Timers (`ubnt_poll_host_on_sta_connect` `0x83e4`, `CONFIRMED`)**:
   - **Proofs:** [`sta_connect_full.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/sta_connect_full.json), [`uph_timers_5e50.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/uph_timers_5e50.json), [`uph_timers_6a00.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/uph_timers_6a00.json).
   - If the CPE entered via **Path B (`Normal AP`)**, `ubnt_poll_host_on_sta_connect` (`0x83e4`) leaves `handle->connected_ap` (`0x10f0`) as `NULL`. Because all STA TDMA timers (`0x7800`, `0x77b0`, `0x5e90`, `0x6514`, `0x67a0`) check `if (handle->connected_ap == NULL) return;`, the CPE remains stably associated in standard 802.11ac CSMA/CA mode without TDMA poll timeouts!
   - Conversely, if the CPE entered via **Path A (`AirMAX AP`)**, `handle->connected_ap` is non-NULL and the CPE's QCA988x firmware has `polling_enable=1` (suppressing autonomous CSMA/CA TX until polled and disconnecting after ~10–15s if no TDMA polls arrive).

---

### 2.3 Stock `umac.ko` Channel, Bandwidth & Monitor Mode Mechanics (`CONFIRMED`)
- **Why `iwpriv ath0 mode 11ACVHT20` fails with `-EINVAL` (`8BF2: Invalid argument`) when `wifi0` is in `40 MHz` (`CONFIRMED`)**:
  - **Proof:** [`setmode_and_chanbw.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/setmode_and_chanbw.json).
  - In `ieee80211_ioctl_setmode` (`.text+0x9ac40..0x9ae04`) $\to$ `wlan_set_desired_phymode` (`.text+0xf64..0xfc8`), `.text+0xf80` checks `(1 << mode) & ic->ic_modecaps` (`0x670(ic)`).
  - While `wifi0` has `chanbw 40` (`ic->ic_chanbwflag`), `11ACVHT20` is excluded from `ic_modecaps`.
  - **Fix:** Run `iwpriv wifi0 chanbw 20` (which calls `ol_chanbw` at `.text+0xb3af0` and updates `ic_modecaps` to 20 MHz modes) **before** setting `mode 11ACVHT20` or `freq 5180M`.
- **Why `athchans -i athX 5180` requires an active scan or post-`ifconfig up` frequency set (`CONFIRMED`)**:
  - **Proofs:** [`athchans_proof.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/athchans_proof.json), [`vap_setup_and_setmode.json`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/vap_setup_and_setmode.json).
  - `athchans` (`SIOCIWFIRSTPRIV+20`) updates the allowed scan channel mask (`ic_chan_active`), not `ic_curchan` directly.
  - When a monitor VAP (`ath9`) is brought up via `ifconfig ath9 up`, `ieee80211_init` initializes its channel from `ic_ibss_chan` (`5165 MHz` default under `countrycode=511`) unless `iwconfig ath9 freq 5.18G` is executed **after** `ifconfig ath9 up` (or while another VAP holds `ic_curchan` at `5180 MHz`).

---

### 2.4 U-Boot `urescue` & Ethernet PHY (`AR8033` / `ATH_GMAC`) Recovery Mechanics (`CONFIRMED`)
- **Proofs:** [`urescue_real.txt`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/urescue_real.txt), [`uupdate_fw_detail.txt`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/uupdate_fw_detail.txt), [`ar8033_uboot.txt`](../artifacts/re_proofs_and_reports_20261021/scratch_proofs/ar8033_uboot.txt).
- Extracted and decompiled from `LAP-120` `mtd0` (`U-Boot 1.1.4-g79d032be`):
  - `urescue` listens on UDP port `69` (TFTP server at `192.168.1.20`), validates the `FW6` / `OPEN` header and `PART` CRCs via `fwcheck`, and flashes `kernel` (`mtd2`) + `rootfs` (`mtd3`).
  - `urescue -e` additionally erases `cfg` (`mtd4`, `0x9f040000..0x9f07ffff`).
