#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Offline, data-only board preflight. Never executes pasted text or target commands."""
from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import struct
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RELEASE = ROOT / "firmware/openwrt/pbe5ac_gen2_ptp_kit/public_release_v5"
DEFAULT_RECEIPT = ROOT / "artifacts/autoresearch/stage231a_public_wa_4board_release_v5_receipt.json"
# Deliberately unset until the actual Stage231 build freezes. A user-supplied
# manifest/receipt can never establish its own trusted identity.
V5_MANIFEST_SHA256 = "UNSET"
V5_RECEIPT_SHA256 = "UNSET"
MAX_INPUT = 65536
MAX_LINE = 2048
MAX_FILE = 32 * 1024 * 1024
MAX_RELEASE = 192 * 1024 * 1024
END_SENTINEL = b"END_BOARD_INFO"
MODULE_SHA256 = "fe4f730fccaa68848a70c952e40c0438b32d413993f22887a0e72fed5eebaae6"

BOARDS = {
    "pbe5ac-gen2": {"model": "PowerBeam 5AC Gen2", "profile": "ubnt,powerbeam-5ac-gen2",
        "sysids": ["0xe3d6"], "aliases": ["PowerBeam 5AC Gen2", "PowerBeam AC Gen2", "PBE-5AC-Gen2"],
        "dtb": "03d8236f5fbf665db1596b904dbc1aeb61a97908d5d08477883dfd5d336d812b",
        "kernel_prefix": "6a12e4fba07b8b462ac7514fe0d95da709fcb9b586a03ee24905f0549a554083",
        "stock": {"factory": "52d25c7f17ffc69dedc66895af090630e913945ac34fcb87288a4c381021f174", "sysupgrade": "c3e17ac02259db08708dfa8250e1b06d7765487923bdd435dc5d52998da301a4"}},
    "lbe5ac-gen2": {"model": "LiteBeam 5AC Gen2", "profile": "ubnt,litebeam-ac-gen2",
        "sysids": ["0xe7f9"], "aliases": ["LiteBeam 5AC Gen2", "LiteBeam AC Gen2", "LBE-5AC-Gen2"],
        "dtb": "13dc1329eedece4ed840d7a0caa1d3bbf261cdda110e6cad2a03fb8cf2905f26",
        "kernel_prefix": "af1e50327bf66506bfdd740f6c3b561cfabf84524099a0ee888fc5f34dbe02b3",
        "stock": {"factory": "dafd701bc80f544fde9368061c86487bc48499d4cc79ec80dbf1a5bbdc33c034", "sysupgrade": "9c014e35de84d663f20e82371165b9f57c37a3b590fe921a9b30cff79b6a549c"}},
    "lap-120": {"model": "LiteAP ac LAP-120", "profile": "ubnt,lap-120",
        "sysids": ["0xe7f5", "0xe8e5"], "aliases": ["LAP-120", "LiteAP ac LAP-120", "LiteAP ac (LAP-120)"],
        "dtb": "ac2240514ca30717ea81cdae2860dd93b5d3a9240722a4a9ce8b4a14be19387e",
        "kernel_prefix": "b9e52ae22af377265b8bafc197afce9fe492c534a73ba012faf90f234aad1eec",
        "stock": {"factory": "943d812c40e8f1e6bfb71b32b12395fdd480b62318bc537c7687f8affa9378c0", "sysupgrade": "cc01cbb3e441c8bb801bbae8b64ea6352e571dee0ef6204d95c6bd80e2a975f1"}},
    "nanostation-ac-loco": {"model": "NanoStation 5AC Loco", "profile": "ubnt,nanostation-ac-loco",
        "sysids": ["0xe7f7", "0xe7fa"], "aliases": ["NanoStation 5AC Loco", "NanoStation AC Loco", "Loco5AC", "NS-5ACL"],
        "dtb": "8ac4ab47a0cabd7a7cee5f9a3046cee205dbb3311f8b9c820e0c4cd87fbcdfa8",
        "kernel_prefix": "d38f731b6ef27073b73f27f278c24acdde96e85744ae9c03692e171d58328ca6",
        "stock": {"factory": "a7bb8db87083e04695d757ed6adc5aae481438f4191316c2eb90045f191f6443", "sysupgrade": "390ae90a2d09b0cba27e3853b14a16e739e5e3610d1e2451116d73470106892e"}},
}
IDENTITY_KEYS = {"board.name", "board.model", "board.shortname", "board_name", "model", "machine model", "hardware name"}
FAMILY_KEYS = {"board.family", "board.platform", "firmware.version", "firmware", "version"}
CHIP_KEYS = {"board.soc", "board.radio", "soc", "cpu model", "radio"}
KNOWN_KEYS = IDENTITY_KEYS | FAMILY_KEYS | CHIP_KEYS | {"board.sysid", "sysid"}


