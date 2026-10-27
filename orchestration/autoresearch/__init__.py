"""FuturaMAX Karpathy-style autoresearch harness + scholar-mcp integration."""

from orchestration.autoresearch.fmx_autoresearch_harness import (
    AutoresearchDecision,
    BenchmarkObservation,
    FmxAutoresearchHarness,
    MutableWirelessPolicy,
    ObjectiveConfig,
    ObjectiveEvaluation,
    ResultsLedger,
    ResultsRow,
    compute_fmx_objective,
    compute_pareto_frontier,
    ground_hypothesis_with_scholar,
)

__all__ = [
    "AutoresearchDecision",
    "BenchmarkObservation",
    "FmxAutoresearchHarness",
    "MutableWirelessPolicy",
    "ObjectiveConfig",
    "ObjectiveEvaluation",
    "ResultsLedger",
    "ResultsRow",
    "compute_fmx_objective",
    "compute_pareto_frontier",
    "ground_hypothesis_with_scholar",
]
