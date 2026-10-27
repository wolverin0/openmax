# PUBLIC_REDACTED_DERIVATIVE; original_sha256=bf7b28c99ba95cc98ccab4d8fe84d101664798d1b0aa7c9c8f82ce472439e4cb
# Private originals are required for native replay.
"""Bounded read-only acquisition and evidence utilities for the 861..866 queue.

This module deliberately offers no remote writer or firmware activation operation.
Stage806 emitted no PB070. A loader cannot safely be derived from that plan.
"""
from __future__ import annotations
import base64
from datetime import datetime, timezone
import hashlib
import ast
import json
import os
from pathlib import Path
import re
import socket
import time
import paramiko
ROOT = Path(__file__).resolve().parents[2]
HOSTS = frozenset(('198.18.0.45', '198.18.0.46', '198.18.0.48', '198.18.0.5', '198.18.0.6'))

def utc():
    return datetime.now(timezone.utc).isoformat()

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

def redact(text):
    return re.sub('(?im)^.*Encryption key:[^\\n]*$', '[REDACTED_WIRELESS_KEY_LINE]', text)

def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate_json_key')
        result[key] = value
    return result

def load(path):

    def reject(value):
        raise ValueError('nonfinite_json')
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs, parse_constant=reject)

def pin(path):
    path = Path(path).resolve()
    blob = path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=len(blob), sha256=sha(blob))

def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)

def credential():
    raise RuntimeError('PUBLIC_TRANSPORT_OR_CREDENTIAL_DISABLED: credential')

def capture(host, command, *, username='root', password='', timeout=20):
    raise RuntimeError('PUBLIC_TRANSPORT_OR_CREDENTIAL_DISABLED: capture')

def evidence_path(stage):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    return ROOT / f'artifacts/verification/stage{stage}/read_only_{stamp}.json'

def save_capture(stage, rows):
    path = evidence_path(stage)
    write(path, dict(stage=stage.upper(), captured_utc=utc(), results=rows, target_writes=False, firmware_loaded=False))
    return pin(path)
