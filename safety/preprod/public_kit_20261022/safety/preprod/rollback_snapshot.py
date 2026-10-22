# PRE-PROD2 SNAPSHOT: recording-stub use ONLY; no production adapter.
# Original: orchestration/rollback/workflow.py
# Original SHA256: 85e412bde00b1e9003bf191a95fe2ebbc868adf4c4fd431ea3428fa8fe5f00c7
# The source body below is byte-identical to that held dirty scaffold.
# Snapshot does not qualify hardware recovery or authorize deployment.
# BEGIN ORIGINAL SOURCE
"""Fail-closed recovery workflow scaffolding; not a qualified device adapter.

Summary: Validates a pinned image before any callback or power operation and requires
separate postboot evidence before reporting recovery. Hardware adapters, bounded I/O,
exact-board qualification and operator authorization remain the caller's responsibility.
Keywords: rollback, recovery workflow, AGENTS.md §4, TFTP recovery, golden image.
"""

from __future__ import annotations

import time
import hashlib
import re
import math
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import Lock
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


class TransferOutcome(Enum):
    NO_WRITE = "no_write_started"
    DELIVERED = "delivery_acknowledged"


@dataclass
class RollbackIncident:
    timestamp: float
    reason: str
    tier_used: RollbackTier
    success: bool
    details: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RecoveryContext:
    target_host: str
    attempt_id: str
    image_sha256: str
    delivered_at: float


