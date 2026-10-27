#!/usr/bin/env python3
"""Source-only v23 manifests and qualified replay of already saved observations."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c

STEMS = {
    937: 'stage937a_v23_active_source_sha256_manifests',
    938: 'stage938a_905_to_934_verified_saved_measurements',
    939: 'stage939a_public_v23_evidence_documentation_sync',
}
SELF = 'tools/observability/' + Path(__file__).name
KIT_RECEIPT = 'artifacts/autoresearch/stage935a_pbe_ltu_fail_closed_kits.json'
KIT_DIRS = ('firmware/openwrt/pbe5ac_gen2_ptp_kit', 'firmware/ltu_safe_kit')
SHA_FILES = tuple(folder + '/SHA256SUMS' for folder in KIT_DIRS)
COMMON = 'tools/verify/stage779_822_offline_common.py'
HEADING = '## Stages935A..940A: source-only v23 release'


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def binding(root: Path, pin: dict) -> dict:
    if (not isinstance(pin, dict) or type(pin.get('bytes')) is not int
            or pin['bytes'] < 0 or not re.fullmatch('[0-9a-f]{64}', str(pin.get('sha256', '')))):
        raise ValueError('invalid_saved_binding')
    now = c.snapshot(root, pin['path'])
    if (not now['available'] or now['bytes'] != pin['bytes'] or now['sha256'] != pin['sha256']):
        raise ValueError('saved_capture_hash_mismatch')
    return c.read_json(root, pin['path'])


def section(text: str, name: str) -> str:
    matches = list(re.finditer(r'(?:^|\n)===' + re.escape(name) +
        r'===\r?\n(.*?)\r?\nEXIT_' + re.escape(name) + r'=(\d+)(?=\r?\n|$)', text, re.S))
    if len(matches) != 1 or matches[0][2] != '0':
        raise ValueError('missing_or_failed_native_section')
    return matches[0][1].strip()


def native_row(capture: dict) -> dict:
    rows = capture.get('results')
    if not isinstance(rows, list) or len(rows) != 1:
        raise ValueError('single_native_result_required')
    row = rows[0]
    if row.get('exit_code') != 0 or row.get('timed_out') is not False or row.get('error_type'):
        raise ValueError('native_transport_failed')
    if not isinstance(row.get('stdout'), str):
        raise ValueError('native_stdout_required')
    return row


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[math.ceil(len(ordered) * fraction)-1]


def replay_906_window(root: Path, wrapper: dict) -> dict:
    raw = wrapper['measurement']
    capture = binding(root, raw['native_capture'])
    normalized = binding(root, dict(path=wrapper['receipt_path'],
        bytes=c.snapshot(root, wrapper['receipt_path']).get('bytes'), sha256=wrapper['receipt_sha256']))
    shared = set(raw) - {'native_capture','native_program_sha256','postwindow_config_capture','firmware_resets','acquisition'}
    if (set(normalized) != shared | {'metrics','acquisition'}
            or any(normalized.get(key) != raw[key] for key in shared)
            or any(normalized['acquisition'].get(key) != value for key,value in raw['acquisition'].items())):
        raise ValueError('saved_normalized_measurement_mismatch')
    if (capture.get('phase') != 'MEASURED_WINDOW'
            or raw.get('experiment_role') != 'AA_NEGATIVE_CONTROL'):
        raise ValueError('wrong_native_window_role')
    for key in ('arm', 'block_index', 'dataset_id', 'session_id', 'window_start_s', 'window_end_s'):
        if capture.get(key) != raw.get(key):
            raise ValueError('native_window_identity_mismatch')
    start, end = raw['window_start_s'], raw['window_end_s']
    if not finite(start) or not finite(end) or end <= start:
        raise ValueError('native_duration_invalid')
    row = native_row(capture)
    if (not re.fullmatch('[0-9a-f]{64}', str(capture.get('program_sha256', '')))
            or row.get('stdin_sha256') != capture['program_sha256']
            or raw.get('native_program_sha256') != capture['program_sha256']):
        raise ValueError('native_program_binding_mismatch')
    text = row['stdout']
    if 'CLEANUP_FAILED=' in text:
        raise ValueError('native_cleanup_failed')
    boot0, boot1 = section(text, 'BOOT0'), section(text, 'BOOT1')
    if boot0 != boot1 or boot0 != raw['config_readback']['boot_id']:
        raise ValueError('native_boot_changed')
    if section(text, 'RESETS0') != section(text, 'RESETS1'):
        raise ValueError('native_reset_observed')
    bodies = re.findall(r'^RECEIVER_BODY_([1-9][0-9]*)=(\d+) EXIT_FETCH_\1=(\d+)$', text, re.M)
    if (not 1 <= len(bodies) <= 64 or [int(v[0]) for v in bodies] != list(range(1, len(bodies)+1))
            or any(int(v[1]) != 4194304 or v[2] != '0' for v in bodies)):
        raise ValueError('receiver_body_acquisition_invalid')
    receiver_bytes = sum(int(v[1]) for v in bodies)
    summaries = re.findall(r'(\d+) packets transmitted, (\d+) packets received', text)
    if len(summaries) != 1:
        raise ValueError('unique_ping_summary_required')
    sent, received = map(int, summaries[0])
    latencies = [float(v) for v in re.findall(r'\btime=([0-9.]+) ms', text)]
    if (sent != 20 or received != len(latencies) or not 0 < received <= sent
            or any(not finite(v) or v < 0 for v in latencies) or 'EXIT_PING=0' not in text):
        raise ValueError('ping_acquisition_invalid')
    acquisition = raw['acquisition']
    if (acquisition['receiver_bytes'] != receiver_bytes or acquisition['packets_sent'] != sent
            or acquisition['packets_received'] != received or acquisition['latencies_ms'] != latencies
            or not math.isclose(acquisition['duration_seconds'], end-start, rel_tol=1e-12)
            or acquisition.get('ota_byte_witness') is not True
            or acquisition.get('radio_rx_bytes_delta', -1) < receiver_bytes):
        raise ValueError('derived_measurements_disagree_with_native')
    metrics=normalized['metrics']
    expected={'goodput_mbps':receiver_bytes*8/(end-start)/1e6,
              'loss_pct':100*(sent-received)/sent,'p95_lat_ms':percentile(latencies,.95),
              'p99_lat_ms':percentile(latencies,.99)}
    if any(not finite(metrics.get(key)) or not math.isclose(metrics[key],value,abs_tol=1e-9)
           for key,value in expected.items()):
        raise ValueError('normalized_metric_arithmetic_mismatch')
    for pin in (capture['prewindow_config'], raw['postwindow_config_capture']):
        native_row(binding(root, pin))
    return dict(window_id=raw['run_id'], receiver_bytes=receiver_bytes, packets_sent=sent,
                packets_received=received, duration_seconds=end-start,
                receiver_goodput_mbps=receiver_bytes*8/(end-start)/1e6,
                p95_rtt_ms=percentile(latencies, .95), p99_rtt_ms=percentile(latencies, .99),
                loss_pct=100*(sent-received)/sent)


def replay_906(root: Path, data: dict) -> dict:
    aa = data['aa']
    rows = aa['rows']
    if aa.get('pairs') != 6 or len(rows) != 12 or aa.get('failures'):
        raise ValueError('declared_aa_cohort_incomplete')
    for pin in data['native_captures'] + aa['native_captures']:
        binding(root, pin)
    windows = [replay_906_window(root, row) for row in rows]
    if len({row['window_id'] for row in windows}) != len(windows):
        raise ValueError('duplicate_native_window')
    evaluation = aa['evaluation']
    if evaluation.get('deployment_authorized') is not False:
        raise ValueError('unexpected_campaign_promotion')
    raw_gate = evaluation.get('raw_gate') or {}
    metrics = {}
    for key in ('receiver_goodput_mbps', 'p95_rtt_ms', 'p99_rtt_ms', 'loss_pct'):
        values = [row[key] for row in windows]
        metrics[key + '_range'] = [min(values), max(values)]
    return dict(kind='SAVED_NATIVE_DIAGNOSTIC_AA', saved_windows_verified=len(windows),
        pairs=6, receiver_bytes=sum(row['receiver_bytes'] for row in windows),
        packets_sent=sum(row['packets_sent'] for row in windows),
        packets_received=sum(row['packets_received'] for row in windows), **metrics,
        observation_scope='single4MiB HTTP request with20integer-interval ICMP probes; management-path diagnostic',
        all_zero_loss=all(row['loss_pct'] == 0 for row in windows),
        original_gate_verdict=raw_gate.get('verdict', 'UNKNOWN'),
        paired_blocks_reached=raw_gate.get('paired_blocks_count'),
        control_result=evaluation.get('control_result', 'UNKNOWN'),
        promotion_allowed=False, new_measurements=0, physical_release_acceptance='UNKNOWN')


def passive_values(row: dict) -> dict:
    text = row['stdout']
    boot = section(text, 'BOOT')
    uptime = float(section(text, 'UPTIME').split()[0])
    cpus = {}
    for name, counters in re.findall(r'^(cpu\d*)\s+([0-9 ]+)$', section(text, 'PROC_STAT'), re.M):
        values = list(map(int, counters.split()))
        if len(values) < 8 or name in cpus:
            raise ValueError('cpu_counters_invalid')
        cpus[name] = values[:8]
    interrupt = section(text, 'INTERRUPTS')
    headers = [line.split() for line in interrupt.splitlines()
               if re.fullmatch(r'\s*CPU\d+(?:\s+CPU\d+)*\s*', line)]
    irq_rows = [line.split() for line in interrupt.splitlines() if re.match(r'^\s*63:', line)]
    irq = None
    if len(headers) == len(irq_rows) == 1 and 'CPU1' in headers[0]:
        irq = int(irq_rows[0][1+headers[0].index('CPU1')])
    if not finite(uptime) or uptime < 0 or not boot or not cpus:
        raise ValueError('passive_native_observation_incomplete')
    return dict(boot=boot, uptime=uptime, cpus=cpus, irq=irq)


def replay_passive(root: Path, data: dict) -> dict:
    evidence = data['evidence_bindings']
    windows = data['windows']
    if len(evidence) != 24 or len(windows) != 12:
        raise ValueError('passive_acquisition_count_mismatch')
    verified = {pin['sha256']: native_row(binding(root, pin)) for pin in evidence}
    if len(verified) != 24:
        raise ValueError('duplicate_passive_capture')
    busy, irqs, durations = [], [], []
    used = set()
    for window in windows:
        snapshots = window['snapshots']
        if len(snapshots) != 2 or window.get('controlled_aa_valid') is not False:
            raise ValueError('passive_window_misclassified')
        native = []
        for snapshot in snapshots:
            pin = snapshot['evidence_binding']
            binding(root, pin)
            if pin['sha256'] not in verified or pin['sha256'] in used:
                raise ValueError('unbound_or_reused_passive_snapshot')
            used.add(pin['sha256'])
            native.append(verified[pin['sha256']])
        a, b = map(passive_values, native)
        times = [native[0]['local_monotonic_start_s'], native[0]['local_monotonic_end_s'],
                 native[1]['local_monotonic_start_s'], native[1]['local_monotonic_end_s']]
        if (a['boot'] != b['boot'] or b['uptime'] <= a['uptime']
                or native[0].get('host') != native[1].get('host')
                or not native[0].get('collector_epoch')
                or native[0]['collector_epoch'] != native[1].get('collector_epoch')
                or not all(finite(t) for t in times) or times != sorted(times)):
            raise ValueError('passive_epoch_or_time_mismatch')
        duration = b['uptime']-a['uptime']
        delta = window['passive_delta']
        if (delta.get('status') != 'PASSIVE_COUNTER_INTERVAL'
                or not math.isclose(delta['target_interval_seconds'], duration, abs_tol=1e-9)
                or delta.get('application_goodput_mbps') is not None):
            raise ValueError('passive_delta_or_goodput_claim_invalid')
        if set(a['cpus']) != set(b['cpus']):
            raise ValueError('passive_cpu_identity_changed')
        for name in a['cpus']:
            differences = [y-x for x,y in zip(a['cpus'][name],b['cpus'][name])]
            if min(differences) < 0 or sum(differences) <= 0:
                raise ValueError('passive_cpu_counter_reset')
            actual_busy = 100*(sum(differences)-differences[3]-differences[4])/sum(differences)
            declared = delta['cpu'][name]
            if declared.get('status') != 'OBSERVED' or not math.isclose(
                    declared['busy_pct'], actual_busy, abs_tol=1e-9):
                raise ValueError('passive_cpu_recomputation_mismatch')
            if name == 'cpu':
                busy.append(actual_busy)
        if a['irq'] is not None and b['irq'] is not None:
            irq_delta = b['irq']-a['irq']
            if irq_delta < 0 or delta.get('irq63_cpu1_delta') != irq_delta:
                raise ValueError('passive_irq_recomputation_mismatch')
            irqs.append(irq_delta)
        elif delta.get('irq63_cpu1_delta') is not None:
            raise ValueError('unobserved_irq_cannot_be_zero')
        durations.append(duration)
    return dict(kind='SAVED_NATIVE_PASSIVE_COUNTERS', native_snapshots_verified=24,
        comparable_counter_intervals=12, aggregate_cpu_busy_pct_range=[min(busy),max(busy)],
        target_interval_seconds_range=[min(durations),max(durations)],
        irq63_cpu1_observed_intervals=len(irqs), irq63_cpu1_delta_range=[min(irqs),max(irqs)] if irqs else None,
        application_goodput_mbps=None, controlled_aa_valid=False, zero_false_positive='UNKNOWN',
        promotion_allowed=False, new_measurements=0, physical_release_acceptance='UNKNOWN')


def evaluate_stage(root: Path, number: int) -> tuple[dict, dict | None]:
    paths = sorted((root/'artifacts/autoresearch').glob(f'stage{number}a*.json'))
    row = dict(stage=f'{number}A', state='MISSING', native_observation_verified=False)
    if not paths:
        return row, None
    if len(paths) != 1:
        row.update(state='AMBIGUOUS_RECEIPTS', receipt_count=len(paths))
        return row, None
    label = paths[0].relative_to(root).as_posix()
    pin = c.snapshot(root, label)
    try:
        data = c.read_json(root, label)
        cls = data.get('evidence_provenance_class',data.get('evidence_class','UNCLASSIFIED'))
        known={'CONFIRMED_LIVE_HARDWARE','CONFIRMED_STATIC_BINARY','SIMULATED_MODEL_ONLY',
               'GATE_RECALIBRATION','DOC_COMPLIANCE_AUDIT','DOCUMENTATION_SYNC',
               'STATISTICAL_AND_DOCS_GATE','UNCLASSIFIED'}
        row.update(receipt_sha256=pin['sha256'], source_class=cls if isinstance(cls,str) and cls in known else 'OTHER_OR_UNCLASSIFIED')
        if cls != 'CONFIRMED_LIVE_HARDWARE':
            row['state'] = 'NON_NATIVE_OR_UNCLASSIFIED'
            return row, pin
        if data.get('stage') != f'{number}A':
            raise ValueError('native_stage_identity_mismatch')
        if number == 905:
            captures = [binding(root, source) for source in data['native_captures']]
            if not captures:
                raise ValueError('native_discovery_capture_missing')
            results = [item for cap in captures for item in cap.get('results',[])]
            row['observation'] = dict(kind='SAVED_NATIVE_DISCOVERY',
                results_captured=len(results), successful_transports=sum(
                    item.get('exit_code') == 0 and item.get('timed_out') is False for item in results),
                application_goodput_mbps=None, promotion_allowed=False, new_measurements=0)
        elif number == 906:
            row['observation'] = replay_906(root,data)
        elif number in (908,909):
            row['observation'] = replay_passive(root,data)
        else:
            row['state'] = 'UNVERIFIED_NATIVE_DECLARATION'
            return row, pin
        row.update(state='SAVED_NATIVE_BYTES_AND_OBSERVATIONS_VERIFIED', native_observation_verified=True)
    except (OSError,ValueError,KeyError,TypeError,IndexError,OverflowError) as exc:
        reason=str(exc) if type(exc) is ValueError and re.fullmatch('[a-z_0-9]+',str(exc)) else 'saved_input_contract'
        row.update(state='INVALID_OR_UNAVAILABLE_NATIVE_EVIDENCE', native_observation_verified=False,
                   reason=type(exc).__name__ + ':' + reason)
        row.pop('observation',None)
    return row, pin


def evidence_ledger(root: Path) -> dict:
    rows, private_pins = [], []
    for number in range(905,935):
        row,pin = evaluate_stage(root,number)
        rows.append(row)
        if pin:
            private_pins.append(pin)
    return dict(stage_range='905A..934A', rows=rows, private_input_bindings=private_pins,
                available_stage_count=len(private_pins), missing_stages=[r['stage'] for r in rows if r['state']=='MISSING'],
                verified_native_stages=[r['stage'] for r in rows if r['native_observation_verified']],
                private_input_scope='Original saved inputs; raw captures withheld from public release',
                fresh_live_windows=0, physical_release_acceptance='UNKNOWN')


def source_manifests(root: Path) -> list[dict]:
    package = c.read_json(root,KIT_RECEIPT)
    members = package['release_source_members']
    if len(members) != 42 or len(set(members)) != 42:
        raise ValueError('expected42active_source_members')
    declared = {row['path']: row for row in package['sources']}
    manifests=[]
    for folder in KIT_DIRS:
        selected=[]
        for label in sorted(members):
            if not label.startswith(folder+'/'):
                continue
            source=c.snapshot(root,label)
            if (not source['available'] or source != declared.get(label)
                    or (root/label).is_symlink() or not label.endswith('.sh') and not (root/label).read_bytes().startswith(b'#!/bin/sh\n')):
                raise ValueError('active_source_changed_or_invalid')
            if any(part in label for part in ('/public_assets/','/public_release_','/repro/')):
                raise ValueError('historical_archive_must_not_enter_v23_manifest')
            selected.append(source)
        if not selected:
            raise ValueError('empty_source_manifest')
        label=folder+'/SHA256SUMS'
        text=''.join(row['sha256']+'  '+Path(row['path']).relative_to(folder).as_posix()+'\n' for row in selected)
        c.atomic_write(c.local(root,label),text)
        manifests.append(dict(**c.snapshot(root,label),members=selected))
    if sum(len(row['members']) for row in manifests) != 42:
        raise ValueError('unassigned_active_source')
    return manifests


def update_document(text: str, block: str, *, readme=False) -> str:
    text=re.sub(r'(?ms)^'+re.escape(HEADING)+r'\n.*?(?=^## |\Z)','',text)
    # Replace the bounded v22 delivery block while preserving its historical qualification elsewhere.
    if readme:
        text=re.sub(r'(?ms)^## Stages849A\.\.854A: offline v22 release\n.*?(?=^## |\Z)','',text)
    text=re.sub(r'<!-- doc-head:.*?-->','<!-- doc-head: Source-qualified evidence and v23 offline source release through940A -->',text,count=1,flags=re.S)
    output=text.rstrip()+'\n\n'+HEADING+'\n\n'+block.rstrip()+'\n'
    while len(output.splitlines()) >= 180 and '\n\n' in output:
        output=output.replace('\n\n','\n',1)
    if (len(output.splitlines()) >= 180 or output.count('<!-- doc-head:') != 1
            or output.count('<!-- /doc-head -->') != 1):
        raise ValueError('document_budget_or_header')
    return output


def release_block(ledger: dict, *, readme=False) -> str:
    prefix='docs/' if readme else ''
    observation={row['stage']:row.get('observation') for row in ledger['rows'] if row['native_observation_verified']}
    lines=['42 active source scripts: two guarded native transactions and40 retired legacy actuators;103 historical archive files are excluded.',
           'Defaults inspect only; explicit apply, exact identity, snapshot, real readback and verified rollback gate the supported transient operations.',
           'tc-less mode verifies the fq_codel default policy, not an existing active root qdisc. LTU native prerequisites and physical compatibility remain UNKNOWN.']
    if '906A' in observation:
        item=observation['906A'];lo,hi=item['receiver_goodput_mbps_range'];loss=item['loss_pct_range']
        lines.append(f"Saved906A:12 diagnostic A/A windows; receiver goodput{lo:.3f}..{hi:.3f}Mbps; loss{loss[0]:.1f}..{loss[1]:.1f}%; original gate{item['original_gate_verdict']}, no promotion.")
    for stage in ('908A','909A'):
        if stage in observation:
            item=observation[stage];low,high=item['aggregate_cpu_busy_pct_range']
            lines.append(f'Saved{stage}:24 native snapshots/12 passive intervals; aggregate CPU busy{low:.2f}..{high:.2f}%; application goodput and zero-FP remain UNKNOWN.')
    lines.extend([f"905A..934A: {ledger['available_stage_count']}/30 receipts available; {len(ledger['missing_stages'])} stages absent at this read. No new radio measurements were made.",
        f'[Source manifests]({prefix}STAGE937A_V23_ACTIVE_SOURCE_SHA256_MANIFESTS.md) and [qualified saved evidence]({prefix}STAGE938A_905_TO_934_VERIFIED_SAVED_MEASUREMENTS.md).'])
    return '\n'.join(lines)


def build(root: Path=ROOT) -> dict:
    root=Path(root).resolve()
    ledger=evidence_ledger(root)
    private_pins=list(ledger['private_input_bindings'])
    manifests=source_manifests(root)
    public_code=[c.snapshot(root,SELF),c.snapshot(root,COMMON)]
    if not all(row['available'] for row in public_code):
        raise ValueError('public_builder_sources_missing')
    reports={}
    first_sources=public_code+[c.snapshot(root,KIT_RECEIPT)]
    first_sources += [member for manifest in manifests for member in manifest['members']]
    first_sources += [{key:value for key,value in manifest.items() if key!='members'} for manifest in manifests]
    first=c.receipt(937,'v23 active source SHA256 manifests',first_sources)
    first.update(evidence_provenance_class='CONFIRMED_STATIC_BINARY',
        provenance_scope='Static executable-source bytes only; no firmware binary built or deployed',
        checksum_manifests=manifests,active_source_count=42,historical_archives_excluded=103,
        firmware_images_built=0,physical_acceptance='UNKNOWN')
    reports['937A']=c.save(root,STEMS[937],first,
        'The two SHA256SUMS files cover exactly42 active source scripts, not firmware images.\n'
        'Two native guarded transactions support bounded transient knobs;40 legacy actuators are explicitly retired.\n'
        'The103 immutable historical archive files are not v23 release members.\n'
        'Every input matches the current Stage935A source pin before checksums are emitted.\n'
        'No proprietary firmware bytes, flash, network command or native device action is included.\n'
        'Source compatibility is not hardware acceptance. Physical acceptance UNKNOWN.\n')
    second=c.receipt(938,'905A..934A qualified saved-observation ledger',public_code)
    second.update(ledger,evidence_provenance_class='CONFIRMED_STATIC_BINARY',
        provenance_scope='Offline byte binding and arithmetic replay; original native observations retain their separate source class',
        original_saved_inputs_rewritten=False,private_captures_published=False,physical_acceptance='UNKNOWN')
    reports['938A']=c.save(root,STEMS[938],second,release_block(ledger)+'\n\n'
        'CONFIRMED alone is never interpreted as measured hardware. Static, synthetic, documentation and unclassified receipts add no measured windows.\n'
        '905 discovery is distinct from906 diagnostic workload and908/909 passive telemetry; they are not pooled into a performance campaign.\n'
        '906 receiver bytes/ping counts/latencies and timing are recomputed from immutable native captures.\n'
        '908/909 CPU/IRQ deltas are recomputed from bound native counters with stable epochs and clocks.\n'
        'This checks supplied bytes, not instrument honesty, present radio state, calibration, treatment benefit or physical release acceptance.\n')
    for label,readme in [('README.md',True),('docs/PUBLIC_OVERVIEW.md',False)]:
        path=c.local(root,label)
        c.atomic_write(path,update_document(path.read_text(encoding='utf-8'),release_block(ledger,readme=readme),readme=readme))
    third_sources=public_code+[c.snapshot(root,p) for p in ('README.md','docs/PUBLIC_OVERVIEW.md',
        f'artifacts/autoresearch/{STEMS[937]}.json',f'artifacts/autoresearch/{STEMS[938]}.json')]
    third=c.receipt(939,'Public v23 evidence documentation sync',third_sources)
    third.update(evidence_provenance_class='CONFIRMED_STATIC_BINARY',
        provenance_scope='Offline documentation and source-manifest synchronization only',
        available_saved_stages=ledger['available_stage_count'],verified_native_stages=ledger['verified_native_stages'],
        missing_stages=ledger['missing_stages'],fresh_live_windows=0,physical_acceptance='UNKNOWN')
    reports['939A']=c.save(root,STEMS[939],third,
        'README and PUBLIC_OVERVIEW retain prior qualified claims and add the bounded v23 source release.\n'
        'Only raw-bound saved observations enter the public numeric summary; missing stages stay missing.\n'
        'Diagnostic A/A, passive counters, static sources and simulated data remain distinct.\n'
        'No new benchmark, physical promotion, device activation or publication is executed by this builder.\n'
        'Docs have fewer than180 lines and one paired initial doc-head. Physical acceptance UNKNOWN.\n')
    for pin in private_pins + first_sources:
        if c.snapshot(root,pin['path']) != pin:
            raise ValueError('input_changed_during_release_metadata_construction')
    return reports


if __name__=='__main__':
    data=build()
    print(json.dumps({'stages':list(data),'verified_native_stages':data['938A']['verified_native_stages'],
                      'available_saved_stages':data['938A']['available_stage_count'],
                      'physical_acceptance':'UNKNOWN'},indent=2))
