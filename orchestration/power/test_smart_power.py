"""Unit tests for orchestration.power.smart_power (SmartPowerController)."""

import time
import unittest
from orchestration.power.smart_power import (
    SmartPowerController,
    MockPowerDriver,
)


class TestSmartPowerController(unittest.TestCase):
    def setUp(self):
        self.driver = MockPowerDriver(initial_state=True)
        # Fast cooldown for testing
        self.controller = SmartPowerController(
            driver=self.driver,
            min_cooldown_seconds=0.05,
            default_off_duration_seconds=0.01,
        )

    def test_power_on_and_off(self):
        self.assertTrue(self.controller.power_off(1))
        self.assertFalse(self.controller.is_powered_on(1))

        self.assertTrue(self.controller.power_on(1))
        self.assertTrue(self.controller.is_powered_on(1))

    def test_safe_power_cycle(self):
        # Initial cycle
        self.assertTrue(self.controller.power_cycle(1, off_duration_sec=0.01, bypass_cooldown=True))
        self.assertTrue(self.controller.is_powered_on(1))
        h = self.controller._get_history(1)
        self.assertEqual(h.total_cycles, 1)

    def test_cooldown_lockout_blocks_rapid_cycle(self):
        # First cycle with cooldown active
        self.assertTrue(self.controller.power_cycle(1, off_duration_sec=0.01, bypass_cooldown=True))
        
        # Immediate second cycle without bypass should be blocked by cooldown
        blocked = self.controller.power_cycle(1, off_duration_sec=0.01, bypass_cooldown=False)
        self.assertFalse(blocked)

        # After sleeping past cooldown, cycle should succeed
        time.sleep(0.06)
        succeeded = self.controller.power_cycle(1, off_duration_sec=0.01, bypass_cooldown=False)
        self.assertTrue(succeeded)

    def test_trigger_tftp_recovery(self):
        # Test TFTP recovery sequence with mock short duration
        ok = self.controller.trigger_tftp_recovery(outlet_id=2, reset_hold_sec=0.02)
        self.assertTrue(ok)
        self.assertTrue(self.controller.is_powered_on(2))
        
        # Verify reset line was pulsed
        self.assertEqual(len(self.driver.reset_pulses), 1)
        outlet, dur = self.driver.reset_pulses[0]
        self.assertEqual(outlet, 2)
        self.assertEqual(dur, 0.02)
        
        h = self.controller._get_history(2)
        self.assertTrue(h.in_recovery_mode)


if __name__ == "__main__":
    unittest.main()
