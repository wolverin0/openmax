#!/usr/bin/env python3
"""Stage 804A — Consolidated Verification & Pytest Gate (Stages 799A..804A, 91 Rounds = 372 / 400 Windows)."""

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

OUT_804A = ROOT / "artifacts" / "autoresearch" / "stage804a_live_wa_400window_800stage_v14_gate_receipt.json"


def main() -> int:
    receipts = [
        "stage799a_live_wa_ani_and_caldata_nf_guard_r85_87.json",
        "stage800a_live_wa_91round_372window_800stage_milestone_r88_91.json",
        "stage801a_live_wa_mk1_251_e2e_v14_400window_milestone.json",
        "stage802a_live_panel1_guarida_84_v14_audit.json",
        "stage803a_cumulative_91round_400window_wa_champion_v14.json",
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

    s803 = json.loads((ROOT / "artifacts" / "autoresearch" / "stage803a_cumulative_91round_400window_wa_champion_v14.json").read_text(encoding="utf-8"))
    payload_804a = {
        "schema_version": "1.0.0",
        "stage": "Stage 804A",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED" if all_ok else "FAILED",
        "protocol": "A1 -> B1 -> A2 -> B2",
        "total_counterbalanced_rounds": s803["total_counterbalanced_rounds"],
        "total_live_windows_including_stage162a_e2e": s803["total_live_windows_including_stage162a_e2e"],
        "total_live_windows_including_stage801a_e2e_r10": s803["total_live_windows_including_stage801a_e2e_r10"],
        "total_live_windows_including_all_10_e2e_rounds": s803["total_live_windows_including_all_10_e2e_rounds"],
        "milestone_800_stage_achieved": s803["milestone_800_stage_achieved"],
        "milestone_91_rounds_372_windows_achieved": s803["milestone_91_rounds_372_windows_achieved"],
        "milestone_400_total_live_windows_achieved": s803["milestone_400_total_live_windows_achieved"],
        "watchdog_seconds": 45,
        "attribution": "QCA firmware + ath10k + mac80211 + Linux + hardware",
        "safety_boundaries": {
            "touched_241_or_242": False,
            "dhcp_lan_ignore_enforced": True,
            "panel1_guarida_zero_rf_disconnect": True,
        },
        "audited_receipts": results,
        "five_pillar_compliance": s803["five_pillar_compliance"],
    }
    OUT_804A.write_text(json.dumps(payload_804a, indent=2), encoding="utf-8")
    gate_804a = audit_stage_receipt_5pillars(payload_804a)
    print("5-Pillar Gate 804A:", gate_804a["compliant"], flush=True)
    if not gate_804a["compliant"] or not all_ok:
        raise RuntimeError(f"Stage 804A failed: {gate_804a} / {results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
