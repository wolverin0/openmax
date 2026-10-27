#!/usr/bin/env python3
"""Saved LTU symbol/model/loopback reconciliation, never a target or monitor executor."""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path
import re
import statistics
import struct
import sys
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from tools.autoresearch import stage525_530_common as h
from tools.re import ground_up_release_common as c

SCRIPT='tools/autoresearch/build_stage528a_ltu_dcxo_gps_tcxo_and_144window_reconciler.py'
OUT='artifacts/autoresearch/stage528a_ltu_dcxo_gps_tcxo_and_144window_reconciler.json'
DOC='docs/STAGE528A_LTU_DCXO_GPS_TCXO_AND_144WINDOW_RECONCILER.md'
SOURCES={485:'stage485a_qca988x_bmiss_and_csa_channel_switch_re.json',486:'stage486a_ltu_ad9361_fastlock_and_cal_table_re.json',
         502:'stage502a_ltu_dcxo_gps_tcxo_drift_monitor.json',515:'stage515a_ltu_dcxo_gps_vs_tcxo_4096qam_cfo_pareto.json',
         467:'stage467a_live_ltu110_round12_144window_autoresearch.json',470:'stage470a_ltu_12round_144window_champion_v10_receipt.json'}
PRODUCERS={486:'tools/re/build_stage486a_ltu_ad9361_fastlock_and_cal_table_re.py',502:'tools/firmware/build_stage502a_ltu_dcxo_gps_tcxo_drift_monitor.py',
           515:'tools/sim/run_stage515a_ltu_dcxo_gps_vs_tcxo_4096qam_cfo_pareto.py',467:'tools/bench/run_stage467a_live_ltu110_round12_144window_autoresearch.py',
           470:'tools/firmware/build_stage470a_ltu_12round_144window_champion_v10.py'}
PROOF='artifacts/verification/stage528a/ame_core_symbols.json'
PROOF_SHA256='d06dd22b47fe90ab21cb70daada6835855fe9b44f3136893c4de3d2721daf147'
AME_SHA256='fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2'
MANIFEST='firmware/ltu_safe_kit/ltu_5board_universal_manifest_v10.json'
CHAMPION='firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh'
WINDOWS=('A1','B1','A2','B2')


def require(ok,code):
    if not ok:raise ValueError(code)


def digest(value):
    require(type(value)is str and re.fullmatch('[0-9a-f]{64}',value)is not None,'sha256');return value


def verify_symbols(root,proof):
    """Recheck root's pinned metadata against actual ELF header and every file slice."""
    require(type(proof)is dict and type(proof.get('source'))is dict,'symbol_proof_object')
    data,pin=h.snapshot(root,proof['source']['path']);require(pin==proof['source'] and pin['sha256']==AME_SHA256,'held_module_pin')
    require(len(data)>=52 and data[:7]==b'\x7fELF\x01\x01\x01' and struct.unpack_from('<H',data,18)[0]==40,'ELF32_LE_ARM')
    elf=proof['elf'];require(type(elf)is dict and type(elf.get('bits'))is int and elf==dict(bits=32,little_endian=True,machine='ARM')
                           and type(elf['little_endian'])is bool,'elf_metadata')
    rows=proof['defined_sized_symbols'];require(type(rows)is list and len(rows)==38,'symbol_census_count')
    names=set()
    for row in rows:
        require(type(row)is dict and type(row.get('name'))is str and re.fullmatch('[A-Za-z0-9_]*(?:dcxo|tcxo)[A-Za-z0-9_]*',row['name'])is not None
                and row['name']not in names,'unique_symbol_name');names.add(row['name'])
        offset=c.integer(row['file_offset'],'file_offset',0,len(data));size=c.integer(row['bytes'],'symbol_size',1,len(data))
        require(offset+size<=len(data) and c.sha(data[offset:offset+size])==digest(row['sha256']),'symbol_slice_pin')
        require((row['type'],row['section'])in(('STT_FUNC','.text'),('STT_OBJECT','.data')),'sized_defined_symbol_kind')
        c.integer(row['section_offset'],'section_offset',0,len(data))
    prefix=sum(name.startswith('bbp_rf_dcxo_') for name in names)
    require(type(proof['broad_defined_sized_count'])is int and proof['broad_defined_sized_count']==len(rows) and
            type(proof['bbp_rf_dcxo_defined_sized_count'])is int and proof['bbp_rf_dcxo_defined_sized_count']==prefix==11,'census_metadata')
    all_rows=proof['all_matching_symbol_rows']
    require(type(all_rows)is list and len(all_rows)==38 and all(type(r)is dict for r in all_rows),'matching_symbol_rows')
    require(all(type(r.get('name'))is str for r in all_rows)and {r['name'] for r in all_rows}==names,'census_names')
    metadata={r['name']:(r['bytes'],r['type'])for r in rows}
    for row in all_rows:
        c.integer(row['section_index'],'defined_section',1,65535);c.integer(row['size'],'defined_size',1,len(data))
        require((row['size'],row['type'])==metadata[row['name']],'symbol_summary_join')
    return dict(status='PINNED_STATIC_SYMBOL_BYTES_ONLY',source=pin,elf=elf,broad_defined_sized_count=len(rows),bbp_rf_dcxo_defined_sized_count=prefix,
                symbols=rows,callable_abi_proven=False,gps_lock_proven=False,cfo_readback_proven=False,board_capability_proven=False),pin


