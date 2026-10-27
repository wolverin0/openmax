#!/usr/bin/env python3
"""Unit tests for Stage 15 Git Push Readiness (<50 MB Gate) & 11-Unit Hardware Master Atlas."""

from __future__ import annotations

import json

from analysis.git_push_readiness_and_master_atlas import (
    DEFAULT_MASTER_ATLAS_PATH,
    MAX_UNIGNORED_SIZE_MB,
    REQUIRED_GITIGNORE_PATTERNS,
    audit_git_push_readiness,
    build_11unit_bench_hardware_atlas,
    build_master_11unit_atlas_report,
)


def test_gitignore_patterns_and_under_50mb_push_readiness() -> None:
    audit = audit_git_push_readiness(max_budget_mb=MAX_UNIGNORED_SIZE_MB)

    assert audit["required_gitignore_patterns_present"] is True
    assert audit["missing_gitignore_patterns"] == []
    assert audit["leaked_binary_dumps"] == []
    assert audit["total_unignored_size_mb"] < 50.0
    assert audit["headroom_under_budget_mb"] > 0.0
    assert audit["git_push_ready"] is True

    cats = audit["tracked_categories_count"]
    assert cats["docs_md"] > 0
    assert cats["python_modules"] > 0
    assert cats["dashboard_files"] > 0
    assert cats["hardware_benchmark_receipts"] > 0


def test_11unit_bench_hardware_atlas_consolidates_all_units() -> None:
    units = build_11unit_bench_hardware_atlas()
    assert len(units) == 11

    unit_ids = [u.unit_id for u in units]
    assert unit_ids == [
        "UNIT_01_LAP120_AP",
        "UNIT_02_LOCO5AC_195",
        "UNIT_03_MIKROTIK_SXT_LITE5",
        "UNIT_04_LITEBEAM_M5",
        "UNIT_05_ROCKET_PRISM_5AC_GEN2",
        "UNIT_06_POWERBEAM_M5_300_PAIR",
        "UNIT_07_ROCKET_2AC_PRISM",
        "UNIT_08_AIRFIBER_4X",
        "UNIT_09_LTU_ROCKET",
        "UNIT_10_LTU_LITE_PRIMARY_BOCA5",
        "UNIT_11_LTU_LITE_SECONDARY_UNIT2",
    ]

    # 2x PowerBeam M5 300 in UNIT_06 + 10 single entries (including 2x LTU-Lite across UNIT_10 & UNIT_11) = 12 physical radios
    assert sum(u.physical_quantity for u in units) == 12


def test_master_11unit_atlas_artifact_persisted_on_disk() -> None:
    report = build_master_11unit_atlas_report()
    assert report["automatic_execution_allowed"] is False
    assert report["atlas_summary"]["bench_unit_entries_count"] == 11
    assert report["atlas_summary"]["total_unique_live_autoresearch_rounds"] == 313

    assert DEFAULT_MASTER_ATLAS_PATH.is_file()
    disk_payload = json.loads(DEFAULT_MASTER_ATLAS_PATH.read_text(encoding="utf-8"))
    assert disk_payload["stage_id"] == "STAGE15-GIT-PUSH-READINESS-AND-11UNIT-MASTER-ATLAS-20261025"
    assert len(disk_payload["bench_units"]) == 11
    assert len(REQUIRED_GITIGNORE_PATTERNS) == 9
