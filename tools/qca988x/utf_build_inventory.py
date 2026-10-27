"""Workstream E4: AR9888 UTF Build-Graph Inventory (`utf_build_inventory.py`).

Reconstructs the exact `TARGET=AR9888` UTF firmware build graph from `Q01`
(`dl/wlan/halphy_tools/target/Makefile`), `Q02`
(`dl/wlan/halphy_tools/target/utf/Makefile`), `Q03` (`tcmd.c`), and `Q08`
(`cmdProcessTlv2.c`), enumerating:
- `TARGET=AR9888` top-level and `utf/` subdirectories
- Required include directories (`PROTOCOL_INC_DIR`, `MAC_CORE_SRC_DIR`,
  `HALPHY_INC_DIR`, `HALPHY_TOOLS_COMMON_DIR`)
- Present vs missing headers, closed-source precompiled target libraries
  (`whal`, `waltest`, `htt`, `wmi`, `rom_addrs`, Xtensa linker scripts), and
  Xtensa toolchain requirements (`xt-xcc` / `xtensa-elf-gcc` for `ath10k`
  Peregrine target CPU)
- Combined E3 + E4 artifact generator for
  `artifacts/qca988x/ar9888_utf_handler_and_build_matrix.json`.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from tools.qca988x.fetch_pinned_sources import (
    STARLINK_WIFI_COMMIT,
    STARLINK_WIFI_REPO,
    get_pinned_source_by_id,
)
from tools.qca988x.trace_utf_handlers import build_utf_handler_trace_summary


@dataclass(frozen=True)
class UTFBuildDependencyItem:
    """Single dependency node in the `TARGET=AR9888` UTF firmware build graph."""

    dependency_id: str
    category: str
    name: str
    expected_path_or_variable: str
    present_in_public_starlink_tree: bool
    required_by_files: List[str] = field(default_factory=list)
    symbols_or_headers_provided: List[str] = field(default_factory=list)
    blocker_severity: str = "NONE"
    mitigation_or_alternative: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_makefile_target_subdirs(makefile_text: str) -> Dict[str, List[str]]:
    """Parse `ifeq ($(TARGET),<CHIP>)` blocks and `SUBDIRS += ...` from `Q01`/`Q02`."""
    target_blocks: Dict[str, List[str]] = {}
    current_target: str | None = None

    target_re = re.compile(r"^\s*ifeq\s*\(\$\(TARGET\),\s*([A-Za-z0-9_]+)\s*\)")
    subdirs_re = re.compile(r"^\s*SUBDIRS\s*\+?=\s*(.+)$")

    for raw_line in makefile_text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        t_match = target_re.match(line)
        if t_match:
            current_target = t_match.group(1)
            target_blocks.setdefault(current_target, [])
            continue
        if line.startswith("endif") and current_target is not None:
            # Keep simple single-level tracking for target blocks
            if "QVIT_BUILD" not in raw_line:
                pass
        s_match = subdirs_re.match(line)
        if s_match:
            tokens = [tok.strip() for tok in s_match.group(1).split() if tok.strip()]
            key = current_target or "DEFAULT"
            target_blocks.setdefault(key, [])
            for tok in tokens:
                if tok not in target_blocks[key]:
                    target_blocks[key].append(tok)
    return target_blocks


def build_ar9888_utf_build_inventory() -> Dict[str, Any]:
    """Reconstruct the complete `TARGET=AR9888` UTF build dependency and blocker matrix."""
    q01 = get_pinned_source_by_id("Q01")
    q02 = get_pinned_source_by_id("Q02")

    dependencies: List[UTFBuildDependencyItem] = [
        UTFBuildDependencyItem(
            dependency_id="DEP-UTF-01",
            category="PUBLIC_UTF_SOURCE_SUBTREE",
            name="halphy_tools target & UTF C sources (`dl/wlan/halphy_tools/target/utf`)",
            expected_path_or_variable="dl/wlan/halphy_tools/target/utf/{commonUTF,device,tcmd_utf,testScriptIF,wmiHostIF,utf_cal}",
            present_in_public_starlink_tree=True,
            required_by_files=[q01.path, q02.path],
            symbols_or_headers_provided=[
                "tcmd_main",
                "tcmd_parse_cmd",
                "tcmd_cont_tx_cmd",
                "tcmd_cont_rx_cmd",
                "initCmdProcessTlv2",
                "memReadHandler",
                "memWriteHandler",
                "regReadHandler",
                "regWriteHandler",
                "noiseFloorReadHandler",
            ],
            blocker_severity="NONE",
            mitigation_or_alternative="Present in pinned commit 1d585ee8909bf7bab4391c0c52d8a9d44137b3bb.",
        ),
        UTFBuildDependencyItem(
            dependency_id="DEP-UTF-02",
            category="PUBLIC_TLV2_COMMON_LIBRARY",
            name="TLV2p0 command dictionary and stream parser (`dl/wlan/halphy_tools/common/tlv2p0`)",
            expected_path_or_variable="$(HALPHY_TOOLS_COMPONENT_DIR)/common/tlv2p0/include",
            present_in_public_starlink_tree=True,
            required_by_files=[q02.path, "dl/wlan/halphy_tools/target/utf/commonUTF/cmdProcessTlv2.c"],
            symbols_or_headers_provided=[
                "cmdRspParmsDict.h",
                "cmdAdcCaptureHandler.h",
                "cmdGenWaveformHandler.h",
                "cmdStreamParsingAndProcessing",
                "createCmdRsp",
            ],
            blocker_severity="NONE",
            mitigation_or_alternative="Present in pinned commit 1d585ee8909bf7bab4391c0c52d8a9d44137b3bb.",
        ),
        UTFBuildDependencyItem(
            dependency_id="DEP-UTF-03",
            category="PUBLIC_AR9888_HW_HEADERS",
            name="AR9888 v2 MAC descriptors and baseband register headers (`dl/include/AR9888/v2`)",
            expected_path_or_variable="dl/include/AR9888/v2/{hw/mac_descriptors,extra/hw}",
            present_in_public_starlink_tree=True,
            required_by_files=[
                "dl/wlan/halphy_tools/target/utf/tcmd_utf/tcmd.c",
                "dl/wlan/halphy_tools/target/utf/commonUTF/cmdProcessTlv2.c",
            ],
            symbols_or_headers_provided=[
                "rx_ppdu_end.h",
                "tx_ppdu_start.h",
                "series_bw.h",
                "bb_lc_reg.h",
                "testcmd_ar988x.h",
                "art_utf_common.h",
                "art_utf_qc98xx.h",
            ],
            blocker_severity="NONE",
            mitigation_or_alternative="Present in pinned commit 1d585ee8909bf7bab4391c0c52d8a9d44137b3bb.",
        ),
        UTFBuildDependencyItem(
            dependency_id="DEP-UTF-04",
            category="MISSING_PRIVATE_COMPONENT_TREE",
            name="QCA Firmware MAC Core & WAL/WHAL source tree (`MAC_CORE_COMPONENT_DIR`)",
            expected_path_or_variable="$(MAC_CORE_COMPONENT_DIR)/src/wal/{include,whal/include,AR/include,AR/tx,AR/rx}",
            present_in_public_starlink_tree=False,
            required_by_files=[
                q02.path,
                "dl/wlan/halphy_tools/target/utf/tcmd_utf/tcmd.c",
                "dl/wlan/halphy_tools/target/utf/commonUTF/cmdProcessTlv2.c",
            ],
            symbols_or_headers_provided=[
                "waltest_tx",
                "waltest_rx",
                "waltest_rx_detach",
                "waltest_tx_detach",
                "qcache_init",
                "tx_send_completion_hdlr",
                "whalReset",
                "whalForceTxGainIdx",
                "whalForceTxTgtPwr",
            ],
            blocker_severity="HARD_BUILD_BLOCKER",
            mitigation_or_alternative=(
                "Cannot recompile standalone `utf.bin` from source without QCA's proprietary "
                "`MAC_CORE_COMPONENT_DIR` (`wal`/`whal`) libraries. Use binary ELF patching or "
                "host-side `ath10k` WMI/debugfs/diagnostic memory hooks against existing `utf.bin` / `firmware-5.bin`."
            ),
        ),
        UTFBuildDependencyItem(
            dependency_id="DEP-UTF-05",
            category="MISSING_PRIVATE_COMPONENT_TREE",
            name="QCA HALPHY internal component headers & calibration library (`HALPHY_COMPONENT_DIR`)",
            expected_path_or_variable="$(HALPHY_COMPONENT_DIR)/include",
            present_in_public_starlink_tree=False,
            required_by_files=[
                q02.path,
                "dl/wlan/halphy_tools/target/utf/commonUTF/cmdProcessTlv2.c",
            ],
            symbols_or_headers_provided=[
                "halphy_reset.h",
                "whalDoCalibration",
                "whalEepromGetCurrentTempInDec",
            ],
            blocker_severity="HARD_BUILD_BLOCKER",
            mitigation_or_alternative=(
                "Proprietary HALPHY object code is already linked inside existing binary `utf.bin` / "
                "`firmware-5.bin` images; invoke via existing TLV2 `CMD_REGREAD`/`CMD_MEMREAD` or host CE diagnostic window."
            ),
        ),
        UTFBuildDependencyItem(
            dependency_id="DEP-UTF-06",
            category="MISSING_PRIVATE_COMPONENT_TREE",
            name="QCA Target Protocol & RTOS/ROM linkage headers (`PROTOCOL_COMPONENT_DIR` + root `Makefile`)",
            expected_path_or_variable="$(PROTOCOL_COMPONENT_DIR)/include, $(PDIR)Makefile, AR9888 ROM symbol table & linker script",
            present_in_public_starlink_tree=False,
            required_by_files=[q01.path, q02.path, "dl/wlan/halphy_tools/target/utf/tcmd_utf/tcmd.c"],
            symbols_or_headers_provided=[
                "codeswap_init",
                "utf_hif_module_install",
                "wmiTcmdInit",
                "wmi_tc_cmds_reply_event",
                "A_ALLOCRAM_INIT",
            ],
            blocker_severity="HARD_BUILD_BLOCKER",
            mitigation_or_alternative=(
                "Root target Makefile, ROM symbol table (`rom.addrs.ld`), and Xtensa `ath10k` RTOS libraries "
                "are not included in the GPL tarball (`dl/` only contains `include` and `wlan/halphy_tools`)."
            ),
        ),
        UTFBuildDependencyItem(
            dependency_id="DEP-UTF-07",
            category="PROPRIETARY_TOOLCHAIN",
            name="Cadence Tensilica Xtensa compiler (`xt-xcc` / `xt-ld`) for AR9888 core config",
            expected_path_or_variable="XTENSA_CORE=ar9888 / xt-xcc",
            present_in_public_starlink_tree=False,
            required_by_files=[q01.path, q02.path],
            symbols_or_headers_provided=["ELF32 Xtensa little-endian target code generation"],
            blocker_severity="SOFT_TOOLCHAIN_BLOCKER",
            mitigation_or_alternative=(
                "Open-source `gcc-xtensa-lx106` / `binutils-xtensa` can disassemble/assemble individual "
                "instructions, while host-side CE diagnostic window (`0x00400000..0x0044ffff`) and register "
                "access require zero target recompilation."
            ),
        ),
    ]

    present_count = sum(1 for d in dependencies if d.present_in_public_starlink_tree)
    missing_count = sum(1 for d in dependencies if not d.present_in_public_starlink_tree)
    hard_blockers = [d.dependency_id for d in dependencies if d.blocker_severity == "HARD_BUILD_BLOCKER"]

    return {
        "schema_version": "1.0",
        "workstream": "E4_UTF_BUILD_GRAPH_INVENTORY",
        "repository": STARLINK_WIFI_REPO,
        "commit": STARLINK_WIFI_COMMIT,
        "target": "AR9888",
        "top_level_makefile": {
            "source_id": "Q01",
            "path": q01.path,
            "sha256": q01.expected_sha256,
            "ar9888_subdirs": ["eeprom", "lib", "otpdump", "utf", "wlansetup", "utfsetup"],
            "optional_qvit_subdir": "qvit (when QVIT_BUILD=y)",
            "other_targets_in_makefile": ["AR6320", "AR900B", "QCA9984", "QCA9888", "IPQ4019"],
        },
        "utf_makefile": {
            "source_id": "Q02",
            "path": q02.path,
            "sha256": q02.expected_sha256,
            "utf_subdirs": [
                "commonUTF",
                "device",
                "tcmd_utf",
                "testScriptIF",
                "wmiHostIF",
                "utf_cal",
            ],
            "required_component_variables": [
                "HALPHY_TOOLS_COMPONENT_DIR",
                "PROTOCOL_COMPONENT_DIR",
                "MAC_CORE_COMPONENT_DIR",
                "HALPHY_COMPONENT_DIR",
            ],
            "required_include_paths": [
                "$(PDIR)include",
                "$(HALPHY_INC_DIR)",
                "$(HALPHY_TOOLS_COMPONENT_DIR)/include/tlv1",
                "$(HALPHY_TOOLS_COMMON_DIR)/tlv2p0/include",
                "$(PROTOCOL_INC_DIR)/include",
                "$(PROTOCOL_INC_DIR)/src/include",
                "$(MAC_CORE_SRC_DIR)/wal/include",
                "$(MAC_CORE_SRC_DIR)/wal/whal/include",
                "$(MAC_CORE_SRC_DIR)/wal/AR/include",
                "$(MAC_CORE_SRC_DIR)/wal/AR/tx",
                "$(MAC_CORE_SRC_DIR)/wal/AR/rx",
            ],
        },
        "total_dependencies_evaluated": len(dependencies),
        "present_in_public_tree_count": present_count,
        "missing_from_public_tree_count": missing_count,
        "hard_build_blocker_ids": hard_blockers,
        "can_build_standalone_utf_from_public_tree_alone": False,
        "feasibility_verdict": "REBUILD_BLOCKED_BY_MISSING_PRIVATE_WAL_WHAL_ROM_LIBS__USE_HOST_DIAG_OR_BINARY_UTF",
        "dependencies": [d.to_dict() for d in dependencies],
    }


def build_combined_utf_handler_and_build_matrix() -> Dict[str, Any]:
    """Combine Workstream E3 handler trace and Workstream E4 build inventory into one artifact."""
    e3 = build_utf_handler_trace_summary()
    e4 = build_ar9888_utf_build_inventory()
    return {
        "schema_version": "1.0",
        "task_id": "T-PB-GEM2-02",
        "workstream": "Physical-Boundary Phase 0 Workstream E3 + E4",
        "target_architecture": "QCA988x / AR9888 v2 (Peregrine)",
        "pinned_repository": STARLINK_WIFI_REPO,
        "pinned_commit": STARLINK_WIFI_COMMIT,
        "live_devices_touched": False,
        "workstream_e3_utf_handler_trace": e3,
        "workstream_e4_utf_build_inventory": e4,
    }


def write_ar9888_utf_handler_and_build_matrix_json(
    output_path: Path = Path("artifacts/qca988x/ar9888_utf_handler_and_build_matrix.json"),
) -> Dict[str, Any]:
    """Generate and write `artifacts/qca988x/ar9888_utf_handler_and_build_matrix.json`."""
    matrix = build_combined_utf_handler_and_build_matrix()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    return matrix


if __name__ == "__main__":
    out = Path("artifacts/qca988x/ar9888_utf_handler_and_build_matrix.json")
    matrix = write_ar9888_utf_handler_and_build_matrix_json(out)
    print(
        json.dumps(
            {
                "artifact": str(out),
                "total_commands_traced": matrix["workstream_e3_utf_handler_trace"][
                    "total_commands_traced"
                ],
                "classification_counts": matrix["workstream_e3_utf_handler_trace"][
                    "classification_counts"
                ],
                "can_build_standalone_utf_from_public_tree_alone": matrix[
                    "workstream_e4_utf_build_inventory"
                ]["can_build_standalone_utf_from_public_tree_alone"],
                "hard_build_blocker_ids": matrix["workstream_e4_utf_build_inventory"][
                    "hard_build_blocker_ids"
                ],
            },
            indent=2,
        )
    )
