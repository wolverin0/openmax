#!/usr/bin/env python3
"""Ground-up v13 offline gate: Stage779..784 and817..822, never live approval."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c
from tools.verify.verify_stage784a_multi_radio_264w_v58_gate import STAGES as FIRST_BLOCK

STEM = 'stage822a_ground_up_v13_822stage_gate'
TEST = 'tests/test_stage817a_to_822a_suite.py'
STAGES = [
    (817, 'tools/firmware/build_stage817a_universal_pb060_triple_patch_openwrt_airos_kit.py',
     'stage817a_universal_pb060_triple_patch_openwrt_airos_kit', TEST),
    (818, 'tools/firmware/build_stage818a_ltu_4096qam_12x_ldpc_and_super4096_safe_kit.py',
     'stage818a_ltu_4096qam_12x_ldpc_and_super4096_safe_kit', TEST),
    (819, 'tools/sim/run_stage819a_guarida_tower_v10_triple_patch_and_xw_mixed_tdma_pareto.py',
     'stage819a_guarida_tower_v10_triple_patch_and_xw_mixed_tdma_pareto', TEST),
    (820, 'tools/observability/build_stage820a_executive_1line_progress_and_tester_matrix_v10.py',
     'stage820a_executive_1line_progress_and_tester_matrix_v10', TEST),
    (821, 'tools/verify/build_stage821a_960window_cross_lane_master_scorecard.py',
     'stage821a_960window_cross_lane_master_scorecard', TEST),
]


def audit_docs(root):
    failures = []
    paths = sorted((root / 'docs').glob('*.md'))
    for path in paths:
        text = path.read_text(encoding='utf-8-sig')
        if (len(text.splitlines()) >= 180 or text.count('<!-- doc-head:') != 1
                or text.count('<!-- /doc-head -->') != 1
                or not text.startswith('<!-- doc-head:')):
            failures.append(dict(path=path.relative_to(root).as_posix(),
                                 lines=len(text.splitlines()), heads=text.count('<!-- doc-head:')))
    return dict(compliant=bool(paths) and not failures, checked=len(paths), failures=failures)


def build(root=ROOT):
    first = [c.verify_stage(root, *row) for row in FIRST_BLOCK]
    checked = [c.verify_stage(root, *row) for row in STAGES]
    previous_gate = c.verify_stage(root, 784,
        'tools/verify/verify_stage784a_multi_radio_264w_v58_gate.py',
        'stage784a_multi_radio_264w_v58_gate', 'tests/test_stage779a_to_784a_suite.py')
    docs = audit_docs(root)
    sources = [c.snapshot(root, p) for p in [
        'tools/verify/verify_stage822a_ground_up_v13_822stage_gate.py',
        'tools/verify/stage779_822_offline_common.py', TEST,
        'tests/test_stage779a_to_784a_suite.py']]
    inventory = set()
    for path in (root / 'artifacts/autoresearch').glob('stage*.json'):
        match = re.match(r'stage(\d+)[a-z]_', path.name, re.I)
        if match and int(match[1]) <= 822:
            inventory.add(int(match[1]))
    data = c.receipt(822, 'Ground-up v13 822-stage offline gate', sources)
    data.update(stages_verified=checked, first_block_rechecked=first,
                previous_gate=previous_gate, docs_audit=docs,
                gate_scope='779A source presence; 780A model; 781A..784A and817A..821A offline deliverables',
                repository_stage_inventory=dict(target=822, observed_receipt_stage_numbers=sorted(inventory),
                                                meaning='filename inventory only; not acceptance of822 stages'),
                live_target_windows=960, live_target_accepted=False, physical_acceptance='UNKNOWN')
    data['compliant'] = (all(row['compliant'] for row in first + checked + [previous_gate])
                         and all(s['available'] for s in sources) and docs['compliant'])
    data['status'] = 'CONFIRMED' if data['compliant'] else 'FAILED'
    return c.save(root, STEM, data, f'Offline gate compliant: {data["compliant"]}.\n\n'
                  'Checks both requested blocks, local hashes, isolated-package boundaries and docs/*.md budgets.\n'
                  '822 is the roadmap target; filename inventory never establishes822 accepted stages.\n'
                  '960 windows is a target, not a synthetic count or accepted live milestone.\n'
                  'All radio, DHCP runtime, 4096QAM/12X LDPC and AP interoperability acceptance remains UNKNOWN.\n'
                  'No SSH, deployment, flash, AME writes or MemoryMaster ingestion.\n')


def main():
    result = build(); print(f'{STEM}: compliant={result["compliant"]}; docs={result["docs_audit"]["checked"]}')
    if not result['compliant']:
        print('Failures:', {r['stage']: r['failures'] for r in result['stages_verified']
                            + result['first_block_rechecked'] if not r['compliant']})
        print('Document violations:', len(result['docs_audit']['failures']))
    return 0 if result['compliant'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
