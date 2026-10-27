#!/usr/bin/env python3
"""Bounded saved-text/static-metadata audit; no patch, payload export or device executor."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.autoresearch import stage525_530_common as h
from tools.re import ground_up_release_common as c

SCRIPT='tools/autoresearch/build_stage526a_xtensa_ram_canary_pb040_pb050_abi_auditor.py'
OUT='artifacts/autoresearch/stage526a_xtensa_ram_canary_pb040_pb050_abi_auditor.json'
DOC='docs/STAGE526A_XTENSA_RAM_CANARY_PB040_PB050_ABI_AUDITOR.md'
S403='artifacts/autoresearch/stage403a_live_wa_pb040_ram_canary_and_nfcal_r43_45.json'
S507='artifacts/autoresearch/stage507a_live_wa_pb050_rc_probe_dampen_and_slot_r50_52.json'
SPEC='artifacts/physical_boundary/pb040_sgmt_surgical_patch_spec_20261025.json'
PROOF='artifacts/verification/stage526a/held_vendor_sgmt.json'
P403='tools/benchmarks/run_stage403a_live_wa_pb040_ram_canary_and_nfcal_r43_45.py'
P507='tools/benchmarks/run_stage507a_live_wa_pb050_rc_probe_dampen_and_slot_r50_52.py'
P311='tools/benchmarks/run_stage311a_to_316a_wa_megamission.py'
TARGET='/lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin'
TMP040='/tmp/firmware-2-pb040.bin';TMP050='/tmp/firmware-2-pb050.bin'
CHECKSUM_NAMES={'firmware-N.bin','athwlan','otp','codeswap','board-N.bin','board'}
OLD_AP='athwlan_AR9888v2_ptmp_ap_bin'


def require(ok,code):
    if not ok:raise ValueError(code)


def hex_text(value,digits):
    require(type(value)is str and re.fullmatch('[0-9a-f]{'+str(digits)+'}',value)is not None,'canonical_hex_required')
    return value


def audit_readback(text,*,expected_sha256,expected_checksums):
    """Expected values bind caller assertions only; complete text is not authenticated runtime."""
    require(type(expected_sha256)is dict and bool(expected_sha256) and set(expected_sha256)<={TARGET,TMP040,TMP050},'expected_hash_paths')
    require(type(expected_checksums)is dict and {'firmware-N.bin','athwlan'}<=set(expected_checksums)<=CHECKSUM_NAMES,'expected_checksum_keys')
    for value in expected_sha256.values():hex_text(value,64)
    for value in expected_checksums.values():hex_text(value,8)
    hashes={};checksums={};issues=[];ignored=0
    valid=type(text)is str and 0<len(text)<=65536
    if valid:
        try:text.encode('utf-8')
        except UnicodeError:valid=False
        valid=valid and all(ord(ch)>=32 or ch in '\t\r\n' for ch in text) and len(text.splitlines())<=512
    if not valid:issues.append('MISSING_OR_INVALID_BOUNDED_TEXT')
    else:
        for line in text.splitlines():
            line=line.strip()
            if not line:continue
            token=line.split()[0]
            if token in CHECKSUM_NAMES:
                match=re.fullmatch(re.escape(token)+r'[ \t]+([0-9a-fA-F]{8})',line)
                if not match:issues.append('MALFORMED_CHECKSUM');continue
                if token in checksums:issues.append('DUPLICATE_CHECKSUM')
                else:checksums[token]=match[1].lower()
            elif re.match(r'[0-9a-fA-F]+[ \t]+',line) or any(path in line for path in (TARGET,TMP040,TMP050)):
                match=re.fullmatch(r'([0-9a-fA-F]{64})[ \t]+(/[^ \t]+)',line)
                if not match or match[2] not in (TARGET,TMP040,TMP050):issues.append('MALFORMED_OR_UNEXPECTED_HASH_PATH');continue
                if match[2] in hashes:issues.append('DUPLICATE_HASH_PATH')
                else:hashes[match[2]]=match[1].lower()
            else:ignored+=1
    checksum_match={k:checksums.get(k)==v for k,v in expected_checksums.items()}
    hash_match={k:hashes.get(k)==v for k,v in expected_sha256.items()}
    if not all(checksum_match.values()):issues.append('MISSING_OR_MISMATCHED_EXPECTED_CHECKSUM')
    if not all(hash_match.values()):issues.append('MISSING_OR_MISMATCHED_EXPECTED_SHA256')
    return dict(status='UNKNOWN' if issues else 'CONSISTENT_SAVED_READBACK',checksums=checksums,file_sha256=hashes,
                expected_checksum_matches=checksum_match,expected_sha256_matches=hash_match,reason_codes=sorted(set(issues)),
                ignored_line_count=ignored,native_loaded_payload_bound=False,bind_reload_execution_proven=False)


def configured_windows(document,round_id):
    require(type(document)is dict and type(document.get('rounds'))is list,'round_document')
    rounds=[r for r in document['rounds'] if type(r)is dict and r.get('round_id')==round_id]
    require(len(rounds)==1,'unique_round_required');windows=rounds[0].get('windows')
    require(type(windows)is list and all(type(w)is dict for w in windows) and
            [w.get('window') for w in windows]==['A1','B1','A2','B2'],'ABAB_order')
    rows=[]
    for w in windows:
        require(w.get('arm')==w['window'][0] and type(w.get('knob_readback'))is dict,'configured_window_schema')
        cfg=w['knob_readback'];reg=cfg['bb_timing_29e00_hex']
        require(type(reg)is str and re.fullmatch('0x[0-9a-f]{8}',reg)is not None,'configured_register_hex')
        row=dict(window=w['window'],configured_register_value=reg,nf_cal_period=c.integer(cfg['nf_cal_period'],'nf',1,3600),
                 getter_status='NOT_RETAINED_CONFIGURED_DICT_ONLY')
        if 'active_fw_stats_poll' in cfg:row['active_fw_stats_poll']=c.integer(cfg['active_fw_stats_poll'],'poll',0,1)
        rows.append(row)
    return rows


def old_ap_segments(spec):
    require(type(spec)is dict,'spec_object');hex_text(spec['source_umac_sha256'],64)
    image=spec['bmi_lz_roundtrip_verification']['images'][OLD_AP];segments=image['segments']
    require(type(segments)is list and [s.get('segment_index') for s in segments]==[0,1,2,3],'old_vendor_segments')
    for s in segments:
        c.integer(s['segment_index'],'segment',0,3);c.integer(s['decoded_size_bytes'],'decoded_size',1,32*1024*1024)
        require(type(s['destination_hex'])is str and re.fullmatch('0x[0-9a-f]{8}',s['destination_hex'])is not None,'segment_address')
        hex_text(s['decoded_sha256'],64)
    hex_text(image['orig_container_sha256'],64)
    return image,segments


def audit(obj403,obj507,spec):
    require(type(obj403)is dict and type(obj507)is dict,'receipt_objects')
    b40=obj403['pb040_live_ram_canary_verification'];b50=obj507['pb050_live_ram_seg2_verification']
    require(type(b40)is dict and type(b50)is dict,'verification_objects')
    require(b40['target_firmware_file']==b50['target_firmware_file']==TARGET and
            b40['volatile_staging_file']==TMP040 and b50['volatile_staging_file']==TMP050,'canonical_firmware_paths')
    stock=hex_text(b40['stock_firmware_sha256'],64);patch40=hex_text(b40['patched_firmware_sha256'],64);patch50=hex_text(b50['patched_firmware_sha256'],64)
    endpoints40={name:audit_readback(b40.get(key),expected_sha256={TARGET:patch40,TMP040:patch40},expected_checksums=b40['patched_fw_checksums'])
                 for name,key in [('ap','ap_20_fw_checksums_readback'),('cpe','cpe_250_fw_checksums_and_wmi_readback')]}
    cpe_stock=audit_readback(b40.get('cpe_250_fw_checksums_and_wmi_readback'),expected_sha256={TARGET:stock,TMP040:patch40},expected_checksums=b40['stock_fw_checksums'])
    endpoints50={name:audit_readback(b50.get(key),expected_sha256={TMP050:patch50},expected_checksums=b50['pb050_fw_checksums'])
                 for name,key in [('ap','ap_20_fw_checksums_readback'),('cpe','cpe_250_fw_checksums_readback')]}
    claim=b50['seg2_rc_probe_patch']
    require(type(claim)is str and len(claim)<=512,'pb050_claim_text')
    match=re.fullmatch(r'Segment 2 \(\.data vaddr=(0x[0-9a-f]{8}), file_off=(0x[0-9a-f]+), \.lit4=(0x[0-9a-f]{8})\): (0x[0-9a-f]+) \(([0-9]+)ms\) -> (0x[0-9a-f]+) \(([0-9]+)ms\)',claim)
    require(match is not None and int(match[4],16)==int(match[5]) and int(match[6],16)==int(match[7]),'pb050_claim_arithmetic')
    c.integer(int(match[2],16),'claimed_file_offset',0,0xffffffff)
    for i in (5,7):c.integer(int(match[i]),'claimed_ms',1,1000000)
    image,segments=old_ap_segments(spec);r43=configured_windows(obj403,'S403A-R43');r50=configured_windows(obj507,'S507A-R50')
    changed=[k for k in ('nf_cal_period','active_fw_stats_poll') if {r.get(k) for r in r50[::2]}!={r.get(k) for r in r50[1::2]}]
    return dict(pb040=dict(endpoints=endpoints40,cpe_stock_consistency=cpe_stock,
                          both_endpoints_support_patched_target_text=all(v['status']=='CONSISTENT_SAVED_READBACK' for v in endpoints40.values()),
                          r43_configured_windows=r43,register_getter_status='UNKNOWN_NO_RETAINED_GETTER_TEXT',
                          direct_host_register_write_confounds_sgmt_effect=True,canary_log_or_exact_patch_payload_proof='NOT_RETAINED'),
                pb050=dict(endpoints=endpoints50,target_path_sha256_status={k:'PRESENT_IN_TEXT' if TARGET in v['file_sha256'] else 'MISSING' for k,v in endpoints50.items()},
                          address_claims=dict(data_vaddr=match[1],file_offset=match[2],lit4_vaddr=match[3],from_ms=int(match[5]),to_ms=int(match[7]),
                                              address_domains_interchangeable=False),r50_configured_windows=r50,other_changed_configured_fields=changed,
                          isolated_patch_effect_proven=False,patch_bind_reload_payload_proof='NOT_RETAINED'),
                vendor_context=dict(source_umac_sha256=spec['source_umac_sha256'],old_vendor_ap_segment2_vaddr=segments[2]['destination_hex'],
                                    claimed_ct_data_minus_old_vendor_segment2=int(match[1],16)-int(segments[2]['destination_hex'],16),
                                    same_binary_build_or_abi_proven=False,offset_transplant_allowed=False),
                native_abi_acceptance=False,status='QUALIFIED_STATIC_AND_SAVED_TEXT_WITH_GAPS',summary=dict(new_hardware_results=0),
                gaps=['Readback strings have no independently retained command exit/boot/bind/reload acquisition chain.',
                      'Exact stock/patched CT payload bytes are not supplied by the pinned403/507 receipts; this is not a global absence claim.',
                      'Checksum/name agreement and staging SHA do not bind the currently executing payload or verify a RAM patch.',
                      'R43 explicitly configures a host register write, so a matching value cannot isolate SGMT causality.',
                      'R50 also changes NF calibration and stats polling; no patch-only counterfactual is retained.',
                      'Named g_rc globals and a hardcoded candidate grid are not native offsets, field types or ABI acceptance.'],
                boundary=dict(target_access=False,physical_acceptance=False,firmware_exported=False,patch_generated=False))


def verify_held_proof(root,proof,spec):
    require(type(proof)is dict and proof.get('symbol')==OLD_AP,'held_proof_schema')
    pins=[]
    for key in ('source','decoder'):
        row=proof[key];data,pin=h.snapshot(root,row['path']);require(pin==row,'held_'+key+'_pin');pins.append(pin)
        if key=='source':source=data
    require(proof['source']['sha256']==spec['source_umac_sha256'],'old_vendor_source_mismatch')
    offset=c.integer(proof['symbol_file_offset'],'symbol_offset',0,len(source));size=c.integer(proof['sgmt_bytes'],'sgmt_size',1,len(source))
    require(offset+size<=len(source) and c.sha(source[offset:offset+size])==proof['sgmt_sha256'],'held_container_slice')
    image,segments=old_ap_segments(spec);meta=proof['metadata'];payloads=proof['payload_segments']
    expected=[dict(destination=hex(int(s['destination_hex'],16)),bytes=s['decoded_size_bytes'],sha256=s['decoded_sha256']) for s in segments]
    require(payloads==expected and meta['container_sha256']==proof['sgmt_sha256']==image['orig_container_sha256']
            and type(meta['schema_version'])is int and meta['schema_version']==1 and
            meta['consumed_bytes']==meta['container_size']==size and meta['decoded_total']==sum(s['bytes'] for s in expected),'held_decoded_metadata')
    records=[r for r in meta['records'] if r.get('kind')=='PAYLOAD']
    require([dict(destination=hex(r['destination']),bytes=r['decoded_size'],sha256=r['decoded_sha256']) for r in records]==expected,'held_record_metadata')
    return dict(status='STATIC_ROOT_DECODING_NOT_CT_ABI',source=proof['source'],decoder=proof['decoder'],container_sha256=proof['sgmt_sha256'],
                container_bytes=size,symbol_file_offset=offset,payload_segments=expected,decoding_reexecuted=False,
                target_execution_proven=False,ct_firmware_context_equivalent=False),pins


def build(root=ROOT):
    a,pa=h.json_source(root,S403);b,pb=h.json_source(root,S507);spec,ps=h.json_source(root,SPEC);proof,pp=h.json_source(root,PROOF)
    result=audit(a,b,spec);result['held_vendor_static_proof'],pins=verify_held_proof(root,proof,spec)
    paths=(P403,P507,P311,'artifacts/verification/stage526a/fullrea_run.json','artifacts/verification/stage526a/fullrea_bmi_loader.txt')
    sources=[pa,pb,ps,pp]+pins+[h.snapshot(root,p)[1] for p in paths]
    fullrea,_=h.json_source(root,paths[-2]);body,_=h.snapshot(root,paths[-1])
    require(type(fullrea['exit_code'])is int and fullrea['exit_code']==0 and fullrea['input_sha256']==proof['source']['sha256']
            and fullrea['output_sha256']==c.sha(body),'static_fullrea_binding')
    require(b'BMILZStreamStart' in body and b'BMILZData' in body,'static_loader_call_anchors')
    result['static_loader']=dict(status='SAVED_HOST_STATIC_HELPER_OUTPUT_NOT_TARGET_EXECUTION',helper_sha256_reported=hex_text(fullrea['helper_sha256'],64),
                                 helper_reexecuted=False,current_external_helper_reverified=False,register_write_intrinsic_proven=False)
    result['producer_anchors']=[c.anchors(Path(root)/P403,['f"echo {bb_timing_29e00_hex}', 'rb["ap_extra_readback"]', 'ap_fw_chk = rpc'],root),
                                c.anchors(Path(root)/P507,['r50_arm_a =','r50_arm_b =','ap_fw_chk = rpc'],root),
                                c.anchors(Path(root)/P311,['cfg = readback["configured"]','"knob_readback": cfg'],root)]
    text='''<!-- doc-head: Stage526A saved PB040/PB050 checksums and static vendor SGMT boundaries -->
Endpoint-specific saved text is not proof of loaded payload, patch acceptance or ABI.
<!-- /doc-head -->

# Stage526A

Parent: fixed525A..530A offline RE1/control-boundary queue in BENCH_PLAN.
Run `python tools/autoresearch/build_stage526a_xtensa_ram_canary_pb040_pb050_abi_auditor.py`.
No producer import, decoder/helper re-execution, target/network/subprocess action,
firmware payload export, patch construction, flash or regulatory change occurs.

## Saved endpoint differences

| Source | Diagnostic checksums firmware-N / athwlan | SHA256 path evidence | Limit |
| --- | --- | --- | --- |
|403 AP |912bcb63 /278d2d76 |/lib and/tmp candidate8d50c1ce... |Saved consistency, no native acquisition chain |
|403 CPE |3e4cf97f /477a6960 |/lib stock398e4380...;/tmp candidate8d50c1ce... |Does not support both ends patched |
|507 AP/CPE |92363606 /12b29d01 |Only/tmp candidatea49160ff... |No/lib SHA or bind/reload/loaded-byte chain |

The strict parser requires complete expected checksum and exact canonical SHA paths.
Duplicate entries, truncated hex, unexpected hash paths, controls, missing fields or
mismatches yield UNKNOWN, never PASS. Raw ignored log lines are not echoed.
Matching text means CONSISTENT_SAVED_READBACK only, not a runtime or ABI verdict.
Neither a filename checksum nor a/tmp SHA proves the currently executing payload.
403/507 record strings from check=False stdout; actual native exit codes are absent.
Exact stock/patched CT payload bytes are not supplied by these pinned receipts.
This is not a claim that such files are absent from every repository or device.

## Register and counterfactual boundary

403 claims a0x13721320->0x13761320 INI shadow. R43 windows retain configured
values only; the helper serializes cfg and drops ap_extra_readback/cpe_extra_readback.
No raw reg_value getter is retained in the PB040 block. Furthermore producer403
directly writes reg_addr0x29e00/reg_value for each arm, so even a genuine matching
getter could not isolate the SGMT patch as its cause. Canary log/payload proof is absent.
R50 simultaneously changes nf_cal_period30->120 and active_fw_stats_poll0->1;
the diagnostic snapshot is taken before trials. No patch-only counterfactual exists.

## Address domains and held static proof

507 reports CT.data vaddr0x0040c140, file offset0x3b1d, .lit4 vaddr0x00980754
and2000->4000ms. They remain distinct reported domains and units, not a patch recipe.
The held Stage17 airOS8.5.12 vendor UMAC46525dc6... has AP segment2 at0x0040d140,
4096 bytes away from the claimed CT address. It is not the CT firmware-2.bin build.
Root's pinned bounded decode metadata has four payloads,309464 decoded bytes,
container55e9c94a.../251681B, matching the old vendor spec. This build rechecks the
actual UMAC container slice, decoder hash and metadata, without repeating decoding
or serializing payload bytes. Metadata consistency is STATIC_ROOT_DECODING_NOT_CT_ABI.
The saved host fullrea BMIFastDownload relocation summary names BMILZStreamStart
and BMILZData. It proves neither native execution nor a0x29e00 write intrinsic.
The external helper hash is reported by its saved receipt, not reverified here.
Named g_rc globals or hardcoded candidate grids do not establish offsets/types/ABI.
No offset is transplanted between vendor/CT images; native ABI acceptance stays false.

Inputs, producer source, old spec, held UMAC/decoder and saved static proof are hashed.
Current bytes are not authenticated historical executed source. Missing native
boot/build/payload/exit/acquisition provenance remains missing. E2 NOT_ACCEPTED.
Decision: KEEP qualified contradiction audit; no new hardware result or RF gain.
'''
    return h.finish(root,526,SCRIPT,OUT,DOC,text,result,sources)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args(argv);print(json.dumps(build(args.root)['summary']));return 0


if __name__=='__main__':raise SystemExit(main())
