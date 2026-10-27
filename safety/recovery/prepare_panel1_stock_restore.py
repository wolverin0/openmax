#!/usr/bin/env python3
"""Prepare the exact Panel1 stock firmware region offline; never operate a device.

Inputs are pinned held backups, not vendor containers. The output excludes bootloader,
environment, configuration and calibration. It is NOT a TFTP container, NOT SYSUPGRADE
QUALIFIED and NOT RESTORE TESTED. No target partition numbers or write commands are supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import zlib
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
EVIDENCE = REPO / "artifacts/canary_panel1_guarida"
NODE = "AP_Panel1-Guarida"
BACKUP = "stock_ap_readonly_backup_20261018T213146Z"
INVENTORY = "phase1_inventory_and_backups.json"
RECEIPT = f"{BACKUP}/receipt.json"
PINS = {
    INVENTORY: "d02827e720921bb452d70c80c22a2d4d86d9c82d6b55daa67ef84482df55e7cc",
    RECEIPT: "885fc9778f9895716c9a94fed626bb69140305f462cd0ed3fa540740715ea7c9",
    f"{NODE}/board.info": "ea804ca63331c7b9d6aeaaf90100dea0e1bbd11cf4cba12db5b9e834476783ab",
    f"{NODE}/proc_mtd.txt": "9bb3e8ada9301591b17132e57760db7e697be80e830f4514e2cf63f038890891",
    f"{NODE}/system.cfg.orig": "0a059eacb67aa75bec9038470811b5c89f6b8d7fb6ed1b6af9047906a09c1a65",
    f"{BACKUP}/system.cfg": "fc0b1b3fd8d97f423ca0ab079f459f8e251a66b205181531ca54caa6f3a105a7",
}
LAYOUT = (
    ("mtd0", "u-boot", 0x000000, 0x040000, True),
    ("mtd1", "u-boot-env", 0x040000, 0x010000, True),
    ("mtd2", "kernel", 0x050000, 0x100000, False),
    ("mtd3", "rootfs", 0x150000, 0xE60000, False),
    ("mtd4", "cfg", 0xFB0000, 0x040000, True),
    ("mtd5", "EEPROM", 0xFF0000, 0x010000, True),
)
REGION_START, REGION_END = 0x050000, 0xFB0000
IMAGE_NAME = "panel1-stock-wa-v8.7.25-firmware-region.raw.bin"
LABELS = ["NOT TFTP CONTAINER", "NOT SYSUPGRADE QUALIFIED", "NOT RESTORE TESTED"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_board(data: bytes) -> dict:
    result = {}
    for line in data.decode("utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        require(key not in result, "Duplicate board identity key")
        result[key] = value
    expected = {"board.sysid": "0xe8e5", "board.name": "LiteAP AC",
                "board.model": "LAP-120", "board.bom": "13-00402-12",
                "board.cpurevision": "0x00001123"}
    require(all(result.get(k) == v for k, v in expected.items()), "Exact board identity mismatch")
    return result


def validate_layout(data: bytes) -> None:
    lines = data.decode("ascii").splitlines()
    require(bool(lines) and lines[0].split() == ["dev:", "size", "erasesize", "name"],
            "Unexpected stock MTD header")
    actual = []
    for line in lines[1:]:
        match = re.fullmatch(r'(mtd\d+):\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+"([^"]+)"', line)
        require(match is not None, "Malformed stock MTD record")
        actual.append((match[1], match[4], int(match[2], 16), int(match[3], 16)))
    require(actual == [(part, name, size, 0x10000) for part, name, _, size, _ in LAYOUT],
            "Stock MTD layout mismatch")
    cursor = 0
    for _, _, offset, size, _ in LAYOUT:
        require(offset == cursor, "Non-contiguous stock layout")
        cursor += size
    require(cursor == 0x1000000, "Unexpected total stock flash size")


def validate_uimage(kernel: bytes) -> dict:
    require(len(kernel) == 0x100000, "Unexpected kernel partition length")
    fields = struct.unpack(">7I4B32s", kernel[:64])
    magic, header_crc, _, payload_size, load, entry, data_crc, os_id, arch, kind, compression, name = fields
    require(magic == 0x27051956, "Stock kernel uImage magic mismatch")
    header = bytearray(kernel[:64])
    header[4:8] = bytes(4)
    require(zlib.crc32(header) == header_crc, "Stock kernel uImage header CRC mismatch")
    require(0 < payload_size <= len(kernel) - 64, "Stock kernel payload exceeds its partition")
    require(zlib.crc32(kernel[64:64 + payload_size]) == data_crc,
            "Stock kernel uImage payload CRC mismatch")
    require((os_id, arch, kind, compression, load, entry) ==
            (5, 5, 2, 3, 0x80002000, 0x80002000), "Unexpected stock kernel format or address")
    require(name.rstrip(b"\0") == b"MIPS Ubiquiti Linux-2.6.32.68", "Unexpected stock kernel identity")
    return {"header_crc_verified": True, "payload_crc_verified": True,
            "payload_bytes": payload_size, "name": name.rstrip(b"\0").decode("ascii")}


def prepare(evidence: Path, output: Path, *, pins: dict[str, str] | None = None) -> dict:
    """Validate every input before exclusive local output creation; pins may describe test fixtures."""
    pins = PINS if pins is None else pins
    require(set(pins) == set(PINS), "Incomplete or unexpected pinned evidence set")
    require(not output.exists() and not output.is_symlink(), "Output already exists; refusing overwrite")
    blobs, sources = {}, {}

    def read(relative: str) -> bytes:
        path = evidence / relative
        require(path.resolve().is_relative_to(evidence.resolve()), "Input escapes evidence directory")
        require(path.is_file() and not path.is_symlink(), f"Missing regular input: {relative}")
        data = path.read_bytes()
        digest = sha256(data)
        if relative in pins:
            require(digest == pins[relative], f"Pinned SHA256 mismatch: {relative}")
        blobs[relative] = data
        sources[relative] = {"bytes": len(data), "sha256": digest}
        return data

    inventory = json.loads(read(INVENTORY))
    receipt = json.loads(read(RECEIPT))
    node = inventory["nodes"][NODE]
    board = parse_board(read(f"{NODE}/board.info"))
    normalize_mac = lambda value: re.sub(r"[:-]", "", value).upper()
    require(normalize_mac(board.get("board.hwaddr", "")) == normalize_mac(node["board_hwaddr"])
            and re.fullmatch(r"[0-9A-F]{12}", normalize_mac(node["board_hwaddr"])) is not None,
            "Board identity does not match inventory")
    require((node["board_sysid"], node["board_name"], node["version"]) ==
            ("0xe8e5", "LiteAP AC", "WA.v8.7.25"), "Inventory target mismatch")
    require(receipt["ip"] == node["ip"] and receipt["complete"] is True
            and receipt["device_writes"] is False
            and receipt["timestamp_utc"] == "20261018T213146Z", "Backup receipt provenance mismatch")
    validate_layout(read(f"{NODE}/proc_mtd.txt"))

    protected = []
    for part, name, offset, size, is_protected in LAYOUT:
        relative = f"{NODE}/{part}.bin" if is_protected else f"{BACKUP}/{part}.bin"
        data = read(relative)
        metadata = node["mtd_backups"][part] if is_protected else receipt["parts"][part]
        digest = hashlib.md5(data).hexdigest()
        require(len(data) == size == metadata["bytes"], f"Partition length mismatch: {part}")
        require(metadata["remote_md5"] == metadata["local_md5"] == digest,
                f"Partition MD5 mismatch: {part}")
        if is_protected:
            require(metadata["match"] is True, f"Unverified protected backup: {part}")
            protected.append({"stock_source": relative, "name": name, "start": offset,
                              "end_exclusive": offset + size, **sources[relative]})
        else:
            require(metadata["verified"] is True and metadata["read_rc"] == 0
                    and metadata["expected_bytes"] == size, f"Unverified firmware backup: {part}")
            require(sources[relative]["sha256"] == metadata["sha256"],
                    f"Partition SHA256 mismatch: {part}")

    read(f"{NODE}/system.cfg.orig")
    config = read(f"{BACKUP}/system.cfg")
    require(sha256(config) == receipt["config_sha256"], "Stock configuration SHA256 mismatch")
    kernel, rootfs = blobs[f"{BACKUP}/mtd2.bin"], blobs[f"{BACKUP}/mtd3.bin"]
    uimage = validate_uimage(kernel)
    require(rootfs[:4] == b"hsqs", "Stock rootfs SquashFS magic mismatch")
    firmware = kernel + rootfs
    require(len(firmware) == REGION_END - REGION_START, "Firmware region length mismatch")
    require(all(REGION_END <= p["start"] or REGION_START >= p["end_exclusive"] for p in protected),
            "Firmware region intersects protected partition")
    manifest = {
        "status": "OFFLINE_PREPARATION_ONLY", "labels": LABELS,
        "device_operations": False, "flash_authorized": False, "restore_tested": False,
        "image": IMAGE_NAME, "sha256": sha256(firmware), "bytes": len(firmware),
        "firmware_region": {"start": REGION_START, "end_exclusive": REGION_END,
                            "composition": [f"{BACKUP}/mtd2.bin", f"{BACKUP}/mtd3.bin"]},
        "target_mtd_number_under_openwrt": None,
        "board": {key: board[key] for key in ("board.sysid", "board.model", "board.bom",
                                              "board.cpurevision")},
        "stock_version": "WA.v8.7.25", "uimage": uimage,
        "protected_partitions_excluded": protected, "sources": sources,
        "configuration_snapshots_identical": blobs[f"{NODE}/system.cfg.orig"] == config,
        "remaining_gates": ["exact-board installation route", "independent restore rehearsal",
                            "qualified failure recovery", "protected hash readback", "operator approval"],
    }
    encoded_manifest = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    output.mkdir(parents=True, exist_ok=False)
    for name, data in ((IMAGE_NAME, firmware), ("manifest.json", encoded_manifest)):
        path = output / name
        with path.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        require(path.read_bytes() == data, f"Local output readback mismatch: {name}")
        path.chmod(0o444)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=EVIDENCE / "stock_restore_preparation_20261018")
    args = parser.parse_args()
    try:
        manifest = prepare(EVIDENCE, args.output_dir)
    except (ValueError, OSError, KeyError, TypeError, UnicodeError) as error:
        print(f"LOCAL PREPARATION REFUSED: {error}")
        return 2
    print(json.dumps({key: manifest[key] for key in ("status", "image", "bytes", "sha256", "labels")},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
