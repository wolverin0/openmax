#!/usr/bin/env python3
"""Deterministic Antigravity (agy) PostToolUse & Stop hook for MemoryMaster auto-ingest + ClosedLoopResearchReactor.

On PostToolUse (write_file/edit_file/run_command) or Stop:
  1. Scans `artifacts/autoresearch/stage*.json` and `artifacts/guarida_canary/stage*.json`
     for newly created or modified stage receipts not yet synced in `~/.memorymaster/hook_state/fmx_ingested_receipts.json`.
  2. Automatically ingests each new stage receipt into `G:/_OneDrive/OneDrive/Desktop/Py Apps/memorymaster/memorymaster.db`
     (`scope="project:futuramax"`, `source_agent="agy-deterministic-hook"`) via `MemoryService.ingest()`.
  3. Automatically enqueues new hardware/benchmark findings into `ClosedLoopResearchReactor`
     (`artifacts/autoresearch/discovery_to_research_queue.json`).
  4. Emits Antigravity's expected JSON response:
     - `{"decision": "allow"}` when invoked as `Stop` (`--event stop`)
     - `{}` when invoked as `PostToolUse` (`--event post-tool`)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MM_ROOT = "G:/_OneDrive/OneDrive/Desktop/Py Apps/memorymaster"
MM_WT_ROOT = "G:/_OneDrive/OneDrive/Desktop/Py Apps/memorymaster/_wt/hooks-main"
DB_PATH = "G:/_OneDrive/OneDrive/Desktop/Py Apps/memorymaster/memorymaster.db"
STATE_DIR = Path.home() / ".memorymaster" / "hook_state"
INGESTED_LEDGER = STATE_DIR / "fmx_ingested_receipts.json"


def _log(event: str, msg: str) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with (STATE_DIR / "agy_hook.log").open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{event}] {msg}\n")
    except Exception:
        pass


def _load_ledger() -> dict[str, str]:
    if not INGESTED_LEDGER.exists():
        return {}
    try:
        return json.loads(INGESTED_LEDGER.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_ledger(ledger: dict[str, str]) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        INGESTED_LEDGER.write_text(json.dumps(ledger, indent=2, sort_keys=True), encoding="utf-8")
    except Exception:
        pass


def _summarize_receipt(path: Path, data: dict) -> tuple[str, str, str]:
    stage = str(
        data.get("stage")
        or data.get("task_id")
        or data.get("experiment_id")
        or path.stem
    )
    verdict = str(
        data.get("verdict")
        or data.get("status")
        or data.get("champion_id")
        or data.get("overall_verdict")
        or "CONFIRMED"
    )
    summary_parts = [f"FuturaMAX receipt {path.name} ({stage}, verdict={verdict})"]
    for key in (
        "summary",
        "headline",
        "champion_summary",
        "decision",
        "key_finding",
        "goodput_delta_pct",
    ):
        val = data.get(key)
        if isinstance(val, (str, int, float)) and str(val).strip():
            summary_parts.append(f"{key}={str(val).strip()[:180]}")
    if "champions" in data and isinstance(data["champions"], dict):
        summary_parts.append(f"champions={','.join(list(data['champions'].keys())[:6])}")
    text = " | ".join(summary_parts)[:480]
    return stage, verdict, text


def sync_new_stage_receipts(max_new_per_run: int = 5) -> dict[str, int]:
    t0 = time.perf_counter()
    ledger = _load_ledger()
    candidates: list[Path] = []
    for sub in ("artifacts/autoresearch", "artifacts/guarida_canary", "artifacts/curation"):
        folder = REPO_ROOT / sub
        if folder.exists():
            candidates.extend(sorted(folder.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:15])

    new_items: list[tuple[Path, str, dict]] = []
    for p in candidates:
        try:
            raw = p.read_bytes()
            sha = hashlib.sha256(raw).hexdigest()[:16]
            key = p.relative_to(REPO_ROOT).as_posix()
            if ledger.get(key) == sha:
                continue
            parsed = json.loads(raw.decode("utf-8", errors="replace"))
            if isinstance(parsed, dict):
                new_items.append((p, sha, parsed))
                if len(new_items) >= max_new_per_run:
                    break
        except Exception:
            continue

    ingested_mm = 0
    enqueued_reactor = 0

    if new_items and os.path.exists(DB_PATH):
        for candidate in (MM_WT_ROOT, MM_ROOT):
            if os.path.exists(candidate) and candidate not in sys.path:
                sys.path.insert(0, candidate)
        try:
            from memorymaster.core.models import CitationInput
            from memorymaster.core.service import MemoryService

            svc = MemoryService(DB_PATH, workspace_root=REPO_ROOT)
            for p, sha, parsed in new_items:
                rel_key = p.relative_to(REPO_ROOT).as_posix()
                stage, verdict, text = _summarize_receipt(p, parsed)
                try:
                    svc.ingest(
                        text=text,
                        citations=[
                            CitationInput(
                                source="fmx-stage-receipt",
                                locator=rel_key,
                                excerpt=text[:200],
                            )
                        ],
                        idempotency_key=f"fmx-receipt-{sha}",
                        claim_type="fact",
                        subject=stage[:64],
                        predicate="benchmark_or_stage_receipt",
                        object_value=verdict[:64],
                        scope="project:futuramax",
                        confidence=0.9,
                        source_agent="agy-deterministic-hook",
                    )
                    ledger[rel_key] = sha
                    ingested_mm += 1
                except Exception as exc:
                    _log("MM-Ingest", f"warn on {rel_key}: {exc}")
                    ledger[rel_key] = sha
        except Exception as exc:
            _log("MM-Service", f"error: {exc}")

    if new_items:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        try:
            from tools.research.closed_loop_research_reactor import ClosedLoopResearchReactor

            reactor = ClosedLoopResearchReactor()
            for p, _sha, parsed in new_items:
                stage, verdict, text = _summarize_receipt(p, parsed)
                reactor.enqueue_discovery(
                    stage_id=stage,
                    hardware_domain=str(parsed.get("hardware_domain") or parsed.get("platform") or "multi-radio"),
                    observation=text,
                    attribution_layer=str(parsed.get("attribution_layer") or "Linux/mac80211/ath10k/airMAX/LTU"),
                    claim_status="CONFIRMED" if "CONFIRM" in verdict.upper() or "PASS" in verdict.upper() else "INFERRED",
                    scholar_queries=[f"IEEE 802.11 {stage} wireless PtMP AQL BQL TDMA"],
                )
                enqueued_reactor += 1
        except Exception as exc:
            _log("Reactor", f"warn: {exc}")

    if new_items:
        _save_ledger(ledger)

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
    if ingested_mm or enqueued_reactor:
        _log("Sync", f"ingested_mm={ingested_mm} enqueued_reactor={enqueued_reactor} elapsed_ms={elapsed_ms}")
    return {"ingested_mm": ingested_mm, "enqueued_reactor": enqueued_reactor}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", choices=["post-tool", "stop"], default="stop")
    args = parser.parse_args()

    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw and raw.strip() else {}
    except Exception:
        data = {}

    sync_new_stage_receipts(max_new_per_run=5)

    if args.event == "stop":
        conv_id = str(data.get("conversationId") or "agy")[:12]
        _log("Stop", f"conv={conv_id} decision=allow")
        sys.stdout.write(json.dumps({"decision": "allow"}))
    else:
        sys.stdout.write(json.dumps({}))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
