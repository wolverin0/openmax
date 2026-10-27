"""
FuturaMAX Karpathy-style Autoresearch Harness + Scholar-MCP Grounding.

Adapts https://github.com/karpathy/autoresearch (program.md + immutable evaluator +
single mutable policy surface + results.tsv keep/discard/crash loop) and
https://github.com/handsome-rich/Awesome-Auto-Research-Tools to FuturaMAX's
hardware-verified wireless bench constraints (AGENTS.md Sections 4, 7, 12.1-12.3).
"""

from __future__ import annotations

import csv
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class AutoresearchDecision(str, Enum):
    KEEP = "keep"
    DISCARD = "discard"
    CRASH = "crash"


@dataclass(frozen=True)
class MutableWirelessPolicy:
    """
    Single mutable surface for an autoresearch iteration (the 'train.py' equivalent).
    All parameters are strictly RAM-only runtime knobs on OpenWrt mac80211/ath10k/tc
    or Stock airOS hybrid interfaces. Flash, ART/calibration, and regulatory/DFS knobs
    are excluded by construction.
    """

    policy_id: str = "baseline"
    description: str = "stock baseline policy"
    aql_txq_limit_ac_be_kb: int = 24000
    aql_threshold_kb: int = 24000
    codel_target_ms: float = 5.0
    codel_interval_ms: float = 100.0
    cake_bandwidth_mbps: Optional[float] = None
    rts_threshold_bytes: int = 2347
    coverage_class: int = 0
    vht_mcs_max_index: int = 9
    complexity_cost: int = 0

    def validate_bounds(self) -> List[str]:
        """Validate that the policy stays within safe RAM-only hardware bounds."""
        errors: List[str] = []
        if not (512 <= self.aql_txq_limit_ac_be_kb <= 65536):
            errors.append(
                f"aql_txq_limit_ac_be_kb={self.aql_txq_limit_ac_be_kb} outside [512, 65536]"
            )
        if not (512 <= self.aql_threshold_kb <= 65536):
            errors.append(
                f"aql_threshold_kb={self.aql_threshold_kb} outside [512, 65536]"
            )
        if not (1.0 <= self.codel_target_ms <= 50.0):
            errors.append(
                f"codel_target_ms={self.codel_target_ms} outside [1.0, 50.0]"
            )
        if not (10.0 <= self.codel_interval_ms <= 500.0):
            errors.append(
                f"codel_interval_ms={self.codel_interval_ms} outside [10.0, 500.0]"
            )
        if self.cake_bandwidth_mbps is not None and not (1.0 <= self.cake_bandwidth_mbps <= 1000.0):
            errors.append(
                f"cake_bandwidth_mbps={self.cake_bandwidth_mbps} outside [1.0, 1000.0]"
            )
        if not (64 <= self.rts_threshold_bytes <= 2347):
            errors.append(
                f"rts_threshold_bytes={self.rts_threshold_bytes} outside [64, 2347]"
            )
        if not (0 <= self.coverage_class <= 31):
            errors.append(
                f"coverage_class={self.coverage_class} outside [0, 31]"
            )
        if not (0 <= self.vht_mcs_max_index <= 9):
            errors.append(
                f"vht_mcs_max_index={self.vht_mcs_max_index} outside [0, 9] (802.11ac ceiling)"
            )
        return errors


@dataclass(frozen=True)
class BenchmarkObservation:
    """
    Immutable measurement output from a fixed-duration bench run.
    """

    goodput_rx_mbps: float
    p50_rtt_ms: float
    p95_rtt_ms: float
    p99_rtt_ms: float
    packet_loss_pct: float = 0.0
    jain_fairness: float = 1.0
    retry_rate: float = 0.0
    station_drops: int = 0
    restoration_verified: bool = True
    repetitions: int = 3


@dataclass(frozen=True)
class ObjectiveConfig:
    """
    Immutable evaluation configuration ('prepare.py' equivalent).
    Defines target normalization constants and hard safety/latency gates.
    """

    target_goodput_mbps: float = 80.0
    baseline_rtt_ms: float = 5.0
    rtt_budget_ms: float = 25.0
    max_p99_rtt_ms: float = 150.0
    max_packet_loss_pct: float = 2.0
    min_repetitions: int = 1
    min_improvement_delta: float = 0.002
    weight_throughput: float = 0.45
    weight_p95_rtt: float = 0.25
    weight_p99_rtt: float = 0.15
    weight_fairness: float = 0.10
    weight_retries: float = 0.05


