"""Reproducible Experiment Report Generator conforming to AGENTS.md §7.

Summary: Generates standardized, audit-proof markdown and JSON experiment reports
from ExperimentResultRecord. Calculates sample statistics, Welch's t-test summaries,
and formats metrics comparison tables for /clawd/reports/ and docs/EXPERIMENTS.md.
Keywords: AGENTS.md §7, report generator, markdown report, audit ledger, Welch t-test.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import List, Tuple
from analysis.metrics.schema import ExperimentResultRecord, RunSample


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: List[float], m: float) -> float:
    if len(values) <= 1:
        return 0.0
    var = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(var)


class ReportGenerator:
    """Generates standardized experiment markdown reports."""

    @classmethod
    def generate_markdown(cls, record: ExperimentResultRecord) -> str:
        """Formats an ExperimentResultRecord into a clean, GitHub-flavored markdown report."""
        meta = record.metadata
        base_samples = record.baseline_samples
        cand_samples = record.candidate_samples

        # Extract values
        b_goodput = [s.aggregate_goodput_mbps for s in base_samples]
        c_goodput = [s.aggregate_goodput_mbps for s in cand_samples]
        b_p99 = [s.p99_latency_ms for s in base_samples]
        c_p99 = [s.p99_latency_ms for s in cand_samples]
        b_fair = [s.jain_fairness_index for s in base_samples]
        c_fair = [s.jain_fairness_index for s in cand_samples]

        b_g_mean, c_g_mean = _mean(b_goodput), _mean(c_goodput)
        b_g_std, c_g_std = _std(b_goodput, b_g_mean), _std(c_goodput, c_g_mean)

        b_p_mean, c_p_mean = _mean(b_p99), _mean(c_p99)
        b_p_std, c_p_std = _std(b_p99, b_p_mean), _std(c_p99, c_p_mean)

        b_f_mean, c_f_mean = _mean(b_fair), _mean(c_fair)
        b_f_std, c_f_std = _std(b_fair, b_f_mean), _std(c_fair, c_f_mean)

        # Decision badge formatting
        decision_badges = {
            "KEEP": "**[KEEP - PROMOTED]**",
            "REJECT": "**[REJECT - ROLLED BACK]**",
            "INCONCLUSIVE": "**[INCONCLUSIVE - NEEDS RE-RUN]**",
        }
        badge = decision_badges.get(record.decision, f"**[{record.decision}]**")

        lines: List[str] = [
            f"# Experiment Report: {meta.experiment_id}",
            "",
            f"**Hypothesis**: {meta.hypothesis}  ",
            f"**Decision**: {badge}  ",
            f"**Rationale**: {record.rationale}",
            "",
            "## 1. Experiment Metadata",
            "",
            "| Parameter | Value |",
            "|---|---|",
            f"| **Hardware Revision** | {meta.hardware_revision} |",
            f"| **Firmware Build Hash** | `{meta.firmware_build_hash}` |",
            f"| **Topology** | {meta.topology} |",
            f"| **Channel / Bandwidth** | {meta.channel_mhz} MHz ({meta.channel_width_mhz} MHz) |",
            f"| **TX Power / Attenuation** | {meta.tx_power_dbm} dBm / {meta.attenuation_db} dB |",
            f"| **Offered Load** | {meta.offered_load_profile} |",
            f"| **Repetitions & Order** | {meta.repetitions} ({' -> '.join(meta.treatment_order)}) |",
            f"| **Rollback Condition** | {meta.rollback_condition} |",
            "",
            "## 2. Key Metrics Summary",
            "",
            "| Metric | Baseline (Mean +/- Std) | Candidate (Mean +/- Std) | Delta % | p-value | Gate Status |",
            "|---|---|---|---|---|---|",
            f"| **Aggregate Goodput (Mbps)** | {b_g_mean:.2f} +/- {b_g_std:.2f} | {c_g_mean:.2f} +/- {c_g_std:.2f} | {record.goodput_delta_pct:+.2f}% | p={record.p_value_goodput:.4f} | {'PASS' if record.goodput_delta_pct >= 5.0 and record.p_value_goodput < 0.10 else 'FAIL/NEUTRAL'} |",
            f"| **p99 Latency (ms)** | {b_p_mean:.2f} +/- {b_p_std:.2f} | {c_p_mean:.2f} +/- {c_p_std:.2f} | {record.p99_latency_delta_pct:+.2f}% | p={record.p_value_p99_latency:.4f} | {'PASS' if record.p99_latency_delta_pct <= 10.0 else 'FAIL'} |",
            f"| **Jain Fairness Index** | {b_f_mean:.4f} +/- {b_f_std:.4f} | {c_f_mean:.4f} +/- {c_f_std:.4f} | {record.fairness_delta_pct:+.2f}% | - | {'PASS' if record.fairness_delta_pct >= -5.0 else 'FAIL'} |",
            "",
            "## 3. Per-Iteration Measurement Ledger",
            "",
            "| Treatment | Iteration | Goodput (Mbps) | p50 Latency (ms) | p95 Latency (ms) | p99 Latency (ms) | Loss % | Retry Rate | Jain Fairness |",
            "|---|---|---|---|---|---|---|---|---|",
        ]

        # Interleave baseline and candidate according to treatment order if possible
        for s in base_samples:
            lines.append(
                f"| Baseline (A) | {s.iteration} | {s.aggregate_goodput_mbps:.2f} | "
                f"{s.p50_latency_ms:.2f} | {s.p95_latency_ms:.2f} | {s.p99_latency_ms:.2f} | "
                f"{s.packet_loss_pct:.2f}% | {s.retry_rate:.4f} | {s.jain_fairness_index:.4f} |"
            )
        for s in cand_samples:
            lines.append(
                f"| Candidate (B) | {s.iteration} | {s.aggregate_goodput_mbps:.2f} | "
                f"{s.p50_latency_ms:.2f} | {s.p95_latency_ms:.2f} | {s.p99_latency_ms:.2f} | "
                f"{s.packet_loss_pct:.2f}% | {s.retry_rate:.4f} | {s.jain_fairness_index:.4f} |"
            )

        lines.extend([
            "",
            "## 4. Configuration Snapshot",
            "```json",
            record.metadata.config_snapshot if isinstance(record.metadata.config_snapshot, str) else str(record.metadata.config_snapshot),
            "```",
            "",
            "---",
            "*Report automatically generated by FuturaMAX ReportGenerator conforming to AGENTS.md §7.*",
        ])

        return "\n".join(lines)

    @classmethod
    def save_report(cls, record: ExperimentResultRecord, out_path_md: Path) -> Path:
        """Saves markdown and JSON reports side-by-side."""
        out_path_md.parent.mkdir(parents=True, exist_ok=True)
        content_md = cls.generate_markdown(record)
        out_path_md.write_text(content_md, encoding="utf-8")

        # Save companion JSON
        out_path_json = out_path_md.with_suffix(".json")
        out_path_json.write_text(record.to_json(), encoding="utf-8")

        return out_path_md
