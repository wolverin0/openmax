# PUBLIC_REDACTED_DERIVATIVE; original_sha256=b846d39d6971c7076bc1db7c64401aeb77e7f323634f06776e28100beae2ce5a
# Private originals are required for native replay.
"""34 inventory endpoints reconciled against passive AP/backbone readbacks."""
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
OUT = ROOT / 'artifacts/autoresearch/stage882a_guarida_34endpoint_complete_readiness_audit.json'
ROSTER = ROOT / 'artifacts/autoresearch/stage361a_guarida_32cpe_cooperative_fault_matrix.json'

def mac(value):
    if not isinstance(value, str) or not re.fullmatch('(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', value):
        raise ValueError('invalid_mac_identity')
    return value.lower()

def observed_macs(row):
    if row.get('exit_code') != 0 or row.get('timed_out'):
        return None
    raw = row.get('stdout', '')
    if row.get('kind') == 'openwrt':
        matches = re.findall('^Station ([0-9A-Fa-f:]{17}) \\(', raw, re.M)
        if not re.search('EXIT_STATIONS_[^=]+=0', raw):
            return None
        try:
            return sorted({mac(item) for item in matches})
        except ValueError:
            return None
    text, rc = section(raw, 'STATIONS')
    if rc != 0:
        return None
    try:
        obj = json.loads(text)
        if not isinstance(obj, list):
            return None
        result = [mac(item['mac']) for item in obj]
        if len(set(result)) != len(result):
            return None
        return sorted(result)
    except (ValueError, TypeError, KeyError):
        return None

def reconcile(roster, rows):
    if len(roster) != 32:
        raise ValueError('expected_32_cpe_inventory_rows')
    identities = [mac(item['mac']) for item in roster]
    if len(set(identities)) != 32:
        raise ValueError('duplicate_inventory_mac')
    byhost = {row['host']: row for row in rows}
    records = []
    for item in roster:
        identity = mac(item['mac'])
        row = byhost.get(item['ap_ip'])
        observed = observed_macs(row) if row else None
        presence = ('NOT_OBSERVED_IN_THIS_SNAPSHOT' if identity not in observed else 'OBSERVED_ASSOCIATED') if observed is not None else 'UNKNOWN'
        records.append(dict(role='CPE', name=item['cpe_name'], ip=item['ip'], mac=identity, ap=item['ap_ip'], roster_observation=presence, direct_cpe_health='UNKNOWN', firmware_compatibility='UNKNOWN', recovery='UNKNOWN', ready=False))
    for host in ('198.18.0.3', '198.18.0.4'):
        row = byhost.get(host)
        ok = bool(row and row.get('exit_code') == 0 and (not row.get('timed_out')))
        records.append(dict(role='BACKBONE_RADIO', ip=host, readback_available=ok, end_to_end_delivery='UNKNOWN', recovery='UNKNOWN', ready=False))
    return records

def build(evidence=None):
    source = c.load(ROSTER)
    rows = c.load(ROOT / evidence['path'])['results'] if evidence else []
    records = reconcile(source['cpes_fault_matrix'], rows)
    return dict(schema_version=1, stage='882A', status='INCOMPLETE', acceptance='NOT_ACCEPTED', implementation=c.pin(__file__), analysis_dependencies=[c.pin(n.__file__), c.pin(c.__file__), c.pin(ROOT / 'tools/autoresearch/run_stage864a_guarida_panel2_panel3_airmagic_and_slot_audit.py')], source_bindings=[c.pin(ROSTER)], evidence=evidence, question='Which of the32 CPEs plus2 backbone radios have current native readiness evidence?', attribution=['external controller', 'Linux', 'proprietary airMAX component'], inventory_scope='32CPE_PLUS2_BACKBONE_NOT34_FRESH_SSH_SUCCESSES', inventory_rows=len(records), direct_cpe_ssh_sessions=0, endpoints=records, ready_count=0, complete_readiness_verified=False, target_writes=False, scan_triggered=False, snapshot_counts={row['host']: len(observed_macs(row)) if observed_macs(row) is not None else None for row in rows}, blockers=['INVENTORY_IS_NOT_DIRECT_HEALTH', 'NO_ENDPOINT_RECOVERY_AND_NATIVE_COMPATIBILITY_ACCEPTANCE', 'NO_LOADED_END_TO_END_QOE_WINDOW'], next_action='Resolve per-endpoint missing evidence without mass changes; never interpret an absent roster entry as a proven outage')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect', action='store_true')
    args = parser.parse_args(argv)
    evidence = None
    if args.inspect:
        user, password = c.credential()
        rows = [n.capture(host, 'airos', username=user, password=password) for host in ('198.18.0.3', '198.18.0.4', '198.18.0.5', '198.18.0.6')]
        rows.append(n.capture('198.18.0.7', 'openwrt', password=password))
        evidence = n.save('882a', rows)
    result = build(evidence)
    c.write(OUT, result)
    print(json.dumps(dict(stage='882A', status=result['status'], inventory_rows=34, evidence=evidence, snapshot_counts=result['snapshot_counts'])))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
