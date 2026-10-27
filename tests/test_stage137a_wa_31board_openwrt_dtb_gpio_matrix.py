import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPO_ROOT
    / "artifacts"
    / "autoresearch"
    / "stage137a_wa_31board_openwrt_dtb_gpio_matrix.json"
)

EXPECTED_17_WA_SYSIDS = {
    "0xe3d6",
    "0xe7f9",
    "0xe8e5",
    "0xe7fd",
    "0xe7fa",
    "0xe7fb",
    "0xe7fc",
    "0xe7f7",
    "0xe7fe",
    "0xe7ff",
    "0xe8f5",
    "0xe9f5",
    "0xe6f5",
    "0xe7f5",
    "0xe3d9",
    "0xe2c5",
    "0xe2c7",
}


def test_stage137a_wa_31_board_records_and_17_sysids():
    assert ARTIFACT_PATH.exists(), f"Missing {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "137A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_verification"]["pbe5ac_241_242_touched"] is False
    assert data["safety_verification"]["guarida_poe_switches_200_201_touched"] is False

    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"

    records = data["wa_31_board_records"]
    assert len(records) == 31
    assert [r["record_index"] for r in records] == list(range(31))

    sysid_matrix = data["unique_sysid_matrix"]
    assert set(sysid_matrix.keys()) == EXPECTED_17_WA_SYSIDS


def test_stage137a_single_vs_dual_phy_and_poe_passthrough_classification():
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    records = data["wa_31_board_records"]
    sysids = data["unique_sysid_matrix"]
    summary = data["compatibility_summary"]

    assert summary["total_wa_board_records"] == 31
    assert summary["unique_wa_sysids"] == 17
    assert summary["single_phy_direct_drop_in_records_count"] == 28
    assert summary["dual_phy_dedicated_dtb_records_count"] == 3
    assert set(summary["dual_phy_dedicated_dtb_sysids"]) == {"0xe7fb", "0xe7fc"}

    for r in records:
        if r["sysid"] in {"0xe7fb", "0xe7fc"}:
            assert r["board_phycount"] == 2
            assert r["dtb_compatibility_class"] == "REQUIRES_DEDICATED_DUAL_ETH_POE_DTB"
            assert r["can_run_pbe5ac_gen2_kernel_dtb_directly"] is False
            assert r["can_run_lbe5ac_gen2_kernel_dtb_directly"] is False
            assert "ar9342_ubnt_wa_2ports.dtsi" in r["openwrt_dtsi_chain"]
        else:
            assert r["board_phycount"] == 1
            assert r["can_run_pbe5ac_gen2_kernel_dtb_directly"] is True
            assert r["can_run_lbe5ac_gen2_kernel_dtb_directly"] is True
            assert "ar9342_ubnt_wa_1port.dtsi" in r["openwrt_dtsi_chain"]

    # Verify NS-5AC (0xe7fb) and NBE-5AC-Gen2 (0xe7fc) dual-PHY details
    assert sysids["0xe7fb"]["models"] == ["NS-5AC"]
    assert sysids["0xe7fb"]["board_phycount"] == 2
    assert sysids["0xe7fb"]["feature_poe_passthrough"] is True
    assert sysids["0xe7fb"]["openwrt_dts_file"].endswith("ar9342_ubnt_nanostation-ac.dts")

    assert sysids["0xe7fc"]["models"] == ["NBE-5AC-Gen2"]
    assert sysids["0xe7fc"]["board_phycount"] == 2
    assert sysids["0xe7fc"]["openwrt_dts_file"].endswith("ar9342_ubnt_nanobeam-ac-gen2.dts")

    # Verify LAP-GPS (0xe7fd) GPS feature flag + single Ethernet PHY
    assert sysids["0xe7fd"]["models"] == ["LAP-GPS"]
    assert sysids["0xe7fd"]["board_phycount"] == 1
    assert sysids["0xe7fd"]["feature_gps"] is True
    assert sysids["0xe7fd"]["can_run_lbe5ac_gen2_kernel_dtb_directly"] is True

    # Verify PBE-5AC-Gen2 / ISO (0xe3d6) and LBE-5AC-Gen2 (0xe7f9) LED topologies
    assert sysids["0xe3d6"]["feature_rssi_leds"] == 4
    assert sysids["0xe7f9"]["feature_rssi_leds"] == 0
    assert sysids["0xe8e5"]["feature_rssi_leds"] == 1
