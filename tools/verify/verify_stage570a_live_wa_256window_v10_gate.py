#!/usr/bin/env python3
"""Stage 570A — Consolidated 256-Window WA v10 Verification & 5-Pillar Gate Receipt Builder."""

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

OUT_570A = ROOT / "artifacts" / "autoresearch" / "stage570a_live_wa_256window_v10_gate_receipt.json"


def main() -> int:
    receipts = [
        "stage565a_live_wa_pb050_v2_and_pacing_r57_59.json",
        "stage566a_live_wa_256window_milestone_r60_63.json",
        "stage567a_live_wa_mk1_251_e2e_v10_milestone.json",
        "stage568a_live_panel1_guarida_84_v10_rollout_audit.json",
        "stage569a_cumulative_63round_256window_wa_champion_v10.json",
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

    s569 = json.loads((ROOT / "artifacts" / "autoresearch" / "stage569a_cumulative_63round_256window_wa_champion_v10.json").read_text(encoding="utf-8"))
    payload_570a = {
        "schema_version": "1.0.0",
        "stage": "Stage 570A",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED" if all_ok else "FAILED",
        "protocol": "A1 -> B1 -> A2 -> B2",
        "total_counterbalanced_rounds": s569["total_counterbalanced_rounds"],
        "total_live_windows_including_stage162a_e2e": s569["total_live_windows_including_stage162a_e2e"],
        "milestone_63_rounds_256_windows_achieved": s569["milestone_63_rounds_256_windows_achieved"],
        "watchdog_seconds": 45,
        "attribution": "QCA firmware + ath10k + mac80211 + Linux + hardware",
        "safety_boundaries": {
            "touched_241_or_242": False,
            "panel1_guarida_zero_rf_disconnect": True,
        },
        "audited_receipts": results,
        "five_pillar_compliance": s569["five_pillar_compliance"],
    }
    OUT_570A.write_text(json.dumps(payload_570a, indent=2), encoding="utf-8")
    gate_570a = audit_stage_receipt_5pillars(payload_570a)
    print("5-Pillar Gate 570A:", gate_570a["compliant"], flush=True)
    if not gate_570a["compliant"] or not all_ok:
        raise RuntimeError(f"Stage 570A failed: {gate_570a} / {results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
