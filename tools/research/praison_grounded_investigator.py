#!/usr/bin/env python3
"""
PraisonAI Grounded Multi-Agent Investigator for openMAX / FuturaMAX.
Architectured with hard silicon grounding, C-source code verification tools,
and an adversarial Gatekeeper to eliminate hallucinations.
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import httpx

FUTURAMAX_ROOT = Path(__file__).resolve().parent.parent.parent
SRCCACHE_DIR = FUTURAMAX_ROOT / "tools" / "research" / "srccache"

# Clean proxy env
os.environ.pop("OPENAI_API_BASE", None)
os.environ.pop("OPENAI_BASE_URL", None)

from praisonaiagents import Agent, PraisonAIAgents, Task, tool
from praisonaiagents.agent.agent import ExecutionConfig

ARXIV_API_URL = "https://export.arxiv.org/api/query"

# ============================================================================
# REAL GROUNDED TOOLS
# ============================================================================

@tool
def search_arxiv(query: str = None, max_results: int = 3, **kwargs) -> str:
    """Search arXiv for preprints.
    Args:
        query: Search keywords
        max_results: Max papers to return
    """
    q = query or kwargs.get("search_query") or kwargs.get("q") or "802.11 rate control"
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
            return f"No papers found for: '{q}'"

        results = []
        for i, entry in enumerate(entries, 1):
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            published = entry.find("atom:published", ns).text.strip()[:10]
            entry_id = entry.find("atom:id", ns).text.strip().split("/")[-1]
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
            author_str = ", ".join(authors[:2]) + (" et al." if len(authors) > 2 else "")
            results.append(f"[{i}] arXiv:{entry_id} ({published}) | {title} by {author_str}\nAbstract: {summary[:350]}...\n")
        return "\n".join(results)
    except Exception as e:
        return f"Error: {e}"

@tool
def grep_driver_source(pattern: str, repo: str = "ath10k-ct") -> str:
    """Search the actual Linux kernel or ath10k-ct C source code in the repository.
    Args:
        pattern: The C symbol, function, variable, or struct to search for (e.g. 'bitrate_mask', 'ratemask-CT', 'WMI_10_4')
        repo: 'ath10k-ct' or 'linux'
    Returns:
        Exact matching file paths and line numbers with surrounding code.
    """
    target_dir = SRCCACHE_DIR / repo
    if not target_dir.exists():
        return f"Error: {target_dir} not found."
    
    matches = []
    regex = re.compile(re.escape(pattern), re.IGNORECASE)
    
    for fpath in target_dir.rglob("*.[ch]"):
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                for line_no, line in enumerate(f, 1):
                    if regex.search(line):
                        rel_path = fpath.relative_to(FUTURAMAX_ROOT)
                        matches.append(f"{rel_path}:{line_no}: {line.strip()}")
                        if len(matches) >= 10:
                            break
        except Exception:
            continue
        if len(matches) >= 10:
            break
            
    if not matches:
        return f"No matches found for '{pattern}' in {repo} source tree."
    return "\n".join(matches)

@tool
def read_c_source_lines(filepath: str, start_line: int = 1, num_lines: int = 25) -> str:
    """Read a block of code from a specific C source file in the codebase.
    Args:
        filepath: Relative or absolute path to the C file (e.g. 'tools/research/srccache/ath10k-ct/ath10k/mac.c')
        start_line: Starting line number (1-indexed)
        num_lines: Number of lines to read (max 50)
    Returns:
        Code lines with numbers.
    """
    p = Path(filepath)
    if not p.is_absolute():
        p = FUTURAMAX_ROOT / p
    if not p.exists():
        return f"Error: File {filepath} does not exist."
        
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            
        start_idx = max(0, int(start_line) - 1)
        end_idx = min(len(lines), start_idx + min(int(num_lines), 50))
        output = [f"{i+1}: {lines[i].rstrip()}" for i in range(start_idx, end_idx)]
        return "\n".join(output)
    except Exception as e:
        return f"Error reading {filepath}: {e}"

@tool
def audit_silicon_and_rf_feasibility(
    requires_gpu: bool,
    requires_ram_mb: int,
    subsystem: str,
    rf_topology: str
) -> str:
    """Audit whether a proposed technical claim or algorithm is physically possible on openMAX hardware.
    TARGET HARDWARE SPECIFICATION:
    - AP SoC: Atheros AR9342 (MIPS 74Kc @ 533-600 MHz, 32-bit single-core, NO GPU, NO FPU).
    - AP RAM: 64 MB or 128 MB DDR2 (strictly bounded memory footprint).
    - Radio Silicon: Qualcomm Atheros QCA9880-BR4A (802.11ac Wave 1, 3x3 MIMO).
    - Firmware: Candela Technologies ath10k-ct FW022 (closed microcode offloaded rate control).
    - AP Antenna: 120-degree sector horn (always covers all CPEs in the sector).
    - CPEs: Stationary outdoor dish antennas (>110 dB path loss between CPEs, hidden to each other).
    - Band: 5 GHz (UNII-1, UNII-2/DFS, UNII-3). NOT 60 GHz mm-Wave.
    
    Args:
        requires_gpu: Set True if the approach needs CUDA, OpenCL, or GPU accelerators.
        requires_ram_mb: Approximate memory required in Megabytes.
        subsystem: The target subsystem ('LINUX_KERNEL', 'MAC80211', 'ATH10K_DRIVER', 'QCA9880_FIRMWARE', 'UPSTREAM_GATEWAY').
        rf_topology: The RF context ('5GHZ_SECTOR_PTMP', 'MMWAVE_BEAMSTEERING', 'INDOOR_OMNI').
    Returns:
        STRICT FEASIBILITY REPORT (PASS or REJECT with specific physical reason).
    """
    rejections = []
    
    if requires_gpu:
        rejections.append("FATAL: Target hardware is MIPS 74Kc with NO GPU. CUDA/OpenCL is physically impossible.")
        
    if requires_ram_mb > 32 and subsystem != "UPSTREAM_GATEWAY":
        rejections.append(f"FATAL: Target AP has only 64-128 MB total RAM. Allocation of {requires_ram_mb} MB on the AP causes kernel OOM panic.")
        
    if "MMWAVE" in rf_topology.upper():
        rejections.append("FATAL: Target network is 5 GHz fixed outdoor PtMP with 120-deg sector AP. mmWave beam-steering deafness assumptions are INVALID.")
        
    if subsystem == "UPSTREAM_GATEWAY" and "RATE" in rf_topology.upper():
        rejections.append("FATAL: Upstream gateway shaper has no visibility into 802.11 PHY rates or MCS masks.")

    if rejections:
        return "AUDIT FAILED (REJECT CLAIM):\n" + "\n".join(rejections)
    
    return "AUDIT PASSED (FEASIBLE): Proposed mechanism respects MIPS 74Kc CPU limits, memory boundaries, and 5 GHz sector geometry."

@tool
def save_grounded_dossier(filename: str, report_markdown: str) -> str:
    """Save the final verified dossier to artifacts and knowledge."""
    p_art = FUTURAMAX_ROOT / "artifacts" / filename
    p_art.parent.mkdir(parents=True, exist_ok=True)
    p_art.write_text(report_markdown, encoding="utf-8")
    return f"Saved verified dossier to {p_art}"


def run_grounded_investigation():
    print("==================================================")
    print("  PraisonAI Grounded Multi-Agent Team (openMAX)")
    print("  Architecture: ScholarScout -> SourceAuditor -> SiliconGatekeeper")
    print("==================================================")

    # Agent 1: Scholar Scout
    scout = Agent(
        name="ScholarScout",
        role="Academic Literature Discovery Agent",
        goal="Discover candidate algorithms and mechanisms for outdoor 802.11ac rate bounding from arXiv.",
        instructions="""
