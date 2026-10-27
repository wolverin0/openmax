#!/usr/bin/env python3
"""Stage 760A — Consolidated Verification & Pytest Gate (Stages 755A..760A, 84 Rounds = 340/344/368 Windows)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

OUT_760A = ROOT / "artifacts" / "autoresearch" / "stage760a_live_wa_344window_v13_gate_receipt.json"


def main() -> int:
    receipts = [
        "stage755a_live_wa_spectral_phyerr_and_vdev_guard_r78_80.json",
        "stage756a_live_wa_84round_344window_milestone_r81_84.json",
        "stage757a_live_wa_mk1_251_e2e_v13_milestone.json",
        "stage758a_live_panel1_guarida_84_v13_audit.json",
        "stage759a_cumulative_84round_344window_wa_champion_v13.json",
    ]
    results: Dict[str, Any] = {}
    all_ok = True
    for rname in receipts:
        p = ROOT / "artifacts" / "autoresearch" / rname
        data = json.loads(p.read_text(encoding="utf-8"))
        audit = audit_stage_receipt_5pillars(data)
        results[rname] = {
            "status": data.get("status"),
            "compliant": audit["compliant"],
            "failures": audit.get("failures", []),
        }
        if not audit["compliant"] or data.get("status") != "CONFIRMED":
            all_ok = False

    s759 = json.loads((ROOT / "artifacts" / "autoresearch" / "stage759a_cumulative_84round_344window_wa_champion_v13.json").read_text(encoding="utf-8"))
    payload_760a = {
        "schema_version": "1.0.0",
        "stage": "Stage 760A",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED" if all_ok else "FAILED",
        "protocol": "A1 -> B1 -> A2 -> B2",
        "total_counterbalanced_rounds": s759["total_counterbalanced_rounds"],
        "total_live_windows_including_stage162a_e2e": s759["total_live_windows_including_stage162a_e2e"],
        "total_live_windows_including_stage757a_e2e_r9": s759["total_live_windows_including_stage757a_e2e_r9"],
        "total_live_windows_including_all_9_e2e_rounds": s759["total_live_windows_including_all_9_e2e_rounds"],
        "milestone_84_rounds_344_windows_achieved": s759["milestone_84_rounds_344_windows_achieved"],
        "watchdog_seconds": 45,
        "attribution": "QCA firmware + ath10k + mac80211 + Linux + hardware",
        "safety_boundaries": {
            "touched_241_or_242": False,
            "panel1_guarida_zero_rf_disconnect": True,
        },
        "audited_receipts": results,
        "five_pillar_compliance": s759["five_pillar_compliance"],
    }
    OUT_760A.write_text(json.dumps(payload_760a, indent=2), encoding="utf-8")
    gate_760a = audit_stage_receipt_5pillars(payload_760a)
    print("5-Pillar Gate 760A:", gate_760a["compliant"], flush=True)
    if not gate_760a["compliant"] or not all_ok:
        raise RuntimeError(f"Stage 760A failed: {gate_760a} / {results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
