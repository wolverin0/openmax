#!/usr/bin/env python3
"""Publish source-bound migration receipts; never acquire data or run producers."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from tools.verify.stage779_822_offline_common import receipt, save, snapshot

STEMS = {
    962: 'stage962a_pb050_051_unified_runner_migration',
    963: 'stage963a_pb053_054_unified_runner_migration',
}
CONTROLLERS = {
    962: 'controller/pb_050_051_scheduler_timing_harness.py',
    963: 'controller/pb_053_054_hmac_epoch_controller.py',
}
TESTS = {
    962: 'tests/test_pb_050_051_scheduler_timing_harness.py',
    963: 'tests/test_pb_053_054_hmac_epoch_controller.py',
}
SELF = 'tools/verify/' + Path(__file__).name
SHARED = [SELF, 'tools/autoresearch/run_stage959a_unified_physical_retest_runner.py',
          'tests/test_stage962a_963a_unified_runner.py',
          'workloads/flent_orchestrator.py', 'analysis/regression_gate/gatekeeper.py',
          'tools/autoresearch/stage897_900_gate_adapter.py',
          'tools/verify/stage779_822_offline_common.py']


def build(root: Path = ROOT) -> dict:
    outputs = {}
    for stage, stem in STEMS.items():
        sources = [snapshot(root,p) for p in [CONTROLLERS[stage],TESTS[stage],*SHARED]]
        if not all(source['available'] for source in sources):
            raise ValueError('controller migration sources missing')
        data = receipt(stage,'PB controller migration to unified physical retest runner',sources)
        data.update(evidence_provenance_class='CONFIRMED_STATIC_BINARY',
            provenance_scope='offline Python source and regression contract only',
            physical_acceptance='UNKNOWN', fresh_live_windows=0,
            controller=CONTROLLERS[stage],
            physical_entrypoint='run_physical_retest',
            frozen_plan_entrypoint='freeze_physical_retest_plan',
            diagnostic_array_promotion_allowed=False,
            historical_receipts_reaccepted=False,
            required_campaign_phases=['AA_CONTROL','AB_DISCOVERY','AB_HOLDOUT'],
            tests_executed_by_this_builder=False,
            executed_test_evidence='Fresh source-bound counts and exit codes are recorded by Stage964A')
        body = ('Controller physical retesting delegates directly to the unified Stage959A runner.\n'
                'The controller experiment role is fixed inside the frozen acquisition plan.\n'
                'Default inspect/plan execution acquires no window; explicit execution must supply the acquisition interface.\n'
                'Raw SHA256-bound A/A, discovery and independent holdout phases are mandatory.\n'
                'Empty/error outputs, copied windows and changed configuration or source contracts fail closed.\n'
                'Legacy timing arrays and imported historical reports cannot promote physical evidence.\n'
                'The physical runner retests QoE; SDR timing, hMAC target actuation and multi-distance acceptance remain separate.\n'
                'Existing diagnostic mathematics remains available as explicitly scoped software output.\n'
                'This builder pins actual source bytes but executes no test, producer, network or device command.\n'
                'Physical acceptance UNKNOWN; no new measurements, firmware activation or durable-memory ingestion.\n')
        outputs[str(stage)+'A'] = save(root,stem,data,body)
    return outputs


if __name__ == '__main__':
    print(json.dumps({stage: row['status'] for stage,row in build().items()}))
