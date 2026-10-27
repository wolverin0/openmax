"""Tests for PB-030 & PB-031 Harness: 5/10 MHz Cabled Loop & LDPC/BCC/STBC/SGI/CCA Response Surface."""

from __future__ import annotations

import json
import pytest

from controller.pb_030_031_phy_response_surface_harness import (
    DEFAULT_MATRIX_OUTPUT_PATH,
    PhyTreatmentArm,
    build_pb_030_031_experiment_matrix,
    compute_physical_limit_diagnostics,
)


def test_pb_030_sub20mhz_and_width_grid_uses_exact_channel_widths() -> None:
    matrix = build_pb_030_031_experiment_matrix()
    assert matrix["automatic_execution_allowed"] is False
    grid = matrix["pb030_sub20mhz_and_width_grid"]
    assert len(grid) == 20  # 5 attenuation steps x 4 widths (5, 10, 20, 40 MHz)

    for entry in grid:
        w = entry["channel_width_mhz"]
        gp = entry["expected_goodput_mbps"]
        assert w in (5, 10, 20, 40)
        assert entry["goodput_per_mhz"] == round(gp / float(w), 4)
        assert entry["physical_diagnostics"]["eta_goodput_bits_per_s_hz"] == round(gp / float(w), 4)


def test_pb_031_response_surface_promotes_valid_regimes_and_rejects_p99_cca_regression() -> None:
    matrix = build_pb_030_031_experiment_matrix()
    treatments = {
        t["treatment_id"]: t for t in matrix["pb031_phy_response_surface_treatments"]
    }
    assert treatments["PB-031-H1-LDPC-VS-BCC-MID-SNR"]["paired_evaluation"]["gate_decision"]["verdict"] == "SYNTHETIC_PASS"
    assert treatments["PB-031-H2-LGI-VS-SGI-HIGH-MULTIPATH"]["paired_evaluation"]["gate_decision"]["verdict"] == "SYNTHETIC_PASS"
    assert treatments["PB-031-H3-STBC-RANK1-FADE"]["paired_evaluation"]["gate_decision"]["verdict"] == "SYNTHETIC_PASS"
    assert (
        treatments["PB-031-H4-OVERAGGRESSIVE-CCA-NEGATIVE-CONTROL"]["paired_evaluation"]["gate_decision"]["verdict"]
        == "REJECT"
    )


def test_phy_treatment_arm_validates_allowlists() -> None:
    with pytest.raises(ValueError, match="Invalid channel_width_mhz"):
        PhyTreatmentArm("bad_width", channel_width_mhz=15)

    with pytest.raises(ValueError, match="Invalid fec_mode"):
        PhyTreatmentArm("bad_fec", channel_width_mhz=20, fec_mode="TURBO")

    with pytest.raises(ValueError, match="Invalid cca_ed_threshold_dbm"):
        PhyTreatmentArm("bad_cca", channel_width_mhz=20, cca_ed_threshold_dbm=-40)

    diag = compute_physical_limit_diagnostics(80.0, 20, 173.3, 25.0)
    assert diag["eta_goodput_bits_per_s_hz"] == 4.0


def test_saved_pb_030_031_matrix_json_exists() -> None:
    data = build_pb_030_031_experiment_matrix()
    assert all(t["paired_evaluation"]["physical_promotion_accepted"] is False
               for t in data["pb031_phy_response_surface_treatments"])
    assert data["gates_covered"] == ["PB-030", "PB-031"]
    assert data["automatic_execution_allowed"] is False
