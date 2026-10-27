#!/usr/bin/env python3
"""Package offline XC/XW/XM diagnostic starters; never build or deploy firmware."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import sys
import tarfile
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "T-S171A-PUBLIC-XC-XW-XM-TESTER-KITS"
DEFAULT_OUTPUT = ROOT / "firmware/openwrt/public_xc_xw_tester_release"
DEFAULT_RECEIPT = ROOT / "artifacts/autoresearch/stage171a_public_xc_xw_tester_release_receipt.json"
EPOCH = 1761264000
MAX_INPUT_BYTES = 2 * 1024 * 1024
SOURCE_PINS = {
    "artifacts/autoresearch/stage158a_xw_xm_30board_openwrt_matrix.json": "c496ff8e71e9d24c29f8b1ab39339c5ddcd90b63127aabd6330b1f9c8991f117",
    "artifacts/autoresearch/stage159a_xc_airprism_hsr_and_passive_openwrt_kit.json": "3842b6e0969623aa29384f2688f4fe3e9d7ee871081164c70d4ad7a37b198e24",
    "artifacts/autoresearch/stage165a_xc_family_universal_kit.json": "32eb982953a62168a14ad93998f60ad2879ea1d574bdec15280950dfce149d48",
    "artifacts/autoresearch/stage166a_xw_xm_ath9k_universal_kit.json": "b97c71cdd74c57125b5659734aa18b9797e653fcee833b0f3681c86ff51620b5",
    "firmware/openwrt/xc_family_universal_kit/99-fmx-xc-universal-champion": "a66c7d0664fe7ea87989b4adaee14df1367fbb6714f97c306d4e667fbb7ed08e",
    "firmware/openwrt/xw_xm_family_universal_kit/99-fmx-xw-xm-ath9k-champion": "f1331274eab7e79b09a51d0407badc3343b09f3ef0b8294d0a1d82a315086e0c",
    "firmware/openwrt/xc_family_universal_kit/sysupgrade-overlay-xc-universal-v1.tar.gz": "e07fd4d7ffb57f5707d12f3c95b00afd6cdde28462628713edbaf4c7fff20e3c",
    "firmware/openwrt/xc_family_universal_kit/xc_board_manifest.json": "78c81c504618a4ec6ba40ffcdcf83985550693607530a452de62c34a0ab34ff6",
    "firmware/openwrt/xw_xm_family_universal_kit/xw_xm_board_manifest.json": "055fbe7ea8ddb3c1f9380332c6486561290a6abf2b00f02b7747534385ebe07a",
    "artifacts/verification/stage170_to_172_sources/profiles.json": "996f4dc8ef25477ec3a9a006b6eb1755918d4180f20da5073d5554185982f9b5",
    "artifacts/verification/stage170_to_172_sources/sha256sums": "0128f80d20e19a4b59bc30832e73e2a718f0e5121981cf1538b919822bf9ffed",
}
STAGES = {stage: next(name for name in SOURCE_PINS if f"stage{stage}a_" in name) for stage in (158, 159, 165, 166)}
OFFICIAL_PROFILES = "artifacts/verification/stage170_to_172_sources/profiles.json"
ARCHIVE_STEM = "openmax-xc-xw-xm-public-tester-kit"
XC_OVERLAY = "firmware/openwrt/xc_family_universal_kit/sysupgrade-overlay-xc-universal-v1.tar.gz"

COLLECTOR = r'''#!/bin/sh
# Manually run on an already booted tester-owned device. No writes or network.
LC_ALL=C
export LC_ALL
clean() { printf '%s' "$1" | tr -cd 'A-Za-z0-9_,.-' | cut -c1-96; }
board=UNKNOWN
if [ -f /tmp/sysinfo/board_name ]; then
 value=$(head -n1 /tmp/sysinfo/board_name)
 case "$value" in ubnt,*) board=$(clean "$value") ;; esac
fi
sysid=UNKNOWN
if [ -f /etc/board.info ]; then
 value=$(sed -n 's/^board.sysid=//p' /etc/board.info | head -n1)
 case "$value" in 0x[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]) sysid=$value ;; esac
fi
memory=$(awk '/^MemTotal:/{print $2; exit}' /proc/meminfo 2>/dev/null)
case "$memory" in ''|*[!0-9]*) memory=null ;; esac
kernel=$(clean "$(uname -r)")
arch=$(clean "$(uname -m)")
printf '{"schema_version":1,"scope":"READ_ONLY_IDENTITY_METADATA","identity_authenticated":false,'
printf '"board":"%s","sysid":"%s","kernel":"%s","architecture":"%s","mem_total_kib":%s,' "$board" "$sysid" "$kernel" "$arch" "$memory"
printf '"wireless_drivers":['
separator=
for path in /sys/class/ieee80211/phy*/device/driver; do
 [ -L "$path" ] || continue
 target=$(readlink "$path" 2>/dev/null)
 driver=${target##*/}
 case "$driver" in ath9k|ath10k_pci|ath10k_ahb) ;; *) driver=UNKNOWN ;; esac
 printf '%s"%s"' "$separator" "$driver"
 separator=,
done
printf '],"interfaces":['
separator=
count=0
for path in /sys/class/net/*; do
 [ -e "$path" ] || continue
 name=${path##*/}
 case "$name" in lo|eth[0-9]*|br-lan|wlan[0-9]*|ath[0-9]*|phy*-ap[0-9]*|phy*-sta[0-9]*) ;; *) continue ;; esac
 name=$(clean "$name")
 wireless=false
 [ ! -d "$path/wireless" ] || wireless=true
 printf '%s{"name":"%s","wireless_metadata_present":%s}' "$separator" "$name" "$wireless"
 separator=,
 count=$((count + 1))
 [ "$count" -lt 32 ] || break
done
printf '],"hardware_acceptance":false,"firmware_install_approved":false}\n'
'''.encode("ascii")

README = b'''# Public XC / XW / XM diagnostic starter

This is a tester kit, not firmware. No installation image, kernel module,
automatic startup hook, configuration, RF command or apply script is supplied.
It does not reproduce proprietary airMAX scheduling or qualify a migration.

1. Verify SHA256SUMS (SHA256SUMS.txt is the identical compatibility alias).
2. Read PROFILE_MATRIX.json. Reported sysids are historical claims, not unique
   board identifiers or an instruction to select a firmware image.
3. On an already booted, tester-owned radio, inspect collect_capabilities.sh.
   Optionally run it manually with sh and save its JSON output yourself.
   It reads board/kernel/RAM/driver/interface metadata only. It never connects
   to another device, reads IP/MAC/configuration credentials or changes knobs.
   Missing fields stay UNKNOWN/null; metadata does not authenticate hardware.
4. Compare the saved identity to the candidate JSON for the correct family.
   Exact model/revision, RAM, flash map, DTS/calibration layout, driver ABI,
   recovery and direct physical tests still need separate qualification.

Rocket Prism / PrismStation active filtering has unqualified GPIO/HSR support:
retain the existing stock airOS environment. PBE-620 and IsoStation have no
exact profile in the held OpenWrt 24.10.4 ath79/generic inventory. A PBE-500
profile is not permission to install it on PBE-620. NanoBeam variants differ.
32 MiB XM remains stock-airOS-only here; do not infer 24.10.4 safety from a
historical script. XW/XM sysids and RAM classifications conflict across sources.

All candidate tuning is disabled and unqualified. Historical numeric values
are configuration proposals, not measured safe defaults, gains, fairness,
capacity, loaded-latency or stability evidence. No WA mac80211 module is copied
to XC or ath9k. The older XC overlay that included one is explicitly excluded.

Original proprietary firmware/configuration is not redistributed. The new
collector and packager are GPL-2.0-or-later. Official inventory provenance is
HTTPS/hash based; GPG verification and exact-board hardware acceptance are absent.
'''


class PackageError(ValueError):
    """Invalid input, unsafe destination or unsupported public payload."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def safe_local(path):
    text = os.fspath(path)
    win = PureWindowsPath(text)
    if text.replace("\\", "/").startswith("//") or "://" in text or (win.drive and not win.root):
        raise PackageError("LOCAL_PATH_REQUIRED")
    if ".." in win.parts:
        raise PackageError("TRAVERSAL_PATH_FORBIDDEN")
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    for part in win.parts[1:] if win.anchor else win.parts:
        if ":" in part or part.rstrip(". ").split(".")[0].upper() in reserved:
            raise PackageError("DEVICE_OR_STREAM_PATH_FORBIDDEN")
    result = Path(os.path.abspath(text))
    cursor = Path(result.anchor)
    for part in result.parts[1:]:
        cursor /= part
        try:
            info = cursor.lstat()
        except FileNotFoundError:
            break
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise PackageError("SYMLINK_OR_REPARSE_PATH_FORBIDDEN")
    return result


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PackageError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _decode_json(data):
    try:
        result = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_pairs,
                            parse_constant=lambda _: (_ for _ in ()).throw(PackageError("FINITE_JSON_REQUIRED")))
        json.dumps(result, ensure_ascii=True, allow_nan=False)
    except (UnicodeError, ValueError, OverflowError) as error:
        raise PackageError("STRICT_FINITE_JSON_REQUIRED") from error
    if not isinstance(result, dict):
        raise PackageError("JSON_OBJECT_REQUIRED")
    return result