Search arXiv for rate adaptation and multi-armed bandit algorithms in 802.11 wireless networks.
Summarize the core candidate algorithms found (e.g. Thompson Sampling, UCB, ADR-bandit) and pass them to SourceAuditor.
Do NOT declare any claim confirmed until verified in source code.
""",
        llm="gpt-4o-mini",
        tools=[search_arxiv],
        execution=ExecutionConfig(max_iter=6, max_tool_calls_per_turn=2)
    )

    # Agent 2: C Source Code Auditor
    auditor = Agent(
        name="SourceAuditor",
        role="ath10k and Linux mac80211 Kernel Source Auditor",
        goal="Verify if proposed rate-mask hooks actually exist in tools/research/srccache/ath10k-ct and linux.",
        instructions="""
Use `grep_driver_source` and `read_c_source_lines` to inspect `tools/research/srccache/ath10k-ct/ath10k/mac.c` and `core.c`.
Specifically investigate:
1. What does `ATH10K_FW_FEATURE_CT_RATEMASK` ("ratemask-CT") actually do?
2. Is `bitrate_mask` in ath10k applied per-STA (station) or per-VDEV (virtual device / entire BSS)?
3. Can the host force a rate mask without causing firmware asserts?
Report the exact C line numbers and struct names.
""",
        llm="gpt-4o-mini",
        tools=[grep_driver_source, read_c_source_lines],
        execution=ExecutionConfig(max_iter=8, max_tool_calls_per_turn=2)
    )

    # Agent 3: Silicon & RF Gatekeeper
    gatekeeper = Agent(
        name="SiliconGatekeeper",
        role="Principal Systems Architect & Reality Gatekeeper",
        goal="Enforce hard hardware boundaries (MIPS 74Kc, 64MB RAM, no GPU, 5 GHz sector) and synthesize final dossier.",
        instructions="""
