#!/usr/bin/env python3
"""Source-bound PB030..033 migration receipts; never execute physical acquisition."""
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import receipt, save, snapshot

STEMS = {
    960: 'stage960a_pb030_031_unified_runner_migration',
    961: 'stage961a_pb032_033_unified_runner_migration',
}
CONTROLLERS = {
    960: 'controller/pb_030_031_phy_response_surface_harness.py',
    961: 'controller/pb_032_033_ratemask_sgi_solver.py',
}
TESTS = {
    960: 'tests/test_pb_030_031_phy_response_surface_harness.py',
    961: 'tests/test_pb_032_033_ratemask_sgi_solver.py',
}
ROLES = {
    960: 'PB_030_031_PHY_RESPONSE_SURFACE',
    961: 'PB_032_033_RATEMASK_SGI',
}
COMMON = [
    'tools/autoresearch/run_stage959a_unified_physical_retest_runner.py',
    'workloads/flent_orchestrator.py',
    'analysis/regression_gate/gatekeeper.py',
    'tools/autoresearch/stage897_900_gate_adapter.py',
    'tests/test_stage960a_961a_unified_runner.py',
    'tests/test_stage959a_unified_physical_runner.py',
    'tools/verify/build_stage960a_961a_unified_controller_migration.py',
    'tools/verify/stage779_822_offline_common.py',
]


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    reports = {}
    for stage in STEMS:
        sources = [snapshot(root, label) for label in [CONTROLLERS[stage], TESTS[stage], *COMMON]]
        if not all(row['available'] for row in sources):
            raise ValueError('controller, unified runner and regression sources are required')
        data = receipt(stage, f'PB controller unified physical runner migration {stage}A', sources)
        data.update(
            evidence_provenance_class='CONFIRMED_STATIC_BINARY',
            provenance_scope='executable source inspection and offline software contracts only',
            controller=CONTROLLERS[stage], frozen_experiment_role=ROLES[stage],
            physical_runner=COMMON[0],
            mandatory_campaign_phases=['AA_CONTROL', 'AB_DISCOVERY', 'AB_HOLDOUT'],
            raw_window_sha256_required=True, actual_flent_and_gatekeeper_required=True,
            holdout_boolean_shortcut=False, legacy_metric_arrays_scope='SYNTHETIC_DIAGNOSTICS_ONLY',
            inspection_invokes_acquisition=False, physical_acceptance='UNKNOWN',
            tests_executed_by_this_builder=False,
            executed_test_evidence='Stage964A source-bound verification gate',
            deployment_authorized=False,
        )
        if [snapshot(root, row['path']) for row in sources] != sources:
            raise ValueError('migration source changed during receipt construction')
        reports[f'{stage}A'] = save(root, STEMS[stage], data,
            'The physical entrypoint delegates to the Stage959A unified acquisition/inference runner.\n'
            f'Its frozen controller role is `{ROLES[stage]}`; cross-controller plans are rejected before acquisition.\n'
            'Plan creation and execution are distinct. Inspection is the default and invokes no acquisition callback.\n'
            'An executed campaign requires A/A, discovery and disjoint holdout with raw per-window SHA256 evidence.\n'
            'Actual hardened Flent parsing and RegressionGatekeeper evaluate the supplied acquisition bytes.\n'
            'Metric arrays, boolean holdout declarations and synthetic fixture verdicts cannot authorize physical promotion.\n'
            'Legacy diagnostic mathematics and synthetic reports remain available, separately labeled and non-promotable.\n'
            'The builder pins software only and never contacts a radio, runs a workload, or writes durable memory.\n'
            'Offline fault-injection tests and their actual exit/count evidence are consolidated in Stage964A.\n'
            'Source construction is CONFIRMED; actual physical acquisition and release acceptance remain UNKNOWN.\n')
    return reports


if __name__ == '__main__':
    print(json.dumps({stage: row['status'] for stage, row in build().items()}))
