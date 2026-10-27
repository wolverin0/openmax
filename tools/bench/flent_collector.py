#!/usr/bin/env python3
"""Flent & Netperf Ingestion and Parser for FuturaMAX.

Ingestion, normalization, and metrics extraction for Flent / RRUL test outputs:
- Reads .flent.gz (gzip-compressed JSON) and .flent / .json uncompressed files.
- Reads raw Netperf time-series logs (TCP_STREAM, TCP_RR, interval demo outputs).
- Extracts time-series RTT and throughput samples with statistics (p50, p90, p95, p99, loss).
- Converts to standard FuturaMAX BufferbloatResult and ExperimentMetric structures.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import logging
import math
import os
import re
import statistics
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Ensure repo root is available in sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.bench.bufferbloat_suite import (
    BufferbloatResult,
    LatencyStats,
    calculate_latency_stats,
    calculate_percentile,
    grade_bufferbloat,
)

logger = logging.getLogger("flent_collector")


@dataclass
class ExperimentMetric:
    """Standardized statistical representation of a benchmark metric series."""
    name: str
    unit: str
    samples: List[float] = field(default_factory=list)
    timestamps: List[float] = field(default_factory=list)
    sample_count: int = 0
    min_val: float = 0.0
    max_val: float = 0.0
    mean_val: float = 0.0
    median_val: float = 0.0
    p50: float = 0.0
    p90: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    stddev: float = 0.0
    loss_pct: float = 0.0

    @classmethod
    def from_samples(
        cls,
        name: str,
        unit: str,
        samples: List[Optional[float]],
        timestamps: Optional[List[float]] = None,
        total_expected: Optional[int] = None,
    ) -> ExperimentMetric:
        """Constructs an ExperimentMetric calculating all summary statistics."""
        valid_samples: List[float] = []
        valid_timestamps: List[float] = []

        raw_total = total_expected if total_expected is not None else len(samples)

        for i, val in enumerate(samples):
            if val is not None and not math.isnan(val):
                valid_samples.append(float(val))
                if timestamps is not None and i < len(timestamps):
                    valid_timestamps.append(float(timestamps[i]))
                else:
                    valid_timestamps.append(float(i))

        count = len(valid_samples)
        if count == 0:
            loss = 100.0 if raw_total > 0 else 0.0
            return cls(
                name=name,
                unit=unit,
                samples=[],
                timestamps=[],
                sample_count=0,
                loss_pct=loss,
            )

        sorted_vals = sorted(valid_samples)
        min_v = sorted_vals[0]
        max_v = sorted_vals[-1]
        mean_v = statistics.mean(valid_samples)
        median_v = statistics.median(valid_samples)
        std_v = statistics.stdev(valid_samples) if count > 1 else 0.0

        p50_v = calculate_percentile(sorted_vals, 50.0)
        p90_v = calculate_percentile(sorted_vals, 90.0)
        p95_v = calculate_percentile(sorted_vals, 95.0)
        p99_v = calculate_percentile(sorted_vals, 99.0)

        missing = max(0, raw_total - count)
        loss = round((missing / raw_total) * 100.0, 2) if raw_total > 0 else 0.0

        return cls(
            name=name,
            unit=unit,
            samples=valid_samples,
            timestamps=valid_timestamps,
            sample_count=count,
            min_val=round(min_v, 3),
            max_val=round(max_v, 3),
            mean_val=round(mean_v, 3),
            median_val=round(median_v, 3),
            p50=round(p50_v, 3),
            p90=round(p90_v, 3),
            p95=round(p95_v, 3),
            p99=round(p99_v, 3),
            stddev=round(std_v, 3),
            loss_pct=loss,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FlentDataset:
    """Parsed Flent dataset containing multi-series time-series telemetry."""
    title: str = "Flent Benchmark"
    test_name: str = "rrul"
    timestamp: str = ""
    duration_seconds: float = 0.0
    target_host: str = "unknown"
    metrics: Dict[str, ExperimentMetric] = field(default_factory=dict)
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def get_metric(self, name: str) -> Optional[ExperimentMetric]:
        """Finds metric by exact or partial name match (case-insensitive)."""
        if name in self.metrics:
            return self.metrics[name]
        lowered = name.lower()
        for k, v in self.metrics.items():
            if lowered in k.lower():
                return v
        return None

    def to_experiment_metrics(self) -> Dict[str, ExperimentMetric]:
        """Returns standard dictionary of experiment metrics."""
        return self.metrics

    def to_bufferbloat_result(
        self,
        target: Optional[str] = None,
        idle_baseline_ms: float = 0.0,
    ) -> BufferbloatResult:
        """Converts Flent / RRUL dataset into standard FuturaMAX BufferbloatResult."""
        target_name = target or self.target_host or "bench-target"

        # 1. Identify primary latency metric (ping_ipv4, ping, etc.)
        ping_metric = None
        for candidate in ["ping_ipv4", "ping", "rtt", "icmp", "tcp_rr"]:
            ping_metric = self.get_metric(candidate)
            if ping_metric and ping_metric.sample_count > 0:
                break

        # 2. Identify throughput metrics
        dl_metric = self.get_metric("download") or self.get_metric("tcp_download")
        ul_metric = self.get_metric("upload") or self.get_metric("tcp_upload")

        # Total goodput
        goodput = 0.0
        if dl_metric:
            goodput += dl_metric.mean_val
        if ul_metric and not dl_metric:
            goodput += ul_metric.mean_val

        # Compute LatencyStats
        if ping_metric and ping_metric.samples:
            total_sent = int(ping_metric.sample_count / (1.0 - (ping_metric.loss_pct / 100.0))) if ping_metric.loss_pct < 100 else ping_metric.sample_count
            lat_stats = calculate_latency_stats(
                rtts=ping_metric.samples,
                packets_sent=max(total_sent, ping_metric.sample_count),
                packets_recv=ping_metric.sample_count,
            )
            bloat_p50 = max(0.0, lat_stats.p50_ms - idle_baseline_ms)
            bloat_p95 = max(0.0, lat_stats.p95_ms - idle_baseline_ms)
            bloat_p99 = max(0.0, lat_stats.p99_ms - idle_baseline_ms)
            grade = grade_bufferbloat(bloat_p95)
        else:
            lat_stats = LatencyStats()
            bloat_p50, bloat_p95, bloat_p99 = None, None, None
            grade = "INCONCLUSIVE"

        # Direction determination
        if dl_metric and ul_metric:
            direction = "bidirectional"
        elif ul_metric:
            direction = "upload"
        else:
            direction = "download"

        return BufferbloatResult(
            timestamp=self.timestamp or dt.datetime.now().isoformat(),
            target=target_name,
            iperf_server=self.target_host,
            direction=direction,
            duration_s=self.duration_seconds,
            streams=len([k for k in self.metrics if "download" in k or "upload" in k]) or 1,
            goodput_mbps=round(goodput, 2) if goodput > 0.0 else None,
            retransmits=None,
            idle_stats=LatencyStats(p50_ms=idle_baseline_ms) if idle_baseline_ms > 0 else None,
            loaded_stats=lat_stats,
            bloat_p50_ms=round(bloat_p50, 2) if bloat_p50 is not None else None,
            bloat_p95_ms=round(bloat_p95, 2) if bloat_p95 is not None else None,
            bloat_p99_ms=round(bloat_p99, 2) if bloat_p99 is not None else None,
            grade=grade,
            metadata={
                "flent_title": self.title,
                "test_name": self.test_name,
                "metrics_count": len(self.metrics),
                "raw_metadata": self.raw_metadata,
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "test_name": self.test_name,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "target_host": self.target_host,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "raw_metadata": self.raw_metadata,
        }

    def format_summary_markdown(self) -> str:
        """Emits readable markdown summary table of all extracted metrics."""
        lines = [
            f"# Flent / RRUL Dataset: {self.title}",
            f"- **Test Name**: `{self.test_name}`",
            f"- **Target Host**: `{self.target_host}`",
            f"- **Duration**: `{self.duration_seconds:.1f}s`",
            f"- **Timestamp**: `{self.timestamp}`",
            "",
            "| Metric Series | Unit | Samples | p50 | p90 | p95 | p99 | Mean | Max | Loss % |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]
        for name, m in sorted(self.metrics.items()):
            lines.append(
                f"| `{name}` | {m.unit} | {m.sample_count} | {m.p50:.2f} | {m.p90:.2f} | "
                f"{m.p95:.2f} | {m.p99:.2f} | {m.mean_val:.2f} | {m.max_val:.2f} | {m.loss_pct:.1f}% |"
            )
        lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Parsers: Flent JSON / GZIP
# ---------------------------------------------------------------------------

def _extract_series_samples(series_data: Any) -> Tuple[List[Optional[float]], List[float]]:
    """Normalizes various Flent raw series structures into (samples, timestamps)."""
    samples: List[Optional[float]] = []
    timestamps: List[float] = []

    if isinstance(series_data, list):
        for idx, item in enumerate(series_data):
            if item is None:
                samples.append(None)
                timestamps.append(float(idx))
            elif isinstance(item, (int, float)):
                samples.append(float(item))
                timestamps.append(float(idx))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                # [timestamp, value]
                t, v = item[0], item[1]
                timestamps.append(float(t) if t is not None else float(idx))
                samples.append(float(v) if v is not None else None)
    elif isinstance(series_data, dict):
        x = series_data.get("x", [])
        y = series_data.get("y", [])
        for idx, v in enumerate(y):
            samples.append(float(v) if v is not None else None)
            t = x[idx] if idx < len(x) else float(idx)
            timestamps.append(float(t) if t is not None else float(idx))

    return samples, timestamps


def parse_flent_content(content: Union[str, bytes]) -> FlentDataset:
    """Parses decompressed JSON or raw bytes into a FlentDataset."""
    if isinstance(content, bytes):
        # Check if gzip-compressed
        if content.startswith(b"\x1f\x8b"):
            try:
                content = gzip.decompress(content).decode("utf-8", errors="replace")
            except Exception as e:
                logger.error("Failed to decompress gzip content: %s", e)
                raise
        else:
            content = content.decode("utf-8", errors="replace")

    data = json.loads(content)

    meta = data.get("METADATA", {})
    raw_values = data.get("RAW_VALUES", {})
    results = data.get("RESULTS", {})

    title = meta.get("TITLE") or meta.get("NAME") or "Flent Benchmark"
    test_name = meta.get("NAME") or meta.get("TITLE") or "rrul"
    ts = str(meta.get("TIME") or dt.datetime.now().isoformat())
    target_host = meta.get("HOST") or "unknown"
    duration = float(meta.get("TOTAL_LENGTH") or meta.get("DURATION") or 0.0)

    # If duration is 0, estimate from X_VALUES or longest raw values series
    x_vals = data.get("X_VALUES")
    if duration == 0.0 and x_vals and isinstance(x_vals, list) and len(x_vals) > 1:
        try:
            duration = float(x_vals[-1]) - float(x_vals[0])
        except Exception:
            pass

    metrics: Dict[str, ExperimentMetric] = {}

    # 1. Parse RAW_VALUES
    for series_name, series_raw in raw_values.items():
        samples, timestamps = _extract_series_samples(series_raw)
        if not samples:
            continue

        # Determine unit
        unit = "value"
        s_lower = series_name.lower()
        if "ping" in s_lower or "rtt" in s_lower or "delay" in s_lower or "latency" in s_lower:
            unit = "ms"
        elif "download" in s_lower or "upload" in s_lower or "throughput" in s_lower or "bandwidth" in s_lower:
            unit = "Mbps"
            # Auto-detect if raw values are bits/sec (e.g. > 10,000)
            valid_nums = [s for s in samples if s is not None]
            if valid_nums and statistics.mean(valid_nums) > 10000.0:
                samples = [(s / 1e6 if s is not None else None) for s in samples]

        metric = ExperimentMetric.from_samples(
            name=series_name,
            unit=unit,
            samples=samples,
            timestamps=timestamps,
        )
        metrics[series_name] = metric

    # 2. Check RESULTS if RAW_VALUES was empty
    if not metrics and isinstance(results, dict):
        for series_name, series_raw in results.items():
            samples, timestamps = _extract_series_samples(series_raw)
            if samples:
                unit = "ms" if "ping" in series_name.lower() else "Mbps"
                metrics[series_name] = ExperimentMetric.from_samples(
                    name=series_name,
                    unit=unit,
                    samples=samples,
                    timestamps=timestamps,
                )

    # If duration still 0, derive from timestamps of first metric
    if duration == 0.0 and metrics:
        first_m = next(iter(metrics.values()))
        if first_m.timestamps and len(first_m.timestamps) > 1:
            duration = max(first_m.timestamps) - min(first_m.timestamps)

    return FlentDataset(
        title=title,
        test_name=test_name,
        timestamp=ts,
        duration_seconds=duration,
        target_host=target_host,
        metrics=metrics,
        raw_metadata=meta,
    )


def parse_flent_file(file_path: Union[str, Path]) -> FlentDataset:
    """Reads a .flent.gz or .flent / .json file from disk and parses it."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Flent file not found: {path}")

    # Read binary header to check for gzip magic
    with open(path, "rb") as f:
        header = f.read(2)

    if header == b"\x1f\x8b" or str(path).endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
            content = f.read()
    else:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

    return parse_flent_content(content)