def _read(path):
    with safe_local(path).open("rb") as handle:
        data = handle.read(MAX_INPUT_BYTES + 1)
    if len(data) > MAX_INPUT_BYTES:
        raise PackageError("INPUT_TOO_LARGE")
    return data


def load_json(path):
    return _decode_json(_read(path))


def inspect_sources(root=ROOT):
    root = safe_local(root)
    documents, inputs, raw = {}, {}, {}
    for name, expected in SOURCE_PINS.items():
        data = _read(root / name)
        if sha256(data) != expected:
            raise PackageError("PINNED_SOURCE_DRIFT: " + name)
        inputs[name] = {"sha256": expected, "bytes": len(data), "redistributed_raw": False}
        raw[name] = data
        if name.endswith(".json"):
            documents[name] = _decode_json(data)
    official = documents[OFFICIAL_PROFILES]
    if official.get("version_number") != "24.10.4" or official.get("target") != "ath79/generic" or not isinstance(official.get("profiles"), dict):
        raise PackageError("WRONG_OFFICIAL_PROFILE_INVENTORY")
    mismatches = []
    for stage, field in ((165, "xc_champion_script"), (166, "xw_xm_champion_script")):
        declared = documents[STAGES[stage]][field]
        actual = inputs.get(declared["path"])
        if actual is None:
            raise PackageError("UNTRACKED_DECLARED_SOURCE")
        if declared["sha256"] != actual["sha256"]:
            mismatches.append({"source_stage": stage, "path": declared["path"],
                "declared_sha256": declared["sha256"], "observed_sha256": actual["sha256"],
                "status": "MUTABLE_SCRIPT_DIFFERS_FROM_HISTORICAL_RECEIPT", "current_script_executed_or_shipped": False})
    overlay = {}
    with tarfile.open(fileobj=io.BytesIO(raw[XC_OVERLAY]), mode="r:gz") as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            if not member.isfile() or member.size > MAX_INPUT_BYTES or name.is_absolute() or ".." in name.parts or member.name in overlay:
                raise PackageError("INVALID_HELD_OVERLAY_MEMBER")
            data = archive.extractfile(member).read(MAX_INPUT_BYTES + 1)
            if len(data) != member.size:
                raise PackageError("HELD_OVERLAY_MEMBER_SIZE_MISMATCH")
            overlay[member.name] = data
    historical = overlay.get("etc/hotplug.d/net/99-fmx-xc-universal-champion", b"")
    if sha256(historical) != documents[STAGES[165]]["xc_champion_script"]["sha256"]:
        raise PackageError("HISTORICAL_XC_SOURCE_NOT_RECOVERED")
    excluded = {name: {"bytes": len(data), "sha256": sha256(data), "redistributed": False} for name, data in overlay.items()}
    if excluded.get("lib/modules/6.6.110/mac80211.ko", {}).get("sha256") != "fe4f730fccaa68848a70c952e40c0438b32d413993f22887a0e72fed5eebaae6":
        raise PackageError("UNEXPECTED_HELD_WA_MODULE")
    return {"root": root, "documents": documents, "inputs": inputs, "raw": raw,
            "source_artifact_mismatches": mismatches, "historical_xc_source": historical,
            "excluded_overlay_members": excluded}


