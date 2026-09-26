#!/usr/bin/env python3
"""FuturaMAX R3: liveness/reachability check for every URL in sources.jsonl.

Covers: HTTP HEAD/GET probing, redirect capture, HTML <title> harvest, and a verdict
of OK / REDIRECT / NOT_FOUND / BLOCKED / ERROR per source. Keywords: link check, 404,
citation hardening, hallucinated URL detection, title harvest, robots-blocked.
Read when: you need to know whether a model-supplied citation actually resolves, or
which citations are dead or invented. A 200 proves the URL EXISTS - it does NOT prove
the source says what the model claimed. That check is manual and belongs to R3 proper.
Verdict: GENERATED. Re-run to refresh; results are timestamped per row.
"""
from __future__ import annotations

import json
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NORM = ROOT / "research" / "normalized"
OUT = NORM / "link_check.jsonl"

UA = "Mozilla/5.0 (compatible; FuturaMAX-research-citation-checker/1.0; +local research audit)"
TIMEOUT = 20
WORKERS = 8

TITLE_RE = re.compile(rb"<title[^>]*>(.{0,400}?)</title>", re.I | re.S)
_print_lock = threading.Lock()


def fetch(url: str) -> dict:
    rec = {
        "url": url,
        "status": None,
        "verdict": "ERROR",
        "final_url": None,
        "title": None,
        "content_type": None,
        "error": None,
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            rec["status"] = resp.status
            rec["final_url"] = resp.geturl()
            rec["content_type"] = resp.headers.get("Content-Type")
            body = resp.read(200_000)
            m = TITLE_RE.search(body)
            if m:
                t = m.group(1).decode("utf-8", errors="replace")
                rec["title"] = " ".join(re.sub(r"<[^>]+>", " ", t).split())[:300]
            rec["verdict"] = "REDIRECT" if rec["final_url"].rstrip("/") != url.rstrip("/") else "OK"
    except urllib.error.HTTPError as e:
        rec["status"] = e.code
        rec["error"] = str(e.reason)[:200]
        if e.code == 404:
            rec["verdict"] = "NOT_FOUND"
        elif e.code in (401, 403, 429, 503):
            rec["verdict"] = "BLOCKED"
        else:
            rec["verdict"] = "HTTP_ERROR"
    except Exception as e:  # noqa: BLE001 - network probing, any failure is data
        rec["error"] = f"{type(e).__name__}: {e}"[:200]
        rec["verdict"] = "ERROR"
    return rec


def main() -> int:
    src = NORM / "sources.jsonl"
    if not src.is_file():
        print("FATAL: run normalize_sources.py first", file=sys.stderr)
        return 1
    rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    urls = [r["url"] for r in rows]

    done = {}
    if OUT.is_file() and "--refresh" not in sys.argv:
        for l in OUT.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                done[r["url"]] = r
    todo = [u for u in urls if u not in done]
    print(f"{len(urls)} sources, {len(done)} already checked, {len(todo)} to check")

    results = list(done.values())
    counter = [0]

    def work(u: str) -> dict:
        r = fetch(u)
        with _print_lock:
            counter[0] += 1
            if counter[0] % 25 == 0:
                print(f"  ...{counter[0]}/{len(todo)}", flush=True)
        time.sleep(0.05)
        return r

    if todo:
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            results.extend(ex.map(work, todo))

    by_url = {r["url"]: r for r in results}
    with OUT.open("w", encoding="utf-8") as fh:
        for u in urls:
            if u in by_url:
                fh.write(json.dumps(by_url[u], ensure_ascii=False) + "\n")

    from collections import Counter

    c = Counter(by_url[u]["verdict"] for u in urls if u in by_url)
    print("\nverdicts:")
    for k, n in c.most_common():
        print(f"  {n:>4}  {k}")

    dead = [by_url[u] for u in urls if u in by_url and by_url[u]["verdict"] in ("NOT_FOUND",)]
    if dead:
        print(f"\nNOT_FOUND ({len(dead)}) - candidate hallucinated or moved citations:")
        for d in dead:
            print(f"  {d['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
