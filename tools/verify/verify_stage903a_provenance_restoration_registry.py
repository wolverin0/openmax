#!/usr/bin/env python3
"""Stage 903A — restoration registry for the remediated receipts.

Stage 901A claims a specific property: the four inserted fields can be removed and the file re-hashes
to the digest it had before remediation. This stage **verifies that claim independently**, file by file,
using only the file and the digest stored inside it.

It also registers, for each of the 31, the class, the citation and the basis, so the determination is
auditable without re-reading the receipt body.

Radio safety: read-only verification. No file is modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AR = REPO_ROOT / "artifacts" / "autoresearch"
OUT = AR / "stage903a_provenance_restoration_registry.json"
REMEDIATION = AR / "stage901a_provenance_remediation_receipt.json"

CLASSES = ("CONFIRMED_LIVE_HARDWARE", "CONFIRMED_STATIC_BINARY", "SIMULATED_MODEL_ONLY")
END_TOKEN = b'"post_audit_remediation_source": "stage901a",'


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def strip_block(raw: bytes) -> bytes:
    start = raw.find(b'\n  "evidence_provenance_class":')
    if start < 0:
        return raw
    end = raw.find(END_TOKEN, start)
    if end < 0:
        return raw
    return raw[:start] + raw[end + len(END_TOKEN):]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    remediation = json.loads(REMEDIATION.read_text(encoding="utf-8-sig"))
    entries = []
    for row in remediation.get("rows", []):
        name = row["receipt"]
        path = AR / name
        record = dict(receipt=name, citation=row.get("citation"),
                      provenance_basis=row.get("provenance_basis"),
                      expected_class=row.get("evidence_provenance_class"))
        if not path.exists():
            record["status"] = "absent"
            entries.append(record)
            continue
        raw = path.read_bytes()
        try:
            receipt = json.loads(raw.decode("utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            record["status"] = "unreadable"
            entries.append(record)
            continue

        preserved = receipt.get("preserved_raw_sha256", "")
        observed = receipt.get("evidence_provenance_class")
        recomputed = hashlib.sha256(strip_block(raw)).hexdigest()
        record.update(
            observed_class=observed,
            class_valid=int(observed in CLASSES),
            preserved_present=int(bool(preserved)),
            recomputed_original_sha256=recomputed,
            restoration_verified=int(bool(preserved) and recomputed == preserved),
            inserted_field_count=sum(1 for key in
                                     ("evidence_provenance_class", "post_audit_reclassified_at",
                                      "preserved_raw_sha256", "post_audit_remediation_source")
                                     if key in receipt),
            status="verified")
        entries.append(record)

    total = len(entries)
    verified = sum(1 for e in entries if e.get("status") == "verified")
    restored = sum(1 for e in entries if e.get("restoration_verified") == 1)
    valid = sum(1 for e in entries if e.get("class_valid") == 1)
    counts = {}
    for entry in entries:
        label = entry.get("observed_class")
        if label in CLASSES:
            counts[label] = counts.get(label, 0) + 1

    report = dict(
        evidence_provenance_class="CONFIRMED_STATIC_BINARY",
        post_audit_reclassified_at=None,
        preserved_raw_sha256=None,
        meta=dict(
            stage="903A", generated_utc="2026-10-27T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/verify/verify_stage903a_provenance_restoration_registry.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            scope="read-only verification of the receipts remediated by Stage 901A",
            method="independent re-derivation: remove the inserted span, hash the remainder, "
                   "compare with the digest stored inside the file",
            premise_corrections=[
                "restoration is verified from the file alone, not from the Stage 901A receipt, so "
                "the claim survives the loss of every other artefact",
                "a class is valid only if it is one of the three declared labels",
            ],
            radio_safety="static only"),
        classes=list(CLASSES),
        registry=entries,
        counts=counts,
        summary=dict(receipts=total,
                     verified=verified,
                     restoration_verified=restored,
                     class_valid=valid,
                     live_hardware=counts.get("CONFIRMED_LIVE_HARDWARE", 0),
                     static_binary=counts.get("CONFIRMED_STATIC_BINARY", 0),
                     simulated_model=counts.get("SIMULATED_MODEL_ONLY", 0),
                     all_restored=int(restored == total == 31),
                     all_classes_valid=int(valid == total == 31)),
        gaps=[
            "restoration proves the original bytes are recoverable, not that the file was correct "
            "before remediation",
            "the registry covers exactly the 31 receipts Stage 895A flagged",
            "a future edit to one of these receipts would invalidate its restoration record",
            "no receipt was re-executed",
            "no dynamic validation"])

    write_atomic(args.out, json.dumps(report, indent=2) + "\n")

    s = report["summary"]
    print(f"[903A] receipts={s['receipts']} verified={s['verified']} "
          f"restored={s['restoration_verified']} class_valid={s['class_valid']} "
          f"live={s['live_hardware']} static={s['static_binary']} sim={s['simulated_model']} "
          f"all_restored={s['all_restored']}")
    for entry in entries:
        if entry.get("restoration_verified") != 1 or entry.get("class_valid") != 1:
            print(f"       FAIL {entry.get('status')} {entry['receipt'][:56]}")
    print(f"[903A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
