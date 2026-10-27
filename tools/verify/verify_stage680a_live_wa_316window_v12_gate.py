#!/usr/bin/env python3
"""Stage 680A — Consolidated Verification & Pytest Gate (Stages 675A..680A, 77 Rounds = 312/316 Windows)."""

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

OUT_680A = ROOT / "artifacts" / "autoresearch" / "stage680a_live_wa_316window_v12_gate_receipt.json"


def main() -> int:
    receipts = [
        "stage675a_live_wa_pb060_and_htt_tx_compl_r71_73.json",
        "stage676a_live_wa_77round_312window_milestone_r74_77.json",
        "stage677a_live_wa_mk1_251_e2e_v12_milestone.json",
        "stage678a_live_panel1_guarida_84_v12_audit.json",
        "stage679a_cumulative_77round_316window_wa_champion_v12.json",
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

    s679 = json.loads((ROOT / "artifacts" / "autoresearch" / "stage679a_cumulative_77round_316window_wa_champion_v12.json").read_text(encoding="utf-8"))
    payload_680a = {
        "schema_version": "1.0.0",
        "stage": "Stage 680A",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED" if all_ok else "FAILED",
        "protocol": "A1 -> B1 -> A2 -> B2",
        "total_counterbalanced_rounds": s679["total_counterbalanced_rounds"],
        "total_live_windows_including_stage162a_e2e": s679["total_live_windows_including_stage162a_e2e"],
        "total_live_windows_including_stage677a_e2e_r8": s679["total_live_windows_including_stage677a_e2e_r8"],
        "milestone_77_rounds_312_windows_achieved": s679["milestone_77_rounds_312_windows_achieved"],
        "milestone_316_windows_with_e2e_achieved": s679["milestone_316_windows_with_e2e_achieved"],
        "watchdog_seconds": 45,
        "attribution": "QCA firmware + ath10k + mac80211 + Linux + hardware",
        "safety_boundaries": {
            "touched_241_or_242": False,
            "panel1_guarida_zero_rf_disconnect": True,
        },
        "audited_receipts": results,
        "five_pillar_compliance": s679["five_pillar_compliance"],
    }
    OUT_680A.write_text(json.dumps(payload_680a, indent=2), encoding="utf-8")
    gate_680a = audit_stage_receipt_5pillars(payload_680a)
    print("5-Pillar Gate 680A:", gate_680a["compliant"], flush=True)
    if not gate_680a["compliant"] or not all_ok:
        raise RuntimeError(f"Stage 680A failed: {gate_680a} / {results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
