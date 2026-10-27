from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage342a_ltu_short_queue_micro_ap_re() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage342a_ltu_short_queue_micro_ap_re.json"
    doc_path = ROOT / "docs/STAGE342A_LTU_SHORT_QUEUE_MICRO_AP_RE.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "342A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_audit"]["touched_dev_ame_nodes"] is False
    assert data["ame_drv_sh_dissection"]["lines"] == 526
    assert data["ame_drv_sh_dissection"]["rt_fifo_threads"]["ame.core.Hi"]["prio"] == 90
    assert data["ame_drv_sh_dissection"]["rt_fifo_threads"]["ame.core.Frm"]["prio"] == 85
    sq = data["short_queue_vs_full_ptmp_architecture"]["sq_micro_ap_mode"]
    std = data["short_queue_vs_full_ptmp_architecture"]["standard_64cpe_ptmp_mode"]
    assert sq["total_l2q_descriptor_ring_entries"] < std["total_l2q_descriptor_ring_entries"]
    assert sq["ame_core_frm_scan_latency_us"] < std["ame_core_frm_scan_latency_us"]

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
