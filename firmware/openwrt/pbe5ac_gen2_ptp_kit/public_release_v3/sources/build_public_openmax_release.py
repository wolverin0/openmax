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
V3_RELEASE = KIT / "public_release_v3"
V3_WORK = ROOT / "artifacts/verification/stage144a_build"
V3_RECEIPT = ROOT / "artifacts/autoresearch/stage144a_public_wa_4board_release_v3_receipt.json"
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
    "lap-120": {"profile": "ubnt,lap-120", "board_id": "0xe7f5", "board_ids": ["0xe7f5", "0xe8e5"],
        "dtb_sha256": "ac2240514ca30717ea81cdae2860dd93b5d3a9240722a4a9ce8b4a14be19387e",
        "base_prefix": "openwrt-24.10.4-ath79-generic-ubnt_lap-120-squashfs-",
        "hashes": {"factory": "943d812c40e8f1e6bfb71b32b12395fdd480b62318bc537c7687f8affa9378c0",
                   "sysupgrade": "cc01cbb3e441c8bb801bbae8b64ea6352e571dee0ef6204d95c6bd80e2a975f1"}},
    "nanostation-ac-loco": {"profile": "ubnt,nanostation-ac-loco", "board_id": "0xe7f7", "board_ids": ["0xe7f7", "0xe7fa"],
        "dtb_sha256": "8ac4ab47a0cabd7a7cee5f9a3046cee205dbb3311f8b9c820e0c4cd87fbcdfa8",
        "base_prefix": "openwrt-24.10.4-ath79-generic-ubnt_nanostation-ac-loco-squashfs-",
        "hashes": {"factory": "a7bb8db87083e04695d757ed6adc5aae481438f4191316c2eb90045f191f6443",
                   "sysupgrade": "390ae90a2d09b0cba27e3853b14a16e739e5e3610d1e2451116d73470106892e"}},
}
ROM_SHA256 = "8566fb1c104b61bdb645fc17ba28d6c0ea1bd738e2d05dc8a935464d872a1ce5"
TEB_SHA256 = "3e3d812ff0d4a2fd1a1f9c1257a9356058ac439108e3c27ef6b11d944b696868"
V3_SHA256 = "fe4f730fccaa68848a70c952e40c0438b32d413993f22887a0e72fed5eebaae6"
CHAMPION_SOURCE_SHA256 = "f3ce5bab92280ce99be09bedaf6cc5316b5249aadd3349040c13901365e59f22"
CHAMPION_BODY_SHA256 = "6a6756562eb44889d638ae6079d9632a82e2094287d7f2bf67ab90894a807f2d"
V3_WORDS = ((0x37580, 0x30640008), (0x37584, 0x1080000b), (0x37588, 0x3c010008),
    (0x3758c, 0x00612025), (0x37590, 0xe0440074), (0x37594, 0x1080fff9),
    (0x37598, 0x7c6304c0), (0x3759c, 0x14600005), (0x375a0, 0x2445076c),
    (0x375a4, 0x8e22000c), (0x375b0, 0x24060820), (0x375b4, 0x1000f91c), (0x375b8, 0x24070004))
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


def rebuild_images(factory_template, sysupgrade_template, squashfs, profile="ubnt,powerbeam-5ac-gen2", release_v3=False):
    factory, original = parse_factory(factory_template), parse_sysupgrade(sysupgrade_template, profile)
    if factory["payload"] != original["payload"]:
        raise ReleaseError("Base factory/sysupgrade payloads disagree")
    inspect_squashfs(squashfs)
    body = original["payload"][:ROOTFS_OFFSET] + squashfs
    body += b"\xff" * (-len(body) % 0x10000) + b"\xde\xad\xc0\xde"
    if len(body) > min(PARTITION_LIMIT, CONSERVATIVE_IMAGE_LIMIT):
        raise ReleaseError("Public image exceeds board capacity")
    meta = copy(original["metadata"])
    meta["openmax"] = {"release": "public-v3" if release_v3 else "public-r1",
                       "mac80211_sha256": V3_SHA256 if release_v3 else TEB_SHA256, "runtime_validated": False}
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


