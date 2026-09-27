#!/usr/bin/env python3
"""
PraisonAI Multi-Topic Autonomous Investigator for openMAX / FuturaMAX.
Executes autonomous research runs across three critical architectural domains:
1. Topic A: Contextual Rate-Mask Bounding & ratemask-CT (Campaign C4 / FMX-0009)
2. Topic B: Spectral FFT Signatures & Interference Classification on QCA9880 (Campaign C1 / FMX-0010)
3. Topic C: Directional PtMP Contention & Uplink Collision Mitigation (Campaign C6/C8 / FMX-0016)
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import httpx

# Ensure working directory is openMAX root
FUTURAMAX_ROOT = Path(__file__).resolve().parent.parent.parent

# Clean local proxy env if present to allow direct OpenAI API calls
os.environ.pop("OPENAI_API_BASE", None)
os.environ.pop("OPENAI_BASE_URL", None)

from praisonaiagents import Agent, tool
from praisonaiagents.agent.agent import ExecutionConfig

ARXIV_API_URL = "https://export.arxiv.org/api/query"

@tool
def search_arxiv(query: str = None, max_results: int = 4, **kwargs) -> str:
    """Search arXiv for peer-reviewed preprints and research papers.
    Args:
        query: Search keywords
        max_results: Number of results to return (default 4)
    Returns:
        Structured string of matching papers with arXiv ID, title, authors, date, summary, and PDF link.
    """
    q = query or kwargs.get("search_query") or kwargs.get("q") or kwargs.get("keywords") or "802.11ac rate control"
    print(f"[TOOL CALL] search_arxiv: query='{q}', max_results={max_results}")
    params = {
        "search_query": f"all:{q}",
        "start": 0,
        "max_results": int(max_results),
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get(ARXIV_API_URL, params=params)
            resp.raise_for_status()
            raw_xml = resp.text

        root = ET.fromstring(raw_xml)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        if not entries:
            return f"No arXiv papers found for query: '{q}'"

        results = []
        for i, entry in enumerate(entries, 1):
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            published = entry.find("atom:published", ns).text.strip()[:10]
            entry_id = entry.find("atom:id", ns).text.strip()
            arxiv_id = entry_id.split("/")[-1]
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
            author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
            
            pdf_link = ""
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                    pdf_link = link.get("href", "")
            
            results.append(
                f"[{i}] arXiv:{arxiv_id} ({published})\n"
                f"Title: {title}\n"
                f"Authors: {author_str}\n"
                f"Abstract: {summary[:400]}...\n"
                f"PDF: {pdf_link}\n"
            )
        return "\n".join(results)
    except Exception as e:
        return f"Error querying arXiv: {e}"

@tool
def search_futura_seeds(keyword: str = None, **kwargs) -> str:
    """Search local openMAX architecture guides for known seeds and boundaries.
    Args:
        keyword: Topic or technical keyword
    Returns:
        Excerpts from researchplan.md and AGENTS.md matching the topic.
    """
    k = keyword or kwargs.get("topic") or kwargs.get("query") or "control"
    matches = []
    files_to_check = [
        FUTURAMAX_ROOT / "docs" / "QCA988X_CONTROL_BOUNDARY.md",
        FUTURAMAX_ROOT / "docs" / "DECISIONS.md",
        FUTURAMAX_ROOT / "AGENTS.md"
    ]
    keyword_lower = str(k).lower()
    for fpath in files_to_check:
        if not fpath.exists():
            continue
        try:
            content = fpath.read_text(encoding="utf-8")
            lines = content.splitlines()
            for idx, line in enumerate(lines):
                if keyword_lower in line.lower():
                    start = max(0, idx - 2)
                    end = min(len(lines), idx + 8)
                    snippet = "\n".join(lines[start:end])
                    matches.append(f"--- From {fpath.name} (line {start+1}) ---\n{snippet}")
                    if len(matches) >= 3:
                        break
        except Exception as e:
            matches.append(f"Error reading {fpath.name}: {e}")
        if len(matches) >= 4:
            break
            
    if not matches:
        return f"No local sections found for '{k}'."
    return "\n\n".join(matches)

@tool
def extract_spans_with_offsets(text_block: str = None, hypothesis: str = None, **kwargs) -> str:
    """Extract verifiable sentence-level spans with exact character offsets from a text or abstract."""
    text = text_block or kwargs.get("text") or kwargs.get("abstract") or ""
    hyp = hypothesis or kwargs.get("claim") or kwargs.get("concept") or ""
    
    sentences = re.split(r'(?<=[.!?])\s+', str(text).strip())
    words = [w.lower() for w in re.findall(r'\b\w+\b', str(hyp)) if len(w) > 3]
    
    findings = []
    for sent in sentences:
        if not sent.strip():
            continue
        sent_lower = sent.lower()
        matched_words = [w for w in words if w in sent_lower]
        score = len(matched_words) / max(len(words), 1)
        if score > 0.12 or any(k in sent_lower for k in ["rate", "spectral", "fft", "hidden", "contention", "rts", "cts", "mcs"]):
            start_pos = str(text).find(sent)
            end_pos = start_pos + len(sent) if start_pos != -1 else -1
            findings.append({
                "span": sent.strip(),
                "start_char": start_pos,
                "end_char": end_pos,
                "overlap_score": round(score, 3)
            })
            
    findings.sort(key=lambda x: x["overlap_score"], reverse=True)
    return json.dumps(findings[:3], indent=2)

@tool
def classify_research_claim(claim: str = None, evidence: str = None, **kwargs) -> str:
    """Classify a research claim into CONFIRMED, INFERRED, UNKNOWN, or REFUTED, with specific control boundary."""
    c = claim or kwargs.get("assertion") or "Claim"
    e = evidence or kwargs.get("evidence") or "Evidence"
    return (
        f"Claim Evaluation:\n"
        f"- Target Claim: {c}\n"
        f"- Evidence: {str(e)[:250]}...\n"
        f"- Epistemic Tiers: CONFIRMED | INFERRED | UNKNOWN | REFUTED\n"
        f"- Subsystem Boundary: LINUX KERNEL / MAC80211 / ATH10K DRIVER / QCA9880 FIRMWARE / GATEWAY SHAPER"
    )

@tool
def save_research_dossier(filename: str = None, report_markdown: str = None, **kwargs) -> str:
    """Save the completed research dossier to artifacts and research/extracted."""
    raw_fn = filename or kwargs.get("name") or "research_dossier.md"
    md = report_markdown or kwargs.get("content") or kwargs.get("markdown") or kwargs.get("report") or kwargs.get("text") or ""
    
    if raw_fn and len(raw_fn) > 100 and not md:
        md = raw_fn
        fn = "research_dossier.md"
    else:
        fn = raw_fn
        
    if not fn.endswith(".md"):
        fn += ".md"
        
    artifacts_dir = FUTURAMAX_ROOT / "artifacts"
    extracted_dir = FUTURAMAX_ROOT / "research" / "extracted"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    extracted_dir.mkdir(parents=True, exist_ok=True)
    
    path_art = artifacts_dir / fn
    path_ext = extracted_dir / fn
    
    path_art.write_text(str(md), encoding="utf-8")
    path_ext.write_text(str(md), encoding="utf-8")
    
    return f"Saved dossier ({len(str(md))} chars) to {path_art} and {path_ext}"


def run_topic_investigation(topic_id: str, topic_title: str, query_terms: list, prompt_text: str, filename: str):
    print(f"\n==================================================")
    print(f"  LAUNCHING TOPIC: {topic_title}")
    print(f"==================================================")
    
    agent = Agent(
        name=f"openMAX-{topic_id}",
        role="Principal Wireless Systems & Linux mac80211 Researcher",
        goal=f"Conduct deep literature search and epistemic classification for: {topic_title}",
        instructions=f"""
