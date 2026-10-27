# PUBLIC_REDACTED_DERIVATIVE
"""Create attributed, offline public derivatives; never stage or publish them.

Original evidence bindings remain bindings to private originals, not to these
derivatives. The output is a portability/metadata contract, not native replay.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import ipaddress
import json
import os
from pathlib import Path, PureWindowsPath
import re
import stat

ROOT = Path(__file__).resolve().parents[2]
STATE = 'PUBLIC_REDACTED_DERIVATIVE'
SELF = 'tools/verify/stage911_916_public_projection.py'
EXCLUDED = 'controller/stage18_wmi_rate_schedule_and_sub20mhz_controller.py'
MAX_FILES = 100
MAX_BYTES = 8 * 1024 * 1024
IP = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
MAC = re.compile(r'\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b')


class PublicCapabilityBlocked(RuntimeError):
    """Public projections cannot acquire private credentials or contact devices."""


def projected_local_path(value):
    """Local-only replacement for the private provider's path utility."""
    text = os.fspath(value)
    if not isinstance(text, str) or text.replace('/', '\\').startswith(('\\\\', '\\??\\')):
        raise ValueError('local text path required')
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', text) or PureWindowsPath(text).is_reserved():
        raise ValueError('remote or device path rejected')
    path = Path(text).absolute()
    if os.name == 'nt':
        import ctypes
        if ctypes.windll.kernel32.GetDriveTypeW(str(path.anchor)) == 4:
            raise ValueError('mapped network drive rejected')
    for ancestor in reversed((path, *path.parents)):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            break
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('symlink or reparse point rejected')
    return path


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def unique_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs)


def source_path(root, label):
    if not isinstance(label, str) or '\\' in label or ':' in label:
        raise ValueError('invalid export path')
    path = projected_local_path(root / label)
    if Path(label).is_absolute() or '..' in Path(label).parts or not path.is_relative_to(root):
        raise ValueError('export escaped repository')
    return path


def import_dependencies(tree, root):
    result = set()
    for node in ast.walk(tree):
        modules = []
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules = [node.module] + [node.module + '.' + alias.name for alias in node.names]
        for module in modules:
            label = module.replace('.', '/') + '.py'
            if module.split('.')[0] in {'tools', 'analysis', 'controller', 'workloads', 'firmware'}:
                if source_path(root, label).is_file():
                    result.add(label)
    return result


def aliases_for(texts, terms):
    """Exact lexical identities remain distinct, including case-distinct keys."""
    joined = '\n'.join(texts)
    if re.search(r'PUBLIC_(?:DEVICE|TERM)_\d+|198\.18\.\d+\.\d+', joined):
        raise ValueError('reserved public alias collision')
    mapping = {}
    addresses = sorted(set(IP.findall(joined)))
    counter = 1
    for address in addresses:
        try:
            parsed = ipaddress.IPv4Address(address)
        except ipaddress.AddressValueError:
            continue
        # Protocol constants and non-private documentation addresses are not identities.
        if parsed.is_private and not parsed.is_loopback and address not in {'0.0.0.0', '255.255.255.255'} and not address.startswith('255.'):
            mapping[address] = f'198.18.{counter // 254}.{counter % 254 + 1}'
            counter += 1
    for index, item in enumerate(sorted(set(MAC.findall(joined))), 1):
        if item.lower() not in {'00:00:00:00:00:00', 'ff:ff:ff:ff:ff:ff'}:
            mapping[item] = f'PUBLIC_DEVICE_{index:04d}'
    occurrences = set()
    for term in terms:
        if len(term) >= 4:
            occurrences.update(match[0] for match in re.finditer(r'\b' + re.escape(term) + r'\b', joined, re.I))
    for index, item in enumerate(sorted(occurrences), 1):
        mapping[item] = f'PUBLIC_TERM_{index:04d}'
    # A single regex prevents cascading substitutions and preserves repeated identity.
    expression = re.compile('|'.join(re.escape(x) for x in sorted(mapping, key=len, reverse=True))) if mapping else None
    return lambda text: expression.sub(lambda match: mapping[match[0]], text) if expression else text


