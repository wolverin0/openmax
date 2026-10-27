#!/usr/bin/env python3
"""Strictly offline PB040 evidence verifier and INERT tmpfs canary plan renderer.

No subprocess, network, device I/O, firmware export or execution API exists here.
The held vendor SGMT is NOT a qualified ath10k API5 firmware-5.bin. All three
shell references exit 78 unconditionally; their runtime observers are absent.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import re
import stat
import sys
from pathlib import Path, PureWindowsPath
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "T-S23-CODEX-PB040-CANARY-LOADER-AND-SURROGATE-UPDATE"
OUTPUT = "artifacts/physical_boundary/pb040_ram_tmpfs_canary_plan_20261025.json"
SPEC = "artifacts/physical_boundary/pb040_sgmt_surgical_patch_spec_20261025.json"
UMAC = "firmware/build/codex-analysis-20261006/rootfs/lib/modules/2.6.32.68/umac.ko"
PATCHER = "firmware/xtensa_sgmt_surgical_patcher.py"
ELF = "analysis/re_ubnt_poll_and_ltu_4096qam.py"
DECODER = "tools/research/sgmt.py"
CORE = "tools/research/srccache/ath10k-ct/ath10k-7.2/core.c"
HW = "tools/research/srccache/ath10k-ct/ath10k-7.2/hw.h"
PINS = {
    SPEC: "ea397abb4f522425674a75ab03554baf02837c3737adf189cfe1a9dbadc07c64",
    UMAC: "46525dc6f8b789bf820f0713841a2a9ecdcba833300ddb1ab1ef06fc4ab6a9c5",
    PATCHER: "49cb277389bc20af708777d4a5e23cc4d923d91b4d83c5a97bde683096f1451d",
    ELF: "118a02ee21abe31eedd7d3dfea3c7b32359ac8e16276bf65c290a89fc87ca770",
    DECODER: "f6e8a73fa2277a26901469a825373dba512262464015e8772a4acf6a1f47dec8",
    CORE: "21e80dc61a721bac8833751775a81198aca153b38f96b0c87de6db0d64e83bf3",
    HW: "ce9d1cbb43e64af6fddf40c47b5843e72b9519c94315a6f085b77ac2812d1327",
}
TARGET = "/lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin"
RAM_FILE = "/tmp/fw_canary/firmware-5.bin"
STAGING = "/tmp/fw_canary_staging/firmware-5.bin"
CONTROL = "/tmp/fw_canary_control"
BIND_COMMAND = f"mount -o bind {RAM_FILE} {TARGET}"
COPY_COMMAND = f"cp {TARGET} {RAM_FILE}"
CANARY_ID = "PB040-CANARY-RODATA"
AP = "athwlan_AR9888v2_ptmp_ap_bin"
BEFORE_SGMT = "55e9c94a2f0b466ff50ced26f589c755b955e751861b466bb71be9f87de261ee"
AFTER_SGMT = "e2402d644fc85e595d9efca09c65281076d05f839e3f47a94b7e9f8b2c82b415"
BEFORE_SEGMENT = "4352471afde9d65477ebf3af97cdfffb48080895a43b3e71745c08389c589483"
AFTER_SEGMENT = "5bae628f353f7e7960310a594ecba663555a7e7292e29a05c4f118d06b19bfdb"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def local_path(value) -> Path:
    """Reject remote/device paths and reparse ancestors before traversing them."""
    text = os.fspath(value)
    if not isinstance(text, str):
        raise ValueError("Local text path required")
    win = text.replace("/", "\\")
    if (win.startswith(("\\\\", "\\??\\"))
            or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", text)
            or PureWindowsPath(text).is_reserved()):
        raise ValueError("Strictly offline: remote/device paths forbidden")
    path = Path(text).absolute()
    if os.name == "nt":
        import ctypes
        if ctypes.windll.kernel32.GetDriveTypeW(str(path.anchor)) == 4:
            raise ValueError("Strictly offline: mapped remote drive forbidden")
    for ancestor in reversed((path, *path.parents)):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            break
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Symlink/reparse paths forbidden")
    return path


def read_local(value, maximum=8 * 1024 * 1024) -> bytes:
    path = local_path(value)
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > maximum:
        raise ValueError("Bounded regular input file required")
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError("Input exceeds size limit")
    return raw


def _pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def load_json(raw):
    def reject(value):
        raise ValueError(f"Nonfinite JSON constant: {value}")
    return json.loads(raw, object_pairs_hook=_pairs_no_duplicates, parse_constant=reject)


def _require(condition, message):
    # Safety checks stay active under python -O, including checks after helpers
    # that historically used assert internally.
    if not condition:
        raise ValueError(message)


def _sources():
    raw, bindings = {}, []
    for relative, digest in PINS.items():
        content = read_local(ROOT / relative)
        _require(sha256(content) == digest, f"Source SHA256 mismatch: {relative}")
        raw[relative] = content
        bindings.append(dict(path=relative, bytes=len(content), sha256=digest))
    return raw, bindings


def _helper(name, relative):
    # Import only already-authenticated, local, existing pure analysis helpers.
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    module = importlib.import_module(name)
    _require(local_path(module.__file__) == local_path(ROOT / relative),
             f"Unexpected imported helper location: {name}")
    return module


def _crosscheck(container, blob, decoder):
    metadata, payloads = decoder.decode_sgmt_memory(blob)
    _require(metadata["file_flags"] == container.file_flags
             and metadata["consumed_bytes"] == len(blob), "SGMT flags/consumption drift")
    _require(payloads == [(s.destination, s.decoded_bytes) for s in container.segments],
             "Independent decoder payload/destination disagreement")
    specials = [(r["kind"], r["destination"]) for r in metadata["records"]
                if r["kind"] != "PAYLOAD"]
    _require(specials == [("BEGINADDR", container.entry_point), ("DONE", container.done_address)],
             "Independent decoder entry/DONE disagreement")
    return metadata


def verify_canary():
    """Recompute all evidence in memory; return metadata only, never payloads."""
    raw, bindings = _sources()
    spec = load_json(raw[SPEC])
    _require(spec["source_umac_sha256"] == PINS[UMAC], "PB040 UMAC binding drift")
    _helper("analysis.re_ubnt_poll_and_ltu_4096qam", ELF)
    patcher = _helper("firmware.xtensa_sgmt_surgical_patcher", PATCHER)
    decoder = _helper("tools.research.sgmt", DECODER)
    # Elf32Image accepts a read_bytes provider: parse the authenticated snapshot,
    # avoiding a second filesystem read or firmware extraction to disk.
    elf = patcher.Elf32Image(SimpleNamespace(read_bytes=lambda: raw[UMAC]))
    data = elf.section_bytes(".data")
    symbols = {s["name"]: s for s in elf.symbols}
    containers, images = {}, []
    retained = spec["bmi_lz_roundtrip_verification"]["images"]
    for name in patcher.AR9888V2_IMAGE_SYMBOLS:
        sym = symbols[name]
        _require(sym["section"] == ".data", "SGMT symbol moved outside .data")
        blob = data[sym["value"]:sym["value"] + sym["size"]]
        container = patcher.SgmtContainer.from_bytes(blob)
        _require(container.to_bytes(recompress=False) == blob, "Original SGMT serialization drift")
        _crosscheck(container, blob, decoder)
        old = retained[name]
        _require(sha256(blob) == old["orig_container_sha256"]
                 and len(blob) == old["orig_container_size_bytes"], "Original SGMT pin drift")
        segments = []
        for segment, recorded in zip(container.segments, old["segments"], strict=True):
            compressed = patcher.bmi_lz_compress(segment.decoded_bytes, enable_lz77=True)
            decoded = patcher.bmi_lz_decompress(compressed, segment.decoded_size)
            _require(decoded == segment.decoded_bytes, "Original segment round-trip drift")
            _require(segment.destination_hex == recorded["destination_hex"]
                     and segment.decoded_size == recorded["decoded_size_bytes"]
                     and segment.decoded_sha256 == recorded["decoded_sha256"], "Segment pin drift")
            segments.append(dict(index=segment.index, destination=segment.destination_hex,
                                 bytes=segment.decoded_size, sha256=segment.decoded_sha256))
        _require(container.entry_point == 0x983c00 and container.done_address == 0,
                 "Original BEGINADDR/DONE drift")
        containers[name] = container
        images.append(dict(symbol=name, bytes=len(blob), sha256=sha256(blob),
                           entry_point="0x00983c00", done_address=0, segments=segments))
    choices = [p for p in patcher.get_pb040_surgical_patch_specs() if p.patch_id == CANARY_ID]
    _require(len(choices) == 1, "Exactly one PB040 canary specification required")
    choice = choices[0]
    _require((choice.target_symbol, choice.segment_index, choice.virtual_address,
              choice.expected_orig_bytes, choice.patched_bytes) == (AP, 1, 0x40b953, b"e", b"E"),
             "Canary specification changed")
    original = containers[AP]
    patched, receipt = patcher.SgmtSurgicalPatcher.validate_and_apply(original, choice)
    result = patched.to_bytes(recompress=False)
    reparsed = patcher.SgmtContainer.from_bytes(result)
    _crosscheck(reparsed, result, decoder)
    _require((reparsed.entry_point, reparsed.done_address, reparsed.file_flags) ==
             (original.entry_point, original.done_address, original.file_flags), "Canary control records drift")
    differences = []
    for left, right in zip(original.segments, reparsed.segments, strict=True):
        _require(left.destination == right.destination and left.decoded_size == right.decoded_size,
                 "Canary segment address/size drift")
        differences.extend((left.index, i, a, b) for i, (a, b) in
                           enumerate(zip(left.decoded_bytes, right.decoded_bytes, strict=True)) if a != b)
        if left.index != 1:
            _require(left.compressed_bytes == right.compressed_bytes, "Untargeted stored segment changed")
    _require(differences == [(1, 2387, 0x65, 0x45)], "Canary must change exactly one decoded byte")
    _require(original.original_container_sha256 == BEFORE_SGMT
             and sha256(result) == AFTER_SGMT and len(result) == 251839
             and original.segments[1].decoded_sha256 == BEFORE_SEGMENT
             and reparsed.segments[1].decoded_sha256 == AFTER_SEGMENT, "Canary before/after pin drift")
    recorded = [p for p in spec["surgical_patch_specifications"] if p["patch_id"] == CANARY_ID]
    _require(len(recorded) == 1 and receipt == recorded[0], "Retained canary receipt disagreement")
    return dict(
        in_memory_roundtrip_verified=True, independent_decoder_agrees=True,
        images_verified=len(images), segments_verified=sum(len(i["segments"]) for i in images),
        original_images=images, patch_id=CANARY_ID, target_symbol=AP, segment_index=1,
        virtual_address="0x0040b953", segment_offset=2387, changed_decoded_bytes=1,
        before_byte_hex="65", after_byte_hex="45", segment_bytes=8500,
        before_sgmt=dict(bytes=251681, sha256=BEFORE_SGMT),
        after_sgmt=dict(bytes=len(result), sha256=sha256(result)),
        before_segment_sha256=BEFORE_SEGMENT, after_segment_sha256=AFTER_SEGMENT,
        entry_point="0x00983c00", done_address=0, binary_payload_exported=False,
        source_bindings=bindings,
    )


GATE = """#!/bin/sh
# INERT OFFLINE REFERENCE. No argument or environment variable enables this file.
printf '%s\\n' 'BLOCKED: no qualified API5 canary, board/build or runtime observers' >&2
exit 78
# Everything below is UNREACHABLE transaction reference, NOT an operational loader.
set -uf
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
LC_ALL=C
export LC_ALL
umask 077
# Observers include bounded command execution, tmpfs/no-swap, mount/PID ownership,
# boot/mount-namespace identity, single-device module scope and stock runtime health.
# UNIMPLEMENTED: a later independently reviewed runtime must supply real evidence.
observe() { return 78; }
observe qualified_board_api5_build_and_observers || exit 78
STOCK_API5_SHA256=UNQUALIFIED
CANARY_API5_SHA256=UNQUALIFIED
"""


def render_scripts(watchdog_seconds=30):
    _require(type(watchdog_seconds) is int and 10 <= watchdog_seconds <= 60,
             "Watchdog seconds must be an integer from 10 to 60")
    # Fixed paths/commands only. No user shell text or module/options interpolation.
    main = GATE + f"""
