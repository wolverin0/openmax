# PUBLIC_REDACTED_DERIVATIVE; original_sha256=e2e3ece2f63e83b1824abfe6fd1509b0c2f39297a3de23de2f0a77ec83adc510
# Private originals are required for native replay.
"""Stage861: native bench preflight and fail-closed PB070 source prerequisite gate."""
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
OUT = ROOT / 'artifacts/autoresearch/stage861a_live_pbe5ac_quad_patch_pb040_to_pb070_ota.json'
SOURCE = ROOT / 'artifacts/autoresearch/stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.json'
BENCH = ('198.18.0.45', '198.18.0.46')
READ = 'probe() { printf \'\\n===%s===\\n\' "$1"; label=$1; shift; "$@"; rc=$?; printf \'\\nEXIT_%s=%s\\n\' "$label" "$rc"; }\nprobe BOARD ubus call system board\nprobe BOOT cat /proc/sys/kernel/random/boot_id\nprobe UPTIME cat /proc/uptime\nprobe IW iw dev\nfor i in /sys/class/net/phy*; do [ -d "$i" ] || continue; n=${i##*/}; probe "INFO_$n" iw dev "$n" info; probe "LINK_$n" iw dev "$n" link; probe "STATIONS_$n" iw dev "$n" station dump; done\nprobe ADDRESS ip -4 address show\nprobe ROUTE ip -4 route show\nfor s in dnsmasq odhcpd; do probe "PID_$s" pidof "$s"; done\nfor f in /lib/firmware/ath10k/QCA988X/hw2.0/firmware-*.bin; do [ -f "$f" ] && probe FIRMWARE sha256sum "$f"; done\nfor p in /sys/kernel/debug/ieee80211/phy*/ath10k; do [ -d "$p" ] || continue; echo "DYNAMIC_PATH=$p"; for f in fw_checksums pktlog_filter; do probe "$f" cat "$p/$f"; done; done\nprobe REG iw reg get\nprobe FDB bridge fdb show\nprobe MODULES lsmod\n'

def prerequisite(source=SOURCE):
    record = c.load(source)
    summary = record.get('summary', {})
    return dict(source=c.pin(source), patch_emitted=summary.get('patch_emitted'), candidate_available=False, native_quad_verified=False, source_reason=summary.get('blocking_reason'), blocker='STAGE806_NO_PB070_BINARY' if summary.get('patch_emitted') == 0 else 'NO_REVIEWED_NATIVE_QUAD_CONTAINER')

def parse_native(row):
    text = row.get('stdout', '')

    def field(pattern):
        found = re.search(pattern, text)
        return found.group(1) if found else None
    board = field('"board_name"\\s*:\\s*"([^"]+)"')
    channels = [dict(channel=int(a), control_mhz=int(b), width_mhz=int(d), center1_mhz=int(e)) for a, b, d, e in re.findall('channel (\\d+) \\((\\d+) MHz\\), width: (\\d+) MHz, center1: (\\d+) MHz', text)]
    pids = {name: field('EXIT_PID_' + name + '=(\\d+)') for name in ('dnsmasq', 'odhcpd')}
    return dict(host=row['host'], board=board, channels=channels, boot_id=field('===BOOT===\\s*([0-9a-f-]{36})'), pktlog_values=re.findall('===pktlog_filter===\\s*([^\\n]+)', text), default_ip_present=bool(re.search('inet 192\\.168\\.1\\.20/', text)) if 'EXIT_ADDRESS=0' in text else None, dhcp_pid_exit=pids, association_observed='Connected to ' in text or 'Station ' in text if 'EXIT_IW=0' in text else None, native_identity_observed=board == 'ubnt,powerbeam-5ac-gen2', transport_ok=row.get('exit_code') == 0 and (not row.get('timed_out')), ota_path_proven=False, cold_boot_persistence='UNKNOWN', v5_activation='UNKNOWN', v6_activation='NOT_EXECUTED')

def build(capture=None):
    p = prerequisite()
    rows = c.load(ROOT / capture['path'])['results'] if capture else []
    return dict(schema_version=1, stage='861A', status='BLOCKED', acceptance='NOT_ACCEPTED', implementation=c.pin(__file__), analysis_dependencies=[c.pin(c.__file__)], question='Is a reviewed native PB040+PB050+PB060+PB070 image available to activate?', attribution=['external controller', 'ath10k', 'QCA firmware'], source_prerequisite=p, blockers=[p['blocker']], evidence=capture, native_state=[parse_native(row) for row in rows], deployment=dict(executed=False, target_writes=False, firmware_loaded=False, watchdog_required_seconds=45, watchdog_armed=False, dynamic_phy_required=True, order=['STA .242', 'AP .241'], flash_writes=False, restoration='NOT_NEEDED_NO_CHANGES'), missing_evidence=['Reviewed native API2 container and all four patch pre/post bytes', 'Exact v5 baseline and PB050 recipe', 'Independent loader/watchdog recovery proof before any activation'], next_action='Provide or develop and independently validate PB070; do not rename raw SGMT to firmware-5.bin')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect', action='store_true', help='Read the two authorized bench radios')
    parser.add_argument('--execute', action='store_true', help='Request activation; withheld without a validated candidate')
    args = parser.parse_args(argv)
    evidence = None
    if args.inspect:
        evidence = c.save_capture('861a', [c.capture(host, READ) for host in BENCH])
    result = build(evidence)
    c.write(OUT, result)
    print(json.dumps(dict(stage='861A', status=result['status'], blockers=result['blockers'], evidence=evidence)))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
