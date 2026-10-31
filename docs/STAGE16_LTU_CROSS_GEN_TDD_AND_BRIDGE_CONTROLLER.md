<!-- doc-head: STAGE16_LTU_CROSS_GEN_TDD_AND_BRIDGE_CONTROLLER.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 16A — LTU Cross-Generation TDD (`cz_len=3` vs `cz_len=6`) Compatibility Controller, `AMEIMG`/NAND Safety Verifier & `NanoStation 5AC Loco` L2 Bridge Detector

**Date:** 2026-10-25  
**Task ID:** `T-S16-LTU-FW-PARITY-AND-L2-BRIDGE` (`subagent:multiradio-autoresearch`)  
**Controller Implementation:** [`controller/ltu_cross_gen_tdd_and_bridge_controller.py`](../controller/ltu_cross_gen_tdd_and_bridge_controller.py)  
**JSON Audit Receipt:** [`artifacts/autoresearch/stage16_ltu_cross_gen_tdd_audit_20261025.json`](../artifacts/autoresearch/stage16_ltu_cross_gen_tdd_audit_20261025.json)  
**Unit Test Suite:** [`tests/test_ltu_cross_gen_tdd_and_bridge_controller.py`](../tests/test_ltu_cross_gen_tdd_and_bridge_controller.py)

---

## 1. Executive Summary

Stage 16A builds a strictly offline diagnostic, firmware verification, and Layer-2 bridge detection controller (`controller/ltu_cross_gen_tdd_and_bridge_controller.py`) grounded in the live 3-unit LTU PtMP sector measurements from Stage 15 ([`artifacts/autoresearch/stage15_ltu_ptmp_sector_20261025.json`](../artifacts/autoresearch/stage15_ltu_ptmp_sector_20261025.json)) and the held LTU `v2.4.2` firmware containers:

1. **Cross-Generation TDD Boundary (`aflturocket.v2.1.0` $\leftrightarrow$ `afltu.v2.4.0` — `CONFIRMED`)**:
   - Models and parses `/sys/class/ame/ame_ctrl_dev/bandwidthConfig` (`common_info`) and kernel `dmesg` logs (`ame_core_isr_giveup_region_calc` and `bbp_mrx_foe_cir_getTD_forPdet`).
   - On `5825 MHz` (`20 MHz`, `2000 us` frame, `750` duty cycle, `dl_symbols=61`, `ul_symbols=19`, `gap0=960`, `gap1=960`), `LTU-Rocket` (`aflturocket.v2.1.0`, `2020-07-03`) programs **`cz_len = 3`** and **`tx_isr_sample = 3852` (`SYM#7`)**, whereas `LTU-Lite #1/#2` (`afltu.v2.4.0`, `2025-04-25`) program **`cz_len = 6`** and **`tx_isr_sample = 2465` (`SYM#4`)** ($\Delta \text{cz\_len} = +3$, $\Delta \text{tx\_isr\_sample} = -1387$ samples).
   - While both `v2.4.0` CPEs achieve crystal lock, `SFOLoop` lock, decode the `v2.1.0` AP beacon (`PUBLIC_TERM_0006`, `PUBLIC_DEVICE_0050`), reach `cpeFsmInitDone`, and clear `__LINK_STATE_NOCARRIER`, the `v2.4.0` kernel immediately logs `ame_core_isr_giveup_region_calc(6783): Not Support!` followed by `bbp_mrx_foe_cir_getTD_forPdet(1213): Timeout in 24657us`.
   - Upgrading `LTU-Rocket` to `aflturocket-2.4.2.261009.bin` aligns both AP and CPE to `cz_len = 6` and `tx_isr_sample = 2465` (`SYM#4`).
2. **Held `v2.4.2` `AMEIMG` Container & NAND Safety Guards (`CONFIRMED`)**:
   - Verifies all **10 parts** of `aflturocket-2.4.2.261009.bin` (`38,918,528` B; `spl`, `uboot`, `dtb`, `kernel`, `rootfs`, `fpga`, `socfpga-uboot`, `socfpga-dtb`, `socfpga-kernel`, `socfpga-rootfs`) and all **5 parts** of `afltu-2.4.2.261009.bin` (`24,366,210` B; `spl`, `uboot`, `dtb`, `kernel`, `rootfs`) with `0` trailing bytes and `100%` matching embedded MD5 digests.
   - Enforces the `amesoc3` Device Tree (`part02_dtb.bin`, `F08`) NAND partition map, strictly blocking any write overlapping `0x00000000..0x00300000` — specifically protecting `uboot` (`0x00140000..0x00240000`) and `EEPROM` (`0x00240000..0x00300000`).
3. **Non-Intrusive `NanoStation 5AC Loco` L2 Bridge Detector (`detect_ltu_rocket_via_loco_bridge`)**:
   - Parses `bridge fdb show`, `brctl showmacs br0`, and `ip -6 neigh` outputs from `NanoStation 5AC Loco` (`198.18.0.42`, `eth0` `PUBLIC_DEVICE_0036`) to detect when `LTU-Rocket` (`MAC PUBLIC_DEVICE_0050` / `PUBLIC_DEVICE_0051`) is connected to the `LAN` port of the `NanoStation 5AC Loco` PoE injector.

---

## 2. Cross-Generation TDD Frame & ISR Boundary Table (`[20-2000-750]`)

| Parameter | `LTU-Rocket` (`aflturocket.v2.1.0`) | `LTU-Lite` (`afltu.v2.4.0`) | `LTU-Rocket` (`aflturocket.v2.4.2` Target) | Status / Impact |
| :--- | :---: | :---: | :---: | :--- |
| `bandwidth` (`MHz`) | `20` | `20` | `20` | Aligned (`22.4 MS/s` sample rate) |
| `frame_period` (`us`) | `2000` | `2000` | `2000` | Aligned |
| `duty_cycle` (`‰`) | `750` (`75%`) | `750` (`75%`) | `750` (`75%`) | Aligned |
| `dl_symbols` / `ul_symbols` | `61` / `19` | `61` / `19` | `61` / `19` | Aligned |
| `gap0` / `gap1` (samples) | `960` / `960` | `960` / `960` | `960` / `960` | Aligned |
| **`cz_len` (Cyclic Zone)** | **`3`** | **`6`** | **`6`** | **`+3` symbol mismatch (`v2.1.0` vs `v2.4.0`)** |
| `rx_isr_sample` (`SYM#`) | `1172` (`SYM#2`) | `1172` (`SYM#2`) | `1172` (`SYM#2`) | Aligned |
| **`tx_isr_sample` (`SYM#`)** | **`3852` (`SYM#7`)** | **`2465` (`SYM#4`)** | **`2465` (`SYM#4`)** | **`-1387` sample shift (`SYM#7` $\rightarrow$ `SYM#4`)** |
| `ame_core_isr_giveup_region_calc` | Supported (`line 6377`) | `Not Support!` (`line 6783`) on `v2.1.0` frame | Supported (`cz_len=6`, `SYM#4`) | Requires AP firmware parity (`v2.4.x`) |

---

## 3. Verified `AMEIMG` Container Parts & Primary `amesoc3` NAND Safety Map

### 3.1 `AMEIMG` Container Parts (`0` Trailing Bytes, `15/15` Embedded MD5s Verified)