# ---------------------------------------------------------------------------
# Parsers: Raw Netperf Logs
# ---------------------------------------------------------------------------

def parse_netperf_log(
    log_text: str,
    metric_name: str = "netperf_throughput",
) -> ExperimentMetric:
    """Parses raw Netperf text logs into an ExperimentMetric.

    Supports:
    1. Standard TCP_STREAM output (Recv/Send Socket Size ... 10^6bits/sec).
    2. TCP_RR output (Request/Resp Size ... Trans. Rate per sec).
    3. Netperf interval time-series (CSV / tabular lines e.g. '0.50, 48.52').
    4. Omni output (THROUGHPUT=48.52).
    """
    lines = [line.strip() for line in log_text.splitlines() if line.strip()]
    samples: List[float] = []
    timestamps: List[float] = []
    unit = "Mbps"

    # Pattern 1: Time-series lines (e.g. "0.50, 48.52" or "0.50 48.52")
    ts_pattern = re.compile(r"^(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)$")

    for line in lines:
        m = ts_pattern.match(line)
        if m:
            t = float(m.group(1))
            val = float(m.group(2))
            timestamps.append(t)
            samples.append(val)

    if samples:
        return ExperimentMetric.from_samples(
            name=metric_name,
            unit=unit,
            samples=samples,
            timestamps=timestamps,
        )

    # Pattern 2: Omni format (THROUGHPUT=XX.XX)
    m_omni = re.search(r"THROUGHPUT=(\d+(?:\.\d+)?)", log_text)
    if m_omni:
        val = float(m_omni.group(1))
        return ExperimentMetric.from_samples(
            name=metric_name,
            unit=unit,
            samples=[val],
            timestamps=[0.0],
        )

    # Pattern 3: Standard TCP_STREAM summary banner
    # Recv Socket Size ... 10^6bits/sec
    #  87380  16384  16384    10.00      48.52
    if "10^6bits/sec" in log_text or "Throughput" in log_text:
        # Search for the numeric line after header
        for line in reversed(lines):
            tokens = line.split()
            if len(tokens) == 5:
                try:
                    # Last token is throughput in 10^6bits/sec (Mbps)
                    tp = float(tokens[4])
                    elapsed = float(tokens[3])
                    return ExperimentMetric.from_samples(
                        name=metric_name,
                        unit="Mbps",
                        samples=[tp],
                        timestamps=[elapsed],
                    )
                except ValueError:
                    continue

    # Pattern 4: TCP_RR (Request/Response)
    # Trans. Rate per sec
    if "Trans. Rate" in log_text or "per sec" in log_text:
        for line in reversed(lines):
            tokens = line.split()
            if len(tokens) >= 5:
                try:
                    rate = float(tokens[-1])
                    elapsed = float(tokens[-2])
                    # TCP_RR rate in transactions/sec can be converted to avg RTT (1000 / rate ms)
                    rtt_ms = round(1000.0 / rate, 2) if rate > 0 else 0.0
                    return ExperimentMetric.from_samples(
                        name="tcp_rr_rtt",
                        unit="ms",
                        samples=[rtt_ms],
                        timestamps=[elapsed],
                    )
                except ValueError:
                    continue

    # Fallback: scan for any floating number on lines by itself
    for line in lines:
        try:
            num = float(line)
            samples.append(num)
            timestamps.append(float(len(samples)))
        except ValueError:
            pass

    return ExperimentMetric.from_samples(
        name=metric_name,
        unit=unit,
        samples=samples,
        timestamps=timestamps,
    )


