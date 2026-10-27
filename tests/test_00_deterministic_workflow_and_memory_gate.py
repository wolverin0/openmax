"""Deterministic 4-Layer Anti-Amnesia & MemoryMaster Gate tests."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from tools.hooks.agy_memorymaster_post_and_stop import sync_new_stage_receipts
from tools.hooks.agy_memorymaster_pre_invocation import (
    DB_PATH,
    build_pre_invocation_payload,
)
from tools.verify.enforce_5pillar_research_gate import audit_repo_deterministic_gates


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_layer1_antigravity_hooks_json_and_user_hooks_wired() -> None:
    repo_hooks = REPO_ROOT / ".agents" / "hooks.json"
    assert repo_hooks.exists(), ".agents/hooks.json must exist"
    parsed = json.loads(repo_hooks.read_text(encoding="utf-8"))
    fmx_hook = parsed.get("futuramax-memorymaster-5pillar", {})
    assert "PreInvocation" in fmx_hook
    assert "PostToolUse" in fmx_hook
    assert "Stop" in fmx_hook

    user_hooks = Path(r"C:\Users\pauol\.gemini\config\hooks.json")
    if user_hooks.exists():
        u_parsed = json.loads(user_hooks.read_text(encoding="utf-8"))
        assert "memorymaster-agy" in u_parsed
        assert "PreInvocation" in u_parsed["memorymaster-agy"]
        assert "Stop" in u_parsed["memorymaster-agy"]


def test_layer1_pre_invocation_injects_memorymaster_and_5pillars() -> None:
    payload = build_pre_invocation_payload(
        {
            "conversationId": "test-conv-1234",
            "workspacePaths": [str(REPO_ROOT)],
            "lastUserInput": "Check PowerBeam PtP OpenWrt BQL and LTU 4096-QAM binary patch",
        }
    )
    assert "injectSteps" in payload
    msg = payload["injectSteps"][0]["ephemeralMessage"]
    assert "[FuturaMAX Deterministic 5-Pillar & Anti-Amnesia Gate]" in msg
    assert "FMX-DISC-01..17" in msg
    assert "[MemoryMaster Pinned `project:futuramax` Claims]" in msg


def test_layer1_post_and_stop_syncs_receipts_into_memorymaster() -> None:
    res = sync_new_stage_receipts(max_new_per_run=5)
    assert "ingested_mm" in res
    assert "enqueued_reactor" in res
    if Path(DB_PATH).exists():
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=2.0)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM claims WHERE scope = 'project:futuramax'")
        count = cur.fetchone()[0]
        conn.close()
        assert count >= 320


def test_layer3_and_layer4_repo_gate_and_git_pre_commit() -> None:
    audit = audit_repo_deterministic_gates(REPO_ROOT)
    assert audit["compliant"] is True, f"Repo deterministic gate failed: {audit['failures']}"
    pre_commit = REPO_ROOT / ".git" / "hooks" / "pre-commit"
    assert pre_commit.exists()
    assert "enforce_5pillar_research_gate.py" in pre_commit.read_text(encoding="utf-8")
