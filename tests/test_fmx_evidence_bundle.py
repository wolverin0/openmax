from copy import deepcopy
from hashlib import sha256
import pytest

from orchestration.autoresearch.fmx_evidence_bundle import (
    build_evidence_bundle, bundle_digest, verify_evidence_bundle,
)


def make(tmp_path):
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs/data.json").write_text('{"schema":9,"original_pointer":"not-followed"}')
    (tmp_path / "code.py").write_text('# never executed\n')
    paths = ["inputs/data.json", "code.py"]
    bundle = build_evidence_bundle(tmp_path, paths, allowed_paths=paths,
                                   schema_provenance={"records_schema": 9, "records": 212, "rounds": 56})
    return bundle, paths


def test_manifest_repeatable_source_bound_and_nonactuating(tmp_path):
    b, paths = make(tmp_path)
    result = verify_evidence_bundle(b, tmp_path, allowed_paths=paths, expected_bundle_sha256=bundle_digest(b))
    assert result["files_verified"] == 2 and result["status"] == "VERIFIED_LOCAL_BYTES_ONLY"
    assert b["schema_provenance"]["records"] == 212
    assert not result["physical_acceptance"] and not b["original_source_pointers_followed"]
    reverse = build_evidence_bundle(tmp_path, paths[::-1], allowed_paths=paths, schema_provenance=b["schema_provenance"])
    assert bundle_digest(b) == bundle_digest(reverse)


def test_changed_file_fails_even_with_unchanged_manifest(tmp_path):
    b, paths = make(tmp_path); (tmp_path / "code.py").write_text('# changed\n')
    with pytest.raises(ValueError, match="tampered"): verify_evidence_bundle(b, tmp_path, allowed_paths=paths, expected_bundle_sha256=bundle_digest(b))


def test_forged_metadata_cannot_replace_external_pin(tmp_path):
    b, paths = make(tmp_path); pin=bundle_digest(b); b["schema_provenance"]["records"] = 999
    with pytest.raises(ValueError, match="trusted"): verify_evidence_bundle(b, tmp_path, allowed_paths=paths, expected_bundle_sha256=pin)


@pytest.mark.parametrize("name", ["../outside", "/absolute", "//host/share", "C:/file", "inputs/../data.json", "inputs\\data.json", "inputs/data.json:stream", "./code.py", "inputs//data.json", "inputs/r76_new.json"])
def test_path_and_future_round_boundaries_before_read(tmp_path, name):
    with pytest.raises(ValueError): build_evidence_bundle(tmp_path, [name], allowed_paths=[name], schema_provenance={"schema": 1})


@pytest.mark.parametrize("mutation", ["boolean_bytes", "promote", "physical", "schema_bool", "duplicate", "uppercase_sha", "new_pointer"])
def test_repinning_does_not_relax_manifest_schema_or_safety(tmp_path, mutation):
    b, paths = make(tmp_path)
    if mutation == "boolean_bytes": b["files"][0]["bytes"] = True
    if mutation == "promote": b["automatic_execution_allowed"] = True
    if mutation == "physical": b["physical_acceptance"] = True
    if mutation == "schema_bool": b["schema_version"] = True
    if mutation == "duplicate": b["files"].append(deepcopy(b["files"][0]))
    if mutation == "uppercase_sha": b["files"][0]["sha256"] = b["files"][0]["sha256"].upper()
    if mutation == "new_pointer": b["files"][0]["original_source"] = "secret"
    with pytest.raises(ValueError): verify_evidence_bundle(b, tmp_path, allowed_paths=paths, expected_bundle_sha256=bundle_digest(b))


def test_allowlist_is_a_separate_boundary_from_selfasserted_files(tmp_path):
    b, paths = make(tmp_path)
    with pytest.raises(ValueError, match="allowlist"): verify_evidence_bundle(b, tmp_path, allowed_paths=["code.py"], expected_bundle_sha256=bundle_digest(b))


def test_symlink_does_not_expand_evidence_scope(tmp_path, monkeypatch):
    # Host Windows may forbid native symlink creation. Simulate only the lstat
    # classification, then prove rejection occurs before reading its contents.
    link=tmp_path / "alias"; link.write_text('must-not-be-read')
    native = type(link).is_symlink
    monkeypatch.setattr(type(link), "is_symlink", lambda self: self == link or native(self))
    with pytest.raises(ValueError, match="Symlink"): build_evidence_bundle(tmp_path, ["alias"], allowed_paths=["alias"], schema_provenance={"schema":1})


