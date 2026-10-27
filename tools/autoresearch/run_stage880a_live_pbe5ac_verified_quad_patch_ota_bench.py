# PUBLIC_REDACTED_DERIVATIVE; original_sha256=b28d32c61552328f696c98b4af85c89c1af4b59ef82a9ccbd233163c0972df81
# Private originals are required for native replay.
"""Stage880 exact direct-bench prerequisites; refuse non-existent Quad firmware."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage861_866_common as c
from tools.autoresearch import stage879_884_common as n
from tools.autoresearch.run_stage861a_live_pbe5ac_quad_patch_pb040_to_pb070_ota import parse_native
from tools.firmware import build_stage879a_verified_pb070_and_pb080_native_sgmt_binaries as b
OUT = ROOT / 'artifacts/autoresearch/stage880a_live_pbe5ac_verified_quad_patch_ota_bench.json'

def build(evidence=None):
    source = c.load(b.OUT)
    rows = c.load(ROOT / evidence['path'])['results'] if evidence else []
    return dict(schema_version=1, stage='880A', status='BLOCKED', acceptance='NOT_ACCEPTED', question='Does exact native Quad outperform a verified baseline on direct .241/.242 OTA?', implementation=c.pin(__file__), source_bindings=[c.pin(b.OUT)], analysis_dependencies=[c.pin(n.__file__), c.pin(c.__file__), c.pin(ROOT / 'tools/autoresearch/run_stage861a_live_pbe5ac_quad_patch_pb040_to_pb070_ota.py')], topology=n.TOPOLOGY, attribution=['external controller', 'ath10k', 'QCA firmware'], evidence=evidence, native_state=[parse_native(row) for row in rows], upstream_quad_emitted=source['quad_emitted'], deployment_executed=False, target_writes=False, watchdog_armed=False, firmware_loaded=False, watchdog_required_seconds=45, dynamic_phy_required=True, desired_channel=dict(control_mhz=5200, center1_mhz=5190, width_mhz=40, note='5190 is the VHT40 center, not a20MHz control channel; require legal HT40 pair'), rounds=3, executed_windows=0, planned_windows=[dict(round=r, window=w, profile='baseline' if w[0] == 'A' else 'native_quad', state='NOT_EXECUTED', goodput_mbps=None, p95_rtt_ms=None) for r in range(1, 4) for w in ('A1', 'B1', 'A2', 'B2')], required_before_activation=['Hash-bound complete native Quad plus independent patch semantics review', 'Exact native API/path, STA-first45s watchdog with tested rollback', 'RF-only path proof with FDB/counters; shared-switch reachability is insufficient', 'Matched receiver metrics and exact restoration, no flash/UCI commit'], blockers=['879A_QUAD_NOT_EMITTED', 'NATIVE_API2_VS_REQUESTED_FIRMWARE5_MISMATCH', 'NO_VERIFIED_BASELINE_AND_OTA_ONLY_ROUTE'], next_action='Resolve879 semantic contracts before implementing activation; no SCP/bind-mount/reload is attempted')

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect', action='store_true')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args(argv)
    evidence = n.save('880a', [n.capture(host, 'bench') for host in ('198.18.0.45', '198.18.0.46')]) if args.inspect else None
    result = build(evidence)
    c.write(OUT, result)
    print(json.dumps(dict(stage='880A', status=result['status'], executed_windows=0, evidence=evidence)))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
