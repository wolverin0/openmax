"""Offline contract regressions. Never execute generated scripts or device tools."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path

import pytest

from firmware import pb040_ram_tmpfs_canary_preparer as preparer


@pytest.fixture(scope="session")
def plan():
    return preparer.build_plan()


def test_real_held_canary_before_after_and_all_originals(plan):
    proof = plan["canary_evidence"]
    assert proof["images_verified"] == 3
    assert proof["segments_verified"] == 12
    assert proof["independent_decoder_agrees"] is True
    assert proof["in_memory_roundtrip_verified"] is True
    assert proof["before_sgmt"] == {"bytes": 251681, "sha256": preparer.BEFORE_SGMT}
    assert proof["after_sgmt"] == {"bytes": 251839, "sha256": preparer.AFTER_SGMT}
    assert proof["before_segment_sha256"] == preparer.BEFORE_SEGMENT
    assert proof["after_segment_sha256"] == preparer.AFTER_SEGMENT
    assert proof["segment_bytes"] == 8500
    assert proof["changed_decoded_bytes"] == 1
    assert (proof["segment_index"], proof["segment_offset"], proof["virtual_address"]) == (1, 2387, "0x0040b953")
    assert (proof["before_byte_hex"], proof["after_byte_hex"]) == ("65", "45")
    assert proof["entry_point"] == "0x00983c00"
    assert proof["done_address"] == 0
    assert proof["binary_payload_exported"] is False


def test_vendor_sgmt_never_misrepresented_as_api5_or_hardware_acceptance(plan):
    assert plan["loader"]["raw_sgmt_is_api5"] is False
    assert plan["loader"]["compatibility_verified"] is False
    assert plan["loader"]["wrapper_alone_proves_abi"] is False
    assert plan["loader"]["stock_api5_sha256"] is None
    assert plan["loader"]["canary_api5_sha256"] is None
    assert plan["physical_acceptance"] is False
    assert plan["runtime_ram_only_verified"] is False
    assert plan["watchdog"]["armed"] is False
    assert plan["rollback"]["verified"] is False
    assert plan["runtime_rollback_implemented"] is False
    assert plan["surrogate"] == dict(new_physical_observations=0, ready_cells_added=0,
                                     training_or_performance_claims_added=False, files_updated=[])


def test_exact_requested_copy_and_bind_and_rollback_order(plan):
    fs = plan["filesystem"]
    assert fs["original_copy_command"] == (
        "cp /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin /tmp/fw_canary/firmware-5.bin")
    assert fs["bind_command"] == (
        "mount -o bind /tmp/fw_canary/firmware-5.bin /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin")
    main, rollback = plan["scripts"]["main"], plan["scripts"]["rollback"]
    assert main.index(fs["original_copy_command"]) < main.index("cp /tmp/fw_canary_staging")
    assert main.index("journal_pending_bind") < main.index(fs["bind_command"])
    assert main.index("independent_guard_pid_birth_argv_and_READY") < main.index(fs["bind_command"])
    assert rollback.index("top_bind_id_source_inode") < rollback.index("timeout 5 umount")
    assert rollback.index("timeout 5 umount") < rollback.index("sha256_matches") < rollback.index("rmmod ath10k_pci")
    assert rollback.index("modprobe ath10k_pci") < rollback.index("exact_stock_firmware_ready")
    assert rollback.index("exact_stock_firmware_ready") < rollback.index("publish_RESTORED")
    assert "no active swap" in " ".join(fs["required_before_writes"])
    assert fs["allowed_write_roots"] == ["/tmp/fw_canary", "/tmp/fw_canary_control"]


@pytest.mark.parametrize("name", ["main", "watchdog", "rollback"])
def test_all_scripts_unconditionally_refuse_before_any_mutation(plan, name):
    text = plan["scripts"][name]
    executable = [s.strip() for s in text.splitlines() if s.strip() and not s.lstrip().startswith("#")]
    assert executable[0].startswith("printf ")
    assert executable[1] == "exit 78"
    assert "observe() { return 78; }" in text
    assert "STOCK_API5_SHA256=UNQUALIFIED" in text
    assert "CANARY_API5_SHA256=UNQUALIFIED" in text
    assert hashlib.sha256(text.encode()).hexdigest() == plan["script_sha256"][name]
    assert preparer.validate_scripts(plan["scripts"]) is True


@pytest.mark.parametrize("attack", [
    "mtd write x firmware", "sysupgrade /tmp/x", "dd if=/tmp/x of=/dev/mtd0",
    "busybox dd if=/tmp/x of=/dev/mtdblock0", "x=d; ${x}${x} if=/tmp/x of=/dev/mtd0",
    "eval 'mtd write x firmware'", "sh -c 'sysupgrade x'", "$(echo dd) if=x of=y",
    "`echo dd` if=x of=y", "umount -a", "rmmod -f ath10k_pci",
    "touch /lib/firmware/overwritten", "# innocuous comment still changes the canonical program",
])
@pytest.mark.parametrize("position", ["before_gate", "after_gate"])
def test_freeform_or_encoded_shell_is_rejected_even_if_inert(plan, attack, position):
    scripts = copy.deepcopy(plan["scripts"])
    if position == "before_gate":
        scripts["main"] = scripts["main"].replace("exit 78\n", attack + "\nexit 78\n", 1)
    else:
        scripts["main"] += attack + "\n"
    with pytest.raises(ValueError, match="Noncanonical"):
        preparer.validate_scripts(scripts)


@pytest.mark.parametrize("seconds", [True, False, 0, 9, 61, 30.0, "30", None, float("nan")])
def test_watchdog_budget_is_typed_and_bounded(seconds):
    with pytest.raises(ValueError, match="Watchdog seconds"):
        preparer.render_scripts(seconds)


@pytest.mark.parametrize("seconds", [10, 30, 60])
def test_finite_watchdog_reference_and_cleanup_coordination(seconds):
    scripts = preparer.render_scripts(seconds)
    assert f"sleep {seconds}\n/bin/sh /tmp/fw_canary_control/rollback.sh" in scripts["watchdog"]
    assert "trap '' HUP" in scripts["watchdog"]
    assert "flock -w 5 8" in scripts["rollback"]
    assert "rollback_rc=$?" in scripts["main"]
    assert "if [ \"$rollback_rc\" -ne 0 ]; then exit 1; fi" in scripts["main"]
    assert preparer.validate_scripts(scripts, seconds)


def test_exported_artifact_is_fresh_canonical_evidence(plan):
    artifact = preparer.load_json(preparer.read_local(preparer.ROOT / preparer.OUTPUT))
    assert artifact == plan
    assert preparer.validate_plan(artifact)


@pytest.mark.parametrize("path,value", [
    (("automatic_execution_allowed",), True), (("physical_acceptance",), True),
    (("scripts_inert",), False), (("runtime_rollback_implemented",), True),
    (("runtime_observers",), "READY"), (("runtime_ram_only_verified",), True),
    (("loader", "compatibility_verified"), True),
    (("loader", "canary_api5_sha256"), preparer.AFTER_SGMT),
    (("rollback", "verified"), True), (("watchdog", "armed"), True),
    (("surrogate", "new_physical_observations"), 1),
    (("surrogate", "new_physical_observations"), False),
    (("canary_evidence", "after_sgmt", "sha256"), "0" * 64),
])
def test_validator_rejects_forged_nested_readiness_or_hashes(plan, monkeypatch, path, value):
    # Expensive in-memory proof is exercised in the preceding real-source test.
    # Isolate canonical field validation here, reusing only that unchanged proof.
    monkeypatch.setattr(preparer, "verify_canary", lambda: copy.deepcopy(plan["canary_evidence"]))
    tampered = copy.deepcopy(plan)
    cursor = tampered
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    with pytest.raises(ValueError, match="canonical evidence"):
        preparer.validate_plan(tampered)


def test_rehashing_a_changed_script_cannot_authorize_it(plan, monkeypatch):
    monkeypatch.setattr(preparer, "verify_canary", lambda: copy.deepcopy(plan["canary_evidence"]))
    tampered = copy.deepcopy(plan)
    tampered["scripts"]["main"] = tampered["scripts"]["main"].replace("exit 78\n", "exit 0\n", 1)
    tampered["script_sha256"]["main"] = preparer.sha256(tampered["scripts"]["main"].encode())
    with pytest.raises(ValueError, match="Noncanonical"):
        preparer.validate_plan(tampered)


def test_source_hash_drift_blocks_before_helper_import(monkeypatch):
    monkeypatch.setitem(preparer.PINS, preparer.SPEC, "0" * 64)
    monkeypatch.setattr(preparer, "_helper", lambda *_: pytest.fail("Unverified source imported"))
    with pytest.raises(ValueError, match="Source SHA256 mismatch"):
        preparer.verify_canary()


@pytest.mark.parametrize("value", [r"\\server\share\x.json", "//server/share/x.json",
                                       r"\\?\C:\x.json", r"\??\C:\x.json", "https://example/x",
                                       "file:///C:/x", "ssh://radio/tmp/x", "NUL"])
def test_remote_and_device_paths_rejected_before_io(value, monkeypatch):
    monkeypatch.setattr(Path, "lstat", lambda *_: pytest.fail("Remote path probed"))
    with pytest.raises(ValueError):
        preparer.local_path(value)


def test_reparse_parent_rejected_before_child_traversal(monkeypatch, tmp_path):
    parent = tmp_path / "junction"
    parent.mkdir()
    original = Path.lstat
    def fake_lstat(path):
        if path == parent:
            return type("Info", (), {"st_mode": 0o040700, "st_file_attributes": 0x400})()
        if parent in path.parents:
            pytest.fail("Traversed an untrusted reparse parent")
        return original(path)
    monkeypatch.setattr(Path, "lstat", fake_lstat)
    with pytest.raises(ValueError, match="reparse"):
        preparer.local_path(parent / "child.json")


def test_duplicate_and_nonfinite_json_rejected():
    for raw in ['{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}']:
        with pytest.raises(ValueError):
            preparer.load_json(raw)


def test_host_preparer_has_no_actuation_or_binary_export_api():
    source = (preparer.ROOT / "firmware/pb040_ram_tmpfs_canary_preparer.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {n.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
               for n in node.names}
    assert not imports & {"subprocess", "socket", "paramiko", "requests", "urllib"}
    assert not any(isinstance(n, ast.Assert) for n in ast.walk(tree))
    calls = [n.func for n in ast.walk(tree) if isinstance(n, ast.Call)]
    assert not any(isinstance(n, ast.Attribute) and n.attr in
                   {"system", "popen", "spawn", "write_bytes", "execv", "execve"} for n in calls)


def test_cli_cannot_accept_execution_or_qualification_flags():
    for flag in ["--execute", "--ssh", "--enable", "--canary", "--allow-flash", "--qualified"]:
        with pytest.raises(SystemExit) as result:
            preparer.main([flag])
        assert result.value.code == 2