def patch_v3(original):
    patched = bytearray(patch_teb(original))
    for offset, word in V3_WORDS:
        struct.pack_into(">I", patched, offset, word)
    if sha256(patched) != V3_SHA256:
        raise ReleaseError("Reproduced authorized-gated v3 module hash mismatch")
    return bytes(patched)


def verify_module(patched, original, release_v3=False):
    expected = V3_SHA256 if release_v3 else TEB_SHA256
    reproduce = patch_v3 if release_v3 else patch_teb
    if len(patched) != 815640 or sha256(patched) != expected or reproduce(original) != patched:
        raise ReleaseError("Module pin/reproduction mismatch")
    if _elf_sections(patched).get(".gnu.linkonce.this_module", (0, 0))[1] != 352:
        raise ReleaseError("Module layout ABI mismatch")
    if b"vermagic=6.6.110 mod_unload MIPS32_R2 32BIT \0" not in patched or b"license=GPL\0" not in patched:
        raise ReleaseError("Module vermagic/license mismatch")
    changed = [i for i, (a, b) in enumerate(zip(original, patched)) if a != b]
    allowed = lambda i: 0x33c88 <= i < 0x33cdc or (release_v3 and any(off <= i < off + 4 for off, _ in V3_WORDS))
    if len(changed) != (113 if release_v3 else 71) or not all(allowed(i) for i in changed):
        raise ReleaseError("Unexpected module changes")
    return {"sha256": expected, "size_bytes": len(patched), "original_sha256": ROM_SHA256,
            "vermagic": "6.6.110 mod_unload MIPS32_R2 32BIT", "module_layout_bytes": 352,
            "elf": "ELF32 BE MIPS", "changed_bytes": len(changed), "patch_reproduced": True,
            "ethertype": "0x6558", "authorized_gated_4addr_event": release_v3,
            "additional_v3_instruction_count": len(V3_WORDS) if release_v3 else 0,
            "hardware_execution_verified": False}


def build_public_champion(source=None):
    # Held R1..R12 source, not a concurrently mutable future-stage champion.
    source = source if source is not None else safe_local(KIT / "public_assets/99-fmx-wa-universal-champion.r1-r12.source.txt").read_bytes()
    if sha256(source) != CHAMPION_SOURCE_SHA256:
        raise ReleaseError("Latest champion source pin mismatch")
    pairs = re.findall(r'^([A-Z0-9_]+)="\$\{\1:-([^}]+)\}"$', source.decode("ascii"), re.M)
    defaults = {name: value for name, value in pairs if not name.startswith("FMX_AIROS_")}
    if len(defaults) != 33 or defaults.get("FMX_AP_FQ_QUANTUM") != "3028" or defaults.get("FMX_STA_FQ_QUANTUM") != "1514":
        raise ReleaseError("Unexpected champion defaults")
    body = safe_local(KIT / "public_assets/wa_champion_openwrt_body.sh").read_bytes()
    if sha256(body) != CHAMPION_BODY_SHA256:
        raise ReleaseError("Public champion body pin mismatch")
    head = "#!/bin/sh\n# Public OpenWrt-only adaptation of pinned Stage140A R1..R12 configured profile.\n"
    head += "# Bench settings are not proven defaults for every device or RF link.\n"
    head += "".join(f"{name}='{value}'\n" for name, value in defaults.items())
    return head.encode("ascii") + body