def extract_literal(text,name):
    require(type(text)is str and len(text)<=2*1024*1024,'bounded_python_source')
    try:tree=ast.parse(text)
    except SyntaxError as exc:raise ValueError('source_syntax')from exc
    matches=[]
    for node in tree.body:
        targets=node.targets if isinstance(node,ast.Assign)else [node.target]if isinstance(node,(ast.AnnAssign,ast.AugAssign))else []
        if any(isinstance(t,ast.Name)and t.id==name for t in targets):matches.append(node)
    require(len(matches)==1 and isinstance(matches[0],(ast.Assign,ast.AnnAssign)) and isinstance(matches[0].value,ast.Constant)
            and type(matches[0].value.value)is str,'unique_literal_constant_required')
    return matches[0].value.value.replace('\r\n','\n').encode('utf-8')


def audit_monitor(text):
    require(type(text)is str and len(text)<=128*1024,'bounded_monitor_text')
    good_sync='SYNC_SOURCE="TCXO_DISCIPLINED_OR_GPS_LOCKED"'in text
    low='CFO_RISK_12X="LOW_WITHIN_0_25_PPM"'in text
    return dict(status='UNSAFE_EVIDENCE_DEFAULTS_PRESENT'if good_sync and low else'UNKNOWN_MONITOR_SEMANTICS',
                missing_log_assumes_good_sync=good_sync,missing_log_assumes_low_cfo=low,
                temperature_fallback_present='|| echo 48000'in text,uptime_fallback_present='|| echo 3600'in text,
                irq_fallback_present='63058438 5698000'in text,gps_lock_evidence='UNKNOWN',cfo_evidence='UNKNOWN',
                script_executed=False,monitor_remediated=False)


