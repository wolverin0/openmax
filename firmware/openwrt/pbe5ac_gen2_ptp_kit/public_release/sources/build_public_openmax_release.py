#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build sanitized public images from pinned stock, locally, without flashing.

Uses pinned native SquashFS tools and TAR streams, preserving Unix metadata
without extracting symlinks on Windows. Never imports private preconfigs.
"""
from __future__ import annotations
import argparse
from copy import copy
import hashlib
import io
import ipaddress
import json
import lzma
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import struct
import subprocess
import sys
import tarfile
import zipfile
import zlib

KIT = Path(__file__).resolve().parent
ROOT = KIT.parents[2]
DEFAULT_RELEASE = KIT / "public_release"
DEFAULT_TOOLS = ROOT / "artifacts/verification/stage117a_tools"
DEFAULT_WORK = ROOT / "artifacts/verification/stage132a_build"
DEFAULT_RECEIPT = ROOT / "artifacts/autoresearch/stage132a_public_lbe5ac_pbe5ac_release_receipt.json"
FACTORY_NAME = "openwrt-24.10.4-ubnt-pbe5ac-gen2-openmax-public-factory.bin"
SYSUPGRADE_NAME = "openwrt-24.10.4-ubnt-pbe5ac-gen2-openmax-public-sysupgrade.bin"
BASE_PREFIX = "openwrt-24.10.4-ath79-generic-ubnt_powerbeam-5ac-gen2-squashfs-"
BASE_HASHES = {"factory": "52d25c7f17ffc69dedc66895af090630e913945ac34fcb87288a4c381021f174",
               "sysupgrade": "c3e17ac02259db08708dfa8250e1b06d7765487923bdd435dc5d52998da301a4"}
BOARDS = {
    "pbe5ac-gen2": {"profile": "ubnt,powerbeam-5ac-gen2", "board_id": "0xe3d6",
                    "dtb_sha256": "03d8236f5fbf665db1596b904dbc1aeb61a97908d5d08477883dfd5d336d812b",
                    "base_prefix": BASE_PREFIX, "hashes": BASE_HASHES},
    "lbe5ac-gen2": {"profile": "ubnt,litebeam-ac-gen2", "board_id": "0xe7f9",
                    "dtb_sha256": "13dc1329eedece4ed840d7a0caa1d3bbf261cdda110e6cad2a03fb8cf2905f26",
                    "base_prefix": "openwrt-24.10.4-ath79-generic-ubnt_litebeam-ac-gen2-squashfs-",
                    "hashes": {"factory": "dafd701bc80f544fde9368061c86487bc48499d4cc79ec80dbf1a5bbdc33c034",
                               "sysupgrade": "9c014e35de84d663f20e82371165b9f57c37a3b590fe921a9b30cff79b6a549c"}},
}
ROM_SHA256 = "8566fb1c104b61bdb645fc17ba28d6c0ea1bd738e2d05dc8a935464d872a1ce5"
TEB_SHA256 = "3e3d812ff0d4a2fd1a1f9c1257a9356058ac439108e3c27ef6b11d944b696868"
TOOL_ARCHIVE = "squashfs-tools-ng-1.3.2-mingw64.zip"
TOOL_SHA256 = "891b1ed46dd856d05e429b01de2c7d86175a4c22478b5a6770f94b9c2100d0f6"
SOURCE_DATE_EPOCH = 1761264000
ROOTFS_OFFSET = 0x280000
PARTITION_LIMIT = 0xF60000
CONSERVATIVE_IMAGE_LIMIT = 0xF30000
MODULE_PATH = "lib/modules/6.6.110/mac80211.ko"
GUIDE_NAME = "OPENMAX_PBE5AC_GEN2_PUBLIC_RELEASE_GUIDE.md"

BOOTSTRAP = br'''#!/bin/sh
# Wired-only first setup; no shared Wi-Fi key or site identity.
set -eu
uci -q batch <<'UCI'
set network.lan.proto='static'
set network.lan.ipaddr='192.168.1.20'
set network.lan.netmask='255.255.255.0'
set system.@system[0].hostname='OpenMAX'
set dhcp.lan.ignore='1'
set dhcp.lan.ra='disabled'
set dhcp.lan.dhcpv6='disabled'
set dhcp.lan.ndp='disabled'
UCI
uci -q delete network.lan.gateway || true
uci -q delete network.lan.dns || true
[ -s /etc/config/wireless ] || wifi config
radio=$(uci -q show wireless | sed -n 's/^wireless\.\([^=]*\)=wifi-device$/\1/p' | head -n 1)
if [ -n "$radio" ]; then
 uci set "wireless.$radio.disabled=1"
 uci -q delete wireless.default_radio0 || true
 uci set wireless.openmax='wifi-iface'
 uci set "wireless.openmax.device=$radio"
 uci set wireless.openmax.mode='ap'
 uci set wireless.openmax.network='lan'
 uci set wireless.openmax.ssid='OpenMAX-Setup'
 uci set wireless.openmax.encryption='psk2'
 uci -q delete wireless.openmax.key || true
 uci set wireless.openmax.wds='1'
 uci set wireless.openmax.disabled='1'
 uci commit wireless
fi
uci commit network
uci commit system
uci commit dhcp
/etc/init.d/openmax-admitter enable
exit 0
'''

ADMITTER = b'''#!/bin/sh
# AP bridge maintenance only. Authentication remains in hostapd.
# No captured vendor IEs, fixed BSSID, beacon or regulatory override.
set -u
once=${1:-}
tick() {
 # Bound host memory on 64 MiB units; never increase a smaller existing cap.
 mem=$(awk '/^MemTotal:/{print $2}' /proc/meminfo)
 if [ "${mem:-0}" -gt 0 ] && [ "$mem" -le 70000 ]; then
  for aqm in /sys/kernel/debug/ieee80211/phy*/aqm; do
   [ -f "$aqm" ] || continue
   cap=$(awk '$2 == "fq_memory_limit" {print $3}' "$aqm")
   case "$cap" in ''|*[!0-9]*) continue ;; esac
   if [ "$cap" -gt 4194304 ]; then
    printf 'fq_memory_limit 4194304' > "$aqm" 2>/dev/null || true
   fi
  done
  for pid in $(pidof hostapd wpa_supplicant 2>/dev/null); do
   [ -w "/proc/$pid/oom_score_adj" ] || continue
   printf '%s' -900 > "/proc/$pid/oom_score_adj" 2>/dev/null || true
  done
 fi
 for obj in $(ubus list 'hostapd.phy*-ap0' 2>/dev/null); do
  iface=${obj#hostapd.}
  case "$iface" in phy*-ap0) ;; *) continue ;; esac
  [ -d "/sys/class/net/$iface" ] || continue
  for dev in /sys/class/net/"$iface".sta*; do
   [ -e "$dev" ] || continue
   sta=${dev##*/}
   ip link set dev "$sta" up 2>/dev/null || continue
   ip link set dev "$sta" master br-lan 2>/dev/null || true
  done
 done
}
while :; do
 tick
 [ "$once" = '--once' ] && exit 0
 sleep 5
done
'''

SERVICE = b'''#!/bin/sh /etc/rc.common
START=95
STOP=10
USE_PROCD=1
start_service() {
 procd_open_instance
 procd_set_param command /usr/sbin/fmx_pbe5ac_admitter.sh
 procd_set_param respawn 3600 5 5
 procd_set_param stdout 1
 procd_set_param stderr 1
 procd_close_instance
}
'''

QOS_POLICY = b'''# Preserve upstream mac80211 AQL/FQ/CoDel defaults.
# No AQL, WMI, BQL, IRQ, NAPI or queue-depth writes from this release.
# On <=64 MiB-class RAM only: lower FQ memory caps above4MiB, never raise them;
# protect hostapd/wpa_supplicant from OOM selection. No airtime/timing override.
# Generic sch_fq_codel target=5ms/interval=100ms are its normal defaults,
# not a mac80211 timing override. No root qdisc is replaced at startup.
# Historical bench profiles are not universal safe tuning values.
'''


class ReleaseError(ValueError):
    """Invalid image, path, toolchain or public payload."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def safe_local(path):
    text, win = str(path), PureWindowsPath(str(path))
    if text.replace("\\", "/").startswith("//") or "://" in text or (win.drive and not win.root):
        raise ReleaseError("Remote/device/URI/drive-relative paths forbidden")
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    for part in win.parts[1:] if win.anchor else win.parts:
        if ":" in part or part.rstrip(". ").split(".")[0].upper() in reserved:
            raise ReleaseError("Device/alternate-stream path forbidden")
    result = Path(os.path.abspath(text))
    current = Path(result.anchor)
    for part in result.parts[1:]:
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            break
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ReleaseError("Symlink/reparse path forbidden")
    return result


