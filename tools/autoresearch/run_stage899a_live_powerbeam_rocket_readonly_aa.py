# PUBLIC_REDACTED_DERIVATIVE; original_sha256=2c2ce36b81d4ad5236a0642f74f89a7698de4d07b166134635f1f5bbbc1cf27c
# Private originals are required for native replay.
"""Measured PowerBeam baseline/baseline HTTP+ICMP; Rocket identity is read-only."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import re
import sys
import time
import uuid
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage897_900_live_common as n
from tools.autoresearch import stage897_900_gate_adapter as adapter
from tools.autoresearch.run_stage864a_guarida_panel2_panel3_airmagic_and_slot_audit import section
from analysis.regression_gate.gatekeeper import RegressionGatekeeper
c = n.c
OUT = ROOT / 'artifacts/autoresearch/stage899a_live_powerbeam_rocket_readonly_aa.json'
PEER = '198.18.0.8'
CONFIG = n.PROBE + 'probe BOARD ubus call system board\nprobe BOOT cat /proc/sys/kernel/random/boot_id\nprobe IW iw dev\nprobe AQL cat /sys/kernel/debug/ieee80211/phy2/aql_txq_limit\nprobe PKTLOG cat /sys/kernel/debug/ieee80211/phy2/ath10k/pktlog_filter\nprobe BQL cat /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max\nprobe AUTO sysctl -n net.ipv4.tcp_autocorking\nprobe RECOVERY sysctl -n net.ipv4.tcp_recovery\nprobe STATIONS iw dev phy2-sta0 station dump\nprobe RESET_LOG_COUNT sh -c \'set -o pipefail; dmesg | awk "/firmware crashed|firmware crash|firmware reset|firmware restart/ {n++} END {print n+0}"\'\n'
WINDOW = n.PROBE + 'set -u\nset -o pipefail\nwork=$(mktemp -d /tmp/fmx-s899-XXXXXX) || exit 65\ncase "$work" in /tmp/fmx-s899-*) ;; *) exit 65;; esac\nmain_pid=$$\nfetch_pid= wc_pid= ping_pid= watchdog_pid=\nstop_child() {\n  target=$1\n  [ -n "$target" ] || return 0\n  if [ -r "/proc/$target/stat" ] && [ "$(awk \'{print $4}\' "/proc/$target/stat")" = "$main_pid" ]; then\n    kill -TERM "$target" 2>/dev/null || true\n    wait "$target" 2>/dev/null || true\n  fi\n}\ncleanup() {\n  stop_child "$fetch_pid"; stop_child "$wc_pid"; stop_child "$ping_pid"; stop_child "$watchdog_pid"\n  rm -f "$work/body.pipe" "$work/count" "$work/fetch.err"\n  rmdir "$work" || printf \'CLEANUP_FAILED=%s\\n\' "$work"\n}\ntrap cleanup 0\ntrap \'exit 130\' HUP INT TERM\n(\n  sleep_pid=\n  trap \'[ -z "$sleep_pid" ] || kill -TERM "$sleep_pid" 2>/dev/null; exit 0\' HUP INT TERM\n  sleep 40 & sleep_pid=$!\n  wait "$sleep_pid"; sleep_pid=\n  kill -TERM "$main_pid"\n) & watchdog_pid=$!\nprobe BOOT0 cat /proc/sys/kernel/random/boot_id\nprobe UPTIME0 cat /proc/uptime\nprobe STATIONS0 iw dev phy2-sta0 station dump\nprobe RESETS0 sh -c \'set -o pipefail; dmesg | awk "/firmware crashed|firmware crash|firmware reset|firmware restart/ {n++} END {print n+0}"\'\nping -c 20 -i 1 -W 1 198.18.0.8 &\nping_pid=$!\nload_ok=1\nmkfifo "$work/body.pipe" || exit 65\nitem=0\nwhile [ "$item" -lt 64 ]; do\n  [ -r "/proc/$ping_pid/stat" ] || break\n  [ "$(awk \'{print $3}\' "/proc/$ping_pid/stat")" != Z ] || break\n  item=$((item+1))\n  wc -c < "$work/body.pipe" > "$work/count" & wc_pid=$!\n  uclient-fetch -q --timeout=8 -O - http://198.18.0.8/bench4m.bin > "$work/body.pipe" 2> "$work/fetch.err" & fetch_pid=$!\n  wait "$fetch_pid"; fetch_rc=$?; fetch_pid=\n  wait "$wc_pid"; wc_rc=$?; wc_pid=\n  count=$(cat "$work/count")\n  cat "$work/fetch.err" >&2\n  printf \'RECEIVER_BODY_%s=%s EXIT_FETCH_%s=%s\\n\' "$item" "$count" "$item" "$fetch_rc"\n  if [ "$fetch_rc" -ne 0 ] || [ "$wc_rc" -ne 0 ] || [ "$count" -ne 4194304 ]; then load_ok=0; break; fi\ndone\nwait "$ping_pid"; ping_rc=$?; ping_pid=\nprintf \'EXIT_PING=%s\\n\' "$ping_rc"\nprobe UPTIME1 cat /proc/uptime\nprobe STATIONS1 iw dev phy2-sta0 station dump\nprobe RESETS1 sh -c \'set -o pipefail; dmesg | awk "/firmware crashed|firmware crash|firmware reset|firmware restart/ {n++} END {print n+0}"\'\nprobe BOOT1 cat /proc/sys/kernel/random/boot_id\n[ "$load_ok" -eq 1 ] && [ "$ping_rc" -eq 0 ]\n'

def required_section(text, name):
    raw, rc = section(text, name)
    if rc != 0 or raw is None:
        raise ValueError('missing_readback_' + name)
    return raw.strip()

def config_from_capture(row):
    if row.get('exit_code') != 0 or row.get('timed_out'):
        raise ValueError('config_transport_failure')
    text = row['stdout']
    board = json.loads(required_section(text, 'BOARD'))
    if board.get('board_name') != 'ubnt,powerbeam-5ac-gen2':
        raise ValueError('unexpected_board')
    native = required_section(text, 'IW')
    channels = set(re.findall('channel (\\d+) \\((\\d+) MHz\\), width: (\\d+) MHz, center1: (\\d+) MHz', native))
    if len(channels) != 1:
        raise ValueError('ambiguous_native_channel')
    channel, control, width, center = map(int, next(iter(channels)))
    return dict(board_name=board['board_name'], kernel=board['kernel'], boot_id=required_section(text, 'BOOT'), channel_width_mhz=width, control_mhz=control, center_mhz=center, station_interface='phy2-sta0', receiver='198.18.0.46', sender=PEER, aql=required_section(text, 'AQL'), pktlog=required_section(text, 'PKTLOG'), bql_limit_max=required_section(text, 'BQL'), tcp_autocorking=required_section(text, 'AUTO'), tcp_recovery=required_section(text, 'RECOVERY'), qdisc_readback='UNAVAILABLE_TC_NOT_INSTALLED', scope='REPEAT_EXISTING_4MIB_HTTP_DURING20_INTEGER_INTERVAL_ICMP_MAX64_REQUESTS', profile='EXISTING_UNMODIFIED_BASELINE', coverage='PARTIAL_CONFIGURATION_NO_TC', reset_instrument='UNCHANGED_BOOT_AND_KERNEL_LOG_RESTART_DELTA_NOT_SILENT_RESET_PROOF')

def counter(text, name):
    match = re.search('^\\s*' + re.escape(name) + ':\\s*(\\d+)\\s*$', text, re.M)
    if not match:
        raise ValueError('missing_station_counter_' + name)
    return int(match.group(1))

def normalize_window(row, config, *, arm, index, dataset, session, window_start, window_end, raw_pin):
    text = row.get('stdout', '')
    if row.get('exit_code') != 0 or row.get('timed_out'):
        raise ValueError('window_transport_or_load_failure')
    if 'CLEANUP_FAILED=' in text:
        raise ValueError('acquisition_cleanup_failed')
    boot0 = required_section(text, 'BOOT0')
    boot1 = required_section(text, 'BOOT1')
    if boot0 != boot1 or boot0 != config['boot_id']:
        raise ValueError('boot_changed')
    reset0 = int(required_section(text, 'RESETS0'))
    reset1 = int(required_section(text, 'RESETS1'))
    if reset1 < reset0:
        raise ValueError('reset_log_epoch_changed')
    if reset1 > reset0:
        raise ValueError('firmware_reset_observed')
    bodies = re.findall('^RECEIVER_BODY_([1-9][0-9]*)=(\\d+) EXIT_FETCH_\\1=(\\d+)$', text, re.M)
    if not 1 <= len(bodies) <= 64 or [int(x[0]) for x in bodies] != list(range(1, len(bodies) + 1)) or any((int(x[1]) != 4194304 or x[2] != '0' for x in bodies)):
        raise ValueError('receiver_body_count_or_exit_invalid')
    receiver_bytes = sum((int(x[1]) for x in bodies))
    match = re.search('(\\d+) packets transmitted, (\\d+) packets received', text)
    if not match:
        raise ValueError('missing_ping_summary')
    sent, received = map(int, match.groups())
    samples = [float(x) for x in re.findall('\\btime=([0-9.]+) ms', text)]
    if sent != 20 or received != len(samples) or received == 0 or ('EXIT_PING=0' not in text):
        raise ValueError('ping_coverage_invalid')
    before = required_section(text, 'STATIONS0')
    after = required_section(text, 'STATIONS1')
    rx = counter(after, 'rx bytes') - counter(before, 'rx bytes')
    tx = counter(after, 'tx bytes') - counter(before, 'tx bytes')
    if min(rx, tx) < 0:
        raise ValueError('station_counter_reset')
    raw = dict(run_id=dataset + f':{index}:{arm}', arm=arm, block_index=index, block_id=dataset + ':' + str(index), is_sentinel=False, dataset_id=dataset, epoch_id=session, session_id=session, peer_id='pbe241to242', profile_id='pbe_existing_baseline', experiment_role='AA_NEGATIVE_CONTROL', evidence_state='BENCH_EXECUTED', window_start_s=window_start, window_end_s=window_end, config_readback=config, firmware_resets=reset1 - reset0, acquisition=dict(receiver_bytes=receiver_bytes, duration_seconds=window_end - window_start, packets_sent=sent, packets_received=received, latencies_ms=samples, capture_drops=0, capture_drops_instrument='COMPLETE_BOUNDED_SSH_STDOUT_AND_PING_SEQUENCE_COUNTS', expected_peers=['pbe241to242'], peer_receiver_bytes={'pbe241to242': receiver_bytes}, http_requests=len(bodies), radio_rx_bytes_delta=rx, radio_tx_bytes_delta=tx, ota_byte_witness=rx >= receiver_bytes, goodput_source='receiver', percentile_method='nearest_rank'), native_capture=raw_pin)
    return raw

def collect(blocks=8):
    if type(blocks) is not int or not 4 <= blocks <= 12:
        raise ValueError('bounded_four_to_twelve_pairs')
    user, password = c.credential()
    host = '198.18.0.46'
    initial = n.run(host, CONFIG, password=password)
    initial_pin = n.save('899a', 'AA_INITIAL_CONFIG', [initial], target_configuration_writes=False)
    config = config_from_capture(initial)
    evaluator = RegressionGatekeeper(num_hypotheses_tested=1, evidence_root=ROOT)
    session = 's899-' + uuid.uuid4().hex
    dataset = session + '-aa'
    plan = dict(created_at_s=time.time(), contract=evaluator.frozen_contract, family_fingerprints=[adapter.digest(json.dumps(config, sort_keys=True, separators=(',', ':')).encode())], blocks=blocks, order=['A', 'B'], profile='same existing baseline', note='FixedABlabelorder, no tuning; Sidak family contains this one declared negative control', initial_native_config=initial_pin, readback_coverage='PARTIAL_NO_TC', source_bindings=adapter.source_bindings(), producer_source_bindings=[c.pin(__file__), c.pin(n.__file__), c.pin(c.__file__)])
    plan_path = ROOT / f'artifacts/verification/stage899a/{session}_frozen_plan.json'
    c.write(plan_path, plan)
    rows = []
    failures = []
    raw_bindings = []
    for index in range(blocks):
        for arm in ('A', 'B'):
            try:
                for binding in plan['producer_source_bindings']:
                    if c.pin(ROOT / binding['path']) != binding:
                        raise ValueError('producer_source_drift')
                check = n.run(host, CONFIG, password=password)
                check_pin = n.save('899a', 'AA_PREWINDOW_CONFIG', [check], target_configuration_writes=False)
                if config_from_capture(check) != config:
                    raise ValueError('baseline_configuration_changed')
                start = time.time()
                result = n.run(host, 'sh -s', password=password, timeout=55, input_bytes=WINDOW.encode())
                end = time.time()
                pin = n.save('899a', 'MEASURED_AA_WINDOW', [result], target_configuration_writes=False, target_filesystem_writes='EPHEMERAL_FIFO_AND_COUNTERS_IN_PRIVATE_TMP_CLEANED_ON_EXIT', dataset_id=dataset, block_index=index, arm=arm, window_start_s=start, window_end_s=end, prewindow_config=check_pin)
                raw_bindings.append(pin)
                post = n.run(host, CONFIG, password=password)
                post_pin = n.save('899a', 'AA_POSTWINDOW_CONFIG', [post], target_configuration_writes=False)
                if config_from_capture(post) != config:
                    raise ValueError('postwindow_configuration_changed')
                for binding in plan['producer_source_bindings']:
                    if c.pin(ROOT / binding['path']) != binding:
                        raise ValueError('postwindow_producer_source_drift')
                raw = normalize_window(result, config, arm=arm, index=index, dataset=dataset, session=session, window_start=start, window_end=end, raw_pin=pin)
                raw['postwindow_config_capture'] = post_pin
                label = f'artifacts/verification/stage899a/{session}_block{index}_{arm}.json'
                prepared = adapter.prepare_measurement(raw, label)
                dest = ROOT / label
                with dest.open('wb') as stream:
                    stream.write(prepared['blob'])
                    stream.flush()
                    c.os.fsync(stream.fileno())
                rows.append(dict(measurement=raw, receipt_path=label, receipt_sha256=prepared['sha256']))
                print(json.dumps(dict(stage='899A', block=index, arm=arm, receiver_bytes=raw['acquisition']['receiver_bytes'], duration_seconds=end - start, ota_byte_witness=raw['acquisition']['ota_byte_witness'])), flush=True)
            except (ValueError, KeyError, TypeError) as exc:
                failures.append(dict(block=index, arm=arm, reason=str(exc)))
                break
        if failures:
            break
    source_stable = all((c.pin(ROOT / x['path']) == x for x in plan['producer_source_bindings']))
    if source_stable:
        evaluation = adapter.evaluate_campaign(rows, evidence_root=ROOT, frozen_plan=plan, mode='AA_CONTROL', gate_options=dict(num_hypotheses_tested=1))
    else:
        evaluation = dict(status='SOURCE_DRIFT', control_result='INVALID_DATA', raw_gate=None, reasons=['producer_changed_before_final_inference'], deployment_authorized=False)
    all_ota = bool(rows) and all((x['measurement']['acquisition']['ota_byte_witness'] for x in rows))
    result = dict(stage='899A', schema_version=1, status='PARTIAL', acceptance='NOT_ACCEPTED', implementation=plan['producer_source_bindings'][0], analysis_dependencies=plan['producer_source_bindings'][1:] + plan['source_bindings'], planned_pairs=blocks, measured_windows=len(rows), rows=rows, failures=failures, frozen_plan=c.pin(plan_path), native_captures=raw_bindings, evaluation=evaluation, all_ota_byte_witnesses=all_ota, target_configuration_writes=False, firmware_or_qdisc_changed=False, acquisition_ram_files='PRIVATE_TMP_FIFO_COUNT_STDERR_ONLY_CLEANED_PER_WINDOW', limitations=['Qdisc settings unavailable without tc; no full configuration equality assertion', 'RX counter witness supports OTA byte activity, not exclusive RF routing proof', 'Repeated4MiBHTTP bulk during20 ICMP is not sector/TriplePlay capacity', 'Rocket .251 verification is separate; no2.4GHz peer assigned for Rocket AA', 'Kernel log/boot reset detector cannot detect all silent firmware resets'], physical_negative_control_acceptance='PARTIAL_NATIVE_COVERAGE', gate_must_not_authorize_candidate=True)
    preflights = []
    for path in sorted((ROOT / 'artifacts/verification/stage899a').glob('read_only_*.json')):
        if c.load(path).get('phase') == 'READ_ONLY_PREFLIGHT':
            preflights.append(c.pin(path))
    result['readonly_preflight_bindings'] = preflights
    c.write(OUT, result)
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect-aa', action='store_true')
    parser.add_argument('--blocks', type=int, default=8)
    args = parser.parse_args(argv)
    if not args.collect_aa:
        parser.error('explicit --collect-aa required; no automatic workload on import')
    result = collect(args.blocks)
    print(json.dumps(dict(stage='899A', measured_windows=result['measured_windows'], evaluation=result['evaluation']['status'], status=result['status'])))
    return 2 if result['failures'] else 0
if __name__ == '__main__':
    raise SystemExit(main())
