"""
Observability Dashboard Reporter.
Reads telemetry.db and renders an executive report detailing agent performance,
latencies, costs, loop-guard stops, and model tier escalations.
"""

import sys
from pathlib import Path
from datetime import datetime
from ledger import get_runs_summary, DB_PATH

FUTURAMAX_ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS_DIR = FUTURAMAX_ROOT / "artifacts"

def generate_report():
    runs = get_runs_summary(limit=20)
    lines = []
    lines.append("# Autonomous Agent Observability & Telemetry Dashboard")
    lines.append(f"> **Generated at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> **Database**: `{DB_PATH}`\n")
    lines.append("## 1. Recent Agent Executions & Escalation Ledger\n")
    
    if not runs:
        lines.append("*No agent runs logged yet.*")
    else:
        lines.append("| Timestamp | Agent / Task | Model / Tier | Status | Duration (s) | Cost ($) | Tools (Total/Fail) | Loop Warnings | Escalated To |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for r in runs:
            ts = r["timestamp"][:19].replace("T", " ")
            dur = f"{r['duration_ms'] / 1000:.1f}s" if r['duration_ms'] else "-"
            cost = f"${r['cost_usd']:.4f}" if r['cost_usd'] is not None else "-"
            tools = f"{r['total_tool_calls']} / {r['failed_tool_calls']}"
            esc = r['escalated_to'] or "-"
            status = r['status']
            if status == "SUCCESS":
                status_badge = "🟢 SUCCESS"
            elif status == "RUNNING":
                status_badge = "🟡 RUNNING"
            elif "STOP" in status or "FAILED" in status:
                status_badge = "🔴 " + status
            else:
                status_badge = status
                
            lines.append(f"| {ts} | **{r['agent_name']}**<br>_{r['task_name']}_ | `{r['model']}`<br>({r['model_tier']}) | {status_badge} | {dur} | {cost} | {tools} | {r['loop_guard_warnings']} | {esc} |")
            
    lines.append("\n## 2. Model Tiering & Escalation Framework\n")
    lines.append("- **Tier 1 (Scout / Fast Polling)**: `gemini-2.5-flash` / `gpt-4o-mini`. Zero reasoning overhead, fast response (<1.5s), cost < $0.001/run. Used for 95% of routine polls.")
    lines.append("- **Tier 2 (Investigator / Multi-Source)**: `gemini-2.5-pro` / `gpt-5.6-sol`. High context window, deep mathematical/algorithmic reasoning. Triggered on anomaly detection or complex synthesis.")
    lines.append("- **Tier 3 (Orchestrator / Pair Commander)**: `claude-fable-5-1` / `gpt-6-astra`. High-stakes architectural, firmware flash, or live routing topology decisions.")
    
    report_md = "\n".join(lines)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = ARTIFACTS_DIR / "agent_observability_dashboard.md"
    out_file.write_text(report_md, encoding="utf-8")
    
    print("\n" + report_md)
    print(f"\n[+] Dashboard artifact updated: {out_file}")
    return report_md

if __name__ == "__main__":
    generate_report()