| Index | Canonical Alias | Raw Header Name | `aflturocket-2.4.2.261009.bin` (`38,918,528` B) | `afltu-2.4.2.261009.bin` (`24,366,210` B) | Target Subsystem |
| :---: | :--- | :--- | :---: | :---: | :--- |
| `0` | `spl` | `spl` | `524,288` B (`MD5: 647ff21a...`) | `524,288` B (`MD5: 9ec57f3d...`) | Primary `amesoc3` SPL |
| `1` | `uboot` | `uboot` | `318,096` B (`MD5: 7b7999c4...`) | `319,344` B (`MD5: f82f4cf4...`) | Primary `amesoc3` U-Boot |
| `2` | `dtb` | `dtb` | `6,605` B (`MD5: f6eb7285...`) | `6,554` B (`MD5: 63cc45a9...`) | Primary `amesoc3` Device Tree |
| `3` | `kernel` | `kernel` | `3,330,408` B (`MD5: c852580e...`) | `3,330,408` B (`MD5: c852580e...`) | Primary Linux `3.14.65` uImage |
| `4` | `rootfs` | `rootfs` | `19,398,656` B (`MD5: 34857397...`) | `20,185,088` B (`MD5: 56b5b44c...`) | Primary UBI/SquashFS RootFS |
| `5` | `fpga` | `HPS FPGA rbf file` | `5,490,084` B (`MD5: 0787e883...`) | *(Absent)* | Arria 10 `.rbf` FPGA Bitstream |
| `6` | `socfpga-uboot` | `HPS U-Boot file` | `1,048,576` B (`MD5: 428be654...`) | *(Absent)* | Arria 10 HPS U-Boot |
| `7` | `socfpga-dtb` | `HPS device tree` | `18,095` B (`MD5: afb4b13a...`) | *(Absent)* | Arria 10 HPS Device Tree |
| `8` | `socfpga-kernel` | `HPS Linux Kernel` | `3,658,656` B (`MD5: 771fe5da...`) | *(Absent)* | Arria 10 HPS Linux `4.14.0 SMP` |
| `9` | `socfpga-rootfs` | `HPS RootFS image` | `5,124,096` B (`MD5: efb32b2b...`) | *(Absent)* | Arria 10 HPS SquashFS RootFS |

### 3.2 Primary `amesoc3` NAND Partition Safety Guard (`verify_nand_write_safety`)

| Partition Label | Address Range | Size | Guard Disposition |
| :--- | :---: | :---: | :--- |
| `spl` | `0x00000000..0x00080000` | `512 KB` | **BLOCKED (Protected Preloader)** |
| `uboot_env0` / `uboot_env1` | `0x00080000..0x00140000` | `768 KB` | **BLOCKED (Protected U-Boot Env)** |
| **`uboot`** | **`0x00140000..0x00240000`** | **`1,024 KB`** | **BLOCKED (Critical `F08` Boundary — Never Touch `0x00160000`/`0x00180000`)** |
| **`EEPROM`** | **`0x00240000..0x00300000`** | **`768 KB`** | **BLOCKED (Protected RF Calibration / MAC / Board Data)** |
| `cfg` | `0x00300000..0x003c0000` | `768 KB` | Writable via `cfgmtd` only when explicitly authorized |
| `dtb0` / `kernel0` / `rootfs0` | `0x003c0000..0x03120000` | `46,464 KB` | Writable via `fwupdate.real` Bank 0 |
| `dtb1` / `kernel1` / `rootfs1` | `0x03120000..0x05e80000` | `46,464 KB` | Writable via `fwupdate.real` Bank 1 |

---

## 4. Non-Intrusive `NanoStation 5AC Loco` L2 Bridge Detector

When `LTU-Rocket` (`MAC PUBLIC_DEVICE_0050`, `PUBLIC_DEVICE_0051`) is physically plugged into the secondary `LAN` port of the `NanoStation 5AC Loco` (`198.18.0.42`, `eth0` `PUBLIC_DEVICE_0036`) PoE injector so that it can reach the bench network over the wireless `LAP-120` $\leftrightarrow$ `Loco 5AC` link without occupying an `EdgeSwitch 10XP` port:
- `detect_ltu_rocket_via_loco_bridge()` inspects `bridge fdb show`, `brctl showmacs br0`, and `ip -6 neigh` outputs.
- It filters out `permanent`/`local` bridge self-entries and confirms `detected=True` with exact `matched_macs`, `matched_ipv6_addresses`, `bridge_port_interface="eth0"`, `bridge_port_number=1`, and `evidence_sources`.