@dataclass(frozen=True)
class ObjectiveEvaluation:
    """Result of evaluating a BenchmarkObservation against ObjectiveConfig."""

    fmx_loss: float
    decision: AutoresearchDecision
    reason: str
    disqualified: bool
    components: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ResultsRow:
    """Single row in Karpathy-style results.tsv."""

    commit: str
    fmx_loss: float
    goodput_mbps: float
    p95_rtt_ms: float
    jain_fairness: float
    status: str
    description: str


def compute_fmx_objective(
    obs: BenchmarkObservation,
    config: ObjectiveConfig = ObjectiveConfig(),
    best_fmx_loss: Optional[float] = None,
    candidate_complexity: int = 0,
    incumbent_complexity: int = 0,
) -> ObjectiveEvaluation:
    """
    Immutable scalar objective evaluator (lower fmx_loss is better, analogous to val_bpb).
    Enforces hard safety/restoration/tail-latency gates before comparing fmx_loss.
    """
    values = [
        obs.goodput_rx_mbps,
        obs.p50_rtt_ms,
        obs.p95_rtt_ms,
        obs.p99_rtt_ms,
        obs.packet_loss_pct,
        obs.jain_fairness,
        obs.retry_rate,
    ]
    if any(not math.isfinite(v) for v in values):
        return ObjectiveEvaluation(
            fmx_loss=float("inf"),
            decision=AutoresearchDecision.CRASH,
            reason="Non-finite telemetry metric observed",
            disqualified=True,
        )

    if not obs.restoration_verified:
        return ObjectiveEvaluation(
            fmx_loss=float("inf"),
            decision=AutoresearchDecision.CRASH,
            reason="Post-run baseline restoration verification failed",
            disqualified=True,
        )

    if obs.station_drops > 0:
        return ObjectiveEvaluation(
            fmx_loss=float("inf"),
            decision=AutoresearchDecision.CRASH,
            reason=f"Station dropped during treatment ({obs.station_drops} drops)",
            disqualified=True,
        )

    if obs.goodput_rx_mbps <= 0.0:
        return ObjectiveEvaluation(
            fmx_loss=float("inf"),
            decision=AutoresearchDecision.CRASH,
            reason=f"Zero/negative receiver goodput ({obs.goodput_rx_mbps} Mbps)",
            disqualified=True,
        )

    if obs.repetitions < config.min_repetitions:
        return ObjectiveEvaluation(
            fmx_loss=float("inf"),
            decision=AutoresearchDecision.DISCARD,
            reason=f"Insufficient repetitions ({obs.repetitions} < {config.min_repetitions})",
            disqualified=True,
        )

    # Compute scalar fmx_loss (lower is better)
    tput_deficit = max(0.0, 1.0 - (obs.goodput_rx_mbps / max(1e-6, config.target_goodput_mbps)))
    p95_excess = max(0.0, obs.p95_rtt_ms - config.baseline_rtt_ms) / max(1e-6, config.rtt_budget_ms)
    p99_excess = max(0.0, obs.p99_rtt_ms - config.baseline_rtt_ms) / max(1e-6, config.rtt_budget_ms)
    unfairness = max(0.0, min(1.0, 1.0 - obs.jain_fairness))
    retry_penalty = max(0.0, min(1.0, obs.retry_rate))

    fmx_loss = round(
        config.weight_throughput * tput_deficit
        + config.weight_p95_rtt * p95_excess
        + config.weight_p99_rtt * p99_excess
        + config.weight_fairness * unfairness
        + config.weight_retries * retry_penalty,
        6,
    )

    components = {
        "tput_deficit": round(tput_deficit, 6),
        "p95_excess": round(p95_excess, 6),
        "p99_excess": round(p99_excess, 6),
        "unfairness": round(unfairness, 6),
        "retry_penalty": round(retry_penalty, 6),
    }

    # Hard tail-latency & packet-loss regression gates (AGENTS.md Section 4)
    if obs.packet_loss_pct > config.max_packet_loss_pct:
        return ObjectiveEvaluation(
            fmx_loss=fmx_loss,
            decision=AutoresearchDecision.DISCARD,
            reason=(
                f"Packet loss {obs.packet_loss_pct:.2f}% exceeds gate "
                f"{config.max_packet_loss_pct:.2f}%"
            ),
            disqualified=True,
            components=components,
        )

    if obs.p99_rtt_ms > config.max_p99_rtt_ms:
        return ObjectiveEvaluation(
            fmx_loss=fmx_loss,
            decision=AutoresearchDecision.DISCARD,
            reason=(
                f"p99 RTT {obs.p99_rtt_ms:.2f} ms exceeds tail-latency gate "
                f"{config.max_p99_rtt_ms:.2f} ms"
            ),
            disqualified=True,
            components=components,
        )

    if best_fmx_loss is None:
        return ObjectiveEvaluation(
            fmx_loss=fmx_loss,
            decision=AutoresearchDecision.KEEP,
            reason="Initial baseline established",
            disqualified=False,
            components=components,
        )

    improvement = best_fmx_loss - fmx_loss
    if improvement >= config.min_improvement_delta:
        return ObjectiveEvaluation(
            fmx_loss=fmx_loss,
            decision=AutoresearchDecision.KEEP,
            reason=f"Improved fmx_loss by {improvement:.6f} ({best_fmx_loss:.6f} -> {fmx_loss:.6f})",
            disqualified=False,
            components=components,
        )

    # Simplicity criterion from Karpathy's program.md: equal performance + simpler is a KEEP
    if abs(improvement) < config.min_improvement_delta and candidate_complexity < incumbent_complexity:
        return ObjectiveEvaluation(
            fmx_loss=fmx_loss,
            decision=AutoresearchDecision.KEEP,
            reason=(
                f"Tied fmx_loss ({fmx_loss:.6f}) with lower complexity "
                f"({candidate_complexity} < {incumbent_complexity})"
            ),
            disqualified=False,
            components=components,
        )

    return ObjectiveEvaluation(
        fmx_loss=fmx_loss,
        decision=AutoresearchDecision.DISCARD,
        reason=(
            f"Did not improve fmx_loss sufficiently "
            f"(candidate {fmx_loss:.6f} vs best {best_fmx_loss:.6f})"
        ),
        disqualified=False,
        components=components,
    )


