"""Bounded ath10k-ct aggregation policy and offline C2 A/B/A/B plan.

Source: OpenWrt 24.10.4 ath10k-ct ac71b14d, ath10k-6.10 debug.c/htt_tx.c.
Reject original integers BEFORE the driver's unsigned-int -> u8 narrowing.
This module has no device adapter; a plan is never permission to execute it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from dataclasses import asdict, dataclass

from controller.airmax_wire import build_htt_type5_aggr_cfg, endian_swap_dword

SOURCE_COMMIT = "ac71b14dc93aef0af6f0f24808b0afb673eaa5f5"


@dataclass(frozen=True)
class AggregationPolicy:
    amsdu: int
    ampdu: int

    def __post_init__(self):
        for name, value, maximum in (("amsdu", self.amsdu, 31), ("ampdu", self.ampdu, 64)):
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError(f"{name} must be an integer in 1..{maximum}, before narrowing")

    def debugfs_value(self) -> str:
        # The external ABI order differs from the internal HTT function arguments.
        return f"{self.amsdu} {self.ampdu}\n"

    def to_htt_word(self) -> int:
        """Compile recommended aggregation limits into a 32-bit HTT Type 5 word.

        Format from UMAC_DATAPATH.md: tag 5 | (max_ampdu << 8) | (max_amsdu << 16).
        """
        return build_htt_type5_aggr_cfg(max_ampdu=self.ampdu, max_amsdu=self.amsdu)

    def to_htt_bytes(self, endian_swap: bool = False) -> bytes:
        """Serialize recommended aggregation limits into 4 bytes (big-endian or dword-swapped)."""
        word = self.to_htt_word()
        raw = struct.pack(">I", word)
        return endian_swap_dword(raw) if endian_swap else raw

    def to_htt_hex(self) -> str:
        """Format 32-bit HTT aggregation word as hexadecimal string."""
        return f"0x{self.to_htt_word():08x}"

    @classmethod
    def from_readback(cls, text: str):
        if not isinstance(text, str) or not re.fullmatch(r"[0-9]{1,3} [0-9]{1,3}\n?", text):
            raise ValueError("expected exactly AMSDU AMPDU decimal readback")
        amsdu, ampdu = map(int, text.split())
        return cls(amsdu, ampdu)


def prepare_plan(baseline: AggregationPolicy, candidate_ampdu: int, *, repeats: int = 3) -> dict:
    """One changed knob, repeated A/B/A/B, final restoration request; NO execution."""
    candidate = AggregationPolicy(baseline.amsdu, candidate_ampdu)
    if candidate.ampdu >= baseline.ampdu:
        raise ValueError("this lower-ceiling experiment requires candidate AMPDU below baseline")
    if type(repeats) is not int or not 3 <= repeats <= 20:
        raise ValueError("use 3..20 A/B/A/B blocks")
    rounds = [
        {"round": block + 1, "position": position + 1, "arm": arm,
         "policy": asdict(baseline if arm == "A" else candidate)}
        for block in range(repeats) for position, arm in enumerate("ABAB")
    ]
    immutable_protocol = {
        "experiment": "C2-aggregation-ampdu",
        "source_commit": SOURCE_COMMIT,
        "hypothesis": "A lower device-wide AMPDU ceiling may lower loaded p99 without material goodput loss.",
        "control_boundary": "ath10k-ct HTT device-wide subframe ceiling; target obedience unverified",
        "changed_knob": "ampdu",
        "unchanged": ["amsdu", "AQL", "rate policy", "channel", "width", "power", "topology", "offered load"],
        "objective_order": ["loaded_p99_ms", "loaded_p95_ms", "worst_client_fairness",
                            "goodput_per_mhz", "retry_airtime", "aggregate_goodput"],
        "reject_run_on": ["firmware recovery", "association loss", "unacceptable packet loss",
                          "watchdog", "CPU starvation", "memory pressure", "baseline drift"],
        "rounds": rounds,
        "restore_after_run_or_error": asdict(baseline),
    }
    fingerprint = hashlib.sha256(json.dumps(immutable_protocol, sort_keys=True,
                                           separators=(",", ":")).encode()).hexdigest()
    return {
        "schema_version": 1, "status": "PREPARED_NOT_RUN", "execution_authorized": False,
        "baseline_provenance": "caller supplied; live readback not verified by this planner",
        "protocol_sha256": fingerprint, "protocol": immutable_protocol,
        "required_before_execution": [
            "operator-authorized isolated lab run; current pause resolved",
            "exact board/image/driver/target firmware and feature fingerprint",
            "live aggregation readback plus verified restore/rollback",
            "attenuation or spacing satisfying BENCH_PLAN P0.3",
            "external traffic endpoints and measured CPU headroom",
            "frozen workload trace/duration and evaluator hash",
            "explicit numeric safety thresholds and baseline-repeat tolerance",
            "complete telemetry including p95/p99, per-client goodput, loss, resets, RAM and retries",
        ],
        "limits": "Only a validated policy/ordering fixture, not a complete executable bench or statistical acceptance.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-readback", required=True)
    parser.add_argument("--candidate-ampdu", type=int, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    print(json.dumps(prepare_plan(AggregationPolicy.from_readback(args.baseline_readback),
                                 args.candidate_ampdu, repeats=args.repeats), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
