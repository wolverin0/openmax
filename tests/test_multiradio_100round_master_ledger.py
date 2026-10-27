import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_multiradio_100round_master_ledger_completeness():
    ledger_path = REPO_ROOT / "artifacts" / "autoresearch" / "multiradio_100round_master_ledger_20261024.json"
    assert ledger_path.exists(), f"Missing {ledger_path}"
    data = json.loads(ledger_path.read_text(encoding="utf-8"))

    assert data["experiment_id"] == "FMX-STAGE12-MULTIRADIO-100ROUND-MASTER-LEDGER"
    assert data["total_paired_rounds"] == 100
    assert data["total_sub_phases_ab_ab"] == 400
    assert data["total_kept"] == 45
    assert data["total_rejected"] == 55
    assert data["total_kept"] + data["total_rejected"] == 100
    assert len(data["all_100_rounds_index"]) == 100

    safety = data["safety_attestation"]
    assert safety["ram_only"] is True
    assert safety["cfgmtd_flash_writes"] == 0
    assert safety["production_guarida_10_10_100_84_touched"] is False
    assert safety["bench_runner_192_168_200_x_touched"] is False

    by_dev = data["by_device_summary"]
    assert by_dev["af4x_invictus"]["total_rounds"] == 20
    assert by_dev["ltu_lite_amesoc"]["total_rounds"] == 20
    assert by_dev["r2ac_prism_ap"]["total_rounds"] == 21
    assert by_dev["r5ac_prism_sta"]["total_rounds"] == 16
    assert by_dev["pbm5_xw_weak_ota"]["total_rounds"] == 23
    assert sum(v["total_rounds"] for v in by_dev.values()) == 100

    for rid in ("PBM5-R23", "PBM5-R25", "R5AC-R19", "R2AC-R19", "R2AC-R21", "AF4X-R19", "LTU-R19"):
        assert rid in data["kept_round_ids"], f"Expected {rid} in kept_round_ids"

    doc_path = REPO_ROOT / "docs" / "STAGE12_MULTIRADIO_100ROUND_MASTER_BENCHMARK.md"
    assert doc_path.exists(), f"Missing {doc_path}"
    assert "FMX-STAGE12-MULTIRADIO-100ROUND-MASTER-LEDGER" in doc_path.read_text(encoding="utf-8")