class ResultsLedger:
    """
    Manages the Karpathy-style tab-separated results.tsv file.
    Columns: commit, fmx_loss, goodput_mbps, p95_rtt_ms, jain_fairness, status, description
    """

    HEADERS = [
        "commit",
        "fmx_loss",
        "goodput_mbps",
        "p95_rtt_ms",
        "jain_fairness",
        "status",
        "description",
    ]

    def __init__(self, tsv_path: Path):
        self.tsv_path = Path(tsv_path)
        self.tsv_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.tsv_path.exists():
            with self.tsv_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerow(self.HEADERS)

    def append(self, row: ResultsRow) -> None:
        clean_desc = row.description.replace("\t", " ").replace("\n", " ").strip()
        loss_str = f"{row.fmx_loss:.6f}" if math.isfinite(row.fmx_loss) else "0.000000"
        with self.tsv_path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(
                [
                    row.commit,
                    loss_str,
                    f"{row.goodput_mbps:.2f}",
                    f"{row.p95_rtt_ms:.2f}",
                    f"{row.jain_fairness:.4f}",
                    row.status,
                    clean_desc,
                ]
            )

    def read_all(self) -> List[ResultsRow]:
        if not self.tsv_path.exists():
            return []
        rows: List[ResultsRow] = []
        with self.tsv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for r in reader:
                rows.append(
                    ResultsRow(
                        commit=r["commit"],
                        fmx_loss=float(r["fmx_loss"]),
                        goodput_mbps=float(r["goodput_mbps"]),
                        p95_rtt_ms=float(r["p95_rtt_ms"]),
                        jain_fairness=float(r["jain_fairness"]),
                        status=r["status"],
                        description=r["description"],
                    )
                )
        return rows


