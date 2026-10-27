"""Standard experiment metrics schema conforming to AGENTS.md §7 and Phase 0 Workstream D.

Summary: Enforces strict data models for PtMP experiment definitions, measurement samples,
and summary results. Eliminates the hard-coded 40 MHz bias in goodput_per_mhz by requiring
explicit channel_width_mhz validation across {5, 10, 20, 40, 80} MHz with deterministic
propagation from ExperimentMetadata and explicit legacy record migration helpers.
Keywords: AGENTS.md §7, metrics schema, channel_width_mhz, goodput_per_mhz, p99 latency, Jain fairness.
"""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

SUPPORTED_CHANNEL_WIDTHS_MHZ: Tuple[int, ...] = (5, 10, 20, 40, 80)


def validate_channel_width_mhz(channel_width_mhz: Optional[int]) -> int:
    """Validates that channel_width_mhz is an explicit supported integer width in {5, 10, 20, 40, 80}."""
    if channel_width_mhz is None or isinstance(channel_width_mhz, bool):
        raise ValueError(
            f"Missing channel_width_mhz: must be explicitly one of {SUPPORTED_CHANNEL_WIDTHS_MHZ}."
        )
    if not isinstance(channel_width_mhz, int) or channel_width_mhz not in SUPPORTED_CHANNEL_WIDTHS_MHZ:
        raise ValueError(
            f"Invalid channel_width_mhz={channel_width_mhz!r}: must be one of {SUPPORTED_CHANNEL_WIDTHS_MHZ}."
        )
    return channel_width_mhz


@dataclass
class ExperimentMetadata:
    experiment_id: str                      # e.g. "FMX-0013"
    hypothesis: str                         # e.g. "CoTSQ 6ms restores 802.11ac A-MPDU depth"
    hardware_revision: str                  # e.g. "LAP-120 (AR9342 rev 2 + QCA9880 hw2.0)"
    firmware_build_hash: str                # e.g. "openwrt-24.10.4-git-f4c2b9a"
    config_snapshot: Dict[str, Any]         # Complete JSON-serializable config parameters
    topology: str                           # e.g. "PtMP 1 AP + 20 CPEs (Hidden Nodes)"
    channel_mhz: int                        # e.g. 5180
    channel_width_mhz: int                  # Explicitly validated: 5, 10, 20, 40, or 80
    tx_power_dbm: float                     # e.g. 20.0
    attenuation_db: float                   # e.g. 45.0
    offered_load_profile: str               # e.g. "Saturated TCP Reverse (Uplink)"
    repetitions: int                        # e.g. 4 (A/B/A/B)
    treatment_order: List[str]              # e.g. ["A", "B", "A", "B"]
    rollback_condition: str                 # e.g. "p99 latency increases > 10% or goodput drops"

    def __post_init__(self) -> None:
        validate_channel_width_mhz(self.channel_width_mhz)
        if self.repetitions < 1:
            raise ValueError(f"repetitions must be >= 1, got {self.repetitions}")


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
    channel_width_mhz: Optional[int] = None
    width_source: str = "explicit"          # "explicit" | "metadata" | "legacy_migrated" | "unverified_missing_width"

    def __post_init__(self) -> None:
        if self.channel_width_mhz is not None:
            validate_channel_width_mhz(self.channel_width_mhz)
            expected_gpm = round(self.aggregate_goodput_mbps / float(self.channel_width_mhz), 4)
            if self.goodput_per_mhz == 0.0 and self.aggregate_goodput_mbps > 0:
                self.goodput_per_mhz = expected_gpm
            elif self.goodput_per_mhz > 0.0 and abs(self.goodput_per_mhz - expected_gpm) > 0.01:
                raise ValueError(
                    f"Inconsistent goodput_per_mhz={self.goodput_per_mhz} for "
                    f"aggregate_goodput_mbps={self.aggregate_goodput_mbps} at "
                    f"channel_width_mhz={self.channel_width_mhz} (expected {expected_gpm})."
                )
        else:
            # Never silently divide by 40.0 MHz when channel_width_mhz is omitted
            if self.goodput_per_mhz == 0.0 and self.width_source == "explicit":
                self.width_source = "unverified_missing_width"

        # Auto-compute Jain's Fairness Index if per-cpe goodput given
        if self.per_cpe_goodput_mbps and self.jain_fairness_index == 1.0:
            rates = list(self.per_cpe_goodput_mbps.values())
            n = len(rates)
            if n > 0:
                sum_x = sum(rates)
                sum_sq = sum(x * x for x in rates)
                if sum_sq > 0:
                    self.jain_fairness_index = round((sum_x ** 2) / (n * sum_sq), 4)

    def bind_channel_width(self, channel_width_mhz: int, source: str = "metadata") -> None:
        """Binds an authoritative channel width to this sample and computes goodput_per_mhz."""
        validate_channel_width_mhz(channel_width_mhz)
        if self.channel_width_mhz is not None and self.channel_width_mhz != channel_width_mhz:
            raise ValueError(
                f"Sample channel_width_mhz={self.channel_width_mhz} conflicts with "
                f"bound channel_width_mhz={channel_width_mhz}."
            )
        self.channel_width_mhz = channel_width_mhz
        self.width_source = source
        self.goodput_per_mhz = round(self.aggregate_goodput_mbps / float(channel_width_mhz), 4)

    def require_verified_width(self) -> int:
        """Ensures the sample has a verified channel width and returns it."""
        if self.channel_width_mhz is None or self.width_source == "unverified_missing_width":
            raise ValueError(
                "RunSample is missing a verified channel_width_mhz; pass channel_width_mhz explicitly "
                "or attach to an ExperimentResultRecord with validated ExperimentMetadata."
            )
        return validate_channel_width_mhz(self.channel_width_mhz)


