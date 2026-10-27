#!/usr/bin/env python3
"""Stage820A: one-line evidence progress and explicit, offline tester matrix."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.sim.run_stage819a_guarida_tower_v10_triple_patch_and_xw_mixed_tdma_pareto import (
    BOUNDARY, emit, pillars, source,
)

SLUG = "stage820a_executive_1line_progress_and_tester_matrix_v10"
INPUTS = (
    ("817A", "stage817a_universal_pb060_triple_patch_openwrt_airos_kit"),
    ("818A", "stage818a_ltu_4096qam_12x_ldpc_and_super4096_safe_kit"),
    ("819A", "stage819a_guarida_tower_v10_triple_patch_and_xw_mixed_tdma_pareto"),
)


def build(root: Path = ROOT) -> dict:
    matrix = []
    sources = [source(root, "tools/observability/build_stage820a_executive_1line_progress_and_tester_matrix_v10.py")[0]]
    for stage, slug in INPUTS:
        pin, obj = source(root, f"artifacts/autoresearch/{slug}.json")
        sources.append(pin)
        matrix.append({"stage": stage, "receipt_present": obj is not None,
                       "reported_status": obj.get("status") if obj else "MISSING",
                       "local_artifact_status": "PRESENT_UNREVIEWED" if obj else "MISSING",
                       "physical_status": "UNKNOWN", "deployment_approved": False,
                       "required_tester_evidence": {
                           "817A": "Exact board/firmware ABI, preimage hashes, patch readback, rollback, coldboot and AP-side stock-airOS8 interoperability.",
                           "818A": "br1-scoped DHCP capture, reboot persistence, supported modulation getter; 4096-QAM/12x/LDPC capability and rollback.",
                           "819A": "Calibrated matched-load 32-CPE topology and A1/B1/A2/B2 IPTV/VoIP/bulk traces; keep pending CPE separate.",
                       }[stage]})
    present = sum(row["receipt_present"] for row in matrix)
    line = f"V10 offline: {present}/3 recibos presentes; simulacion 819A; aceptacion fisica UNKNOWN; 0 ventanas live nuevas; deploy no autorizado."
    receipt = {"stage": "820A", "status": "CONFIRMED", "execution_mode": "OFFLINE_OBSERVABILITY",
               "claim_scope": "presence and source-report reconciliation only",
               "attribution": ["external controller"], "boundary": dict(BOUNDARY),
               "executive_1line": line, "tester_matrix": matrix, "sources": sources,
               "false_positive_rate_pct": None, "false_negative_rate_pct": None,
               "five_pillar_compliance": pillars("820A", "tri-state evidence matrix; no physical PASS from receipt presence")}
    rows = "\n".join(f"| {r['stage']} | {r['reported_status']} | UNKNOWN |" for r in matrix)
    return emit(root, SLUG, receipt, "# Stage820A executive progress and tester matrix v10\n\n"
                + line + "\n\n| Stage | Imported status | Physical acceptance |\n| --- | --- | --- |\n" + rows
                + "\n\nReceipt presence is reported separately from local independent review and hardware acceptance.\n"
                "Tester requirements are prospective; this artifact does not contact testers or authorize deployment.\n"
                "False-positive and false-negative rates are unknown without labeled observations.\n"
                "No SSH, remote commands, radio mutations or new live windows.\n")


def main() -> int:
    print(build()["executive_1line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