def public_payloads(profile="ubnt,powerbeam-5ac-gen2", release_v3=False):
    if profile not in {b["profile"] for b in BOARDS.values()}:
        raise ReleaseError("Unknown public board profile")
    result = {"etc/uci-defaults/99-openmax-public": (BOOTSTRAP, 0o755),
            "usr/sbin/fmx_pbe5ac_admitter.sh": (ADMITTER, 0o755),
            "etc/init.d/openmax-admitter": (SERVICE, 0o755),
            "etc/openmax/qos-defaults.conf": (QOS_POLICY, 0o644),
            "etc/openmax-release": (("OPENMAX_RELEASE='public-r1'\nOPENMAX_BASE='OpenWrt 24.10.4'\nOPENMAX_PROFILE='" + profile + "'\n").encode(), 0o644)}
    if release_v3:
        result["etc/openmax-release"] = (result["etc/openmax-release"][0].replace(b"public-r1", b"public-v3"), 0o644)
        result["etc/uci-defaults/99-openmax-public"] = (BOOTSTRAP.replace(b"exit 0\n", b"/etc/init.d/openmax-champion enable\nexit 0\n"), 0o755)
        result["etc/hotplug.d/net/99-fmx-wa-universal-champion"] = (build_public_champion(), 0o755)
        result["etc/openmax/champion.conf"] = (b"# Experimental R1..R12 profile; opt in after wired setup.\nenabled=0\n", 0o644)
        result["etc/init.d/openmax-champion"] = (b"#!/bin/sh /etc/rc.common\nSTART=96\nstart() {\n ACTION=ifup /etc/hotplug.d/net/99-fmx-wa-universal-champion\n}\n", 0o755)
        result["etc/openmax/qos-defaults.conf"] = (b"# public-v3: upstream timing by default; opt-in R1..R12 queue profile.\n# AP quantum3028 / STA1514; known bench throughput/latency tradeoff.\n# No country/power/channel/coverage/beacon/GI overwrite.\n# Raw requested/getter observations: /var/run/openmax-champion/status.\n", 0o644)
    return result


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


def audit_tar(path, profile="ubnt,powerbeam-5ac-gen2", release_v3=False):
    entries, findings, public = _tar_entries(path), [], public_payloads(profile, release_v3)
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


def _write_public_tar(stock_tar, target_tar, module, profile="ubnt,powerbeam-5ac-gen2", release_v3=False):
    original = _tar_entries(stock_tar)
    if MODULE_PATH not in original:
        raise ReleaseError("Base module absent")
    module_check = verify_module(module, original[MODULE_PATH][1], release_v3)
    additions = public_payloads(profile, release_v3)
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
    check = audit_tar(target_tar, profile, release_v3)
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


