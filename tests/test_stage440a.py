#!/usr/bin/env python3
"""Pytest suite for Stage 440A — LTU Short-Queue Micro-AP & AD9361 Split-Frequency Kit."""

from __future__ import annotations

import json

from tools.firmware.build_stage440a_ltu_sq_micro_ap_and_split_freq_kit import (
    ARTIFACT_OUT,
    DOC_OUT,
    HELPER_SH_OUT,
    build_stage440a,
)


def test_stage440a_ltu_sq_and_split_freq_kit() -> None:
    report = build_stage440a()
    assert HELPER_SH_OUT.exists()
    assert ARTIFACT_OUT.exists()
    assert DOC_OUT.exists()
    loaded = json.loads(ARTIFACT_OUT.read_text(encoding="utf-8"))
    assert loaded["stage"] == "440A"
    assert loaded["memory_master_claim_id"] == "mm-fef1"
    assert loaded["helper_script"]["default_mode"] == "--inspect-only"
    assert loaded["helper_script"]["lf_only"] is True
    assert loaded["helper_script"]["zero_dev_ame_touches"] is True
    assert loaded["validated_offsets_and_symbols"]["stage424a_ame_core_eab_token_hits"] == 359
    assert loaded["validated_offsets_and_symbols"]["stage438a_sq_nq_scheduler_hits"]["SQ_hits"] == 6
    assert report["safety_audit"]["touched_dev_ame_nodes"] is False