def audit_windows467(document,claim470):
    require(type(document)is dict and type(claim470)is dict,'receipt_objects')
    rounds=document['counterbalanced_rounds'];require(type(rounds)is list and 1<=len(rounds)<=64,'rounds')
    ids=set();rows=[]
    for r in rounds:
        require(type(r)is dict,'round_object');rid=c.integer(r['round'],'round_id',1,1000000)
        require(rid not in ids,'duplicate_round');ids.add(rid)
        windows=r['windows'];require(type(windows)is dict and set(windows)==set(WINDOWS),'ABAB_named_map')
        for key in WINDOWS:
            w=windows[key];require(type(w)is dict,'window_object')
            counters={k:c.integer(w[k],k,0,2**64-1)for k in('irq52_cpu0_count','irq52_cpu1_count','net_rx_softirq_cpu0','net_rx_softirq_cpu1')}
            rows.append(dict(round=rid,window=key,arm=key[0],rtt_avg_ms=h.number(w['rtt_avg_ms'],'rtt'),
                             busy_read_us=c.integer(w['busy_read_us'],'busy_read',0,1000000),tcp_early_retrans=c.integer(w['tcp_early_retrans'],'tlp',0,4),
                             reported_absolute_counters=counters))
    means={a:statistics.mean(w['rtt_avg_ms']for w in rows if w['arm']==a)for a in('A','B')}
    claimed=c.integer(claim470['total_live_measurement_windows'],'claimed_windows',0,1000000)
    campaigns=c.integer(claim470['total_live_campaigns'],'claimed_campaigns',1,1000000)
    claimed_rounds=c.integer(claim470['total_live_ab_rounds'],'claimed_rounds',0,1000000)
    summary=document['summary_metrics'];conflicts=[]
    for field,actual in [('total_rounds',len(rounds)),('total_windows',len(rows)),('cumulative_ltu110_live_windows',claimed)]:
        if c.integer(summary[field],field,0,1000000)!=actual:conflicts.append(field)
    require(type(document.get('live_ssh_connected'))is bool,'reported_connection_flag')
    return dict(available_named_rounds=len(rounds),available_direct_windows=len(rows),claimed_cumulative_windows=claimed,
                unlinked_claimed_windows=max(0,claimed-len(rows)),claimed_campaigns=campaigns,claimed_ab_rounds=claimed_rounds,
                claim_arithmetic_consistent=claimed_rounds*4==claimed and campaigns*3==claimed_rounds,summary_conflicts=conflicts,
                reported_rtt_means_ms=means,reported_rtt_delta_pct=h.delta(means['A'],means['B']),windows=rows,
                provenance_status='AMBIGUOUS_NATIVE_PROVENANCE_WITH_SYNTHETIC_FALLBACK',probe_scope='LOOPBACK_127_0_0_1_NOT_OTA',
                reported_live_ssh_connected=document['live_ssh_connected'],flag_excludes_partial_error_fallback=False,
                fallback_branch_actually_taken='UNKNOWN_NO_NATIVE_TRANSCRIPT_OR_EXIT',counter_deltas_epoch_qualified=False,
                historical_window_chain_complete=False,accepted_ota_windows=0)


def audit_v10(claim,manifest,producer_text,current_bytes):
    require(type(claim)is dict and type(manifest)is dict and type(current_bytes)is bytes,'v10_inputs')
    require(claim['script_path']==manifest['champion_script']==CHAMPION and claim['champion_version']==manifest['manifest_version']=='v10','v10_path_version')
    expected=digest(claim['script_sha256']);manifest_hash=digest(manifest['champion_script_sha256'])
    literal=extract_literal(producer_text,'CHAMPION_V10_SH_CONTENT');boards=manifest['boards']
    require(type(boards)is list and 1<=len(boards)<=32,'manifest_boards');ids=set();reported_live=[]
    for row in boards:
        require(type(row)is dict and type(row.get('board_id'))is str and re.fullmatch('0x[0-9a-f]{4}',row['board_id'])is not None
                and row['board_id']not in ids and type(row.get('model'))is str and bool(row['model']),'board_identity')
        ids.add(row['board_id']);require(type(row.get('live_bench_verified'))is bool,'board_verification_boolean')
        if row['live_bench_verified']:reported_live.append(row['model'])
    counts={k:c.integer(manifest[k],k,0,1000000)for k in('cumulative_live_campaigns','cumulative_live_ab_rounds','cumulative_live_windows')}
    return dict(recorded_v10_sha256=expected,manifest_sha256_claim=manifest_hash,recorded_claims_agree=expected==manifest_hash,
                current_script_sha256=c.sha(current_bytes),current_script_bytes=len(current_bytes),current_script_matches_v10=c.sha(current_bytes)==expected,
                current_producer_literal_sha256=c.sha(literal),current_producer_literal_bytes=len(literal),literal_matches_recorded_v10=c.sha(literal)==expected,
                old_v10_recovered=c.sha(literal)==expected,manifest_models=len(boards),manifest_reported_live_models=reported_live,
                manifest_cumulative_claims=counts,all_manifest_models_hardware_qualified=False,script_written_or_executed=False)


