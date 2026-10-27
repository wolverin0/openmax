"""Explicit-allowlist, source-bound offline evidence manifests.

Only caller-listed local regular files are read. Original-source pointers inside
JSON are never followed. A trusted external bundle digest is mandatory during
verification: a self-asserted acceptance string is not an integrity boundary.
No archive extraction, file deletion, target execution or network is provided.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from pathlib import Path, PurePosixPath

MAX_FILE_BYTES = 20_000_000
MAX_TOTAL_BYTES = 100_000_000


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("Finite JSON metadata required") from exc


def bundle_digest(bundle):
    return sha256(_canonical(bundle)).hexdigest()


def _name(name):
    if not isinstance(name, str) or not name or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError("Canonical relative POSIX path required")
    p = PurePosixPath(name)
    if p.is_absolute() or str(p) != name or any(x in ("", ".", "..") for x in name.split("/")):
        raise ValueError("Traversal/noncanonical path forbidden")
    if re.search(r"(?:^|[_/.-])r(?:7[6-9]|[8-9][0-9]|[1-9][0-9]{2,})(?:[_/.-]|$)", name.lower()):
        raise ValueError("R76+ artifacts outside this campaign")
    return name


def _file(root, name, allowed):
    name = _name(name)
    if name not in allowed:
        raise ValueError("File not in explicit caller allowlist")
    p = root
    for part in PurePosixPath(name).parts:
        p = p / part
        # Reject links at every level, including Windows junction/reparse points.
        if p.is_symlink() or p.is_junction():
            raise ValueError("Symlink/junction evidence forbidden")
    try:
        p.resolve(strict=True).relative_to(root)
    except (ValueError, OSError) as exc:
        raise ValueError("Missing/outside evidence file") from exc
    if not p.is_file():
        raise ValueError("Regular evidence file required")
    size = p.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ValueError("Evidence file bound exceeded")
    data = p.read_bytes()
    if len(data) != size:
        raise ValueError("Evidence changed during read")
    return dict(path=name, bytes=len(data), sha256=sha256(data).hexdigest())


def _allowlist(allowed_paths):
    if not isinstance(allowed_paths, (tuple, list, set, frozenset)) or not allowed_paths:
        raise ValueError("Nonempty explicit allowlist required")
    names = [_name(x) for x in allowed_paths]
    if len(set(names)) != len(names) or len({x.casefold() for x in names}) != len(names):
        raise ValueError("Duplicate/case-colliding paths")
    return set(names)


def build_evidence_bundle(root, files, *, allowed_paths, schema_provenance):
    """Return manifest only; caller owns saving it and its external digest pin."""
    root = Path(root).resolve(strict=True)
    allowed = _allowlist(allowed_paths)
    if not isinstance(files, (tuple, list)) or not 1 <= len(files) <= 256:
        raise ValueError("Bounded nonempty explicit file list required")
    names = [_name(x) for x in files]
    if len(set(names)) != len(names) or len({x.casefold() for x in names}) != len(names):
        raise ValueError("Duplicate/case-colliding files")
    if not isinstance(schema_provenance, dict) or not schema_provenance:
        raise ValueError("Explicit schema provenance required")
    _canonical(schema_provenance)
    bindings = [_file(root, name, allowed) for name in sorted(names)]
    if sum(x["bytes"] for x in bindings) > MAX_TOTAL_BYTES:
        raise ValueError("Total bundle size exceeded")
    return dict(schema_version=1, kind="OFFLINE_SOURCE_BOUND_EVIDENCE_MANIFEST",
                files=bindings, schema_provenance=json.loads(_canonical(schema_provenance)),
                automatic_execution_allowed=False, physical_acceptance=False,
                original_source_pointers_followed=False,
                limits=["Digests prove local byte consistency, not measurement truth or physical acceptance", "External trusted digest required; self-asserted status is not acceptance"])


def verify_evidence_bundle(bundle, root, *, allowed_paths, expected_bundle_sha256):
    if not isinstance(expected_bundle_sha256, str) or not re.fullmatch("[0-9a-f]{64}", expected_bundle_sha256):
        raise ValueError("External lowercase SHA256 pin required")
    if not isinstance(bundle, dict) or bundle_digest(bundle) != expected_bundle_sha256:
        raise ValueError("Bundle differs from external trusted digest")
    if type(bundle.get("schema_version")) is not int or bundle["schema_version"] != 1:
        raise ValueError("Unsupported schema")
    for flag in ("automatic_execution_allowed", "physical_acceptance", "original_source_pointers_followed"):
        if bundle.get(flag) is not False:
            raise ValueError("Nonactuation/source scope flag changed")
    if bundle.get("kind") != "OFFLINE_SOURCE_BOUND_EVIDENCE_MANIFEST":
        raise ValueError("Unknown bundle kind")
    rows = bundle.get("files")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 256:
        raise ValueError("Bounded bindings required")
    if any(not isinstance(x, dict) or set(x) != {"path", "bytes", "sha256"} for x in rows):
        raise ValueError("Exact binding schema required")
    for row in rows:
        if type(row["bytes"]) is not int or not 0 <= row["bytes"] <= MAX_FILE_BYTES or not isinstance(row["sha256"], str) or not re.fullmatch("[0-9a-f]{64}", row["sha256"]):
            raise ValueError("Malformed byte/hash binding")
    rebuilt = build_evidence_bundle(root, [x["path"] for x in rows], allowed_paths=allowed_paths,
                                    schema_provenance=bundle.get("schema_provenance"))
    if rebuilt != bundle:
        raise ValueError("Evidence file tampered or manifest changed")
    return dict(status="VERIFIED_LOCAL_BYTES_ONLY", files_verified=len(rows),
                bytes_verified=sum(x["bytes"] for x in rows), bundle_sha256=expected_bundle_sha256,
                automatic_execution_allowed=False, physical_acceptance=False)
