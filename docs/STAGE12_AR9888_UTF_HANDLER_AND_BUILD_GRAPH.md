<!-- doc-head: STAGE12_AR9888_UTF_HANDLER_AND_BUILD_GRAPH.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — AR9888 UTF Command Handler Tracer & Build-Graph Inventory (Workstreams E3 + E4)

## 1. Executive Summary

This document records the deterministic static analysis of the **QCA988x / AR9888 ("Peregrine") Unit Test Firmware (`UTF`)** command dispatch pipeline (Workstream E3) and the **`TARGET=AR9888` UTF build graph** (Workstream E4), derived from the commit-pinned `SpaceExplorationTechnologies/starlink-wifi@1d585ee8909bf7bab4391c0c52d8a9d44137b3bb` source tree (`Q01..Q10`).

All tooling and structured outputs are implemented in:
- [`tools/qca988x/trace_utf_handlers.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/qca988x/trace_utf_handlers.py)
- [`tools/qca988x/utf_build_inventory.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/qca988x/utf_build_inventory.py)
- [`artifacts/qca988x/ar9888_utf_handler_and_build_matrix.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/qca988x/ar9888_utf_handler_and_build_matrix.json)

---

## 2. Workstream E3: AR9888 UTF Command-to-Handler Trace (`CONFIRMED`)

Every TLV2, SYSCMD, and legacy WMI TCMD command was traced across four layers:
1. **Command Dictionary (`Q07` / `Q04`)**: `dl/wlan/halphy_tools/common/tlv2p0/include/cmdRspParmsDict.h` and `dl/include/testcmd_ar988x.h`.
2. **Parser / Parameter Schema (`Q09` / `Q10`)**: `cmdAdcCaptureHandler.h`, `cmdGenWaveformHandler.h`, and `tlv2p0` auto-generated command parameter structures.
3. **Target Registration (`Q08`)**: `initCmdProcessTlv2()` in `dl/wlan/halphy_tools/target/utf/commonUTF/cmdProcessTlv2.c` (lines `950-967`).
4. **Target Execution (`Q08` / `Q03`)**: Handler implementations in `cmdProcessTlv2.c` and `dl/wlan/halphy_tools/target/utf/tcmd_utf/tcmd.c`.

### 2.1 Complete Command Classification Matrix

| Command Name | ID | Response Name / ID | Layer | Registered in `AR9888` (`Q08`/`Q03`)? | Target Handler Symbol | Read-Only Safe? | Classification |
| :--- | ---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **`CMD_REGREAD`** | `9` | `CMD_REGREADRSP` (`10`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:952`) | `regReadHandler` | **Yes** | **`EXACT_AR9888`** |
| **`CMD_REGWRITE`** | `11` | `CMD_REGWRITERSP` (`12`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:953`) | `regWriteHandler` | No | **`EXACT_AR9888`** |
| **`CMD_TX`** | `14` | `CMD_BASICRSP` (`13`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:954`) | `txHandler` | No | **`EXACT_AR9888`** |
| **`CMD_TXSTATUS`** | `15` | `CMD_TXSTATUSRSP` (`16`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:955`) | `txStatusHandler` | **Yes** (`stopTx=0`) | **`EXACT_AR9888`** |
| **`CMD_RX`** | `17` | `CMD_RXRSP` (`21`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:956`) | `rxHandler` | No | **`EXACT_AR9888`** |
| **`CMD_RXSTATUS`** | `18` | `CMD_RXSTATUSRSP` (`19`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:957`) | `rxStatusHandler` | **Yes** (`stopRx=0`) | **`EXACT_AR9888`** |
| **`CMD_HWCAL`** | `20` | `CMD_BASICRSP` (`13`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:958`) | `hwCalHandler` | No | **`EXACT_AR9888`** |
| **`CMD_MEMWRITE`** | `40` | `CMD_MEMWRITERSP` (`41`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:959`) | `memWriteHandler` | No | **`EXACT_AR9888`** |
| **`CMD_MEMREAD`** | `42` | `CMD_MEMREADRSP` (`43`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:960`) | `memReadHandler` | **Yes** | **`EXACT_AR9888`** |
| **`CMD_ADCCAPTURE`** | `59` | `CMD_ADCCAPTURERSP` (`60`) | `TLV2_EXTCMD` | **No** (`#ifdef USE_TLV2_EXTCMD` only) | `None` | No | **`SHARED_ONLY`** |
| **`CMD_GENWAVEFORM`** | `61` | `CMD_GENWAVEFORMRSP` (`62`) | `TLV2_EXTCMD` | **No** (`#ifdef USE_TLV2_EXTCMD` only) | `None` | No | **`SHARED_ONLY`** |
| **`CMD_LMQUERY`** | `76` | `CMD_LMQUERYRSP` (`77`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:963`) | `LMQueryHandler` | **Yes** | **`EXACT_AR9888`** |
| **`CMD_NOISEFLOORREAD`** | `102` | `CMD_NOISEFLOORREADRSP` (`103`) | `TLV2_CMD` | **Yes** (`cmdProcessTlv2.c:966`) | `noiseFloorReadHandler` | No (calls `whalReset`) | **`EXACT_AR9888`** |
| **`SYSCMD_PHYDBGDUMP`** | `10009` | `SYSCMD_PHYDBGDUMPRSP` (`10010`) | `TLV2_SYSCMD` | **No** | `None` | Yes | **`SHARED_ONLY`** |
| **`TCMD_CONT_TX_ID`** | `0` | `TCMD_CONT_TX_REPLY` (`0`) | `WMI_TCMD_TLV` | **Yes** (via `TC_CMD_TLV_ID` / `txCmdProcessor`) | `tcmd_cont_tx_cmd` | No | **`EXACT_AR9888`** |
| **`TCMD_CONT_RX_ID`** | `1` | `TCMD_CONT_RX_REPLY` (`1`) | `WMI_TCMD_TLV` | **Yes** (via `TC_CMD_TLV_ID` / `rxCmdProcessor`) | `tcmd_cont_rx_cmd` | No (`REPORT` is passive) | **`EXACT_AR9888`** |
| **`TCMD_SET_REG_ID`** | `5` | `None` | `WMI_TCMD_LEGACY` | **No** (omitted from `tcmd_parse_cmd` switch) | `None` | No | **`NOT_FOUND`** |

### 2.2 Critical Findings on `ADCCAPTURE` (`59`), `GENWAVEFORM` (`61`), and `TCMD_SET_REG_ID` (`5`)

1. **`CMD_ADCCAPTURE` (`59`) and `CMD_GENWAVEFORM` (`61`) are `SHARED_ONLY` (`CONFIRMED`)**:
   - Both commands have auto-generated parameter headers in `dl/wlan/halphy_tools/common/tlv2p0/include/` (`cmdAdcCaptureHandler.h` `Q09` and `cmdGenWaveformHandler.h` `Q10`) defining `dataI[2048]` and `dataQ[2048]` (`A_UINT16`) arrays under `#ifdef USE_TLV2_EXTCMD`.
   - However, `initCmdProcessTlv2()` in `dl/wlan/halphy_tools/target/utf/commonUTF/cmdProcessTlv2.c` (`Q08`, lines `950-967`) **never registers** `ADCCAPTURE` or `GENWAVEFORM` for `AR9888`.
   - Instead, on `AR9888`, waveform/tone generation in UTF is performed via `tcmd_cont_tx_sine()`, `tcmd_cont_tx_cwtone()`, and `tcmd_cont_tx_clpcpkt()` inside `tcmd.c` (`Q03`, lines `2143-2215`).
2. **`CMD_MEMREAD` (`42`) and `CMD_REGREAD` (`9`) are unconditionally wired (`EXACT_AR9888`, `CONFIRMED`)**:
   - `memReadHandler` (`cmdProcessTlv2.c:68-102`) reads up to `255` bytes per call via `hwMemRead32((A_UINT16)currentDevIndex, addr)` without calling `isValidReg()`, returning `CMD_MEMREADRSP` (`43`).
   - `regReadHandler` (`cmdProcessTlv2.c:147-176`) checks `isValidReg(pParms->regaddress)` and `regaddress % 4 == 0`, reads the 32-bit word via `hwMemRead32()`, and returns `CMD_REGREADRSP` (`10`).
3. **Legacy `TCMD_SET_REG_ID` (`5`) is `NOT_FOUND` in `tcmd_parse_cmd()` (`CONFIRMED`)**:
   - While `TCMD_SET_REG` (`testCmdId = 5`) is declared in `dl/include/testcmd_ar988x.h` (`Q04`), `tcmd_parse_cmd()` in `tcmd.c` (`Q03:1157-1231`) only accepts `TC_CMD_TLV_ID` (`4`) and `TC_CMDS_ID` (`3`) (with `TCMD_CONT_TX_ID` and `TCMD_CONT_RX_ID` wrapped in `#if 0` and routed through TLV). Sending raw `TCMD_SET_REG_ID` directly over `WMI_PDEV_UTF_CMDID` returns `A_ERROR`; TLV2 `CMD_REGREAD`/`CMD_REGWRITE` or host CE diagnostic window reads/writes must be used instead.

---

## 3. Workstream E4: `TARGET=AR9888` UTF Build-Graph Inventory (`CONFIRMED`)

Inspection of `dl/wlan/halphy_tools/target/Makefile` (`Q01`) and `dl/wlan/halphy_tools/target/utf/Makefile` (`Q02`) reveals the exact directory hierarchy and external build dependencies for `TARGET=AR9888`:

### 3.1 Makefile Subdirectory Graph (`Q01`, `Q02`)

- **Top-level `TARGET=AR9888` (`Q01`)**:
  - `SUBDIRS += eeprom lib otpdump utf wlansetup utfsetup` (plus `qvit` if `QVIT_BUILD=y`).
- **UTF Subtree (`Q02`, `dl/wlan/halphy_tools/target/utf/Makefile`)**:
  - `SUBDIRS = commonUTF device tcmd_utf testScriptIF wmiHostIF utf_cal`

### 3.2 Present vs. Missing Build Dependencies

| Dependency ID | Category | Component / Path | Present in Public Repo? | Blocker Severity |
| :--- | :--- | :--- | :--- | :--- |
| **`DEP-UTF-01`** | `PUBLIC_UTF_SOURCE_SUBTREE` | `dl/wlan/halphy_tools/target/utf/*` (`tcmd.c`, `cmdProcessTlv2.c`, etc.) | **Yes** | `NONE` |
| **`DEP-UTF-02`** | `PUBLIC_TLV2_COMMON_LIBRARY` | `dl/wlan/halphy_tools/common/tlv2p0/*` (`cmdRspParmsDict.h`, parsers) | **Yes** | `NONE` |
| **`DEP-UTF-03`** | `PUBLIC_AR9888_HW_HEADERS` | `dl/include/AR9888/v2/*` (`rx_ppdu_end.h`, `tx_ppdu_start.h`, `bb_lc_reg.h`) | **Yes** | `NONE` |
| **`DEP-UTF-04`** | `MISSING_PRIVATE_COMPONENT_TREE` | `$(MAC_CORE_COMPONENT_DIR)/src/wal/{include,whal/include,AR/include,AR/tx,AR/rx}` (`waltest_tx`, `waltest_rx`, `whalReset`) | **No** | **`HARD_BUILD_BLOCKER`** |
| **`DEP-UTF-05`** | `MISSING_PRIVATE_COMPONENT_TREE` | `$(HALPHY_COMPONENT_DIR)/include` (`halphy_reset.h`, `whalDoCalibration`) | **No** | **`HARD_BUILD_BLOCKER`** |
| **`DEP-UTF-06`** | `MISSING_PRIVATE_COMPONENT_TREE` | `$(PROTOCOL_COMPONENT_DIR)/include`, root target `Makefile`, AR9888 ROM symbol linker script (`rom.addrs.ld`) | **No** | **`HARD_BUILD_BLOCKER`** |
| **`DEP-UTF-07`** | `PROPRIETARY_TOOLCHAIN` | Cadence Tensilica Xtensa compiler (`xt-xcc` for `AR9888` core configuration) | **No** | `SOFT_TOOLCHAIN_BLOCKER` |

### 3.3 Strategic Conclusion for Phase 0 / Stage 2 Lab Execution

Because `MAC_CORE_COMPONENT_DIR` (`wal`/`whal`), `HALPHY_COMPONENT_DIR`, `PROTOCOL_COMPONENT_DIR`, and the `AR9888` ROM linker scripts are proprietary Qualcomm Atheros components excluded from the public `starlink-wifi` tarball (`DEP-UTF-04..06`), **recompiling a fresh `utf.bin` from source is blocked**.

Instead, FuturaMAX / openMAX has two **immediately executable, zero-recompilation paths**:
1. **Production `firmware-5.bin` + Host CE Diagnostic Window (`ath10k_pci_diag_read_mem` / `debugfs`)**: Read target DRAM (`0x00400000..0x0044ffff`) and memory-mapped baseband registers (`0x00009b00`, `0x0000ab00`, `0x0000a370`) directly from the host driver or via a minimal binary patch to existing `firmware-5.bin`.
2. **Existing Binary `utf.bin` + TLV2 `CMD_REGREAD` (`9`) / `CMD_MEMREAD` (`42`)**: Drive existing prebuilt `utf.bin` blobs on lab bench hardware using TLV2 `CMD_REGREAD`, `CMD_REGWRITE`, `CMD_MEMREAD`, `CMD_MEMWRITE`, `CMD_TXSTATUS`, and `CMD_RXSTATUS`.