def _text(value, *, maximum=160):
    if not isinstance(value, str) or not 0 < len(value) <= maximum or not value.isascii() or any(ord(char) < 32 for char in value):
        raise PackageError("BOUNDED_ASCII_LABEL_REQUIRED")
    return value


def _uint(value):
    if type(value) is not int or not 0 <= value <= 2**32 - 1:
        raise PackageError("STRICT_UNSIGNED_INTEGER_REQUIRED")
    return value


def _record(record_id, family, source, model, sysid, profile, official, *, ram=None, historical_gate=None):
    _text(record_id)
    _text(model)
    _text(profile)
    if not isinstance(sysid, str) or not re.fullmatch(r"0x[0-9a-fA-F]{4}", sysid):
        raise PackageError("STRICT_SYSID_STRING_REQUIRED")
    if ram is not None:
        _uint(ram)
    present = profile in official
    if family == "XM" and ram is not None and ram <= 32:
        status = "STOCK_AIROS_ONLY_32MB_OPENWRT_UNQUALIFIED"
    elif present:
        status = "UPSTREAM_PROFILE_PRESENT_IDENTITY_UNQUALIFIED"
    else:
        status = "UNSUPPORTED_OR_UNKNOWN_EXACT_PROFILE"
    return {"record_id": record_id, "family": family, "source": source, "model": model,
            "reported_sysid": sysid.lower(), "claimed_openwrt_profile": profile,
            "ram_mib_claim": ram, "historical_safety_claim": historical_gate,
            "official_profile_present": present, "support_status": status,
            "exact_board_verified": False, "firmware_install_approved": False}


