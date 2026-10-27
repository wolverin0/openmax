# PUBLIC_REDACTED_DERIVATIVE; original_sha256=9e7e41f8974e4a41095ee536cb30b1b6e7a9964b9a28ad597698ed258cd888da
# Private originals are required for native replay.
"""Stage864: read-only Guarida spectral/TDMA evidence, never active AirMagic scans."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage861_866_common as c
OUT = ROOT / 'artifacts/autoresearch/stage864a_guarida_panel2_panel3_airmagic_and_slot_audit.json'
PANELS = ('198.18.0.5', '198.18.0.6')
READ = 'probe() { printf \'\\n===%s===\\n\' "$1"; label=$1; shift; "$@"; rc=$?; printf \'\\nEXIT_%s=%s\\n\' "$label" "$rc"; }\nprobe HOST hostname\nprobe VERSION cat /etc/version\nprobe BOARD sed -n \'/^board.name=/p;/^board.sysid=/p\' /etc/board.info\nprobe BOOT cat /proc/sys/kernel/random/boot_id\nprobe UPTIME cat /proc/uptime\nprobe STATIONS wstalist\nprobe STATUS mca-status\nprobe COUNTERS cat /proc/net/dev\nprobe POLL_PATHS ls /proc/sys/dev/ubnt_poll\nprobe FRAME_CONFIG grep -E \'^radio[.]1[.](frame_duration|frame|tdma|dl_ratio|dlratio|polling|chanbw|freq|airmax|airmagic)=\' /tmp/system.cfg\nfor f in /proc/sys/dev/ubnt_poll/*; do [ -f "$f" ] || continue; n=${f##*/}; case "$n" in *slot*|*frame*|*ratio*|*tdma*) probe "$n" cat "$f";; esac; done\nprobe INTERVAL_BOOT0 cat /proc/sys/kernel/random/boot_id\nprobe INTERVAL_UPTIME0 cat /proc/uptime\nprobe INTERVAL_STATUS0 mca-status\nsleep 5\nprobe INTERVAL_STATUS1 mca-status\nprobe INTERVAL_UPTIME1 cat /proc/uptime\nprobe INTERVAL_BOOT1 cat /proc/sys/kernel/random/boot_id\n'

def section(text, name):
    match = re.search('===' + re.escape(name) + '===\\n(.*?)\\nEXIT_' + re.escape(name) + '=(\\d+)', text, re.S)
    return (match.group(1), int(match.group(2))) if match else (None, None)

def parse_panel(row):
    text = row.get('stdout', '')
    raw, rc = section(text, 'STATIONS')
    stations, error = (None, None)
    if rc == 0 and raw:
        try:
            obj = json.loads(raw)
            if not isinstance(obj, list) or any((not isinstance(item, dict) for item in obj)):
                raise ValueError('unexpected_station_schema')
            stations = [item['mac'].lower() for item in obj if isinstance(item.get('mac'), str)]
            if len(stations) != len(obj) or len(set(stations)) != len(stations):
                raise ValueError('missing_or_duplicate_station_identity')
        except (ValueError, TypeError) as exc:
            stations = None
            error = type(exc).__name__
    status, status_rc = section(text, 'STATUS')
    try:
        values = status_values(status) if status_rc == 0 else {}
    except ValueError:
        values = {}
    return dict(host=row['host'], transport_ok=row.get('exit_code') == 0 and (not row.get('timed_out')), station_macs=stations, station_count=len(stations) if stations is not None else None, station_parse_error=error, station_command_exit=rc, native_status={key: values.get(key) for key in ('deviceName', 'chanbw', 'freq', 'airTime', 'wlanPolling', 'wlanScanStatus', 'cpuUsage')}, passive_interval=interval(row), spectral_efficiency_bps_hz=None, slot_utilization_pct=None, limits=['PHY link rate is not delivered goodput', 'Lifetime counters are not interval slot utilization', 'AirMagic score formula and live slot denominator are unverified'])

def status_values(raw):
    result = {}
    for line in (raw or '').splitlines():
        for piece in line.split(','):
            key, sep, value = piece.strip().partition('=')
            if sep:
                if key in result:
                    raise ValueError('duplicate_status_key')
                result[key] = value
    return result

def interval(row):
    text = row.get('stdout', '')
    fields = {key: section(text, key) for key in ('INTERVAL_BOOT0', 'INTERVAL_BOOT1', 'INTERVAL_UPTIME0', 'INTERVAL_UPTIME1', 'INTERVAL_STATUS0', 'INTERVAL_STATUS1')}
    if row.get('exit_code') != 0 or row.get('timed_out') or any((rc != 0 for _, rc in fields.values())):
        return dict(status='UNAVAILABLE', l2_interface_activity_bps_hz=None)
    if not fields['INTERVAL_BOOT0'][0].strip() or fields['INTERVAL_BOOT0'][0].strip() != fields['INTERVAL_BOOT1'][0].strip():
        return dict(status='REJECTED_BOOT_CHANGED', l2_interface_activity_bps_hz=None)
    try:
        before = status_values(fields['INTERVAL_STATUS0'][0])
        after = status_values(fields['INTERVAL_STATUS1'][0])
        dt = float(fields['INTERVAL_UPTIME1'][0].split()[0]) - float(fields['INTERVAL_UPTIME0'][0].split()[0])
        width = int(before['chanbw'])
        if dt <= 0 or not math.isfinite(dt) or width <= 0 or (before['chanbw'] != after['chanbw']) or (before['freq'] != after['freq']):
            raise ValueError('interval_or_channel_changed')
        counter_keys = ('wlanRxBytes', 'wlanTxBytes')
        if any((int(sample[key]) < 0 for sample in (before, after) for key in counter_keys)):
            raise ValueError('negative_absolute_counter')
        deltas = {key: int(after[key]) - int(before[key]) for key in counter_keys}
        if any((value < 0 for value in deltas.values())):
            raise ValueError('counter_reset_or_wrap')
    except (ValueError, KeyError, IndexError):
        return dict(status='REJECTED_INVALID_COUNTERS', l2_interface_activity_bps_hz=None)
    mbps = sum(deltas.values()) * 8 / dt / 1000000.0
    return dict(status='OBSERVED_PASSIVE_L2_ACTIVITY', seconds=dt, width_mhz=width, counter_deltas=deltas, l2_interface_activity_mbps=mbps, l2_interface_activity_bps_hz=spectral_efficiency(mbps, width), goodput_bps_hz=None, slot_utilization_pct=None, limitation='AP interface bytes over a bracketed passive interval; not unique application delivery or capacity')

def spectral_efficiency(goodput_mbps, width_mhz):
    for value in (goodput_mbps, width_mhz):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError('nonfinite_metric')
    if goodput_mbps < 0 or width_mhz <= 0:
        raise ValueError('invalid_metric_domain')
    return goodput_mbps / width_mhz

def build(evidence=None):
    rows = c.load(ROOT / evidence['path'])['results'] if evidence else []
    parsed = [parse_panel(row) for row in rows]
    expected = dict(zip(PANELS, ('Panel2-Guarida', 'Panel3-Guarida')))
    observed = len(parsed) == 2 and all((row['transport_ok'] and row['station_macs'] is not None and (row['native_status']['deviceName'] == expected.get(row['host'])) for row in parsed))
    return dict(schema_version=1, stage='864A', status='PARTIAL' if observed else 'BLOCKED', implementation=c.pin(__file__), analysis_dependencies=[c.pin(c.__file__)], acceptance='NOT_ACCEPTED', evidence=evidence, panels=parsed, question='What native evidence supports Guarida spectrum efficiency and TDMA slots?', attribution=['external controller', 'proprietary airMAX component'], target_writes=False, air_magic_scan_triggered=False, load_generated=False, spectral_efficiency_bps_hz=None, slot_utilization_pct=None, blockers=['NO_SYNCHRONIZED_DELIVERED_BYTES_AND_BANDWIDTH_WINDOW', 'NO_VALIDATED_NATIVE_SLOT_COUNTER_DENOMINATOR'], next_action='Decode available native readbacks, then acquire matched passive interval counters; no tower tuning')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect', action='store_true')
    args = parser.parse_args(argv)
    evidence = None
    if args.inspect:
        try:
            user, password = c.credential()
            rows = [c.capture(host, READ, username=user, password=password) for host in PANELS]
        except (OSError, KeyError) as exc:
            rows = [dict(host=host, exit_code=None, stdout='', stderr='', target_writes=False, error_type=type(exc).__name__) for host in PANELS]
        evidence = c.save_capture('864a', rows)
    result = build(evidence)
    c.write(OUT, result)
    print(json.dumps(dict(stage='864A', status=result['status'], evidence=evidence, station_counts=[item['station_count'] for item in result['panels']])))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