observe root_tools_timeout_flock_and_memory || exit 78
observe all_tmp_roots_tmpfs_no_swap_no_symlinks || exit 78
observe no_existing_target_overlay_and_stock_module_baseline || exit 78
# Exclusive creation; never adopt or delete another run's state.
mkdir -m 700 {CONTROL} || exit 78
exec 9>{CONTROL}/lock
flock -n 9 || exit 78
mkdir -m 700 /tmp/fw_canary || exit 78
observe capture_stock_boot_config_namespace_inode_baseline || exit 78
{COPY_COMMAND} || exit 1
observe sha256_matches {RAM_FILE} "$STOCK_API5_SHA256" || exit 1
observe qualified_api5_pair_and_embedded_sgmt_before_after_hashes || exit 78
observe regular_owned_staging_hash {STAGING} "$CANARY_API5_SHA256" || exit 78
cp {STAGING} {RAM_FILE} || exit 1
observe sha256_matches {RAM_FILE} "$CANARY_API5_SHA256" || exit 1
observe install_canonical_guard_scripts_in_owned_control_tmpfs || exit 78
nohup /bin/sh {CONTROL}/watchdog.sh </dev/null >{CONTROL}/watchdog.log 2>&1 &
observe independent_guard_pid_birth_argv_and_READY "$!" || exit 1
finish() {{
    canary_rc=$?
    /bin/sh {CONTROL}/rollback.sh
    rollback_rc=$?
    observe retain_both_exit_codes "$canary_rc" "$rollback_rc"
    if [ "$rollback_rc" -ne 0 ]; then exit 1; fi
    exit "$canary_rc"
}}
trap finish EXIT
trap 'exit 1' HUP INT TERM
observe guard_alive_and_deadline_with_rollback_reserve || exit 1
observe journal_pending_bind_source_inode_and_parent_mount || exit 1
{BIND_COMMAND} || exit 1
observe capture_and_verify_owned_bind_id_source_inode_namespace || exit 1
observe journal_module_touched_and_validate_single_leaf_driver || exit 1
timeout 5 rmmod ath10k_pci || exit 1
timeout 5 modprobe ath10k_pci || exit 1
observe bounded_canary_semantic_readback_and_health || exit 1
exit 0
"""
    watchdog = GATE + f"""