def inspect_uimage(data):
    if len(data) < 64 or data[:4] != b"\x27\x05\x19\x56":
        raise ReleaseError("Invalid uImage magic/header")
    head_crc, size, data_crc = (struct.unpack_from(">I", data, n)[0] for n in (4, 12, 24))
    if not 0 < size <= len(data) - 64:
        raise ReleaseError("uImage length exceeds input")
    if zlib.crc32(data[:4] + b"\0" * 4 + data[8:64]) & 0xffffffff != head_crc:
        raise ReleaseError("uImage header CRC mismatch")
    if zlib.crc32(data[64:64 + size]) & 0xffffffff != data_crc:
        raise ReleaseError("uImage data CRC mismatch")
    return {"data_size": size, "header_crc_valid": True, "data_crc_valid": True,
            "kernel_sha256": sha256(data[:64 + size])}


def inspect_squashfs(data):
    if len(data) < 96 or data[:4] != b"hsqs":
        raise ReleaseError("Missing SquashFS superblock")
    block = struct.unpack_from("<I", data, 12)[0]
    comp, log = struct.unpack_from("<HH", data, 20)
    version = struct.unpack_from("<HH", data, 28)
    used = struct.unpack_from("<Q", data, 40)[0]
    if version != (4, 0) or comp != 4 or block != 262144 or log != 18 or not 96 <= used <= len(data):
        raise ReleaseError("Unexpected SquashFS format/bounds")
    return {"version": "4.0", "compression": "xz", "block_size": block, "bytes_used": used}


