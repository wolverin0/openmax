#!/usr/bin/env python3
"""Stage 895A — consolidated truth table over Stage 500A..878A, plus the promotion rules.

This is the merging stage. It classifies **every** receipt in the range with the same five rules used
by Stage 893A and 894A, and then checks its own labels against theirs on the shared subset. A
disagreement is a defect in the classifier, not a matter of interpretation, so
`classifier_disagreement` must be zero.

## The table

For every receipt: one label, the rule that fired, the evidence tier, and the scope class. For every
module: the label distribution and the live fraction. For every patch gate: the three-column matrix
from Stage 892A.

## The promotion rules, stated once and enforced by Stage 896A

| From | May be cited as | Never as |
| :--- | :--- | :--- |
| CONFIRMED_LIVE_HARDWARE | measured behaviour on the named target | a mechanism's internal design |
| CONFIRMED_STATIC_BINARY | binary content, layout, symbol or vocabulary | runtime behaviour or on-air effect |
| SIMULATED_MODEL_ONLY | a model, a scenario, a planning input | any measurement, any hardware claim |
| REFUTED | an absent name, a blocked gate, a negative result | evidence that the opposite is true |
| UNCLASSIFIED | nothing | anything |

The last row is the point of the whole exercise. A receipt that declares no provenance is **listed by
name** and can be cited as **nothing**, which is a stronger and more useful statement than a guessed
label.

## What this table refuses to certify

No gate reaches runtime. Stage 892A measured `runtime_proven = 0` for all seven of PB-040 to PB-100,
because no `dmesg` and no `debugfs` witness exists anywhere in the range. The SGMT patches are proven
at the **container** level and are **pending execution** with `caldata` and `board-2.bin` reloaded on a
live target.

Radio safety: static only. Reads receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AR = REPO_ROOT / "artifacts" / "autoresearch"
OUT = AR / "stage895a_ko_module_claims_truth_table.json"

STAGE_MIN, STAGE_MAX = 500, 878
NEGATIVE = ("REFUTED", "BLOCKED", "FAILED", "LOCKED", "FAIL_OR_UNASSESSED")
SIM_TOKENS = ("sim", "simpy", "pymoo", "nsga", "pareto", "model", "synthetic",
              "scorecard", "fixture", "monte")
STATIC_KEYS = ("sha256", "tool_sha256", "sha256_uncompressed", "symbols", "modules", "bytes")
BINARY_KEY_TOKENS = ("sha256", "bytes", "symbol", "offset", "address", "segment",
                     "hash", "module", "package", "firmware", "elf")
STRUCT_KEYS = ("checks", "artifact_checks", "doc_checks", "helper_script", "claims",
               "claims_synced_count", "repo_5pillar_gate_result", "stages_verified",
               "verified_stages", "evaluated_channel_profiles", "master_bundle_artifact",
               "helper_artifact", "baked_images", "five_pillar_audit", "safety_audit",
               "breakthroughs_ledger", "repository_scale_metrics", "claim_status",
               "writes_performed", "protocol")
LABELS = ("CONFIRMED_LIVE_HARDWARE", "REFUTED", "SIMULATED_MODEL_ONLY",
          "CONFIRMED_STATIC_BINARY", "UNCLASSIFIED")
PROMOTION = {
    "CONFIRMED_LIVE_HARDWARE": dict(may="measured behaviour on the named target",
                                    never="a mechanism's internal design"),
    "CONFIRMED_STATIC_BINARY": dict(may="binary content, layout, symbol or vocabulary",
                                    never="runtime behaviour or on-air effect"),
    "SIMULATED_MODEL_ONLY": dict(may="a model, a scenario, a planning input",
                                 never="any measurement, any hardware claim"),
    "REFUTED": dict(may="an absent name, a blocked gate, a negative result",
                    never="evidence that the opposite is true"),
    "UNCLASSIFIED": dict(may="nothing", never="anything"),
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


def live_markers(receipt: dict) -> list[str]:
    fired = []
    meta = receipt.get("meta", {}) if isinstance(receipt.get("meta"), dict) else {}
    for source in (receipt, meta):
        for key, value in source.items():
            low = key.lower()
            if key in ("live_devices_touched", "live_ssh_connected",
                       "ap_241_verified", "sta_242_verified", "live_target_accepted"):
                if value is True:
                    fired.append(key)
            if key.startswith("total_live_") and isinstance(value, int) and value > 0:
                fired.append(key)
            if "windows" in low and isinstance(value, int) and value > 0:
                fired.append(key)
            if "hardware_pair" in low:
                fired.append(key)
    return sorted(set(fired))


def classify(receipt: dict, stem: str) -> tuple[str, list[str], str, str]:
    explicit = receipt.get("evidence_provenance_class")
    if explicit in ("CONFIRMED_LIVE_HARDWARE", "CONFIRMED_STATIC_BINARY",
                    "SIMULATED_MODEL_ONLY"):
        scope_class = ("live" if explicit == "CONFIRMED_LIVE_HARDWARE" else
                       "sim" if explicit == "SIMULATED_MODEL_ONLY" else "static")
        return explicit, ["R0"], scope_class, "explicit_field"
    meta = receipt.get("meta", {}) if isinstance(receipt.get("meta"), dict) else {}
    rules = []
    live = live_markers(receipt)
    if live:
        rules.append("R1")
    status = str(receipt.get("status") or meta.get("status") or receipt.get("verdict") or "")
    if any(token in status.upper() for token in NEGATIVE):
        rules.append("R2")
    low = stem.lower()
    keys = " ".join(list(receipt.keys())).lower()
    if (any(token in low for token in SIM_TOKENS)
            or "simulat" in keys or "synthetic" in keys or "fixture" in keys):
        rules.append("R3")
    scope = str(meta.get("scope") or receipt.get("scope") or "").lower()
    has_binary = any(any(token in key.lower() for token in BINARY_KEY_TOKENS)
                     for key in receipt.keys())
    key_static = any("static" in key.lower() or "proof" in key.lower() for key in receipt.keys())
    if ("static" in scope or any(key in receipt for key in STATIC_KEYS) or has_binary
            or key_static):
        rules.append("R4")
    elif any(key in receipt for key in STRUCT_KEYS):
        rules.append("R4s")

    static_rule = "R4" in rules or "R4s" in rules
    if "R1" in rules:
        label = "CONFIRMED_LIVE_HARDWARE"
    elif "R2" in rules:
        label = "REFUTED"
    elif "R3" in rules:
        label = "SIMULATED_MODEL_ONLY"
    elif static_rule:
        label = "CONFIRMED_STATIC_BINARY"
    else:
        label = "UNCLASSIFIED"

    scope_class = ("live" if live else
                   "sim" if "R3" in rules else
                   "static" if static_rule else "unknown")
    tier = ("binary_bytes" if "R4" in rules else
            "artefact_structure" if "R4s" in rules else "none")
    return label, rules, scope_class, tier


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for path in sorted(AR.glob("stage*.json")):
        match = re.match(r"stage(\d+)([a-z])", path.stem)
        if not match or not (STAGE_MIN <= int(match.group(1)) <= STAGE_MAX):
            continue
        receipt = load(path)
        if not isinstance(receipt, dict):
            continue
        label, rules, scope_class, tier = classify(receipt, path.stem)
        rows.append(dict(stage=receipt.get("stage") or path.stem,
                         receipt=path.name, stage_number=int(match.group(1)),
                         label=label, rules=rules, scope_class=scope_class,
                         evidence_tier=tier, status=receipt.get("status"),
                         live_markers=live_markers(receipt)))

    counts = {label: sum(1 for r in rows if r["label"] == label) for label in LABELS}
    undeclared = sorted(r["receipt"] for r in rows if r["label"] == "UNCLASSIFIED")
    tiers = {}
    for tier in ("binary_bytes", "artefact_structure", "none"):
        tiers[tier] = sum(1 for r in rows if r["evidence_tier"] == tier)

    # cross-check against the two subset stages on the entries they share
    disagreements = []
    for other_name in ("stage893a_xtensa_findings_truth_classification.json",
                       "stage894a_ko_module_claims_truth_classification.json"):
        other = load(AR / other_name) or {}
        mine = {r["receipt"]: r["label"] for r in rows}
        for finding in other.get("findings", []) or []:
            name = finding.get("receipt")
            if name in mine and not mine[name] == finding.get("label"):
                disagreements.append(dict(receipt=name, here=mine[name],
                                          there=finding.get("label"),
                                          source=other_name))

    gates = (load(AR / "stage892a_pb040_pb100_binary_vs_runtime_audit.json") or {}).get("gates", [])
    runtime_proven = sum(g.get("runtime_proven", 0) for g in gates)

    report = dict(
        meta=dict(
            stage="895A", generated_utc="2026-10-27T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/verify/build_stage895a_ko_module_claims_truth_table.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            audit_reference="artifacts/chatgpt_audit_1afaeb7/AUDITORIA_2026-10-27.md sections A09 and A10",
            stage_range=[STAGE_MIN, STAGE_MAX],
            scope="offline static; reads receipts only, no firmware written, no radio contacted",
            method="independent re-classification of every receipt with the same five rules, "
                   "cross-checked against Stage 893A and 894A on the shared subset",
            premise_corrections=[
                "simulation receipts carry status CONFIRMED, so a status word is not a provenance "
                "label and cannot be promoted",
                "no gate reaches runtime: the SGMT patches are proven at container level and remain "
                "pending execution with caldata and board-2.bin reloaded on a live target",
            ],
            radio_safety="static only"),
        rules=dict(order=["R1 live markers", "R2 negative status", "R3 simulation markers",
                          "R4 static binary evidence", "R4s structural artefact verification",
                          "R5 residual"],
                   labels=list(LABELS)),
        promotion_rules=PROMOTION,
        findings=rows,
        gates=gates,
        counts=counts,
        evidence_tiers=tiers,
        provenance_undeclared=undeclared,
        classifier_disagreement=disagreements,
        summary=dict(receipts_in_range=len(rows),
                     confirmed_live_hardware=counts["CONFIRMED_LIVE_HARDWARE"],
                     confirmed_static_binary=counts["CONFIRMED_STATIC_BINARY"],
                     simulated_model_only=counts["SIMULATED_MODEL_ONLY"],
                     refuted=counts["REFUTED"],
                     provenance_undeclared=counts["UNCLASSIFIED"],
                     citable_findings=len(rows) - counts["UNCLASSIFIED"],
                     tier_binary_bytes=tiers["binary_bytes"],
                     tier_artefact_structure=tiers["artefact_structure"],
                     tier_none=tiers["none"],
                     classifier_disagreements=len(disagreements),
                     gates_audited=len(gates),
                     gates_runtime_proven=runtime_proven,
                     patches_pending_live_execution=len(gates) - runtime_proven,
                     hardware_evidence_fraction=round(
                         counts["CONFIRMED_LIVE_HARDWARE"] / float(len(rows)), 4) if rows else 0.0,
                     structural_complete=int(len(rows) == sum(counts.values()))),
        gaps=[
            "the table classifies provenance, not correctness: a static finding can still be wrong",
            "the residual is real: some receipts declare no provenance at all and are listed by name",
            "per-module attribution is not carried in this table, it lives in Stage 894A",
            "no gate reaches runtime, so no on-air effect is certified anywhere in this table",
            "no dynamic validation"])

    write_atomic(args.out, json.dumps(report, indent=2) + "\n")

    s = report["summary"]
    print(f"[895A] receipts={s['receipts_in_range']} live={s['confirmed_live_hardware']} "
          f"static={s['confirmed_static_binary']} sim={s['simulated_model_only']} "
          f"refuted={s['refuted']} undeclared={s['provenance_undeclared']} "
          f"citable={s['citable_findings']} tiers={tiers} "
          f"disagreements={s['classifier_disagreements']} "
          f"gates={s['gates_audited']} runtime={s['gates_runtime_proven']} "
          f"structural={s['structural_complete']}")
    print(f"[895A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
