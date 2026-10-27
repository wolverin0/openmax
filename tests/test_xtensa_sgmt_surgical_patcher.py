"""Unit tests for Stage 17 PB-040 Surgical Xtensa SGMT Re-Packer & Lossless BMI_LZ Codec
(`T-PB-040-XTENSA-SURGICAL-RAM-PATCH-BUILDER`).
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from firmware.xtensa_sgmt_surgical_patcher import (
    DEFAULT_ARTIFACT_OUT,
    SgmtContainer,
    SgmtSurgicalPatcher,
    SurgicalPatchSpec,
    bmi_lz_compress,
    bmi_lz_decompress,
    build_pb040_surgical_patch_report,
    get_pb040_surgical_patch_specs,
    load_ar9888v2_sgmt_containers,
)


def test_bmi_lz_roundtrip_all_12_ar9888v2_segments() -> None:
    containers = load_ar9888v2_sgmt_containers()
    assert set(containers.keys()) == {
        "athwlan_AR9888v2_ptmp_ap_bin",
        "athwlan_AR9888v2_ptmp_sta_bin",
        "athwlan_AR9888v2_ptp_bin",
    }

    seg_count = 0
    for sym_name, container in containers.items():
        assert container.entry_point == 0x00983C00
        assert len(container.segments) == 4
        for seg in container.segments:
            recomp = bmi_lz_compress(seg.decoded_bytes, enable_lz77=True)
            redecomp = bmi_lz_decompress(recomp, seg.decoded_size)
            assert redecomp == seg.decoded_bytes, f"Roundtrip failed on {sym_name} seg {seg.index}"
            seg_count += 1

    assert seg_count == 12


def test_all_4_pb040_surgical_patch_specs_apply_cleanly() -> None:
    containers = load_ar9888v2_sgmt_containers()
    ap_container = containers["athwlan_AR9888v2_ptmp_ap_bin"]
    specs = get_pb040_surgical_patch_specs()
    assert [s.patch_id for s in specs] == [
        "PB040-CANARY-RODATA",
        "PB040-WMI-DISPATCH-0x9064",
        "PB040-CCA-AGC-OVERRIDE",
        "PB040-SUB20MHZ-PLL-DIV",
    ]

    for spec in specs:
        patched, receipt = SgmtSurgicalPatcher.validate_and_apply(ap_container, spec)
        assert receipt["segment_length_preserved"] is True
        assert receipt["bmi_lz_roundtrip_verified"] is True
        assert receipt["entry_point_preserved_hex"] == "0x00983c00"
        assert patched.entry_point == 0x00983C00

        repacked_blob = patched.to_bytes(recompress=False)
        reparsed = SgmtContainer.from_bytes(repacked_blob)
        seg = reparsed.segments[spec.segment_index]
        rel = spec.virtual_address - seg.destination
        assert seg.decoded_bytes[rel : rel + len(spec.patched_bytes)] == spec.patched_bytes


def test_surgical_patcher_fail_closed_guardrails() -> None:
    containers = load_ar9888v2_sgmt_containers()
    ap_container = containers["athwlan_AR9888v2_ptmp_ap_bin"]
    base_spec = get_pb040_surgical_patch_specs()[0]

    # 1. Reject length mismatch (would cause Xtensa l32r literal pool drift)
    bad_len_spec = SurgicalPatchSpec(
        patch_id="BAD-LEN",
        pb_stage="TEST",
        description="Length mismatch test",
        target_symbol=base_spec.target_symbol,
        segment_index=1,
        virtual_address=0x0040B953,
        expected_orig_bytes=b"e",
        patched_bytes=b"EE",
        sibling_addresses={},
        safety_rationale="",
    )
    with pytest.raises(ValueError, match="Length mismatch"):
        SgmtSurgicalPatcher.validate_and_apply(ap_container, bad_len_spec)

    # 2. Reject original byte mismatch
    bad_orig_spec = SurgicalPatchSpec(
        patch_id="BAD-ORIG",
        pb_stage="TEST",
        description="Orig mismatch test",
        target_symbol=base_spec.target_symbol,
        segment_index=1,
        virtual_address=0x0040B953,
        expected_orig_bytes=b"Z",
        patched_bytes=b"E",
        sibling_addresses={},
        safety_rationale="",
    )
    with pytest.raises(ValueError, match="Original byte mismatch"):
        SgmtSurgicalPatcher.validate_and_apply(ap_container, bad_orig_spec)

    # 3. Reject out-of-bounds virtual address
    bad_addr_spec = SurgicalPatchSpec(
        patch_id="BAD-ADDR",
        pb_stage="TEST",
        description="Address out-of-bounds test",
        target_symbol=base_spec.target_symbol,
        segment_index=1,
        virtual_address=0x00983C00,
        expected_orig_bytes=b"e",
        patched_bytes=b"E",
        sibling_addresses={},
        safety_rationale="",
    )
    with pytest.raises(ValueError, match="outside Segment"):
        SgmtSurgicalPatcher.validate_and_apply(ap_container, bad_addr_spec)


def test_pb040_artifact_and_docs_persisted() -> None:
    assert DEFAULT_ARTIFACT_OUT.exists()
    persisted = json.loads(DEFAULT_ARTIFACT_OUT.read_text(encoding="utf-8"))
    report = build_pb040_surgical_patch_report()
    assert (
        persisted["bmi_lz_roundtrip_verification"]["segments_verified"]
        == report["bmi_lz_roundtrip_verification"]["segments_verified"]
        == 12
    )
    assert persisted["bmi_lz_roundtrip_verification"]["all_segments_100pct_byte_identical"] is True
    assert len(persisted["surgical_patch_specifications"]) == 4
    assert Path("docs/STAGE17_PB040_XTENSA_SURGICAL_RAM_PATCH_SPEC.md").exists()
