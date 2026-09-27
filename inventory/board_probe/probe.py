"""Hardware and OS fingerprinting probe for Ubiquiti airMAX AC hardware.

Summary: Parses system information from airOS or OpenWrt (live via SSH or offline logs)
to extract SoC model, RAM, flash map, radio PCI ID, driver/firmware version, GPS presence,
and validates that protected partitions are identified and shielded.
Keywords: FMX-0001, board probe, AR9342, QCA9880, LAP-GPS, LAP-120, LBE-5AC, OpenWrt, airOS.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


KNOWN_BOARD_IDS: Dict[str, str] = {
    "0xe805": "NanoBeam 5AC Gen2",
    "0xe825": "LiteAP AC (LAP-120)",
    "0xe835": "LiteAP GPS (LAP-GPS)",
    "0xe855": "LiteBeam 5AC Gen2",
    "0xe865": "NanoStation 5AC Loco",
    "0xe885": "NanoStation 5AC",
    "0xe8a5": "Rocket 5AC Lite",
    "0xe8b5": "Rocket 5AC Prism Gen2",
}

# Known PCI IDs for Ubiquiti AC radios
PCI_QCA9880 = "168c:003c"  # Qualcomm Atheros QCA9880 / QCA9882 802.11ac Wave 1


@dataclass
class MtdPartition:
    dev_name: str  # e.g. "mtd0"
    size_bytes: int
    erasesize_bytes: int
    name: str  # e.g. "u-boot", "ART"
    is_protected: bool = False


@dataclass
class BoardIdentity:
    os_type: str  # "airOS" | "OpenWrt" | "unknown"
    os_version: str
    model_name: str
    board_id: Optional[str]
    soc_model: str
    cpu_arch: str
    ram_bytes: int
    flash_bytes: int
    radio_pci_id: str
    radio_chipset: str
    wireless_driver: str
    driver_variant: str  # "ath10k-ct", "ath10k-upstream", "ol_ath", or "unknown"
    firmware_version: str
    has_gps: bool
    partitions: List[MtdPartition] = field(default_factory=list)
    protected_partitions_intact: bool = False
    is_supported_lab_unit: bool = False
    validation_errors: List[str] = field(default_factory=list)


class BoardProbeParser:
    """Parses raw shell and procfs outputs from Ubiquiti airMAX AC hardware."""

    PROTECTED_NAMES = {"u-boot", "u-boot-env", "EEPROM", "ART", "cfg", "board_config", "caldata"}

    @classmethod
    def parse_cpuinfo(cls, text: str) -> Dict[str, str]:
        """Extracts SoC model and system type from /proc/cpuinfo."""
        out = {"soc": "Unknown SoC", "cpu": "Unknown CPU", "mips": "0"}
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                key, val = [x.strip() for x in line.split(":", 1)]
                k_lower = key.lower()
                if "system type" in k_lower or "machine" in k_lower:
                    out["soc"] = val
                elif "cpu model" in k_lower:
                    out["cpu"] = val
                elif "bogomips" in k_lower:
                    out["mips"] = val
        return out

    @classmethod
    def parse_meminfo(cls, text: str) -> int:
        """Extracts total RAM in bytes from /proc/meminfo."""
        match = re.search(r"MemTotal:\s+(\d+)\s+kB", text, re.IGNORECASE)
        if match:
            return int(match.group(1)) * 1024
        return 0

    @classmethod
    def parse_mtd(cls, text: str) -> List[MtdPartition]:
        """Parses /proc/mtd and marks protected partitions."""
        partitions: List[MtdPartition] = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("dev:"):
                continue
            # Format: mtdX: 00040000 00010000 "u-boot"
            match = re.match(r"(mtd\d+):\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+\"([^\"]+)\"", line)
            if match:
                dev_name = match.group(1)
                size = int(match.group(2), 16)
                erasesize = int(match.group(3), 16)
                name = match.group(4)
                is_prot = name in cls.PROTECTED_NAMES or dev_name in ("mtd0", "mtd1", "mtd4", "mtd5")
                partitions.append(MtdPartition(
                    dev_name=dev_name,
                    size_bytes=size,
                    erasesize_bytes=erasesize,
                    name=name,
                    is_protected=is_prot,
                ))
        return partitions

    @classmethod
    def parse_lspci(cls, text: str) -> str:
        """Extracts wireless radio PCI device ID (e.g. 168c:003c)."""
        match = re.search(r"(168c:[0-9a-fA-F]{4})", text, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        return "unknown"

    @classmethod
    def parse_os_release(cls, etc_version: str, os_release: str) -> tuple[str, str]:
        """Detects OS type (airOS vs OpenWrt) and release version."""
        combined = f"{etc_version}\n{os_release}".lower()
        if "openwrt" in combined or "lede" in combined:
            m = re.search(r'version="?([^"\n]+)"?', os_release, re.IGNORECASE)
            ver = m.group(1) if m else "OpenWrt Unknown"
            return "OpenWrt", ver
        elif "wa." in combined or "xc." in combined or "2xc." in combined or "airos" in combined:
            m = re.search(r'(wa|xc|2xc)\.v[0-9\.\-]+', etc_version, re.IGNORECASE)
            ver = m.group(0) if m else etc_version.strip().splitlines()[0] if etc_version.strip() else "airOS Unknown"
            return "airOS", ver
        return "unknown", "unknown"

    @classmethod
    def parse_wireless_drivers(cls, dmesg_or_lsmod: str) -> tuple[str, str, str]:
        """Identifies active driver, variant (ath10k-ct vs standard), and firmware version."""
        text = dmesg_or_lsmod
        driver = "unknown"
        variant = "unknown"
        fw_ver = "unknown"

        if "ath10k_pci" in text or "ath10k" in text:
            driver = "ath10k_pci"
            if "ath10k-ct" in text or "ath10k_ct" in text:
                variant = "ath10k-ct"
            else:
                variant = "ath10k-upstream"
            
            # Extract firmware version
            m_fw = re.search(r"firmware\s+ver\s+([^\s,]+)", text, re.IGNORECASE)
            if m_fw:
                fw_ver = m_fw.group(1)
            else:
                m_fw2 = re.search(r"qca988x/hw2\.0/firmware-([0-9\.\-a-zA-Z]+)", text)
                if m_fw2:
                    fw_ver = m_fw2.group(1)
        elif "ath_pci" in text or "ubnthal" in text or "ol_ath" in text:
            driver = "ol_ath (airOS)"
            variant = "proprietary"
            m_ver = re.search(r"ath_pci:\s+([0-9\.\-]+)", text)
            if m_ver:
                fw_ver = m_ver.group(1)

        return driver, variant, fw_ver

    @classmethod
    def detect_gps(cls, dmesg_text: str, tty_list: str) -> bool:
        """Detects whether GPS hardware (LAP-GPS UART on ttyS1) is active."""
        if "ttyS1" in tty_list or "ttyS1" in dmesg_text:
            if "gps" in dmesg_text.lower() or "ubnt_gps" in dmesg_text.lower() or "nmea" in dmesg_text.lower():
                return True
        return False

    @classmethod
    def parse_board_info(cls, system_info_text: str, board_info_text: str) -> tuple[str, Optional[str]]:
        """Extracts model name and board ID from /proc/ubnthal/."""
        combined = f"{system_info_text}\n{board_info_text}"
        board_id = None
        m_bid = re.search(r"board\.sysid=([0-9a-fxA-FX]+)", combined, re.IGNORECASE)
        if not m_bid:
            m_bid = re.search(r"sysid=([0-9a-fxA-FX]+)", combined, re.IGNORECASE)
        if m_bid:
            board_id = m_bid.group(1).lower()

        m_name = re.search(r"system\.model=([^\n]+)", combined)
        if not m_name:
            m_name = re.search(r"board\.name=([^\n]+)", combined)
        
        if m_name:
            model_name = m_name.group(1).strip()
        elif board_id and board_id in KNOWN_BOARD_IDS:
            model_name = KNOWN_BOARD_IDS[board_id]
        else:
            model_name = "Generic airMAX AC"

        return model_name, board_id

    @classmethod
    def probe_device_facts(
        cls,
        cpuinfo: str,
        meminfo: str,
        mtd: str,
        lspci: str,
        etc_version: str,
        os_release: str,
        dmesg: str,
        lsmod: str,
        system_info: str = "",
        board_info: str = "",
        tty_list: str = "",
    ) -> BoardIdentity:
        """Synthesizes raw probe outputs into a unified BoardIdentity dataclass."""
        errors: List[str] = []

        cpu_data = cls.parse_cpuinfo(cpuinfo)
        ram_bytes = cls.parse_meminfo(meminfo)
        partitions = cls.parse_mtd(mtd)
        pci_id = cls.parse_lspci(lspci)
        os_type, os_ver = cls.parse_os_release(etc_version, os_release)
        drv, drv_variant, fw_ver = cls.parse_wireless_drivers(f"{dmesg}\n{lsmod}")
        has_gps = cls.detect_gps(dmesg, tty_list)
        model_name, board_id = cls.parse_board_info(system_info, board_info)

        # Calculate total flash size by summing partitions (excluding virtual 'firmware' or duplicate blocks)
        total_flash = 0
        has_uboot = False
        has_art = False
        for p in partitions:
            if p.name == "u-boot":
                has_uboot = True
            if p.name in ("EEPROM", "ART", "caldata"):
                has_art = True
            if p.dev_name == "mtd0" or "spi" in p.dev_name or p.name in ("u-boot", "kernel", "rootfs", "cfg", "EEPROM", "ART"):
                total_flash += p.size_bytes

        # Standard airMAX flash is 16 MB (16,777,216 bytes)
        flash_bytes = 16777216 if total_flash == 0 else total_flash

        # Chipset mapping
        chipset = "Qualcomm Atheros QCA9880 / QCA9882 (Wave 1)" if pci_id == PCI_QCA9880 else "Unknown Radio"

        # Check protected partitions
        protected_intact = has_uboot and has_art
        if not protected_intact:
            errors.append("Critical partitions missing: u-boot or ART not identified in MTD table")

        # Validate lab unit compatibility
        is_supported = (
            ("ar9342" in cpu_data["soc"].lower() or "qca956" in cpu_data["soc"].lower() or "74kc" in cpu_data["cpu"].lower())
            and (pci_id == PCI_QCA9880 or pci_id == "unknown")
            and (50 * 1024 * 1024 <= ram_bytes <= 256 * 1024 * 1024)
        )

        if not is_supported:
            errors.append(f"Hardware not recognized as supported airMAX AC platform (SoC: {cpu_data['soc']}, RAM: {ram_bytes}B)")

        return BoardIdentity(
            os_type=os_type,
            os_version=os_ver,
            model_name=model_name,
            board_id=board_id,
            soc_model=cpu_data["soc"],
            cpu_arch=cpu_data["cpu"],
            ram_bytes=ram_bytes,
            flash_bytes=flash_bytes,
            radio_pci_id=pci_id,
            radio_chipset=chipset,
            wireless_driver=drv,
            driver_variant=drv_variant,
            firmware_version=fw_ver,
            has_gps=has_gps,
            partitions=partitions,
            protected_partitions_intact=protected_intact,
            is_supported_lab_unit=is_supported,
            validation_errors=errors,
        )