@dataclass
class ExperimentResultRecord:
    metadata: ExperimentMetadata
    baseline_samples: List[RunSample] = field(default_factory=list)
    candidate_samples: List[RunSample] = field(default_factory=list)
    decision: str = "INCONCLUSIVE"          # "REJECT" | "INCONCLUSIVE" | "KEEP_FOR_REPLICATION" | "PROMOTE" | "KEEP"
    goodput_delta_pct: float = 0.0
    p99_latency_delta_pct: float = 0.0
    fairness_delta_pct: float = 0.0
    p_value_goodput: float = 1.0
    p_value_p99_latency: float = 1.0
    confidence_interval_95_goodput: Tuple[float, float] = (0.0, 0.0)
    rationale: str = ""

    def __post_init__(self) -> None:
        width = validate_channel_width_mhz(self.metadata.channel_width_mhz)
        for sample in self.baseline_samples + self.candidate_samples:
            if sample.channel_width_mhz is not None and sample.channel_width_mhz != width:
                raise ValueError(
                    f"Sample channel_width_mhz={sample.channel_width_mhz} conflicts with "
                    f"ExperimentMetadata.channel_width_mhz={width}."
                )
            source = sample.width_source if sample.channel_width_mhz == width and sample.width_source != "unverified_missing_width" else "metadata"
            sample.bind_channel_width(width, source=source)

    def to_json(self, indent: int = 2) -> str:
        """Serializes the experiment record to standard JSON."""
        return json.dumps(asdict(self), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> ExperimentResultRecord:
        """Deserializes from JSON string with strict channel_width_mhz validation."""
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

    @classmethod
    def from_legacy_json(
        cls,
        json_str: str,
        fallback_channel_width_mhz: Optional[int] = None,
    ) -> ExperimentResultRecord:
        """Loads a legacy JSON record that may have had 40 MHz hard-coded goodput_per_mhz."""
        raw = json.loads(json_str)
        migrated = migrate_legacy_record_dict(raw, fallback_channel_width_mhz=fallback_channel_width_mhz)
        return cls.from_json(json.dumps(migrated))


def migrate_legacy_record_dict(
    data: Dict[str, Any],
    fallback_channel_width_mhz: Optional[int] = None,
) -> Dict[str, Any]:
    """Migrates a legacy ExperimentResultRecord dict by recomputing goodput_per_mhz from metadata width."""
    out = copy.deepcopy(data)
    meta = out.get("metadata", {})
    width = meta.get("channel_width_mhz", fallback_channel_width_mhz)
    validate_channel_width_mhz(width)
    meta["channel_width_mhz"] = width
    out["metadata"] = meta

    for key in ("baseline_samples", "candidate_samples"):
        migrated_samples = []
        for sample in out.get(key, []):
            s = dict(sample)
            s["channel_width_mhz"] = width
            s["width_source"] = "legacy_migrated"
            gp = float(s.get("aggregate_goodput_mbps", 0.0))
            s["goodput_per_mhz"] = round(gp / float(width), 4)
            migrated_samples.append(s)
        out[key] = migrated_samples
    return out
