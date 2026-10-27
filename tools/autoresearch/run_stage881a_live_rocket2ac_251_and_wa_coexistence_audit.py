# PUBLIC_REDACTED_DERIVATIVE; original_sha256=033ab21f368bada8bd302070f3a23d78e55440a2a35a5669a6faeab9fc4b986c
# Private originals are required for native replay.
"""Stage881 read-only Rocket2AC and WA coexistence, with actual band geometry."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage861_866_common as c
from tools.autoresearch import stage879_884_common as n
from tools.autoresearch.run_stage864a_guarida_panel2_panel3_airmagic_and_slot_audit import section, status_values
OUT = ROOT / 'artifacts/autoresearch/stage881a_live_rocket2ac_251_and_wa_coexistence_audit.json'

def parse(row):
    raw = row.get('stdout', '')
    status, rc = section(raw, 'STATUS')
    try:
        values = status_values(status) if rc == 0 else {}
    except ValueError:
        values = {}
    board, board_rc = section(raw, 'BOARD')
    channels = [dict(control_mhz=int(a), width_mhz=int(b), center_mhz=int(d)) for a, b, d in sorted(set(re.findall('channel \\d+ \\((\\d+) MHz\\), width: (\\d+) MHz, center1: (\\d+) MHz', raw)))]
    if values.get('centerFreq') and values.get('chanbw'):
        try:
            channels = [dict(center_mhz=float(values['centerFreq']), width_mhz=float(values['chanbw']))]
        except ValueError:
            channels = []
    return dict(host=row['host'], transport_ok=row.get('exit_code') == 0 and (not row.get('timed_out')), identity_readback=board if board_rc == 0 else None, device_name=values.get('deviceName'), channels=channels, association_readback_available='Connected to ' in raw or 'Station ' in raw or 'EXIT_STATIONS=0' in raw, interference_causality='UNKNOWN', application_delivery='UNKNOWN')

def overlap(a, b):
    if not a or not b:
        return None
    import math
    for channel in (a, b):
        for key in ('center_mhz', 'width_mhz'):
            value = channel[key]
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError('invalid_channel_geometry')
    return max(0, min(a['center_mhz'] + a['width_mhz'] / 2, b['center_mhz'] + b['width_mhz'] / 2) - max(a['center_mhz'] - a['width_mhz'] / 2, b['center_mhz'] - b['width_mhz'] / 2))

def build(evidence=None):
    rows = c.load(ROOT / evidence['path'])['results'] if evidence else []
    observations = [parse(row) for row in rows]
    comparisons = []
    for i, a in enumerate(observations):
        for b in observations[i + 1:]:
            for ca in a['channels']:
                for cb in b['channels']:
                    comparisons.append(dict(host_a=a['host'], host_b=b['host'], nominal_overlap_mhz=overlap(ca, cb), meaning='Frequency-envelope geometry only, not a measured interference test'))
    return dict(schema_version=1, stage='881A', status='PARTIAL', acceptance='NOT_ACCEPTED', implementation=c.pin(__file__), analysis_dependencies=[c.pin(n.__file__), c.pin(c.__file__), c.pin(ROOT / 'tools/autoresearch/run_stage864a_guarida_panel2_panel3_airmagic_and_slot_audit.py')], question='What identities and band occupancy are observed on Rocket2AC and WA bench?', attribution=['external controller', 'Linux', 'proprietary airMAX component'], topology=n.TOPOLOGY, evidence=evidence, observations=observations, comparisons=comparisons, target_writes=False, scan_triggered=False, load_generated=False, blockers=['NO_CONTROLLED_COEXISTENCE_LOAD_OR_RECEIVER_DELIVERY_WINDOW'], next_action='Keep corrected .251Rocket2AC/.1MK1 mapping; quantify effects only with a separately guarded matched workload')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect', action='store_true')
    args = parser.parse_args(argv)
    evidence = None
    if args.inspect:
        user, password = c.credential()
        rows = [n.capture('198.18.0.48', 'airos', username=user, password=password)]
        rows += [n.capture(host, 'openwrt', password=password) for host in ('198.18.0.43', '198.18.0.47')]
        evidence = n.save('881a', rows)
    result = build(evidence)
    c.write(OUT, result)
    print(json.dumps(dict(stage='881A', status=result['status'], evidence=evidence, observed=[dict(host=x['host'], transport_ok=x['transport_ok'], channels=x['channels']) for x in result['observations']])))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