class PublicTransform(ast.NodeTransformer):
    def __init__(self, scrub):
        self.scrub = scrub
        self.blocked = []
        self.network_names = {'socket', 'paramiko', 'requests', 'httpx', 'urllib', 'subprocess'}

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split('.')[0] in self.network_names:
                self.network_names.add(alias.asname or alias.name.split('.')[0])
        return node

    def visit_ImportFrom(self, node):
        if node.module == EXCLUDED[:-3].replace('/', '.'):
            if any(alias.name != 'local_path' for alias in node.names):
                raise ValueError('unsupported private provider import')
            return ast.ImportFrom(module=SELF[:-3].replace('/', '.'), names=[ast.alias(name='projected_local_path', asname=alias.asname or 'local_path') for alias in node.names], level=0)
        if node.module and node.module.split('.')[0] in self.network_names:
            self.network_names.update(alias.asname or alias.name for alias in node.names)
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return ast.copy_location(ast.Constant(self.scrub(node.value)), node)
        return node

    def visit_FunctionDef(self, node):
        credential = node.name.lower() in {'credential', 'credentials', 'load_credentials', 'fetch_credentials', 'get_password', 'load_password'}
        transport = False
        for call in (x for x in ast.walk(node) if isinstance(x, ast.Call)):
            fn = call.func
            base = fn
            while isinstance(base, ast.Attribute):
                base = base.value
            if isinstance(base, ast.Name) and base.id in self.network_names:
                transport = True
            if isinstance(fn, ast.Attribute) and fn.attr in {'exec_command', 'open_sftp', 'sendall', 'create_connection', 'open_session'}:
                transport = True
        if credential or transport:
            self.blocked.append(node.name)
            node.body = [ast.Raise(exc=ast.Call(func=ast.Name(id='RuntimeError', ctx=ast.Load()), args=[ast.Constant('PUBLIC_TRANSPORT_OR_CREDENTIAL_DISABLED: ' + node.name)], keywords=[]), cause=None)]
            node.decorator_list = []
            return node
        return self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef


def project_python(text, scrub, original_sha):
    tree = ast.parse(text)
    transform = PublicTransform(scrub)
    tree = transform.visit(tree)
    ast.fix_missing_locations(tree)
    code = ast.unparse(tree)
    # Marker is a comment so original future imports retain their valid position.
    return f'# {STATE}; original_sha256={original_sha}\n# Private originals are required for native replay.\n' + code + '\n', transform.blocked


def project_json(text, scrub, original_sha):
    value = unique_json(text)
    def walk(item):
        if isinstance(item, str):
            return scrub(item)
        if isinstance(item, list):
            return [walk(x) for x in item]
        if isinstance(item, dict):
            out = {}
            for key, val in item.items():
                new = scrub(key)
                if new in out:
                    raise ValueError('redaction collapsed JSON keys')
                if key.lower() in {'stdout', 'stderr', 'raw_stdout', 'raw_stderr', 'capture_body', 'raw_capture', 'raw_bytes'}:
                    out[new] = {'publication_state': 'PRIVATE_CAPTURE_WITHHELD'}
                else:
                    out[new] = walk(val)
            return out
        return item
    value = walk(value)
    if not isinstance(value, dict) or 'publication_redaction' in value:
        raise ValueError('receipt must be an original object')
    value['publication_redaction'] = dict(state=STATE, original_sha256=original_sha, original_retained_locally=True, source_bindings='NOT_REPINNED_PRIVATE_ORIGINALS_REQUIRED', original_evidence=False, derivative_acceptance='NOT_ACCEPTED')
    return json.dumps(value, indent=2, ensure_ascii=True) + '\n'


def public_test(label, original_sha):
    return f'''# {STATE}; historical source_sha256={original_sha}
"""Public metadata contract only; PRIVATE_NATIVE_REPLAY_NOT_EXECUTED.

Original historical tests remain local and are not reproduced by this test.
"""
import json
from pathlib import Path

def test_public_projection_metadata_contract():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'projection_manifest.json').read_text())
    row = next(x for x in manifest['files'] if x['path'] == {label!r})
    assert row['original_sha256'] == {original_sha!r}
    assert row['test_scope'] == 'PUBLIC_METADATA_CONTRACT_NOT_NATIVE_REPLAY'
    assert manifest['physical_acceptance'] == 'NOT_ACCEPTED'
    assert manifest['network_access'] is False
'''


