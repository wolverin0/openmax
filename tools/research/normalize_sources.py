#!/usr/bin/env python3
"""FuturaMAX R2: merge per-run link ledgers into research/normalized/sources.jsonl.

Covers: cross-run URL dedupe, source_type inference, primary-source flagging, and the
cross-model corroboration count (how many independent model runs cited the same URL).
Keywords: sources.jsonl, dedupe, canonical URL, source_type, primary_source, corroboration.
Read when: you need the deduplicated citation universe or want to know which sources
more than one model found independently. Corroboration is a DISCOVERY signal only -
per the handoff, repetition across models never establishes truth.
Verdict: GENERATED. Regenerate with tools/research/normalize_sources.py.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
EXTRACTED = ROOT / "research" / "extracted"
NORM = ROOT / "research" / "normalized"

# (regex on canonical url, source_type, primary_source, default evidence weight note)
TYPE_RULES: list[tuple[re.Pattern, str, bool]] = [
    (re.compile(r"^https?://(git\.kernel\.org|kernel\.org/pub|lore\.kernel\.org)"), "kernel_source_or_list", True),
    (re.compile(r"^https?://(www\.)?spinics\.net/lists|marc\.info|mailman|lists\.(infradead|openwrt|freebsd)\.org"), "mailing_list", True),
    (re.compile(r"^https?://(github|gitlab)\.com/.+/(commit|pull|tree|blob)/"), "source_code_commit", True),
    (re.compile(r"^https?://(github|gitlab)\.com/"), "source_code_repo", True),
    (re.compile(r"^https?://(git\.openwrt\.org|openwrt\.org|forum\.openwrt\.org|dev\.openwrt\.org)"), "openwrt_official_or_forum", True),
    (re.compile(r"^https?://patents\.google\.com|patentimages|espacenet|uspto\.gov|freepatentsonline"), "patent", True),
    (re.compile(r"^https?://(fcc|fccid)\.(gov|io)|fcc\.report|fccid\.io"), "fcc_filing", True),
    (re.compile(r"^https?://(arxiv\.org|doi\.org|dl\.acm\.org|ieeexplore\.ieee\.org|usenix\.org|link\.springer\.com|sciencedirect\.com|mdpi\.com|semanticscholar\.org|researchgate\.net|ncbi\.nlm\.nih\.gov)"), "academic_paper", True),
    (re.compile(r"^https?://(help\.u[ib]\.com|ui\.com|ubnt\.com|community\.u[ib]\.com|dl\.ubnt\.com|techspecs\.ui\.com)"), "vendor_ubiquiti", True),
    (re.compile(r"^https?://(www\.)?qualcomm\.com|qca|codeaurora"), "vendor_qualcomm", True),
    (re.compile(r"^https?://(wireless\.(docs\.)?kernel\.org|linuxwireless|wiki\.debian|man7\.org|docs\.kernel\.org)"), "official_docs", True),
    (re.compile(r"^https?://(www\.)?wikipedia\.org|[a-z]{2}\.wikipedia\.org"), "encyclopedia", False),
    (re.compile(r"^https?://(www\.)?(reddit|stackexchange|stackoverflow|serverfault|superuser)\.com"), "forum_qa", False),
    (re.compile(r"^https?://(forum|forums)\."), "forum_qa", False),
    (re.compile(r"^https?://(www\.)?youtube\.com|youtu\.be"), "video", False),
]


def infer_type(url: str) -> tuple[str, bool]:
    for rx, t, primary in TYPE_RULES:
        if rx.search(url):
            return t, primary
    return "web_page_unclassified", False


DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(v\d+)?", re.I)


def stable_id(url: str) -> str:
    return "S-" + hashlib.sha1(url.encode()).hexdigest()[:10]


def main() -> int:
    NORM.mkdir(parents=True, exist_ok=True)
    agg: dict[str, dict] = {}

    for lp in sorted(EXTRACTED.glob("*/*/links.jsonl")):
        for line in lp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("is_chrome_host"):
                continue
            url = rec["url_canonical"]
            src = agg.get(url)
            if src is None:
                stype, primary = infer_type(url)
                doi = DOI_RE.search(url)
                arx = ARXIV_RE.search(url)
                src = agg[url] = {
                    "source_id": stable_id(url),
                    "title": None,
                    "authors_or_org": None,
                    "source_type": stype,
                    "publication_date": None,
                    "accessed_at": None,
                    "url": url,
                    "host": rec["host"],
                    "doi_or_stable_id": (doi.group(0) if doi else (f"arXiv:{arx.group(1)}" if arx else None)),
                    "repository_commit_or_version": None,
                    "status_current_superseded_abandoned": "UNVERIFIED",
                    "primary_source": primary,
                    "raw_run_ids": [],
                    "providers": [],
                    "anchor_texts": [],
                    "total_occurrences": 0,
                    "evidence_grade": "UNGRADED",
                    "link_check": "PENDING",
                    "notes": "auto-extracted at R2; title/date/grade require R3 verification",
                }
            if rec["run_id"] not in src["raw_run_ids"]:
                src["raw_run_ids"].append(rec["run_id"])
            if rec["provider"] not in src["providers"]:
                src["providers"].append(rec["provider"])
            src["total_occurrences"] += rec.get("occurrences", 1)
            for at in rec.get("anchor_texts", []):
                if at and at not in src["anchor_texts"] and len(src["anchor_texts"]) < 8:
                    src["anchor_texts"].append(at)

    rows = sorted(agg.values(), key=lambda r: (-len(r["providers"]), r["source_type"], r["url"]))
    for r in rows:
        r["cross_model_corroboration"] = len(r["providers"])

    with (NORM / "sources.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    by_type = defaultdict(int)
    by_corr = defaultdict(int)
    for r in rows:
        by_type[r["source_type"]] += 1
        by_corr[r["cross_model_corroboration"]] += 1

    print(f"unique sources: {len(rows)}")
    print("\nby source_type:")
    for t, n in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {n:>4}  {t}")
    print("\nby number of independent model runs citing it:")
    for k in sorted(by_corr, reverse=True):
        print(f"  {by_corr[k]:>4} sources cited by {k} run(s)")
    print(f"\nprimary_source=True: {sum(1 for r in rows if r['primary_source'])}")
    print("\nmulti-model sources (>=3 runs):")
    for r in rows:
        if r["cross_model_corroboration"] >= 3:
            print(f"  [{r['cross_model_corroboration']}] {r['source_type']:<24} {r['url'][:95]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
