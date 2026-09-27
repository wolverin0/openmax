"""Post-flash and operational health monitoring for Ubiquiti airMAX AC hardware.

Summary: Audits kernel dmesg, memory headroom, MTD write-protect flags, and wireless
radio interface readiness to detect crashes, OOM conditions, or hardware failures
and determine whether an immediate rollback is required (AGENTS.md §4).
Keywords: health check, post-boot audit, kernel oops, ath10k crash, memory headroom.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


PANIC_PATTERNS = [
    r"kernel\s+panic",
    r"oops:\s+\d+",
    r"out\s+of\s+memory:\s+kill\s+process",
    r"ath10k.*device\s+halted",
    r"ath10k.*firmware\s+crashed",
    r"ath10k.*failed\s+to\s+ping\s+firmware",
    r"ath10k.*wmi\s+timeout",
    r"watchdog:\s+bug:\s+soft\s+lockup",
    r"nmi\s+watchdog:\s+bug:\s+hard\s+lockup",
]


@dataclass
class HealthCheckResult:
    is_healthy: bool
    failed_checks: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, object] = field(default_factory=dict)


class SystemHealthMonitor:
    """Performs non-invasive health evaluation of the radio operating system."""

    @classmethod
    def check_dmesg(cls, dmesg_text: str) -> List[str]:
        """Scans dmesg for critical kernel, driver, or firmware failures."""
        failures: List[str] = []
        for line in dmesg_text.splitlines():
            for pat in PANIC_PATTERNS:
                if re.search(pat, line, re.IGNORECASE):
                    failures.append(f"Critical kernel/driver error: {line.strip()}")
                    break
        return failures

    @classmethod
    def check_memory(cls, meminfo_text: str, min_headroom_kb: int = 8192) -> Tuple[bool, int, Optional[str]]:
        """Verifies that available memory (MemFree + Buffers + Cached) >= min_headroom_kb."""
        mem_free = 0
        buffers = 0
        cached = 0

        for line in meminfo_text.splitlines():
            m_free = re.search(r"MemFree:\s+(\d+)\s+kB", line)
            if m_free:
                mem_free = int(m_free.group(1))
            m_buf = re.search(r"Buffers:\s+(\d+)\s+kB", line)
            if m_buf:
                buffers = int(m_buf.group(1))
            m_cach = re.search(r"Cached:\s+(\d+)\s+kB", line)
            if m_cach:
                cached = int(m_cach.group(1))

        available_kb = mem_free + buffers + cached
        if available_kb < min_headroom_kb:
            return False, available_kb, f"Insufficient memory headroom: {available_kb} kB available (min: {min_headroom_kb} kB)"
        return True, available_kb, None

    @classmethod
    def check_wireless_interface(cls, iw_dev_text: str, ifconfig_text: str) -> Tuple[bool, Optional[str]]:
        """Verifies that the primary wireless interface (wlan0) is active and UP."""
        has_wlan0 = "wlan0" in iw_dev_text or "ath0" in iw_dev_text
        if not has_wlan0:
            return False, "Primary wireless interface (wlan0/ath0) not found in 'iw dev'"

        is_up = ("UP" in ifconfig_text and "wlan0" in ifconfig_text) or ("UP" in ifconfig_text and "ath0" in ifconfig_text)
        if not is_up:
            return False, "Wireless interface exists but is not marked UP in ifconfig"

        return True, None

    @classmethod
    def check_mtd_write_protection(cls, mtd_flags: Dict[str, int]) -> Tuple[bool, List[str]]:
        """Verifies that mtd0 (u-boot) and mtd5 (ART) are NOT write-unlocked in operational mode."""
        # Linux MTD flags: MTD_WRITEABLE = 0x800
        # If writeable flag is set on protected partitions, flag as warning or failure
        violations: List[str] = []
        for mtd, flags in mtd_flags.items():
            if mtd in ("mtd0", "mtd5") and (flags & 0x800):
                violations.append(f"CRITICAL: Protected partition {mtd} has writeable flag set (flags=0x{flags:x})")
        return len(violations) == 0, violations

    @classmethod
    def run_health_audit(
        cls,
        dmesg_text: str,
        meminfo_text: str,
        iw_dev_text: str,
        ifconfig_text: str,
        mtd_flags: Optional[Dict[str, int]] = None,
        min_headroom_kb: int = 8192,
    ) -> HealthCheckResult:
        """Runs the complete suite of system health checks."""
        failures: List[str] = []
        warnings: List[str] = []
        metrics: Dict[str, object] = {}

        # 1. dmesg check
        dmesg_fails = cls.check_dmesg(dmesg_text)
        failures.extend(dmesg_fails)

        # 2. memory check
        mem_ok, avail_kb, mem_err = cls.check_memory(meminfo_text, min_headroom_kb)
        metrics["available_ram_kb"] = avail_kb
        if not mem_ok and mem_err:
            failures.append(mem_err)

        # 3. wireless interface check
        wl_ok, wl_err = cls.check_wireless_interface(iw_dev_text, ifconfig_text)
        if not wl_ok and wl_err:
            failures.append(wl_err)

        # 4. MTD protection check
        if mtd_flags:
            mtd_ok, mtd_errs = cls.check_mtd_write_protection(mtd_flags)
            failures.extend(mtd_errs)

        is_healthy = len(failures) == 0

        return HealthCheckResult(
            is_healthy=is_healthy,
            failed_checks=failures,
            warnings=warnings,
            metrics=metrics,
        )