def synthetic_parser_test():
    return '''# PUBLIC_REDACTED_DERIVATIVE; new synthetic fixtures, not native replay
"""Public pure-parser and disabled-transport contracts, no private input files."""
import importlib
import inspect
import socket
import pytest
from firmware.xtensa_sgmt_surgical_patcher import SgmtContainer, read_bmi_varint, write_bmi_varint
from tools.autoresearch.run_stage864a_guarida_panel2_panel3_airmagic_and_slot_audit import spectral_efficiency

def test_synthetic_varint_vectors_and_truncation():
    for value in [0, 127, 128, 16384, 0xffffffff]:
        encoded=write_bmi_varint(value)
        assert read_bmi_varint(encoded,0)==(value,len(encoded))
    for raw in [b'', b'\\x80', b'\\xff'*6]:
        with pytest.raises(ValueError): read_bmi_varint(raw,0)

def test_synthetic_sgmt_invalid_inputs_cannot_validate():
    for raw in [b'', b'\\x00'*16, b'not-firmware'*4]:
        with pytest.raises(ValueError): SgmtContainer.from_bytes(raw)

def test_synthetic_spectral_arithmetic_domain():
    assert spectral_efficiency(120,40)==3
    for goodput,width in [(1,0),(-1,20),(float('nan'),20),(1,float('inf'))]:
        with pytest.raises(ValueError): spectral_efficiency(goodput,width)

def test_public_acquisition_is_disabled_before_socket(monkeypatch):
    modules=[importlib.import_module('tools.autoresearch.'+name) for name in
      ['stage861_866_common','stage879_884_common','stage897_900_live_common']]
    def denied(*args,**kwargs): raise AssertionError('socket attempted')
    monkeypatch.setattr(socket,'create_connection',denied)
    monkeypatch.setattr(socket.socket,'connect',denied)
    for module,names in zip(modules,[['credential','capture'],['capture'],['connect','run']]):
        for name in names:
            fn=getattr(module,name)
            signature=inspect.signature(fn)
            kwargs={key:None for key,p in signature.parameters.items() if p.default is inspect.Parameter.empty}
            with pytest.raises(RuntimeError,match='PUBLIC_TRANSPORT_OR_CREDENTIAL_DISABLED'):
                fn(**kwargs)
'''


