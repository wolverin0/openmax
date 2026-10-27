# PUBLIC_REDACTED_DERIVATIVE; original_sha256=728fa9e7a3e5d007ecb0a6943abb05404fe7d54e6cbad1a1d7ad5d8fbcc72d86
# Private originals are required for native replay.
"""WA campaign prerequisite receipt; no measurements are synthesized on failure."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage861_866_common as c
from tools.autoresearch import stage897_900_gate_adapter as adapter
OUT = ROOT / 'artifacts/autoresearch/stage898a_live_wa_aa_and_holdout.json'
UPSTREAM = ROOT / 'artifacts/autoresearch/stage897a_live_wa_hardened_kit_verify.json'

def build():
    previous = c.load(UPSTREAM)
    return dict(stage='898A', schema_version=1, status='BLOCKED', acceptance='NOT_ACCEPTED', implementation=c.pin(__file__), analysis_dependencies=[c.pin(c.__file__), *adapter.source_bindings()], source_bindings=[c.pin(UPSTREAM)], target_configuration_writes=False, prerequisite_897_status=previous['status'], blockers=['NO_VERIFIED_OPENWRT_STA_ON_OPERATOR_CANDIDATE_ADDRESSES', '897_CANONICAL_KIT_NOT_APPLIED_OR_VERIFIED', 'NO_IDENTIFIED_RESTORABLE_BASELINE_AND_MATCHED_CANDIDATE'], aa=dict(state='NOT_EXECUTED', measured_pairs=0, raw_gate=None, control_result='NOT_ACQUIRED'), discovery=dict(state='NOT_EXECUTED', measured_pairs=0, raw_gate=None), holdout=dict(state='NOT_EXECUTED', measured_pairs=0, raw_gate=None, copied_samples=False, disjointness='NOT_ESTABLISHED_NO_ACQUISITION'), planned_contract=dict(pairing_unit='paired_block', multiplicity='single_step_Sidak', freeze_before_first_window=True, aa_pairs=8, discovery_pairs=8, holdout_pairs=8, holdout_must_have_disjoint=['dataset_id', 'block_id', 'epoch_id', 'session_id', 'run_id', 'receipt_path', 'raw_sha256'], holdout_receipt_authority='INDEPENDENT_HASH_BOUND_RECEIPT_NOT_BOOLEAN', state='DRAFT_NOT_FROZEN_OR_EXECUTED'), goodput_mbps=None, p95_rtt_ms=None, p99_rtt_ms=None, next_action='Identify the actual associated OpenWrt STA and approve an implementable native kit profile; then acquire fresh distinct phases')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    r = build()
    c.write(OUT, r)
    print(json.dumps(dict(stage='898A', status=r['status'], measured_pairs=0)))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
