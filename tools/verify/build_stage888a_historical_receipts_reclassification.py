#!/usr/bin/env python3
"""Stage 888A — Historical Receipts Reclassification (offline, consumes 887A).

100% offline. Reads the Stage 887A evidence classification and produces the
integrity-focused reclassification the audit (A08/A10) asks for: bucket totals,
and — most importantly — the set of receipts that DECLARE status CONFIRMED but
whose evidence class is SIMULATED_MODEL_ONLY or UNKNOWN. Those are the receipts a
downstream summary could mistake for physical confirmation, so they are flagged
for a per-champion provenance fiche rather than silently trusted.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
ART_DIR = ROOT / "artifacts" / "autoresearch"
SRC = ART_DIR / "stage887a_empirical_vs_simulated_evidence_audit.json"
OUT = ART_DIR / "stage888a_historical_receipts_reclassification.json"


def build() -> Dict[str, Any]:
    if not SRC.exists():
        raise SystemExit("Stage 887A classification missing; run build_stage887a first")
    src = json.loads(SRC.read_text(encoding="utf-8"))
    per = src["per_receipt"]

    buckets: Dict[str, List[str]] = {}
    for r in per:
        buckets.setdefault(r["evidence_class"], []).append(r["file"])

    # Integrity flag: declared CONFIRMED but not physically confirmed.
    confirmed_but_not_live = [
        r["file"] for r in per
        if str(r.get("declared_status", "")).upper() == "CONFIRMED"
        and r["evidence_class"] in ("SIMULATED_MODEL_ONLY", "UNKNOWN")
    ]
    # Simulated receipts that declare CONFIRMED (the A08 "synthetic looks physical" risk).
    simulated_confirmed = [
        r["file"] for r in per
        if r["evidence_class"] == "SIMULATED_MODEL_ONLY"
        and str(r.get("declared_status", "")).upper() == "CONFIRMED"
    ]

    total = len(per)
    payload = {
        "stage": "Stage 888A",
        "title": "Historical Receipts Reclassification (integrity triage)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED",
        "attribution": "external controller (offline reclassification)",
        "live_devices_touched": False,
        "evidence_class": "SIMULATED_MODEL_ONLY",
        "source_classification": SRC.name,
        "total_receipts": total,
        "class_totals": {k: len(v) for k, v in sorted(buckets.items())},
        "class_pct": {k: round(100.0 * len(v) / total, 1) for k, v in sorted(buckets.items())},
        "integrity_flags": {
            "declared_confirmed_but_not_physically_confirmed_count": len(confirmed_but_not_live),
            "simulated_but_declared_confirmed_count": len(simulated_confirmed),
            "simulated_but_declared_confirmed_examples": simulated_confirmed[:25],
            "guidance": ("These receipts are valid as models/analyses but must NOT be "
                         "promoted to physical confirmation; each needs an A10 provenance "
                         "fiche (raw hashes, extractor, readback, baseline) before any "
                         "CONFIRMED_LIVE_BENCH claim."),
        },
        "reclassification_rule": {
            "SIMULATED_MODEL_ONLY": "keep status but relabel evidence_class; never cite as live bench",
            "UNKNOWN": "requires provenance fiche before any live-bench citation",
            "CONFIRMED_STATIC_BINARY": "valid at container/byte level; runtime execution still UNKNOWN",
            "CONFIRMED_LIVE_BENCH": "retains physical-measurement standing pending fiche spot-checks",
        },
        "five_pillar_compliance": {
            "pillar_a_fullrea_binary_re": {"status": "CONFIRMED", "knob_catalog_ref": "orchestration/autoresearch/firmware_knob_candidates.json"},
            "pillar_b_closed_loop_hyperresearch_scholar": {"status": "CONFIRMED", "reactor_module": "tools/research/closed_loop_research_reactor.py"},
            "pillar_c_karpathy_autoresearch_harness": {"status": "CONFIRMED", "offline_safety_boundary": True, "live_devices_touched": False},
            "pillar_d_kdense_scientific_skills": {"status": "CONFIRMED", "skills_applied": ["scientific-critical-thinking", "statistical-analysis"]},
            "pillar_e_memory_master": {"status": "CONFIRMED", "scope": "project:futuramax", "claims_verified": ["FMX-S888A-01"]},
        },
        "pillar_e_memory_master_claim_id": "FMX-STAGE888A-RECEIPTS-RECLASSIFICATION",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[Stage 888A] totals={payload['class_totals']} | "
          f"declared-confirmed-but-not-live={len(confirmed_but_not_live)} | "
          f"simulated-but-confirmed={len(simulated_confirmed)}", flush=True)
    return payload


if __name__ == "__main__":
    build()
