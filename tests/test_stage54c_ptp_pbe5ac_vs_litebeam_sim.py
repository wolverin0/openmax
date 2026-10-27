"""Unit and integration tests for Stage 54C PowerBeam 5AC Gen2 vs LiteBeam 5AC Gen2 PtP simulation and Observability Hub sync."""

from __future__ import annotations

import json
from pathlib import Path

from simulation.ptmp.stage54c_ptp_pbe5ac_vs_litebeam_openwrt_vs_airos_sim import (
    DEFAULT_OUTPUT_PATH as DEFAULT_OUT_JSON,
    HARDWARE_PROFILES,
    MAC_PROFILES as MAC_MODES,
    PBE_BOOST_RECEIPT_PATH as PBE_OTA_BOOST_JSON,
    load_calibration_baselines,
    run_stage54c_simulation,
)
from tools.generate_command_center_dashboard import generate_dashboard
from tools.generate_observability_hub import DEFAULT_JSON_OUT, generate_observability_hub


def test_pbe5ac_ota_boost_receipt_calibration_exists() -> None:
    assert PBE_OTA_BOOST_JSON.exists(), f"Missing {PBE_OTA_BOOST_JSON}"
    data = json.loads(PBE_OTA_BOOST_JSON.read_text(encoding="utf-8"))
    after = data["ota_rf_observations"]["after_boost"]
    assert -68.5 <= float(after["ap_rx_signal_dbm"]) <= -66.5
    assert int(data["topology"]["ap"]["channel_width_mhz"]) == 20
    assert int(data["topology"]["ap"]["freq_mhz"]) == 5205


def test_stage54c_calibration_inputs_and_profiles() -> None:
    cal = load_calibration_baselines()
    assert cal["pbe5ac_ota_boost"]["mean_rx_signal_dbm"] == -67.5
    v18 = cal["stage52a_champion_v18"]
    assert v18["bql_limit_min"] == 4542
    assert v18["bql_limit_max"] == 42392
    assert v18["bql_hold_time"] == 1000
    assert v18["fq_quantum"] == 4542
    assert v18["dev_weight_tx_bias"] == 2
    assert abs(v18["goodput_gain_pct_vs_v17"] - 7.022) < 0.05
    assert abs(v18["p50_rtt_delta_pct_vs_v17"] - (-28.919)) < 0.05

    assert set(HARDWARE_PROFILES.keys()) == {"PBE-5AC-Gen2", "LBE-5AC-Gen2"}
    assert HARDWARE_PROFILES["PBE-5AC-Gen2"].antenna_gain_dbi == 25.0
    assert HARDWARE_PROFILES["LBE-5AC-Gen2"].antenna_gain_dbi == 23.0
    assert {
        "airMAX_FF_8ms",
        "airMAX_FF_5ms",
        "airMAX_Flexible",
        "OpenWrt_Stage52A_Champion_v18",
    }.issubset(set(MAC_MODES.keys()))


def test_stage54c_simulation_matrix_and_receipt(tmp_path: Path) -> None:
    out_file = tmp_path / "stage54c_test.json"
    receipt = run_stage54c_simulation(output_path=out_file)
    assert out_file.exists()
    assert DEFAULT_OUT_JSON.exists()
    assert receipt["stage"] == "Stage 54C"
    assert receipt["status"] == "COMPLETED"
    hm = receipt["headline_matrix"]
    assert set(hm.keys()) == {"PBE-5AC-Gen2", "LBE-5AC-Gen2"}

    for hw_id in ("PBE-5AC-Gen2", "LBE-5AC-Gen2"):
        modes = hm[hw_id]
        for required_mode in (
            "airMAX_FF_8ms",
            "airMAX_FF_5ms",
            "airMAX_Flexible",
            "OpenWrt_Stage52A_Champion_v18",
        ):
            assert required_mode in modes

        # OpenWrt Stage 52A Champion v18 must achieve highest goodput and lowest p50/p95 RTT
        v18 = modes["OpenWrt_Stage52A_Champion_v18"]
        flex = modes["airMAX_Flexible"]
        ff8 = modes["airMAX_FF_8ms"]
        ff5 = modes["airMAX_FF_5ms"]

        assert v18["aggregate_goodput_mbps"] > flex["aggregate_goodput_mbps"]
        assert v18["aggregate_goodput_mbps"] > ff8["aggregate_goodput_mbps"]
        assert v18["loaded_p50_rtt_ms"] < flex["loaded_p50_rtt_ms"]
        assert v18["loaded_p50_rtt_ms"] < ff5["loaded_p50_rtt_ms"]
        assert v18["loaded_p95_rtt_ms"] < flex["loaded_p95_rtt_ms"]
        assert v18["voip_loss_pct"] == 0.0

        # FF 5ms must have lower p50 RTT than FF 8ms, while FF 8ms has higher goodput than FF 5ms
        assert ff5["loaded_p50_rtt_ms"] < ff8["loaded_p50_rtt_ms"]
        assert ff8["aggregate_goodput_mbps"] > ff5["aggregate_goodput_mbps"]

    # PowerBeam 5AC Gen2 (25 dBi dish, -67.5 dBm) must outperform LiteBeam 5AC Gen2 (23 dBi, -71.5 dBm)
    pbe_v18 = hm["PBE-5AC-Gen2"]["OpenWrt_Stage52A_Champion_v18"]
    lbe_v18 = hm["LBE-5AC-Gen2"]["OpenWrt_Stage52A_Champion_v18"]
    assert pbe_v18["aggregate_goodput_mbps"] > lbe_v18["aggregate_goodput_mbps"]
    assert pbe_v18["loaded_p50_rtt_ms"] < lbe_v18["loaded_p50_rtt_ms"]


def test_observability_hub_and_dashboard_include_stage51a_52a_54c() -> None:
    payload = generate_observability_hub()
    assert DEFAULT_JSON_OUT.exists()
    assert "Stage 52A Champion v18" in payload["active_champion"]
    assert payload["counts"]["ptp_comparison_rows"] == 8
    assert len(payload["ptp_comparison"]) == 8
    assert all(float(row["goodput_mbps"]) > 10.0 for row in payload["ptp_comparison"])

    champ_versions = [c["version"] for c in payload["promoted_champions"]]
    assert any("Champion v17" in v for v in champ_versions)
    assert any("Champion v18" in v for v in champ_versions)

    rejected_stages = [r["stage_round"] for r in payload["rejected_experiments"]]
    assert any("Stage 51A" in s for s in rejected_stages)
    assert any("Stage 52A" in s for s in rejected_stages)

    html_path = generate_dashboard()
    html_text = html_path.read_text(encoding="utf-8")
    assert "Stage 51A" in html_text
    assert "Stage 52A" in html_text
    assert "Stage 54C" in html_text
    assert "PowerBeam 5AC Gen2" in html_text
    assert "LiteBeam 5AC Gen2" in html_text
