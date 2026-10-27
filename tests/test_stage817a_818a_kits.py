"""Disposable offline regressions for composition and inspect-only kit boundaries."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys

import pytest

from firmware.xtensa_sgmt_surgical_patcher import SgmtContainer, SgmtSegment, bmi_lz_compress
from tools.firmware import build_stage817a_universal_pb060_triple_patch_openwrt_airos_kit as pb
from tools.firmware import build_stage818a_ltu_4096qam_12x_ldpc_and_super4096_safe_kit as ltu
from tools.firmware.build_stage474a_pb050_xtensa_rc_probe_dampener_sgmt_patch import get_pb050_rc_probe_dampen_specs_for_target
from tools.firmware.build_stage650a_pb060_xtensa_txop_and_tid_sched_sgmt_patch import get_pb060_specs_for_target


def fixture_sgmt():
    target = "OpenWrt_10.1.467-ct_IE3"
    specs = get_pb050_rc_probe_dampen_specs_for_target(target) + get_pb060_specs_for_target(target)
    bases = [0x00980000, 0x0040B000, 0x00400000, 0x00980000]
    segments = []
    for index, base in enumerate(bases):
        relevant = [sp for sp in specs if sp.segment_index == index]
        length = max([0x1020 if index == 3 else 32] + [sp.virtual_address - base + len(sp.expected_orig_bytes) for sp in relevant])
        raw = bytearray(length)
        for spec in relevant:
            offset = spec.virtual_address - base
            raw[offset:offset + len(spec.expected_orig_bytes)] = spec.expected_orig_bytes
        if index == 3:
            raw[0x1000:0x1000 + len(pb.PB040_BEFORE)] = pb.PB040_BEFORE
        data = bytes(raw)
        segments.append(SgmtSegment(index, base, data, bmi_lz_compress(data)))
    return target, SgmtContainer(1, tuple(segments), 0x00983C00).to_bytes(recompress=False)


def test_triple_composition_changes_all_three_families_and_preserves_layout():
    target, original = fixture_sgmt()
    output, receipts = pb.compose(target, original)
    assert output != original
    assert {r["patch_id"][:5] for r in receipts} == {"PB040", "PB050", "PB060"}
    before, after = SgmtContainer.from_bytes(original), SgmtContainer.from_bytes(output)
    assert [(s.destination, s.decoded_size) for s in before.segments] == [(s.destination, s.decoded_size) for s in after.segments]
    with pytest.raises(ValueError):
        pb.compose(target, output)  # Already patched is not an original.


def test_absent_originals_are_not_synthesized(tmp_path):
    helper = tmp_path / pb.HELPER
    helper.parent.mkdir(parents=True)
    helper.write_bytes((pb.ROOT / pb.HELPER).read_bytes())
    result = pb.build(tmp_path)
    assert result["status"] == "UNKNOWN"
    assert result["images"] == []
    assert not result["boundary"]["activation_available"]
    assert {Path(row["path"]).name for row in result["package_files"]} == {"SHA256SUMS", "fmx_pb060_triple_patch_loader.sh"}


@pytest.mark.parametrize("bridge,chain,proto,source,dest,blocked", [
    ("br1", "OUTPUT", "udp", 67, 68, True),
    ("br1", "FORWARD", "udp", 67, 68, True),
    ("br1", "OUTPUT", "udp", 547, 546, True),
    ("br0", "OUTPUT", "udp", 67, 68, False),
    ("br1", "INPUT", "udp", 67, 68, False),
    ("br1", "OUTPUT", "udp", 68, 67, False),
    ("br1", "OUTPUT", "tcp", 67, 68, False),
])
def test_br1_offer_policy_scope(bridge, chain, proto, source, dest, blocked):
    assert ltu.blocks_dhcp_offer(bridge, chain, proto, source, dest) is blocked


def test_missing_ltu_evidence_keeps_runtime_unknown(tmp_path):
    helper = tmp_path / ltu.HELPER
    helper.parent.mkdir(parents=True)
    helper.write_bytes((pb.ROOT / ltu.HELPER).read_bytes())
    result = ltu.build(tmp_path)
    assert result["status"] == "UNKNOWN"
    assert result["rogue_dhcp_remediation"]["zero_rogue_dhcp_verified"] is False
    assert result["rogue_dhcp_remediation"]["rogue_leases_emitted"] is None
    assert {Path(row["path"]).name for row in result["package_files"]} == {"SHA256SUMS", "fmx_ltu_4096qam_12x_safe_kit.sh"}


@pytest.mark.parametrize("label", [pb.HELPER, ltu.HELPER])
def test_shell_inspection_and_apply_refusal(label):
    bash = Path("C:/Program Files/Git/bin/bash.exe")
    command = str(bash) if bash.is_file() else shutil.which("sh")
    if command is None:
        pytest.skip("POSIX shell unavailable")
    path = pb.ROOT / label
    assert subprocess.run([command, "-n", str(path)], capture_output=True).returncode == 0
    inspect = subprocess.run([command, str(path)], capture_output=True, text=True)
    assert inspect.returncode == 0 and "UNKNOWN" in inspect.stdout
    refused = subprocess.run([command, str(path), "--apply"], capture_output=True, text=True)
    assert refused.returncode == 64 and "BLOCKED" in refused.stderr


def test_no_package_path_escape(tmp_path):
    with pytest.raises(ValueError):
        pb.local(tmp_path, "../outside")


STUB_DRIVER = r'''
import json, os, pathlib, sys
tool, args = sys.argv[1], sys.argv[2:]
base = pathlib.Path(os.environ['FMX_STUB_BASE'])
log = base / 'calls.jsonl'
with log.open('a') as stream:
    stream.write(json.dumps([tool, *args]) + '\n')
if tool == 'id':
    print(os.environ.get('FMX_STUB_UID', '0')); sys.exit(0)
if tool == 'ip':
    print('8: br1 inet ' + os.environ.get('FMX_STUB_IP', '192.168.1.20') + '/24 scope global br1'); sys.exit(0)
if args == ['--version']:
    print(os.environ.get('FMX_STUB_VERSION', 'ebtables v1.8.9 (nf_tables)')); sys.exit(0)
statepath = base / 'state.json'
state = json.loads(statepath.read_text()) if statepath.exists() else {'OUTPUT': [], 'FORWARD': [], 'UNRELATED': [['keep']]}
op, chain, *rule = args[2:]
fail = os.environ.get('FMX_STUB_FAIL', '')
if fail and any(part in ' '.join([op, chain, *rule]) for part in fail.split('|')):
    sys.exit(1)
if op == '-L':
    if chain not in state: sys.exit(1)
    for entry in state[chain]: print('ebtables -t filter -A ' + chain + ' ' + ' '.join(entry))
elif op == '-N':
    if chain in state: sys.exit(1)
    state[chain] = []
elif op == '-A':
    state[chain].append(rule)
elif op == '-I':
    state[chain].insert(int(rule[0])-1, rule[1:])
elif op == '-D':
    if rule not in state[chain]: sys.exit(1)
    state[chain].remove(rule)
elif op == '-F':
    state[chain] = []
elif op == '-X':
    if state[chain] or any(chain in rule for rules in state.values() for rule in rules): sys.exit(1)
    del state[chain]
else: sys.exit(2)
statepath.write_text(json.dumps(state))
'''


def stubbed_apply(tmp_path, *, confirmation=True, **settings):
    bash = Path("C:/Program Files/Git/bin/bash.exe")
    if not bash.is_file():
        pytest.skip("Git shell stub harness unavailable")
    bindir = tmp_path / "bin"
    bindir.mkdir(exist_ok=True)
    driver = tmp_path / "driver.py"
    driver.write_text(STUB_DRIVER, encoding="utf-8")
    for name in ("id", "ip", "ebtables"):
        (bindir / name).write_text(f'#!/bin/sh\nexec "{Path(sys.executable).as_posix()}" "{driver.as_posix()}" {name} "$@"\n', encoding="utf-8", newline="\n")
    environment = dict(os.environ, FMX_STUB_BASE=str(tmp_path), TMPDIR=tmp_path.as_posix())
    environment.update({f"FMX_STUB_{key.upper()}": str(value) for key, value in settings.items()})
    # Set PATH inside bash so every radio-facing command resolves to our stub.
    shell_bindir = "/" + bindir.drive[0].lower() + bindir.as_posix()[2:]
    command = f'PATH="{shell_bindir}:$PATH"; export PATH; exec sh "{(pb.ROOT / ltu.HELPER).as_posix()}" --apply-zero-dhcp'
    if confirmation:
        command += " --confirm-br1-192.168.1.20"
    return subprocess.run([str(bash), "-c", command], env=environment, capture_output=True, text=True)


def test_guarded_apply_is_scoped_and_idempotent_with_stubs(tmp_path):
    first = stubbed_apply(tmp_path)
    assert first.returncode == 0, first.stderr
    before = (tmp_path / "state.json").read_text()
    second = stubbed_apply(tmp_path)
    assert second.returncode == 0, second.stderr
    assert (tmp_path / "state.json").read_text() == before
    state = json.loads(before)
    assert state["UNRELATED"] == [["keep"]]
    assert state["OUTPUT"] == state["FORWARD"] == [["--logical-out", "br1", "-j", "FMX818_DHCP"]]
    assert len(state["FMX818_DHCP"]) == 2
    assert "lease_capture_verified=false" in first.stdout


@pytest.mark.parametrize("settings,confirmation", [
    ({}, False), ({"uid": "1000"}, True), ({"ip": "192.168.1.21"}, True),
    ({"version": "unknown firewall"}, True),
])
def test_apply_guards_never_mutate(tmp_path, settings, confirmation):
    result = stubbed_apply(tmp_path, confirmation=confirmation, **settings)
    assert result.returncode != 0
    assert not (tmp_path / "state.json").exists()


def test_partial_rule_failure_rolls_back_only_new_chain(tmp_path):
    result = stubbed_apply(tmp_path, fail="-I FORWARD")
    assert result.returncode != 0
    state = json.loads((tmp_path / "state.json").read_text())
    assert state == {"OUTPUT": [], "FORWARD": [], "UNRELATED": [["keep"]]}
    assert not (tmp_path / "fmx-stage818a-zero-dhcp.lock").exists()


def test_existing_incompatible_chain_is_preserved(tmp_path):
    before = {"OUTPUT": [], "FORWARD": [], "FMX818_DHCP": [["-j", "ACCEPT"]], "UNRELATED": [["keep"]]}
    (tmp_path / "state.json").write_text(json.dumps(before))
    result = stubbed_apply(tmp_path)
    assert result.returncode != 0
    assert json.loads((tmp_path / "state.json").read_text()) == before


def test_incomplete_rollback_is_reported(tmp_path):
    result = stubbed_apply(tmp_path, fail="-I FORWARD|-X FMX818_DHCP")
    assert result.returncode == 70
    assert "ROLLBACK_INCOMPLETE" in result.stderr
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["UNRELATED"] == [["keep"]]


def test_owned_jumps_precede_existing_accept_and_preserve_it(tmp_path):
    before = {"OUTPUT": [["-j", "ACCEPT"]], "FORWARD": [["-j", "ACCEPT"]], "UNRELATED": [["keep"]]}
    (tmp_path / "state.json").write_text(json.dumps(before))
    result = stubbed_apply(tmp_path)
    assert result.returncode == 0, result.stderr
    state = json.loads((tmp_path / "state.json").read_text())
    for parent in ("OUTPUT", "FORWARD"):
        assert state[parent] == [["--logical-out", "br1", "-j", "FMX818_DHCP"], ["-j", "ACCEPT"]]
    # An outside writer moving ACCEPT ahead of our jump must invalidate repeats.
    state["OUTPUT"].reverse()
    (tmp_path / "state.json").write_text(json.dumps(state))
    refused = stubbed_apply(tmp_path)
    assert refused.returncode == 78
    assert json.loads((tmp_path / "state.json").read_text()) == state
