"""Verification tests for Stage 99C Rocket 2AC Prism (2XC.v8.7.11) ELF module audit and deep fast-path benchmark."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "artifacts" / "autoresearch" / "stage99c_r2ac_prism_2xc_deep_bench.json"
DOC_PATH = ROOT / "docs" / "STAGE99C_R2AC_PRISM_2XC_DEEP_BENCH.md"
SCRIPT_PATH = ROOT / "tools" / "bench" / "run_stage99c_r2ac_prism_2xc_deep_bench.py"


def test_stage99c_files_exist_and_doc_budget() -> None:
    assert SCRIPT_PATH.exists(), f"Missing script {SCRIPT_PATH}"
    assert ARTIFACT_PATH.exists(), f"Missing artifact {ARTIFACT_PATH}"
    assert DOC_PATH.exists(), f"Missing doc {DOC_PATH}"

    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 160, f"Doc exceeds 160 lines ({len(lines)})"
    assert lines[0].startswith("<!-- doc-head:"), "Doc must start with <!-- doc-head: -->"


def test_stage99c_2xc_vs_5xc_binary_invariance_and_pktlog_audit() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "99C"
    assert data["status"] == "CONFIRMED"
    assert str(data.get("pillar_e_memory_master_claim_id", "")).startswith("mm-")

    mod = data["module_and_knob_audit"]
    assert mod["ubnt_poll_host_rodata_identical_to_5xc_874cs"] is True
    assert mod["ubnt_poll_host_data_identical_to_5xc_874cs"] is True
    assert mod["ubnt_poll_host_text_differing_bytes_vs_5xc_874cs"] == 130

    extracted = mod["extracted_2xc_modules"]
    assert extracted["ubnt_poll_host.ko"]["size_bytes"] == 186560
    assert extracted["ubnt_poll_host.ko"]["md5"] == "ba1c6b4fa2c1a0ac6704fbd9361b9f4c"
    assert extracted["ath_pktlog.ko"]["size_bytes"] == 20740
    assert extracted["ath_pktlog.ko"]["md5"] == "a0401962294531f82851b1d9911ae8fd"
    assert extracted["ath_spectral.ko"]["size_bytes"] == 38284
    assert extracted["ath_spectral.ko"]["md5"] == "a0b0e6109e52181da388fd4fb4e84873"
    assert "ath_pktlog" not in mod["etc_modules_d_50_ath_11c_2ac"]


def test_stage99c_counterbalanced_triple_play_trials() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    trials = data["counterbalanced_2xc_deep_trials"]
    assert len(trials) == 4
    expected = [
        "S99C-ARM-A-STAGE98D-BASELINE",
        "S99C-ARM-B-2XC-DEEP-FASTPATH-CHAMPION",
        "S99C-ARM-A-STAGE98D-BASELINE",
        "S99C-ARM-B-2XC-DEEP-FASTPATH-CHAMPION",
    ]
    assert [t["arm_id"] for t in trials] == expected

    arm_a = data["arm_summaries"]["S99C-ARM-A-STAGE98D-BASELINE"]
    arm_b = data["arm_summaries"]["S99C-ARM-B-2XC-DEEP-FASTPATH-CHAMPION"]
    assert arm_b["iptv_udp_median_mbps"] > 5.0
    assert arm_b["voip_udp_median_mbps"] > 0.05
    assert arm_b["irq2_wifi1_total_delta"] < arm_a["irq2_wifi1_total_delta"]
