"""Unit tests for orchestration.rollback.workflow (RollbackManager)."""

import unittest
import hashlib
import tempfile
import time
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from orchestration.power.smart_power import SmartPowerController, MockPowerDriver
from orchestration.rollback.workflow import (
    RecoveryVerification, RollbackManager, RollbackState, RollbackTier, TransferOutcome,
)


class TestRollbackManager(unittest.TestCase):
    def test_same_manager_allows_only_one_concurrent_attempt(self):
        entered, release = Event(), Event()
        calls, validations = [], []
        original_is_file = Path.is_file
        def checked_file(path):
            validations.append(1)
            if len(validations) == 1:
                entered.set()
                release.wait(timeout=2)
            return original_is_file(path)
        def transfer(_):
            calls.append(1)
            return False
        with patch.object(Path, "is_file", checked_file), ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(self.manager.execute_recovery, "fixture", transfer,
                                verify_recovery_fn=self.verifier)
            self.assertTrue(entered.wait(timeout=1))
            second = pool.submit(self.manager.execute_recovery, "fixture", transfer,
                                 verify_recovery_fn=self.verifier)
            try:
                self.assertFalse(second.result(timeout=1).success)
            finally:
                release.set()
            self.assertFalse(first.result(timeout=1).success)
        self.assertEqual(calls, [1])

    def test_uncertain_result_blocks_later_invocation(self):
        transfer = Mock(return_value=False)
        for _ in range(2):
            result = self.manager.execute_recovery("fixture", ssh_sysupgrade_fn=transfer, verify_recovery_fn=self.verifier)
            self.assertFalse(result.success)
        self.assertEqual(transfer.call_count, 1)

    def test_stale_unbound_receipt_cannot_prove_recovery(self):
        result = self.manager.execute_recovery(
            "fixture", ssh_sysupgrade_fn=lambda _: True,
            verify_recovery_fn=Mock(return_value=self.evidence),
        )
        self.assertFalse(result.success)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.image = Path(self.temp.name) / "golden.bin"
        self.image.write_bytes(b"disposable recovery fixture")
        self.driver = MockPowerDriver(initial_state=True)
        self.power = SmartPowerController(
            driver=self.driver,
            min_cooldown_seconds=0.01,
            default_off_duration_seconds=0.01,
        )
        self.manager = RollbackManager(
            target_host="192.168.1.20",
            outlet_id=1,
            golden_image_path=self.image,
            golden_image_sha256=hashlib.sha256(self.image.read_bytes()).hexdigest(),
            power_controller=self.power,
        )
        self.evidence = RecoveryVerification(
            "192.168.1.20", True, True, True, True, True, "fixture-only-postboot-receipt",
        )
        self.verifier = Mock(side_effect=lambda context: replace(
            self.evidence, attempt_id=context.attempt_id, image_sha256=context.image_sha256,
            observed_at=time.time(),
        ))

    def test_successful_tier1_soft_rollback(self):
        def mock_ssh_sysupgrade(p: Path) -> bool:
            return True

        incident = self.manager.execute_recovery(
            failure_reason="Post-flash kernel oops detected in dmesg",
            ssh_sysupgrade_fn=mock_ssh_sysupgrade,
            verify_recovery_fn=self.verifier,
        )

        self.assertTrue(incident.success)
        self.assertEqual(incident.tier_used, RollbackTier.TIER_1_SOFT_SYSUPGRADE)
        self.assertEqual(self.manager.state, RollbackState.RECOVERED)
        self.assertEqual(len(self.manager.history), 1)

    def test_escalation_to_tier2_tftp_recovery(self):
        # SSH fails (e.g. host unreachable or locked)
        def mock_failing_ssh(p: Path) -> TransferOutcome:
            return TransferOutcome.NO_WRITE

        tftp_calls = []
        def mock_tftp_push(p: Path) -> bool:
            tftp_calls.append(p)
            return True

        incident = self.manager.execute_recovery(
            failure_reason="Device completely unreachable after flash",
            ssh_sysupgrade_fn=mock_failing_ssh,
            tftp_push_fn=mock_tftp_push,
            reset_hold_sec=0.01,
            settle_delay_sec=0.01,
            verify_recovery_fn=self.verifier,
        )

        self.assertTrue(incident.success)
        self.assertEqual(incident.tier_used, RollbackTier.TIER_2_POE_TFTP_RECOVERY)
        self.assertEqual(self.manager.state, RollbackState.RECOVERED)
        self.assertEqual(len(tftp_calls), 1)
        self.assertEqual(tftp_calls[0], self.image)

    def test_missing_tftp_does_not_reset_or_report_recovered(self):
        self.power.trigger_tftp_recovery = Mock(return_value=True)
        incident = self.manager.execute_recovery("no real transfer adapter", verify_recovery_fn=self.verifier)
        self.assertFalse(incident.success)
        self.assertEqual(self.manager.state, RollbackState.FAILED)
        self.power.trigger_tftp_recovery.assert_not_called()

    def test_wrong_golden_hash_prevents_any_action(self):
        self.manager.golden_image_sha256 = "0" * 64
        transfer = Mock(return_value=True)
        self.power.trigger_tftp_recovery = Mock(return_value=True)
        incident = self.manager.execute_recovery("fixture", ssh_sysupgrade_fn=transfer, verify_recovery_fn=self.verifier)
        self.assertFalse(incident.success)
        transfer.assert_not_called()
        self.power.trigger_tftp_recovery.assert_not_called()

    def test_verifier_required_before_any_write(self):
        transfer = Mock(return_value=True)
        incident = self.manager.execute_recovery("fixture", ssh_sysupgrade_fn=transfer)
        self.assertFalse(incident.success)
        transfer.assert_not_called()

    def test_delivery_alone_never_proves_recovery(self):
        self.power.trigger_tftp_recovery = Mock(return_value=True)
        for evidence in (True, None, RecoveryVerification(
            "192.168.1.20", True, True, False, True, True, "incomplete-fixture",
        ), RecoveryVerification(
            "different-device", True, True, True, True, True, "wrong-device-fixture",
        )):
            with self.subTest(evidence=evidence):
                self.setUp()
                self.power.trigger_tftp_recovery = Mock(return_value=True)
                incident = self.manager.execute_recovery(
                    "fixture", ssh_sysupgrade_fn=lambda _: True,
                    tftp_push_fn=lambda _: True, verify_recovery_fn=lambda _: evidence,
                )
                self.assertFalse(incident.success)
                self.assertEqual(self.manager.state, RollbackState.FAILED)
        self.power.trigger_tftp_recovery.assert_not_called()

    def test_ambiguous_soft_failure_does_not_escalate(self):
        self.power.trigger_tftp_recovery = Mock(return_value=True)
        transfer = Mock(return_value=False)
        for result in (False, None, "success", TimeoutError("fixture")):
            with self.subTest(result=result):
                self.setUp()
                self.power.trigger_tftp_recovery = Mock(return_value=True)
                soft = Mock(side_effect=result) if isinstance(result, Exception) else Mock(return_value=result)
                incident = self.manager.execute_recovery(
                    "fixture", ssh_sysupgrade_fn=soft, tftp_push_fn=transfer,
                    verify_recovery_fn=self.verifier,
                )
                self.assertFalse(incident.success)
        transfer.assert_not_called()
        self.power.trigger_tftp_recovery.assert_not_called()

    def test_image_change_prevents_escalation(self):
        self.power.trigger_tftp_recovery = Mock(return_value=True)
        def soft(_):
            self.image.write_bytes(b"changed fixture")
            return TransferOutcome.NO_WRITE
        incident = self.manager.execute_recovery(
            "fixture", ssh_sysupgrade_fn=soft, tftp_push_fn=lambda _: True,
            verify_recovery_fn=self.verifier,
        )
        self.assertFalse(incident.success)
        self.power.trigger_tftp_recovery.assert_not_called()

    def test_tftp_needs_postboot_verification(self):
        self.power.trigger_tftp_recovery = Mock(return_value=True)
        self.verifier.side_effect = None
        self.verifier.return_value = False
        incident = self.manager.execute_recovery(
            "fixture", tftp_push_fn=lambda _: True, verify_recovery_fn=self.verifier,
        )
        self.assertFalse(incident.success)
        self.verifier.assert_called_once()
        self.assertEqual(self.verifier.call_args.args[0].target_host, self.manager.target_host)

    def test_receipt_must_match_attempt_image_and_freshness(self):
        for altered in ({"attempt_id": "old-attempt"}, {"image_sha256": "0" * 64},
                        {"observed_at": 1.0}, {"observed_at": float("inf")},
                        {"observed_at": time.time() + 3600}):
            with self.subTest(altered=altered):
                self.setUp()
                def verifier(context):
                    valid = replace(self.evidence, attempt_id=context.attempt_id,
                                    image_sha256=context.image_sha256, observed_at=time.time())
                    return replace(valid, **altered)
                result = self.manager.execute_recovery("fixture", ssh_sysupgrade_fn=lambda _: True,
                                                       verify_recovery_fn=verifier)
                self.assertFalse(result.success)
                self.assertTrue(self.manager.recovery_uncertain)

    def test_verifier_timeout_cannot_trigger_another_write(self):
        self.power.trigger_tftp_recovery = Mock(return_value=True)
        self.verifier.side_effect = TimeoutError("fixture")
        incident = self.manager.execute_recovery(
            "fixture", ssh_sysupgrade_fn=lambda _: True, tftp_push_fn=lambda _: True,
            verify_recovery_fn=self.verifier,
        )
        self.assertFalse(incident.success)
        self.power.trigger_tftp_recovery.assert_not_called()


if __name__ == "__main__":
    unittest.main()
