#!/usr/bin/env python3
"""Audit actual Git index blobs; values are never included in findings.

Read-only by default. --plan audits working files for an explicit publication
selection; it does not stage, commit, push, rewrite history or contact devices.
Private finding paths/line numbers stay under the local Git metadata directory.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
STEM = 'stage826a_public_git_hygiene_and_push_gate'
MAX_BYTES = 8 * 1024 * 1024
TEXT_EXTENSIONS = {'.py','.md','.json','.jsonl','.yaml','.yml','.toml','.ini','.txt',
                   '.sh','.ps1','.c','.h','.patch','.diff','.html','.css','.js','.mjs','.xml',
                   '.conf','.config','.example','.service','.rules','.csv','.cfg'}
PRIVATE_ROOTS = ('.agents/','.claude/','.codex/','.git/','private/','research/raw/',
                 'handoffs/','tools/research/srccache/',
                 'artifacts/documentation/','artifacts/verification/',
                 'firmware/openwrt/futuramax-','infra_openwisp_official/')
PROBES = ['nested/proprietary.bin','nested/module.ko','nested/root.sqfs',
          '.env.production','nested/mixedHaCkErOnE.md',
          'docs/STAGE81A_private.md','tools/re/audit_stage98c_private.py']


def git(root, *args, input=None):
    proc = subprocess.run(['git', *args], cwd=root, input=input, capture_output=True)
    if proc.returncode:
        raise RuntimeError('git command failed: ' + args[0])
    return proc.stdout


def path_reason(label):
    low=label.lower(); p=PurePosixPath(low)
    if p.is_absolute() or '..' in p.parts or '\\' in label or ':' in label:
        return 'unsafe_path'
    if 'hackerone' in low:
        return 'coordinated_disclosure'
    for match in re.finditer(r'stage(\d+)[a-z](?:_|\.|/|$)',low):
        if 81 <= int(match[1]) <= 98:
            return 'restricted_stage81_to98'
    if p.suffix in {'.bin','.ko','.sqfs','.squashfs','.raw','.db','.sqlite','.zip','.gz','.tar','.xz','.7z','.elf','.asm','.stdout','.stderr','.log'}:
        return 'binary_dump_archive_or_raw_log'
    if low.startswith(PRIVATE_ROOTS) or low=='agents.md':
        return 'private_operator_or_raw_evidence'
    if low.startswith('artifacts/') and not low.startswith('artifacts/autoresearch/'):
        return 'nonpublic_artifact_category'
    if p.name.startswith('.env') or any(x in p.name for x in ('credential','password','secret','system.cfg','backup','original.txt')):
        return 'credential_or_backup_path'
    if p.suffix not in TEXT_EXTENSIONS and p.name not in {
        '.gitignore','.gitattributes','license','makefile','dockerfile','requirements','copying','authors'}:
        return 'non_source_or_unknown_format'
    return None


def content_findings(blob, private_terms=()):
    if len(blob)>MAX_BYTES:
        return [dict(rule='size_limit',line=0)]
    if b'\0' in blob:
        return [dict(rule='binary_content',line=0)]
    try:
        text=blob.decode('utf-8-sig')
    except UnicodeDecodeError:
        return [dict(rule='non_utf8_content',line=0)]
    patterns={
        'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
        'provider_token':r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})',
        'credential_url':r'https?://[^\s/@:]+:[^\s/@]+@',
        'password_hash':r'\$(?:[156]\$[^\s$"\x27]{1,16}\$[./A-Za-z0-9]{12,}|2[aby]\$\d\d\$[./A-Za-z0-9]{40,})',
        'restricted_report_body':r'(?:AMEDEV[-_]BUG[-_]\d+|W3[-_]BUG[-_]\d+|HACKERONE[ ]SUBMISSION|HackerOne[ ]Ubiquiti[ ]submission[ ]dossier)',
        'operational_address':r'\b(?:10\.10\.\d{1,3}\.\d{1,3}|192\.168\.(?:100|200)\.\d{1,3})\b',
    }
    findings=[]
    for rule,pattern in patterns.items():
        for match in re.finditer(pattern,text,re.I):
            findings.append(dict(rule=rule,line=text.count('\n',0,match.start())+1))
    secret=re.compile(r'''(?i)(?:password|passwd|passphrase|psk|secret|api[_-]?key|access[_-]?token)["']?\s*[:=]\s*["']([^"'\r\n]{3,})["']''')
    placeholders=re.compile(r'(?i)^(?:test|dummy|example|sample|placeholder|changeme|redacted|not[_-]?set|none|unknown|password|secret|token|your[_-].*|\*+|x+|<.*>|\$.*|\{.*\})$')
    for match in secret.finditer(text):
        value=match[1]
        if not placeholders.fullmatch(value):
            findings.append(dict(rule='literal_credential',line=text.count('\n',0,match.start())+1))
    unquoted=re.compile(r'(?i)(?:[\w.-]*password|passwd|passphrase|wpa_psk|api_key)\s*=\s*([^\s"\x27;\\]{3,})')
    for match in unquoted.finditer(text):
        if not placeholders.fullmatch(match[1]):
            findings.append(dict(rule='unquoted_credential',line=text.count('\n',0,match.start())+1))
    for term in private_terms:
        if len(term)>=4:
            for match in re.finditer(r'\b'+re.escape(term)+r'\b',text,re.I):
                findings.append(dict(rule='private_operator_term',line=text.count('\n',0,match.start())+1))
    # Do not publish native device identifiers. Clearly synthetic examples allowed.
    for match in re.finditer(r'\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b',text,re.I):
        if match[0].lower() not in {'00:00:00:00:00:00','ff:ff:ff:ff:ff:ff','00:11:22:33:44:55','02:00:00:00:00:01'}:
            findings.append(dict(rule='device_identifier',line=text.count('\n',0,match.start())+1))
    return findings


def index_blobs(root):
    entries=[]
    for item in git(root,'ls-files','--stage','-z').split(b'\0'):
        if not item:continue
        meta,path=item.split(b'\t',1);mode,oid,stage=meta.split()
        if stage!=b'0':raise ValueError('unmerged index')
        entries.append((path.decode('utf-8'),mode.decode(),oid.decode()))
    objects=list(dict.fromkeys(oid for _,_,oid in entries))
    response=git(root,'cat-file','--batch',input=('\n'.join(objects)+'\n').encode()) if objects else b''
    blobs={};offset=0
    for oid in objects:
        end=response.index(b'\n',offset);header=response[offset:end].split();size=int(header[2]);offset=end+1
        if header[1]!=b'blob':raise ValueError('nonblob in index')
        blobs[oid]=response[offset:offset+size];offset+=size+1
    return [(path,mode,blobs[oid]) for path,mode,oid in entries]


def ignore_audit(root):
    proc=subprocess.run(['git','check-ignore','--no-index','--stdin','-z'],cwd=root,
                        input=b'\0'.join(x.encode() for x in PROBES)+b'\0',capture_output=True)
    if proc.returncode not in (0,1):raise RuntimeError('ignore probe failed')
    ignored={x.decode() for x in proc.stdout.split(b'\0') if x}
    return {p:p in ignored for p in PROBES}


def audit(root=ROOT, plan=False, private_terms=()):
    root=Path(root).resolve()
    if str(root).startswith('\\\\'):raise ValueError('local checkout required')
    if git(root,'rev-parse','--show-toplevel').decode().strip().replace('\\','/').lower()!=root.as_posix().lower():
        raise ValueError('exact checkout root required')
    selected=[];findings=[]
    if plan:
        labels=sorted(set(git(root,'ls-files','--cached','--others','--exclude-standard','-z').decode().split('\0'))-{''})
        entries=[]
        for label in labels:
            path=root/label
            if not path.resolve().is_relative_to(root):
                findings.append(dict(path=label,rule='path_outside_checkout',line=0));continue
            if path.is_symlink():entries.append((label,'120000',b''));continue
            if path.is_file():
                reason=path_reason(label)
                if reason:findings.append(dict(path=label,rule=reason,line=0));continue
                entries.append((label,'100644',path.read_bytes()))
    else:
        entries=index_blobs(root)
    for label,mode,blob in entries:
        reason=path_reason(label)
        issues=[dict(rule=reason,line=0)] if reason else content_findings(blob,private_terms)
        if mode not in ('100644','100755'):
            issues.append(dict(rule='symlink_or_gitlink',line=0))
        if issues:findings.extend(dict(path=label,**item) for item in issues)
        else:selected.append(dict(path=label,bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest()))
    if entries:
        ignored_proc=subprocess.run(['git','check-ignore','--no-index','--stdin','-z'],cwd=root,
            input=b'\0'.join(label.encode() for label,_,_ in entries)+b'\0',capture_output=True)
        if ignored_proc.returncode not in (0,1):raise RuntimeError('tracked ignore audit failed')
        ignored_labels={x.decode() for x in ignored_proc.stdout.split(b'\0') if x}
        if ignored_labels:
            selected=[s for s in selected if s['path'] not in ignored_labels]
            findings.extend(dict(path=label,rule='ignored_but_tracked',line=0) for label in sorted(ignored_labels))
    ignored=ignore_audit(root)
    status=git(root,'status','--porcelain=v1','-z').split(b'\0')
    manifest_exclusions=[f'artifacts/autoresearch/{STEM}.json',f'docs/{STEM.upper()}.md']
    result=dict(stage='826A',status='CONFIRMED' if not findings and all(ignored.values()) else 'FAILED',
                scope='working-tree publication plan' if plan else 'actual Git index blobs only; prior history not rewritten',
                compliant=not findings and all(ignored.values()),
                selected_count=len(selected),excluded_or_failed_paths=len({x['path'] for x in findings}),
                findings_by_rule=dict(Counter(x['rule'] for x in findings)),ignore_probes=ignored,
                status_entries=sum(bool(x) for x in status),
                manifest_sha256=hashlib.sha256(json.dumps([x for x in selected if x['path'] not in manifest_exclusions],sort_keys=True).encode()).hexdigest(),
                manifest_exclusions=manifest_exclusions,
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
                pushed_commit=None,push_verified=False,
                boundary=dict(radio_access=False,flash_executed=False,history_rewritten=False))
    return result,selected,findings


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--plan',action='store_true');p.add_argument('--write',action='store_true')
    args=p.parse_args(argv)
    gitdir=Path(git(args.root,'rev-parse','--absolute-git-dir').decode().strip())
    policy=gitdir/'stage826a/private_terms.json'
    terms=json.loads(policy.read_text()) if policy.exists() else []
    result,selected,findings=audit(args.root,args.plan,terms)
    private=gitdir/'stage826a';private.mkdir(parents=True,exist_ok=True)
    (private/('plan.json' if args.plan else 'index_audit.json')).write_text(
        json.dumps(dict(result=result,selected=selected,findings=findings),indent=2),encoding='utf-8')
    if args.write:
        dest=args.root/'artifacts/autoresearch'/f'{STEM}.json';dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        doc=args.root/'docs'/f'{STEM.upper()}.md';doc.parent.mkdir(parents=True,exist_ok=True)
        doc.write_text('<!-- doc-head: Stage826A public Git index hygiene and remote push receipt -->\n'
                       '<!-- /doc-head -->\n\n# Stage826A public Git hygiene and push gate\n\n'
                       f'Index audit compliant: {result["compliant"]}; selected files: {result["selected_count"]}.\n'
                       'Only actual indexed blob bytes establish publication eligibility. Ignore rules alone do not untrack files.\n'
                       'Private findings remain in local Git metadata; no credential values are emitted.\n'
                       'Prior published history is not rewritten or certified clean by this gate.\n'
                       'Pushed commit: pending verification by the release coordinator.\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0 if result['compliant'] else 1


if __name__=='__main__':raise SystemExit(main())
