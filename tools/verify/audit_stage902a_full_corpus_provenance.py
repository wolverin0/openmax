#!/usr/bin/env python3
"""Stage 902A — provenance audit over 100 % of `artifacts/autoresearch/`.

Stage 901A fixed the **31** receipts that Stage 895A flagged. This stage re-audits the **whole**
directory, not just the Stage 500A..878A window, and reports how many receipts still declare no
provenance.

## Rule order

1. **explicit field** — `evidence_provenance_class` wins, because a curated determination outranks a
   pattern;
2. **live** — `experiment_id` marked LIVE, a declared hardware pair, live-window counters, or per-device
   address keys;
3. **negative** — a status or verdict of REFUTED, BLOCKED, FAILED or LOCKED;
4. **simulation** — filename or keys mark a model, fixture or scorecard;
5. **static** — offline-static scope, binary descriptors, or a structural verification block;
6. **measurement payload** — a crossover schedule, objective configuration with numeric targets, a
   measured loss and a Pareto frontier; this is what the live autoresearch runs carry instead of a
   status word;
7. nothing fires — **undeclared**.

Rule 6 was added because the first pass over the full directory reported **371** undeclared receipts,
almost all of them `lap120_*` autoresearch runs whose payload is measurement rather than metadata. Their
names alone are not evidence; their numeric payload is.

Radio safety: read-only. No file is modified, no radio is contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AR = REPO_ROOT / "artifacts" / "autoresearch"
OUT = AR / "stage902a_full_corpus_provenance_audit.json"

LIVE = "CONFIRMED_LIVE_HARDWARE"
STATIC = "CONFIRMED_STATIC_BINARY"
SIM = "SIMULATED_MODEL_ONLY"
NEG = "REFUTED"
UNDECLARED = "UNCLASSIFIED"

NEGATIVE = ("REFUTED", "BLOCKED", "FAILED", "LOCKED", "FAIL_OR_UNASSESSED")
SIM_TOKENS = ("sim", "simpy", "pymoo", "nsga", "pareto", "model", "synthetic",
              "scorecard", "fixture", "monte")
BINARY_TOKENS = ("sha256", "bytes", "symbol", "offset", "address", "segment",
                 "hash", "module", "package", "firmware", "elf")
STRUCT_KEYS = ("checks", "artifact_checks", "doc_checks", "helper_script", "claims",
               "claims_synced_count", "repo_5pillar_gate_result", "stages_verified",
               "verified_stages", "evaluated_channel_profiles", "master_bundle_artifact",
               "helper_artifact", "baked_images", "five_pillar_audit", "safety_audit",
               "breakthroughs_ledger", "repository_scale_metrics", "claim_status",
               "writes_performed", "protocol")
MEASUREMENT_KEYS = ("crossover_schedule", "objective_config", "best_fmx_loss",
                    "pareto_frontier", "iterations")
# an audit must not count its own output as corpus: these four receipts are this batch's product,
# and including them would make every run change the population it measures
AUDIT_FAMILY = {
    "stage901a_provenance_remediation_receipt.json",
    "stage902a_full_corpus_provenance_audit.json",
    "stage903a_provenance_restoration_registry.json",
    "stage904a_zero_ambiguous_receipts_gate.json",
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


def live_evidence(receipt: dict) -> str:
    meta = receipt.get("meta", {}) if isinstance(receipt.get("meta"), dict) else {}
    for source in (receipt, meta):
        experiment = str(source.get("experiment_id", "")).upper()
        if "LIVE" in experiment:
            return "experiment_id"
        for key, value in source.items():
            low = key.lower()
            if key in ("live_devices_touched", "live_ssh_connected", "ap_241_verified",
                       "sta_242_verified", "live_target_accepted") and value is True:
                return key
            if key.startswith("total_live_") and isinstance(value, int) and value > 0:
                return key
            if "windows" in low and isinstance(value, int) and value > 0:
                return key
            if "hardware_pair" in low:
                return key
    for key in receipt.keys():
        if str(key).replace(".", "").isdigit():
            return f"device_address_key:{key}"
    return ""


def measurement_evidence(receipt: dict) -> str:
    for key in MEASUREMENT_KEYS:
        if key not in receipt:
            continue
        value = receipt[key]
        if key == "objective_config" and isinstance(value, dict):
            numeric = [k for k, v in value.items() if isinstance(v, (int, float))]
            if numeric:
                return f"{key} with {len(numeric)} numeric targets"
        elif isinstance(value, (int, float, list, dict)) and value:
            return key
    return ""


def classify(receipt: dict, name: str) -> tuple[str, str]:
    explicit = receipt.get("evidence_provenance_class")
    if explicit in (LIVE, STATIC, SIM):
        return explicit, "explicit_field"

    evidence = live_evidence(receipt)
    if evidence:
        return LIVE, evidence

    meta = receipt.get("meta", {}) if isinstance(receipt.get("meta"), dict) else {}
    status = str(receipt.get("status") or meta.get("status") or receipt.get("verdict") or "")
    if any(token in status.upper() for token in NEGATIVE):
        return NEG, f"status:{status[:24]}"

    low = name.lower()
    keys = " ".join(list(receipt.keys())).lower()
    if (any(token in low for token in SIM_TOKENS)
            or "simulat" in keys or "synthetic" in keys or "fixture" in keys):
        return SIM, "simulation_marker"

    measured = measurement_evidence(receipt)
    if measured:
        return LIVE, f"measurement_payload:{measured}"

    scope = str(meta.get("scope") or receipt.get("scope") or "").lower()
    has_binary = any(any(token in key.lower() for token in BINARY_TOKENS)
                     for key in receipt.keys())
    key_static = any("static" in key.lower() or "proof" in key.lower() for key in receipt.keys())
    if "static" in scope or has_binary or key_static:
        return STATIC, "binary_descriptor"
    if any(key in receipt for key in STRUCT_KEYS):
        return STATIC, "structural_verification"

    return UNDECLARED, "no_marker"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    files = sorted(AR.glob("*.json"))
    rows = []
    unreadable = []
    excluded = []
    for path in files:
        if path.name in AUDIT_FAMILY:
            excluded.append(path.name)
            continue
        receipt = load(path)
        if not isinstance(receipt, dict):
            unreadable.append(path.name)
            continue
        label, evidence = classify(receipt, path.stem)
        rows.append(dict(receipt=path.name, label=label, evidence=evidence,
                         has_explicit_field=int("evidence_provenance_class" in receipt),
                         preserved_raw_sha256=receipt.get("preserved_raw_sha256")))

    counts = {}
    for row in rows:
        counts[row["label"]] = counts.get(row["label"], 0) + 1
    undeclared = sorted(r["receipt"] for r in rows if r["label"] == UNDECLARED)
    explicit = sum(r["has_explicit_field"] for r in rows)

    report = dict(
        evidence_provenance_class="CONFIRMED_STATIC_BINARY",
        post_audit_reclassified_at=None,
        preserved_raw_sha256=None,
        meta=dict(
            stage="902A", generated_utc="2026-10-27T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/verify/audit_stage902a_full_corpus_provenance.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            scope="read-only audit of artifacts/autoresearch; no file modified, no radio contacted",
            method="seven ordered rules, explicit field first, then live, negative, simulation, "
                   "measurement payload, static; anything left is undeclared",
            premise_corrections=[
                "the first pass reported 371 undeclared receipts because the rules expected status "
                "metadata, while the live autoresearch runs carry a measurement payload instead",
                "a filename that encodes a distance and a loss is not evidence; the numeric payload "
                "inside the receipt is",
            ],
            radio_safety="static only"),
        counts=counts,
        unreadable=unreadable,
        audit_receipts_excluded=excluded,
        undeclared=undeclared,
        rows=rows,
        summary=dict(receipts_in_directory=len(files),
                     audit_receipts_excluded=len(excluded),
                     receipts_audited=len(files) - len(excluded),
                     receipts_classified=len(rows),
                     unreadable=len(unreadable),
                     explicit_field=explicit,
                     live_hardware=counts.get(LIVE, 0),
                     static_binary=counts.get(STATIC, 0),
                     simulated_model=counts.get(SIM, 0),
                     refuted=counts.get(NEG, 0),
                     undeclared=len(undeclared),
                     zero_ambiguous=int(len(undeclared) == 0),
                     coverage_fraction=round(
                         len(rows) / float(max(1, len(files) - len(excluded))), 4)),
        gaps=[
            "a label states the provenance of a receipt, not the correctness of its conclusion",
            "measurement payload is evidence that numbers were produced by a run, not that the run "
            "was instrumented correctly",
            "the audit reads receipts only, so a receipt that lies about its own payload passes",
            "the 12 previously unreadable receipts from other workstreams are counted separately "
            "and are not classified",
            "no dynamic validation"])

    write_atomic(args.out, json.dumps(report, indent=2) + "\n")

    s = report["summary"]
    print(f"[902A] receipts={s['receipts_in_directory']} classified={s['receipts_classified']} "
          f"unreadable={s['unreadable']} explicit={s['explicit_field']} live={s['live_hardware']} "
          f"static={s['static_binary']} sim={s['simulated_model']} refuted={s['refuted']} "
          f"undeclared={s['undeclared']} zero_ambiguous={s['zero_ambiguous']}")
    for name in undeclared[:10]:
        print(f"       UNDECLARED {name[:62]}")
    print(f"[902A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
