#!/usr/bin/env python3
"""800-stage horizon: bounded filename catalog plus frozen evidence readiness."""
from collections import Counter
import os
from pathlib import Path
import re
import stat
import sys
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.sim import stage787_792_common as h
c=h.c
SCRIPT='tools/verify/build_stage791a_800stage_horizon_readiness_audit.py'
OUT='artifacts/autoresearch/stage791a_800stage_horizon_readiness_audit.json'
DOC='docs/STAGE791A_800STAGE_HORIZON_READINESS_AUDIT.md'
INVENTORY='artifacts/verification/stage791a/horizon_inventory.json'
PRIOR={787:'artifacts/autoresearch/stage787a_wa_vht20_78mbps_vs_vht40_channel_efficiency_sim.json',
       788:'artifacts/autoresearch/stage788a_guarida_backbone_5210_to_5220_shift_pareto.json',
       789:'artifacts/autoresearch/stage789a_bench_and_tower_rogue_dhcp_audit_ledger.json',
       790:'artifacts/autoresearch/stage790a_panel1_guarida_84_20h_zero_drop_reliability_model.json',
       529:'artifacts/autoresearch/stage529a_500stage_cross_lane_artifact_integrity_gate.json',
       530:'artifacts/verification/stage530a_codex_530stage_master_gate_receipt.json'}
SOURCES=tuple(PRIOR.values())+(INVENTORY,)
MAX_ENTRIES=20000;MAX_FILES=5000
FOLDERS=(('artifacts/autoresearch','.json','RECEIPT_BASENAME'),('docs','.md','DOCUMENT_BASENAME'),
         ('tests','.py','TEST_BASENAME_NOT_FULL_COVERAGE'))
DOC_TEXT='''<!-- doc-head: Stage791A bounded800-horizon artifact catalog and qualified readiness HOLD -->
File labels, local tests and saved claims never establish800 accepted physical experiments.
<!-- /doc-head -->

# Stage791A

Parent: fixed787A..792A offline RE1 support in BENCH_PLAN.
Run `python tools/verify/build_stage791a_800stage_horizon_readiness_audit.py`.
No radio, network, producer, runtime-health check or migration is executed.

## Explicit catalog scope

On first creation, enumerate top-level artifacts/autoresearch stage*.json,
docs/STAGE*.md and tests/test_stage*.py basenames with numeric IDs1..800.
At most20000 directory entries and5000 matched regular files, no reparse/symlink
traversal. Missing directories, exclusions and limits are retained as scan issues.
Higher-numbered stage files are counted separately. Nested archives, scripts,
alternate naming schemes and consolidated-test full coverage are not inferred.
This catalog does not parse/hash every named receipt or validate all their schemas,
document bodies, five pillars, provenance, command exits or experiment acceptance.
Generic receipts and stages covered inside aggregate files may not appear by name.
Presence is neither completion nor a claim that absent labels mean absent research.

The catalog is retained at artifacts/verification/stage791a/horizon_inventory.json
and frozen with the six saved audit/model receipts. Replays reuse that cutoff,
not a continuously updated repository inventory. No stage source or historical
document is rewritten to manufacture milestone readiness.

## Evidence readiness

787..790 provide local sensitivity/ledger enabling work with explicit unknowns.
The VHT20 peak uses a composite rate and lacks per-window width readback;
the5210->5220 shift lacks a native209.5M counter and calibration; DHCP runtime
eradication/persistence is unproven; snapshots do not establish20h zero-outage
surveillance or a packet denominator for WDS reliability.

529 is reused as a dated repository-wide structural-policy audit with its original
FAIL_OR_UNASSESSED status and retained historical/vendor/schema/budget/drift
findings. It is not relabeled current compliance or rerun as a prerequisite.
530 preserves207 tests:205PASS/2source-driftFAIL, masterINCOMPLETE, wiring-gate0.
Its inherited failures are separate from this new queue's792 local regression.

800 acceptance additionally needs an authoritative stage-to-deliverable/physical
acceptance manifest, native data/firmware/config/boot/epoch chains, missing trials,
reviewed regulatory/recovery prerequisites and resolved relevant evidence gaps.
No complete800-stage acceptance manifest is supplied by these inputs. Readiness
therefore remains HOLD_EVIDENCE_GAPS; accepted-stage count is UNKNOWN (null),
not zero,800 or the count of basenames. Local tooling can pass while the milestone
remains NOT_ACCEPTED. No new hardware work is authorized by this audit.
KEEP the readiness audit and concrete missing-evidence ledger. E2 NOT_ACCEPTED.
'''


