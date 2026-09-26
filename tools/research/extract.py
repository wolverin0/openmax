#!/usr/bin/env python3
"""FuturaMAX R1/R2 extraction: raw report -> readable markdown + a link ledger.

Covers: HTML saved-chat-page, PDF and Markdown extraction into research/extracted/,
plus per-run links.jsonl holding every outbound URL with its anchor text and position.
Keywords: extraction, html2text, pymupdf, link ledger, canonical URL, chat chrome.
Read when: you need the text of an external Deep Research report, or its raw citation
list, without re-parsing 1 MB of browser-saved HTML. Never edits research/raw/.
Verdict: CURRENT. Deterministic and re-runnable; output is GENERATED, not evidence.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "research" / "intake" / "manifest.json"
OUT = ROOT / "research" / "extracted"

DROP_TAGS = ["script", "style", "svg", "button", "noscript", "iframe", "canvas", "textarea", "form"]

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "ref_src", "fbclid", "gclid", "mc_cid", "mc_eid", "s", "spm",
}

# Hosts that are UI chrome / the provider's own product, not research citations.
CHROME_HOST_PAT = re.compile(
    r"(^|\.)(z\.ai|chat\.z\.ai|grok\.com|x\.ai|x\.com|mistral\.ai|chat\.mistral\.ai|"
    r"openai\.com|chatgpt\.com|google\.com/intl|apps\.apple\.com|play\.google\.com)$",
    re.I,
)


def canonical_url(u: str) -> str:
    try:
        sp = urlsplit(u.strip())
    except ValueError:
        return u.strip()
    if sp.scheme not in ("http", "https"):
        return u.strip()
    host = sp.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    q = [(k, v) for k, v in parse_qsl(sp.query, keep_blank_values=True) if k.lower() not in TRACKING_PARAMS]
    path = sp.path.rstrip("/") or "/"
    return urlunsplit((sp.scheme, host, path, urlencode(q), ""))


def html_to_md(raw_bytes: bytes) -> tuple[str, list[dict]]:
    from bs4 import BeautifulSoup
    import html2text

    soup = BeautifulSoup(raw_bytes.decode("utf-8", errors="replace"), "html.parser")
    for t in soup(DROP_TAGS):
        t.decompose()

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href.startswith(("http://", "https://")):
            continue
        links.append({"url_raw": href, "anchor_text": " ".join(a.get_text(" ").split())[:300]})

    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_images = True
    h.ignore_emphasis = False
    h.protect_links = True
    h.single_line_break = False
    md = h.handle(str(soup))
    return md, links


def pdf_to_md(path: Path) -> tuple[str, list[dict]]:
    import fitz  # pymupdf

    doc = fitz.open(path)
    parts, links = [], []
    for i, page in enumerate(doc, 1):
        parts.append(f"\n\n<!-- page {i} -->\n")
        parts.append(page.get_text("text"))
        for lk in page.get_links():
            uri = lk.get("uri")
            if uri and uri.startswith(("http://", "https://")):
                rect = lk.get("from")
                anchor = ""
                if rect is not None:
                    anchor = " ".join(page.get_textbox(rect).split())[:300]
                links.append({"url_raw": uri, "anchor_text": anchor, "page": i})
    doc.close()
    return "".join(parts), links


URL_RE = re.compile(r"https?://[^\s<>\)\]\"'`]+")
MD_LINK_RE = re.compile(r"\[([^\]]{0,300})\]\((https?://[^\s\)]+)\)")


def md_links(text: str) -> list[dict]:
    out = []
    seen_spans = set()
    for m in MD_LINK_RE.finditer(text):
        out.append({"url_raw": m.group(2), "anchor_text": " ".join(m.group(1).split())})
        seen_spans.add(m.span(2))
    for m in URL_RE.finditer(text):
        if m.span() in seen_spans:
            continue
        out.append({"url_raw": m.group(0).rstrip(".,;:"), "anchor_text": ""})
    return out


def main() -> int:
    if not MANIFEST.is_file():
        print("FATAL: run tools/research/intake.py first", file=sys.stderr)
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    summary = []
    for run in manifest["runs"]:
        src = ROOT / run["primary_raw_path"]
        run_id = run["run_id"]
        dest = OUT / run["provider"] / run_id
        dest.mkdir(parents=True, exist_ok=True)

        suffix = src.suffix.lower()
        if suffix in (".html", ".htm"):
            md, links = html_to_md(src.read_bytes())
            links += [l for l in md_links(md) if l["url_raw"] not in {x["url_raw"] for x in links}]
        elif suffix == ".pdf":
            md, links = pdf_to_md(src)
            links += [l for l in md_links(md) if l["url_raw"] not in {x["url_raw"] for x in links}]
        else:
            md = src.read_text(encoding="utf-8", errors="replace")
            links = md_links(md)

        md = re.sub(r"\n{4,}", "\n\n\n", md)
        (dest / "report.md").write_text(md, encoding="utf-8")

        # Canonicalize + dedupe links, keep first anchor text seen and an occurrence count.
        agg: dict[str, dict] = {}
        for l in links:
            cu = canonical_url(l["url_raw"])
            host = urlsplit(cu).netloc
            rec = agg.setdefault(
                cu,
                {
                    "run_id": run_id,
                    "provider": run["provider"],
                    "url_canonical": cu,
                    "host": host,
                    "anchor_texts": [],
                    "occurrences": 0,
                    "is_chrome_host": bool(CHROME_HOST_PAT.search(host)),
                },
            )
            rec["occurrences"] += 1
            at = l.get("anchor_text", "")
            if at and at not in rec["anchor_texts"]:
                rec["anchor_texts"].append(at[:300])

        with (dest / "links.jsonl").open("w", encoding="utf-8") as fh:
            for cu in sorted(agg):
                fh.write(json.dumps(agg[cu], ensure_ascii=False) + "\n")

        cited = [v for v in agg.values() if not v["is_chrome_host"]]
        summary.append(
            {
                "run_id": run_id,
                "chars": len(md),
                "links_total": len(agg),
                "links_cited": len(cited),
                "hosts_cited": len({v["host"] for v in cited}),
            }
        )

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "extraction_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"{'run_id':<20}{'chars':>9}{'links':>8}{'cited':>8}{'hosts':>7}")
    for s in summary:
        print(f"{s['run_id']:<20}{s['chars']:>9}{s['links_total']:>8}{s['links_cited']:>8}{s['hosts_cited']:>7}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
