"""
FuturaMAX Closed-Loop Research Reactor (Controller Bridge Module)
=================================================================
Re-exports all closed-loop discovery-to-research reactor symbols,
empirical round ingestion routines, and Stage 47C/48C/49C/50C `M28..M35` synthesis
functions from `tools.research.closed_loop_research_reactor`.
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.research.closed_loop_research_reactor import (
    DISCOVERY_QUEUE_JSON,
    STAGE28_REACTOR_RECEIPT_JSON,
    STAGE34A_BENCH_JSON,
    STAGE35A_BENCH_JSON,
    STAGE36A_BENCH_JSON,
    STAGE37A_BENCH_JSON,
    STAGE39A_BENCH_JSON,
    STAGE40A_BENCH_JSON,
    STAGE41A_BENCH_JSON,
    STAGE41C_REACTOR_V10_RECEIPT_JSON,
    STAGE42A_BENCH_JSON,
    STAGE44A_BENCH_JSON,
    STAGE44C_REACTOR_V11_RECEIPT_JSON,
    STAGE45B_LTU_JSON,
    STAGE45C_REACTOR_V12_RECEIPT_JSON,
    STAGE46A_BENCH_JSON,
    STAGE46C_REACTOR_V13_RECEIPT_JSON,
    STAGE47B_LTU_OTA_JSON,
    STAGE47C_REACTOR_S40A_S42A_RECEIPT_JSON,
    STAGE48C_REACTOR_V14_RECEIPT_JSON,
    STAGE49C_REACTOR_V15_RECEIPT_JSON,
    STAGE50C_REACTOR_V16_RECEIPT_JSON,
    VAULT_ROOT,
    ClosedLoopResearchReactor,
    backfill_recent_discoveries_and_run_reactor,
    formulate_followup_queries,
    ingest_stage28_followup_papers_into_vault,
    ingest_stage34a_35a_36a_champion_v10_and_synthesize_m18_m21,
    ingest_stage37a_champion_v11_and_synthesize_m22_m23,
    ingest_stage39a_champion_v12_and_synthesize_m24_m25,
    ingest_stage40a_and_stage42a_and_synthesize_m28_m29,
    ingest_stage41a_champion_v13_and_synthesize_m26_m27,
    ingest_stage42a_r5_champion_v14_and_synthesize_m30_m31,
    ingest_stage44a_and_stage45b_and_synthesize_m32_m33,
    ingest_stage46a_and_stage47b_and_synthesize_m34_m35,
)

__all__ = [
    "DISCOVERY_QUEUE_JSON",
    "STAGE28_REACTOR_RECEIPT_JSON",
    "STAGE34A_BENCH_JSON",
    "STAGE35A_BENCH_JSON",
    "STAGE36A_BENCH_JSON",
    "STAGE37A_BENCH_JSON",
    "STAGE39A_BENCH_JSON",
    "STAGE40A_BENCH_JSON",
    "STAGE41A_BENCH_JSON",
    "STAGE41C_REACTOR_V10_RECEIPT_JSON",
    "STAGE42A_BENCH_JSON",
    "STAGE44A_BENCH_JSON",
    "STAGE44C_REACTOR_V11_RECEIPT_JSON",
    "STAGE45B_LTU_JSON",
    "STAGE45C_REACTOR_V12_RECEIPT_JSON",
    "STAGE46A_BENCH_JSON",
    "STAGE46C_REACTOR_V13_RECEIPT_JSON",
    "STAGE47B_LTU_OTA_JSON",
    "STAGE47C_REACTOR_S40A_S42A_RECEIPT_JSON",
    "STAGE48C_REACTOR_V14_RECEIPT_JSON",
    "STAGE49C_REACTOR_V15_RECEIPT_JSON",
    "STAGE50C_REACTOR_V16_RECEIPT_JSON",
    "VAULT_ROOT",
    "ClosedLoopResearchReactor",
    "backfill_recent_discoveries_and_run_reactor",
    "formulate_followup_queries",
    "ingest_stage28_followup_papers_into_vault",
    "ingest_stage34a_35a_36a_champion_v10_and_synthesize_m18_m21",
    "ingest_stage37a_champion_v11_and_synthesize_m22_m23",
    "ingest_stage39a_champion_v12_and_synthesize_m24_m25",
    "ingest_stage40a_and_stage42a_and_synthesize_m28_m29",
    "ingest_stage41a_champion_v13_and_synthesize_m26_m27",
    "ingest_stage42a_r5_champion_v14_and_synthesize_m30_m31",
    "ingest_stage44a_and_stage45b_and_synthesize_m32_m33",
    "ingest_stage46a_and_stage47b_and_synthesize_m34_m35",
]

if __name__ == "__main__":
    s47 = ingest_stage40a_and_stage42a_and_synthesize_m28_m29()
    s48 = ingest_stage42a_r5_champion_v14_and_synthesize_m30_m31()
    s49 = ingest_stage44a_and_stage45b_and_synthesize_m32_m33()
    s50 = ingest_stage46a_and_stage47b_and_synthesize_m34_m35()
    print(f"WROTE_STAGE47C_REACTOR_S40A_S42A_RECEIPT: {STAGE47C_REACTOR_S40A_S42A_RECEIPT_JSON}")
    print(f"WROTE_STAGE48C_REACTOR_V14_RECEIPT: {STAGE48C_REACTOR_V14_RECEIPT_JSON}")
    print(f"WROTE_STAGE49C_REACTOR_V15_RECEIPT: {STAGE49C_REACTOR_V15_RECEIPT_JSON}")
    print(f"WROTE_STAGE50C_REACTOR_V16_RECEIPT: {STAGE50C_REACTOR_V16_RECEIPT_JSON}")
    print(f"SYNTHESIZED_NEXT_WAVE_V15: {[m['mechanism_id'] for m in s49['next_wave_mechanisms_m32_to_m33']]}")
    print(f"SYNTHESIZED_NEXT_WAVE_V16: {[m['mechanism_id'] for m in s50['next_wave_mechanisms_m34_to_m35']]}")