def build_profile_matrix(sources):
    if not isinstance(sources, dict) or not isinstance(sources.get("documents"), dict) or not isinstance(sources.get("raw"), dict):
        raise PackageError("VERIFIED_SOURCE_OBJECT_REQUIRED")
    for name, pin in SOURCE_PINS.items():
        raw = sources["raw"].get(name)
        if not isinstance(raw, bytes) or sha256(raw) != pin:
            raise PackageError("VERIFIED_SOURCE_OBJECT_DRIFT")
        if name.endswith(".json") and _json_bytes(sources["documents"].get(name)) != _json_bytes(_decode_json(raw)):
            raise PackageError("VERIFIED_SOURCE_DOCUMENT_DRIFT")
    docs = sources["documents"]
    official = docs[OFFICIAL_PROFILES]["profiles"]
    s158, s159, s165, s166 = (docs[STAGES[number]] for number in (158, 159, 165, 166))
    records = []
    for sysid, record in s159["passive_xc_16board_openwrt_kit"].items():
        if not isinstance(record, dict) or not isinstance(record.get("models"), list) or not record["models"]:
            raise PackageError("MALFORMED_XC_PASSIVE_RECORD")
        records.append(_record("xc159-" + sysid, "XC", STAGES[159], ", ".join(_text(m) for m in record["models"]),
                               sysid, record["openwrt_profile_id"], official, historical_gate="Historical SquashFS-compatible claim only"))
    for sysid, record in s165["xc_boards"].items():
        records.append(_record("xc165-" + sysid, "XC", STAGES[165], record["model"], sysid,
                               record["openwrt_board_id"].replace("ubnt,", "ubnt_", 1), official, ram=record["ram_mb"]))
    for record in s158["xw_30_board_records"]:
        records.append(_record("xw158-" + str(_uint(record["record_index"])), "XW", STAGES[158], record["name"],
                               record["sysid"], record["openwrt_profile_id"], official,
                               ram=record["ram_mib"], historical_gate=record["ram_safety_gate"]))
    for index, record in enumerate(s158["xm_ram_safety_matrix"]):
        records.append(_record("xm158-" + str(index), "XM", STAGES[158], record["name"], record["sysid"],
                               "UNKNOWN", official, ram=record["ram_mib"], historical_gate=record["ram_safety_gate"]))
    for family in s166["families"].values():
        for sysid, label in family["boards"].items():
            match = re.search(r"\((ubnt,[a-z0-9-]+)\)", label)
            if match is None:
                raise PackageError("MALFORMED_ATH9K_PROFILE_LABEL")
            records.append(_record("ath9k166-" + family["family"] + "-" + sysid, family["family"], STAGES[166],
                                   label, sysid, match.group(1).replace("ubnt,", "ubnt_", 1), official, ram=family["ram_mb"]))
    if len({r["record_id"] for r in records}) != len(records) or len(s158["xw_30_board_records"]) != 30:
        raise PackageError("RECORD_INVENTORY_MISMATCH")
    targets = []
    specifications = (
        ("Rocket Prism 5AC Gen2", "XC", None, True), ("PrismStation 5AC", "XC", None, True),
        ("PowerBeam 5AC 500", "XC", "ubnt_powerbeam-5ac-500", False),
        ("PowerBeam 5AC 620", "XC", "ubnt_powerbeam-5ac-620", False),
        ("IsoStation 5AC XC", "XC", "ubnt_isostation-5ac-xc", False),
        ("NanoBeam 5AC 19 XC", "XC", "ubnt_nanobeam-ac-xc", False),
        ("Rocket 5AC Lite", "XC", "ubnt_rocket-5ac-lite", False),
    )
    for model, family, profile, active_filter in specifications:
        present = profile in official if profile else False
        status = ("STOCK_AIROS_ONLY_ACTIVE_FILTER_UNQUALIFIED" if active_filter else
                  "UPSTREAM_PROFILE_PRESENT_IDENTITY_UNQUALIFIED" if present else "UNSUPPORTED_EXACT_PROFILE")
        targets.append({"model": model, "family": family, "candidate_profile": profile,
                        "official_profile_present": present, "support_status": status,
                        "exact_revision_dts_calibration_verified": False, "firmware_install_approved": False})
    return {"schema_version": 1, "official_inventory": {"version": "24.10.4", "target": "ath79/generic",
            "sha256": SOURCE_PINS[OFFICIAL_PROFILES], "https_source": "https://downloads.openwrt.org/releases/24.10.4/targets/ath79/generic/profiles.json",
            "gpg_verified": False}, "targets": targets, "reported_records": records,
            "identity_is_not_unique_by_sysid": True,
            "conflicts": [
                "Stage165 XC sysid/model/profile assignments disagree with Stage159 passive records; neither authorizes an image.",
                "Stage165 XC overlay contained a WA mac80211 object; the overlay and every kernel module are excluded.",
                "Stage166 XW sysid/model assignments disagree with Stage158 (including e845/e855/e866/e885); preserve records separately.",
                "Stage166 calls XM32MB profiles verified, while Stage158 explicitly blocks OpenWrt24.10.4 on32MB XM.",
                "Stage158 profile names and direct-safe flags are historical claims; some exact names are absent from the official inventory.",
                "Active AirPrism GPIO/HSR behavior is not qualified for these proposed OpenWrt profiles."]}


