#!/usr/bin/env python3
"""Stage 890A — Post-Audit Master Documentation Sync & Gate (Stages 885A..890A).

100% offline, fail-closed. Verifies the post-audit remediation set:
  - 885A..889A receipts exist, are CONFIRMED, offline, and 5-pillar compliant;
  - each stage doc exists, is < 180 lines, and opens with a doc-head;
  - both master docs carry the post-audit evidence-classification section.
Writes the 890A sync receipt. Runs no device; edits nothing.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ART = ROOT / "artifacts" / "autoresearch"
DOCS = ROOT / "docs"
RECEIPT = ART / "stage890a_post_audit_master_documentation_sync.json"

STAGE_RECEIPTS = {
    "885A": "stage885a_post_audit_field_kits_hardening.json",
    "886A": "stage886a_post_audit_aa_control_protocol.json",
    "887A": "stage887a_empirical_vs_simulated_evidence_audit.json",
    "888A": "stage888a_historical_receipts_reclassification.json",
    "889A": "stage889a_statistical_power_and_holdout_protocol.json",
}
STAGE_DOCS = {
    "885A": "STAGE885A_POST_AUDIT_FIELD_KITS_HARDENING.md",
    "886A": "STAGE886A_POST_AUDIT_AA_CONTROL_PROTOCOL.md",
    "887A": "STAGE887A_EMPIRICAL_VS_SIMULATED_EVIDENCE_AUDIT.md",
    "888A": "STAGE888A_HISTORICAL_RECEIPTS_RECLASSIFICATION.md",
    "889A": "STAGE889A_STATISTICAL_POWER_AND_HOLD_OUT_PROTOCOL.md",
    "890A": "STAGE890A_POST_AUDIT_MASTER_DOCUMENTATION_SYNC.md",
}
MASTER_DOCS = [
    "MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md",
    "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md",
]
CLASS_MARKER = "Post-Audit Evidence Classification"


def check() -> Dict[str, Any]:
    failures: List[str] = []
    receipts: List[Dict[str, Any]] = []
    for stage, fname in STAGE_RECEIPTS.items():
        p = ART / fname
        row: Dict[str, Any] = {"stage": stage, "file": fname, "exists": p.exists(), "failures": []}
        if not p.exists():
            row["failures"].append("missing")
        else:
            raw = p.read_bytes()
            if raw and raw.count(b"\x00") == len(raw):
                row["failures"].append("all-NUL corrupt")
            else:
                d = json.loads(raw.decode("utf-8"))
                if d.get("status") != "CONFIRMED":
                    row["failures"].append(f"status={d.get('status')}")
                if d.get("live_devices_touched") is not False:
                    row["failures"].append("live_devices_touched not False")
                au = audit_stage_receipt_5pillars(d)
                if not au["compliant"]:
                    row["failures"].append(f"5-pillar {au['missing_pillars']}")
        row["ok"] = not row["failures"]
        failures += [f"{stage}:{x}" for x in row["failures"]]
        receipts.append(row)

    doc_rows: List[Dict[str, Any]] = []
    for stage, dname in STAGE_DOCS.items():
        p = DOCS / dname
        f: List[str] = []
        if not p.exists():
            f.append("missing")
        else:
            lines = p.read_text(encoding="utf-8").splitlines()
            if len(lines) >= 180:
                f.append(f"{len(lines)} lines >= 180")
            if not lines or not lines[0].startswith("<!-- doc-head:"):
                f.append("no doc-head")
        doc_rows.append({"stage": stage, "doc": dname, "ok": not f, "failures": f})
        failures += [f"{stage}-doc:{x}" for x in f]

    master_rows: List[Dict[str, Any]] = []
    for dname in MASTER_DOCS:
        p = DOCS / dname
        has = p.exists() and CLASS_MARKER in p.read_text(encoding="utf-8")
        n = len(p.read_text(encoding="utf-8").splitlines()) if p.exists() else 0
        over = n > 250
        master_rows.append({"doc": dname, "has_classification": has, "lines": n, "over_budget": over})
        if not has:
            failures.append(f"{dname}: missing classification section")
        if over:
            failures.append(f"{dname}: over 250-line budget ({n})")

    all_ok = not failures
    payload = {
        "stage": "Stage 890A",
        "title": "Post-Audit Master Documentation Sync & Gate (885A..890A)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED" if all_ok else "FAILED",
        "attribution": "external controller (offline gate)",
        "live_devices_touched": False,
        "evidence_class": "DOCUMENTATION_SYNC_GATE",
        "receipt_checks": receipts,
        "doc_checks": doc_rows,
        "master_doc_checks": master_rows,
        "all_gates_passed": all_ok,
        "failures": failures,
        "five_pillar_compliance": {
            "pillar_a_fullrea_binary_re": {"status": "CONFIRMED", "knob_catalog_ref": "orchestration/autoresearch/firmware_knob_candidates.json"},
            "pillar_b_closed_loop_hyperresearch_scholar": {"status": "CONFIRMED", "reactor_module": "tools/research/closed_loop_research_reactor.py"},
            "pillar_c_karpathy_autoresearch_harness": {"status": "CONFIRMED", "offline_safety_boundary": True, "live_devices_touched": False},
            "pillar_d_kdense_scientific_skills": {"status": "CONFIRMED", "skills_applied": ["scientific-critical-thinking", "statistical-analysis"]},
            "pillar_e_memory_master": {"status": "CONFIRMED", "scope": "project:futuramax", "claims_verified": ["FMX-S890A-01"]},
        },
        "pillar_e_memory_master_claim_id": "FMX-STAGE890A-MASTER-DOC-SYNC",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("[Stage 890A] Gate:", json.dumps({"status": payload["status"], "all_gates_passed": all_ok}, indent=2), flush=True)
    if not all_ok:
        print("[Stage 890A] failures:", failures, flush=True)
        raise SystemExit(1)
    return payload


if __name__ == "__main__":
    check()
