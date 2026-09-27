"""Unit tests for inventory.board_probe.probe (BoardProbeParser)."""

import unittest
from inventory.board_probe.probe import BoardProbeParser, PCI_QCA9880


AIROS_CPUINFO = """
system type		: Atheros AR9342 rev 2
machine			: Ubiquiti LiteAP AC
processor		: 0
cpu model		: MIPS 74Kc V4.12
BogoMIPS		: 266.64
wait instruction	: yes
microsecond timers	: yes
tlb_entries		: 32
extra interrupt vector	: yes
hardware watchpoint	: yes, count: 4, address/irw mask: [0x0ffc, 0x0ffc, 0x0ffb, 0x0ffb]
ASEs implemented	: mips16 dsp dsp2
shadow register sets	: 1
kscratch registers	: 0
core			: 0
VCED exceptions		: not available
VCEI exceptions		: not available
"""

AIROS_MEMINFO = """
MemTotal:          60232 kB
MemFree:           31420 kB
Buffers:            1820 kB
Cached:            14980 kB
"""

AIROS_MTD = """
dev:    size   erasesize  name
mtd0: 00040000 00010000 "u-boot"
mtd1: 00010000 00010000 "u-boot-env"
mtd2: 00100000 00010000 "kernel"
mtd3: 00e00000 00010000 "rootfs"
mtd4: 00040000 00010000 "cfg"
mtd5: 00010000 00010000 "EEPROM"
"""

AIROS_LSPCI = """
00:00.0 Network controller [0280]: Qualcomm Atheros QCA988x 802.11ac Wireless Network Adapter [168c:003c] (rev 00)
"""

AIROS_VERSION = "WA.v8.7.1"

AIROS_SYSTEM_INFO = """
system.model=LiteAP AC
board.sysid=0xe825
board.name=LAP-120
"""

AIROS_DMESG = """
[    0.000000] Linux version 4.4.153 (build@builder)
[    1.234567] ath_pci: 10.1.467 loaded
[    1.456789] ubnthal: system driver registered
"""

OPENWRT_CPUINFO = """
system type		: Qualcomm Atheros QCA956X ver 1 rev 0
machine			: Ubiquiti LiteAP AC (LAP-120)
processor		: 0
cpu model		: MIPS 74Kc V5.0
BogoMIPS		: 385.84
"""

OPENWRT_MEMINFO = """
MemTotal:          61384 kB
MemFree:           38920 kB
"""

OPENWRT_OS_RELEASE = """
NAME="OpenWrt"
VERSION="24.10.4"
ID="openwrt"
"""

OPENWRT_DMESG_ATH10K = """
[   10.234567] ath10k_pci 0000:00:00.0: enabling device (0000 -> 0002)
[   10.567890] ath10k-ct: firmware ver 10.2.4-ct-988x-001-f2d34e loaded
[   10.890123] ath10k: qca988x hw2.0 target 0x00000000 chip_id 0x00000000
"""

OPENWRT_GPS_DMESG = """
[    8.123456] ttyS1 at MMIO 0x18020000 (irq = 11, base_baud = 25000000) is a 16550A
[    8.234567] ubnt_gps: LAP-GPS NMEA receiver initialized on ttyS1 at 9600 baud
"""


class TestBoardProbeParser(unittest.TestCase):
    def test_parse_airmax_airos(self):
        identity = BoardProbeParser.probe_device_facts(
            cpuinfo=AIROS_CPUINFO,
            meminfo=AIROS_MEMINFO,
            mtd=AIROS_MTD,
            lspci=AIROS_LSPCI,
            etc_version=AIROS_VERSION,
            os_release="",
            dmesg=AIROS_DMESG,
            lsmod="ath_pci ubnthal",
            system_info=AIROS_SYSTEM_INFO,
            board_info="",
            tty_list="ttyS0",
        )
        self.assertEqual(identity.os_type, "airOS")
        self.assertEqual(identity.os_version, "WA.v8.7.1")
        self.assertEqual(identity.model_name, "LiteAP AC")
        self.assertEqual(identity.board_id, "0xe825")
        self.assertEqual(identity.radio_pci_id, PCI_QCA9880)
        self.assertEqual(identity.wireless_driver, "ol_ath (airOS)")
        self.assertTrue(identity.protected_partitions_intact)
        self.assertTrue(identity.is_supported_lab_unit)
        self.assertFalse(identity.has_gps)
        self.assertEqual(len(identity.partitions), 6)
        self.assertTrue(identity.partitions[0].is_protected)  # u-boot
        self.assertTrue(identity.partitions[5].is_protected)  # EEPROM

    def test_parse_openwrt_ath10k_ct(self):
        identity = BoardProbeParser.probe_device_facts(
            cpuinfo=OPENWRT_CPUINFO,
            meminfo=OPENWRT_MEMINFO,
            mtd=AIROS_MTD,
            lspci=AIROS_LSPCI,
            etc_version="",
            os_release=OPENWRT_OS_RELEASE,
            dmesg=f"{OPENWRT_DMESG_ATH10K}\n{OPENWRT_GPS_DMESG}",
            lsmod="ath10k_pci ath10k_core mac80211",
            system_info="",
            board_info="",
            tty_list="ttyS0 ttyS1",
        )
        self.assertEqual(identity.os_type, "OpenWrt")
        self.assertEqual(identity.os_version, "24.10.4")
        self.assertEqual(identity.wireless_driver, "ath10k_pci")
        self.assertEqual(identity.driver_variant, "ath10k-ct")
        self.assertEqual(identity.firmware_version, "10.2.4-ct-988x-001-f2d34e")
        self.assertTrue(identity.has_gps)
        self.assertTrue(identity.is_supported_lab_unit)

    def test_reject_unsupported_hardware(self):
        fake_cpu = "system type : Intel x86_64\ncpu model : Core i7"
        fake_mem = "MemTotal: 16777216 kB"
        identity = BoardProbeParser.probe_device_facts(
            cpuinfo=fake_cpu,
            meminfo=fake_mem,
            mtd="",
            lspci="",
            etc_version="",
            os_release="Ubuntu 22.04",
            dmesg="",
            lsmod="",
        )
        self.assertFalse(identity.is_supported_lab_unit)
        self.assertFalse(identity.protected_partitions_intact)
        self.assertGreater(len(identity.validation_errors), 0)


if __name__ == "__main__":
    unittest.main()
