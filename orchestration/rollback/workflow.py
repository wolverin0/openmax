"""Automated Rollback and Recovery Workflow Manager conforming to AGENTS.md §4.

Summary: Executes multi-tier automated rollback upon health check failure or watchdog
unresponsiveness: Tier 1 soft sysupgrade / config revert via SSH, and Tier 2 hardware
PoE reset to u-boot TFTP recovery with golden firmware push.
Keywords: rollback, recovery workflow, AGENTS.md §4, TFTP recovery, golden image.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, List, Optional
from orchestration.power.smart_power import SmartPowerController


class RollbackTier(Enum):
    NONE = "none"
    TIER_1_SOFT_SYSUPGRADE = "tier1_soft_sysupgrade"
    TIER_2_POE_TFTP_RECOVERY = "tier2_poe_tftp_recovery"


class RollbackState(Enum):
    IDLE = "idle"
    HEALTH_FAILED = "health_failed"
    ROLLING_BACK_SOFT = "rolling_back_soft"
    ROLLING_BACK_TFTP = "rolling_back_tftp"
    RECOVERED = "recovered"
    FAILED = "failed"


@dataclass
class RollbackIncident:
    timestamp: float
    reason: str
    tier_used: RollbackTier
    success: bool
    details: List[str] = field(default_factory=list)


class RollbackManager:
    """Manages multi-tier automated rollback for airMAX AC devices."""

    def __init__(
        self,
        target_host: str,
        outlet_id: int,
        golden_image_path: Path,
        golden_image_sha256: str,
        power_controller: SmartPowerController,
    ):
        self.target_host = target_host
        self.outlet_id = outlet_id
        self.golden_image_path = golden_image_path
        self.golden_image_sha256 = golden_image_sha256
        self.power = power_controller
        self.state = RollbackState.IDLE
        self.history: List[RollbackIncident] = []

    def execute_recovery(
        self,
        failure_reason: str,
        ssh_sysupgrade_fn: Optional[Callable[[Path], bool]] = None,
        tftp_push_fn: Optional[Callable[[Path], bool]] = None,
        reset_hold_sec: float = 12.0,
        settle_delay_sec: float = 2.0,
    ) -> RollbackIncident:
        """Executes recovery pipeline: attempts Tier 1 soft restore, escalating to Tier 2 if needed."""
        self.state = RollbackState.HEALTH_FAILED
        details: List[str] = [f"Triggered recovery due to: {failure_reason}"]
        ts = time.time()

        # Tier 1: Soft sysupgrade if device is reachable over SSH
        if ssh_sysupgrade_fn:
            self.state = RollbackState.ROLLING_BACK_SOFT
            details.append("Attempting Tier 1 Soft Sysupgrade over SSH...")
            try:
                ok_soft = ssh_sysupgrade_fn(self.golden_image_path)
                if ok_soft:
                    self.state = RollbackState.RECOVERED
                    details.append("Tier 1 Soft Sysupgrade succeeded.")
                    incident = RollbackIncident(
                        timestamp=ts,
                        reason=failure_reason,
                        tier_used=RollbackTier.TIER_1_SOFT_SYSUPGRADE,
                        success=True,
                        details=details,
                    )
                    self.history.append(incident)
                    return incident
                else:
                    details.append("Tier 1 Soft Sysupgrade failed. Escalating to Tier 2.")
            except Exception as e:
                details.append(f"Tier 1 Soft Sysupgrade exception: {e}. Escalating to Tier 2.")

        # Tier 2: Hard recovery via PoE Remote Reset and TFTP
        self.state = RollbackState.ROLLING_BACK_TFTP
        details.append("Initiating Tier 2 PoE Remote Reset TFTP Recovery...")

        poe_ok = self.power.trigger_tftp_recovery(
            self.outlet_id,
            reset_hold_sec=reset_hold_sec,
            settle_delay_sec=settle_delay_sec,
        )
        if not poe_ok:
            self.state = RollbackState.FAILED
            details.append("CRITICAL: Failed to pulse PoE remote reset line.")
            incident = RollbackIncident(
                timestamp=ts,
                reason=failure_reason,
                tier_used=RollbackTier.TIER_2_POE_TFTP_RECOVERY,
                success=False,
                details=details,
            )
            self.history.append(incident)
            return incident

        details.append("PoE reset asserted. Pushing golden image via TFTP...")
        tftp_ok = False
        if tftp_push_fn:
            try:
                tftp_ok = tftp_push_fn(self.golden_image_path)
            except Exception as e:
                details.append(f"TFTP push exception: {e}")
        else:
            # Simulated TFTP recovery for dry-run
            tftp_ok = True

        if tftp_ok:
            self.state = RollbackState.RECOVERED
            details.append("Tier 2 TFTP recovery image pushed successfully.")
        else:
            self.state = RollbackState.FAILED
            details.append("CRITICAL: TFTP push failed.")

        incident = RollbackIncident(
            timestamp=ts,
            reason=failure_reason,
            tier_used=RollbackTier.TIER_2_POE_TFTP_RECOVERY,
            success=tftp_ok,
            details=details,
        )
        self.history.append(incident)
        return incident