You are an autonomous research agent for openMAX (Ubiquiti airMAX AC / QCA9880 / ath10k).
Follow these exact steps:
1. Search local architecture seeds using `search_futura_seeds`.
2. Search arXiv using `search_arxiv` with terms: {query_terms}.
3. Extract exact sentence-level evidence spans using `extract_spans_with_offsets`.
4. Classify each finding with `classify_research_claim` into CONFIRMED, INFERRED, UNKNOWN, or REFUTED, specifying the exact subsystem (LINUX KERNEL, MAC80211, ATH10K DRIVER, QCA9880 FIRMWARE).
5. Synthesize a detailed Markdown dossier containing:
   - Executive Summary
   - Exact Technical Mechanisms & Claims
   - Epistemic Evaluation Table
   - Control Boundary Analysis (What is host-owned vs firmware-owned)
   - Concrete Proposed Experiments
6. Save the dossier using `save_research_dossier(filename='{filename}', report_markdown=...)`.
""",
        llm="gpt-4o-mini",
        tools=[
            search_arxiv,
            search_futura_seeds,
            extract_spans_with_offsets,
            classify_research_claim,
            save_research_dossier
        ],
        execution=ExecutionConfig(
            max_iter=15,
            max_tool_calls_per_turn=10
        )
    )

    result = agent.start(prompt_text)
    print(f"[+] Completed {topic_id}")
    return result

def main():
    topics = [
        {
            "id": "Topic1-RateMask",
            "title": "Contextual Rate-Mask Bounding & ratemask-CT (Campaign C4 / FMX-0009)",
            "query_terms": ["rate adaptation bandit 802.11", "rate mask Wi-Fi outdoor"],
            "prompt": "Investigate outer-loop contextual rate-mask bounding, multi-armed bandits, and ratemask-CT on 802.11ac outdoor stationary PtMP links. How can the host eliminate doomed high-order MCS probing without breaking on-chip rate microcode? Save dossier as praisonai_topic1_ratemask_dossier.md.",
            "file": "praisonai_topic1_ratemask_dossier.md"
        },
        {
            "id": "Topic2-SpectralFFT",
            "title": "Spectral FFT Signatures & Interference Classification on QCA9880 (Campaign C1 / FMX-0010)",
            "query_terms": ["ath10k spectral scan FFT", "Wi-Fi interference classification machine learning"],
            "prompt": "Investigate baseband FFT spectral scanning via ath10k RelayFS and machine learning classification of RF interference (DFS radar, adjacent channels, non-Wi-Fi emitters). How to capture and classify on QCA9880 without CPU lockup? Save dossier as praisonai_topic2_spectral_fft_dossier.md.",
            "file": "praisonai_topic2_spectral_fft_dossier.md"
        },
        {
            "id": "Topic3-DirectionalContention",
            "title": "Directional PtMP Contention & Uplink Collision Mitigation (Campaign C6/C8 / FMX-0016)",
            "query_terms": ["hidden terminal PtMP directional antenna", "RTS CTS 802.11ac outdoor contention"],
            "prompt": "Investigate directional PtMP uplink contention mitigation under high inter-CPE isolation (>110 dB). Quantify the tradeoffs between dynamic CCA, selective hardware RTS/CTS, and airtime-deficit scheduling. Save dossier as praisonai_topic3_directional_contention_dossier.md.",
            "file": "praisonai_topic3_directional_contention_dossier.md"
        }
    ]

    for t in topics:
        try:
            run_topic_investigation(
                topic_id=t["id"],
                topic_title=t["title"],
                query_terms=t["query_terms"],
                prompt_text=t["prompt"],
                filename=t["file"]
            )
        except Exception as e:
            print(f"[!] Error running {t['id']}: {e}")

if __name__ == "__main__":
    main()
