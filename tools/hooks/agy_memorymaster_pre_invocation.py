#!/usr/bin/env python3
"""Deterministic Antigravity (agy) PreInvocation hook for MemoryMaster recall + FuturaMAX 5-Pillar gate.

Reads Antigravity's PreInvocation JSON payload from stdin:
  {"conversationId": "...", "workspacePaths": [...], "lastUserInput": "..."}
Executes:
  1. MemoryMaster `hook_recall` against G:/_OneDrive/OneDrive/Desktop/Py Apps/memorymaster/memorymaster.db
  2. Pinned claim summary for `project:futuramax` / `project:infra` / `project:wisp`
  3. FuturaMAX 5-Pillar & 17-Discovery (`FMX-DISC-01..17`) invariant reminder when workspace is futuraMAX
Emits Antigravity's native PreInvocation contract:
  {"injectSteps": [{"ephemeralMessage": "..."}]}
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

MM_ROOT = "G:/_OneDrive/OneDrive/Desktop/Py Apps/memorymaster"
MM_WT_ROOT = "G:/_OneDrive/OneDrive/Desktop/Py Apps/memorymaster/_wt/hooks-main"
DB_PATH = "G:/_OneDrive/OneDrive/Desktop/Py Apps/memorymaster/memorymaster.db"
STATE_DIR = Path.home() / ".memorymaster" / "hook_state"


def _log(msg: str) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with (STATE_DIR / "agy_hook.log").open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [PreInvocation] {msg}\n")
    except Exception:
        pass


def _fetch_pinned_futuramax_claims(limit: int = 6) -> list[str]:
    if not os.path.exists(DB_PATH):
        return []
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=1.5)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT human_id, scope, substr(text, 1, 220)
            FROM claims
            WHERE status = 'confirmed'
              AND (
                (scope = 'project:futuramax' AND pinned = 1)
                OR (scope IN ('project:futuramax', 'project:wisp', 'project:wispoptimizer') AND confidence >= 0.85)
              )
            ORDER BY pinned DESC, updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = [f"- [{r[0] or 'mm'}] ({r[1]}): {r[2]}" for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception as exc:
        _log(f"sqlite pinned fallback error: {exc}")
        return []


def _run_mm_hook_recall(query: str, conversation_id: str, cwd: str) -> str:
    if not query or len(query.strip()) < 2:
        return ""
    for candidate in (MM_WT_ROOT, MM_ROOT):
        if os.path.exists(candidate) and candidate not in sys.path:
            sys.path.insert(0, candidate)
    os.environ["MEMORYMASTER_DEFAULT_DB"] = DB_PATH
    try:
        from memorymaster.recall.remote import hook_recall

        hook_data = {
            "prompt": query,
            "session_id": conversation_id,
            "cwd": cwd,
        }
        ctx, via = hook_recall(query, hook_data, db_path=DB_PATH)
        _log(f"hook_recall via={via} query_len={len(query)} hit={bool(ctx)}")
        return ctx or ""
    except Exception as exc:
        _log(f"hook_recall error: {exc}")
        return ""


def build_pre_invocation_payload(stdin_data: dict) -> dict:
    t0 = time.perf_counter()
    query = str(stdin_data.get("lastUserInput") or stdin_data.get("prompt") or "").strip()
    conversation_id = str(stdin_data.get("conversationId") or stdin_data.get("session_id") or "agy")
    workspaces = stdin_data.get("workspacePaths") or []
    cwd = workspaces[0] if isinstance(workspaces, list) and workspaces else str(stdin_data.get("cwd") or os.getcwd())
    is_futuramax = "futuramax" in cwd.lower()

    blocks: list[str] = []

    # 1. Run MemoryMaster semantic/FTS/hybrid recall on user input
    recall_ctx = _run_mm_hook_recall(query, conversation_id, cwd)
    if recall_ctx:
        blocks.append(f"[MemoryMaster Automatic Recall (`memorymaster.db`)]\n{recall_ctx.strip()}")

    # 2. If inside FuturaMAX, always attach pinned project claims + 5-Pillar & 17-Discovery gate
    if is_futuramax:
        pinned = _fetch_pinned_futuramax_claims(limit=6)
        if pinned:
            blocks.append(
                "[MemoryMaster Pinned `project:futuramax` Claims]\n" + "\n".join(pinned)
            )
        blocks.append(
            "[FuturaMAX Deterministic 5-Pillar & Anti-Amnesia Gate]\n"
            "- Pillar A (`/fullrea`): REA MCP + Ghidra/IDA/Rizin + `fullrea_helper.py` + 571-Knob Catalog (`orchestration/autoresearch/firmware_knob_candidates.json`).\n"
            "- Pillar B (`HYPERRESEARCH` + `scholar-mcp`): Enqueue discoveries via `ClosedLoopResearchReactor` (`tools/research/closed_loop_research_reactor.py`).\n"
            "- Pillar C (Karpathy `autoresearch`): Counterbalanced `A1->B1->A2->B2`, `45s` rollback watchdog, Staged PtP OpenWrt conversion (Hybrid `airOS 8` AP `.241` <-> `OpenWrt` STA `.242` first, NEVER ask operator to climb a tower).\n"
            "- Pillar D (K-Dense Skills): `pymoo`, `simpy`, `statistical-analysis`, `scientific-critical-thinking`.\n"
            "- Pillar E (`memory-master`): Auto-recalled above; ingest new milestones with `scope=\"project:futuramax\"`.\n"
            "- Curated Ledgers: `docs/CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md` (`FMX-DISC-01..17`, `Champion v1..v19`) & `docs/CURATED_MULTILANE_CODEX_AGY_RECONCILIATION.md`."
        )

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
    _log(f"done conv={conversation_id[:12]} blocks={len(blocks)} elapsed_ms={elapsed_ms}")

    if not blocks:
        return {}
    return {
        "injectSteps": [
            {
                "ephemeralMessage": "\n\n".join(blocks),
            }
        ]
    }


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw and raw.strip() else {}
    except Exception:
        data = {}

    out = build_pre_invocation_payload(data if isinstance(data, dict) else {})
    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
