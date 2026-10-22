"""Smart Power Controller and PoE Remote Reset Manager.

Summary: Orchestrates managed PDU outlets, smart relay switches (Tasmota/Shelly),
and PoE remote-reset lines for unattended automated power-cycling and bootloader TFTP
recovery qualification (FMX-0002, AGENTS.md §4).
Keywords: smart power, PoE reset, TFTP recovery, PDU, power cycle, cool-down lockout.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional


class PowerDriver(ABC):
    """Abstract interface for physical or simulated power control hardware."""

    @abstractmethod
    def set_outlet_state(self, outlet_id: int, state: bool) -> bool:
        """Sets outlet to ON (True) or OFF (False)."""
        pass

    @abstractmethod
    def get_outlet_state(self, outlet_id: int) -> bool:
        """Returns True if outlet is currently ON, False if OFF."""
        pass

    @abstractmethod
    def pulse_poe_reset(self, outlet_id: int, duration_sec: float) -> bool:
        """Pulses the PoE remote reset line (DC offset) to force u-boot TFTP recovery."""
        pass


class MockPowerDriver(PowerDriver):
    """In-memory mock driver for testing, dry-runs, and simulations."""

    def __init__(self, initial_state: bool = True):
        self.outlets: Dict[int, bool] = {}
        self.reset_pulses: list[tuple[int, float]] = []
        self._default = initial_state

    def set_outlet_state(self, outlet_id: int, state: bool) -> bool:
        self.outlets[outlet_id] = state
        return True

    def get_outlet_state(self, outlet_id: int) -> bool:
        return self.outlets.get(outlet_id, self._default)

    def pulse_poe_reset(self, outlet_id: int, duration_sec: float) -> bool:
        self.reset_pulses.append((outlet_id, duration_sec))
        return True


@dataclass
class OutletHistory:
    last_state_change: float = 0.0
    total_cycles: int = 0
    in_recovery_mode: bool = False


class SmartPowerController:
    """Manages power cycling with cool-down safety guards and recovery automation."""

    def __init__(
        self,
        driver: PowerDriver,
        min_cooldown_seconds: float = 5.0,
        default_off_duration_seconds: float = 5.0,
    ):
        self.driver = driver
        self.min_cooldown_sec = min_cooldown_seconds
        self.default_off_sec = default_off_duration_seconds
        self.history: Dict[int, OutletHistory] = {}

    def _get_history(self, outlet_id: int) -> OutletHistory:
        if outlet_id not in self.history:
            self.history[outlet_id] = OutletHistory()
        return self.history[outlet_id]

    def power_on(self, outlet_id: int) -> bool:
        """Powers ON the target outlet."""
        h = self._get_history(outlet_id)
        ok = self.driver.set_outlet_state(outlet_id, True)
        if ok:
            h.last_state_change = time.time()
        return ok

    def power_off(self, outlet_id: int) -> bool:
        """Powers OFF the target outlet."""
        h = self._get_history(outlet_id)
        ok = self.driver.set_outlet_state(outlet_id, False)
        if ok:
            h.last_state_change = time.time()
        return ok

    def is_powered_on(self, outlet_id: int) -> bool:
        """Checks if outlet is ON."""
        return self.driver.get_outlet_state(outlet_id)

    def power_cycle(
        self,
        outlet_id: int,
        off_duration_sec: Optional[float] = None,
        bypass_cooldown: bool = False,
    ) -> bool:
        """Performs a safe power cycle (OFF -> wait -> ON) respecting cooldown."""
        h = self._get_history(outlet_id)
        now = time.time()
        elapsed = now - h.last_state_change

        if not bypass_cooldown and elapsed < self.min_cooldown_sec:
            # Cool-down guard violation: rapid cycling damages power electronics
            return False

        off_time = off_duration_sec or self.default_off_sec

        # 1. Turn OFF
        if not self.power_off(outlet_id):
            return False

        # 2. Wait off duration
        time.sleep(off_time)

        # 3. Turn ON
        if not self.power_on(outlet_id):
            return False

        h.total_cycles += 1
        return True

    def trigger_tftp_recovery(
        self,
        outlet_id: int,
        reset_hold_sec: float = 12.0,
        settle_delay_sec: float = 2.0,
    ) -> bool:
        """
        Triggers Ubiquiti u-boot TFTP recovery mode ('urescue').
        Standard Ubiquiti recovery requires holding the reset button/line
        for 8-15 seconds while powering on until the signal LEDs alternate flash.
        """
        h = self._get_history(outlet_id)

        # 1. Power off
        if not self.power_off(outlet_id):
            return False
        time.sleep(settle_delay_sec)

        # 2. Assert reset pulse line
        if not self.driver.pulse_poe_reset(outlet_id, reset_hold_sec):
            return False

        # 3. Power on while reset is asserted
        if not self.power_on(outlet_id):
            return False

        # 4. Wait for reset release window
        time.sleep(reset_hold_sec)
        h.in_recovery_mode = True
        return True
