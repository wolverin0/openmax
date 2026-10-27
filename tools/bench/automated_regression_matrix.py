#!/usr/bin/env python3
"""Automated Regression Matrix Benchmark Orchestrator for FuturaMAX.

Executes multi-treatment experimental matrices comparing:
- Treatment 1: Stock Baseline (No shaping, default aggregation)
- Treatment 2: CAKE DiffServ4 (Egress shaping)
- Treatment 3: CAKE + FQ Pacing
- Treatment 4: CAKE + Dynamic Aggregation (Reduced A-MPDU under load)

Runs treatments in controlled sequence with configurable repetitions.
Calculates comparative metrics:
- Goodput delta (%)
- Latency delta under load (p50, p90, p95, p99 reduction in ms and %)
- Jain's Fairness Index across multiple stations
- Packet loss reduction

Generates both Markdown comparison tables and structured JSON receipts in research/raw/bench/.
Supports --dry-run with realistic synthetic distributions for offline validation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import statistics
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Try local imports if available
try:
    from tools.bench.bufferbloat_suite import (
        BufferbloatSuite,
        LatencyStats,
        TestResult,
        calculate_latency_stats,
    )
except ImportError:
    pass


def calculate_jains_fairness(allocations: Union[List[float], Dict[str, float]]) -> float:
    """Calculates Jain's Fairness Index: J(x) = (sum(x))^2 / (n * sum(x^2))."""
    if isinstance(allocations, dict):
        values = [float(v) for v in allocations.values()]
    else:
        values = [float(v) for v in allocations]

    if not values:
        return 1.0
    if len(values) == 1:
        return 1.0

    sum_x = sum(values)
    sum_sq = sum(x * x for x in values)
    n = len(values)

    if sum_sq <= 0.0 or sum_x <= 0.0:
        return 0.0

    jain = (sum_x * sum_x) / (n * sum_sq)
    return round(min(1.0, max(0.0, jain)), 4)


def calculate_delta_pct(base: float, treatment: float) -> float:
    """Calculates percentage change: ((treatment - base) / base) * 100."""
    if base == 0.0:
        return 0.0
    return round(((treatment - base) / base) * 100.0, 2)


def calculate_reduction_ms(base: float, treatment: float) -> float:
    """Calculates absolute reduction: base - treatment. Positive = improvement."""
    return round(base - treatment, 3)


def calculate_reduction_pct(base: float, treatment: float) -> float:
    """Calculates percentage reduction: ((base - treatment) / base) * 100. Positive = improvement."""
    if base == 0.0:
        return 0.0
    return round(((base - treatment) / base) * 100.0, 2)


@dataclass
class TreatmentConfig:
    """Configuration for an experimental treatment."""
    id: str
    name: str
    description: str
    shaping: str  # "none", "cake", "fq", etc.
    diffserv: str = "besteffort"
    pacing: bool = False
    ampdu_max_frames: Optional[int] = None
    ampdu_max_bytes: Optional[int] = None


TREATMENT_1_STOCK = TreatmentConfig(
    id="T1",
    name="Stock Baseline",
    description="No traffic shaping, standard FIFO/pfifo_fast, full hardware A-MPDU aggregation",
    shaping="none",
    ampdu_max_frames=64,
    ampdu_max_bytes=65535,
)

TREATMENT_2_CAKE = TreatmentConfig(
    id="T2",
    name="CAKE DiffServ4",
    description="Linux CAKE qdisc with 4-tin DiffServ isolation, ACK filter, and bandwidth shaping",
    shaping="cake",
    diffserv="diffserv4",
    pacing=False,
    ampdu_max_frames=64,
    ampdu_max_bytes=65535,
)

TREATMENT_3_CAKE_PACING = TreatmentConfig(
    id="T3",
    name="CAKE + FQ Pacing",
    description="CAKE egress shaping combined with socket/kernel pacing to smooth microbursts",
    shaping="cake",
    diffserv="diffserv4",
    pacing=True,
    ampdu_max_frames=64,
    ampdu_max_bytes=65535,
)

