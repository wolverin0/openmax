#!/usr/bin/env python3
"""Inventory every docs Markdown file; enforce the active router contract."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = "artifacts/autoresearch/stage263a_docs_budget_audit_receipt.json"
ROUTERS = {"docs/CURRENT_STATE.md", "docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md",
           "docs/DECISIONS.md", "docs/RESEARCH_LEDGER.md", "docs/BENCH_PLAN.md"}


def inspect_markdown(data: bytes) -> dict:
    text = data.decode("utf-8-sig")
    lines = text.splitlines()
    openings = [i + 1 for i, line in enumerate(lines) if re.search(r"<!--\s*doc-head\b", line)]
    closings = [i + 1 for i, line in enumerate(lines) if re.search(r"<!--\s*/doc-head\s*-->", line)]
    errors = []
    if len(lines) >= 220:
        errors.append("line_budget_requires_less_than_220")
    if openings != [1] or not lines or not re.fullmatch(r"<!-- doc-head: [^<>]+ -->", lines[0]):
        errors.append("requires_single_doc_head_at_line_1")
    if (len(closings) != 1 or not openings or not 1 < closings[0] <= 8
            or not re.fullmatch(r"<!-- /doc-head -->", lines[closings[0]-1])):
        errors.append("requires_paired_header_with_at_most_six_summary_lines")
    return {"lines": len(lines), "doc_head_lines": openings, "closing_lines": closings,
            "errors": errors, "compliant": not errors}


def active_routers(root: Path) -> set[str]:
    active = set(ROUTERS)
    agents = root / "AGENTS.md"
    if agents.exists():
        for target in re.findall(r"\]\((docs/[^)]+\.md)(?:#[^)]*)?\)", agents.read_text(encoding="utf-8-sig")):
            active.add(target)
    return active


def audit(root: Path = ROOT) -> dict:
    root = root.resolve()
    active = active_routers(root)
    records = []
    for path in sorted((root / "docs").rglob("*")):
        if path.suffix.lower() != ".md" or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        row = {"path": rel, "active_router": rel in active}
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(root / "docs"):
                raise ValueError("symlink_or_external_path")
            data = path.read_bytes()
            row.update(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
            row.update(inspect_markdown(data))
        except (OSError, UnicodeError, ValueError) as exc:
            row.update(compliant=False, errors=[str(exc)])
        records.append(row)
    missing = sorted(active - {row["path"] for row in records})
    failures = [row["path"] for row in records if row["active_router"] and not row["compliant"]]
    return {"stage": "263A", "task_id": "T-S263A-DOCS-AUDIT", "static_sources": records,
            "scope": "All docs/**/*.md inventoried; AGENTS-linked routers plus five continuity docs enforced",
            "active_router_paths": sorted(active), "missing_active_routers": missing,
            "summary": {"scanned": len(records), "active": sum(r["active_router"] for r in records),
                        "all_docs_noncompliant": sum(not r["compliant"] for r in records),
                        "active_failures": failures},
            "compliant": not failures and not missing,
            "boundary": {"local_read_only": True, "documents_rewritten": False,
                         "hardware_access": False, "historical_docs_not_exempt_from_inventory": True}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = audit(args.root)
    output = args.output or args.root / RECEIPT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"compliant": result["compliant"], **result["summary"]}))
    return 0 if result["compliant"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
