#!/usr/bin/env python3
"""Stage 809A — PB-040 to PB-070 quad-patch Pareto, projected from receipt data.

This is a **simulation**, and its inputs are **real receipt fields**, not invented numbers. That
distinction is the whole point: a Pareto front computed from a dry-run receipt is a **projection**,
and labelling it as a measurement would be the kind of fabrication this series refuses.

Inputs:

  * `artifacts/qca988x/pb_040_inert_mutation_dryrun_receipt.json` — the **only** gate with per-role
    measured diffs. Each `roles_verified` entry carries `mutation_offset_in_segment`,
    `expected_diff_bytes`, `observed_total_diff_bytes` and `changed_byte_offsets_in_dram`.
  * `artifacts/qca988x/pb_060_070_pilot_and_verdict.json` — PB-070's readiness: `ready_to_execute`,
    `unmet_prerequisites`, `safety_level`.

Two objectives are minimised, both taken straight from PB-040:

| Objective | Field | Meaning |
| :--- | :--- | :--- |
| **cost** | `observed_total_diff_bytes` | bytes that actually changed |
| **offset** | `mutation_offset_in_segment` | how far into the segment the anchor sits |

The Pareto front keeps every role that is not dominated on both. A role with equal cost and equal
offset dominates nothing, so ties are reported as such rather than resolved arbitrarily.

**All four roles are blocked.** PB-040 states `spi_flash_write_allowed: false` and
`operator_gate_required_for_bench: true`; PB-070 states `ready_to_execute: false` with unmet
prerequisites. So the front is a **planning artefact for a gated bench**, never an execution order.

`execution_authorised = 0`. Nothing here may be used to justify a write.

Radio safety: static only. Reads two JSON files; no firmware, no flash, no radio.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PB = REPO_ROOT / "artifacts" / "qca988x"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage809a_pb040_to_pb070_quad_patch_pareto.json")

PB040 = PB / "pb_040_inert_mutation_dryrun_receipt.json"
PB060_070 = PB / "pb_060_070_pilot_and_verdict.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    pb040 = load(PB040) if PB040.exists() else {}
    pb070 = load(PB060_070) if PB060_070.exists() else {}

    roles = []
    for name, r in (pb040.get("roles_verified") or {}).items():
        roles.append(dict(
            role=name,
            cost=int(r.get("observed_total_diff_bytes", 0)),
            expected=int(r.get("expected_diff_bytes", 0)),
            offset=int(r.get("mutation_offset_in_segment", 0)),
            dram=float("nan") if not isinstance(r.get("changed_byte_offsets_in_dram"), list)
            else len(r["changed_byte_offsets_in_dram"]),
            segment=r.get("target_dram_segment"),
            anchor=r.get("source_anchor_ascii"),
            mutated=r.get("mutated_anchor_ascii")))
    roles.sort(key=lambda x: x["role"])

    # Pareto front on (cost, offset), both minimised
    front, dominated = [], []
    for r in roles:
        is_dom = any((o["cost"] <= r["cost"] and o["offset"] <= r["offset"]
                      and (o["cost"] < r["cost"] or o["offset"] < r["offset"]))
                     for o in roles if o["role"] != r["role"])
        (dominated if is_dom else front).append(r)

    readiness = (pb070.get("prerequisite_readiness") or {}).get("PB-070", {})
    gated = dict(
        spi_flash_write_allowed=pb040.get("spi_flash_write_allowed"),
        automatic_execution_allowed=pb040.get("automatic_execution_allowed"),
        operator_gate_required=pb040.get("operator_gate_required_for_bench"),
        pb070_ready=readiness.get("ready_to_execute"),
        pb070_unmet=readiness.get("unmet_prerequisites"),
        pb070_safety_level=readiness.get("safety_level"))

    total_cost = sum(r["cost"] for r in roles)
    front_cost = sum(r["cost"] for r in front)
    all_blocked = (gated["spi_flash_write_allowed"] is False
                   and gated["pb070_ready"] is False)

    report = dict(
        meta=dict(stage="809A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/sim/run_stage809a_pb040_to_pb070_quad_patch_pareto.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static simulation; reads two JSON receipts only; no firmware, "
                        "no flash, no radio",
                  method="two-objective Pareto (cost = observed diff bytes, offset = mutation "
                         "offset in segment) over PB-040 roles_verified, cross-checked against "
                         "PB-070 readiness",
                  label="PROJECTION FROM RECEIPT DATA - not a measurement, not an execution order",
                  radio_safety="static only"),
        inputs=dict(pb040=dict(path=PB040.relative_to(REPO_ROOT).as_posix(),
                               sha256=hashlib.sha256(PB040.read_bytes()).hexdigest(),
                               gate=pb040.get("gate_id"), phase=pb040.get("phase")),
                    pb060_070=dict(path=PB060_070.relative_to(REPO_ROOT).as_posix(),
                                   sha256=hashlib.sha256(PB060_070.read_bytes()).hexdigest(),
                                   gates=pb070.get("gates_covered"))),
        roles=roles,
        pareto_front=front,
        dominated=dominated,
        gates=gated,
        summary=dict(roles_parsed=len(roles),
                     pareto_front_size=len(front),
                     dominated_count=len(dominated),
                     total_cost_bytes=total_cost,
                     front_cost_bytes=front_cost,
                     cost_fraction_on_front=(round(front_cost / total_cost, 4)
                                             if total_cost else None),
                     all_roles_blocked=int(all_blocked),
                     execution_authorised=0,
                     measurement_or_projection="projection"),
        gaps=["this is a projection from a dry-run receipt, not a measurement of any deployed "
              "behaviour",
              "PB-070 is not ready: unmet prerequisites are listed and spi_flash_write_allowed is "
              "false, so no role may be executed",
              "the two objectives are both taken from PB-040, so the front cannot reveal a "
              "trade-off that PB-040 did not already record",
              "the offsets are per-segment and the segment base is ambiguous (Stage 806A), so the "
              "front is ordinal only",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[809A] roles={s['roles_parsed']} front={s['pareto_front_size']} "
          f"dominated={s['dominated_count']} cost={s['total_cost_bytes']}B "
          f"front_cost={s['front_cost_bytes']}B blocked={s['all_roles_blocked']} "
          f"exec_authorised=0")
    for r in front:
        print(f"        FRONT {r['role'][:44]:<44} cost={r['cost']} off={r['offset']}")
    print(f"[809A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
