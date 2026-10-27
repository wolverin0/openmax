from __future__ import annotations

from pathlib import Path

from tools.telemetry.run_stage77a_aeon_rf_timeseries_regime_classifier import (
    DEFAULT_OUTPUT_JSON,
    generate_calibrated_rf_timeseries_dataset,
    run_stage77a_aeon_rf_timeseries_classifier,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE77A_DOC = REPO_ROOT / "docs" / "STAGE77A_AEON_MULTIVARIATE_RF_TIMESERIES_REGIME_CLASSIFIER.md"


def test_stage77a_aeon_3d_dataset_shape_and_regimes() -> None:
    X, y = generate_calibrated_rf_timeseries_dataset(n_per_class=20, n_timepoints=60)
    assert X.shape == (100, 6, 60)
    assert set(y.tolist()) == {0, 1, 2, 3, 4}


def test_stage77a_classifier_accuracy_zero_fp_and_5pillar_gate() -> None:
    payload = run_stage77a_aeon_rf_timeseries_classifier()
    assert DEFAULT_OUTPUT_JSON.exists()

    gate = audit_stage_receipt_5pillars(payload)
    assert gate["compliant"] is True, f"Missing pillars: {gate['missing_pillars']}"

    ev = payload["evaluation_metrics"]
    assert ev["heldout_accuracy"] >= 0.98
    assert ev["heldout_macro_f1"] >= 0.98
    assert ev["cv_5fold_mean_accuracy"] >= 0.98
    assert ev["frozen_collector_false_positive_rate"] == 0.0


def test_stage77a_doc_budget_and_header() -> None:
    assert STAGE77A_DOC.exists()
    lines = STAGE77A_DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220, f"Expected < 220 lines, got {len(lines)}"
    assert lines[0].startswith("<!-- doc-head:")
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