def audit_model515(document):
    keys=('mean_goodput_mbps','p99_latency_ms','dwell_4096qam_12x_pct','ldpc_retrans_rate_pct')
    rows={label:{k:h.number(document[source][k],k,0,100 if k.endswith('_pct')else 1e12)for k in keys}
          for label,source in [('baseline','free_running_tcxo_baseline'),('champion','gps_disciplined_dcxo_pareto_champion')]}
    return dict(status='UNCALIBRATED_SYNTHETIC_MODEL_NOT_MEASURED',reported_metrics=rows,
                recomputed_synthetic_goodput_gain_pct=h.delta(rows['baseline']['mean_goodput_mbps'],rows['champion']['mean_goodput_mbps']),
                measured_4096qam_or_cfo_threshold=False,model_reexecuted=False)


def build(root=ROOT):
    documents={};sources=[]
    for stage,name in SOURCES.items():documents[stage],pin=h.json_source(root,'artifacts/autoresearch/'+name);sources.append(pin)
    proof,pin=h.json_source(root,PROOF);sources.append(pin);require(pin['sha256']==PROOF_SHA256,'root_symbol_metadata_pin')
    static,source_pin=verify_symbols(root,proof);sources.append(source_pin)
    manifest,pin=h.json_source(root,MANIFEST);sources.append(pin)
    monitor_path=documents[502]['monitor_script']['path'];monitor,monitor_pin=h.snapshot(root,monitor_path);sources.append(monitor_pin)
    champion,champion_pin=h.snapshot(root,CHAMPION);sources.append(champion_pin)
    texts={}
    for stage,path in PRODUCERS.items():raw,pin=h.snapshot(root,path);sources.append(pin);texts[stage]=raw.decode('utf-8')
    saved_symbols=documents[486]['modules'][0]['dcxo_symbols']
    require(type(saved_symbols)is list and all(type(n)is str for n in saved_symbols),'saved_symbol_list')
    result=dict(named_source_correction=dict(stage485_modules=[r['module']for r in documents[485]['modules']],stage485_is_ltu_dcxo_source=False,
                                             actual_ltu_source_stage=486),
                static_symbols=static,saved486=dict(reported_capped_dcxo_tcxo_count=len(saved_symbols),producer_cap=30,
                    reported_names_are_broad_not_bbp_prefix=True,census_is_complete=False),
                monitor=audit_monitor(monitor.decode('utf-8')),model515=audit_model515(documents[515]),
                window_chain=audit_windows467(documents[467],documents[470]),v10=audit_v10(documents[470],manifest,texts[470],champion),
                causal_join_between_linux_loopback_and_dcxo_model_allowed=False,status='QUALIFIED_STATIC_AND_SAVED_EVIDENCE_WITH_GAPS',
                summary=dict(new_hardware_results=0,static_dcxo_tcxo_symbols=38,bbp_rf_dcxo_symbols=11,available_windows=12,unlinked_claimed_windows=132),
                gaps=['Static ARM symbol bytes do not prove callable ABI, GPS lock, oscillator control, board capability or measured CFO.',
                      'Monitor silence and synthetic temperature/IRQ fallbacks are unsafe evidence; never infer healthy clock discipline from absence of logs.',
                      '515 oscillator/EVM/throughput constants are uncalibrated model assumptions, not measured4096QAM/CFO limits.',
                      '467 probes loopback and allows parser/exception fallback even after a connection opened; the actual branch is unknown.',
                      'IRQ values are absolute phase snapshots, not before/after same-epoch per-window deltas.',
                      '144 is a cumulative claim: only12 named windows are directly present, without an authenticated historical chain or OTA proof.',
                      'Current shared script and current producer literal are separate hash observations; neither is silently relabeled the recordedv10.'])
    result['monitor']['matches_recorded_script_sha256']=monitor_pin['sha256']==digest(documents[502]['monitor_script']['sha256'])
    result['summary']['available_windows']=result['window_chain']['available_direct_windows']
    result['summary']['unlinked_claimed_windows']=result['window_chain']['unlinked_claimed_windows']
    result['monitor']['reported_cfo_threshold_ppm']=h.number(documents[502]['cfo_4096qam_thresholds']['max_cfo_ppm_for_4096qam_12x'],'cfo_threshold')
    result['producer_anchors']=[c.anchors(Path(root)/PRODUCERS[486],['syms.matching(r"dcxo|tcxo", 30)'],root),
        c.anchors(Path(root)/PRODUCERS[467],['ping -Q 0xb8 -c 5 -i 0.2 127.0.0.1','rtt_avg_ms = 0.198 if default_tlp == 3 else 0.236','except Exception:'],root),
        c.anchors(Path(root)/PRODUCERS[515],['residual_cfo_hz = 12.0 if use_gps_dcxo_discipline else 420.0','base_evm_db = -41.2 if use_gps_dcxo_discipline else -35.8'],root)]
    text='''<!-- doc-head: Stage528A LTU static DCXO census, monitor provenance and cumulative-window limits -->
Symbols, synthetic models, loopback summaries and board claims remain separate evidence.
<!-- /doc-head -->

# Stage528A

Parent: fixed525A..530A offline RE1/control-boundary queue in BENCH_PLAN.
Run `python tools/autoresearch/build_stage528a_ltu_dcxo_gps_tcxo_and_144window_reconciler.py`.
No monitor/model/producer/firmware execution, device/network access or shared-script edit.

## Which source and which symbols?

Named485 is QCA988x WA/XC UMAC bmiss/CSA research, not LTU DCXO.
Actual486 uses ame_core.ko and syms.matching(r"dcxo|tcxo",30): a capped broad list,
not30 bbp_rf_dcxo functions or a complete census. Root's pinned held ELF32LE ARM
ame_corefe5d489e... contains38 sized defined DCXO/TCXO symbols, including11 with
bbp_rf_dcxo_ prefix. This audit checks actual ELF attributes and every file slice
against root's metadata hashes. It does not repeat symbol decoding or execute code.
Names/static bytes do not establish a callable ABI, GPS lock, measured CFO,
TCXO quality, analog pin topology or universal board oscillator capability.

## Monitor and synthetic model are not clock measurements

502's shell monitor labels an empty DCXO log TCXO_DISCIPLINED_OR_GPS_LOCKED and
LOW_WITHIN_0_25_PPM. Temperature48000, uptime3600 and an IRQ line have fallback
values. Silence or fabricated fallback values cannot establish synchronization.
The audit leaves GPS/CFO evidence UNKNOWN and does not run or repair the monitor.
The0.25ppm/4096QAM threshold is reported, not empirically validated here.
515 uses synthetic CFO starts12/420Hz, EVM bases-41.2/-35.8dB and hardcoded
throughput/latency tiers in its SimPy/NSGA-II parameter search. Its saved baseline
409.73 and champion618Mbps are model results, not measured RF or LTU CFO limits.
No causal link joins this static/model work to Linux latency or IRQ summaries.

## Twelve present windows versus144 cumulative claims

467 supplies three named A1/B1/A2/B2 maps,12 windows. 470/manifest claim12
campaigns,36 AB rounds and144 cumulative windows;132 are not linked by this input.
This arithmetic is not144 accepted experiments or144 measured OTA windows.
PROBE_R12_CMD pings127.0.0.1, so its RTT is loopback, not a radio-link probe.
The parser defaults RTT to0.236/0.198ms; an except branch can synthesize complete
rounds. live_ssh_connected=True does not exclude a later failure/fallback. The
actual branch and raw exit/stdout are unknown; the audit does not allege which ran.
IRQ counters are absolute phase values without per-window before/after boot epochs.
Busy-read/TLP values also change together; no DCXO/GPS/TCXO cause follows.

## Version and board claims

470/manifest record v10 SHA28ba77b4...; the current shared script is hashed
separately at the report cutoff. CHAMPION_V10_SH_CONTENT is extracted as an AST literal,
never imported/generated; its digest is independently compared with the recorded
hash. The literal can match even while the current shared script differs.
The JSON keeps both observations; digest equality identifies held bytes,
not authenticated historical execution or hardware acceptance.
The filename says5board, but the manifest lists six models. Only LTU-Lite has a
reported live flag, which itself is not independent hardware qualification. No
other model inherits LTU-Lite evidence or a presumed GPS/DCXO capability.
Current producer/source/proof/script hashes are inventory, not authenticated
historical execution provenance. E2 NOT_ACCEPTED. Decision: KEEP qualified audit.
'''
    return h.finish(root,528,SCRIPT,OUT,DOC,text,result,sources)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);args=p.parse_args(argv)
    print(json.dumps(build(args.root)['summary']));return 0


if __name__=='__main__':raise SystemExit(main())