def catalog(root=ROOT):
    root=c.local_path(root).resolve();rows=[];issues=[];entries_seen=0;higher=0
    for folder,suffix,role in FOLDERS:
        directory=c.local_path(root/folder)
        try:
            with os.scandir(directory) as stream:
                for entry in stream:
                    entries_seen+=1
                    if entries_seen>MAX_ENTRIES:
                        issues.append(dict(reason='ENTRY_LIMIT'));return catalog_result(rows,issues,entries_seen,higher)
                    match=re.match(r'^(?:test_)?stage(\d{1,5})([a-z]*)(?:_|\.)',entry.name,re.I)
                    if not match or Path(entry.name).suffix.lower()!=suffix:continue
                    info=entry.stat(follow_symlinks=False)
                    label=f'{folder}/{entry.name}'
                    if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
                        issues.append(dict(path=label,reason='REPARSE_OR_SYMLINK_NOT_FOLLOWED'));continue
                    if not stat.S_ISREG(info.st_mode):continue
                    number=int(match[1])
                    if number>800:higher+=1;continue
                    if number<1:continue
                    if len(rows)>=MAX_FILES:
                        issues.append(dict(reason='FILE_LIMIT'));return catalog_result(rows,issues,entries_seen,higher)
                    rows.append(dict(path=label,numeric_id=number,label=str(number)+match[2].upper(),role=role))
        except OSError as exc:issues.append(dict(path=folder,reason=type(exc).__name__))
    return catalog_result(rows,issues,entries_seen,higher)


def catalog_result(rows,issues,entries,higher):
    numbers=sorted({r['numeric_id']for r in rows});labels=sorted({r['label']for r in rows})
    return dict(scope='TOP_LEVEL_BASENAMES_ONLY_HELD_CUTOFF',rows=sorted(rows,key=lambda r:r['path']),
        numeric_ids_present=numbers,stage_labels_present=labels,numeric_ids_without_matching_basename=sorted(set(range(1,801))-set(numbers)),
        role_counts=dict(Counter(r['role']for r in rows)),entries_examined=entries,above800_matched_files=higher,
        issues=issues,receipt_schema_validity='NOT_ASSESSED_BY_FILENAME_CATALOG',accepted_stage_count=None,
        complete_manifest=False)


def assess(receipts,inventory):
    for stage in PRIOR:
        if stage not in receipts or not isinstance(receipts[stage],dict):raise ValueError('required_receipt_object')
    r=receipts
    checks=[dict(question='Local787..790 enabling deliverables',status='QUALIFIED_OFFLINE_TOOLING',
                 evidence=[r[n]['status']for n in range(787,791)]),
        dict(question='VHT20/VHT40 physical interference comparison',status='MISSING_NATIVE_WIDTH_AND_MATCHED_TREATMENT',
             evidence=r[787]['saved_anchor']['width_readback_proven']),
        dict(question='209.5M subframes linked to actual channel-shift trial',status='MISSING_COUNTER_COHORT_AND_CALIBRATION',
             evidence=r[788]['evidence']['subframe_provenance']),
        dict(question='Bench/tower DHCP eradication and persistence',status='UNPROVEN_RUNTIME',evidence=r[789]['eradication_verdict']),
        dict(question='Panel1 complete outage surveillance and empirical bound',status='MISSING_NATIVE_SURVEILLANCE',
             evidence=r[790]['actual_event_surveillance']),
        dict(question='Dated529 repository structural policy',status=r[529]['status'],evidence=r[529]['summary']),
        dict(question='Historical530 acceptance',status=r[530]['status'],evidence=r[530]['pytest_counts']),
        dict(question='Authoritative800-stage acceptance manifest',status='NOT_SUPPLIED',evidence=None)]
    return dict(readiness='HOLD_EVIDENCE_GAPS',milestone_acceptance='NOT_ACCEPTED',accepted_stage_count=None,
        checks=checks,catalog_scan_issues=inventory['issues'],physical_promotion_authorized=False,
        evidence_gap_actions=['Link authoritative native sources and epochs; retain synthetic/loopback/literal classifications.',
            'Supply per-stage acceptance manifest independent of filenames and claim labels.',
            'Resolve required schema/policy/revision findings within their own scope before any physical promotion.'])


def build(root=ROOT):
    root=c.local_path(root).resolve();path=c.local_path(root/INVENTORY)
    if not path.exists():c.write_json(path,catalog(root))
    payloads,sources=h.freeze(root,791,SOURCES)
    receipts={n:h.json_source(payloads[p])for n,p in PRIOR.items()};inventory=h.json_source(payloads[INVENTORY])
    result=assess(receipts,inventory)
    result.update(status='QUALIFIED_OFFLINE_HORIZON_AUDIT',claim_classification='UNKNOWN_800_STAGE_ACCEPTANCE',
                  attribution='external offline auditor',filename_catalog=inventory,
                  reused529_is_current_global_compliance=False)
    return h.finish(root,791,SCRIPT,OUT,DOC,DOC_TEXT,result,sources)


if __name__=='__main__':raise SystemExit(h.cli(build))
