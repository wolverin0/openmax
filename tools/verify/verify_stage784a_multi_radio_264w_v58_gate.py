#!/usr/bin/env python3
"""Verify the offline Stage779A..784A deliverables, without live acceptance."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c

STEM = 'stage784a_multi_radio_264w_v58_gate'
STAGES = [
    (779, 'tools/autoresearch/run_stage779a_multi_radio_264w_milestone_campaign.py',
     'stage779a_multi_radio_264w_milestone_campaign', 'tests/test_stage779a.py'),
    (780, 'tools/sim/run_stage780a_nsga3_pareto_ani_immunity_and_irq52_napi.py',
     'stage780a_nsga3_pareto_ani_immunity_and_irq52_napi', 'tests/test_stage780a.py'),
    (781, 'tools/firmware/build_stage781a_cross_fleet_champion_bundle_v58.py',
     'stage781a_cross_fleet_champion_bundle_v58', 'tests/test_stage779a_to_784a_suite.py'),
    (782, 'tools/sim/run_stage782a_guarida_32cpe_ani_and_napi_pareto.py',
     'stage782a_guarida_32cpe_ani_and_napi_pareto', 'tests/test_stage779a_to_784a_suite.py'),
    (783, 'tools/observability/build_stage783a_memorymaster_264w_v58_ledger.py',
     'stage783a_memorymaster_264w_v58_ledger', 'tests/test_stage779a_to_784a_suite.py'),
]


def build(root=ROOT):
    checked = [c.verify_stage(root, *row) for row in STAGES]
    data = c.receipt(784, 'Multi-radio 264w v58 offline gate', [])
    data.update(compliant=all(r['compliant'] for r in checked), stages_verified=checked,
                gate_scope='offline artifacts only; Stage779A source presence only',
                live_campaign_acceptance='UNKNOWN', physical_acceptance='UNKNOWN')
    data['status'] = 'CONFIRMED' if data['compliant'] else 'FAILED'
    return c.save(root, STEM, data, f'Offline gate compliant: {data["compliant"]}.\n\n'
                  '779A source and test exist; its live runner was not executed.\n'
                  '780A model and 781A..783A provenance are checked from local files.\n'
                  'Missing live campaign, radio acceptance and MemoryMaster ingestion remain UNKNOWN.\n'
                  'This gate never approves deployment or confirms 264 measured windows.\n')


def main():
    result = build(); print(f'{STEM}: compliant={result["compliant"]} (offline scope)')
    return 0 if result['compliant'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