def _json_bytes(value):
    try:
        return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")
    except (ValueError, TypeError, OverflowError) as error:
        raise PackageError("FINITE_JSON_PAYLOAD_REQUIRED") from error


def _candidate(family, matrix, sources):
    stage = 165 if family == "XC" else 166
    document = sources["documents"][STAGES[stage]]
    if family == "XC":
        data = sources["historical_xc_source"]
        if not isinstance(data, bytes) or sha256(data) != document["xc_champion_script"]["sha256"]:
            raise PackageError("HISTORICAL_XC_CANDIDATE_SOURCE_DRIFT")
        values = dict(re.findall(r'^([A-Z0-9_]+)="\$\{\1:-([^}]+)\}"$', data.decode("ascii"), re.M))
    else:
        key = "XW_64MB" if family == "XW" else "XM_32MB"
        values = {name: value for name, value in document["families"][key].items() if name != "boards"}
    return {"schema_version": 1, "family": family, "enabled": False, "approved_for_live": False,
            "source_stage": str(stage), "source_status_is_not_acceptance": True,
            "historical_candidate_values": values, "configuration_verified": False,
            "hardware_performance_measured_here": False,
            "records": [r for r in matrix["reported_records"] if r["family"] == family],
            "required_before_any_application": ["Exact model/revision and actual driver/ABI", "Independent getter availability and bounds",
                "RAM/flash/calibration/DTS qualification", "Recovery and separately authorized physical counterbalanced test"],
            "kernel_modules_included": [], "actuation_script_included": False}