def inspect_board_kernel(payload, board):
    if board not in BOARDS:
        raise ReleaseError("Unknown kernel board")
    spec = BOARDS[board]
    kernel = inspect_uimage(payload)
    try:
        decoder = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
        raw = decoder.decompress(payload[64:64 + kernel["data_size"]], max_length=32 * 1024 * 1024)
    except lzma.LZMAError as error:
        raise ReleaseError("Invalid compressed kernel") from error
    if not decoder.eof:
        raise ReleaseError("Kernel decompression exceeds bound or is truncated")
    offset = raw.rfind(b"\xd0\x0d\xfe\xed")
    if offset < 0 or offset + 40 > len(raw):
        raise ReleaseError("Board DTB missing")
    size = struct.unpack_from(">I", raw, offset + 4)[0]
    dtb = raw[offset:offset + size]
    if size < 40 or len(dtb) != size or sha256(dtb) != spec["dtb_sha256"] or spec["profile"].encode() + b"\0" not in dtb:
        raise ReleaseError("Wrong board DTB; cross-board relabel rejected")
    return {**kernel, "dtb_sha256": sha256(dtb), "dtb_size_bytes": size,
            "compatible": spec["profile"], "kernel_prefix_sha256": sha256(payload[:ROOTFS_OFFSET])}


def parse_factory(data):
    if len(data) < 268 or data[:4] != b"OPEN" or zlib.crc32(data[:260]) & 0xffffffff != struct.unpack_from(">I", data, 260)[0]:
        raise ReleaseError("Factory header CRC/magic mismatch")
    if data[264:268] != b"\0" * 4:
        raise ReleaseError("Factory header pad mismatch")
    pos, parts = 268, []
    for expected in (b"kernel", b"rootfs"):
        h = data[pos:pos + 56]
        if len(h) != 56 or h[:4] != b"PART" or h[4:20].rstrip(b"\0") != expected:
            raise ReleaseError("Unexpected factory partition table")
        size, capacity = struct.unpack_from(">II", h, 48)
        end = pos + 56 + size
        if not 0 < size <= capacity or end + 8 > len(data):
            raise ReleaseError("Factory partition length exceeds capacity")
        if data[end + 4:end + 8] != b"\0" * 4 or zlib.crc32(data[pos:end]) & 0xffffffff != struct.unpack_from(">I", data, end)[0]:
            raise ReleaseError("Factory partition CRC mismatch")
        parts.append({"name": expected.decode(), "header": h, "data": data[pos + 56:end], "capacity": capacity})
        pos = end + 8
    if data[pos:] != b"ENDS" + b"\0" * 260 or [p["capacity"] for p in parts] != [0x100000, 0xe60000]:
        raise ReleaseError("Wrong factory suffix/partition capacities")
    payload = b"".join(p["data"] for p in parts)
    inspect_uimage(payload)
    return {"header": data[:268], "parts": parts, "suffix": data[pos:], "payload": payload}


def parse_sysupgrade(data, profile="ubnt,powerbeam-5ac-gen2"):
    end, trailers = len(data), []
    for kind in (0, 1):
        if end < 16:
            raise ReleaseError("Missing FWx0 trailer")
        magic, crc, actual_kind, pad, size = struct.unpack_from(">4sIB3sI", data, end - 16)
        if magic != b"FWx0" or actual_kind != kind or pad != b"\0" * 3 or not 16 <= size <= end:
            raise ReleaseError("Invalid FWx0 trailer")
        if (zlib.crc32(data[:end - 16]) ^ 0xffffffff) & 0xffffffff != crc:
            raise ReleaseError("FWx0 CRC mismatch")
        trailers.append({"kind": kind, "data": data[end - size:end - 16], "crc_valid": True})
        end -= size
    if trailers[0]["data"] != b"# fake certificate" or trailers[1]["data"][:8] != b"\0" * 8:
        raise ReleaseError("Unexpected metadata wrapper")
    try:
        meta = json.loads(trailers[1]["data"][8:])
    except (ValueError, UnicodeError) as error:
        raise ReleaseError("Invalid firmware metadata JSON") from error
    if not isinstance(meta, dict) or not isinstance(meta.get("version"), dict):
        raise ReleaseError("Malformed firmware metadata")
    if profile not in {b["profile"] for b in BOARDS.values()} or meta.get("supported_devices") != [profile] or meta["version"].get("target") != "ath79/generic" or meta["version"].get("version") != "24.10.4":
        raise ReleaseError("Wrong device/target/release")
    payload = data[:end]
    if payload[-4:] != b"\xde\xad\xc0\xde" or (len(payload) - 4) % 0x10000 or len(payload) > CONSERVATIVE_IMAGE_LIMIT:
        raise ReleaseError("Invalid rootfs padding/flash size")
    inspect_uimage(payload)
    inspect_squashfs(payload[ROOTFS_OFFSET:])
    return {"payload": payload, "trailers": trailers, "metadata": meta}


def _append_fwx0(prefix, payload, kind):
    covered = prefix + payload
    return covered + struct.pack(">4sIB3sI", b"FWx0", (zlib.crc32(covered) ^ 0xffffffff) & 0xffffffff,
                                  kind, b"\0" * 3, len(payload) + 16)


