#!/usr/bin/env python3
"""Package available v58 references and helpers offline; no firmware promotion."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c

STEM = 'stage781a_cross_fleet_champion_bundle_v58'
SOURCES = [
    'tools/autoresearch/run_stage779a_multi_radio_264w_milestone_campaign.py',
    'tools/sim/run_stage780a_nsga3_pareto_ani_immunity_and_irq52_napi.py',
    'artifacts/autoresearch/stage749a_cross_fleet_champion_v57_bundle.json',
    'artifacts/autoresearch/stage779a_multi_radio_264w_milestone_campaign.json',
    'artifacts/autoresearch/stage780a_nsga3_pareto_ani_immunity_and_irq52_napi.json',
    'firmware/openwrt/common/fmx_qca988x_ani_spur_helper.sh',
    'firmware/ltu_safe_kit/fmx_ltu_irq_napi_and_dhcp_guard.sh',
    'orchestration/autoresearch/firmware_knob_candidates.json',
]


def build(root=ROOT):
    sources = [c.snapshot(root, p) for p in SOURCES]
    data = c.receipt(781, 'Cross-fleet champion bundle v58', sources)
    data.update(champion_version='v58', package_kind='REFERENCE_AND_HELPER_KIT',
                multi_radio_window_target=264, new_live_windows=0,
                measured_performance='UNKNOWN', runtime_activation='BLOCKED_PENDING_RADIO_ACCEPTANCE')
    data['package'] = c.package(root, f'artifacts/autoresearch/{STEM}.zip', sources)
    data['missing_sources'] = [s['path'] for s in sources if not s['available']]
    data['prerequisites'] = {'779A': 'SOURCE_VERIFIED_NOT_EXECUTED', '780A': 'OFFLINE_MODEL'}
    return c.save(root, STEM, data,
                  'CONFIRMED: local reference/helper ZIP and source hashes.\n\n'
                  '264 windows is the campaign target; no new live windows were acquired.\n'
                  '779A is inspected as source only because its runner opens SSH connections.\n'
                  '780A results are a model. Imported champion labels do not establish measured gains.\n'
                  'The ZIP contains available sources, not a flashable image or deployment approval.\n')


def main():
    result = build(); print(f'{STEM}: packaged; missing={len(result["missing_sources"])}; live=0'); return 0


if __name__ == '__main__':
    raise SystemExit(main())