def public_payloads(matrix, sources):
    provenance = {"task_id": TASK_ID, "inputs": sources["inputs"], "proprietary_binaries_redistributed": False,
                  "source_artifact_mismatches": sources["source_artifact_mismatches"],
                  "excluded_overlay_members": sources["excluded_overlay_members"],
                  "historical_memory_claims_only": ["mm-37fa", "mm-1375"], "new_hardware_claim": None}
    result = {"README.md": (README, 0o644), "PROFILE_MATRIX.json": (_json_bytes(matrix), 0o644),
              "SOURCE_PROVENANCE.json": (_json_bytes(provenance), 0o644),
              "collect_capabilities.sh": (COLLECTOR, 0o755)}
    for family in ("XC", "XW", "XM"):
        result["families/" + family.lower() + ".candidate.json"] = (_json_bytes(_candidate(family, matrix, sources)), 0o644)
    return result


def audit_payloads(payloads):
    for name, (data, mode) in payloads.items():
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or path.suffix.lower() in {".bin", ".ko", ".cfg", ".pem", ".key"}:
            raise PackageError("FORBIDDEN_PUBLIC_PAYLOAD_PATH")
        if not isinstance(data, bytes) or mode not in (0o644, 0o755):
            raise PackageError("INVALID_PUBLIC_PAYLOAD")
        if re.search(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|ssh-(?:rsa|ed25519) [A-Za-z0-9+/]{16}", data):
            raise PackageError("PRIVATE_CREDENTIAL_MATERIAL_FORBIDDEN")
        if re.search(rb"\b(?:192\.168\.(?:100|200|15)\.\d+|10\.10\.\d+\.\d+|10\.99\.\d+\.\d+)\b", data):
            raise PackageError("LAB_ADDRESS_FORBIDDEN")
        if name.endswith(".json"):
            _decode_json(data)
    collector = payloads["collect_capabilities.sh"][0]
    executable = b"\n".join(line for line in collector.splitlines() if not line.startswith(b"#"))
    executable = executable.replace(b"2>/dev/null", b"")
    if re.search(rb"\b(?:ssh|scp|wget|curl|uci|iwpriv|iw|insmod|rmmod|sysctl|cfgmtd|mtd|reboot|tc)\b|/dev/mtd|/sys/kernel/debug|>>|[0-9]?>(?!&)",
                 executable):
        raise PackageError("COLLECTOR_ACTUATION_OR_NETWORK_FORBIDDEN")
    return {"sanitized": True, "files_scanned": len(payloads), "modules": 0, "firmware_images": 0,
            "private_configs": 0, "collector_executed": False, "raw_legacy_scripts_redistributed": False}


def _archives(payloads):
    zipped = io.BytesIO()
    with zipfile.ZipFile(zipped, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, (data, mode) in sorted(payloads.items()):
            info = zipfile.ZipInfo(name, date_time=(2025, 10, 24, 0, 0, 0))
            info.create_system, info.external_attr, info.compress_type = 3, (stat.S_IFREG | mode) << 16, zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    tarred = io.BytesIO()
    with tarfile.open(fileobj=tarred, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, (data, mode) in sorted(payloads.items()):
            member = tarfile.TarInfo(name)
            member.size, member.mode, member.mtime = len(data), mode, EPOCH
            archive.addfile(member, io.BytesIO(data))
    compressed = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=compressed, mtime=EPOCH, compresslevel=9) as handle:
        handle.write(tarred.getvalue())
    return {ARCHIVE_STEM + ".zip": zipped.getvalue(), ARCHIVE_STEM + ".tar.gz": compressed.getvalue()}


def _verify_archives(archives, payloads):
    with zipfile.ZipFile(io.BytesIO(archives[ARCHIVE_STEM + ".zip"])) as archive:
        if archive.namelist() != sorted(payloads) or any(archive.read(name) != payloads[name][0] for name in archive.namelist()):
            raise PackageError("ZIP_READBACK_MISMATCH")
    with tarfile.open(fileobj=io.BytesIO(archives[ARCHIVE_STEM + ".tar.gz"]), mode="r:gz") as archive:
        members = archive.getmembers()
        if [m.name for m in members] != sorted(payloads):
            raise PackageError("TAR_INVENTORY_MISMATCH")
        for member in members:
            if not member.isfile() or member.uid or member.gid or member.mode != payloads[member.name][1] or archive.extractfile(member).read() != payloads[member.name][0]:
                raise PackageError("TAR_READBACK_MISMATCH")


def _destinations(root, output_dir, receipt_path):
    output, receipt = safe_local(output_dir), safe_local(receipt_path)
    if output.parent != root / "firmware/openwrt" or not re.fullmatch(r"public_xc_xw_tester_release(?:_[A-Za-z0-9_-]{1,40})?", output.name):
        raise PackageError("DEDICATED_OUTPUT_DIRECTORY_REQUIRED")
    if receipt.parent != root / "artifacts/autoresearch" or not re.fullmatch(r"stage171a_[A-Za-z0-9_-]+\.json", receipt.name):
        raise PackageError("STAGE171_RECEIPT_PATH_REQUIRED")
    return output, receipt


def _atomic_write(path, data):
    path = safe_local(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".stage171a-", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _existing_inventory(output, expected):
    files, pending = set(), [output]
    directories = {str(PurePosixPath(name).parent) for name in expected} | {"."}
    while pending:
        parent = pending.pop()
        with os.scandir(parent) as entries:
            for entry in entries:
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                    raise PackageError("SYMLINK_OR_REPARSE_OUTPUT_FORBIDDEN")
                path = Path(entry.path)
                relative = path.relative_to(output).as_posix()
                if stat.S_ISDIR(info.st_mode):
                    if relative not in directories:
                        raise PackageError("UNEXPECTED_EXISTING_OUTPUT_DIRECTORY")
                    pending.append(path)
                elif stat.S_ISREG(info.st_mode):
                    files.add(relative)
                else:
                    raise PackageError("NONREGULAR_OUTPUT_FORBIDDEN")
    if files != set(expected):
        raise PackageError("UNEXPECTED_EXISTING_OUTPUT_INVENTORY")


def build_release(*, root=ROOT, output_dir=None, receipt_path=None, overwrite=False):
    root = safe_local(root)
    output, receipt_path = _destinations(root, output_dir or root / "firmware/openwrt/public_xc_xw_tester_release",
                                        receipt_path or root / "artifacts/autoresearch" / DEFAULT_RECEIPT.name)
    sources = inspect_sources(root)
    matrix = build_profile_matrix(sources)
    payloads = public_payloads(matrix, sources)
    sanitization = audit_payloads(payloads)
    manifest = {"schema_version": 1, "task_id": TASK_ID, "package_type": "DIAGNOSTIC_STARTER_NOT_FIRMWARE",
                "files": {name: {"sha256": sha256(data), "bytes": len(data), "mode": mode} for name, (data, mode) in sorted(payloads.items())}}
    payloads["PACKAGE_MANIFEST.json"] = (_json_bytes(manifest), 0o644)
    archives = _archives(payloads)
    if archives != _archives(payloads):
        raise PackageError("IN_MEMORY_REPRODUCIBILITY_FAILURE")
    _verify_archives(archives, payloads)
    files = {name: data for name, (data, _mode) in payloads.items()}
    files.update(archives)
    sums = "".join(f"{sha256(data)}  {name}\n" for name, data in sorted(files.items())).encode("ascii")
    files.update({"SHA256SUMS": sums, "SHA256SUMS.txt": sums})
    if output.exists():
        if not overwrite:
            raise PackageError("OUTPUT_EXISTS_FORCE_REQUIRED")
        existing = load_json(output / "PACKAGE_MANIFEST.json")
        if existing.get("task_id") != TASK_ID or type(existing.get("schema_version")) is not int or existing["schema_version"] != 1:
            raise PackageError("UNMANAGED_OUTPUT_FORBIDDEN")
        _existing_inventory(output, files)
    if receipt_path.exists():
        existing = load_json(receipt_path)
        if not overwrite or existing.get("task_id") != TASK_ID or existing.get("schema_version") != 1:
            raise PackageError("UNMANAGED_OR_UNAPPROVED_RECEIPT_OVERWRITE")
    for name, data in sorted(files.items()):
        _atomic_write(output / name, data)
    for name, data in files.items():
        if _read(output / name) != data:
            raise PackageError("OUTPUT_READBACK_MISMATCH")
    result = {"schema_version": 1, "stage": "171A", "task_id": TASK_ID, "status": "LOCAL_DIAGNOSTIC_STARTERS_BUILT_WITH_QUALIFICATIONS",
              "static_sources": sources["inputs"], "profile_matrix": matrix,
              "source_artifact_mismatches": sources["source_artifact_mismatches"],
              "excluded_overlay_members": sources["excluded_overlay_members"],
              "outputs": {name: {"path": (output / name).relative_to(root).as_posix(), "sha256": sha256(data), "bytes": len(data)} for name, data in sorted(files.items())},
              "implementation_sha256": sha256(Path(__file__).read_bytes()), "sanitization": sanitization,
              "reproducibility": {"two_independent_archive_serializations_equal": True, "zip_and_tar_roundtrip_verified": True,
                                  "fixed_epoch": EPOCH, "saved_outputs_read_back": True, "cross_toolchain_identity_proven": False},
              "boundary": {"device_contacts": [], "flash_executed": False, "hardware_test_executed": False,
                           "kernel_modules_included": False, "firmware_images_built": False, "deployment_executed": False,
                           "publication_executed": False, "collector_executed": False, "native_gain_claim": False},
              "pillar_a_ground_up_re_and_knob_catalog": {"status": "SAVED_SOURCE_AUDIT_ONLY", "source_stages": [158, 159, 165, 166], "binary_execution": False},
              "pillar_b_hyperresearch_and_scholar_reactor": {"status": "NOT_RUN_FOR_THIS_OFFLINE_PACKAGE", "official_profile_inventory_hash_verified": True,
                  "inherited_scholar_claims_independently_verified": False},
              "pillar_c_karpathy_autoresearch_and_watchdog": {"status": "OFFLINE_ARCHIVE_ROUNDTRIP_ONLY", "live_counterbalanced_test": False},
              "pillar_d_scientific_pareto_validation": {"status": "NO_PERFORMANCE_ACCEPTANCE", "hardware_results": [], "unresolved_source_conflicts": matrix["conflicts"]},
              "pillar_e_memory_master_claim_id": {"status": "NO_NEW_CLAIM_CREATED", "claim_id": None, "historical_source_claims_only": ["mm-37fa", "mm-1375"]},
              "qualification": ["Official profile presence does not qualify a model revision, DTS, calibration, ABI or recovery.",
                  "Conflicting historical sysids are preserved as separate source records.", "XM32MB remains stock-airOS-only; active AirPrism remains unqualified.",
                  "New read-only collector has not run on hardware; no RF gain or stable-tail-latency claim.",
                  "Files are atomically replaced individually; the output directory is not a transactional deployment."]}
    _atomic_write(receipt_path, _json_bytes(result))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = build_release(root=args.root, output_dir=args.output_dir, receipt_path=args.receipt, overwrite=args.force)
    except (PackageError, OSError) as error:
        print("Stage171 package failed: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps({"stage": result["stage"], "status": result["status"], "files": len(result["outputs"]),
                      "firmware_images": 0, "kernel_modules": 0}, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
