#!/usr/bin/env python3
"""Build an offline MemoryMaster outbox, without claiming remote ingestion."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c

STEM = 'stage783a_memorymaster_264w_v58_ledger'
SOURCES = ['artifacts/autoresearch/stage781a_cross_fleet_champion_bundle_v58.json',
           'artifacts/autoresearch/stage782a_guarida_32cpe_ani_and_napi_pareto.json']


def build(root=ROOT):
    sources = [c.snapshot(root, p) for p in SOURCES]
    if not all(s['available'] for s in sources):
        raise ValueError('781A/782A must be built first')
    data = c.receipt(783, 'MemoryMaster 264w v58 local ledger', sources)
    data.update(scope='project:futuramax', ingestion_status='NOT_INGESTED',
                campaign_window_target=264, measured_windows_added=0,
                entries=[dict(claim_key=f'project:futuramax:{s["sha256"]}',
                              classification='CONFIRMED' if '781a' in s['path'] else 'INFERRED',
                              claim_scope='offline artifact construction', source=s,
                              physical_acceptance='UNKNOWN') for s in sources])
    return c.save(root, STEM, data, 'CONFIRMED: content-addressed local ledger/outbox.\n\n'
                  '264w is a campaign target and v58 a package label.\n'
                  'No MemoryMaster service was contacted; entries have NOT_INGESTED status.\n'
                  'Package construction and simulated results remain distinct from radio acceptance.\n')


def main():
    build(); print(f'{STEM}: local ledger; NOT_INGESTED; live=0'); return 0


if __name__ == '__main__':
    raise SystemExit(main())
