#!/usr/bin/env python3
"""Pytest suite for Stage 351A — Universal WA v8 SquashFS Bake."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.firmware.build_stage351a_wa_squashfs_v8_bake import (
    ARTIFACT_OUT,
    WA_V8_KIT_DIR,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage351a_wa_v8_images_and_receipt() -> None:
    assert ARTIFACT_OUT.exists()
    loaded = json.loads(ARTIFACT_OUT.read_text(encoding="utf-8"))
    assert loaded["stage"] == "351A"
    assert loaded["memory_master_claim_id"] == "mm-91f1"
    assert loaded["live_radios_241_242_20_250_touched"] is False
    assert loaded["boards_baked_count"] == 4
    assert loaded["total_images_baked"] == 16
    assert loaded["integrated_components"]["gro_normal_batch"] == 16
    assert loaded["integrated_components"]["r25_r30_bench_champion_goodput_mbps"] == 70.15

    # Verify all 9 embedded files in both AP and STA SquashFS round-trip digests
    for key in ("squashfs_ap_v8_verification", "squashfs_sta_v8_verification"):
        embedded = loaded[key]["verified_embedded_sha256"]
        assert "99-fmx-wa-universal-champion" in embedded
        assert "99-fmx-wmm-dscp-qos" in embedded
        assert "fmx_chain_imbalance_rescue_daemon.sh" in embedded
        assert "fmx_xtensa_ram_patch_loader.sh" in embedded
        assert "mac80211.ko" in embedded

    for slug, binfo in loaded["boards"].items():
        for variant in ("factory_ap", "factory_sta", "sysupgrade_ap", "sysupgrade_sta"):
            v = binfo[variant]
            img_path = REPO_ROOT / v["path"]
            assert img_path.exists(), f"Missing {img_path}"
            raw = img_path.read_bytes()
            assert len(raw) == v["size_bytes"]
            assert hashlib.sha256(raw).hexdigest() == v["sha256"]
