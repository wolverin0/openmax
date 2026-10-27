"""
Tests for Stage 44C (`T-S44C-GEM2-IMAGEBUILDER-CHAMPION-V11-AND-CLOSED-LOOP-REACTOR-V11`):
Verifies:
  1. `render_uci_defaults_98_futuramax_champion_v11_aqm()` embeds Stage 37A Champion v11
     (`fq_quantum 4542` on AP / `1514` on CPE, `fq_limit 2048` on AP / `1024` on CPE,
     `fq_memory_limit 4194304`, `AC_VO 300/600`, `AC_VI 1200/2400`, `AC_BE 1500/3000`,
     `AC_BK 500/1000`, `aql_threshold 5000`) alongside `99-futuramax-wds-dms` and Dual-NMS coexistence.
  2. `ingest_stage37a_champion_v11_and_synthesize_m22_m23()` ingests `S37A-R1` (`REFUTED`) and
     `S37A-R2` (`CONFIRMED` Champion v11) and synthesizes `M22` and `M23`.
"""

from __future__ import annotations

from pathlib import Path

from controller.multiradio_golden_profile_applicator import FORBIDDEN_TOKENS
from firmware.openwrt.futuramax_openwrt_imagebuilder_packager import (
    STAGE44C_OUTPUT_JSON,
    TARGET_DEVICE_SPECS,
    build_imagebuilder_overlay_for_target,
    generate_stage44c_imagebuilder_champion_v11_manifest,
    render_uci_defaults_98_futuramax_champion_v11_aqm,
)
from tools.research.closed_loop_research_reactor import (
    DISCOVERY_QUEUE_JSON,
    VAULT_ROOT,
    ingest_stage37a_champion_v11_and_synthesize_m22_m23,
)


def test_stage44c_imagebuilder_champion_v11_uci_defaults_and_manifest(tmp_path: Path) -> None:
    for target_id in TARGET_DEVICE_SPECS:
        v11_script = render_uci_defaults_98_futuramax_champion_v11_aqm(target_id)
        assert "fq_memory_limit 4194304" in v11_script
        assert 'echo "0 300 600"' in v11_script
        assert 'echo "1 1200 2400"' in v11_script
        assert 'echo "2 1500 3000"' in v11_script
        assert 'echo "3 500 1000"' in v11_script
        assert "echo 5000 >" in v11_script

        if target_id in ("ubnt_lap-120", "ubnt_rocket-prism-5ac-gen2"):
            assert "fq_quantum 4542" in v11_script
            assert "fq_limit 2048" in v11_script
        else:
            assert "fq_quantum 1514" in v11_script
            assert "fq_limit 1024" in v11_script

        for tok in FORBIDDEN_TOKENS:
            assert tok not in v11_script.lower()

        bundle = build_imagebuilder_overlay_for_target(target_id)
        files = bundle["overlay_files"]
        assert "files/etc/uci-defaults/98-futuramax-champion-v11-aqm" in files
        assert "files/etc/hotplug.d/net/99-futuramax-wds-dms" in files
        assert "files/usr/sbin/fmx_uisp_ws_reporter" in files
        assert "files/usr/sbin/fmx_netjson_watchdog" in files

    out_manifest = tmp_path / "stage44c_manifest.json"
    manifest = generate_stage44c_imagebuilder_champion_v11_manifest(output_path=out_manifest)
    assert out_manifest.exists()
    assert STAGE44C_OUTPUT_JSON.exists()
    assert manifest["stage"] == "44C"
    assert manifest["targets_count"] == 4


def test_stage44c_closed_loop_reactor_v11_synthesizes_m22_and_m23(tmp_path: Path) -> None:
    out_receipt = tmp_path / "stage44c_reactor.json"
    res = ingest_stage37a_champion_v11_and_synthesize_m22_m23(output_path=out_receipt)
    assert out_receipt.exists()
    assert res["stage"] == "44C"

    events = {e["round_id"]: e for e in res["ingested_reactor_events"]}
    assert events["S37A-R1"]["empirical_status"] == "HW_REFUTED_OR_BOUNDED"
    assert events["S37A-R1"]["gp_delta_pct"] == -3.628
    assert events["S37A-R2"]["empirical_status"] == "HW_CONFIRMED"
    assert events["S37A-R2"]["gp_delta_pct"] == 2.648

    mids = [m["mechanism_id"] for m in res["next_wave_mechanisms_m22_to_m23"]]
    assert mids == ["M22", "M23"]

    fb_dir = VAULT_ROOT / "notes" / "empirical_feedback"
    assert (fb_dir / "empirical_feedback_S37A-R1.md").exists()
    assert (fb_dir / "empirical_feedback_S37A-R2.md").exists()
    assert DISCOVERY_QUEUE_JSON.exists()
