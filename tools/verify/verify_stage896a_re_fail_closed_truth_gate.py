#!/usr/bin/env python3
"""Stage 896A — fail-closed truth gate over the 891A..895A receipts.

The gate exists because Stages 891A..895A produce numbers that can be quoted out of context. It
asserts the structural claims and the **negative** ones: nothing may be promoted across the boundaries
the audit drew.

Invariants:

| Stage | Asserted |
| :--- | :--- |
| **891A** | every container parses, zero failures, all compressed, 12 patches valid, 3 of 3 RAM roles matched |
| **892A** | 7 gates, 3 with static provenance, 2 present on target, **0 with site execution**, 7 pending, 0 dmesg |
| **893A** | 143 classified, structural completeness, residual listed and counted |
| **894A** | 258 classified, at least 10 modules tracked with a per-module live fraction |
| **895A** | 333 receipts, tallies sum, **0 classifier disagreements**, 0 gates at runtime, 5 promotion rules |

Cross-stage:

  * 891A's container verdict and 892A's static column must agree on how many gates have a carrier;
  * 892A and 895A must both report **zero** gates at runtime;
  * 893A and 894A label agreement with 895A must be exact, which 895A already computes as
    `classifier_disagreement`.

Radio safety: static only. Reads JSON receipts only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AR = REPO_ROOT / "artifacts" / "autoresearch"
OUT = AR / "stage896a_re_fail_closed_truth_gate.json"

R = {
    "891A": AR / "stage891a_sgmt_fail_closed_binary_audit.json",
    "892A": AR / "stage892a_pb040_pb100_binary_vs_runtime_audit.json",
    "893A": AR / "stage893a_xtensa_findings_truth_classification.json",
    "894A": AR / "stage894a_ko_module_claims_truth_classification.json",
    "895A": AR / "stage895a_ko_module_claims_truth_table.json",
}


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    data = {k: load(p) for k, p in R.items()}
    failures: list[str] = []
    checks: list[dict] = []

    def check(stage: str, name: str, ok: bool, detail: str = "") -> None:
        checks.append(dict(stage=stage, check=name, ok=bool(ok), detail=detail))
        if not ok:
            failures.append(f"{stage}:{name} {detail}".strip())

    for stage, receipt in data.items():
        if receipt is None:
            check(stage, "receipt_present", False, "missing or unreadable")
            continue
        check(stage, "receipt_present", True)
        check(stage, "radio_safety", receipt["meta"]["radio_safety"] == "static only")
        check(stage, "has_gaps", bool(receipt.get("gaps")))

    if data.get("891A"):
        s = data["891A"]["summary"]
        check("891A", "all_containers_parsed",
              s["containers_ok"] == s["containers_found"] == 35,
              f"{s['containers_ok']}/{s['containers_found']}")
        check("891A", "zero_container_failures", s["containers_failed"] == 0)
        check("891A", "zero_failure_records", s["failure_count"] == 0)
        check("891A", "segments_counted", s["total_segments"] == 140)
        check("891A", "no_uncompressed_container", s["flags_uncompressed"] == 0)
        check("891A", "all_patches_valid",
              s["patches_ok"] == s["patches_audited"] == 12,
              f"{s['patches_ok']}/{s['patches_audited']}")
        check("891A", "ram_roles_matched",
              s["ram_roles_matched"] == s["ram_roles_checked"] == 3)
        check("891A", "fail_closed", s["fail_closed"] == 1)

    if data.get("892A"):
        s = data["892A"]["summary"]
        check("892A", "seven_gates", s["gates"] == 7)
        check("892A", "three_static", s["gates_static_proven"] == 3)
        check("892A", "two_present", s["gates_on_target_present"] == 2)
        check("892A", "zero_site_execution", s["gates_site_execution_proven"] == 0)
        check("892A", "zero_runtime_proven", s["gates_runtime_proven"] == 0)
        check("892A", "all_pending", s["gates_pending"] == 7)
        check("892A", "no_dmesg", s["dmesg_receipts"] == 0)
        check("892A", "pending_statement_explicit", s["explicit_pending_statement"] == 1)

    if data.get("893A"):
        s = data["893A"]["summary"]
        check("893A", "classified_143", s["receipts_classified"] == 143)
        check("893A", "structural_complete", s["structural_complete"] == 1)
        check("893A", "residual_listed",
              s["provenance_undeclared"] == len(data["893A"]["unclassified"]))
        check("893A", "citable_plus_residual",
              s["citable_findings"] + s["provenance_undeclared"] == s["receipts_classified"])

    if data.get("894A"):
        s = data["894A"]["summary"]
        check("894A", "classified_258", s["receipts_classified"] == 258)
        check("894A", "structural_complete", s["structural_complete"] == 1)
        check("894A", "modules_tracked", s["modules_tracked"] >= 10)
        check("894A", "residual_listed",
              s["provenance_undeclared"] == len(data["894A"]["unclassified"]))
        per_module = data["894A"].get("per_module", {})
        check("894A", "per_module_fractions",
              all(0.0 <= v["live_fraction"] <= 1.0 for v in per_module.values()))

    if data.get("895A"):
        s = data["895A"]["summary"]
        check("895A", "receipts_333", s["receipts_in_range"] == 333)
        check("895A", "tallies_sum",
              s["receipts_in_range"] == (s["confirmed_live_hardware"]
                                         + s["confirmed_static_binary"]
                                         + s["simulated_model_only"] + s["refuted"]
                                         + s["provenance_undeclared"]))
        check("895A", "zero_classifier_disagreement", s["classifier_disagreements"] == 0)
        check("895A", "zero_gates_at_runtime", s["gates_runtime_proven"] == 0)
        check("895A", "seven_gates_audited", s["gates_audited"] == 7)
        check("895A", "promotion_rules_complete",
              len(data["895A"].get("promotion_rules", {})) == 5)
        check("895A", "unclassified_not_citable",
              data["895A"]["promotion_rules"]["UNCLASSIFIED"]["may"] == "nothing")

    if data.get("891A") and data.get("892A"):
        gates = ["PB-040", "PB-050", "PB-060", "PB-070", "PB-080", "PB-090", "PB-100"]
        derived = set()
        for container in data["891A"].get("containers", []):
            name = container["file"].lower().replace("-", "").replace("_", "")
            for gate in gates:
                if gate.replace("-", "").lower() in name and container["ok"] == 1:
                    derived.add(gate)
        static_gates = data["892A"]["summary"]["gates_static_proven"]
        check("cross", "static_gate_count_agrees",
              len(derived) == static_gates == 3,
              f"891A-derived={len(derived)} 892A={static_gates}")

    if data.get("892A") and data.get("895A"):
        a = data["892A"]["summary"]["gates_runtime_proven"]
        b = data["895A"]["summary"]["gates_runtime_proven"]
        check("cross", "runtime_zero_agrees", a == 0 and b == 0, f"892A={a} 895A={b}")

    if data.get("893A") and data.get("894A") and data.get("895A"):
        disagreements = data["895A"].get("classifier_disagreement", [])
        check("cross", "subset_labels_agree", len(disagreements) == 0,
              f"disagreements={len(disagreements)}")

    compliant = len(failures) == 0
    report = dict(
        meta=dict(
            stage="896A", generated_utc="2026-10-27T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/verify/verify_stage896a_re_fail_closed_truth_gate.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            audit_reference="artifacts/chatgpt_audit_1afaeb7/AUDITORIA_2026-10-27.md section A09",
            scope="offline static verification; reads five JSON receipts only",
            method="per-stage invariants plus three cross-stage agreements; compliant is the "
                   "emptiness of a named failures list",
            radio_safety="static only"),
        receipts={k: dict(path=v.relative_to(REPO_ROOT).as_posix(),
                          sha256=hashlib.sha256(v.read_bytes()).hexdigest())
                  for k, v in R.items() if v.exists()},
        checks=checks,
        failures=failures,
        summary=dict(stages_expected=len(R),
                     stages_present=sum(1 for v in data.values() if not v is None),
                     checks_run=len(checks),
                     checks_passed=sum(1 for c in checks if c["ok"]),
                     failures=len(failures),
                     cross_stage_checks=sum(1 for c in checks if c["stage"] == "cross"),
                     compliant=int(compliant)),
        gaps=[
            "the gate verifies receipt consistency and the absence of promotion, not the truth of "
            "any individual binary finding",
            "a receipt could be wrong and internally consistent, and this gate would pass it",
            "runtime remains unproven by construction: the gate asserts zero, it cannot prove one",
            "no dynamic validation"])

    write_atomic(args.out, json.dumps(report, indent=2) + "\n")

    s = report["summary"]
    print(f"[896A] stages={s['stages_present']}/{s['stages_expected']} "
          f"checks={s['checks_passed']}/{s['checks_run']} cross={s['cross_stage_checks']} "
          f"failures={s['failures']} compliant={s['compliant']}")
    for failure in failures:
        print("        FAIL", failure)
    print(f"[896A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