def rebuild_images(factory_template, sysupgrade_template, squashfs, profile="ubnt,powerbeam-5ac-gen2"):
    factory, original = parse_factory(factory_template), parse_sysupgrade(sysupgrade_template, profile)
    if factory["payload"] != original["payload"]:
        raise ReleaseError("Base factory/sysupgrade payloads disagree")
    inspect_squashfs(squashfs)
    body = original["payload"][:ROOTFS_OFFSET] + squashfs
    body += b"\xff" * (-len(body) % 0x10000) + b"\xde\xad\xc0\xde"
    if len(body) > min(PARTITION_LIMIT, CONSERVATIVE_IMAGE_LIMIT):
        raise ReleaseError("Public image exceeds board capacity")
    meta = copy(original["metadata"])
    meta["openmax"] = {"release": "public-r1", "mac80211_sha256": TEB_SHA256, "runtime_validated": False}
    metadata = b"\0" * 8 + json.dumps(meta, sort_keys=True, separators=(",", ":")).encode()
    public_sys = _append_fwx0(_append_fwx0(body, metadata, 1), b"# fake certificate", 0)
    blocks = []
    for part, content in zip(factory["parts"], (body[:0x100000], body[0x100000:])):
        h = bytearray(part["header"])
        struct.pack_into(">I", h, 48, len(content))
        block = bytes(h) + content
        blocks.append(block + struct.pack(">II", zlib.crc32(block) & 0xffffffff, 0))
    public_factory = factory["header"] + b"".join(blocks) + factory["suffix"]
    if parse_factory(public_factory)["payload"] != parse_sysupgrade(public_sys, profile)["payload"]:
        raise ReleaseError("Rebuilt payload mismatch")
    return public_factory, public_sys


def _elf_sections(data):
    if len(data) < 52 or data[:6] != b"\x7fELF\x01\x02" or struct.unpack_from(">H", data, 18)[0] != 8:
        raise ReleaseError("Module must be ELF32 BE MIPS")
    start = struct.unpack_from(">I", data, 32)[0]
    width, count, names_index = struct.unpack_from(">HHH", data, 46)
    if width != 40 or count == 0 or names_index >= count or start + count * width > len(data):
        raise ReleaseError("Invalid ELF section bounds")
    sections = [struct.unpack_from(">10I", data, start + i * width) for i in range(count)]
    strings = sections[names_index]
    names = data[strings[4]:strings[4] + strings[5]]
    return {names[s[0]:].split(b"\0", 1)[0].decode(): (s[4], s[5]) for s in sections}


def patch_teb(original):
    if sha256(original) != ROM_SHA256:
        raise ReleaseError("Unrecognized original mac80211")
    offset = _elf_sections(original)[".text"][0]
    branch = lambda op, rs, pc: (op << 26) | (rs << 21) | ((0x33c6c - pc - 4) >> 2)
    words = [branch(4, 6, 0x33c18), 0xafb10064, 0x8cc80054, 0x8cc90058, 0x01094823,
             0x2d2a001c, branch(5, 10, 0x33c30), 0x8cc900a8, 0x912a000c, 0x912b000d,
             0x000a5200, 0x014b5025, 0x394a6558, branch(5, 10, 0x33c4c), 0x2508fff2,
             0x2529000e, 0xacc80054, 0xacc900a8, 0x90ca0064, 0x7c0a1044, 0xa0ca0064]
    patched = bytearray(original)
    for i, word in enumerate(words):
        struct.pack_into(">I", patched, offset + 0x33c18 + 4 * i, word)
    if sha256(patched) != TEB_SHA256:
        raise ReleaseError("Reproduced TEB module hash mismatch")
    return bytes(patched)


def verify_module(patched, original):
    if len(patched) != 815640 or sha256(patched) != TEB_SHA256 or patch_teb(original) != patched:
        raise ReleaseError("Module pin/reproduction mismatch")
    if _elf_sections(patched).get(".gnu.linkonce.this_module", (0, 0))[1] != 352:
        raise ReleaseError("Module layout ABI mismatch")
    if b"vermagic=6.6.110 mod_unload MIPS32_R2 32BIT \0" not in patched or b"license=GPL\0" not in patched:
        raise ReleaseError("Module vermagic/license mismatch")
    changed = [i for i, (a, b) in enumerate(zip(original, patched)) if a != b]
    if len(changed) != 71 or not all(0x33c88 <= i < 0x33cdc for i in changed):
        raise ReleaseError("Unexpected module changes")
    return {"sha256": TEB_SHA256, "size_bytes": len(patched), "original_sha256": ROM_SHA256,
            "vermagic": "6.6.110 mod_unload MIPS32_R2 32BIT", "module_layout_bytes": 352,
            "elf": "ELF32 BE MIPS", "changed_bytes": 71, "patch_reproduced": True,
            "ethertype": "0x6558", "hardware_execution_verified": False}


