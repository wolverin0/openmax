"""TFTP regression tests: fake sockets only, never device or power access."""

import contextlib
import io
import hashlib
import socket
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from safety.recovery import urescue_push as recovery


HOST = "192.0.2.20"
SERVER = (HOST, 43123)


def ack(block, source=SERVER):
    return struct.pack(">HH", 4, block), source


class FakeSocket:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.sent = []
        self.closed = False

    def settimeout(self, timeout):
        self.timeout = timeout

    def sendto(self, packet, destination):
        self.sent.append((packet, destination))

    def recvfrom(self, size):
        reply = next(self.replies, socket.timeout("simulated silence"))
        if isinstance(reply, Exception):
            raise reply
        return reply

    def close(self):
        self.closed = True


class TestUrescueSafety(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="fmx-urescue-test-")
        self.addCleanup(directory.cleanup)
        self.image = Path(directory.name) / "fixture.bin"
        self.image.write_bytes(b"UBNT" + bytes(32))

    def upload(self, replies):
        fake = FakeSocket(replies)
        self.addCleanup(lambda: self.assertTrue(fake.closed))
        return fake, patch.object(recovery.socket, "socket", return_value=fake)

    def image_digest(self):
        return hashlib.sha256(self.image.read_bytes()).hexdigest()

    def put_fixture(self, host):
        return recovery.tftp_put(self.image, host, expected_sha256=self.image_digest())

    def test_missing_malformed_or_wrong_digest_never_opens_socket(self):
        for digest in [None, "", "abc", "g" * 64, "0" * 64]:
            with self.subTest(digest=digest), patch.object(recovery.socket, "socket") as factory:
                with self.assertRaises(ValueError):
                    recovery.tftp_put(self.image, HOST, expected_sha256=digest)
                factory.assert_not_called()

    def test_raw_uimage_rejected_even_with_matching_digest(self):
        self.image.write_bytes(b"\x27\x05\x19\x56" + bytes(64))
        with patch.object(recovery.socket, "socket") as factory:
            with self.assertRaisesRegex(ValueError, "raw uImage"):
                self.put_fixture(HOST)
            factory.assert_not_called()

    def test_cli_invalid_digest_is_refused_before_any_probe_or_upload(self):
        for digest in [None, "bad", "0" * 64]:
            args = ["urescue_push.py", "--image", str(self.image), "--yes"]
            if digest is not None:
                args += ["--expect-sha256", digest]
            with self.subTest(digest=digest), patch.object(recovery.sys, "argv", args), \
                    patch.object(recovery, "ping_ok") as ping, \
                    patch.object(recovery.socket, "socket") as factory, \
                    contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(recovery.main(), 3)
                ping.assert_not_called()
                factory.assert_not_called()

    def test_file_replaced_during_confirmation_is_not_sent(self):
        # Before the repair this returned 0 and sent replacement bytes under the old digest.
        args = ["urescue_push.py", "--image", str(self.image), "--device-ip", HOST,
                "--expect-sha256", self.image_digest()]

        def confirm(_):
            self.image.write_bytes(b"UBNT-different-fixture")
            return "YES"

        with patch.object(recovery.sys, "argv", args), \
                patch.object(recovery, "ping_ok", return_value=True), \
                patch("builtins.input", side_effect=confirm), \
                patch.object(recovery.socket, "socket") as factory, \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(recovery.main(), 5)
        factory.assert_not_called()

    def test_file_change_after_validation_cannot_change_payload(self):
        approved = self.image.read_bytes()
        digest = self.image_digest()
        fake = FakeSocket([ack(0), ack(1)])

        def socket_factory(*_):
            self.image.write_bytes(b"UBNT-replaced-after-validation")
            return fake

        with patch.object(recovery.socket, "socket", side_effect=socket_factory), \
                contextlib.redirect_stdout(io.StringIO()):
            recovery.tftp_put(self.image, HOST, expected_sha256=digest)
        self.assertEqual(fake.sent[1][0][4:], approved)
        self.assertTrue(fake.closed)

    def test_probe_silence_is_not_urescue_confirmation(self):
        fake = FakeSocket([socket.timeout("simulated silence")])
        with patch.object(recovery, "tcp_open", return_value=False), \
                patch.object(recovery, "ping_ok", return_value=True), \
                patch.object(recovery.socket, "socket", return_value=fake):
            self.assertFalse(recovery.is_in_urescue(HOST))
        self.assertTrue(fake.closed)
        self.assertEqual(len(fake.sent), 1)
        self.assertEqual(fake.sent[0][0][:2], b"\x00\x01")

    def test_missing_final_ack_is_unknown_and_not_retried(self):
        fake, transport = self.upload([ack(0), socket.timeout("simulated lost final ACK")])
        with transport, self.assertRaisesRegex(RuntimeError, "UNKNOWN"):
            self.put_fixture(HOST)
        self.assertEqual(len(fake.sent), 2)

    def test_wrq_timeout_is_not_retried(self):
        fake, transport = self.upload([socket.timeout("simulated WRQ timeout")])
        with transport, self.assertRaises(RuntimeError):
            self.put_fixture(HOST)
        self.assertEqual(len(fake.sent), 1)

    def test_mid_transfer_timeout_is_not_retried(self):
        self.image.write_bytes(b"UBNT" + bytes(509))
        fake, transport = self.upload([ack(0), socket.timeout("simulated DATA timeout")])
        with transport, self.assertRaises(RuntimeError):
            self.put_fixture(HOST)
        self.assertEqual(len(fake.sent), 2)

    def test_ack_zero_from_wrong_host_is_rejected(self):
        fake, transport = self.upload([ack(0, ("192.0.2.99", 43123)), ack(1)])
        with transport, self.assertRaises(RuntimeError):
            self.put_fixture(HOST)
        self.assertEqual(len(fake.sent), 1)

    def test_data_ack_from_wrong_transfer_port_is_rejected(self):
        fake, transport = self.upload([ack(0), ack(1, (HOST, 43124))])
        with transport, self.assertRaises(RuntimeError):
            self.put_fixture(HOST)
        self.assertEqual(len(fake.sent), 2)

    def test_wrong_ack_block_is_rejected_without_resend(self):
        fake, transport = self.upload([ack(0), ack(0)])
        with transport, self.assertRaises(RuntimeError):
            self.put_fixture(HOST)
        self.assertEqual(len(fake.sent), 2)

    def test_ack_zero_wrong_block_or_invalid_port_is_rejected(self):
        for reply in [ack(1), ack(0, (HOST, 0))]:
            with self.subTest(reply=reply):
                fake, transport = self.upload([reply])
                with transport, self.assertRaises(RuntimeError):
                    self.put_fixture(HOST)
                self.assertEqual(len(fake.sent), 1)

    def test_malformed_packets_are_rejected_at_each_phase(self):
        for packet in [b"", b"\x00", b"\x00\x04\x00", b"\x00\x04\x00\x00extra",
                       b"\x00\x05\x00\x02", b"\x00\x03\x00\x01"]:
            for during_data in [False, True]:
                with self.subTest(packet=packet, during_data=during_data):
                    replies = ([ack(0)] if during_data else []) + [(packet, SERVER)]
                    fake, transport = self.upload(replies)
                    with transport, self.assertRaisesRegex(RuntimeError, "UNKNOWN"):
                        self.put_fixture(HOST)
                    self.assertEqual(len(fake.sent), 2 if during_data else 1)

    def test_vendor_rejection_is_not_suppressed_or_retried(self):
        packet = struct.pack(">HH", 5, 2) + b"Firmware check failed\x00"
        for during_data in [False, True]:
            with self.subTest(during_data=during_data):
                replies = ([ack(0)] if during_data else []) + [(packet, SERVER)]
                fake, transport = self.upload(replies)
                with transport, self.assertRaisesRegex(RuntimeError, "Firmware check failed"):
                    self.put_fixture(HOST)
                self.assertEqual(len(fake.sent), 2 if during_data else 1)

    def test_socket_error_is_unknown_and_closes_socket(self):
        fake, transport = self.upload([ack(0), ConnectionResetError("simulated reset")])
        with transport, self.assertRaisesRegex(RuntimeError, "UNKNOWN"):
            self.put_fixture(HOST)
        self.assertEqual(len(fake.sent), 2)

    def test_acknowledged_partial_last_block_uses_selected_transfer_port(self):
        fake, transport = self.upload([ack(0), ack(1)])
        output = io.StringIO()
        with transport, contextlib.redirect_stdout(output):
            self.put_fixture(HOST)
        self.assertEqual(fake.sent[0][1], (HOST, recovery.TFTP_PORT))
        self.assertEqual(fake.sent[1], (b"\x00\x03\x00\x01" + self.image.read_bytes(), SERVER))
        self.assertIn("recovery are NOT verified", output.getvalue())

    def test_exact_block_size_requires_acknowledged_zero_length_last_block(self):
        self.image.write_bytes(b"UBNT" + bytes(508))
        fake, transport = self.upload([ack(0), ack(1), ack(2)])
        with transport:
            self.put_fixture(HOST)
        self.assertEqual(len(fake.sent), 3)
        self.assertEqual(fake.sent[2], (b"\x00\x03\x00\x02", SERVER))

    def test_rrq_reply_is_not_authenticated_bootloader_identity(self):
        fake = FakeSocket([(b"\x00\x05\x00\x01File not found\x00", SERVER)])
        with patch.object(recovery, "tcp_open", return_value=False), \
                patch.object(recovery, "ping_ok", return_value=True), \
                patch.object(recovery.socket, "socket", return_value=fake):
            self.assertFalse(recovery.is_in_urescue(HOST))
        self.assertEqual(len(fake.sent), 1)
        self.assertEqual(fake.sent[0][0][:2], b"\x00\x01")

    def test_invalid_target_ip_never_opens_socket(self):
        with patch.object(recovery.socket, "socket") as factory, self.assertRaises(ValueError):
            self.put_fixture("not-an-ip")
        factory.assert_not_called()

    def test_cli_missing_ack_returns_nonzero_without_success_message(self):
        fake, transport = self.upload([ack(0), socket.timeout("lost final ACK")])
        output, errors = io.StringIO(), io.StringIO()
        args = ["urescue_push.py", "--image", str(self.image), "--device-ip", HOST, "--yes",
                "--expect-sha256", self.image_digest()]
        with transport, patch.object(recovery.sys, "argv", args), \
                patch.object(recovery, "ping_ok", return_value=True), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(recovery.main(), 5)
        self.assertIn("UNKNOWN", errors.getvalue())
        self.assertNotIn("delivery acknowledged", output.getvalue())
        self.assertEqual(len(fake.sent), 2)

    def test_cli_probe_timeout_returns_nonzero_and_never_sends_wrq(self):
        fake = FakeSocket([socket.timeout("silence")])
        args = ["urescue_push.py", "--probe-only", "--device-ip", HOST]
        with patch.object(recovery.sys, "argv", args), \
                patch.object(recovery, "tcp_open", return_value=False), \
                patch.object(recovery, "ping_ok", return_value=True), \
                patch.object(recovery.socket, "socket", return_value=fake), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(recovery.main(), 1)
        self.assertEqual(len(fake.sent), 1)
        self.assertEqual(fake.sent[0][0][:2], b"\x00\x01")

    def test_watch_ping_without_os_does_not_certify_recovery(self):
        output = io.StringIO()
        with patch.object(recovery, "tcp_open", return_value=False), \
                patch.object(recovery, "ping_ok", return_value=True), \
                patch.object(recovery.time, "time", side_effect=[0, 0, 2]), \
                patch.object(recovery.time, "sleep"), \
                patch.object(recovery.socket, "socket") as factory, \
                contextlib.redirect_stdout(output):
            self.assertFalse(recovery.watch_for_urescue(HOST, seconds=1))
        factory.assert_not_called()
        self.assertIn("UNKNOWN", output.getvalue())
        self.assertNotIn("UNIT IS IN URESCUE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