class PreflightError(ValueError):
    """A bounded, non-sensitive error code; never include raw submitted text."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def local_path(path):
    text = os.fspath(path)
    win = PureWindowsPath(text)
    if text.replace("\\", "/").startswith("//") or "://" in text or (win.drive and not win.root):
        raise PreflightError("LOCAL_PATH_REQUIRED")
    if ".." in win.parts:
        raise PreflightError("TRAVERSAL_FORBIDDEN")
    devices = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    for part in win.parts[1:] if win.anchor else win.parts:
        if ":" in part or part.endswith((".", " ")) or part.rstrip(". ").split(".")[0].upper() in devices:
            raise PreflightError("DEVICE_OR_STREAM_PATH_FORBIDDEN")
    result = Path(os.path.abspath(text))
    cursor = Path(result.anchor)
    for part in result.parts[1:]:
        cursor /= part
        try:
            info = cursor.lstat()
        except FileNotFoundError:
            break
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise PreflightError("SYMLINK_OR_REPARSE_FORBIDDEN")
    return result


def read_bytes(path, limit=MAX_FILE):
    path = local_path(path)
    if not stat.S_ISREG(path.stat().st_mode):
        raise PreflightError("REGULAR_FILE_REQUIRED")
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        raise PreflightError("FILE_SIZE_LIMIT")
    return data


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise PreflightError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    try:
        value = json.loads(data.decode("utf-8-sig"), object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(PreflightError("FINITE_JSON_REQUIRED")))
        json.dumps(value, allow_nan=False)
    except (UnicodeError, ValueError, OverflowError) as error:
        raise PreflightError("STRICT_JSON_REQUIRED") from error
    if not isinstance(value, dict):
        raise PreflightError("JSON_OBJECT_REQUIRED")
    return value


def _normal(value):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"^(?:ubiquiti|ubnt)\s+", "", value.lower()))


def parse_identity(data):
    """Extract only canonical allowlisted identity facts; discard all raw lines."""
    if not isinstance(data, bytes) or not data or len(data) > MAX_INPUT:
        raise PreflightError("INPUT_SIZE_LIMIT")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeError as error:
        raise PreflightError("UTF8_REQUIRED") from error
    if any(ord(c) < 32 and c not in "\r\n\t" for c in text) or "\x7f" in text:
        raise PreflightError("CONTROL_CHARACTER_FORBIDDEN")
    lines = text.splitlines()
    if len(lines) > 1024 or any(len(line.encode("utf-8")) > MAX_LINE for line in lines):
        raise PreflightError("LINE_SIZE_LIMIT")
    values, seen, ignored = [], set(), 0
    for line in lines:
        line = re.sub(r"^\s*\[\s*[0-9.]+\]\s*", "", line.strip())
        dmesg_model = re.fullmatch(r"(?:(?:MIPS:\s*)?machine is\s+|(?:OF:\s*fdt:\s*)?Machine model:\s*)(.{1,256})", line, re.I)
        if dmesg_model:
            line = "machine model=" + dmesg_model[1]
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_. -]{0,63})\s*[=:]\s*(.{1,256})", line)
        if not match or match[1].strip().lower() not in KNOWN_KEYS:
            ignored += 1
            continue
        key, value = match[1].strip().lower(), match[2].strip()
        if key in seen:
            raise PreflightError("DUPLICATE_IDENTITY_FIELD")
        seen.add(key)
        values.append((key, value))
    boards, families, sysids, chips, systems = set(), set(), set(), set(), set()
    unknown_model = False
    for key, value in values:
        if key in IDENTITY_KEYS:
            found = [board for board, spec in BOARDS.items()
                     if _normal(value) in {_normal(x) for x in [spec["profile"], board, *spec["aliases"]]}]
            boards.update(found)
            if not found:
                unknown_model = True
                label = _normal(value)
                if any(x in label for x in ("ltu", "airfiber")):
                    families.add("LTU")
                elif any(x in label for x in ("rocketprism", "prismstation", "powerbeam5ac500", "powerbeam5ac620", "rocket5aclite", "isostation")):
                    families.add("XC")
        elif key in {"board.sysid", "sysid"}:
            if not re.fullmatch(r"(?:0x)?[0-9a-f]{4}", value, re.I):
                raise PreflightError("SYSID_FORMAT")
            sysids.add("0x" + value.lower().removeprefix("0x"))
        elif key in FAMILY_KEYS:
            family = re.fullmatch(r"(WA|XC|XW|XM|LTU)(?:[. _-]v?[0-9][A-Za-z0-9._-]{0,80})?", value, re.I)
            if family:
                families.add(family[1].upper())
            if re.fullmatch(r"OpenWrt(?:\s+[0-9][A-Za-z0-9._-]{0,60})?", value, re.I):
                systems.add("OpenWrt")
            elif family:
                systems.add("airOS" if family[1].upper() != "LTU" else "LTU")
        elif key in CHIP_KEYS:
            chips.update(x.upper() for x in re.findall(r"\b(?:AR[0-9]{4}|QCA[0-9]{4})\b", value, re.I))
    if "QCA9558" in chips:
        families.add("XC")
    return {"model_candidates": sorted(boards), "firmware_families": sorted(families),
            "operating_systems": sorted(systems), "sysids": sorted(sysids), "observed_chips": sorted(chips),
            "unrecognized_model_field": unknown_model, "ignored_line_count": ignored,
            "input_is_untrusted_assertion": True, "physical_identity_verified": False}


def resolve_identity(parsed):
    reasons = []
    candidates = parsed["model_candidates"]
    families, ids, chips = set(parsed["firmware_families"]), parsed["sysids"], set(parsed["observed_chips"])
    if len(candidates) != 1:
        reasons.append("EXACT_MODEL_REQUIRED" if not candidates else "CONFLICTING_MODELS")
    if parsed["unrecognized_model_field"]:
        reasons.append("UNRECOGNIZED_MODEL_FIELD")
    if len(families) > 1:
        reasons.append("CONFLICTING_FIRMWARE_FAMILIES")
    if len(parsed["operating_systems"]) > 1:
        reasons.append("CONFLICTING_OPERATING_SYSTEMS")
    if len(ids) > 1:
        reasons.append("CONFLICTING_SYSIDS")
    board = candidates[0] if len(candidates) == 1 else None
    spec = BOARDS.get(board)
    if spec:
        if families - {"WA"}:
            reasons.append("MODEL_FIRMWARE_FAMILY_CONFLICT")
        if ids and any(value not in spec["sysids"] for value in ids):
            reasons.append("MODEL_SYSID_CONFLICT")
        if chips - {"AR9340", "AR9341", "AR9342", "AR9344", "QCA9880", "QCA9882"}:
            reasons.append("MODEL_CHIP_FAMILY_CONFLICT")
    elif ids:
        reasons.append("SYSID_ALONE_IS_AMBIGUOUS_INCLUDING_XC_COLLISIONS")
    return {"status": "IDENTIFIED_FOR_INSPECTION" if not reasons else "BLOCKED", "reason_codes": reasons,
            "board": board if not reasons else None, "model": spec["model"] if spec else None,
            "profile": spec["profile"] if spec and not reasons else None,
            "firmware_family_observed": next(iter(families)) if len(families) == 1 else "UNKNOWN",
            "catalog_family": "WA" if spec else "UNKNOWN", "observed": parsed,
            "expected_chip_family": {"soc": "AR934x", "radio": "QCA988x", "basis": "CATALOG_FAMILY_NOT_A_CHIP_READBACK"} if spec else None,
            "diagnostic_only_families": sorted(families - {"WA"}),
            "physical_identity_verified": False, "flash_approved": False}


def _sysupgrade(data, spec):
    end, blocks = len(data), []
    for kind in (0, 1):
        if end < 16:
            raise PreflightError("FWX0_TRUNCATED")
        magic, crc, actual, pad, size = struct.unpack_from(">4sIB3sI", data, end - 16)
        if magic != b"FWx0" or actual != kind or pad != b"\0" * 3 or not 16 <= size <= end:
            raise PreflightError("FWX0_HEADER")
        if (zlib.crc32(data[:end - 16]) ^ 0xffffffff) & 0xffffffff != crc:
            raise PreflightError("FWX0_CRC")
        blocks.append(data[end - size:end - 16])
        end -= size
    if blocks[0] != b"# fake certificate" or blocks[1][:8] != b"\0" * 8:
        raise PreflightError("FWX0_METADATA_WRAPPER")
    metadata = strict_json(blocks[1][8:])
    version, release = metadata.get("version"), metadata.get("openmax")
    if not isinstance(version, dict) or not isinstance(release, dict):
        raise PreflightError("IMAGE_METADATA_SCHEMA")
    if metadata.get("supported_devices") != [spec["profile"]] or version.get("target") != "ath79/generic" or version.get("version") != "24.10.4" or release.get("release") != "public-v5":
        raise PreflightError("IMAGE_BOARD_OR_VERSION_MISMATCH")
    payload = data[:end]
    if payload[-4:] != b"\xde\xad\xc0\xde" or (len(payload) - 4) % 65536 or len(payload) > 0xf30000:
        raise PreflightError("IMAGE_SIZE_OR_PADDING")
    return payload


def _factory(data):
    if len(data) < 268 or data[:4] != b"OPEN" or zlib.crc32(data[:260]) & 0xffffffff != struct.unpack_from(">I", data, 260)[0] or data[264:268] != b"\0" * 4:
        raise PreflightError("FACTORY_HEADER_CRC")
    pos, parts = 268, []
    for name, cap in ((b"kernel", 0x100000), (b"rootfs", 0xe60000)):
        header = data[pos:pos + 56]
        if len(header) != 56 or header[:4] != b"PART" or header[4:20].rstrip(b"\0") != name:
            raise PreflightError("FACTORY_PARTITION")
        size, capacity = struct.unpack_from(">II", header, 48)
        end = pos + 56 + size
        if not 0 < size <= capacity == cap or end + 8 > len(data):
            raise PreflightError("FACTORY_PARTITION_SIZE")
        if zlib.crc32(data[pos:end]) & 0xffffffff != struct.unpack_from(">I", data, end)[0] or data[end + 4:end + 8] != b"\0" * 4:
            raise PreflightError("FACTORY_PARTITION_CRC")
        parts.append(data[pos + 56:end])
        pos = end + 8
    if data[pos:] != b"ENDS" + b"\0" * 260:
        raise PreflightError("FACTORY_SUFFIX")
    return b"".join(parts)


def _kernel(payload, spec):
    if len(payload) < 0x280000 + 96 or sha256(payload[:0x280000]) != spec["kernel_prefix"]:
        raise PreflightError("OFFICIAL_BOARD_KERNEL_PREFIX_MISMATCH")
    header = bytearray(payload[:64])
    magic, crc = struct.unpack_from(">II", header)
    header[4:8] = b"\0" * 4
    size = struct.unpack_from(">I", payload, 12)[0]
    if magic != 0x27051956 or zlib.crc32(header) & 0xffffffff != crc or size > 0x280000 - 64:
        raise PreflightError("KERNEL_UIMAGE_HEADER")
    compressed = payload[64:64 + size]
    if zlib.crc32(compressed) & 0xffffffff != struct.unpack_from(">I", payload, 24)[0]:
        raise PreflightError("KERNEL_DATA_CRC")
    try:
        decoder = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
        raw = decoder.decompress(compressed, max_length=32 * 1024 * 1024)
    except lzma.LZMAError as error:
        raise PreflightError("KERNEL_COMPRESSION") from error
    if not decoder.eof:
        raise PreflightError("KERNEL_DECOMPRESSION_LIMIT")
    offset = raw.rfind(b"\xd0\x0d\xfe\xed")
    if offset < 0 or offset + 40 > len(raw):
        raise PreflightError("DTB_MISSING")
    size = struct.unpack_from(">I", raw, offset + 4)[0]
    dtb = raw[offset:offset + size]
    if size < 40 or len(dtb) != size or sha256(dtb) != spec["dtb"] or spec["profile"].encode() + b"\0" not in dtb:
        raise PreflightError("OFFICIAL_BOARD_DTB_MISMATCH")
    rootfs = payload[0x280000:]
    used = struct.unpack_from("<Q", rootfs, 40)[0]
    if rootfs[:4] != b"hsqs" or struct.unpack_from("<HH", rootfs, 28) != (4, 0) or struct.unpack_from("<H", rootfs, 20)[0] != 4 or not 96 <= used <= len(rootfs):
        raise PreflightError("ROOTFS_FORMAT")
    return sha256(rootfs[:used])


def validate_release(release_dir=DEFAULT_RELEASE, receipt_path=DEFAULT_RECEIPT):
    """Validate every local byte against fixed anchors, then each board container."""
    if not all(re.fullmatch(r"[0-9a-f]{64}", value) for value in (V5_MANIFEST_SHA256, V5_RECEIPT_SHA256)):
        raise PreflightError("V5_TRUST_ANCHOR_NOT_FROZEN")
    release_dir = local_path(release_dir)
    manifest = read_bytes(release_dir / "SHA256SUMS", 128 * 1024)
    receipt_raw = read_bytes(receipt_path, 2 * 1024 * 1024)
    if sha256(manifest) != V5_MANIFEST_SHA256 or sha256(receipt_raw) != V5_RECEIPT_SHA256:
        raise PreflightError("V5_TRUST_ANCHOR_MISMATCH")
    receipt = strict_json(receipt_raw)
    if type(receipt.get("schema_version")) is not int or receipt["schema_version"] != 1 or receipt.get("version") != 5 or not isinstance(receipt.get("outputs"), dict) or not isinstance(receipt.get("boards"), dict):
        raise PreflightError("V5_RECEIPT_SCHEMA")
    try:
        lines = manifest.decode("ascii").splitlines()
    except UnicodeError as error:
        raise PreflightError("MANIFEST_ASCII_REQUIRED") from error
    files, total = {}, 0
    if not 8 <= len(lines) <= 256:
        raise PreflightError("MANIFEST_COUNT")
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  (.{1,200})", line)
        if not match:
            raise PreflightError("MANIFEST_LINE")
        digest, name = match.groups()
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name or PureWindowsPath(name).drive or name in files or path.as_posix() != name or name == "SHA256SUMS":
            raise PreflightError("MANIFEST_UNSAFE_OR_DUPLICATE_PATH")
        member = local_path(release_dir / name)
        if not member.is_relative_to(release_dir):
            raise PreflightError("MANIFEST_PATH_OUTSIDE_RELEASE")
        data = read_bytes(member)
        if sha256(data) != digest:
            raise PreflightError("RELEASE_PAYLOAD_HASH_MISMATCH")
        total += len(data)
        if total > MAX_RELEASE:
            raise PreflightError("RELEASE_SIZE_LIMIT")
        files[name] = data
    actual, pending, entries_seen = set(), [release_dir], 0
    while pending:
        parent = pending.pop()
        with os.scandir(parent) as entries:
            for entry in entries:
                entries_seen += 1
                if entries_seen > 1024:
                    raise PreflightError("RELEASE_DIRECTORY_ENTRY_LIMIT")
                p = local_path(entry.path)
                if p.is_file():
                    actual.add(p.relative_to(release_dir).as_posix())
                elif p.is_dir():
                    pending.append(p)
                else:
                    raise PreflightError("NONREGULAR_RELEASE_MEMBER")
    if actual != set(files) | {"SHA256SUMS"} or set(receipt["outputs"]) != set(files):
        raise PreflightError("RELEASE_INVENTORY_MISMATCH")
    if set(receipt["boards"]) != set(BOARDS):
        raise PreflightError("RELEASE_BOARD_INVENTORY")
    for name, data in files.items():
        pin = receipt["outputs"][name]
        if not isinstance(pin, dict) or pin.get("sha256") != sha256(data) or type(pin.get("size_bytes")) is not int or pin["size_bytes"] != len(data):
            raise PreflightError("RECEIPT_OUTPUT_BINDING")
    image_info = {}
    for board, spec in BOARDS.items():
        details = receipt["boards"][board]
        if not isinstance(details, dict) or details.get("profile") != spec["profile"] or details.get("input_sha256") != spec["stock"]:
            raise PreflightError("OFFICIAL_SOURCE_PROVENANCE_MISMATCH")
        module = details.get("module")
        if not isinstance(module, dict) or module.get("sha256") != MODULE_SHA256:
            raise PreflightError("EXPECTED_MODULE_ABI_PROVENANCE_MISMATCH")
        pair = {}
        for kind in ("factory", "sysupgrade"):
            name = f"openwrt-24.10.4-ubnt-{board}-openmax-public-{kind}.bin"
            if name not in files:
                raise PreflightError("EXPECTED_IMAGE_MISSING")
            data = files[name]
            pair[kind] = {"filename": name, "bytes": len(data), "sha256": sha256(data), "md5": hashlib.md5(data).hexdigest()}
        sys_payload = _sysupgrade(files[pair["sysupgrade"]["filename"]], spec)
        if _factory(files[pair["factory"]["filename"]]) != sys_payload:
            raise PreflightError("FACTORY_SYSUPGRADE_PAYLOAD_MISMATCH")
        rootfs_hash = _kernel(sys_payload, spec)
        if details.get("emitted_rootfs_sha256") != rootfs_hash:
            raise PreflightError("ROOTFS_RECEIPT_BINDING")
        image_info[board] = pair
    return {"status": "VERIFIED_LOCAL_RELEASE_BYTES", "manifest_sha256": V5_MANIFEST_SHA256,
            "receipt_sha256": V5_RECEIPT_SHA256, "file_count": len(files) + 1,
            "image_count": 8, "images": image_info, "physical_compatibility_verified": False,
            "gpg_or_publisher_authentication_established": False,
            "md5_purpose": "BYTE_IDENTIFICATION_ONLY_SHA256_IS_THE_INTEGRITY_CHECK"}


def preflight(data, release_dir=DEFAULT_RELEASE, receipt_path=DEFAULT_RECEIPT, *, ota=False):
    identity = resolve_identity(parse_identity(data))
    reasons = list(identity["reason_codes"])
    try:
        release = validate_release(release_dir, receipt_path)
    except (PreflightError, OSError):
        # Keep diagnostics bounded; no exception path or arbitrary input is echoed.
        release = {"status": "BLOCKED", "reason_code": "RELEASE_NOT_VERIFIED"}
        reasons.append("RELEASE_NOT_VERIFIED")
    if ota:
        reasons.append("WIRED_FIRST_IMAGE_HAS_NO_PROVISIONED_OTA_MIGRATION_OR_WATCHDOG")
    board = identity["board"]
    images = release.get("images", {}).get(board, {}) if board else {}
    commands = ["cat /etc/board.info", "cat /tmp/sysinfo/board_name", "cat /etc/openwrt_release", "uname -r"]
    if images:
        # Names are fixed catalog strings; no submitted value enters shell text.
        name = images["sysupgrade"]["filename"]
        commands += ["sha256sum -c SHA256SUMS", f"md5sum {name}", f"sysupgrade -T ./{name}"]
    return {"schema_version": 1, "stage": "232A", "status": "BLOCKED" if reasons else "READY_FOR_WIRED_INSPECTION",
            "reason_codes": reasons, "identity": identity, "release": {k: v for k, v in release.items() if k != "images"},
            "candidate_files": images, "inspection_commands_not_executed": commands,
            "command_context": "Inspection only on an already booted tester-owned unit; sysupgrade -T is OpenWrt image test only, not an airOS command or physical acceptance.",
            "flash_step": {"status": "BLOCKED", "command": None, "reason": "Exact physical revision, supported recovery and installation path require separate validation; pasted identity never grants it."},
            "ota_plan": {"status": "BLOCKED", "command": None,
                         "reason": "Public v5 starts wired-first with Wi-Fi disabled and has no provisioned OTA migration image/watchdog.",
                         "conditional_sequence": "If the remote STA remains stock airOS PtP, keep a compatible airOS PtP AP while converting the remote STA first, or apply PtP=0 using the supported path and verify reassociation plus L2/L3 data before an OpenWrt AP. A config key alone is not a loaded-state getter.",
                         "reference": "artifacts/autoresearch/stage138a_ptp_sta_data_gate_verdict.json",
                         "evidence_scope": "Static held WA8.7.25 sequence guard, not universal or physical acceptance."},
            "execution": {"pasted_text_executed": False, "network_or_device_contact": False, "flash_executed": False},
            "physical_acceptance": "UNKNOWN", "E2": "NOT_ACCEPTED"}


def write_output(path, report, *, input_path=None, release_dir=DEFAULT_RELEASE, receipt_path=DEFAULT_RECEIPT):
    target, release = local_path(path), local_path(release_dir)
    protected = {local_path(__file__), local_path(receipt_path), local_path(DEFAULT_RECEIPT)}
    if input_path is not None:
        protected.add(local_path(input_path))
    if target in protected or target.is_relative_to(release) or target.is_relative_to(local_path(DEFAULT_RELEASE)) or target.exists():
        raise PreflightError("OUTPUT_COLLISION_OR_EXISTING_FILE")
    if not target.parent.is_dir():
        raise PreflightError("OUTPUT_PARENT_MUST_EXIST")
    payload = (json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
    fd, temp = tempfile.mkstemp(prefix=".stage232-", suffix=".tmp", dir=target.parent)
    temporary = Path(temp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        # Hard-link creation is atomic and refuses an output created meanwhile.
        os.link(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def _stdin_data(interactive):
    if not interactive:
        data = sys.stdin.buffer.read(MAX_INPUT + 1)
        if len(data) > MAX_INPUT:
            raise PreflightError("INPUT_SIZE_LIMIT")
        return data
    print("Paste board identity. Finish with END_BOARD_INFO on its own line.", file=sys.stderr)
    result = bytearray()
    for _ in range(1025):
        line = sys.stdin.buffer.readline(MAX_LINE + 2)
        if not line:
            raise PreflightError("INTERACTIVE_SENTINEL_REQUIRED")
        if line.rstrip(b"\r\n") == END_SENTINEL:
            return bytes(result)
        result.extend(line)
        if len(result) > MAX_INPUT:
            raise PreflightError("INPUT_SIZE_LIMIT")
    raise PreflightError("LINE_SIZE_LIMIT")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--input", type=Path)
    inputs.add_argument("--interactive", action="store_true")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE)
    parser.add_argument("--receipt-file", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--ota", action="store_true", help="Evaluate an OTA request; public wired-first images always block it")
    args = parser.parse_args(argv)
    try:
        data = read_bytes(args.input, MAX_INPUT) if args.input else _stdin_data(args.interactive)
        report = preflight(data, args.release_dir, args.receipt_file, ota=args.ota)
        if args.output:
            write_output(args.output, report, input_path=args.input, release_dir=args.release_dir, receipt_path=args.receipt_file)
        print(json.dumps(report, ensure_ascii=True, allow_nan=False))
        return 0 if report["status"] == "READY_FOR_WIRED_INSPECTION" else 1
    except (PreflightError, OSError, UnicodeError):
        print(json.dumps({"schema_version": 1, "stage": "232A", "status": "ERROR", "reason_code": "INVALID_INPUT_OR_LOCAL_IO", "flash_executed": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