def _source_notice(release_v3=False):
    notice = b'''# OpenMAX public-r1 sources and notices
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
    if release_v3:
        notice = notice.replace(b"public-r1", b"public-v3").replace(
            b"Separate official ubnt,powerbeam-5ac-gen2 and ubnt,litebeam-ac-gen2 base images.",
            b"Separate official PowerBeam/LiteBeam Gen2, LAP-120 and NanoStation AC Loco base images.")
        notice = notice.replace(b"21-instruction patch", b"21-instruction TEB plus 13-instruction authorized-gated event patch")
        notice += b"\nPublic champion is an OpenWrt-only adaptation, opt-in, with no airOS or RF actuation.\nThe standalone public-v3 guide describes benchmark qualifications and unchanged regulatory choices.\n"
    return notice


def build_release(*, root=ROOT, output_dir=None, tools_dir=DEFAULT_TOOLS, work_dir=DEFAULT_WORK,
                  module_path=None, guide_path=None, overwrite=False, board="pbe5ac-gen2", _defer=False,
                  release_v3=False):
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
    module_name = "mac80211_teb_4addr_v3_6.6.110.ko" if release_v3 else "mac80211_teb_6.6.110.ko"
    module_pin = V3_SHA256 if release_v3 else TEB_SHA256
    module = safe_local(module_path or kit / module_name).read_bytes()
    if sha256(module) != module_pin:
        raise ReleaseError("TEB module pin mismatch")
    guide = safe_local(guide_path or root / "docs" / ("OPENMAX_WA_4BOARD_PUBLIC_V3_RELEASE_GUIDE.md" if release_v3 else GUIDE_NAME)).read_bytes()
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
    tar_audit = _write_public_tar(stock_tar, public_tar, module, profile, release_v3)
    with public_tar.open("rb") as handle:
        _run_tool([tools["tar2sqfs"], "-f", "-q", "-s", "-c", "xz", "-b", "262144", "-j", "1",
                   "-k", "-d", f"uid=0,gid=0,mode=0755,mtime={SOURCE_DATE_EPOCH}", public_sqfs], stdin=handle)
    with reread_tar.open("wb") as handle:
        _run_tool([tools["sqfs2tar"], "-r", ".", "-L", "-s", public_sqfs], stdout=handle)
    reread = audit_tar(reread_tar, profile, release_v3)
    if reread["inventory"] != tar_audit["inventory"]:
        raise ReleaseError("Repacked rootfs content/ownership/mode mismatch")
    out_factory, out_sys = rebuild_images(factory, sysimage, public_sqfs.read_bytes(), profile, release_v3)
    rebuilt = parse_sysupgrade(out_sys, profile)
    if rebuilt["payload"][:ROOTFS_OFFSET] != parsed["payload"][:ROOTFS_OFFSET]:
        raise ReleaseError("Kernel prefix changed")
    if inspect_board_kernel(rebuilt["payload"], board) != board_kernel:
        raise ReleaseError("Board kernel readback changed")
    factory_name = f"openwrt-24.10.4-ubnt-{board}-openmax-public-factory.bin"
    sys_name = f"openwrt-24.10.4-ubnt-{board}-openmax-public-sysupgrade.bin"
    guide_name = "OPENMAX_WA_4BOARD_PUBLIC_V3_RELEASE_GUIDE.md" if release_v3 else GUIDE_NAME
    payloads = {factory_name: out_factory, sys_name: out_sys, guide_name: guide,
                "SOURCE_AND_LICENSES.md": _source_notice(release_v3),
                "sources/build_public_openmax_release.py": Path(__file__).read_bytes(),
                "sources/public_assets/COPYING.GPL-2.0": license_text,
                "modules/" + module_name: module}
    if release_v3:
        payloads["sources/public_assets/wa_champion_openwrt_body.sh"] = safe_local(kit / "public_assets/wa_champion_openwrt_body.sh").read_bytes()
        payloads["sources/public_assets/99-fmx-wa-universal-champion.r1-r12.source.txt"] = safe_local(kit / "public_assets/99-fmx-wa-universal-champion.r1-r12.source.txt").read_bytes()
        payloads["sources/99-fmx-wa-universal-champion.public.sh"] = build_public_champion()
    for name, (data, _mode) in public_payloads(profile, release_v3).items():
        payloads["sources/public_payloads/" + board + "/" + name] = data
    sums = _checksum_text(payloads)
    if not _defer:
        _publish_bundle(output, payloads, overwrite)
    inventory_path = work / "rootfs_inventory.json"
    inventory_path.write_text(json.dumps(reread, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema_version": 1, "stage": "144A" if release_v3 else "117A", "status": "LOCAL_PUBLIC_CANDIDATES_BUILT_NOT_HARDWARE_VALIDATED",
        "board_profile": profile, "board_id": spec["board_id"],
        "board_id_evidence": "Operator hardware catalog; not encoded by the shared WA factory header",
        "openwrt_version": "24.10.4", "kernel": "6.6.110",
        "board_ids": spec.get("board_ids", [spec["board_id"]]),
        "inputs": {"factory_sha256": pins["factory"], "sysupgrade_sha256": pins["sysupgrade"],
                   "module_sha256": module_pin, "private_preconfigs_imported": False,
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
            "stock_regular_content_preserved_except": [MODULE_PATH], "modified_files": sorted(public_payloads(profile, release_v3)) + [MODULE_PATH],
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
    if release_v3:
        receipt["release"] = "public-v3"
        receipt["defaults"].update({"champion_enabled": False, "champion_opt_in_required": True,
            "queue_policy": "Upstream timing until opt-in to experimental R1..R12 configured queue profile",
            "champion_ap_quantum": 3028, "champion_sta_quantum": 1514,
            "champion_source_sha256": CHAMPION_SOURCE_SHA256,
            "champion_public_sha256": sha256(build_public_champion()), "airOS_fallback_removed": True,
            "radio_configuration_preserved": True})
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
    for board in ("pbe5ac-gen2", "lbe5ac-gen2"):
        receipt, files = build_release(root=root, output_dir=output, tools_dir=tools_dir,
            work_dir=work / board, overwrite=overwrite, board=board, _defer=True)
        for name, data in files.items():
            if name in payloads and payloads[name] != data:
                raise ReleaseError("Conflicting shared release asset")
            payloads[name] = data
        boards[board] = receipt
    # Firmware prefixes are board-specific; a relabeled common kernel is forbidden.
    prefixes = [parse_sysupgrade(payloads[f"openwrt-24.10.4-ubnt-{board}-openmax-public-sysupgrade.bin"],
                BOARDS[board]["profile"])["payload"][:ROOTFS_OFFSET] for board in boards]
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


def champion_evidence(root=ROOT):
    pins = {
        "stage123a_live_wa_qca9882_deep_autoresearch.json": "88e98553de6e30d223fbc08479359e00fe544a467423c6e3d7d88a4bf79e535e",
        "stage135a_live_wa_round4_6_autoresearch.json": "8c1f7f26f8798fbc169c91285aab3f85eb57a80a351e1a9e71ae07b69c6bd81d",
        "stage139a_live_wa_round7_9_autoresearch.json": "d95c701b67412af06b4b160aeb06f1d8bb5f704fdc45c02b75a8508ba61d37e6",
        "stage140a_live_wa_round10_12_champion_headtohead.json": "eb3afa4f3e72d4f09a4fc2445ebc89218401a680907c28809a3afe16c703948c"}
    rounds, sources, last = [], {}, None
    for name, pin in pins.items():
        data = safe_local(Path(root) / "artifacts/autoresearch" / name).read_bytes()
        if sha256(data) != pin:
            raise ReleaseError("R1..R12 saved evidence pin mismatch")
        last = json.loads(data.decode("utf-8-sig"))
        sources[name] = pin
        for record in last["rounds"]:
            if [w["window"] for w in record["windows"]] != ["A1", "B1", "A2", "B2"]:
                raise ReleaseError("Saved counterbalanced window sequence mismatch")
            rounds.append({key: value for key, value in record.items()
                           if key in ("round_id", "decision", "arm_a_mean_goodput_mbps", "arm_b_mean_goodput_mbps",
                                      "arm_a_mean_p95_rtt_ms", "arm_b_mean_p95_rtt_ms", "arm_a_mean_p99_rtt_ms", "arm_b_mean_p99_rtt_ms")})
    if len(rounds) != 12 or [int(r["round_id"].split("-R")[-1]) for r in rounds] != list(range(1, 13)):
        raise ReleaseError("Saved round identities/count mismatch")
    state = last["final_applied_state"]
    observations = {}
    for side in ("ap", "cpe"):
        raw = state[side + "_readback_raw"]
        lines = raw.splitlines()
        observations[side] = {"raw": raw, "tcp_limit_output_bytes": int(lines[-2]), "netdev_max_backlog": int(lines[-1])}
    return {"sources": sources, "source_champion_sha256": CHAMPION_SOURCE_SHA256,
        "round_count": 12, "window_count": 48, "rounds": rounds,
        "configured_final": state["configured"], "saved_getters": observations,
        "getter_mismatches": ["tcp_limit_output_bytes: configured65536 vs observed98304",
                              "netdev_max_backlog: configured1500 vs observed1000"],
        "qualification": ["48 saved windows span twelve different comparisons on one LAP-to-Loco link",
            "R12 RETAIN_ARM_A; aggregate goodput improves while p95/p99 regress against stock",
            "Short windows/small RTT sample counts do not establish stable tail latency or four-board physical acceptance",
            "Configured fields copied into knob_readback are not independent measured getters",
            "This public adaptation preserves user RF settings and omits the airOS implementation"]}


def _verify_emitted_v3(root, board, receipt, tools):
    profile = BOARDS[board]["profile"]
    factory_path = root / receipt["outputs"][f"openwrt-24.10.4-ubnt-{board}-openmax-public-factory.bin"]["path"]
    sys_path = root / receipt["outputs"][f"openwrt-24.10.4-ubnt-{board}-openmax-public-sysupgrade.bin"]["path"]
    factory, image = factory_path.read_bytes(), sys_path.read_bytes()
    body = parse_sysupgrade(image, profile)["payload"]
    if parse_factory(factory)["payload"] != body:
        raise ReleaseError("Emitted factory/sysupgrade mismatch")
    used = inspect_squashfs(body[ROOTFS_OFFSET:])["bytes_used"]
    verification = receipt["rootfs_verification"]
    work = (root / verification["public_tar_path"]).parent
    sqfs, tar = work / "emitted-image.squashfs", work / "emitted-image.tar"
    carved = body[ROOTFS_OFFSET:ROOTFS_OFFSET + used]
    sqfs.write_bytes(carved)
    with tar.open("wb") as handle:
        _run_tool([tools["sqfs2tar"], "-r", ".", "-L", "-s", sqfs], stdout=handle)
    audit = audit_tar(tar, profile, True)
    inventory = json.loads((root / verification["inventory_path"]).read_text(encoding="utf-8"))
    if audit["inventory"] != inventory["inventory"]:
        raise ReleaseError("Emitted image inventory mismatch")
    verification.update({"emitted_tar_path": tar.relative_to(root).as_posix(), "emitted_tar_sha256": sha256(tar.read_bytes()),
        "emitted_sysupgrade_sha256": sha256(image), "emitted_factory_sha256": sha256(factory),
        "emitted_rootfs_sha256": sha256(carved), "emitted_rootfs_bytes_used": used,
        "emitted_inventory_equal": True, "native_readback_exit_code": 0})


def build_wa_v3_release(*, root=ROOT, output_dir=None, tools_dir=DEFAULT_TOOLS,
                        work_dir=V3_WORK, overwrite=False):
    root = safe_local(root)
    kit = root / "firmware/openwrt/pbe5ac_gen2_ptp_kit"
    output, work = safe_local(output_dir or kit / "public_release_v3"), safe_local(work_dir)
    if not output.name.startswith("public_release_v3"):
        raise ReleaseError("V3 output must use a dedicated public_release_v3 directory")
    evidence = champion_evidence(root)
    boards, payloads, prefixes = {}, {}, []
    for board in BOARDS:
        receipt, files = build_release(root=root, output_dir=output, tools_dir=tools_dir,
            work_dir=work / board, overwrite=overwrite, board=board, _defer=True, release_v3=True)
        for name, data in files.items():
            if name in payloads and payloads[name] != data:
                raise ReleaseError("Conflicting shared v3 asset")
            payloads[name] = data
        boards[board] = receipt
        prefixes.append(receipt["container_verification"]["board_kernel"]["kernel_prefix_sha256"])
    if len(set(prefixes)) != 4:
        raise ReleaseError("Four board-specific kernels required")
    payloads["BENCHMARK_EVIDENCE_AND_LIMITS.json"] = (json.dumps(evidence, indent=2, allow_nan=False) + "\n").encode()
    _publish_bundle(output, payloads, overwrite)
    tools = _toolchain(tools_dir)
    shared_sums = {"path": (output / "SHA256SUMS").relative_to(root).as_posix(),
                   "sha256": sha256(_checksum_text(payloads).encode())}
    for board, receipt in boards.items():
        _verify_emitted_v3(root, board, receipt, tools)
        receipt["sha256sums"] = shared_sums
    return {"schema_version": 1, "stage": "144A", "release": "public-v3",
        "status": "LOCAL_FOUR_BOARD_V3_CANDIDATES_BUILT_NOT_HARDWARE_VALIDATED",
        "boards": boards, "sha256sums": shared_sums, "champion_evidence": evidence,
        "module_sha256": V3_SHA256, "champion_public_sha256": sha256(build_public_champion()),
        "outputs": {name: {"path": (output / name).relative_to(root).as_posix(), "sha256": sha256(data),
                    "size_bytes": len(data)} for name, data in payloads.items()},
        "board_specific_kernel_prefixes_distinct": True,
        "boundaries": {"radios_contacted": [], "flash_executed": False, "published": False,
                       "hardware_boot_verified": False, "recovery_verified": False}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=V3_RELEASE)
    parser.add_argument("--tools-dir", type=Path, default=DEFAULT_TOOLS)
    parser.add_argument("--work-dir", type=Path, default=V3_WORK)
    parser.add_argument("--receipt", type=Path, default=V3_RECEIPT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        target = safe_local(args.receipt)
        if target.parent != ROOT / "artifacts/autoresearch" or not target.name.startswith("stage144a_") or target.suffix != ".json":
            raise ReleaseError("Receipt must be a Stage144A autoresearch JSON")
        receipt = build_wa_v3_release(output_dir=args.output_dir, tools_dir=args.tools_dir, work_dir=args.work_dir, overwrite=args.force)
        target.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    except (ReleaseError, OSError, subprocess.SubprocessError) as error:
        print(f"Stage144A build failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"receipt": target.relative_to(ROOT).as_posix(), "status": receipt["status"],
                      "factory_sha256": receipt["outputs"][FACTORY_NAME]["sha256"],
                      "sysupgrade_sha256": receipt["outputs"][SYSUPGRADE_NAME]["sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
