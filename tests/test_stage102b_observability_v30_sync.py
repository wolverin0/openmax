"""Tests for Stage 102B (T-S102B-PROMETHEUS-GRAFANA-V30-CHAMPION-V23-SYNC)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.telemetry import fmx_prometheus_exporter as exporter_module
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage102b_observability_v30_sync import (
    DASHBOARD_PATH,
    DEFAULT_RECEIPT_OUT,
    REPO_ROOT,
    build_stage102b_observability_v30_sync_receipt,
    verify_stage102b_exporter_and_rules,
)


def test_stage102b_build_receipt_and_five_pillars(tmp_path: Path) -> None:
    out_file = tmp_path / "stage102b_observability_v30_sync.json"
    receipt = build_stage102b_observability_v30_sync_receipt(output_path=out_file)
    assert out_file.exists()
    assert receipt["stage"] == "102B"
    assert receipt["curation_version"] == "v30.0"
    assert receipt["status"] == "CONFIRMED"

    pillar_audit = audit_stage_receipt_5pillars(receipt)
    assert pillar_audit["compliant"] is True
    assert pillar_audit["missing_pillars"] == []

    # Also verify canonical artifact on disk
    canonical = build_stage102b_observability_v30_sync_receipt(output_path=DEFAULT_RECEIPT_OUT)
    assert DEFAULT_RECEIPT_OUT.exists()
    assert canonical["five_pillar_gate"]["compliant"] is True


def test_stage102b_exporter_v23_vlan107_ltu_superframe_and_r2ac_2xc() -> None:
    res = verify_stage102b_exporter_and_rules()
    assert res["exporter_ready"] is True
    assert res["openmetrics_eof_valid"] is True
    assert res["required_metrics_present"] is True
    assert res["missing_metrics"] == []
    assert res["required_alerts_present"] is True
    assert res["missing_alerts"] == []


def test_stage102b_drift_detection_across_all_four_v30_domains() -> None:
    now = 2_000_000_000.0
    exp = exporter_module.TelemetryExporter(expected_links=("link1",), clock=lambda: now + 60.0)

    def make_obs(seq: int, gen: str, **extra):
        obs = {
            "link": "link1",
            "generation": gen,
            "ap": "ap1",
            "peer_mac": "02:00:00:00:00:01",
            "boot_id": "boot-1",
            "timestamp_s": now + (seq - 1) * 60.0,
            "probe_seq": seq,
            "survey_active_time_ms": 1000 + seq * 100,
            "tx_packets": 100 + seq * 10,
            "rx_packets": 200 + seq * 10,
            "icmp_sent": 5,
            "icmp_rcvd": 5,
            "l2_associated": True,
            "probe_scope": "ap_local",
            "l2_scope": "station",
            "avg_rtt_ms": 2.0,
        }
        obs.update(extra)
        return {"schema_version": 1, "observations": [obs]}

    # 1. OpenWrt v23 healer inactive -> compliant == 0, VLAN107 p95 > 12ms -> compliant == 0
    v23_bad = {
        "healer_daemon_active": False,
        "xc_auto_heal_recovery_ms": 2500.0,
        "survivor_wa_to_mk1_p95_rtt_ms": 20.218,
        "vlan107_eth0_107_tx_queue_len": 1000,
        "aql_be_low_us": 3000,
        "aql_be_high_us": 6000,
        "aql_threshold": 12000,
    }
    mk1_bad = {
        "dscp_ef_cs4_preserved": False,
        "qos_egress_ingress_map_active": False,
        "btest_port_2000_reachable": True,
        "cpe_to_mk1_e2e_p50_rtt_ms": 4.393,
        "cpe_to_mk1_e2e_p95_rtt_ms": 15.798,
        "voip_jitter_ms": 2.55,
    }
    assert exp.ingest(make_obs(1, "openwrt_wa", openwrt_v23=v23_bad, vlan107_mk1=mk1_bad), now=now)
    assert exp.ingest(make_obs(2, "openwrt_wa", openwrt_v23=v23_bad, vlan107_mk1=mk1_bad), now=now + 60.0)
    rendered = exp.render(now=now + 60.0)
    assert 'fmx_openwrt_v23_profile_compliant{ap="ap1",generation="openwrt_wa",link="link1",peer_mac="02:00:00:00:00:01"} 0' in rendered
    assert 'fmx_vlan107_mk1_dscp_qos_compliant{ap="ap1",generation="openwrt_wa",link="link1",peer_mac="02:00:00:00:00:01"} 0' in rendered


def test_stage102b_dashboard_and_doc_line_budget() -> None:
    build_stage102b_observability_v30_sync_receipt(output_path=DEFAULT_RECEIPT_OUT)
    dash = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    panel_ids = {p["id"] for p in dash["panels"]}
    assert {44, 45, 46, 47}.issubset(panel_ids)

    doc_path = REPO_ROOT / "docs" / "STAGE102B_OBSERVABILITY_V30_CHAMPION_V23_SYNC.md"
    text = doc_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 180
    assert text.startswith("<!-- doc-head:")
    assert text.count("<!-- doc-head:") == 1
    assert text.count("<!-- /doc-head -->") == 1
