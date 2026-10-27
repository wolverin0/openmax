#!/usr/bin/env python3
"""Unit & Binary Verification Suite for Stage 119A:
WA Family Universal Compatibility (PBE-5AC-Gen2 / LBE-5AC-Gen2 / LAP-120 / NS-5AC-Loco)
and Exhaustive airOS 8 rc.poststart <-> OpenWrt 24.10.4 Autoresearch Bridge.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parent.parent
RECEIPT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage119a_wa_family_pbe_lbe_compatibility_and_rc_poststart_map.json"
)


def test_stage119a_receipt_passes_5pillar_gate_and_safety():
    assert RECEIPT_PATH.exists(), f"Missing {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"
    assert data["stage"] == "119A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_verification"]["pbe5ac_241_242_touched"] is False
    assert data["safety_verification"]["guarida_poe_switches_200_201_touched"] is False
    assert data["safety_verification"]["flash_writes_performed"] == 0


def test_wa_family_universal_hardware_and_binary_compatibility():
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    compat = data["wa_family_universal_compatibility"]

    assert compat["shared_platform_dtsi"] == "target/linux/ath79/dts/ar9342_ubnt_wa.dtsi"
    assert compat["shared_caldata_offsets"]["mtd5_2g4_ar9342_wmac_offset_hex"] == "0x1000"
    assert compat["shared_caldata_offsets"]["mtd5_2g4_length_bytes"] == 1088
    assert compat["shared_caldata_offsets"]["mtd5_5g_qca9882_pcie_offset_hex"] == "0x5000"
    assert compat["shared_caldata_offsets"]["mtd5_5g_length_bytes"] == 2116

    models = {m["model_code"]: m for m in compat["models"]}
    assert set(models.keys()) == {"PBE-5AC-Gen2", "LBE-5AC-Gen2", "LAP-120", "NS-5AC-Loco"}
    for code, m in models.items():
        assert m["openmax_stack_100pct_compatible"] is True, f"{code} not marked compatible"
        assert m["shared_platform_dtsi"] == "ar9342_ubnt_wa.dtsi"
        assert m["ram_mib"] == 64
        assert m["flash_mib"] == 16
        assert "168c:003c" in m["main_5g_pcie_radio"]
        assert "AR8035" in m["eth0_phy"]

    # Verify all referenced stack artifacts exist on disk and match SHA-256
    for key, art in compat["identical_stack_artifacts"].items():
        p = REPO_ROOT / art["path"]
        assert p.exists(), f"Missing artifact for {key}: {p}"
        b = p.read_bytes()
        assert len(b) == art["size_bytes"]
        assert hashlib.sha256(b).hexdigest() == art["sha256"]

    # Verify binary ABI split between OpenWrt 24.10.4 release (815,640 B, 352B, 0xa8) and Panel1 snapshot (829,464 B, 384B, 0xa4)
    abi = data["pillar_a_ground_up_re_and_knob_catalog"]["binary_abi_matrix"]
    owrt_teb_path = REPO_ROOT / abi["openwrt_24_10_4_official_release_6_6_110"]["teb_ko"]["path"]
    p1_teb_path = REPO_ROOT / abi["panel1_guarida_snapshot_6_6_110"]["teb_ko"]["path"]

    b_owrt = owrt_teb_path.read_bytes()
    b_p1 = p1_teb_path.read_bytes()
    assert len(b_owrt) == 815640
    assert len(b_p1) == 829464

    with owrt_teb_path.open("rb") as f:
        elf_owrt = ELFFile(f)
        assert int(elf_owrt.get_section_by_name(".gnu.linkonce.this_module")["sh_size"]) == 352
    with p1_teb_path.open("rb") as f:
        elf_p1 = ELFFile(f)
        assert int(elf_p1.get_section_by_name(".gnu.linkonce.this_module")["sh_size"]) == 384

    assert struct.unpack_from(">I", b_owrt, 0x033CA4)[0] == 0x8CC900A8
    assert struct.unpack_from(">I", b_p1, 0x033CA4)[0] == 0x8CC900A4


def test_rc_poststart_to_openwrt_autoresearch_bridge_completeness():
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    bridge = data["rc_poststart_to_openwrt_autoresearch_bridge"]
    assert len(bridge) == 13

    by_id = {g["knob_group_id"]: g for g in bridge}
    expected_groups = {
        "BRIDGE-01-TDMA-VS-80211-WDS-ADMISSION",
        "BRIDGE-02-AMPDU-SWRETRY-TO-AQL",
        "BRIDGE-03-UPH-TIMING-BURST-TO-FQ-QUANTUM",
        "BRIDGE-04-AC-MINFREE-TO-FQ-MEMORY-LIMIT-AND-OOM-GUARD",
        "BRIDGE-05-MULTIQ3-HOST80211-TO-NATIVE-WMM-FQ-TIN",
        "BRIDGE-06-PKTLOG-VOW-TO-CLEAN-ATH10K-FASTPATH",
        "BRIDGE-07-TXQUEUELEN-192-TO-ETH0-BQL-AND-256",
        "BRIDGE-08-NAPI-BUDGET-AND-TX-COMPLETION-BIAS",
        "BRIDGE-09-TCP-TSQ-PACING-AND-CHECKSUM-OFFLOAD",
        "BRIDGE-10-CABQ-MCAST-AND-BEACON-TIMING",
        "BRIDGE-11-CWMIN-CWMAX-ACKTIMEOUT-TO-COVERAGE-CLASS",
        "BRIDGE-12-SYNCHRONOUS-3INT-CSA-TO-HOSTAPD-SWITCH-CHAN",
        "BRIDGE-13-PERSISTENCE-AND-OTA-ROLLBACK-WATCHDOG",
    }
    assert set(by_id.keys()) == expected_groups

    for gid, g in by_id.items():
        assert g["status"] == "CONFIRMED", f"{gid} not CONFIRMED"
        assert len(g["airos8_rc_poststart_knobs"]) >= 1
        assert len(g["openwrt_24_10_4_equivalent_knobs"]) >= 1
        assert g["live_241_242_autoresearch_role"]