def build(root=ROOT, plan_path=None, output_dir=None):
    root = projected_local_path(root).resolve()
    plan_path = projected_local_path(plan_path or root / '.git/stage911_916/publication_plan.json')
    output = projected_local_path(output_dir or root / '.git/stage911_916/public_projection')
    allowed = root / '.git/stage911_916'
    if not output.is_relative_to(allowed) or output == allowed:
        raise ValueError('projection output must be beneath local Git stage911_916 directory')
    if output.exists() and any(output.iterdir()):
        raise ValueError('projection output must be empty; never overwrite reviewed derivatives')
    plan = unique_json(plan_path.read_text(encoding='utf-8-sig'))
    from tools.verify.verify_stage826a_public_git_hygiene_and_push_gate import content_findings, path_reason
    terms_path = root / '.git/stage826a/private_terms.json'
    terms = unique_json(terms_path.read_text(encoding='utf-8-sig')) if terms_path.exists() else []
    if not isinstance(terms, list) or any(not isinstance(x, str) for x in terms):
        raise ValueError('invalid local privacy policy')
    selected = set(plan['primary_paths']) | {x['path'] for x in plan['file_inventory'] if x['role'] == 'MINIMAL_IMPORT_DEPENDENCY'}
    selected.discard(EXCLUDED)
    pending = list(selected)
    original = {}
    while pending:
        label = pending.pop()
        if label in original:
            continue
        if path_reason(label) or label == EXCLUDED:
            raise ValueError('nonpublic source selected')
        path = source_path(root, label)
        blob = path.read_bytes()
        if len(blob) > MAX_BYTES or b'\0' in blob:
            raise ValueError('source is too large or binary')
        text = blob.decode('utf-8-sig')
        original[label] = (blob, text)
        if label.endswith('.py') and not label.startswith('tests/'):
            for dep in import_dependencies(ast.parse(text), root):
                if dep != EXCLUDED and dep not in original:
                    pending.append(dep)
        if len(original) + len(set(pending)) > MAX_FILES:
            raise ValueError('dependency closure exceeds bounded export')
    scrub = aliases_for([x[1] for x in original.values()], terms)
    projected = {}
    rows = []
    for label, (blob, text) in sorted(original.items()):
        digest = sha(blob)
        row = dict(path=label, original_sha256=digest, state=STATE, source_binding_scope='PRIVATE_ORIGINAL_NOT_REPINNED')
        if label.startswith('tests/'):
            body = public_test(label, digest)
            row['test_scope'] = 'PUBLIC_METADATA_CONTRACT_NOT_NATIVE_REPLAY'
        elif label.endswith('.py'):
            body, row['blocked_functions'] = project_python(text, scrub, digest)
        elif label.endswith('.json'):
            body = project_json(text, scrub, digest)
        elif label.endswith('.md'):
            body = scrub(text)
            body = re.sub(r'<!-- doc-head:.*?<!-- /doc-head -->\s*', '', body, count=1, flags=re.S)
            body = '<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->\n<!-- /doc-head -->\n' + STATE + '; inherited historical claims are not acceptance of this derivative.\n\n' + body
            if len(body.splitlines()) >= 180:
                body = '\n'.join(x for x in body.splitlines() if x.strip()) + '\n'
            if len(body.splitlines()) >= 180:
                raise ValueError('projected document exceeds authorized line bound')
        else:
            raise ValueError('unsupported projection source')
        projected[label] = body.encode('utf-8')
        row['projected_sha256'] = sha(projected[label])
        rows.append(row)
    # Self-contained safe utility required by the one excluded private-provider import.
    if SELF not in projected:
        own = Path(__file__).read_bytes()
        projected[SELF] = ('# ' + STATE + '\n').encode() + own
        rows.append(dict(path=SELF, original_sha256=sha(own), projected_sha256=sha(projected[SELF]), state=STATE, role='PUBLIC_PATH_UTILITY_AND_PROJECTOR', source_binding_scope='ATTRIBUTION_ONLY'))
    if 'firmware/xtensa_sgmt_surgical_patcher.py' in projected and 'tools/autoresearch/run_stage864a_guarida_panel2_panel3_airmagic_and_slot_audit.py' in projected:
        label = 'tests/test_public_synthetic_parsers.py'
        projected[label] = synthetic_parser_test().encode()
        rows.append(dict(path=label, original_sha256=None, projected_sha256=sha(projected[label]), state=STATE, role='NEW_SYNTHETIC_PUBLIC_CONTRACT', test_scope='SYNTHETIC_PURE_PARSER_NOT_NATIVE_REPLAY'))
    projected['requirements-public-projection.txt'] = b'pytest\nparamiko\nscipy\npyelftools\ncapstone\n'
    # Prevent ancestor operator-checkout pytest.ini from injecting private modules.
    projected['pytest.ini'] = b'[pytest]\npythonpath = .\ntestpaths = tests\n'
    manifest = dict(schema_version='1.0', state=STATE, physical_acceptance='NOT_ACCEPTED', network_access=False, native_replay_executed=False, original_source_bindings_repinned=False, primary_count=len(plan['primary_paths']), files=rows, withheld_private_provider=EXCLUDED, alias_mapping_emitted=False, privacy_findings=[])
    for label, blob in projected.items():
        for finding in content_findings(blob, terms):
            manifest['privacy_findings'].append(dict(path=label, **finding))
    manifest['status'] = 'PREPARED' if not manifest['privacy_findings'] else 'BLOCKED_PRIVACY_REVIEW'
    note = '<!-- doc-head: Public projection scope and private-original evidence boundary -->\n<!-- /doc-head -->\n# Public projection\n\n' + STATE + '\n\nThese files are attributed derivatives. Original files remain unchanged locally.\nTransport and credential acquisition functions explicitly raise before acquisition.\nIdentity aliases are consistent across exported files; the private alias map is absent.\nProtocol constants are preserved. Raw capture bodies and binary firmware are withheld.\nHistorical receipt statuses and original source hashes are retained; source bindings\nrefer to private originals and cannot verify public derivatives as native evidence.\nHistorical tests here verify public metadata only, not private native replay.\nPure parser algorithms remain available for explicitly synthetic fixtures.\nNo physical acceptance, activation authority, network execution or publication is implied.\nUse `python -m pytest tests` in this projection for public metadata contracts.\nPrivate original tests are maintained separately in the operator checkout.\n'
    projected['PUBLICATION.md'] = note.encode()
    projected['projection_manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    for label, blob in projected.items():
        target = output / label
        projected_local_path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
    return manifest


def main():
    import sys
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    result = build(args.root, output_dir=args.output_dir)
    print(json.dumps(dict(status=result['status'], file_count=len(result['files']), privacy_finding_count=len(result['privacy_findings']), network_access=False)))
    return 0 if result['status'] == 'PREPARED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