trap '' HUP
observe validate_control_root_and_canonical_rollback_hash || exit 78
observe record_own_pid_birth_argv_and_monotonic_start || exit 78
observe publish_READY_in_owned_tmpfs || exit 78
# Separate process survives caller/session loss. No caller-PID kill is needed.
sleep {watchdog_seconds}
/bin/sh {CONTROL}/rollback.sh
rollback_rc=$?
observe record_guard_ENDED_and_rollback_rc "$rollback_rc"
exit "$rollback_rc"
"""
    rollback = GATE + f"""
observe same_boot_mount_namespace_and_owned_control || exit 78
exec 8>{CONTROL}/cleanup.lock
flock -w 5 8 || exit 1
# Idempotence must be established by the baseline, not an untrusted DONE flag.
observe journal_pending_recovery_and_top_bind_id_source_inode || exit 1
timeout 5 umount {TARGET} || exit 1
observe sha256_matches {TARGET} "$STOCK_API5_SHA256" || exit 1
# Unmount restores file lookup, not firmware already running in device SRAM.
observe baseline_loaded_and_module_was_touched_single_device_scope || exit 1
timeout 5 rmmod ath10k_pci || exit 1
timeout 5 modprobe ath10k_pci || exit 1
observe exact_stock_firmware_ready_interfaces_config_boot_health || exit 1
observe publish_RESTORED_only_with_complete_evidence || exit 1
# Guard disarms only after proving RESTORED; keep RAM receipts on any failure.
observe signal_guard_disarm_after_RESTORED_with_identity || exit 1
exit 0
"""
    return dict(main=main, watchdog=watchdog, rollback=rollback)


def validate_scripts(scripts, watchdog_seconds=30):
    expected = render_scripts(watchdog_seconds)
    _require(type(scripts) is dict and scripts.keys() == expected.keys(), "Unexpected shell inventory")
    for name, text in scripts.items():
        _require(type(text) is str and text == expected[name],
                 f"Noncanonical/forbidden shell program: {name}")
        # Defense in depth; exact template equality also rejects encoded command
        # construction, substitutions, arbitrary sh -c and appended flash actions.
        forbidden = r"(?m)^\s*(?:\S*/)?(?:mtd(?:_write)?|sysupgrade|dd|flashcp|flash_erase|nandwrite|ubiformat|fw_setenv)(?:\s|$)|/dev/(?:mtd|mmcblk|sd[a-z])"
        _require(not re.search(forbidden, text), "Flash command/device path forbidden")
    return True


def build_plan(watchdog_seconds=30):
    scripts = render_scripts(watchdog_seconds)
    validate_scripts(scripts, watchdog_seconds)
    evidence = verify_canary()
    return dict(
        schema_version=1, task_id=TASK_ID, generated_for_date="2026-10-25",
        mode="STRICTLY_OFFLINE_METADATA_AND_INERT_SCRIPT_GENERATION",
        status="OFFLINE_PLAN_VALIDATED_PHYSICAL_EXECUTION_BLOCKED",
        automatic_execution_allowed=False, physical_acceptance=False, scripts_inert=True,
        runtime_rollback_implemented=False, runtime_observers="UNIMPLEMENTED_BLOCKED",
        filesystem_ram_only_policy_validated=True, runtime_ram_only_verified=False,
        flash_writes_permitted=False, payload_export_permitted=False,
        canary_evidence=evidence,
        loader=dict(
            compatibility_verified=False, held_format="vendor SGMT embedded in umac.ko for kernel 2.6.32.68",
            requested_format="ath10k API5 QCA-ATH10K\\0 container with aligned IEs",
            raw_sgmt_is_api5=False, wrapper_alone_proves_abi=False,
            stock_api5_sha256=None, canary_api5_sha256=None,
            stock_api5_bytes=None, canary_api5_bytes=None,
            qualified_board_build_module=None, semantic_canary_readback=None,
            reason="SGMT magic differs from API5; exact firmware/build/ABI join is missing",
            source_anchors=[f"{HW}:138-181", f"{CORE}:2381-2438", f"{CORE}:2484-2528"],
        ),
        filesystem=dict(
            original_read_only=TARGET, ram_copy=RAM_FILE, qualified_candidate_staging=STAGING,
            guard_and_journal_root=CONTROL, original_copy_command=COPY_COMMAND,
            bind_command=BIND_COMMAND, underlying_stock_file_written=False,
            allowed_write_roots=["/tmp/fw_canary", "/tmp/fw_canary_control"],
            required_before_writes=[
                "all roots and candidate staging are verified tmpfs; /tmp name alone is insufficient",
                "no active swap; never run swapoff or change global configuration",
                "root-owned parents; no symlinks; fresh exclusive private roots; no state adoption",
                "bounded free memory and staging sizes; missing memory fields block",
                "no existing target overlay; regular stock and candidate files pinned by size/hash",
            ],
        ),
        watchdog=dict(
            deadline_seconds=watchdog_seconds, rollback_reserve_seconds=10,
            armed=False, independent_process_required=True, caller_session_survival_verified=False,
            reference_launch=f"nohup /bin/sh {CONTROL}/watchdog.sh </dev/null >{CONTROL}/watchdog.log 2>&1 &",
            command_timeout_seconds=5,
        ),
        rollback=dict(
            verified=False, idempotence_implemented=False,
            reference_commands=[f"umount {TARGET}", "rmmod ath10k_pci", "modprobe ath10k_pci"],
            ownership_required=["boot ID and mount namespace", "pending intent before bind",
                                "exact top mount ID, parent, source tmpfs identity and source inode",
                                "PID start time and exact argv for any guard signaling",
                                "exclusive cleanup lock; no foreign/new mount adoption"],
            acceptance=["owned bind removed; exact stock file size/hash visible",
                        "initial module loaded state and fixed options restored",
                        "stock firmware ready, interfaces, config, boot identity and health match baseline",
                        "canary and rollback exit codes retained; any missing proof is restoration incomplete"],
            limits=["unmount alone does not replace firmware in SRAM",
                    "no operational observers or exact stock build baseline exist in this deliverable",
                    "userspace guard cannot guarantee recovery from kernel hang, power loss or memory collapse",
                    "power-cycle/recovery remains a separately qualified physical prerequisite"],
        ),
        prohibitions=["mtd", "mtd_write", "sysupgrade", "dd", "flashcp", "flash_erase",
                      "nandwrite", "ubiformat", "fw_setenv", "persistent firmware/config/partition writes",
                      "SSH/network/device execution", "force/lazy/global unmount", "forced module removal"],
        script_validation="exact canonical program bytes; no free-form shell or enabling flag",
        scripts=scripts, script_sha256={name: sha256(text.encode()) for name, text in scripts.items()},
        surrogate=dict(new_physical_observations=0, training_or_performance_claims_added=False,
                       files_updated=[], ready_cells_added=0),
        missing_evidence=["exact qualified original/canary API5 pair and embedded SGMT provenance",
                          "authorized isolated board, driver/build/ABI and single-device scope",
                          "implemented and independently tested runtime ownership, deadline and health observers",
                          "proven recovery and qualified semantic canary readback"],
        decision="KEEP_OFFLINE_PREPARER; BLOCK_PHYSICAL_EXECUTION",
    )


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def validate_plan(plan):
    _require(type(plan) is dict, "Plan object required")
    seconds = plan.get("watchdog", {}).get("deadline_seconds")
    expected = build_plan(seconds)
    validate_scripts(plan.get("scripts"), seconds)
    # Compare every nested safety/readiness/evidence field, preserving JSON types
    # (False is not accepted as integer 0). Unknown fields also fail closed.
    _require(_canonical(plan) == _canonical(expected), "Plan differs from freshly verified canonical evidence")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", type=str, help="Validate an existing local JSON plan; no actuation")
    args = parser.parse_args(argv)
    if args.validate:
        validate_plan(load_json(read_local(args.validate)))
        print("PASS: canonical offline plan; physical execution BLOCKED")
    else:
        plan = build_plan()
        output = local_path(ROOT / OUTPUT)
        _require(output.parent.is_dir(), "Existing local artifact directory required")
        output.write_text(json.dumps(plan, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(f"WROTE {OUTPUT}; physical execution BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
