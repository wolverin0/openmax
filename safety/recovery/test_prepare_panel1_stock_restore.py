"""Offline restore preparation contract; all inputs are disposable local fixtures."""

import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from safety.recovery import prepare_panel1_stock_restore as builder


class TestPanel1StockPreparation(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fmx-stock-prepare-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "evidence"
        self.output = Path(temporary.name) / "output"
        self.board_dir = self.root / builder.NODE
        self.backup = self.root / builder.BACKUP
        self.board_dir.mkdir(parents=True)
        self.backup.mkdir()
        self.config = b"fixture.private=value-not-for-output\n"
        board = ("board.sysid=0xe8e5\nboard.name=LiteAP AC\nboard.model=LAP-120\n"
                 "board.bom=13-00402-12\nboard.cpurevision=0x00001123\n"
                 "board.hwaddr=020000000001\n")
        (self.board_dir / "board.info").write_text(board)
        self.map_text = "dev:    size   erasesize  name\n" + "".join(
            f'{part}: {size:08x} 00010000 "{name}"\n'
            for part, name, _, size, _ in builder.LAYOUT)
        (self.board_dir / "proc_mtd.txt").write_text(self.map_text)
        (self.board_dir / "system.cfg.orig").write_bytes(self.config + b"original=1\n")
        (self.backup / "system.cfg").write_bytes(self.config)
        kernel = bytearray(b"\xff" * 0x100000)
        payload = bytes(range(128))
        kernel[64:64 + len(payload)] = payload
        kernel[:64] = struct.pack(">7I4B32s", 0x27051956, 0, 123, len(payload), 0x80002000,
                                  0x80002000, zlib.crc32(payload), 5, 5, 2, 3,
                                  b"MIPS Ubiquiti Linux-2.6.32.68")
        self.fix_header_crc(kernel)
        protected, firmware = {}, {}
        for part, _, _, size, is_protected in builder.LAYOUT:
            data = bytes(kernel) if part == "mtd2" else (
                b"hsqs" + bytes(size - 4) if part == "mtd3" else bytes(size))
            directory = self.board_dir if is_protected else self.backup
            (directory / (part + ".bin")).write_bytes(data)
            md5 = hashlib.md5(data).hexdigest()
            metadata = {"bytes": size, "remote_md5": md5, "local_md5": md5}
            if is_protected:
                protected[part] = {**metadata, "match": True}
            else:
                firmware[part] = {**metadata, "expected_bytes": size, "read_rc": 0,
                                  "sha256": builder.sha256(data), "verified": True}
        self.inventory = {"nodes": {builder.NODE: {
            "ip": "192.0.2.20", "board_hwaddr": "020000000001", "board_sysid": "0xe8e5",
            "board_name": "LiteAP AC", "version": "WA.v8.7.25", "mtd_backups": protected}}}
        self.receipt = {"ip": "192.0.2.20", "complete": True, "device_writes": False,
                        "timestamp_utc": "20261018T213146Z", "parts": firmware,
                        "config_sha256": builder.sha256(self.config)}
        self.write_json(builder.INVENTORY, self.inventory)
        self.write_json(builder.RECEIPT, self.receipt)
        self.pins = {name: builder.sha256((self.root / name).read_bytes()) for name in builder.PINS}

    @staticmethod
    def fix_header_crc(kernel):
        kernel[4:8] = bytes(4)
        kernel[4:8] = struct.pack(">I", zlib.crc32(kernel[:64]))

    def write_json(self, relative, value):
        (self.root / relative).write_text(json.dumps(value), encoding="utf-8")

    def repin(self, relative):
        self.pins[relative] = builder.sha256((self.root / relative).read_bytes())

    def refresh_kernel_receipt(self, data):
        (self.backup / "mtd2.bin").write_bytes(data)
        md5 = hashlib.md5(data).hexdigest()
        self.receipt["parts"]["mtd2"].update(
            local_md5=md5, remote_md5=md5, sha256=builder.sha256(data))
        self.write_json(builder.RECEIPT, self.receipt)
        self.repin(builder.RECEIPT)

    def prepare(self):
        return builder.prepare(self.root, self.output, pins=self.pins)

    def refused(self, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_exact_region_excludes_protected_spans_and_pins_private_sources(self):
        manifest = self.prepare()
        image = (self.output / builder.IMAGE_NAME).read_bytes()
        self.assertEqual(image, (self.backup / "mtd2.bin").read_bytes() +
                         (self.backup / "mtd3.bin").read_bytes())
        self.assertEqual(len(image), 0xFB0000 - 0x50000)
        self.assertEqual(manifest["sha256"], builder.sha256(image))
        self.assertEqual(manifest["labels"], builder.LABELS)
        self.assertFalse(manifest["restore_tested"])
        self.assertIsNone(manifest["target_mtd_number_under_openwrt"])
        self.assertFalse(manifest["configuration_snapshots_identical"])
        self.assertEqual(len(manifest["protected_partitions_excluded"]), 4)
        self.assertNotIn("value-not-for-output", json.dumps(manifest))

    def test_existing_output_is_never_overwritten(self):
        self.output.mkdir()
        sentinel = self.output / "existing"
        sentinel.write_text("preserve")
        with self.assertRaisesRegex(ValueError, "refusing overwrite"):
            self.prepare()
        self.assertEqual(sentinel.read_text(), "preserve")

    def test_corrupt_firmware_is_refused_before_output(self):
        (self.backup / "mtd3.bin").write_bytes(bytes(0xE60000))
        self.refused("MD5 mismatch")

    def test_corrupt_protected_backup_is_refused_before_output(self):
        (self.board_dir / "mtd0.bin").write_bytes(b"x" * 0x40000)
        self.refused("MD5 mismatch")

    def test_partition_length_mismatch_is_refused(self):
        (self.backup / "mtd2.bin").write_bytes(b"short")
        self.refused("length mismatch")

    def test_receipt_is_pinned(self):
        self.receipt["parts"]["mtd2"]["verified"] = False
        self.write_json(builder.RECEIPT, self.receipt)
        self.refused("Pinned SHA256 mismatch")

    def test_layout_mismatch_is_refused_even_with_matching_source_pin(self):
        path = self.board_dir / "proc_mtd.txt"
        path.write_text(self.map_text.replace('"kernel"', '"firmware"'))
        self.repin(f"{builder.NODE}/proc_mtd.txt")
        self.refused("layout mismatch")

    def test_wrong_bom_or_sysid_is_refused(self):
        path = self.board_dir / "board.info"
        original = path.read_text()
        for old, new in [("13-00402-12", "13-00402-06"), ("0xe8e5", "0xe7fa")]:
            with self.subTest(field=old):
                path.write_text(original.replace(old, new))
                self.repin(f"{builder.NODE}/board.info")
                self.refused("Exact board identity mismatch")

    def test_identity_must_match_inventory(self):
        path = self.board_dir / "board.info"
        path.write_text(path.read_text().replace("020000000001", "020000000002"))
        self.repin(f"{builder.NODE}/board.info")
        self.refused("does not match inventory")

    def test_missing_source_refuses_without_output(self):
        (self.board_dir / "mtd1.bin").unlink()
        self.refused("Missing regular input")

    def test_unverified_receipt_refuses_even_with_matching_pin(self):
        self.receipt["parts"]["mtd2"]["verified"] = False
        self.write_json(builder.RECEIPT, self.receipt)
        self.repin(builder.RECEIPT)
        self.refused("Unverified firmware backup")

    def test_remote_md5_must_match_local(self):
        self.receipt["parts"]["mtd2"]["remote_md5"] = "0" * 32
        self.write_json(builder.RECEIPT, self.receipt)
        self.repin(builder.RECEIPT)
        self.refused("MD5 mismatch")

    def test_config_must_match_receipt(self):
        (self.backup / "system.cfg").write_bytes(self.config + b"drift=1\n")
        self.repin(f"{builder.BACKUP}/system.cfg")
        self.refused("configuration SHA256 mismatch")

    def test_payload_crc_rejects_corruption_even_when_receipt_matches(self):
        kernel = bytearray((self.backup / "mtd2.bin").read_bytes())
        kernel[64] ^= 1
        self.refresh_kernel_receipt(kernel)
        self.refused("payload CRC mismatch")

    def test_header_crc_rejects_corruption_even_when_receipt_matches(self):
        kernel = bytearray((self.backup / "mtd2.bin").read_bytes())
        kernel[8] ^= 1
        self.refresh_kernel_receipt(kernel)
        self.refused("header CRC mismatch")

    def test_oversized_uimage_payload_is_refused(self):
        kernel = bytearray((self.backup / "mtd2.bin").read_bytes())
        kernel[12:16] = struct.pack(">I", len(kernel))
        self.fix_header_crc(kernel)
        self.refresh_kernel_receipt(kernel)
        self.refused("payload exceeds")


if __name__ == "__main__":
    unittest.main()
