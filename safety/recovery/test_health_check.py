"""Unit tests for safety.recovery.health_check (SystemHealthMonitor)."""

import unittest
from safety.recovery.health_check import SystemHealthMonitor


CLEAN_DMESG = """
[    0.000000] Linux version 5.15.150 (builder@openwrt)
[    5.123456] ath10k_pci 0000:00:00.0: qca988x hw2.0 target 0x00000000 chip_id 0x00000000
[    5.456789] ath10k: firmware ver 10.2.4-ct-988x booted
"""

CRASH_DMESG = """
[   45.123456] ath10k_pci 0000:00:00.0: firmware crashed! (reason: 0x2)
[   45.123480] ath10k_pci 0000:00:00.0: failed to ping firmware
"""

CLEAN_MEMINFO = """
MemTotal:          61384 kB
MemFree:           14500 kB
Buffers:            2100 kB
Cached:             8200 kB
"""

OOM_MEMINFO = """
MemTotal:          61384 kB
MemFree:            1200 kB
Buffers:             200 kB
Cached:             1100 kB
"""

CLEAN_IW_DEV = """
phy#0
	Interface wlan0
		ifindex 3
		wdev 0x1
		addr 24:a4:3c:00:11:22
		type AP
"""

CLEAN_IFCONFIG = """
wlan0     Link encap:Ethernet  HWaddr 24:A4:3C:00:11:22  
          inet6 addr: fe80::26a4:3cff:fe00:1122/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
"""


class TestSystemHealthMonitor(unittest.TestCase):
    def test_clean_health_audit_passes(self):
        res = SystemHealthMonitor.run_health_audit(
            dmesg_text=CLEAN_DMESG,
            meminfo_text=CLEAN_MEMINFO,
            iw_dev_text=CLEAN_IW_DEV,
            ifconfig_text=CLEAN_IFCONFIG,
            mtd_flags={"mtd0": 0x0, "mtd1": 0x0, "mtd5": 0x0},
            min_headroom_kb=8192,
        )
        self.assertTrue(res.is_healthy)
        self.assertEqual(len(res.failed_checks), 0)
        self.assertEqual(res.metrics["available_ram_kb"], 14500 + 2100 + 8200)

    def test_dmesg_crash_detected(self):
        fails = SystemHealthMonitor.check_dmesg(CRASH_DMESG)
        self.assertGreaterEqual(len(fails), 1)
        self.assertTrue(any("firmware crashed" in f for f in fails))

    def test_low_memory_detected(self):
        ok, avail, err = SystemHealthMonitor.check_memory(OOM_MEMINFO, min_headroom_kb=8192)
        self.assertFalse(ok)
        self.assertEqual(avail, 1200 + 200 + 1100)
        self.assertIn("Insufficient memory headroom", err)

    def test_wireless_down_detected(self):
        down_ifconfig = "wlan0 Link encap:Ethernet BROADCAST MULTICAST"
        ok, err = SystemHealthMonitor.check_wireless_interface(CLEAN_IW_DEV, down_ifconfig)
        self.assertFalse(ok)
        self.assertIn("not marked UP", err)

    def test_mtd_protection_violation_detected(self):
        # mtd0 has writeable flag 0x800 set
        ok, violations = SystemHealthMonitor.check_mtd_write_protection({"mtd0": 0x800, "mtd5": 0x0})
        self.assertFalse(ok)
        self.assertEqual(len(violations), 1)
        self.assertIn("mtd0 has writeable flag set", violations[0])


if __name__ == "__main__":
    unittest.main()