def public_payloads(profile="ubnt,powerbeam-5ac-gen2"):
    if profile not in {b["profile"] for b in BOARDS.values()}:
        raise ReleaseError("Unknown public board profile")
    return {"etc/uci-defaults/99-openmax-public": (BOOTSTRAP, 0o755),
            "usr/sbin/fmx_pbe5ac_admitter.sh": (ADMITTER, 0o755),
            "etc/init.d/openmax-admitter": (SERVICE, 0o755),
            "etc/openmax/qos-defaults.conf": (QOS_POLICY, 0o644),
            "etc/openmax-release": (("OPENMAX_RELEASE='public-r1'\nOPENMAX_BASE='OpenWrt 24.10.4'\nOPENMAX_PROFILE='" + profile + "'\n").encode(), 0o644)}


def _tar_entries(path):
    entries = {}
    with tarfile.open(safe_local(path), "r:") as archive:
        for member in archive:
            name = member.name.removeprefix("./").rstrip("/") or "."
            parsed = PurePosixPath(name)
            if parsed.is_absolute() or ".." in parsed.parts or "\\" in name or name in entries or member.islnk():
                raise ReleaseError("Unsafe/duplicate/hardlink TAR member")
            data = archive.extractfile(member).read() if member.isfile() else None
            entries[name] = (member, data)
    return entries


def audit_tar(path, profile="ubnt,powerbeam-5ac-gen2"):
    entries, findings, public = _tar_entries(path), [], public_payloads(profile)
    for name, (member, data) in entries.items():
        if any(token in name.lower() for token in ("authorized_keys", "id_rsa", "id_ed25519", "dropbear_rsa_host_key", "dropbear_ed25519_host_key", "rc.poststart", "sysupgrade-overlay")):
            findings.append("private-or-lab-file")
        if data is None:
            continue
        if re.search(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\r\n]+[A-Za-z0-9+/=]{16}", data):
            findings.append("private-key-material")
        if re.search(rb"\b(?:192\.168\.100\.[0-9]+|192\.168\.15\.[0-9]+|10\.10\.[0-9]+\.[0-9]+|10\.99\.[0-9]+\.[0-9]+)\b", data):
            findings.append("lab-network-literal")
        if name in public:
            for value in re.findall(rb"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])", data):
                if ipaddress.ip_address(value.decode()).is_private and value not in (b"192.168.1.20", b"255.255.255.0"):
                    findings.append("unexpected-private-ip")
            if re.search(rb"(?:option\s+key\s+|\.key\s*=\s*)['\"][^'\"]+['\"]", data):
                findings.append("baked-wifi-key")
    if findings:
        raise ReleaseError("Sanitization failed: " + ", ".join(sorted(set(findings))))
    for name, (expected, mode) in public.items():
        if name not in entries or entries[name][1] != expected or entries[name][0].mode != mode:
            raise ReleaseError("Public payload/mode readback mismatch")
    inventory = {name: {"sha256": sha256(data) if data is not None else None, "mode": member.mode,
                        "uid": member.uid, "gid": member.gid, "type": member.type.decode("ascii"), "linkname": member.linkname}
                 for name, (member, data) in entries.items()}
    return {"member_count": len(entries), "findings": [], "inventory": inventory,
            "public_payload_paths": sorted(public), "private_keys_found": 0, "lab_addresses_found": 0}


def _write_public_tar(stock_tar, target_tar, module, profile="ubnt,powerbeam-5ac-gen2"):
    original = _tar_entries(stock_tar)
    if MODULE_PATH not in original:
        raise ReleaseError("Base module absent")
    module_check = verify_module(module, original[MODULE_PATH][1])
    additions = public_payloads(profile)
    additions[MODULE_PATH] = (module, original[MODULE_PATH][0].mode)
    result = dict(original)
    for name, (data, mode) in additions.items():
        member = tarfile.TarInfo("./" + name)
        member.mode, member.mtime, member.size = mode, SOURCE_DATE_EPOCH, len(data)
        result[name] = (member, data)
        parent = PurePosixPath(name).parent
        while str(parent) != ".":
            if str(parent) not in result:
                directory = tarfile.TarInfo("./" + str(parent))
                directory.type, directory.mode, directory.mtime = tarfile.DIRTYPE, 0o755, SOURCE_DATE_EPOCH
                result[str(parent)] = (directory, None)
            parent = parent.parent
    with tarfile.open(target_tar, "w", format=tarfile.PAX_FORMAT) as archive:
        for name in sorted(result, key=lambda key: (key != ".", key)):
            member, data = result[name]
            member = copy(member)
            member.mtime = SOURCE_DATE_EPOCH
            member.pax_headers = {k: v for k, v in member.pax_headers.items() if k not in ("mtime", "atime", "ctime")}
            archive.addfile(member, io.BytesIO(data) if data is not None else None)
    check = audit_tar(target_tar, profile)
    changed = [name for name in original if result[name][1] != original[name][1]]
    if changed != [MODULE_PATH]:
        raise ReleaseError("Unexpected stock file modification")
    check["module"] = module_check
    return check


def _toolchain(tools_dir):
    root = safe_local(tools_dir)
    archive = root / TOOL_ARCHIVE
    if sha256(archive.read_bytes()) != TOOL_SHA256:
        raise ReleaseError("Native tool archive pin mismatch")
    with zipfile.ZipFile(archive) as package:
        for name in package.namelist():
            if name.endswith((".exe", ".dll")) and safe_local(root / name).read_bytes() != package.read(name):
                raise ReleaseError("Native executable/DLL pin mismatch")
    folder = root / "squashfs-tools-ng-1.3.2-mingw64/bin"
    return {name: folder / (name + ".exe") for name in ("sqfs2tar", "tar2sqfs")}


