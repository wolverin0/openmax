#!/usr/bin/env python3
"""Lossless, local normalization of top-level docs/*.md to the Stage822A budget.

Only doc-head metadata is removed. Long documents retain every other line in
same-directory continuation pages; exact original bytes are backed up first.
No original file or generated page is deleted. A plan is validated before writes.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = 'artifacts/verification/stage822a_doc_budget.json'
LIMIT = 180
PAYLOAD_LIMIT = 155
OPEN = '<!-- stage822a-payload-begin -->'
CLOSE = '<!-- stage822a-payload-end -->'
HEAD = re.compile(r'<!--\s*(?:doc-head\b[\s\S]*?|/doc-head\s*)-->')
FENCE = re.compile(r'^\s{0,3}(`{3,}|~{3,})')


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def bounded(root: Path, relative: str) -> Path:
    root = root.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or str(path).startswith('\\\\'):
        raise ValueError('path outside local repository')
    return path


def inspect(blob: bytes) -> dict:
    text = blob.decode('utf-8-sig')
    lines = text.splitlines()
    valid = (len(lines) < LIMIT and text.count('<!-- doc-head:') == 1
             and text.count('<!-- /doc-head -->') == 1
             and bool(lines) and lines[0].startswith('<!-- doc-head:')
             and '<!-- /doc-head -->' in lines[1:8])
    return {'lines': len(lines), 'doc_heads': text.count('<!-- doc-head:'),
            'doc_head_closings': text.count('<!-- /doc-head -->'), 'compliant': valid}


def body_lines(blob: bytes) -> list[str]:
    """Preserve substantive lines, removing only doc-head comment metadata."""
    return HEAD.sub('', blob.decode('utf-8-sig')).splitlines()


def header(topic: str) -> list[str]:
    topic = topic.replace('<', '').replace('>', '')
    return [f'<!-- doc-head: {topic} -->', '<!-- /doc-head -->', '']


def fence_end(line: str, marker: str) -> bool:
    return bool(re.fullmatch(r'\s{0,3}' + re.escape(marker[0]) +
                             '{' + str(len(marker)) + r',}\s*', line))


def chunks(lines: list[str]) -> list[list[str]]:
    """Keep fenced code atomic and repeat a split table's original header."""
    blocks: list[list[str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        opening = FENCE.match(line)
        if opening:
            marker = opening.group(1); block = [line]; i += 1
            while i < len(lines):
                block.append(lines[i]); i += 1
                if fence_end(block[-1], marker):
                    break
            else:
                raise ValueError('unclosed fenced block: normalize manually')
            if len(block) > PAYLOAD_LIMIT:
                raise ValueError('fenced block exceeds continuation payload budget')
            blocks.append(block)
        elif line.lstrip().startswith('|'):
            block = [line]; i += 1
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                block.append(lines[i]); i += 1
            # Tables are kept atomic where possible. Long tables split at rows;
            # headers are rendered outside the canonical payload (see render).
            if len(block) > PAYLOAD_LIMIT:
                blocks.extend([block[j:j + PAYLOAD_LIMIT] for j in range(0, len(block), PAYLOAD_LIMIT)])
            else:
                blocks.append(block)
        else:
            blocks.append([line]); i += 1
    result: list[list[str]] = []; current: list[str] = []
    for block in blocks:
        if current and len(current) + len(block) > PAYLOAD_LIMIT:
            result.append(current); current = []
        current.extend(block)
    if current or not result:
        result.append(current)
    if [line for chunk in result for line in chunk] != lines:
        raise AssertionError('substantive lines changed while partitioning')
    return result


def slug(title: str) -> str:
    title = re.sub(r'<[^>]*>', '', title).lower().strip()
    title = ''.join(c for c in title if unicodedata.category(c)[0] in 'LN'
                    or c in ' _-')
    return title.replace(' ', '-')


def headings(parts: list[list[str]]) -> list[dict]:
    global_seen: Counter = Counter(); result = []
    for number, lines in enumerate(parts):
        local_seen: Counter = Counter(); marker = None
        for line in lines:
            opening = FENCE.match(line)
            if marker:
                if fence_end(line, marker):
                    marker = None
                continue
            if opening:
                marker = opening.group(1); continue
            found = re.match(r'^#{1,6}\s+(.+?)(?:\s+#+)?$', line)
            if not found:
                continue
            title = found.group(1); base = slug(title)
            if not base:
                continue
            old = base + (f'-{global_seen[base]}' if global_seen[base] else '')
            new = base + (f'-{local_seen[base]}' if local_seen[base] else '')
            global_seen[base] += 1; local_seen[base] += 1
            result.append({'title': title, 'anchor': old, 'page_anchor': new, 'part': number})
    return result


def label(text: str) -> str:
    return text.replace('[', '\\[').replace(']', '\\]').replace('\n', ' ')


def content_bytes(lines: list[str]) -> bytes:
    return ('\n'.join(lines) + '\n').encode('utf-8')


def render(name: str, original: bytes) -> tuple[dict[str, bytes], dict]:
    body = body_lines(original)
    simple = content_bytes(header(f'{name} preserved document content') + body)
    digest = sha(original)
    backup = f'artifacts/documentation/stage822a/{digest}/{name}.original.txt'
    record = {'path': 'docs/' + name, 'original_sha256': digest, 'original_bytes': len(original),
              'before': inspect(original), 'original_backup': backup,
              'canonical_body_sha256': sha(content_bytes(body)),
              'preservation': 'all non-doc-head source lines retained in original order', 'parts': []}
    outputs: dict[str, bytes] = {}
    if inspect(simple)['compliant']:
        outputs['docs/' + name] = simple
    else:
        parts = chunks(body)
        stem = Path(name).stem
        names = [f'{stem}_CONTINUATION_{digest[:10]}_{i+1:03d}.md' for i in range(len(parts))]
        routes = headings(parts)
        router = header(f'{name} complete-content router and exact original backup') + [
            f'# {stem}: complete document', '',
            'All substantive text is preserved in the continuation pages below, in original order.',
            'These pages form this document; this router changes no acceptance claim.',
            f'[Exact original bytes](../{backup}) (SHA-256 `{digest}`).', '',
            '## Complete content',
        ] + [f'- [Part {i+1}/{len(parts)}]({page})' for i, page in enumerate(names)]
        router += ['', '## Original section routes']
        for item in routes:
            router.append(f'<a id="{item["anchor"]}"></a> [{label(item["title"])}]'
                          f'({names[item["part"]]}#{item["page_anchor"]})')
        outputs['docs/' + name] = content_bytes(router)
        table_header = None
        for i, part in enumerate(parts):
            # Navigation outside payload leaves every source line byte-for-byte
            # reconstructable. Missing-page aliases preserve original #fragment links.
            aliases = []
            for item in routes:
                if item['part'] != i or item['anchor'] != item['page_anchor']:
                    aliases.append(f'<a id="{item["anchor"]}"></a> '
                                   f'[{label(item["title"])}]({names[item["part"]]}#{item["page_anchor"]})')
            intro = header(f'{name} continuation {i+1} of {len(parts)}; source lines preserved') + [
                f'[Document router]({name}) | Part {i+1}/{len(parts)}',
                (' | '.join(aliases) if aliases else ''), '',
            ]
            repeated = []
            if part and part[0].lstrip().startswith('|') and table_header:
                # Avoid adding a header before a real table's own header.
                if len(part) < 2 or not re.match(r'^\s*\|?[\s:|-]+\|?\s*$', part[1]):
                    repeated = table_header
            payload = intro + repeated + [OPEN] + part + [CLOSE]
            data = content_bytes(payload)
            if not inspect(data)['compliant']:
                raise ValueError(f'continuation exceeds budget: {name}:{i+1}')
            path = 'docs/' + names[i]; outputs[path] = data
            record['parts'].append({'path': path, 'payload_sha256': sha(content_bytes(part)),
                                    'payload_lines': len(part), 'repeated_table_header': repeated})
            # Save the nearest valid pipe-table header for cross-page continuation.
            for j in range(len(part) - 1):
                if (part[j].lstrip().startswith('|') and
                        re.match(r'^\s*\|?[\s:|-]+\|?\s*$', part[j+1])):
                    table_header = part[j:j+2]
        if not inspect(outputs['docs/' + name])['compliant']:
            raise ValueError(f'router exceeds budget: {name}')
    record['outputs'] = [{'path': path, 'sha256': sha(data), **inspect(data)}
                         for path, data in outputs.items()]
    return outputs, record


def plan(root: Path = ROOT) -> list[dict]:
    root = root.resolve()
    if str(root).startswith('\\\\'):
        raise ValueError('local root required')
    proposed = []
    for path in sorted((root / 'docs').glob('*.md')):
        if path.is_symlink():
            raise ValueError('symlink document forbidden')
        original = path.read_bytes()
        if inspect(original)['compliant']:
            continue
        outputs, record = render(path.name, original)
        proposed.append({'original': original, 'record': record, 'outputs': outputs})
    return proposed


def apply(root: Path, proposed: list[dict]) -> dict:
    root = root.resolve()
    # Fail before the first write if any shared original changed since planning.
    for item in proposed:
        if bounded(root, item['record']['path']).read_bytes() != item['original']:
            raise ValueError('shared document changed after planning: ' + item['record']['path'])
    manifest_path = bounded(root, MANIFEST)
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {
        'stage': '822A', 'scope': 'top-level docs/*.md only', 'revisions': [],
        'boundary': {'network_access': False, 'device_access': False, 'source_deletions': False}}
    for item in proposed:
        rec = item['record']; backup = bounded(root, rec['original_backup'])
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists() and backup.read_bytes() != item['original']:
            raise ValueError('original backup collision')
        backup.write_bytes(item['original'])
        if sha(backup.read_bytes()) != rec['original_sha256']:
            raise ValueError('original backup verification failed')
        for relative, data in item['outputs'].items():
            if relative == rec['path']:
                continue
            dest = bounded(root, relative)
            if dest.exists() and dest.read_bytes() != data:
                raise ValueError('continuation collision: ' + relative)
            dest.write_bytes(data)
        dest = bounded(root, rec['path'])
        if dest.read_bytes() != item['original']:
            raise ValueError('shared document changed before replacement: ' + rec['path'])
        dest.write_bytes(item['outputs'][rec['path']])
        previous['revisions'].append(rec)
    scanned = [{'path': p.relative_to(root).as_posix(), **inspect(p.read_bytes())}
               for p in sorted((root / 'docs').glob('*.md'))]
    previous['audit'] = {'documents': len(scanned), 'noncompliant': [r for r in scanned if not r['compliant']],
                         'max_lines': max((r['lines'] for r in scanned), default=0)}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(previous, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return previous


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    proposed = plan(args.root)
    print(json.dumps({'mode': 'APPLY' if args.apply else 'PLAN', 'documents_to_normalize': len(proposed),
                      'continuation_pages': sum(len(x['record']['parts']) for x in proposed),
                      'substantive_lines_preserved': True}))
    if args.apply:
        result = apply(args.root, proposed)
        print(json.dumps(result['audit']))
        return 0 if not result['audit']['noncompliant'] else 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
