#!/usr/bin/env python3
"""Prepared Stage235 receipt audit; regression execution awaits queue resumption."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import re
import signal
import stat
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

TASK_ID = "T-S235A-SAFE-LOCAL-FULL-OPENMAX-RELEASE-REGRESSION"
DEFAULT_OUTPUT = ROOT / "artifacts/verification/stage235a_full_release_regression"
DEFAULT_RECEIPT = ROOT / "artifacts/autoresearch/stage235a_full_release_regression_receipt.json"
MAX_JSON_BYTES = 64 * 1024 * 1024
# Candidate explicit list: the execution entry point is deliberately disabled.
# Final pipeline/preflight files and adapted historical tests still need review.
SUITES = (
    ("release-pipeline-236", ("WA", "XC", "XW", "XM"), "tests/test_stage231a_to_236a_release_pipeline.py"),
    ("user-board-preflight-232", ("WA", "XC", "XW", "XM"), "tests/test_preflight_validate_user_board_info.py"),
    ("public-releases-172", ("WA", "XC", "XW", "XM"), "tests/test_stage170a_to_172a_public_releases.py"),
    ("tester-documents-196", ("WA",), "tests/test_stage194a_to_196a_docs_and_reddit_sync.py"),
    ("saved-wa-v3-144", ("WA",), "tests/test_stage144a_public_wa_4board_release_v3.py"),
    ("saved-wa-two-board-132", ("WA",), "tests/test_stage132a_public_lbe5ac_pbe5ac_release.py"),
    ("saved-ltu-champion-41", ("LTU",), "tests/test_stage41b_champion_v15_and_ltu_verifier.py"),
    ("saved-ltu-link-42", ("LTU",), "tests/test_stage42b_stage47b_ltu_ota_verifier.py"),
    ("saved-ltu-triple-play-48", ("LTU",), "tests/test_stage48b_ltu_ota_triple_play_verifier.py"),
    ("saved-ltu-hybrid-maxbd-50", ("LTU",), "tests/test_stage50b_ltu_hybrid_swq_and_maxbd_verifier.py"),
)
STAGE_FILENAME = re.compile(r"^stage(\d+)[a-z]?(?:[_-].*)?\.json$", re.I)


class RegressionError(ValueError):
    """Malformed evidence, unsafe path or invalid local invocation."""


def safe_local(path):
    text = os.fspath(path)
    windows = PureWindowsPath(text)
    if text.replace("\\", "/").startswith("//") or "://" in text or (windows.drive and not windows.root):
        raise RegressionError("LOCAL_PATH_REQUIRED")
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    for part in windows.parts[1:] if windows.anchor else windows.parts:
        if part == ".." or ":" in part or part.rstrip(". ").split(".")[0].upper() in reserved:
            raise RegressionError("DEVICE_STREAM_OR_TRAVERSAL_PATH_FORBIDDEN")
    result = Path(os.path.abspath(text))
    cursor = Path(result.anchor)
    for part in result.parts[1:]:
        cursor /= part
        try:
            info = cursor.lstat()
        except FileNotFoundError:
            break
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise RegressionError("SYMLINK_OR_REPARSE_PATH_FORBIDDEN")
    return result


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RegressionError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def strict_json(data):
    try:
        parsed = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_pairs,
                            parse_constant=lambda _: (_ for _ in ()).throw(RegressionError("NONFINITE_JSON")))
        json.dumps(parsed, allow_nan=False, ensure_ascii=True)
    except (UnicodeError, ValueError, OverflowError, RecursionError) as error:
        raise RegressionError("STRICT_FINITE_JSON_REQUIRED: " + str(error)) from error
    if not isinstance(parsed, dict):
        raise RegressionError("JSON_OBJECT_REQUIRED")
    return parsed


def _read(path, maximum=MAX_JSON_BYTES):
    with safe_local(path).open("rb") as handle:
        data = handle.read(maximum + 1)
    if len(data) > maximum:
        raise RegressionError("FILE_EXCEEDS_DOCUMENTED_READ_BOUND")
    return data


def _stage_number(value):
    if type(value) is int:
        return value
    if isinstance(value, str):
        match = re.fullmatch(r"\s*(?:Stage\s*)?(\d+)[a-z]?\s*", value, re.I)
        return int(match.group(1)) if match else None
    return None


def _receipt_class(name, document):
    if any(key in document for key in ("command", "exit_code", "sha256_before", "stdout")) or re.search(r"test_run|pytest|execution", name, re.I):
        return "auxiliary_test_or_execution_log"
    if re.search(r"review|audit|readback|repro|freeze", name, re.I):
        return "auxiliary_report_or_snapshot"
    return "research_receipt_or_stage_artifact"


def _receipt_paths(root, minimum, maximum):
    found, errors, nonmatching = [], [], 0
    for relative in ("artifacts/autoresearch", "artifacts/verification"):
        try:
            directory = safe_local(root / relative)
            if not directory.exists():
                errors.append({"path": relative, "error": "MISSING_AUDIT_DIRECTORY"})
                continue
            pending = [directory]
            while pending:
                parent = pending.pop()
                with os.scandir(parent) as entries:
                    for entry in entries:
                        info = entry.stat(follow_symlinks=False)
                        path = Path(entry.path)
                        rel = path.relative_to(root).as_posix()
                        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                            errors.append({"path": rel, "error": "LINK_OR_REPARSE_NOT_FOLLOWED"})
                            continue
                        if stat.S_ISDIR(info.st_mode):
                            pending.append(path)
                        elif stat.S_ISREG(info.st_mode) and path.suffix.lower() == ".json":
                            match = STAGE_FILENAME.fullmatch(path.name)
                            if match and minimum <= int(match.group(1)) <= maximum:
                                found.append((path, int(match.group(1))))
                            else:
                                nonmatching += 1
        except OSError as error:
            errors.append({"path": relative, "error": type(error).__name__ + ": " + str(error)})
        except RegressionError as error:
            errors.append({"path": relative, "error": str(error)})
    return sorted(found), errors, nonmatching


def audit_receipts(root=ROOT, min_stage=100, max_stage=233):
    """Run the existing structural gate per discovered stage JSON, without edits.

    Discovery is recursive only in the two artifact roots. Auxiliary logs are
    classified and retained in every overall count; schema is never research truth.
    """
    if type(min_stage) is not int or type(max_stage) is not int or not 0 <= min_stage <= max_stage <= 10000:
        raise RegressionError("BOUNDED_INTEGER_STAGE_RANGE_REQUIRED")
    root = safe_local(root)
    paths, discovery_errors, nonmatching = _receipt_paths(root, min_stage, max_stage)
    rows = []
    for path, filename_stage in paths:
        row = {"path": path.relative_to(root).as_posix(), "filename_stage": filename_stage,
               "sha256": None, "bytes": None, "parse_status": "BLOCKED", "gate": None,
               "classification": "unparsed_stage_json", "errors": []}
        try:
            data = _read(path)
            row.update({"sha256": sha256(data), "bytes": len(data)})
            document = strict_json(data)
            row["parse_status"] = "PARSED"
            row["classification"] = _receipt_class(path.name, document)
            declared_stage = _stage_number(document.get("stage"))
            row["declared_stage"] = declared_stage
            if declared_stage is not None and declared_stage != filename_stage:
                row["errors"].append("FILENAME_AND_DECLARED_STAGE_DIFFER")
            if "stage" in document and type(document["stage"]) not in (str, int):
                row["errors"].append("STAGE_FIELD_NOT_SCALAR")
            row["gate"] = audit_stage_receipt_5pillars(document)
        except (RegressionError, OSError) as error:
            row["errors"].append(type(error).__name__ + ": " + str(error))
        row["structurally_compliant"] = row["parse_status"] == "PARSED" and not row["errors"] and bool(row["gate"] and row["gate"]["compliant"])
        rows.append(row)
    seen = sorted({number for _, number in paths})
    missing = sorted(set(range(min_stage, max_stage + 1)) - set(seen))
    compliant = sum(row["structurally_compliant"] for row in rows)
    classes = {}
    for row in rows:
        category = row["classification"]
        counts = classes.setdefault(category, {"matched": 0, "compliant": 0, "noncompliant": 0})
        counts["matched"] += 1
        counts["compliant" if row["structurally_compliant"] else "noncompliant"] += 1
    discovered_ok = bool(rows) and compliant == len(rows) and not discovery_errors
    return {"audit_kind": "PER_RECEIPT_EXISTING_FIVE_PILLAR_STRUCTURAL_GATE", "structural_only": True,
            "research_truth_verified": False, "historical_receipts_modified": False,
            "scope": {"roots": ["artifacts/autoresearch", "artifacts/verification"], "recursive": True,
                      "filename_rule": STAGE_FILENAME.pattern, "auxiliary_receipts_included": True,
                      "max_json_bytes": MAX_JSON_BYTES, "nonmatching_json_not_audited": nonmatching},
            "range": {"min_stage": min_stage, "max_stage": max_stage},
            "counts": {"matched": len(rows), "parsed": sum(row["parse_status"] == "PARSED" for row in rows),
                       "invalid": sum(row["parse_status"] != "PARSED" for row in rows), "compliant": compliant,
                       "noncompliant": len(rows) - compliant, "by_classification": classes},
            "coverage": {"present_stage_numbers": seen, "missing_stage_numbers": missing,
                         "full_range_covered": not missing, "numbers_are_not_invented_receipts": True},
            "all_discovered_receipts_structurally_compliant": discovered_ok,
            "full_range_structurally_compliant": discovered_ok and not missing,
            "status": "STRUCTURAL_ONLY_PASS" if discovered_ok and not missing else "BLOCKED_STRUCTURAL_OR_COVERAGE_GAPS",
            "discovery_errors": discovery_errors, "receipts": rows,
            "qualification": "Gate presence is neither source authenticity nor physical, scholarly, statistical, deployment or MemoryMaster acceptance."}


if __name__ == "__main__":
    print("Stage235 execution is not wired yet; no regression or catalogue run was performed.", file=sys.stderr)
    raise SystemExit(2)