def _run_tool(command, *, stdin=None, stdout=None):
    result = subprocess.run([str(p) for p in command], stdin=stdin, stdout=stdout or subprocess.PIPE,
                            stderr=subprocess.PIPE, cwd=str(Path(command[0]).parent), timeout=120,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if result.returncode:
        raise ReleaseError(f"Native tool {Path(command[0]).name} failed, exit {result.returncode}")
    return result


def _source_notice():
    return b'''# OpenMAX public-r1 sources and notices
Base: OpenWrt 24.10.4 r28959-29397011cc, ath79/generic.
Separate official ubnt,powerbeam-5ac-gen2 and ubnt,litebeam-ac-gen2 base images.
Modified OpenWrt image, not Ubiquiti-signed firmware or an official OpenWrt build.
Original package notices remain in the unchanged stock filesystem.

- Base images/checksums/buildinfo: https://downloads.openwrt.org/releases/24.10.4/targets/ath79/generic/
- Base source/build recipes: https://github.com/openwrt/openwrt/tree/v24.10.4
- Package sources: https://sources.openwrt.org/ (exact versions/hashes are in those build recipes).
- Modified mac80211 is GPL: the included builder contains the complete deterministic 21-instruction patch and pins.
- New bootstrap, service and admitter sources are in sources/public_payloads/, GPL-2.0-or-later.
- GPLv2 text: sources/public_assets/COPYING.GPL-2.0.

Rebuild in the source repository using the pinned official base images; no device dump or private config is needed.
Retain notices and provide complete corresponding sources for covered components when redistributing.
These source locators and the modification recipe do not assert a blanket licensing review of upstream packages.
'''


def build_release(*, root=ROOT, output_dir=None, tools_dir=DEFAULT_TOOLS, work_dir=DEFAULT_WORK,
                  module_path=None, guide_path=None, overwrite=False, board="pbe5ac-gen2", _defer=False):
    if board not in BOARDS:
        raise ReleaseError("Unknown board; no cross-board fallback")
    spec = BOARDS[board]
    profile, pins = spec["profile"], spec["hashes"]
    root = safe_local(root)
    kit = root / "firmware/openwrt/pbe5ac_gen2_ptp_kit"
    output, work = safe_local(output_dir or kit / "public_release"), safe_local(work_dir)
    if output.parent != kit or not output.name.startswith("public_release"):
        raise ReleaseError("Output must be a public_release directory inside this kit")
    if not work.is_relative_to(root / "artifacts/verification") or work == root / "artifacts/verification":
        raise ReleaseError("Workspace must be a dedicated verification subdirectory")
    factory_path = safe_local(root / "firmware/openwrt" / (spec["base_prefix"] + "factory.bin"))
    sys_path = safe_local(root / "firmware/openwrt" / (spec["base_prefix"] + "sysupgrade.bin"))
    factory, sysimage = factory_path.read_bytes(), sys_path.read_bytes()
    if sha256(factory) != pins["factory"] or sha256(sysimage) != pins["sysupgrade"]:
        raise ReleaseError("Official stock base pin mismatch; private prebaked images rejected")
    parsed = parse_sysupgrade(sysimage, profile)
    if parse_factory(factory)["payload"] != parsed["payload"]:
        raise ReleaseError("Official base payload mismatch")
    board_kernel = inspect_board_kernel(parsed["payload"], board)
    module = safe_local(module_path or kit / "mac80211_teb_6.6.110.ko").read_bytes()
    if sha256(module) != TEB_SHA256:
        raise ReleaseError("TEB module pin mismatch")
    guide = safe_local(guide_path or root / "docs" / GUIDE_NAME).read_bytes()
    license_text = safe_local(kit / "public_assets/COPYING.GPL-2.0").read_bytes()
    tools = _toolchain(tools_dir)
    if output.exists() and not overwrite:
        raise ReleaseError("Output exists; explicit --force required")
    # Reject existing redirected children before any scratch writes or backend execution.
    if work.exists():
        for child in work.rglob("*"):
            safe_local(child)
    work.mkdir(parents=True, exist_ok=True)
    stock_sqfs, stock_tar = work / "stock.squashfs", work / "stock.tar"
    used = inspect_squashfs(parsed["payload"][ROOTFS_OFFSET:])["bytes_used"]
    stock_sqfs.write_bytes(parsed["payload"][ROOTFS_OFFSET:ROOTFS_OFFSET + used])
    with stock_tar.open("wb") as handle:
        _run_tool([tools["sqfs2tar"], "-r", ".", "-L", "-s", stock_sqfs], stdout=handle)
    public_tar, public_sqfs, reread_tar = work / "public.tar", work / "public.squashfs", work / "reread.tar"
    tar_audit = _write_public_tar(stock_tar, public_tar, module, profile)
    with public_tar.open("rb") as handle:
        _run_tool([tools["tar2sqfs"], "-f", "-q", "-s", "-c", "xz", "-b", "262144", "-j", "1",
                   "-k", "-d", f"uid=0,gid=0,mode=0755,mtime={SOURCE_DATE_EPOCH}", public_sqfs], stdin=handle)
    with reread_tar.open("wb") as handle:
        _run_tool([tools["sqfs2tar"], "-r", ".", "-L", "-s", public_sqfs], stdout=handle)
    reread = audit_tar(reread_tar, profile)
    if reread["inventory"] != tar_audit["inventory"]:
        raise ReleaseError("Repacked rootfs content/ownership/mode mismatch")
    out_factory, out_sys = rebuild_images(factory, sysimage, public_sqfs.read_bytes(), profile)
    rebuilt = parse_sysupgrade(out_sys, profile)
    if rebuilt["payload"][:ROOTFS_OFFSET] != parsed["payload"][:ROOTFS_OFFSET]:
        raise ReleaseError("Kernel prefix changed")
    if inspect_board_kernel(rebuilt["payload"], board) != board_kernel:
        raise ReleaseError("Board kernel readback changed")
    factory_name = f"openwrt-24.10.4-ubnt-{board}-openmax-public-factory.bin"
    sys_name = f"openwrt-24.10.4-ubnt-{board}-openmax-public-sysupgrade.bin"
    payloads = {factory_name: out_factory, sys_name: out_sys, GUIDE_NAME: guide,
                "SOURCE_AND_LICENSES.md": _source_notice(),
                "sources/build_public_openmax_release.py": Path(__file__).read_bytes(),
                "sources/public_assets/COPYING.GPL-2.0": license_text,
                "modules/mac80211_teb_6.6.110.ko": module}
    for name, (data, _mode) in public_payloads(profile).items():
        payloads["sources/public_payloads/" + board + "/" + name] = data
    sums = _checksum_text(payloads)
    if not _defer:
        _publish_bundle(output, payloads, overwrite)
    inventory_path = work / "rootfs_inventory.json"
    inventory_path.write_text(json.dumps(reread, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema_version": 1, "stage": "117A", "status": "LOCAL_PUBLIC_CANDIDATES_BUILT_NOT_HARDWARE_VALIDATED",
        "board_profile": profile, "board_id": spec["board_id"],
        "board_id_evidence": "Operator hardware catalog; not encoded by the shared WA factory header",
        "openwrt_version": "24.10.4", "kernel": "6.6.110",
        "inputs": {"factory_sha256": pins["factory"], "sysupgrade_sha256": pins["sysupgrade"],
                   "module_sha256": TEB_SHA256, "private_preconfigs_imported": False,
                   "official_checksum_url": "https://downloads.openwrt.org/releases/24.10.4/targets/ath79/generic/sha256sums",
                   "official_checksums_https_compared": True, "gpg_signature_verified": False},
        "toolchain": {"name": "squashfs-tools-ng", "version": "1.3.2", "archive_sha256": TOOL_SHA256,
                      "url": "https://infraroot.at/pub/squashfs/windows/" + TOOL_ARCHIVE,
                      "archive_and_executables_checked": True, "target_code_executed": False},
        "build": {"source_date_epoch": SOURCE_DATE_EPOCH, "compression": "xz", "block_size": 262144,
                  "jobs": 1, "builder_sha256": sha256(Path(__file__).read_bytes()), "rootfs_offset": ROOTFS_OFFSET,
                  "firmware_bytes": len(rebuilt["payload"]), "conservative_limit": CONSERVATIVE_IMAGE_LIMIT,
                  "board_partition_limit": PARTITION_LIMIT},
        "outputs": {name: {"path": (output / name).relative_to(root).as_posix(), "sha256": sha256(data), "size_bytes": len(data)}
                    for name, data in payloads.items()},
        "sha256sums": {"path": (output / "SHA256SUMS").relative_to(root).as_posix(), "sha256": sha256(sums.encode())},
        "module": tar_audit["module"],
        "container_verification": {"factory_header_and_part_crcs": True, "sysupgrade_metadata_crcs": True,
            "factory_sysupgrade_payload_equal": True, "kernel_prefix_unchanged": True,
            "uimage": inspect_uimage(rebuilt["payload"]), "board_kernel": board_kernel, "vendor_signature_generated": False},
        "rootfs_verification": {"sanitized": True, "member_count": reread["member_count"],
            "stock_regular_content_preserved_except": [MODULE_PATH], "modified_files": sorted(public_payloads(profile)) + [MODULE_PATH],
            "actual_repacked_squashfs_reread": True, "private_keys_found": 0, "lab_addresses_found": 0,
            "inventory_path": inventory_path.relative_to(root).as_posix(), "inventory_sha256": sha256(inventory_path.read_bytes()),
            "stock_tar_path": stock_tar.relative_to(root).as_posix(), "public_tar_path": reread_tar.relative_to(root).as_posix()},
        "defaults": {"management_address": "192.168.1.20/24", "dhcp_server": False, "wireless_enabled": False,
            "shared_wifi_key": False, "wds_4addr": True, "admitter": "dynamic phy*-ap0 WDS bridge maintenance",
            "vendor_ie_captures_embedded": False, "queue_policy": "Preserve upstream AQL/CoDel timing; bound FQ memory to4MiB on64MiB-class RAM",
            "memory_guard": {"max_memtotal_kib": 70000, "fq_memory_cap_bytes": 4194304, "only_lower_existing_cap": True, "daemon_oom_score_adj": -900},
            "regulatory_override": False},
        "boundaries": {"radios_contacted": [], "flash_executed": False, "published": False, "signature_bypass": False,
            "protected_partition_data_imported": False, "hardware_boot_verified": False, "recovery_verified": False,
            "stock_airos_zero_touch_interop_claimed": False},
        "limitations": ["Local image validation is not boot/flash/recovery/performance acceptance",
            "OpenWrt-style ENDS/fake-certificate wrappers are not vendor authentication",
            "Wired initial setup only; no remote OTA migration profile or saved credentials",
            "No captured vendor IE material or stock airOS zero-touch claim",
            "Source/license notices and patch recipe supplied; no blanket licensing review"]}
    return (receipt, payloads) if _defer else receipt


def _checksum_text(payloads):
    return "".join(f"{sha256(payloads[name])}  {name}\n" for name in sorted(payloads))


def _publish_bundle(output, payloads, overwrite):
    output = safe_local(output)
    if output.exists() and not overwrite:
        raise ReleaseError("Output exists; explicit --force required")
    allowed = set(payloads) | {"SHA256SUMS"}
    if output.exists():
        for path in output.rglob("*"):
            safe_local(path)
            if path.is_file() and path.relative_to(output).as_posix() not in allowed:
                raise ReleaseError("Unexpected file in release directory; refusing replacement")
    output.mkdir(parents=True, exist_ok=True)
    # Each file replaces atomically; the checksum manifest is committed last.
    for name, data in {**payloads, "SHA256SUMS": _checksum_text(payloads).encode("ascii")}.items():
        target = safe_local(output / name)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = safe_local(target.with_name(target.name + ".stage132a-tmp"))
        if temporary.exists():
            raise ReleaseError("Build temporary already exists")
        with temporary.open("xb") as handle:
            handle.write(data)
        os.replace(temporary, target)
        if target.read_bytes() != data:
            raise ReleaseError("Published local file readback mismatch")


def build_dual_release(*, root=ROOT, output_dir=None, tools_dir=DEFAULT_TOOLS,
                       work_dir=DEFAULT_WORK, overwrite=False):
    root = safe_local(root)
    kit = root / "firmware/openwrt/pbe5ac_gen2_ptp_kit"
    output = safe_local(output_dir or kit / "public_release")
    work = safe_local(work_dir)
    boards, payloads = {}, {}
    for board in BOARDS:
        receipt, files = build_release(root=root, output_dir=output, tools_dir=tools_dir,
            work_dir=work / board, overwrite=overwrite, board=board, _defer=True)
        for name, data in files.items():
            if name in payloads and payloads[name] != data:
                raise ReleaseError("Conflicting shared release asset")
            payloads[name] = data
        boards[board] = receipt
    # Firmware prefixes are board-specific; a relabeled common kernel is forbidden.
    prefixes = [parse_sysupgrade(payloads[f"openwrt-24.10.4-ubnt-{board}-openmax-public-sysupgrade.bin"],
                BOARDS[board]["profile"])["payload"][:ROOTFS_OFFSET] for board in BOARDS]
    if prefixes[0] == prefixes[1]:
        raise ReleaseError("Board-specific kernel prefixes unexpectedly identical")
    _publish_bundle(output, payloads, overwrite)
    sums = _checksum_text(payloads)
    shared_sums = {"path": (output / "SHA256SUMS").relative_to(root).as_posix(), "sha256": sha256(sums.encode())}
    for receipt in boards.values():
        receipt["stage"] = "132A"
        receipt["sha256sums"] = shared_sums
    return {"schema_version": 1, "stage": "132A",
        "status": "LOCAL_DUAL_BOARD_PUBLIC_CANDIDATES_BUILT_NOT_HARDWARE_VALIDATED",
        "boards": boards, "sha256sums": shared_sums,
        "outputs": {name: {"path": (output / name).relative_to(root).as_posix(),
                    "sha256": sha256(data), "size_bytes": len(data)} for name, data in payloads.items()},
        "board_specific_kernel_prefixes_distinct": True,
        "boundaries": {"radios_contacted": [], "flash_executed": False, "published": False,
                       "hardware_boot_verified": False, "recovery_verified": False}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RELEASE)
    parser.add_argument("--tools-dir", type=Path, default=DEFAULT_TOOLS)
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        target = safe_local(args.receipt)
        if target.parent != ROOT / "artifacts/autoresearch" or not target.name.startswith("stage132a_") or target.suffix != ".json":
            raise ReleaseError("Receipt must be a Stage132A autoresearch JSON")
        receipt = build_dual_release(output_dir=args.output_dir, tools_dir=args.tools_dir, work_dir=args.work_dir, overwrite=args.force)
        target.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    except (ReleaseError, OSError, subprocess.SubprocessError) as error:
        print(f"Stage132A build failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"receipt": target.relative_to(ROOT).as_posix(), "status": receipt["status"],
                      "factory_sha256": receipt["outputs"][FACTORY_NAME]["sha256"],
                      "sysupgrade_sha256": receipt["outputs"][SYSUPGRADE_NAME]["sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
