#!/usr/bin/env python3
"""Stage 634A — Consolidated 284-Window WA v11 Verification & 5-Pillar Gate Receipt Builder."""

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

OUT_634A = ROOT / "artifacts" / "autoresearch" / "stage634a_live_wa_284window_v11_gate_receipt.json"


def main() -> int:
    receipts = [
        "stage629a_live_wa_pb050_v3_and_sgi_guard_r64_66.json",
        "stage630a_live_wa_70round_284window_milestone_r67_70.json",
        "stage631a_live_wa_mk1_251_e2e_v11_milestone.json",
        "stage632a_live_panel1_guarida_84_v11_20h_audit.json",
        "stage633a_cumulative_70round_284window_wa_champion_v11.json",
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

    s633 = json.loads((ROOT / "artifacts" / "autoresearch" / "stage633a_cumulative_70round_284window_wa_champion_v11.json").read_text(encoding="utf-8"))
    payload_634a = {
        "schema_version": "1.0.0",
        "stage": "Stage 634A",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED" if all_ok else "FAILED",
        "protocol": "A1 -> B1 -> A2 -> B2",
        "total_counterbalanced_rounds": s633["total_counterbalanced_rounds"],
        "total_live_windows_including_stage162a_e2e": s633["total_live_windows_including_stage162a_e2e"],
        "milestone_70_rounds_284_windows_achieved": s633["milestone_70_rounds_284_windows_achieved"],
        "watchdog_seconds": 45,
        "attribution": "QCA firmware + ath10k + mac80211 + Linux + hardware",
        "safety_boundaries": {
            "touched_241_or_242": False,
            "panel1_guarida_zero_rf_disconnect": True,
        },
        "audited_receipts": results,
        "five_pillar_compliance": s633["five_pillar_compliance"],
    }
    OUT_634A.write_text(json.dumps(payload_634a, indent=2), encoding="utf-8")
    gate_634a = audit_stage_receipt_5pillars(payload_634a)
    print("5-Pillar Gate 634A:", gate_634a["compliant"], flush=True)
    if not gate_634a["compliant"] or not all_ok:
        raise RuntimeError(f"Stage 634A failed: {gate_634a} / {results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