def parse_netperf_file(
    file_path: Union[str, Path],
    metric_name: str = "netperf_throughput",
) -> ExperimentMetric:
    """Reads a Netperf output text file and parses into ExperimentMetric."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Netperf file not found: {path}")

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    return parse_netperf_log(text, metric_name=metric_name)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="FuturaMAX Flent & Netperf Ingestion and Parser")
    parser.add_argument("file", help="Path to .flent.gz, .flent, .json, or netperf log file")
    parser.add_argument("--json", action="store_true", help="Output parsed dataset as JSON")
    parser.add_argument("--export-bloat", type=str, default=None, help="Export BufferbloatResult JSON to path")
    parser.add_argument("--target", type=str, default=None, help="Target device name / IP")
    parser.add_argument("--idle-baseline-ms", type=float, default=0.0, help="Idle baseline latency in ms")

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        # Check if Netperf text or Flent dataset
        if file_path.suffix in [".gz", ".json", ".flent"]:
            ds = parse_flent_file(file_path)
            bloat = ds.to_bufferbloat_result(target=args.target, idle_baseline_ms=args.idle_baseline_ms)

            if args.json:
                print(json.dumps(ds.to_dict(), indent=2))
            else:
                print(ds.format_summary_markdown())
                print(f"[+] Bufferbloat Grade: {bloat.grade}")
                if bloat.goodput_mbps:
                    print(f"[+] Total Goodput: {bloat.goodput_mbps:.2f} Mbps")
                if bloat.loaded_stats:
                    print(f"[+] Loaded Latency: p50={bloat.loaded_stats.p50_ms:.2f}ms, p95={bloat.loaded_stats.p95_ms:.2f}ms")

            if args.export_bloat:
                out_p = Path(args.export_bloat)
                out_p.parent.mkdir(parents=True, exist_ok=True)
                with open(out_p, "w", encoding="utf-8") as f:
                    json.dump(bloat.to_dict(), f, indent=2)
                print(f"[+] Saved BufferbloatResult to {out_p}")

        else:
            # Assume Netperf log text
            metric = parse_netperf_file(file_path)
            if args.json:
                print(json.dumps(metric.to_dict(), indent=2))
            else:
                print(f"Metric: {metric.name} ({metric.unit})")
                print(f"Samples: {metric.sample_count} | Mean: {metric.mean_val:.2f} | p95: {metric.p95:.2f}")

    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