Review the findings from ScholarScout and SourceAuditor.
1. Run `audit_silicon_and_rf_feasibility` on any proposal.
2. Reject any proposal that requires GPUs, exceeds 16 MB RAM, or confuses mmWave beamsteering with 5 GHz sector horns.
3. Synthesize a definitive Grade-A Markdown report with:
   - Executive Summary
   - Verified C Source Code Ground Truth (with file paths and line numbers)
   - Academic Algorithm Analysis (ADR-bandit vs Thompson Sampling)
   - Real Physical Feasibility on Ubiquiti LAP-120
   - Concrete Testbed Implementation Recipe
4. Save the dossier using `save_grounded_dossier(filename='praisonai_grounded_ratemask_dossier.md', report_markdown=...)`.
""",
        llm="gpt-4o-mini",
        tools=[audit_silicon_and_rf_feasibility, save_grounded_dossier],
        execution=ExecutionConfig(max_iter=8, max_tool_calls_per_turn=2)
    )

    task1 = Task(
        description="Search arXiv for 802.11 rate adaptation and multi-armed bandit literature.",
        expected_output="Summary of candidate rate adaptation algorithms.",
        agent=scout
    )

    task2 = Task(
        description="Verify in ath10k-ct C source code how ratemask-CT and bitrate_mask are implemented.",
        expected_output="Source code verification of rate mask control surface in ath10k-ct.",
        agent=auditor
    )

    task3 = Task(
        description="Audit feasibility on AR9342 MIPS 74Kc / QCA9880 and synthesize verified dossier.",
        expected_output="Final grounded dossier saved to artifacts/praisonai_grounded_ratemask_dossier.md.",
        agent=gatekeeper
    )

    agents = PraisonAIAgents(
        agents=[scout, auditor, gatekeeper],
        tasks=[task1, task2, task3],
        process="sequential"
    )

    print("\n[+] Starting Grounded Multi-Agent Team Execution...")
    result = agents.start()
    print("\n[+] Grounded Team Execution Complete.")
    return result

if __name__ == "__main__":
    run_grounded_investigation()