@dataclass(frozen=True)
class RecoveryVerification:
    """Independent postboot readback, backed by a saved receipt identified by evidence_id."""

    target_host: str
    identity_matches: bool
    firmware_matches: bool
    config_matches: bool
    protected_partitions_match: bool
    service_healthy: bool
    evidence_id: str
    attempt_id: str = ""
    image_sha256: str = ""
    observed_at: float = 0.0

    def confirms(self, context: RecoveryContext) -> bool:
        return (
            self.target_host == context.target_host
            and self.attempt_id == context.attempt_id
            and self.image_sha256 == context.image_sha256
            and type(self.observed_at) in (int, float)
            and math.isfinite(self.observed_at)
            and context.delivered_at <= self.observed_at <= time.time()
            and isinstance(self.evidence_id, str)
            and bool(self.evidence_id.strip())
            and all(value is True for value in (
                self.identity_matches, self.firmware_matches, self.config_matches,
                self.protected_partitions_match, self.service_healthy,
            ))
        )


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
        # Process-local latch only. No production runner or durable retry adapter
        # is qualified by this scaffold; restarting must never be used to bypass it.
        self.recovery_uncertain = False
        self._attempt_lock = Lock()

    def execute_recovery(
        self,
        failure_reason: str,
        ssh_sysupgrade_fn: Optional[Callable[[Path], bool | TransferOutcome]] = None,
        tftp_push_fn: Optional[Callable[[Path], bool | TransferOutcome]] = None,
        reset_hold_sec: float = 12.0,
        settle_delay_sec: float = 2.0,
        verify_recovery_fn: Optional[Callable[[RecoveryContext], RecoveryVerification]] = None,
    ) -> RollbackIncident:
        """Serialize attempts on this instance without changing an active attempt's state."""
        if not self._attempt_lock.acquire(blocking=False):
            return RollbackIncident(time.time(), failure_reason, RollbackTier.NONE, False,
                                    ["Recovery attempt already active on this manager; no action taken."])
        try:
            return self._execute_recovery(failure_reason, ssh_sysupgrade_fn, tftp_push_fn,
                                          reset_hold_sec, settle_delay_sec, verify_recovery_fn)
        finally:
            self._attempt_lock.release()

    def _execute_recovery(
        self,
        failure_reason: str,
        ssh_sysupgrade_fn: Optional[Callable[[Path], bool | TransferOutcome]] = None,
        tftp_push_fn: Optional[Callable[[Path], bool | TransferOutcome]] = None,
        reset_hold_sec: float = 12.0,
        settle_delay_sec: float = 2.0,
        verify_recovery_fn: Optional[Callable[[RecoveryContext], RecoveryVerification]] = None,
    ) -> RollbackIncident:
        """Run only with real, bounded adapters and separately obtained authorization.

        True/DELIVERED means acknowledged delivery. Only explicit NO_WRITE permits
        escalation. False, exceptions and invalid results are ambiguous and stop the
        pipeline. Delivery or a power reset alone never establishes recovery.
        """
        self.state = RollbackState.HEALTH_FAILED
        details: List[str] = [f"Triggered recovery due to: {failure_reason}"]
        ts = time.time()
        attempt_id = uuid.uuid4().hex

        def finish(tier: RollbackTier, success: bool, detail: str) -> RollbackIncident:
            self.state = RollbackState.RECOVERED if success else RollbackState.FAILED
            details.append(detail)
            incident = RollbackIncident(ts, failure_reason, tier, success, details)
            self.history.append(incident)
            return incident

        if self.recovery_uncertain:
            return finish(RollbackTier.NONE, False, "Earlier action remains unverified; manual reconciliation required before another attempt.")

        def image_valid() -> bool:
            try:
                if not isinstance(self.golden_image_sha256, str) or not re.fullmatch(
                    r"[0-9a-fA-F]{64}", self.golden_image_sha256
                ):
                    return False
                if self.golden_image_path.is_symlink() or not self.golden_image_path.is_file():
                    return False
                with self.golden_image_path.open("rb") as handle:
                    digest = hashlib.file_digest(handle, "sha256").hexdigest()
                return digest == self.golden_image_sha256.lower()
            except OSError:
                return False

        def verify(tier: RollbackTier) -> RollbackIncident:
            context = RecoveryContext(self.target_host, attempt_id, self.golden_image_sha256.lower(), time.time())
            try:
                evidence = verify_recovery_fn(context)
            except Exception as error:
                return finish(tier, False, f"Postboot verification failed ({type(error).__name__}); do not retry automatically.")
            if not isinstance(evidence, RecoveryVerification) or not evidence.confirms(context):
                return finish(tier, False, "Image delivered, but complete postboot recovery evidence is absent; stop.")
            self.recovery_uncertain = False
            return finish(tier, True, "Recovery verified by independent postboot readback.")

        if not image_valid():
            return finish(RollbackTier.NONE, False, "Golden image missing or SHA256 mismatch; no action taken.")
        if not callable(verify_recovery_fn):
            return finish(RollbackTier.NONE, False, "Postboot verifier required; no action taken.")
        if not callable(ssh_sysupgrade_fn) and not callable(tftp_push_fn):
            return finish(RollbackTier.NONE, False, "No recovery transfer adapter; no action taken.")

        # Tier 1: Soft sysupgrade if device is reachable over SSH
        if callable(ssh_sysupgrade_fn):
            self.state = RollbackState.ROLLING_BACK_SOFT
            details.append("Attempting Tier 1 Soft Sysupgrade over SSH...")
            self.recovery_uncertain = True
            try:
                ok_soft = ssh_sysupgrade_fn(self.golden_image_path)
            except Exception as error:
                return finish(RollbackTier.TIER_1_SOFT_SYSUPGRADE, False,
                              f"Soft transfer outcome unknown ({type(error).__name__}); no automatic power reset.")
            if ok_soft is True or ok_soft is TransferOutcome.DELIVERED:
                return verify(RollbackTier.TIER_1_SOFT_SYSUPGRADE)
            if ok_soft is not TransferOutcome.NO_WRITE:
                return finish(RollbackTier.TIER_1_SOFT_SYSUPGRADE, False,
                              "Soft transfer outcome unconfirmed; no automatic power reset.")
            self.recovery_uncertain = False
            details.append("Soft adapter reports no write started; considering Tier 2.")

        if not callable(tftp_push_fn):
            return finish(RollbackTier.NONE, False, "TFTP adapter absent; no power reset attempted.")
        if not image_valid():
            return finish(RollbackTier.NONE, False, "Golden image changed before Tier 2; no power reset attempted.")

        # Tier 2: Hard recovery via PoE Remote Reset and TFTP
        self.state = RollbackState.ROLLING_BACK_TFTP
        details.append("Initiating Tier 2 PoE Remote Reset TFTP Recovery...")
        self.recovery_uncertain = True

        try:
            poe_ok = self.power.trigger_tftp_recovery(
                self.outlet_id,
                reset_hold_sec=reset_hold_sec,
                settle_delay_sec=settle_delay_sec,
            )
        except Exception as error:
            return finish(RollbackTier.TIER_2_POE_TFTP_RECOVERY, False,
                          f"Power operation outcome unknown ({type(error).__name__}); stop.")
        if poe_ok is not True:
            return finish(RollbackTier.TIER_2_POE_TFTP_RECOVERY, False, "Power recovery not confirmed; no TFTP push.")
        if not image_valid():
            return finish(RollbackTier.TIER_2_POE_TFTP_RECOVERY, False, "Golden image changed; no TFTP push.")
        try:
            tftp_ok = tftp_push_fn(self.golden_image_path)
        except Exception as error:
            return finish(RollbackTier.TIER_2_POE_TFTP_RECOVERY, False,
                          f"TFTP outcome unknown ({type(error).__name__}); stop.")
        if tftp_ok is not True and tftp_ok is not TransferOutcome.DELIVERED:
            return finish(RollbackTier.TIER_2_POE_TFTP_RECOVERY, False, "TFTP delivery not confirmed; stop.")
        return verify(RollbackTier.TIER_2_POE_TFTP_RECOVERY)
