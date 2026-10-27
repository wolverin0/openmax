#!/usr/bin/env python3
"""Reproducible offline audit core; no device, research service or remote access."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.verify.stage779_822_offline_common import atomic_write

CORE_TESTS=(
 'tests/test_chatgpt_audit_1afaeb7_regressions.py',
 'tests/test_chatgpt_audit_wa_kit.py',
 'tests/test_chatgpt_audit_sgmt.py',
 'tests/test_chatgpt_audit_pb_campaign.py',
 'tests/test_chatgpt_audit_public_checkout.py',
 'workloads/test_flent_orchestrator.py',
 'analysis/regression_gate/test_gatekeeper.py',
 'tests/test_pb_gatekeeper_paired_aa.py',
 'tests/test_powerbeam_m5_and_5ac_bench_harness.py',
 'tests/test_pb_021_022_024_csi_and_sdr_correlator.py',
 'tests/test_pb_060_070_autonomous_search_and_phy_gate.py',
)
PRIVATE_TESTS=('tests/test_pb_011_sgmt_container_inspector.py',
               'tests/test_xtensa_sgmt_surgical_patcher.py')


def readme_links(text):
    return [unquote(match[1].split('#',1)[0]) for match in re.finditer(r'\]\(([^)]+)\)',text)
            if match[1] and not urlsplit(match[1]).scheme and not match[1].startswith('#')]


def missing_readme_links(text,public_paths):
    return sorted(set(readme_links(text))-set(public_paths))


def available_paths(root):
    """Git's index in a checkout, filesystem in an exported public tree."""
    top=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=root,capture_output=True,text=True)
    if top.returncode==0 and Path(top.stdout.strip()).resolve()==root.resolve():
        result=subprocess.run(['git','ls-files','-z'],cwd=root,capture_output=True,check=True)
        return {p for p in result.stdout.decode().split('\0') if p}
    return {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--private',action='store_true',help='Also run separately held firmware checks; never acquires inputs')
    parser.add_argument('--collect-only',action='store_true')
    parser.add_argument('--junitxml',type=Path)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args(argv);root=args.root.resolve()
    tests=CORE_TESTS+(PRIVATE_TESTS if args.private else ())
    missing=[p for p in tests if not (root/p).is_file()]
    broken=missing_readme_links((root/'README.md').read_text(encoding='utf-8'),available_paths(root))
    if missing or broken:
        print(json.dumps(dict(status='FAILED',missing_tests=missing,broken_public_links=broken)));return 1
    command=[sys.executable,'-m','pytest',*tests,'-q']
    if args.collect_only:command.append('--collect-only')
    if args.junitxml:command.append('--junitxml='+str(args.junitxml.resolve()))
    completed=subprocess.run(command,cwd=root)
    result=dict(audit_base='1afaeb7712161068044238755166dff3a7043248',
                status=('COLLECTION_PASS' if args.collect_only else 'OFFLINE_SOFTWARE_PASS') if completed.returncode==0 else 'FAILED',
                tests_executed=not args.collect_only,
                exit_code=completed.returncode,scope='public synthetic fixtures and software contracts',
                private_checks_requested=args.private,physical_acceptance='UNKNOWN',
                network_access=False,radio_commands_executed=False,firmware_loaded=False,
                native_firewall_changed=False,tests=list(tests),
                source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in tests})
    if args.report:atomic_write(args.report.resolve(),json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))
    return completed.returncode


if __name__=='__main__':raise SystemExit(main())
