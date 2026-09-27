#!/usr/bin/env python3
"""
Autonomous Paper & Kernel Patch Scout for futuraMAX.
Token-Efficient research crawler for 802.11ac, ath10k, AQL, and bufferbloat literature.

Architecture:
- Level 0 (Deterministic): Queries arXiv API via HTTPS. Checks IDs against knowledge/known_papers.json.
  Cost: 0 tokens, 0 USD.
- Level 1 (PraisonAI Scout): Dispatched ONLY if an unanalyzed paper is discovered.
  Reads title & abstract, extracts relevance to QCA9880/ath10k-ct, suggests candidate FMX recipe,
  and logs telemetry to telemetry.db.
"""

import os
import sys
import json
import subprocess
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

# Ensure project tools are in path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
OBSERVABILITY_DIR = PROJECT_DIR / "tools" / "observability"
SENTINEL_COMMON_DIR = Path("G:/_OneDrive/OneDrive/Desktop/Py Apps/infra/scripts/sentinel_common")

if str(SENTINEL_COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(SENTINEL_COMMON_DIR))
if str(OBSERVABILITY_DIR) not in sys.path:
    sys.path.insert(0, str(OBSERVABILITY_DIR))

try:
    from base_scout import TokenEfficientScout
except ImportError:
    TokenEfficientScout = None

INDEX_FILE = PROJECT_DIR / "knowledge" / "known_papers.json"
INCOMING_FILE = PROJECT_DIR / "knowledge" / "INCOMING_PAPERS.md"

SEARCH_TERMS = [
    "all:ath10k",
    "all:\"airMAX\"",
    "all:\"CoTSQ\"",
    "all:\"Airtime Queue Limits\""
]

def load_known_ids() -> set:
    if not INDEX_FILE.exists():
        return set()
    try:
        data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        return set(data.get("known_ids", []))
    except Exception:
        return set()

def save_known_id(paper_id: str, title: str):
    data = {"known_ids": [], "papers": []}
    if INDEX_FILE.exists():
        try:
            data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    if paper_id not in data["known_ids"]:
        data["known_ids"].append(paper_id)
        data["papers"].append({
            "id": paper_id,
            "title": title,
            "indexed_at": datetime.now(timezone.utc).isoformat()
        })
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        INDEX_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def query_arxiv(search_query: str, max_results: int = 5) -> list[dict]:
    """Consulta arXiv API usando curl determinista (0 tokens)."""
    encoded_query = search_query.replace('"', '%22').replace(' ', '+')
    url = f"https://export.arxiv.org/api/query?search_query={encoded_query}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    
    try:
        proc = subprocess.run(["curl.exe", "-s", url], capture_output=True, text=True, timeout=15)
        if proc.returncode != 0:
            return []
        
        xml_data = proc.stdout
        if "<feed" not in xml_data:
            return []
            
        tree = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = tree.findall("atom:entry", ns)
        
        papers = []
        for entry in entries:
            id_tag = entry.find("atom:id", ns)
            title_tag = entry.find("atom:title", ns)
            summary_tag = entry.find("atom:summary", ns)
            published_tag = entry.find("atom:published", ns)
            
            p_id = id_tag.text.strip().split("/abs/")[-1] if id_tag is not None else ""
            p_title = " ".join(title_tag.text.split()) if title_tag is not None else ""
            p_summary = " ".join(summary_tag.text.split()) if summary_tag is not None else ""
            p_pub = published_tag.text.strip() if published_tag is not None else ""
            
            if p_id and p_title:
                papers.append({
                    "id": p_id,
                    "title": p_title,
                    "summary": p_summary,
                    "published": p_pub
                })
        return papers
    except Exception as e:
        print(f"[ERROR] Failed to query arXiv: {e}")
        return []

def run_scout(dry_run: bool = False, force_one: bool = False) -> int:
    print("=" * 60)
    print("futuraMAX Autonomous Research Scout (arXiv & Kernel)")
    print("=" * 60)
    
    known = load_known_ids()
    print(f"[INDEX] Loaded {len(known)} existing paper IDs from {INDEX_FILE.name}")
    
    new_papers = []
    # Nivel 0: Consulta determinista (0 tokens)
    for term in SEARCH_TERMS:
        print(f"Checking query: {term}...")
        found = query_arxiv(term, max_results=3)
        for p in found:
            if force_one and not new_papers:
                new_papers.append(p)
                break
            if p["id"] not in known and not any(x["id"] == p["id"] for x in new_papers):
                new_papers.append(p)
        if force_one and new_papers:
            break

    if not new_papers:
        print("[OK] No new unanalyzed papers found on arXiv.")
        print("[TOKEN ECONOMY] 0 tokens consumed. Cost: $0.000000 USD.")
        return 0

    print(f"\n[NEW DISCOVERIES] Found {len(new_papers)} candidate paper(s) to analyze!")
    for p in new_papers:
        print(f"  -> [{p['id']}] {p['title']} ({p['published'][:10]})")

    if dry_run:
        print("[DRY-RUN] Scout execution skipped by flag.")
        return 0

    if not TokenEfficientScout:
        print("[ERROR] TokenEfficientScout class not available.")
        return 1

    scout = TokenEfficientScout(
        agent_name="futuramax_literature_scout",
        project="futuraMAX",
        model="gemini/gemini-3.8-flash",
        max_budget=0.015
    )

    for p in new_papers:
        print(f"\nAnalyzing paper {p['id']} with PraisonAI Scout...")
        context = f"Title: {p['title']}\nPublished: {p['published']}\nAbstract: {p['summary']}"
        instructions = (
            "Evaluate relevance to futuraMAX: Ubiquiti airMAX AC PtMP replacement using OpenWrt & ath10k-ct on QCA9880. "
            "Focus on AQL queue limits, CoTSQ socket bounds, and collision avoidance in directional PtMP."
        )
        
        analysis = scout.analyze_incident(instructions=instructions, incident_data=context)
        print(f"Result for {p['id']}:")
        print(json.dumps(analysis, indent=2))
        
        # Guardar en known IDs
        save_known_id(p["id"], p["title"])
        
        # Registrar en INCOMING_PAPERS.md si tiene severidad o recomendación
        res = analysis.get("result", {})
        markdown_entry = f"""
### [{p['id']}] {p['title']}
- **Published**: {p['published']}
- **Scout Analysis**: {json.dumps(res, indent=2)}
- **Cost**: ${analysis.get('cost_usd', 0):.6f} | **Tokens**: In={analysis.get('tokens_in', 0)}, Out={analysis.get('tokens_out', 0)}
- **Indexed**: {datetime.now(timezone.utc).isoformat()}

---
"""
        with open(INCOMING_FILE, "a", encoding="utf-8") as f:
            f.write(markdown_entry)
        print(f"[SAVED] Appended review to {INCOMING_FILE.name}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="futuraMAX Paper Scout")
    parser.add_argument("--dry-run", action="store_true", help="Fetch arXiv papers without dispatching LLM Scout")
    parser.add_argument("--force-one", action="store_true", help="Force analysis of one paper for verification")
    args = parser.parse_args()
    
    sys.exit(run_scout(dry_run=args.dry_run, force_one=args.force_one))
