# Autonomous Agent Observability & Telemetry Dashboard
> **Generated at**: 2026-09-26 21:11:13
> **Database**: `G:\_OneDrive\OneDrive\Desktop\Py Apps\futuraMAX\tools\observability\telemetry.db`

## 1. Recent Agent Executions & Escalation Ledger

*No agent runs logged yet.*

## 2. Model Tiering & Escalation Framework

- **Tier 1 (Scout / Fast Polling)**: `gemini-2.5-flash` / `gpt-4o-mini`. Zero reasoning overhead, fast response (<1.5s), cost < $0.001/run. Used for 95% of routine polls.
- **Tier 2 (Investigator / Multi-Source)**: `gemini-2.5-pro` / `gpt-5.6-sol`. High context window, deep mathematical/algorithmic reasoning. Triggered on anomaly detection or complex synthesis.
- **Tier 3 (Orchestrator / Pair Commander)**: `claude-fable-5-1` / `gpt-6-astra`. High-stakes architectural, firmware flash, or live routing topology decisions.