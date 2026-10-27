"""
Shared Multi-Agent Task Board & Atomic Claim Manager (`orchestration/task_board.py`).

Allows all FuturaMAX / openMAX agents (Antigravity Coordinator, Codex, visible Orca Gemini terminals,
and background subagents) to list, claim, claim-next, enqueue, update, and complete tasks in
`artifacts/orchestration/agent_task_board.json` and synchronize the Markdown table in
`docs/MULTI_AGENT_TASK_BOARD.md`.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
JSON_BOARD_PATH = ROOT / "artifacts" / "orchestration" / "agent_task_board.json"
MD_BOARD_PATH = ROOT / "docs" / "MULTI_AGENT_TASK_BOARD.md"

PHASE0_QUEUE: List[Dict[str, Any]] = [
    {
        "task_id": "T-PB-CODEX-01",
        "status": "READY",
        "owner": "codex:term_a6309070",
        "priority": "P0",
        "title": "Physical-Boundary Phase 0 Workstream A + B: Register & Distill Research Report + Source Audit (starlink-wifi & linux pinned commits)",
        "exclusive_write_scope": "knowledge/QCA988X_PHYSICAL_BOUNDARY_2026.md, research/physical_boundary/evidence_delta_2026-10-24.md, research/physical_boundary/source_manifest.json, research/physical_boundary/source_audit.md",
        "updated_utc": "2026-10-24T17:47:00Z",
        "summary": "Execute Workstreams A & B of research/openMAX_codex_physical_boundary_phase0_prompt.md on research/openMAX_QCA988x_physical_boundary_research_2026-10-24.md",
    },
    {
        "task_id": "T-PB-CODEX-02",
        "status": "READY",
        "owner": "codex:term_a6309070",
        "priority": "P0",
        "title": "Autoresearch Waves BQ-BT (R93..R96), BU-BX (R97..R102), BY-CF (R103..R134) Offline Matrix & Root Doc Sync",
        "exclusive_write_scope": "orchestration/autoresearch/*, artifacts/autoresearch/waves_*, docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md, docs/CURRENT_STATE.md, docs/DECISIONS.md, docs/RESEARCH_LEDGER.md, docs/EXPERIMENTS.md, docs/DOCS-MAP.md",
        "updated_utc": "2026-10-24T17:47:00Z",
        "summary": "Queued after T-PB-CODEX-01: integrate R93..R134 into offline selector & 7 root docs",
    },
    {
        "task_id": "T-PB-GEM1-01",
        "status": "READY",
        "owner": "orca:gemini-lane1",
        "priority": "P0",
        "title": "Physical-Boundary Phase 0 Workstream D (D1 + D2): Repair Autonomous Experiment Oracle (analysis/metrics/schema.py width fix + analysis/regression_gate/gatekeeper.py paired A/B & A/A null replay)",
        "exclusive_write_scope": "analysis/metrics/schema.py, analysis/regression_gate/gatekeeper.py, tests/test_pb_metrics_schema_width.py, tests/test_pb_gatekeeper_paired_aa.py",
        "updated_utc": "2026-10-24T17:47:00Z",
        "summary": "Fix 40MHz hard-coded denominator in schema.py + implement paired block-aware bootstrap/permutation & A/A null-label replay in gatekeeper.py",
    },
    {
        "task_id": "T-PB-GEM1-02",
        "status": "READY",
        "owner": "orca:gemini-lane1",
        "priority": "P0",
        "title": "Physical-Boundary Phase 0 Workstream C: Machine-Readable Experimental Ladder (PB-000..PB-070) + Validator + Docs",
        "exclusive_write_scope": "research/physical_boundary/ladder.yaml, research/physical_boundary/ladder_schema.py, docs/PHYSICAL_BOUNDARY_EXPERIMENTAL_LADDER.md, tests/test_pb_experimental_ladder.py",
        "updated_utc": "2026-10-24T17:47:00Z",
        "summary": "Build machine-verifiable PB-000..PB-070 DAG ladder with prerequisites, safety gates, and falsification criteria",
    },
    {
        "task_id": "T-PB-GEM1-03",
        "status": "READY",
        "owner": "orca:gemini-lane1",
        "priority": "P0",
        "title": "Physical-Boundary Phase 0 Workstream F: Frozen First Physical Campaign Plan (Track 1 UTF Read-Only & Track 2 Channel-Capture Qualification)",
        "exclusive_write_scope": "docs/bench/PB_FIRST_PHYSICAL_CAMPAIGN.md, controller/pb_campaign_preflight_verifier.py, tests/test_pb_campaign_preflight_verifier.py",
        "updated_utc": "2026-10-24T17:47:00Z",
        "summary": "Freeze Track 1 (AR9888 UTF read-only bring-up) and Track 2 (bb_capture_channel / bb_captured_channel export) with strict allowlists",
    },
    {
        "task_id": "T-PB-GEM2-01",
        "status": "READY",
        "owner": "orca:gemini-lane2",
        "priority": "P0",
        "title": "Physical-Boundary Phase 0 Workstream E1 + E2: Pinned Source Verifier & Exact AR9888/v2 Descriptor Map Extractor",
        "exclusive_write_scope": "tools/qca988x/fetch_pinned_sources.py, tools/qca988x/extract_descriptor_map.py, artifacts/qca988x/ar9888_v2_descriptor_map.json, docs/STAGE12_AR9888_V2_DESCRIPTOR_AND_CHANNEL_DUMP_MAP.md, tests/test_qca988x_descriptor_map.py",
        "updated_utc": "2026-10-24T17:47:00Z",
        "summary": "Extract exact bit offsets/masks for bb_capture_channel, bb_captured_channel, bb_length, txbf_h_info, cv_ptr, EVM, timestamps, and series_bw",
    },
    {
        "task_id": "T-PB-GEM2-02",
        "status": "READY",
        "owner": "orca:gemini-lane2",
        "priority": "P0",
        "title": "Physical-Boundary Phase 0 Workstream E3 + E4: AR9888 UTF Command Handler Tracer & UTF Build-Graph Inventory",
        "exclusive_write_scope": "tools/qca988x/trace_utf_handlers.py, tools/qca988x/utf_build_inventory.py, artifacts/qca988x/ar9888_utf_handler_and_build_matrix.json, docs/STAGE12_AR9888_UTF_HANDLER_AND_BUILD_GRAPH.md, tests/test_qca988x_utf_tools.py",
        "updated_utc": "2026-10-24T17:47:00Z",
        "summary": "Classify ADCCAPTURE (ID 59), GENWAVEFORM (ID 61), PHYDBGDUMP, REGREAD/WRITE, MEMREAD/WRITE, and TARGET=AR9888 UTF build dependencies",
    },
    {
        "task_id": "T-PB-GEM2-03",
        "status": "READY",
        "owner": "orca:gemini-lane2",
        "priority": "P0",
        "title": "Physical-Boundary Phase 0 Workstream E5: QCA988x Target DRAM Memory-Diff & Channel-Dump / CFR Packing Analyzer",
        "exclusive_write_scope": "tools/qca988x/memory_diff_analyzer.py, artifacts/qca988x/memory_diff_fixture_report.json, docs/STAGE12_QCA988X_TARGET_DRAM_AND_CHANNEL_DUMP_ANALYZER.md, tests/test_qca988x_memory_diff_analyzer.py",
        "updated_utc": "2026-10-24T17:47:00Z",
        "summary": "Offline analyzer for aligned 0x400000..0x44ffff target DRAM snapshots, packet-correlated channel-dump blobs, and CFR tone-packing hypotheses",
    },
    {
        "task_id": "T-BENCH-03",
        "status": "READY",
        "owner": "subagent:bench-runner",
        "priority": "P0",
        "title": "Physical Bench R135..R140: Coarse hMAC-Style Per-Peer/TID Host Queue Gating + Mixed Bidir/VoIP Distance Sweep (1km..14km on LAP-120 <-> Loco195)",
        "exclusive_write_scope": "tools/bench/run_live_autoresearch_r135..r140*.py, artifacts/autoresearch/lap120_loco195_r135..r140*.json",
        "updated_utc": "2026-10-24T17:47:00Z",
        "summary": "Physical test of Experiment #14 (coarse host queue gating + asymmetric AQL + AC_VO VoIP slice across 1km..14km)",
    },
]


def load_board() -> Dict[str, Any]:
    JSON_BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not JSON_BOARD_PATH.exists():
        data = {
            "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tasks": list(PHASE0_QUEUE),
        }
        save_board(data)
        return data
    return json.loads(JSON_BOARD_PATH.read_text(encoding="utf-8"))


def save_board(data: Dict[str, Any]) -> None:
    JSON_BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    JSON_BOARD_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    if MD_BOARD_PATH.exists():
        md_text = MD_BOARD_PATH.read_text(encoding="utf-8")
        start_marker = "<!-- TASK_TABLE_START -->"
        end_marker = "<!-- TASK_TABLE_END -->"
        if start_marker in md_text and end_marker in md_text:
            lines = [
                start_marker,
                "| Task ID | Status | Owner Agent | Priority | Title & Deliverable | Exclusive Write Scope | Last Updated (UTC) | Summary / Notes |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
            ]
            for t in data["tasks"]:
                tid = t.get("task_id") or t.get("id") or "UNKNOWN"
                t["task_id"] = tid
                lines.append(
                    f"| `{tid}` | `{t.get('status', 'DONE')}` | `{t.get('owner', 'any')}` | `{t.get('priority', 'P0')}` | {t.get('title', tid)} | `{t.get('exclusive_write_scope', 'assigned_lane_scope')}` | `{t.get('updated_utc', data['updated_utc'])}` | {t.get('summary', '')} |"
                )
            lines.append(end_marker)
            prefix = md_text.split(start_marker)[0]
            suffix = md_text.split(end_marker)[1]
            MD_BOARD_PATH.write_text(prefix + "\n".join(lines) + suffix, encoding="utf-8")
    try:
        from tools.build_command_center_html import build_html
        build_html()
    except Exception:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="FuturaMAX Shared Multi-Agent Task Board")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")
    sub.add_parser("seed-phase0")

    p_claim = sub.add_parser("claim")
    p_claim.add_argument("--task-id", required=True)
    p_claim.add_argument("--agent", required=True)
    p_claim.add_argument("--status", default="RUNNING")
    p_claim.add_argument("--note", default="")

    p_next = sub.add_parser("claim-next")
    p_next.add_argument("--agent", required=True)

    p_done = sub.add_parser("complete")
    p_done.add_argument("--task-id", required=True)
    p_done.add_argument("--agent", required=True)
    p_done.add_argument("--summary", required=True)

    args = parser.parse_args()
    board = load_board()
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if args.cmd == "list":
        print(json.dumps(board, indent=2))
        return

    if args.cmd == "seed-phase0":
        existing_ids = {t["task_id"]: t for t in board["tasks"]}
        if "T-CODEX-01" in existing_ids:
            existing_ids["T-CODEX-01"]["status"] = "DONE"
            existing_ids["T-CODEX-01"]["updated_utc"] = now_str
            existing_ids["T-CODEX-01"]["summary"] = (
                "Waves BI-BL and BM-BP (R87..R92) completed offline: 4,282 PASS, 0 failed, 5 held Flent skips; sealed final_validation.json & STAGE12_R87_TO_R92_COVCLASS31_CEILING_AND_FULL_MATRIX_AUDIT.md"
            )
        for item in PHASE0_QUEUE:
            if item["task_id"] not in existing_ids:
                board["tasks"].append(dict(item))
        save_board(board)
        print(f"SEEDED_PHASE0_QUEUE: total_tasks={len(board['tasks'])}")
        return

    if args.cmd == "claim-next":
        for t in board["tasks"]:
            if t["status"] in ("READY", "PENDING") and (
                args.agent in t["owner"] or t["owner"] in args.agent or t["owner"] == "any"
            ):
                t["status"] = "RUNNING"
                t["owner"] = args.agent
                t["updated_utc"] = now_str
                save_board(board)
                print(json.dumps({"claimed": True, "task": t}, indent=2))
                return
        print(json.dumps({"claimed": False, "reason": "NO_MORE_READY_TASKS_FOR_AGENT"}, indent=2))
        return

    found = False
    for t in board["tasks"]:
        tid = t.get("task_id") or t.get("id")
        if tid and "task_id" not in t:
            t["task_id"] = tid
        if tid == args.task_id:
            found = True
            t["owner"] = args.agent
            t["updated_utc"] = now_str
            if args.cmd == "claim":
                t["status"] = args.status
                if args.note:
                    t["summary"] = args.note
            elif args.cmd == "complete":
                t["status"] = "DONE"
                t["summary"] = args.summary
            break

    if not found:
        board["tasks"].append(
            {
                "task_id": args.task_id,
                "status": "DONE" if args.cmd == "complete" else args.status,
                "owner": args.agent,
                "priority": "P0",
                "title": f"Task {args.task_id}",
                "exclusive_write_scope": "assigned_lane_scope",
                "updated_utc": now_str,
                "summary": args.summary if args.cmd == "complete" else (args.note or "Active task"),
            }
        )

    save_board(board)
    print(f"OK: {args.cmd} {args.task_id} by {args.agent}")


if __name__ == "__main__":
    main()
