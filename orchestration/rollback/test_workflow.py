"""Unit tests for orchestration.rollback.workflow (RollbackManager)."""

import unittest
from pathlib import Path
from orchestration.power.smart_power import SmartPowerController, MockPowerDriver
from orchestration.rollback.workflow import RollbackManager, RollbackState, RollbackTier


class TestRollbackManager(unittest.TestCase):
    def setUp(self):
        self.driver = MockPowerDriver(initial_state=True)
        self.power = SmartPowerController(
            driver=self.driver,
            min_cooldown_seconds=0.01,
            default_off_duration_seconds=0.01,
        )
        self.manager = RollbackManager(
            target_host="192.168.1.20",
            outlet_id=1,
            golden_image_path=Path("/firmware/golden_sysupgrade.bin"),
            golden_image_sha256="abcdef1234567890",
            power_controller=self.power,
        )

    def test_successful_tier1_soft_rollback(self):
        def mock_ssh_sysupgrade(p: Path) -> bool:
            return True

        incident = self.manager.execute_recovery(
            failure_reason="Post-flash kernel oops detected in dmesg",
            ssh_sysupgrade_fn=mock_ssh_sysupgrade,
        )

        self.assertTrue(incident.success)
        self.assertEqual(incident.tier_used, RollbackTier.TIER_1_SOFT_SYSUPGRADE)
        self.assertEqual(self.manager.state, RollbackState.RECOVERED)
        self.assertEqual(len(self.manager.history), 1)

    def test_escalation_to_tier2_tftp_recovery(self):
        # SSH fails (e.g. host unreachable or locked)
        def mock_failing_ssh(p: Path) -> bool:
            return False

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
        )

        self.assertTrue(incident.success)
        self.assertEqual(incident.tier_used, RollbackTier.TIER_2_POE_TFTP_RECOVERY)
        self.assertEqual(self.manager.state, RollbackState.RECOVERED)
        self.assertEqual(len(tftp_calls), 1)
        self.assertEqual(tftp_calls[0], Path("/firmware/golden_sysupgrade.bin"))


if __name__ == "__main__":
    unittest.main()
