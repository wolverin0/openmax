#!/usr/bin/env python3
"""Unit tests for controller/rocket_prism_multivendor_ap_controller.py (T-PB-GEM1-16)."""

from __future__ import annotations

import json

import pytest

from controller.rocket_prism_multivendor_ap_controller import (
    DEFAULT_PLAN_OUTPUT_PATH,
    build_rocket_prism_multivendor_plan_report,
    build_rocket_prism_multivendor_profile,
)


def test_rocket_prism_multivendor_profile_enforces_ram_only_and_lap120_guard_band() -> None:
    prof = build_rocket_prism_multivendor_profile(center_freq_mhz=5765, channel_width_mhz=20)
    assert prof.ram_only_no_flash_commit is True
    assert prof.ubnt_poll_allow_80211 == 1
    assert prof.ubnt_poll_op_mode == 0
    assert prof.iwpriv_addmtikie == 1
    assert prof.lap120_freq_separation_mhz == 585

    # Verify zero flash writes in apply/rollback commands
    for cmd in prof.ram_only_apply_commands + prof.instant_rollback_commands:
        assert "cfgmtd" not in cmd
        assert "mtd " not in cmd

    # Reject any frequency within 300 MHz of LAP-120 (5180 MHz)
    with pytest.raises(ValueError, match="within 300 MHz"):
        build_rocket_prism_multivendor_profile(center_freq_mhz=5240, channel_width_mhz=20)


def test_rocket_prism_sxt_and_lbm5_plan_artifact_promotes() -> None:
    assert DEFAULT_PLAN_OUTPUT_PATH.exists()
    saved = json.loads(DEFAULT_PLAN_OUTPUT_PATH.read_text(encoding="utf-8"))
    assert saved["automatic_execution_allowed"] is False

    cpes = {c["mgmt_ip"]: c for c in saved["cpe_profiles"]}
    assert "10.99.0.3" in cpes
    assert "10.99.0.4" in cpes
    assert cpes["10.99.0.3"]["vendor"] == "MikroTik"
    assert cpes["10.99.0.4"]["spatial_streams"] == 1
    assert saved["paired_ab_evaluation"]["verdict"] == "PROMOTE"
