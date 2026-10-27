"""Tests for PB-040 Offline Preparation: Reversible Inert Target-Firmware SGMT Mutation Builder."""

from __future__ import annotations

import json
import pytest

from tools.qca988x.inert_target_mutation_builder import (
    DEFAULT_OUTPUT_PATH,
    build_pb_040_dryrun_receipt,
    validate_inert_string_mutation,
)


def test_pb_040_inert_mutation_modifies_only_4_dram_bytes_and_preserves_iram() -> None:
    receipt = build_pb_040_dryrun_receipt()
    assert receipt["gate_id"] == "PB-040"
    assert receipt["automatic_execution_allowed"] is False
    assert receipt["ram_only_target_load_required"] is True
    assert receipt["spi_flash_write_allowed"] is False

    for role in (
        "athwlan_AR9888v2_ptmp_ap_bin",
        "athwlan_AR9888v2_ptmp_sta_bin",
        "athwlan_AR9888v2_ptp_bin",
    ):
        res = receipt["roles_verified"][role]
        assert res["expected_diff_bytes"] == 4
        assert res["observed_total_diff_bytes"] == 4
        assert res["iram_code_segments_untouched"] is True
        assert res["repacked_container_valid_sgmt"] is True
        assert res["entry_point_preserved"] is True
        assert res["reversible_restoration_bit_exact"] is True


def test_pb_040_rejects_unsafe_or_length_changing_mutations() -> None:
    with pytest.raises(ValueError, match="preserve exact byte length"):
        validate_inert_string_mutation(b"UBNT_POLL", b"UBNT_POLL_LONG")

    with pytest.raises(ValueError, match="must not contain null terminators"):
        validate_inert_string_mutation(b"UBNT\x00POLL", b"OMAX\x00POLL")

    with pytest.raises(ValueError, match="must not alter printf"):
        validate_inert_string_mutation(b"CYCLES: %d", b"CYCLES: %s")


def test_pb_040_saved_receipt_exists_and_matches() -> None:
    assert DEFAULT_OUTPUT_PATH.exists()
    data = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    assert data["gate_id"] == "PB-040"
    assert data["automatic_execution_allowed"] is False
    assert data["roles_verified"]["athwlan_AR9888v2_ptmp_ap_bin"]["mutation_virtual_address"] == "0x0040c39c"