class FmxAutoresearchHarness:
    """
    Stateful Karpathy-style autoresearch loop controller for FuturaMAX.
    Tracks the incumbent policy, evaluates candidate policies via an injected
    immutable runner, logs every run to results.tsv, and automatically reverts
    to the incumbent policy on DISCARD or CRASH.
    """

    def __init__(
        self,
        tsv_path: Path,
        config: ObjectiveConfig = ObjectiveConfig(),
        initial_policy: Optional[MutableWirelessPolicy] = None,
        auto_sync_pillars: bool = True,
    ):
        self.ledger = ResultsLedger(tsv_path)
        self.config = config
        self.incumbent_policy: MutableWirelessPolicy = initial_policy or MutableWirelessPolicy()
        self.best_fmx_loss: Optional[float] = None
        self.history: List[Dict[str, Any]] = []
        self.auto_sync_pillars: bool = auto_sync_pillars

    def _emit_to_memorymaster_and_reactor(
        self,
        commit_tag: str,
        candidate_policy: MutableWirelessPolicy,
        obs: BenchmarkObservation,
        eval_res: ObjectiveEvaluation,
    ) -> None:
        """Deterministically emit KEEP iterations into ClosedLoopResearchReactor & MemoryMaster."""
        if not self.auto_sync_pillars or eval_res.decision != AutoresearchDecision.KEEP:
            return
        summary = (
            f"Autoresearch KEEP {commit_tag} ({candidate_policy.policy_id}): "
            f"goodput={obs.goodput_rx_mbps:.2f} Mbps, p95={obs.p95_rtt_ms:.2f} ms, "
            f"p99={obs.p99_rtt_ms:.2f} ms, fmx_loss={eval_res.fmx_loss:.6f} ({eval_res.reason})"
        )
        try:
            from tools.research.closed_loop_research_reactor import ClosedLoopResearchReactor

            reactor = ClosedLoopResearchReactor()
            reactor.enqueue_discovery(
                stage_id=f"AUTORESEARCH-{commit_tag}",
                hardware_domain="OpenWrt/airMAX/LTU",
                observation=summary,
                attribution_layer="mac80211/ath10k/tc",
                claim_status="CONFIRMED",
                scholar_queries=[f"IEEE 802.11 AQL CoDel {candidate_policy.description[:60]}"],
            )
        except Exception:
            pass
        try:
            mm_root = "G:/_OneDrive/OneDrive/Desktop/Py Apps/memorymaster"
            db_path = f"{mm_root}/memorymaster.db"
            if Path(db_path).exists():
                if mm_root not in sys.path:
                    sys.path.insert(0, mm_root)
                from memorymaster.core.models import CitationInput
                from memorymaster.core.service import MemoryService

                svc = MemoryService(db_path, workspace_root=Path(__file__).resolve().parents[2])
                svc.ingest(
                    text=summary,
                    citations=[
                        CitationInput(
                            source="fmx-autoresearch-harness",
                            locator=str(self.ledger.tsv_path),
                            excerpt=summary[:200],
                        )
                    ],
                    idempotency_key=f"fmx-autoresearch-{commit_tag}-{candidate_policy.policy_id}",
                    claim_type="fact",
                    subject=candidate_policy.policy_id,
                    predicate="autoresearch_keep",
                    object_value=f"{obs.goodput_rx_mbps:.2f}Mbps/{obs.p95_rtt_ms:.2f}ms",
                    scope="project:futuramax",
                    confidence=0.9,
                    source_agent="fmx-autoresearch-harness",
                )
        except Exception:
            pass

    def run_iteration(
        self,
        commit_tag: str,
        candidate_policy: MutableWirelessPolicy,
        benchmark_fn: Callable[[MutableWirelessPolicy], BenchmarkObservation],
    ) -> ObjectiveEvaluation:
        """
        Execute one autoresearch iteration:
        1. Validate candidate_policy bounds (reject as CRASH if out of bounds).
        2. Run immutable benchmark_fn(candidate_policy).
        3. Evaluate with compute_fmx_objective.
        4. Record in results.tsv and update or rollback incumbent_policy.
        """
        bound_errors = candidate_policy.validate_bounds()
        if bound_errors:
            eval_res = ObjectiveEvaluation(
                fmx_loss=float("inf"),
                decision=AutoresearchDecision.CRASH,
                reason="Policy bounds violation: " + "; ".join(bound_errors),
                disqualified=True,
            )
            self.ledger.append(
                ResultsRow(
                    commit=commit_tag,
                    fmx_loss=0.0,
                    goodput_mbps=0.0,
                    p95_rtt_ms=0.0,
                    jain_fairness=0.0,
                    status=AutoresearchDecision.CRASH.value,
                    description=f"{candidate_policy.description} [BOUNDS_ERROR: {bound_errors[0]}]",
                )
            )
            self.history.append(
                {
                    "commit": commit_tag,
                    "policy": asdict(candidate_policy),
                    "evaluation": asdict(eval_res),
                    "incumbent_after": self.incumbent_policy.policy_id,
                }
            )
            return eval_res

        try:
            obs = benchmark_fn(candidate_policy)
        except Exception as exc:
            eval_res = ObjectiveEvaluation(
                fmx_loss=float("inf"),
                decision=AutoresearchDecision.CRASH,
                reason=f"Benchmark execution exception: {exc}",
                disqualified=True,
            )
            self.ledger.append(
                ResultsRow(
                    commit=commit_tag,
                    fmx_loss=0.0,
                    goodput_mbps=0.0,
                    p95_rtt_ms=0.0,
                    jain_fairness=0.0,
                    status=AutoresearchDecision.CRASH.value,
                    description=f"{candidate_policy.description} [EXCEPTION: {exc}]",
                )
            )
            self.history.append(
                {
                    "commit": commit_tag,
                    "policy": asdict(candidate_policy),
                    "evaluation": asdict(eval_res),
                    "incumbent_after": self.incumbent_policy.policy_id,
                }
            )
            return eval_res

        eval_res = compute_fmx_objective(
            obs=obs,
            config=self.config,
            best_fmx_loss=self.best_fmx_loss,
            candidate_complexity=candidate_policy.complexity_cost,
            incumbent_complexity=self.incumbent_policy.complexity_cost,
        )

        if eval_res.decision == AutoresearchDecision.KEEP:
            self.incumbent_policy = candidate_policy
            self.best_fmx_loss = eval_res.fmx_loss

        self.ledger.append(
            ResultsRow(
                commit=commit_tag,
                fmx_loss=eval_res.fmx_loss if math.isfinite(eval_res.fmx_loss) else 0.0,
                goodput_mbps=obs.goodput_rx_mbps if math.isfinite(obs.goodput_rx_mbps) else 0.0,
                p95_rtt_ms=obs.p95_rtt_ms if math.isfinite(obs.p95_rtt_ms) else 0.0,
                jain_fairness=obs.jain_fairness if math.isfinite(obs.jain_fairness) else 0.0,
                status=eval_res.decision.value,
                description=candidate_policy.description,
            )
        )

        self.history.append(
            {
                "commit": commit_tag,
                "policy": asdict(candidate_policy),
                "observation": asdict(obs),
                "evaluation": asdict(eval_res),
                "incumbent_after": self.incumbent_policy.policy_id,
            }
        )
        self._emit_to_memorymaster_and_reactor(commit_tag, candidate_policy, obs, eval_res)
        return eval_res