@pytest.mark.parametrize("pin", [None, "", "0"*63, True])
def test_external_digest_mandatory(tmp_path, pin):
    b, paths = make(tmp_path)
    with pytest.raises(ValueError): verify_evidence_bundle(b, tmp_path, allowed_paths=paths, expected_bundle_sha256=pin)


@pytest.mark.parametrize('round_id',['r57','r58','r59','r60'])
def test_ao_explicit_frozen_round_path_permitted_when_source_allowlisted(tmp_path,round_id):
    name=round_id+'_frozen.json';(tmp_path/name).write_text('{"source_snapshot":true}')
    bundle=build_evidence_bundle(tmp_path,[name],allowed_paths=[name],schema_provenance={'schema':11})
    verified=verify_evidence_bundle(bundle,tmp_path,allowed_paths=[name],expected_bundle_sha256=bundle_digest(bundle))
    assert verified['files_verified']==1 and not verified['automatic_execution_allowed']


def test_ao_future_round_rejected_before_any_content_read(tmp_path,monkeypatch):
    name='r76_forbidden.json';p=tmp_path/name;p.write_text('do not read')
    native=type(p).read_bytes
    def read(path):
        if path==p:raise AssertionError('future content was read')
        return native(path)
    monkeypatch.setattr(type(p),'read_bytes',read)
    with pytest.raises(ValueError,match='R76'):
        build_evidence_bundle(tmp_path,[name],allowed_paths=[name],schema_provenance={'schema':11})


@pytest.mark.parametrize('round_id', ['r61', 'r62', 'r63', 'r64', 'r65'])
def test_as_new_frozen_round_allowlisted_bundle_is_hash_bound(tmp_path, round_id):
    name = round_id + '_frozen.json'
    (tmp_path / name).write_text('{"source_snapshot":true}')
    bundle = build_evidence_bundle(tmp_path, [name], allowed_paths=[name], schema_provenance={'schema':12})
    pin = bundle_digest(bundle)
    assert verify_evidence_bundle(bundle, tmp_path, allowed_paths=[name], expected_bundle_sha256=pin)['files_verified'] == 1
    (tmp_path / name).write_text('{"source_snapshot":false}')
    with pytest.raises(ValueError, match='tampered'):
        verify_evidence_bundle(bundle, tmp_path, allowed_paths=[name], expected_bundle_sha256=pin)


@pytest.mark.parametrize('round_id', ['r66', 'r67', 'r68', 'r69', 'r70'])
def test_aw_new_round_allowlisted_bytes_and_tamper_are_distinct(tmp_path, round_id):
    name = round_id + '_frozen.json'
    (tmp_path / name).write_text('{"disposable":true}')
    bundle = build_evidence_bundle(tmp_path, [name], allowed_paths=[name], schema_provenance={'schema':13})
    pin = bundle_digest(bundle)
    assert verify_evidence_bundle(bundle, tmp_path, allowed_paths=[name], expected_bundle_sha256=pin)['files_verified'] == 1
    (tmp_path / name).write_text('{"disposable":false}')
    with pytest.raises(ValueError, match='tampered'):
        verify_evidence_bundle(bundle, tmp_path, allowed_paths=[name], expected_bundle_sha256=pin)


@pytest.mark.parametrize('round_id', ['r71', 'r72', 'r73', 'r74', 'r75'])
def test_ba_allowlisted_new_source_bytes_remain_tamper_bound(tmp_path, round_id):
    name = round_id+'_frozen.json'; path = tmp_path/name
    path.write_text('{"disposable":true}')
    bundle = build_evidence_bundle(tmp_path, [name], allowed_paths=[name], schema_provenance={'schema':14})
    pin = bundle_digest(bundle)
    assert verify_evidence_bundle(bundle, tmp_path, allowed_paths=[name], expected_bundle_sha256=pin)['files_verified'] == 1
    path.write_text('{"disposable":false}')
    with pytest.raises(ValueError, match='tampered'):
        verify_evidence_bundle(bundle, tmp_path, allowed_paths=[name], expected_bundle_sha256=pin)
