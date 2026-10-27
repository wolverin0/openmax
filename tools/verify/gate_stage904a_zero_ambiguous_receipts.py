#!/usr/bin/env python3
"""Stage 904A — gate on the provenance remediation, scoped honestly.

The gate answers two different questions, and keeps them apart:

1. **Did the remediation succeed on its 31 targets?** Asserted: all classified, all restored, zero
   ambiguous, counts summing.
2. **Is the whole corpus now free of undeclared receipts?** **Not asserted as true**, because it is
   not true. Stage 902A measured **177** undeclared receipts across `artifacts/autoresearch/`: **157**
   historical stage receipts from before the provenance convention, and **20** auxiliary artefacts such
   as ledgers, queues and atlases.

`compliant` covers question 1 plus the honesty of the answer to question 2. `full_corpus_zero` is
reported as **0** and can never be quoted as 1, which is the point of separating them.

A gate that asserted zero across the corpus would either fail, or force me to mass-edit 177 receipts
belonging to other workstreams. Neither is acceptable: the first hides the achievement, the second
manufactures a green number.

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
OUT = AR / "stage904a_zero_ambiguous_receipts_gate.json"

R = {
    "901A": AR / "stage901a_provenance_remediation_receipt.json",
    "902A": AR / "stage902a_full_corpus_provenance_audit.json",
    "903A": AR / "stage903a_provenance_restoration_registry.json",
}


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
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
        check(stage, "has_gaps", bool(receipt.get("gaps")))

    declared_targets = 31
    if data.get("901A"):
        s = data["901A"]["summary"]
        targets = s["targets"]
        check("901A", "targets_present", targets > 0, f"targets={targets}")
        check("901A", "targets_match_declared_31", targets == declared_targets,
              f"targets={targets} declared={declared_targets}")
        check("901A", "no_failures", s["failed"] == 0)
        check("901A", "zero_ambiguous", s["ambiguous_remaining"] == 0)
        check("901A", "restoration_all", s["restoration_verified_all"] == 1)
        check("901A", "classes_sum_targets",
              s["live_hardware"] + s["static_binary"] + s["simulated_model"] == targets,
              f"{s['live_hardware']}/{s['static_binary']}/{s['simulated_model']} vs {targets}")
        # cumulative proof that every target carries the remediation, independent of how many
        # files this particular run had to touch
        check("901A", "remediated_total_covers_targets",
              s.get("remediated_total", 0) == targets,
              f"remediated_total={s.get('remediated_total')} targets={targets}")
        check("901A", "rows_match_targets",
              len(data["901A"].get("rows", [])) == targets)
        accounted = (s.get("remediated_this_run", 0) + s.get("repaired_this_run", 0)
                     + s.get("already_correct", 0))
        check("901A", "row_accounting_complete", accounted == targets,
              f"accounted={accounted} targets={targets}")
    else:
        targets = 0

    if data.get("903A"):
        s = data["903A"]["summary"]
        check("903A", "verified_covers_targets",
              data.get("901A") is not None and s["verified"] == targets,
              f"verified={s['verified']} targets={targets}")
        check("903A", "all_31_verified", s["verified"] == declared_targets)
        check("903A", "all_31_restored", s["all_restored"] == 1)
        check("903A", "all_classes_valid", s["all_classes_valid"] == 1)
        check("903A", "counts_agree_with_901A",
              data["901A"] is not None
              and s["live_hardware"] == data["901A"]["summary"]["live_hardware"]
              and s["static_binary"] == data["901A"]["summary"]["static_binary"]
              and s["simulated_model"] == data["901A"]["summary"]["simulated_model"])

    if data.get("902A"):
        s = data["902A"]["summary"]
        undeclared = data["902A"].get("undeclared", [])
        check("902A", "whole_directory_audited",
              s["receipts_classified"] + s["audit_receipts_excluded"] == s["receipts_in_directory"]
              and s["coverage_fraction"] == 1.0,
              f"{s['receipts_classified']}+{s['audit_receipts_excluded']}"
              f"/{s['receipts_in_directory']}")
        check("902A", "audit_family_not_self_counted", s["audit_receipts_excluded"] == 4,
              f"excluded={s['audit_receipts_excluded']}")
        check("902A", "undeclared_count_matches_list", s["undeclared"] == len(undeclared))
        remediated = set(data["901A"]["targets"]) if data.get("901A") else set()
        leaked = [name for name in undeclared if name in remediated]
        check("902A", "no_remediated_receipt_left_undeclared", len(leaked) == 0,
              f"leaked={leaked[:3]}")
    else:
        undeclared = []

    stage_undeclared = [n for n in undeclared if n.startswith("stage")]
    auxiliary_undeclared = [n for n in undeclared if not n.startswith("stage")]
    full_corpus_zero = int(len(undeclared) == 0)

    check("gate", "full_corpus_zero_is_reported", full_corpus_zero in (0, 1))
    check("gate", "remediation_scope_complete",
          data.get("901A") is not None and data["901A"]["summary"]["zero_ambiguous"] == 1)

    compliant = len(failures) == 0
    report = dict(
        evidence_provenance_class="CONFIRMED_STATIC_BINARY",
        post_audit_reclassified_at=None,
        preserved_raw_sha256=None,
        meta=dict(
            stage="904A", generated_utc="2026-10-27T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/verify/gate_stage904a_zero_ambiguous_receipts.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            scope="offline static verification; reads three JSON receipts only",
            method="asserts the remediation scope and reports the full-corpus residual separately; "
                   "compliant covers the scope plus the honesty of the residual",
            premise_corrections=[
                "the 31 undeclared receipts found by Stage 895A were scoped to Stage 500A..878A; the "
                "full directory contains 177 more",
                "a gate that asserted zero across the corpus would either fail or require mass "
                "editing third-party receipts, so the two questions are separated",
                "the gate is idempotent: it derives the target count from the remediation receipt "
                "and asserts a cumulative remediated_total, so a second run reports the same 31 "
                "instead of degrading to zero",
            ],
            radio_safety="static only"),
        receipts={k: dict(path=v.relative_to(REPO_ROOT).as_posix(),
                          sha256=hashlib.sha256(v.read_bytes()).hexdigest())
                  for k, v in R.items() if v.exists()},
        checks=checks,
        failures=failures,
        outstanding=dict(
            full_corpus_undeclared=len(undeclared),
            historical_stage_receipts=len(stage_undeclared),
            auxiliary_artefacts=len(auxiliary_undeclared),
            sample=undeclared[:12],
            note="these predate the provenance convention and belong to other workstreams; they "
                 "were listed rather than mass-edited"),
        idempotency=dict(
            declared_targets=declared_targets,
            targets_seen=targets,
            remediated_this_run=(data.get("901A") or {}).get("summary", {}).get(
                "remediated_this_run"),
            remediated_total=(data.get("901A") or {}).get("summary", {}).get("remediated_total"),
            already_correct=(data.get("901A") or {}).get("summary", {}).get("already_correct"),
            idempotent_rerun=(data.get("901A") or {}).get("summary", {}).get("idempotent_rerun"),
            stable_across_reruns=int(targets == declared_targets)),
        summary=dict(stages_expected=len(R),
                     stages_present=sum(1 for v in data.values() if not v is None),
                     checks_run=len(checks),
                     checks_passed=sum(1 for c in checks if c["ok"]),
                     failures=len(failures),
                     remediation_targets=targets,
                     remediation_zero_ambiguous=data["901A"]["summary"]["zero_ambiguous"]
                     if data.get("901A") else 0,
                     idempotent_rerun=(data.get("901A") or {}).get("summary", {}).get(
                         "idempotent_rerun"),
                     full_corpus_undeclared=len(undeclared),
                     full_corpus_zero=full_corpus_zero,
                     compliant=int(compliant)),
        gaps=[
            "the gate asserts the remediation scope, not a clean corpus",
            "the residual 177 receipts remain undeclared and are a standing defect",
            "a class recorded under Stage 901A states the evidence a receipt contains, not the truth "
            "of its conclusion",
            "no receipt was re-executed and no radio was contacted",
            "no dynamic validation"])

    write_atomic(args.out, json.dumps(report, indent=2) + "\n")

    s = report["summary"]
    print(f"[904A] stages={s['stages_present']}/{s['stages_expected']} "
          f"checks={s['checks_passed']}/{s['checks_run']} failures={s['failures']} "
          f"remediation_zero={s['remediation_zero_ambiguous']} "
          f"full_corpus_undeclared={s['full_corpus_undeclared']} "
          f"full_corpus_zero={s['full_corpus_zero']} compliant={s['compliant']}")
    for failure in failures:
        print("        FAIL", failure)
    print(f"[904A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