async def ground_hypothesis_with_scholar(
    query: str,
    limit: int = 5,
    scholar_repo_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Grounds an autoresearch hypothesis using our local `scholar-mcp` engine
    (ArXiv + OpenAlex fallback + DuckDB HuggingFace + Jev semantic predicates).
    """
    default_repo = Path(r"G:\_OneDrive\OneDrive\Desktop\Py Apps\scholar-mcp")
    repo_dir = scholar_repo_path or default_repo
    if repo_dir.exists() and str(repo_dir) not in sys.path:
        sys.path.insert(0, str(repo_dir))

    from scholar.retrieval.engine import ScholarEngine

    engine = ScholarEngine()
    papers = await engine.search_papers(query=query, limit=limit)
    results: List[Dict[str, Any]] = []
    for p in papers:
        author_names = [a.name if hasattr(a, "name") else str(a) for a in p.authors[:4]]
        results.append(
            {
                "id": p.id,
                "title": p.title,
                "authors": author_names,
                "published_date": p.published_date,
                "citations_count": p.citations_count,
                "abstract_snippet": (p.abstract or "")[:350],
            }
        )
    return results


def compute_pareto_frontier(runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Multi-objective non-dominated Pareto sorting (per `.agents/skills/pymoo/SKILL.md`).
    Finds all feasible (non-disqualified) iterations that are non-dominated across
    the 3-objective vector:
      - maximize goodput_rx_mbps
      - minimize p95_rtt_ms
      - minimize p99_rtt_ms
    """
    feasible: List[Dict[str, Any]] = []
    for r in runs:
        ev = r.get("evaluation", {})
        obs = r.get("observation", {})
        if ev.get("disqualified", False):
            continue
        g = float(obs.get("goodput_rx_mbps", 0.0))
        p95 = float(obs.get("p95_rtt_ms", float("inf")))
        p99 = float(obs.get("p99_rtt_ms", float("inf")))
        if g > 0.0 and math.isfinite(p95) and math.isfinite(p99):
            feasible.append(r)

    pareto: List[Dict[str, Any]] = []
    for i, cand in enumerate(feasible):
        obs_i = cand["observation"]
        g_i, p95_i, p99_i = (
            float(obs_i["goodput_rx_mbps"]),
            float(obs_i["p95_rtt_ms"]),
            float(obs_i["p99_rtt_ms"]),
        )
        dominated = False
        for j, other in enumerate(feasible):
            if i == j:
                continue
            obs_j = other["observation"]
            g_j, p95_j, p99_j = (
                float(obs_j["goodput_rx_mbps"]),
                float(obs_j["p95_rtt_ms"]),
                float(obs_j["p99_rtt_ms"]),
            )
            no_worse = (g_j >= g_i) and (p95_j <= p95_i) and (p99_j <= p99_i)
            strictly_better = (g_j > g_i) or (p95_j < p95_i) or (p99_j < p99_i)
            if no_worse and strictly_better:
                dominated = True
                break
        if not dominated:
            pareto.append(cand)

    pareto.sort(key=lambda r: float(r["observation"]["p95_rtt_ms"]))
    return pareto