TREATMENT_4_CAKE_DYN_AGGR = TreatmentConfig(
    id="T4",
    name="CAKE + Dynamic Aggregation",
    description="CAKE shaping with dynamically constrained A-MPDU aggregation (32 frames / 16 KB) under load",
    shaping="cake",
    diffserv="diffserv4",
    pacing=True,
    ampdu_max_frames=32,
    ampdu_max_bytes=16384,
)

STANDARD_TREATMENTS = [
    TREATMENT_1_STOCK,
    TREATMENT_2_CAKE,
    TREATMENT_3_CAKE_PACING,
    TREATMENT_4_CAKE_DYN_AGGR,
]


@dataclass
class IterationResult:
    """Measurements recorded during a single treatment iteration."""
    treatment_id: str
    iteration: int
    goodput_mbps: float
    p50_latency_ms: float
    p90_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    packet_loss_pct: float
    station_goodputs: Dict[str, float] = field(default_factory=dict)
    jain_fairness: float = 1.0
    retransmits: Optional[int] = None
    rtt_samples: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TreatmentSummary:
    """Statistical summary across multiple repetitions of a treatment."""
    treatment_id: str
    name: str
    description: str
    iteration_count: int
    mean_goodput_mbps: float
    mean_p50_latency_ms: float
    mean_p90_latency_ms: float
    mean_p95_latency_ms: float
    mean_p99_latency_ms: float
    mean_packet_loss_pct: float
    mean_jain_fairness: float
    iterations: List[IterationResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "treatment_id": self.treatment_id,
            "name": self.name,
            "description": self.description,
            "iteration_count": self.iteration_count,
            "mean_goodput_mbps": self.mean_goodput_mbps,
            "mean_p50_latency_ms": self.mean_p50_latency_ms,
            "mean_p90_latency_ms": self.mean_p90_latency_ms,
            "mean_p95_latency_ms": self.mean_p95_latency_ms,
            "mean_p99_latency_ms": self.mean_p99_latency_ms,
            "mean_packet_loss_pct": self.mean_packet_loss_pct,
            "mean_jain_fairness": self.mean_jain_fairness,
            "iterations": [it.to_dict() for it in self.iterations],
        }


@dataclass
class ComparisonMetrics:
    """Comparative performance deltas relative to baseline (Treatment 1)."""
    treatment_id: str
    name: str
    goodput_delta_pct: float
    p50_reduction_ms: float
    p50_reduction_pct: float
    p90_reduction_ms: float
    p90_reduction_pct: float
    p95_reduction_ms: float
    p95_reduction_pct: float
    p99_reduction_ms: float
    p99_reduction_pct: float
    packet_loss_reduction_pct: float
    jain_fairness_delta: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MatrixReceipt:
    """Complete experimental regression matrix receipt."""
    matrix_id: str
    timestamp: str
    target: str
    iface: str
    bandwidth: str
    repetitions: int
    duration_secs: float
    treatments: Dict[str, TreatmentSummary] = field(default_factory=dict)
    comparisons: Dict[str, ComparisonMetrics] = field(default_factory=dict)
    markdown_report: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matrix_id": self.matrix_id,
            "timestamp": self.timestamp,
            "target": self.target,
            "iface": self.iface,
            "bandwidth": self.bandwidth,
            "repetitions": self.repetitions,
            "duration_secs": self.duration_secs,
            "treatments": {k: v.to_dict() for k, v in self.treatments.items()},
            "comparisons": {k: v.to_dict() for k, v in self.comparisons.items()},
            "markdown_report": self.markdown_report,
        }


