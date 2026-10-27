#!/usr/bin/env python3
"""Tests for Stage 75A umac.ko and ath_dev.ko /fullrea binary dissection."""

from __future__ import annotations

import json
from pathlib import Path

from tools.re.dissect_stage75a_umac_and_ath_dev_ko import (
    DEFAULT_OUT_JSON,
    REPO_ROOT,
    build_stage75a_dissection,
)

DOC_PATH = REPO_ROOT / "docs" / "STAGE75A_UMAC_AND_ATH_DEV_FULLREA_BINARY_DISSECTION.md"


def test_stage75a_artifact_and_binary_identity() -> None:
    assert DEFAULT_OUT_JSON.exists(), "Stage 75A artifact JSON must exist"
    data = json.loads(DEFAULT_OUT_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "75A"
    assert data["claim_status"] == "CONFIRMED"

    bins = data["binaries"]
    assert bins["wa_umac_ko"]["size_bytes"] == 2356432
    assert bins["xc_umac_ko"]["size_bytes"] == 2358768
    assert bins["wa_ath_dev_ko"]["size_bytes"] == 287216
    assert bins["xc_ath_dev_ko"]["size_bytes"] == 287216

    diffs = data["wa_vs_xc_text_diff"]
    assert diffs["umac_ko"]["total_word_diffs"] == 2545
    assert diffs["ath_dev_ko"]["total_word_diffs"] == 162
    assert diffs["ath_dev_ko"]["imm16_shift_histogram"]["0x00c4->0x00c8"] == 73
    assert diffs["ath_dev_ko"]["imm16_shift_histogram"]["0x00bc->0x00c0"] == 23
    assert diffs["ath_dev_ko"]["imm16_shift_histogram"]["0x0072->0x0076"] == 19
    assert diffs["ath_dev_ko"]["imm16_shift_histogram"]["0x0001->0x0015"] == 5
    assert diffs["ath_dev_ko"]["imm16_shift_histogram"]["0x0021->0x0040"] == 2


def test_stage75a_multiq_and_cksum_and_minfree_dissections() -> None:
    report = build_stage75a_dissection()
    knobs = report["knob_dissections"]

    multiq = knobs["set_multiq"]
    assert multiq["wext_priv_entry"]["cmd_hex"] == "0x019e"
    assert multiq["wext_priv_entry"]["rodata_offset"] == "0x00b85c"
    assert multiq["vap_alloc_queues"] == 5
    assert multiq["optimal_value"] == 3
    assert multiq["subqueue_mapping_by_tid"] == {
        "tid_1_2_AC_BK": 0,
        "tid_0_3_AC_BE": 1,
        "tid_4_5_AC_VI": 2,
        "tid_6_7_AC_VO": 3,
        "high_prio_flag": 4,
    }

    cksum = knobs["enable_tx_tcp_cksum"]
    assert cksum["section"] == ".bss"
    assert cksum["offset"] == "0x01bca0"
    assert cksum["default_value"] == 0

    minfree = knobs["wmm_minfree_and_swretry"]["ath_dev_data_defaults"]
    assert minfree == {
        "CABMinfree_data_0x03c8": 48,
        "ACVIMinfree_data_0x03cc": 16,
        "ACBEMinfree_data_0x03d0": 32,
        "ACBKMinfree_data_0x03d4": 48,
        "UAPSDMinfree_bss_0x00c8": 0,
        "ACVOMinfree_bss_0x00cc": 0,
    }


def test_stage75a_verified_instructions_and_bugs() -> None:
    data = json.loads(DEFAULT_OUT_JSON.read_text(encoding="utf-8"))
    umac_insns = data["verified_instruction_words"]["umac_ko"]
    ath_insns = data["verified_instruction_words"]["ath_dev_ko"]

    # alloc_netdev_mq 5 queues (addiu $a3, $zero, 5)
    assert umac_insns["osif_vap_init_alloc_netdev_mq_5queues_0x0a283c"] == "0x24070005"
    # lw $v0, 0x44($s0) (dev->features load at 0x0bc1f4 in XC / 0x0bc1f0 in WA)
    assert umac_insns["ol_ath_attach_ori_netif_f_csum_0x12_0x0bc1f4"] == "0x8e020044"
    # sll $s6, $s6, 0x1d (HTT TX desc bit 29 cksum offload)
    assert umac_insns["ol_tx_desc_ll_shift_cksum_bit29_0x0d18bc"] == "0x0016b740"
    # sltiu $v0, $v0, 0x30 (hardcoded 48 ath_buf A-MPDU cliff in ath_tx_start_dma)
    assert ath_insns["ath_tx_start_dma_hardcoded_48_cliff_0x01ba00"] == "0x2c420030"

    bug_ids = [b["bug_id"] for b in data["bugs"]]
    assert bug_ids == [
        "UMAC-BUG-01",
        "UMAC-BUG-02",
        "UMAC-BUG-03",
        "UMAC-BUG-04",
        "UMAC-BUG-05",
        "ATHDEV-BUG-01",
        "ATHDEV-BUG-02",
        "ATHDEV-BUG-03",
        "ATHDEV-BUG-04",
    ]


def test_stage75a_doc_constraints() -> None:
    assert DOC_PATH.exists(), "Stage 75A markdown documentation must exist"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Expected < 220 lines, got {len(lines)}"
    assert text.count("<!-- doc-head:") == 1
    for bug_id in ("UMAC-BUG-01", "UMAC-BUG-05", "ATHDEV-BUG-01", "ATHDEV-BUG-03"):
        assert bug_id in text
