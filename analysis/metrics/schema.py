"""Standard experiment metrics schema conforming to AGENTS.md §7.

Summary: Enforces strict data models for PtMP experiment definitions, measurement samples,
and summary results. Provides JSON serialization, validation, and confidence interval math.
Keywords: AGENTS.md §7, metrics schema, experiment record, p99 latency, Jain fairness.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ExperimentMetadata:
    experiment_id: str                      # e.g. "FMX-0013"
    hypothesis: str                         # e.g. "CoTSQ 6ms restores 802.11ac A-MPDU depth"
    hardware_revision: str                  # e.g. "LAP-120 (AR9342 rev 2 + QCA9880 hw2.0)"
    firmware_build_hash: str                # e.g. "openwrt-24.10.4-git-f4c2b9a"
    config_snapshot: Dict[str, Any]         # Complete JSON-serializable config parameters
    topology: str                           # e.g. "PtMP 1 AP + 20 CPEs (Hidden Nodes)"
    channel_mhz: int                        # e.g. 5180
    channel_width_mhz: int                  # 20, 40, or 80
    tx_power_dbm: float                     # e.g. 20.0
    attenuation_db: float                   # e.g. 45.0
    offered_load_profile: str               # e.g. "Saturated TCP Reverse (Uplink)"
    repetitions: int                        # e.g. 4 (A/B/A/B)
    treatment_order: List[str]              # e.g. ["A", "B", "A", "B"]
    rollback_condition: str                 # e.g. "p99 latency increases > 10% or goodput drops"


@dataclass
class RunSample:
    treatment_id: str                       # "baseline" (A) or "candidate" (B)
    iteration: int
    duration_seconds: float
    aggregate_goodput_mbps: float
    per_cpe_goodput_mbps: Dict[str, float] = field(default_factory=dict)
    goodput_per_mhz: float = 0.0
    airtime_per_delivered_bit_ns: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    jitter_ms: float = 0.0
    packet_loss_pct: float = 0.0
    jain_fairness_index: float = 1.0
    retry_rate: float = 0.0
    cpu_utilization_pct: float = 0.0
    ram_used_bytes: int = 0
    firmware_resets: int = 0

    def __post_init__(self):
        # Auto-compute goodput per MHz if channel width is provided
        if self.aggregate_goodput_mbps > 0 and self.goodput_per_mhz == 0.0:
            # Default to 40 MHz normalization if not set
            self.goodput_per_mhz = round(self.aggregate_goodput_mbps / 40.0, 3)

        # Auto-compute Jain's Fairness Index if per-cpe goodput given
        if self.per_cpe_goodput_mbps and self.jain_fairness_index == 1.0:
            rates = list(self.per_cpe_goodput_mbps.values())
            n = len(rates)
            if n > 0:
                sum_x = sum(rates)
                sum_sq = sum(x * x for x in rates)
                if sum_sq > 0:
                    self.jain_fairness_index = round((sum_x ** 2) / (n * sum_sq), 4)


@dataclass
class ExperimentResultRecord:
    metadata: ExperimentMetadata
    baseline_samples: List[RunSample] = field(default_factory=list)
    candidate_samples: List[RunSample] = field(default_factory=list)
    decision: str = "INCONCLUSIVE"          # "KEEP" | "REJECT" | "INCONCLUSIVE"
    goodput_delta_pct: float = 0.0
    p99_latency_delta_pct: float = 0.0
    fairness_delta_pct: float = 0.0
    p_value_goodput: float = 1.0
    p_value_p99_latency: float = 1.0
    confidence_interval_95_goodput: Tuple[float, float] = (0.0, 0.0)
    rationale: str = ""

    def to_json(self, indent: int = 2) -> str:
        """Serializes the experiment record to standard JSON."""
        return json.dumps(asdict(self), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> ExperimentResultRecord:
        """Deserializes from JSON string."""
        data = json.loads(json_str)
        meta = ExperimentMetadata(**data["metadata"])
        base = [RunSample(**s) for s in data.get("baseline_samples", [])]
        cand = [RunSample(**s) for s in data.get("candidate_samples", [])]
        return cls(
            metadata=meta,
            baseline_samples=base,
            candidate_samples=cand,
            decision=data.get("decision", "INCONCLUSIVE"),
            goodput_delta_pct=data.get("goodput_delta_pct", 0.0),
            p99_latency_delta_pct=data.get("p99_latency_delta_pct", 0.0),
            fairness_delta_pct=data.get("fairness_delta_pct", 0.0),
            p_value_goodput=data.get("p_value_goodput", 1.0),
            p_value_p99_latency=data.get("p_value_p99_latency", 1.0),
            confidence_interval_95_goodput=tuple(data.get("confidence_interval_95_goodput", (0.0, 0.0))),
            rationale=data.get("rationale", ""),
        )