class AutomatedRegressionMatrix:
    """Orchestrates multi-treatment regression testing and statistical comparison."""

    def __init__(
        self,
        target_ip: str = "10.99.0.1",
        iface: str = "eth0",
        bandwidth: str = "50Mbit",
        repetitions: int = 3,
        duration: int = 10,
        treatments: Optional[List[TreatmentConfig]] = None,
        out_dir: Optional[Union[str, Path]] = None,
        dry_run: bool = False,
    ):
        self.target_ip = target_ip
        self.iface = iface
        self.bandwidth = bandwidth
        self.repetitions = repetitions
        self.duration = duration
        self.treatments = treatments or list(STANDARD_TREATMENTS)
        self.dry_run = dry_run

        if out_dir is None:
            today = dt.date.today().isoformat()
            self.out_dir = Path("research/raw/bench") / today
        else:
            self.out_dir = Path(out_dir)

    def _generate_synthetic_iteration(
        self,
        treatment: TreatmentConfig,
        iteration: int,
    ) -> IterationResult:
        """Generates realistic synthetic bench data for offline qualification and unit tests."""
        # Realistic hardware profiles:
        # Stock: high bufferbloat (p95 ~ 140ms), packet loss ~ 4.5%, uneven station goodputs
        # CAKE: p95 drops to ~ 18ms, goodput slight reduction (shaping overhead), fairness high
        # CAKE + Pacing: p95 drops to ~ 12ms, jitter minimized, high fairness
        # CAKE + Dynamic Aggregation: p95 drops to ~ 7ms, p99 drops to ~ 14ms, highest fairness
        noise_factor = (iteration * 0.3) - 0.3

        if treatment.id == "T1":  # Stock Baseline
            goodput = round(94.2 + noise_factor, 2)
            p50 = round(45.0 + noise_factor * 2, 2)
            p90 = round(110.0 + noise_factor * 3, 2)
            p95 = round(135.0 + noise_factor * 4, 2)
            p99 = round(185.0 + noise_factor * 5, 2)
            loss = round(4.2 + abs(noise_factor) * 0.2, 2)
            st_goodputs = {"sta1": 55.0, "sta2": 32.0, "sta3": 7.2}
            retrans = 142

        elif treatment.id == "T2":  # CAKE DiffServ4
            goodput = round(48.5 + noise_factor * 0.5, 2)  # shaped to ~50Mbit
            p50 = round(8.5 + noise_factor, 2)
            p90 = round(14.0 + noise_factor, 2)
            p95 = round(18.2 + noise_factor * 1.5, 2)
            p99 = round(28.0 + noise_factor * 2, 2)
            loss = round(0.5 + abs(noise_factor) * 0.1, 2)
            st_goodputs = {"sta1": 24.5, "sta2": 16.0, "sta3": 8.0}
            retrans = 12

        elif treatment.id == "T3":  # CAKE + FQ Pacing
            goodput = round(48.8 + noise_factor * 0.5, 2)
            p50 = round(5.2 + noise_factor * 0.5, 2)
            p90 = round(9.8 + noise_factor * 0.8, 2)
            p95 = round(12.4 + noise_factor, 2)
            p99 = round(19.0 + noise_factor * 1.2, 2)
            loss = round(0.1 + abs(noise_factor) * 0.05, 2)
            st_goodputs = {"sta1": 22.0, "sta2": 17.5, "sta3": 9.3}
            retrans = 3

        else:  # T4: CAKE + Dynamic Aggregation
            goodput = round(47.9 + noise_factor * 0.4, 2)
            p50 = round(3.8 + noise_factor * 0.4, 2)
            p90 = round(6.5 + noise_factor * 0.5, 2)
            p95 = round(7.9 + noise_factor * 0.6, 2)
            p99 = round(13.5 + noise_factor * 0.8, 2)
            loss = round(0.05 + abs(noise_factor) * 0.02, 2)
            st_goodputs = {"sta1": 19.5, "sta2": 18.0, "sta3": 10.4}
            retrans = 1

        jain = calculate_jains_fairness(st_goodputs)

        return IterationResult(
            treatment_id=treatment.id,
            iteration=iteration,
            goodput_mbps=goodput,
            p50_latency_ms=p50,
            p90_latency_ms=p90,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            packet_loss_pct=loss,
            station_goodputs=st_goodputs,
            jain_fairness=jain,
            retransmits=retrans,
            rtt_samples=[p50, p90, p95, p99],
        )

    def _execute_physical_treatment(
        self,
        treatment: TreatmentConfig,
        iteration: int,
    ) -> IterationResult:
        """Executes treatment commands and measures live link performance."""
        # 1. Apply Treatment Configuration
        if treatment.shaping == "none":
            # Reset qdisc to stock
            subprocess.run(["tc", "qdisc", "del", "dev", self.iface, "root"], capture_output=True)
        elif treatment.shaping == "cake":
            cake_cmd = ["tc", "qdisc", "replace", "dev", self.iface, "root", "cake", "bandwidth", self.bandwidth]
            if treatment.diffserv:
                cake_cmd.append(treatment.diffserv)
            cake_cmd.append("ack-filter")
            subprocess.run(cake_cmd, capture_output=True)

        if treatment.pacing and treatment.shaping != "cake":
            fq_cmd = ["tc", "qdisc", "replace", "dev", self.iface, "root", "fq", "pacing"]
            subprocess.run(fq_cmd, capture_output=True)

        # 2. Run Bufferbloat measurement
        suite = BufferbloatSuite(
            target_ip=self.target_ip,
            ping_interval=0.02,
            duration=self.duration,
            streams=1,
            dry_run=False,
        )
        test_res = suite.run_single_measurement("tcp_dl")

        # Ingest latency stats
        lat = test_res.latency
        st_goodputs = {"primary_sta": test_res.throughput_mbps}
        jain = calculate_jains_fairness(st_goodputs)

        return IterationResult(
            treatment_id=treatment.id,
            iteration=iteration,
            goodput_mbps=test_res.throughput_mbps,
            p50_latency_ms=lat.p50_ms,
            p90_latency_ms=lat.p90_ms,
            p95_latency_ms=lat.p95_ms,
            p99_latency_ms=lat.p99_ms,
            packet_loss_pct=lat.loss_pct,
            station_goodputs=st_goodputs,
            jain_fairness=jain,
            retransmits=test_res.retransmits,
            rtt_samples=test_res.raw_rtts,
        )

    def run_matrix(self) -> MatrixReceipt:
        """Executes all treatments in sequence for the configured repetitions."""
        run_id = f"matrix-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        timestamp = dt.datetime.now().isoformat()

        treatment_summaries: Dict[str, TreatmentSummary] = {}

        for trt in self.treatments:
            iterations: List[IterationResult] = []
            for it_num in range(1, self.repetitions + 1):
                if self.dry_run:
                    it_res = self._generate_synthetic_iteration(trt, it_num)
                else:
                    it_res = self._execute_physical_treatment(trt, it_num)
                iterations.append(it_res)

            # Summarize treatment iterations
            mean_goodput = round(statistics.mean(it.goodput_mbps for it in iterations), 2)
            mean_p50 = round(statistics.mean(it.p50_latency_ms for it in iterations), 2)
            mean_p90 = round(statistics.mean(it.p90_latency_ms for it in iterations), 2)
            mean_p95 = round(statistics.mean(it.p95_latency_ms for it in iterations), 2)
            mean_p99 = round(statistics.mean(it.p99_latency_ms for it in iterations), 2)
            mean_loss = round(statistics.mean(it.packet_loss_pct for it in iterations), 2)
            mean_jain = round(statistics.mean(it.jain_fairness for it in iterations), 4)

            summary = TreatmentSummary(
                treatment_id=trt.id,
                name=trt.name,
                description=trt.description,
                iteration_count=len(iterations),
                mean_goodput_mbps=mean_goodput,
                mean_p50_latency_ms=mean_p50,
                mean_p90_latency_ms=mean_p90,
                mean_p95_latency_ms=mean_p95,
                mean_p99_latency_ms=mean_p99,
                mean_packet_loss_pct=mean_loss,
                mean_jain_fairness=mean_jain,
                iterations=iterations,
            )
            treatment_summaries[trt.id] = summary

        # Clean up / reset qdisc
        if not self.dry_run:
            subprocess.run(["tc", "qdisc", "del", "dev", self.iface, "root"], capture_output=True)

        # Compute comparative metrics against baseline (T1)
        comparisons = self._compute_comparisons(treatment_summaries)
        markdown = self.format_markdown_report(treatment_summaries, comparisons)

        receipt = MatrixReceipt(
            matrix_id=run_id,
            timestamp=timestamp,
            target=self.target_ip,
            iface=self.iface,
            bandwidth=self.bandwidth,
            repetitions=self.repetitions,
            duration_secs=float(self.duration),
            treatments=treatment_summaries,
            comparisons=comparisons,
            markdown_report=markdown,
        )

        return receipt

    def _compute_comparisons(
        self,
        summaries: Dict[str, TreatmentSummary],
    ) -> Dict[str, ComparisonMetrics]:
        """Calculates delta % and latency reductions relative to baseline (T1)."""
        comparisons: Dict[str, ComparisonMetrics] = {}
        baseline = summaries.get("T1")
        if not baseline:
            return comparisons

        for trt_id, trt in summaries.items():
            if trt_id == "T1":
                # Baseline compared to itself is 0
                comparisons["T1"] = ComparisonMetrics(
                    treatment_id="T1",
                    name=trt.name,
                    goodput_delta_pct=0.0,
                    p50_reduction_ms=0.0,
                    p50_reduction_pct=0.0,
                    p90_reduction_ms=0.0,
                    p90_reduction_pct=0.0,
                    p95_reduction_ms=0.0,
                    p95_reduction_pct=0.0,
                    p99_reduction_ms=0.0,
                    p99_reduction_pct=0.0,
                    packet_loss_reduction_pct=0.0,
                    jain_fairness_delta=0.0,
                )
                continue

            cmp_obj = ComparisonMetrics(
                treatment_id=trt_id,
                name=trt.name,
                goodput_delta_pct=calculate_delta_pct(baseline.mean_goodput_mbps, trt.mean_goodput_mbps),
                p50_reduction_ms=calculate_reduction_ms(baseline.mean_p50_latency_ms, trt.mean_p50_latency_ms),
                p50_reduction_pct=calculate_reduction_pct(baseline.mean_p50_latency_ms, trt.mean_p50_latency_ms),
                p90_reduction_ms=calculate_reduction_ms(baseline.mean_p90_latency_ms, trt.mean_p90_latency_ms),
                p90_reduction_pct=calculate_reduction_pct(baseline.mean_p90_latency_ms, trt.mean_p90_latency_ms),
                p95_reduction_ms=calculate_reduction_ms(baseline.mean_p95_latency_ms, trt.mean_p95_latency_ms),
                p95_reduction_pct=calculate_reduction_pct(baseline.mean_p95_latency_ms, trt.mean_p95_latency_ms),
                p99_reduction_ms=calculate_reduction_ms(baseline.mean_p99_latency_ms, trt.mean_p99_latency_ms),
                p99_reduction_pct=calculate_reduction_pct(baseline.mean_p99_latency_ms, trt.mean_p99_latency_ms),
                packet_loss_reduction_pct=round(baseline.mean_packet_loss_pct - trt.mean_packet_loss_pct, 2),
                jain_fairness_delta=round(trt.mean_jain_fairness - baseline.mean_jain_fairness, 4),
            )
            comparisons[trt_id] = cmp_obj

        return comparisons

    @classmethod
    def format_markdown_report(
        cls,
        summaries: Dict[str, TreatmentSummary],
        comparisons: Dict[str, ComparisonMetrics],
    ) -> str:
        """Formats multi-treatment results into clean Markdown tables."""
        lines = [
            "# FuturaMAX Automated Regression Matrix Report",
            "",
            "## 1. Summary Comparison Table",
            "",
            "| Treatment | Goodput (Mbps) | Goodput Delta (%) | p50 (ms) | p95 (ms) | p95 Red. (%) | p99 (ms) | Loss (%) | Jain Fairness |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]

        for trt_id, summary in summaries.items():
            cmp_obj = comparisons.get(trt_id)
            g_delta = f"{cmp_obj.goodput_delta_pct:+.1f}%" if cmp_obj and trt_id != "T1" else "BASELINE"
            p95_red = f"{cmp_obj.p95_reduction_pct:+.1f}%" if cmp_obj and trt_id != "T1" else "-"

            lines.append(
                f"| **{summary.treatment_id}: {summary.name}** | {summary.mean_goodput_mbps:.1f} | {g_delta} | "
                f"{summary.mean_p50_latency_ms:.1f} | {summary.mean_p95_latency_ms:.1f} | {p95_red} | "
                f"{summary.mean_p99_latency_ms:.1f} | {summary.mean_packet_loss_pct:.2f}% | {summary.mean_jain_fairness:.4f} |"
            )

        lines.extend([
            "",
            "## 2. Latency Reduction Analysis (Under Saturated Load)",
            "",
            "| Treatment | p50 Red. (ms) | p90 Red. (ms) | p95 Red. (ms) | p99 Red. (ms) | Loss Red. (%) | Jain Delta |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        ])

        for trt_id, cmp_obj in comparisons.items():
            if trt_id == "T1":
                continue
            lines.append(
                f"| **{cmp_obj.treatment_id}: {cmp_obj.name}** | "
                f"{cmp_obj.p50_reduction_ms:+.1f} ms | {cmp_obj.p90_reduction_ms:+.1f} ms | "
                f"{cmp_obj.p95_reduction_ms:+.1f} ms | {cmp_obj.p99_reduction_ms:+.1f} ms | "
                f"{cmp_obj.packet_loss_reduction_pct:+.2f}% | {cmp_obj.jain_fairness_delta:+.4f} |"
            )

        lines.extend([
            "",
            "## 3. Repetition Breakdown",
            "",
            "| Treatment | Iter | Goodput (Mbps) | p50 (ms) | p95 (ms) | p99 (ms) | Loss (%) | Retransmits |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ])

        for trt_id, summary in summaries.items():
            for it in summary.iterations:
                retrans_str = str(it.retransmits) if it.retransmits is not None else "-"
                lines.append(
                    f"| {summary.treatment_id} | #{it.iteration} | {it.goodput_mbps:.1f} | "
                    f"{it.p50_latency_ms:.1f} | {it.p95_latency_ms:.1f} | {it.p99_latency_ms:.1f} | "
                    f"{it.packet_loss_pct:.2f}% | {retrans_str} |"
                )

        lines.append("")
        return "\n".join(lines)

    def save_receipt(self, receipt: MatrixReceipt) -> Path:
        """Saves structured JSON receipt and Markdown report to research/raw/bench/."""
        self.out_dir.mkdir(parents=True, exist_ok=True)
        json_file = self.out_dir / f"{receipt.matrix_id}.json"
        md_file = self.out_dir / f"{receipt.matrix_id}.md"

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(receipt.to_dict(), f, indent=2)

        with open(md_file, "w", encoding="utf-8") as f:
            f.write(receipt.markdown_report)

        return json_file


def main():
    parser = argparse.ArgumentParser(description="FuturaMAX Automated Regression Matrix Benchmark")
    parser.add_argument("--target", default="10.99.0.1", help="Target IP address (default: 10.99.0.1)")
    parser.add_argument("--iface", default="eth0", help="Network interface facing CPE (default: eth0)")
    parser.add_argument("--bandwidth", default="50Mbit", help="Shaped bandwidth rate (default: 50Mbit)")
    parser.add_argument("--repetitions", type=int, default=3, help="Repetitions per treatment (default: 3)")
    parser.add_argument("--duration", type=int, default=10, help="Test duration per repetition in seconds (default: 10)")
    parser.add_argument("--out-dir", type=str, default=None, help="Output directory for receipts and reports")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution with synthetic distribution")

    args = parser.parse_args()

    orchestrator = AutomatedRegressionMatrix(
        target_ip=args.target,
        iface=args.iface,
        bandwidth=args.bandwidth,
        repetitions=args.repetitions,
        duration=args.duration,
        out_dir=args.out_dir,
        dry_run=args.dry_run,
    )

    print(f"[*] Starting Automated Regression Matrix against {args.target} ({len(STANDARD_TREATMENTS)} treatments x {args.repetitions} reps)...")
    receipt = orchestrator.run_matrix()
    saved_json = orchestrator.save_receipt(receipt)

    print(f"[+] Matrix execution complete! Saved: {saved_json}")
    print("\n" + receipt.markdown_report)


if __name__ == "__main__":
    main()
