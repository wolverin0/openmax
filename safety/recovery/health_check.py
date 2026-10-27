"""Post-flash and operational health monitoring for Ubiquiti airMAX AC hardware.

Summary: Audits kernel dmesg, memory headroom, MTD write-protect flags, and wireless
radio interface readiness to detect crashes, OOM conditions, or missing evidence.
An unhealthy result blocks acceptance; it never authorizes a rollback by itself.
Keywords: health check, post-boot audit, kernel oops, ath10k crash, memory headroom.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


PANIC_PATTERNS = [
    r"kernel\s+panic",
    r"oops:\s+\d+",
    r"out\s+of\s+memory:\s+kill(?:ed)?\s+process",
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
        """Use kernel MemAvailable, or conservative MemFree on legacy kernels.

        Cached includes tmpfs; adding it can count a staged image as free RAM.
        """
        fields = dict(re.findall(r"^(MemAvailable|MemFree):\s+(\d+)\s+kB\s*$", meminfo_text, re.MULTILINE))
        if not fields or type(min_headroom_kb) is not int or min_headroom_kb <= 0:
            return False, 0, "Missing memory evidence or invalid headroom threshold"
        available_kb = int(fields.get("MemAvailable", fields.get("MemFree", "0")))
        if available_kb < min_headroom_kb:
            return False, available_kb, f"Insufficient memory headroom: {available_kb} kB available (min: {min_headroom_kb} kB)"
        return True, available_kb, None

    @classmethod
    def check_wireless_interface(
        cls, iw_dev_text: str, ifconfig_text: str,
        expected_interfaces: Tuple[str, ...] = ("wlan0", "ath0"),
    ) -> Tuple[bool, Optional[str]]:
        """Check the expected interface's own flags, using the caller's verified names."""
        interfaces = set(re.findall(r"^\s*Interface\s+(\S+)\s*$", iw_dev_text, re.MULTILINE)) & set(expected_interfaces)
        if not interfaces:
            return False, "Expected wireless interface not found in 'iw dev'"

        blocks = re.split(r"(?m)(?=^\S)", ifconfig_text)
        is_up = any(
            re.match(r"^(?:" + "|".join(re.escape(name) for name in sorted(interfaces)) + r")(?:\s|:)", block)
            and re.search(r"\bUP\b", block)
            for block in blocks
        )
        if not is_up:
            return False, "Wireless interface exists but is not marked UP in ifconfig"

        return True, None

    @classmethod
    def check_mtd_write_protection(
        cls, mtd_flags: Dict[str, int], protected_partitions: Optional[Tuple[str, ...]] = None,
    ) -> Tuple[bool, List[str]]:
        """Require protection evidence for a caller-supplied, verified partition map."""
        if not protected_partitions:
            return False, ["Verified protected-partition map is missing"]
        violations: List[str] = []
        for mtd in protected_partitions:
            flags = mtd_flags.get(mtd)
            if type(flags) is not int or flags < 0:
                violations.append(f"Protection evidence missing or invalid for {mtd}")
            elif flags & 0x800:
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
        protected_partitions: Optional[Tuple[str, ...]] = None,
        dmesg_returncode: Optional[int] = None,
        expected_interfaces: Tuple[str, ...] = ("wlan0", "ath0"),
    ) -> HealthCheckResult:
        """Runs the complete suite of system health checks."""
        failures: List[str] = []
        warnings: List[str] = []
        metrics: Dict[str, object] = {}

        # 1. dmesg check
        dmesg_fails = cls.check_dmesg(dmesg_text)
        failures.extend(dmesg_fails)
        if not dmesg_text.strip():
            failures.append("Kernel log evidence is missing")
        if type(dmesg_returncode) is not int or dmesg_returncode != 0:
            failures.append("Successful kernel log acquisition is not evidenced")
        if re.search(r"(?im)^dmesg:.*(?:fail|denied|not permitted)", dmesg_text):
            failures.append("Kernel log acquisition returned an error")

        # 2. memory check
        mem_ok, avail_kb, mem_err = cls.check_memory(meminfo_text, min_headroom_kb)
        metrics["available_ram_kb"] = avail_kb
        if not mem_ok and mem_err:
            failures.append(mem_err)

        # 3. wireless interface check
        wl_ok, wl_err = cls.check_wireless_interface(iw_dev_text, ifconfig_text, expected_interfaces)
        if not wl_ok and wl_err:
            failures.append(wl_err)

        # 4. MTD protection check
        _, mtd_errs = cls.check_mtd_write_protection(mtd_flags or {}, protected_partitions)
        failures.extend(mtd_errs)

        is_healthy = len(failures) == 0

        return HealthCheckResult(
            is_healthy=is_healthy,
            failed_checks=failures,
            warnings=warnings,
            metrics=metrics,
        )
