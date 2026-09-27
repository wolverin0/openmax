"""
PraisonAI & Autonomous Agent Observability Ledger.
SQLite-backed telemetry tracking agent executions, model tiers, tool call latencies,
costs, loop-guard warnings, and escalation events for tuning and observability.
"""

import sqlite3
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

DB_PATH = Path(__file__).resolve().parent / "telemetry.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS agent_runs (
        run_id TEXT PRIMARY KEY,
        timestamp TEXT,
        agent_name TEXT,
        task_name TEXT,
        model TEXT,
        model_tier TEXT,
        status TEXT,
        cost_usd REAL,
        tokens_input INTEGER,
        tokens_output INTEGER,
        duration_ms REAL,
        loop_guard_warnings INTEGER DEFAULT 0,
        escalated_to TEXT,
        error_summary TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tool_telemetry (
        call_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT,
        tool_name TEXT,
        timestamp TEXT,
        duration_ms REAL,
        success INTEGER,
        loop_warning INTEGER DEFAULT 0,
        args_preview TEXT,
        error_msg TEXT,
        FOREIGN KEY(run_id) REFERENCES agent_runs(run_id)
    )
    """)
    conn.commit()
    conn.close()

init_db()

class TelemetryTracker:
    def __init__(self, run_id: str, agent_name: str, task_name: str, model: str, model_tier: str = "scout"):
        self.run_id = run_id
        self.agent_name = agent_name
        self.task_name = task_name
        self.model = model
        self.model_tier = model_tier
        self.start_time = time.time()
        self.loop_warnings = 0
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO agent_runs (run_id, timestamp, agent_name, task_name, model, model_tier, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.run_id,
            datetime.now(timezone.utc).isoformat(),
            self.agent_name,
            self.task_name,
            self.model,
            self.model_tier,
            "RUNNING"
        ))
        conn.commit()
        conn.close()

    def record_tool_call(self, tool_name: str, duration_ms: float, success: bool, args: Dict[str, Any] = None, loop_warning: bool = False, error_msg: str = None):
        if loop_warning:
            self.loop_warnings += 1
            
        args_str = json.dumps(args, default=str)[:300] if args else ""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO tool_telemetry (run_id, tool_name, timestamp, duration_ms, success, loop_warning, args_preview, error_msg)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.run_id,
            tool_name,
            datetime.now(timezone.utc).isoformat(),
            round(duration_ms, 2),
            1 if success else 0,
            1 if loop_warning else 0,
            args_str,
            str(error_msg)[:300] if error_msg else None
        ))
        conn.commit()
        conn.close()

    def finish(self, status: str, cost_usd: float = 0.0, tokens_in: int = 0, tokens_out: int = 0, escalated_to: Optional[str] = None, error_summary: Optional[str] = None):
        duration_ms = (time.time() - self.start_time) * 1000
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        UPDATE agent_runs
        SET status = ?, cost_usd = ?, tokens_input = ?, tokens_output = ?, duration_ms = ?, loop_guard_warnings = ?, escalated_to = ?, error_summary = ?
        WHERE run_id = ?
        """, (
            status,
            cost_usd,
            tokens_in,
            tokens_out,
            round(duration_ms, 2),
            self.loop_warnings,
            escalated_to,
            error_summary,
            self.run_id
        ))
        conn.commit()
        conn.close()

def get_runs_summary(limit: int = 15) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
    SELECT r.*, COUNT(t.call_id) as total_tool_calls,
           SUM(CASE WHEN t.success = 0 THEN 1 ELSE 0 END) as failed_tool_calls
    FROM agent_runs r
    LEFT JOIN tool_telemetry t ON r.run_id = t.run_id
    GROUP BY r.run_id
    ORDER BY r.timestamp DESC
    LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows
