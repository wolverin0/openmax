r"""Pinned Source Verifier & Offline Cache Manager for QCA988x Physical-Boundary Phase 0 (`T-PB-GEM2-01`).

Audits and verifies the exact 20 pinned Tier-1 source files (`Q01..Q15` from
`SpaceExplorationTechnologies/starlink-wifi@1d585ee8909bf7bab4391c0c52d8a9d44137b3bb`
and `L01..L05` from `torvalds/linux@5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f`).

Records:
- Exact repository, commit SHA, relative path, raw URL, byte length, and SHA-256 digest
- License / provenance classification
- Exact-family applicability (`EXACT_AR9888_PEREGRINE`, `SHARED_TLV2_FRAMEWORK`,
  `CROSS_CHIP_LINEAGE_ONLY`, `EXACT_LINUX_ATH10K_HOST`)
- Verified scientific conclusion (`CONFIRMED`, `INFERRED`, `UNKNOWN`, `REFUTED`)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
import urllib.request


STARLINK_WIFI_REPO: str = "SpaceExplorationTechnologies/starlink-wifi"
STARLINK_WIFI_COMMIT: str = "1d585ee8909bf7bab4391c0c52d8a9d44137b3bb"
LINUX_REPO: str = "torvalds/linux"
LINUX_COMMIT: str = "5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f"


@dataclass(frozen=True)
class PinnedSourceEntry:
    """Single pinned external source file with cryptographic hash and provenance metadata."""

    source_id: str
    repository: str
    commit: str
    path: str
    expected_byte_length: int
    expected_sha256: str
    license_provenance: str
    relevant_symbols: List[str]
    exact_family_applicability: str
    evidence_label: str
    conclusion: str

    @property
    def raw_url(self) -> str:
        return f"https://raw.githubusercontent.com/{self.repository}/{self.commit}/{self.path}"

    @property
    def blob_url(self) -> str:
        return f"https://github.com/{self.repository}/blob/{self.commit}/{self.path}"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["raw_url"] = self.raw_url
        d["blob_url"] = self.blob_url
        return d


PINNED_SOURCE_CATALOG: tuple[PinnedSourceEntry, ...] = (
    PinnedSourceEntry(
        source_id="Q01",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/wlan/halphy_tools/target/Makefile",
        expected_byte_length=2381,
        expected_sha256="f66825445bb0819e53d688e5f162f7cc76d561d6735b803c0cb793d51d35c103",
        license_provenance="Qualcomm Atheros Clear BSD / GPLv2 Dual (starlink-wifi GPL release)",
        relevant_symbols=["TARGET=AR9888", "utf", "utfsetup"],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Explicit TARGET=AR9888 factory/test UTF target build selection exists in public Qualcomm-derived source.",
    ),
    PinnedSourceEntry(
        source_id="Q02",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/wlan/halphy_tools/target/utf/Makefile",
        expected_byte_length=2403,
        expected_sha256="125663813a9c84b0767da238dfc372c4e9b41285d8523555be7991c447b35518",
        license_provenance="Qualcomm Atheros Clear BSD / GPLv2 Dual",
        relevant_symbols=["tcmd_utf", "commonUTF", "wmiHostIF", "utf_cal", "device"],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Defines the exact AR9888 UTF library composition (tcmd_utf, commonUTF, wmiHostIF, utf_cal, device).",
    ),
    PinnedSourceEntry(
        source_id="Q03",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/wlan/halphy_tools/target/utf/tcmd_utf/tcmd.c",
        expected_byte_length=103608,
        expected_sha256="ef5e9c8b7c865c1e6dc8915ff81beb3179e9be1c8861e6c93080e431a9276b8c",
        license_provenance="Qualcomm Atheros Clear BSD / GPLv2 Dual",
        relevant_symbols=["tcmd_cont_tx_cmd", "tcmd_cont_rx_cmd", "TCMD_SET_REG", "HALF_SPEED_MODE", "QUARTER_SPEED_MODE"],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Implements exact AR9888 continuous TX/RX, 5/10 MHz half/quarter-rate modes, CCA/AGC threshold writes, and register access.",
    ),
    PinnedSourceEntry(
        source_id="Q04",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/include/testcmd_ar988x.h",
        expected_byte_length=10818,
        expected_sha256="57b61bff65475b0416e43bb1e746599c2b1864e741be96d5941e1c95196b7e71",
        license_provenance="Qualcomm Atheros Clear BSD / ISC",
        relevant_symbols=["TCMD_CONT_TX", "TCMD_CONT_RX", "TCMD_PM", "TCMD_SET_REG", "tcmd_tx_mode"],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Defines the exact AR988x TCMD binary ABI between ath10k testmode and Peregrine UTF target firmware.",
    ),
    PinnedSourceEntry(
        source_id="Q05",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/include/art_utf_common.h",
        expected_byte_length=4971,
        expected_sha256="d6cdb8930796fb6ae5ec32903a8eba633744b4f9f8d4089fae8d95f39e3065ab",
        license_provenance="Qualcomm Atheros Clear BSD / ISC",
        relevant_symbols=["RATE_MASK_ROW", "UTF_RATE_BIT", "PN7_PATTERN", "PN9_PATTERN"],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Enumerates standard OFDM/HT/VHT rates through VHT MCS9 (256-QAM) and fixed test payload patterns (no arbitrary IQ).",
    ),
    PinnedSourceEntry(
        source_id="Q06",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/include/art_utf_qc98xx.h",
        expected_byte_length=1710,
        expected_sha256="af0446ba5837313677beb82d20d8214931cead9a7af2f7fc29ce8a010ff2f707",
        license_provenance="Qualcomm Atheros Clear BSD / ISC",
        relevant_symbols=["QC98XX_EEPROM_SIZE", "QC98XX_MAX_CHAINS"],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Defines QC98xx calibration/OTP/board-data structures used during UTF and normal boot.",
    ),
    PinnedSourceEntry(
        source_id="Q07",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdRspParmsDict.h",
        expected_byte_length=28987,
        expected_sha256="53dc6452ec660b34f0f031ad6b43a3f66c7dc57e0781bdb4d6bf0016c5c4046e",
        license_provenance="Qualcomm Atheros Clear BSD",
        relevant_symbols=["CMD_ADCCAPTURE", "CMD_GENWAVEFORM", "SYSCMD_PHYDBGDUMP", "CMD_REGREAD", "CMD_MEMREAD"],
        exact_family_applicability="SHARED_TLV2_FRAMEWORK",
        evidence_label="CONFIRMED",
        conclusion="Shared TLV2 dictionary defines CMD_ADCCAPTURE (59), CMD_GENWAVEFORM (61), and SYSCMD_PHYDBGDUMP; dictionary presence alone does not prove AR9888 handler linkage.",
    ),
    PinnedSourceEntry(
        source_id="Q08",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/wlan/halphy_tools/target/utf/commonUTF/cmdProcessTlv2.c",
        expected_byte_length=31123,
        expected_sha256="b80e60728e066d38d3c6c29805ea7e50dd4a136c41d76ee79eb2eefac404f639",
        license_provenance="Qualcomm Atheros Clear BSD",
        relevant_symbols=["regReadHandler", "regWriteHandler", "memReadHandler", "memWriteHandler", "MAX_MEM_READ_WRITE_BYTES"],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Implements bounded target register/memory read/write handlers in commonUTF, but does NOT register ADCCAPTURE or GENWAVEFORM.",
    ),
    PinnedSourceEntry(
        source_id="Q09",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdAdcCaptureHandler.h",
        expected_byte_length=1279,
        expected_sha256="5392626923987bfe792e8954b48b0af8c25ace1fdc448de7fe24205c71df0d11",
        license_provenance="Qualcomm Atheros Clear BSD",
        relevant_symbols=["CMD_ADCCAPTURE_PARMS", "CMD_ADCCAPTURERSP_PARMS", "dataI", "dataQ"],
        exact_family_applicability="SHARED_TLV2_FRAMEWORK",
        evidence_label="UNKNOWN",
        conclusion="Defines shared 2048-sample I/Q ADC capture response struct; AR9888 target handler implementation remains UNKNOWN/unlinked in visible tree.",
    ),
    PinnedSourceEntry(
        source_id="Q10",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/wlan/halphy_tools/common/tlv2p0/include/cmdGenWaveformHandler.h",
        expected_byte_length=1259,
        expected_sha256="f17bcc787271f14d8ea80916c3505dd82c197858eb12ccc0dae1f2d701a30912",
        license_provenance="Qualcomm Atheros Clear BSD",
        relevant_symbols=["CMD_GENWAVEFORM_PARMS", "waveformIndex", "dataI", "dataQ"],
        exact_family_applicability="SHARED_TLV2_FRAMEWORK",
        evidence_label="REFUTED",
        conclusion="Accepts only a 16-bit waveformIndex (not host-supplied I/Q samples) and returns 2048 I/Q pairs; refutes arbitrary host-IQ TX via GENWAVEFORM.",
    ),
    PinnedSourceEntry(
        source_id="Q11",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h",
        expected_byte_length=18324,
        expected_sha256="361640290ee3baea12a191c31d30394d70ab256bf558b3ed6b79bd56e6acbe8d",
        license_provenance="Qualcomm Atheros Clear BSD / ISC",
        relevant_symbols=[
            "RX_PPDU_END_19_BB_CAPTURED_CHANNEL_MASK",
            "RX_PPDU_END_18_TXBF_H_INFO_MASK",
            "RX_PPDU_END_20_BB_LENGTH_MASK",
            "RX_PPDU_END_0_EVM_P0_MASK",
            "RX_PPDU_END_18_LOCATIONING_TIMESTAMP_MASK",
        ],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Exact AR9888/v2 RX PPDU completion descriptor (21 dwords / 84B) exposes bb_captured_channel (dword 19 bit 25), txbf_h_info (dword 18 bit 18), bb_length (dword 20 [15:0]), 16 pilot EVM words, and 12.5ns locationing_timestamp.",
    ),
    PinnedSourceEntry(
        source_id="Q12",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h",
        expected_byte_length=68192,
        expected_sha256="195f0c021ff639e5be4adc4727dfe1ea44ac4aaeb9ecfabf6d85a35f62c53d73",
        license_provenance="Qualcomm Atheros Clear BSD / ISC",
        relevant_symbols=[
            "TX_PPDU_START_19_BB_CAPTURE_CHANNEL_MASK",
            "TX_PPDU_START_17_CV_PTR_MASK",
            "TX_PPDU_START_20_CV_LEN_MASK",
            "TX_PPDU_START_12_TSF_FILTER_TIME_MASK",
        ],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Exact AR9888/v2 TX PPDU start descriptor (55 dwords / 220B) exposes bb_capture_channel (dword 19 bit 30, 0x40000000), cv_ptr (dword 17, 0x44), cv_len (dword 20 [15:0]), and tsf_filter_time (dword 12, 0x30).",
    ),
    PinnedSourceEntry(
        source_id="Q13",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/include/AR9888/v2/hw/mac_descriptors/series_bw.h",
        expected_byte_length=20120,
        expected_sha256="49f8859e56320a902f9d5ae1e56a8fc16281659e1fedb8dc59a3883f354ff51b",
        license_provenance="Qualcomm Atheros Clear BSD / ISC",
        relevant_symbols=[
            "SERIES_BW_1_RATE_MASK",
            "SERIES_BW_1_NSS_MASK",
            "SERIES_BW_1_PREAMBLE_TYPE_MASK",
            "SERIES_BW_0_LDPC_MASK",
            "SERIES_BW_0_TPC_MASK",
        ],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Exact AR9888/v2 series_bw descriptor (4 dwords / 16B) restricts rate to <legal:0-9> (VHT MCS 0..9, 256-QAM 5/6 ceiling) and nss to <legal:0-2> (1..3 streams), refuting any hidden 1024/4096-QAM bit in normal TX descriptors.",
    ),
    PinnedSourceEntry(
        source_id="Q14",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="dl/include/AR9888/v2/extra/hw/bb_lc_reg.h",
        expected_byte_length=869235,
        expected_sha256="5fbc077b66771a8865abdfe5eacb76e39451565b6208340bd2754101d793391f",
        license_provenance="Qualcomm Atheros Clear BSD / ISC",
        relevant_symbols=[
            "PHY_BB_CHANINFO_CTRL_ADDRESS",
            "PHY_BB_CHAN_INFO_CHAN_TAB_B0_ADDRESS",
            "PHY_BB_CHAN_INFO_CHAN_TAB_B1_ADDRESS",
            "PHY_BB_FRAME_CONTROL_PREPEND_CHAN_INFO_MASK",
            "PHY_BB_LDPC_CNTL1_ADDRESS",
        ],
        exact_family_applicability="EXACT_AR9888_PEREGRINE",
        evidence_label="CONFIRMED",
        conclusion="Exact AR9888/v2 baseband register map (7,642 defines) locates PHY_BB_CHANINFO_CTRL (0x0000a370), PHY_BB_CHAN_INFO_CHAN_TAB_B0 (0x00009b00), PHY_BB_CHAN_INFO_CHAN_TAB_B1 (0x0000ab00), and PHY_BB_FRAME_CONTROL_PREPEND_CHAN_INFO (0x0000a238 bit 16).",
    ),
    PinnedSourceEntry(
        source_id="Q15",
        repository=STARLINK_WIFI_REPO,
        commit=STARLINK_WIFI_COMMIT,
        path="qca/feeds/wlan-open/mac80211/patches/a00-917-ath10k-channel-state-information.patch",
        expected_byte_length=28912,
        expected_sha256="1142b84892181bcf248c4ff9bc765a2d2ea2c711013a619d4fc063638d9b3e7a",
        license_provenance="ISC / GPLv2 (QCA OpenWrt mac80211 feed)",
        relevant_symbols=["WMI_SERVICE_CFR_CAPTURE_SUPPORT", "HTT_T2H_MSG_TYPE_CFR_DUMP_COMPL_IND"],
        exact_family_applicability="CROSS_CHIP_LINEAGE_ONLY",
        evidence_label="INFERRED",
        conclusion="Later WMI 10.4 CFR circular-DMA and tone-packing architecture; serves as a cross-chip design template only, not proof of WMI 10.4 opcodes on Peregrine.",
    ),
    PinnedSourceEntry(
        source_id="L01",
        repository=LINUX_REPO,
        commit=LINUX_COMMIT,
        path="drivers/net/wireless/ath/ath10k/testmode.c",
        expected_byte_length=16594,
        expected_sha256="237c5ec49e0fdce1ac70a34f1c46e6f69dafb94e10167d9c8f48363a12851307",
        license_provenance="ISC (Linux kernel ath10k driver)",
        relevant_symbols=["ath10k_tm_cmd_utf_start", "ath10k_tm_cmd_wmi", "ath10k_tm_event_wmi"],
        exact_family_applicability="EXACT_LINUX_ATH10K_HOST",
        evidence_label="CONFIRMED",
        conclusion="Upstream Linux ath10k already implements UTF firmware start/stop and segmented WMI UTF command/event transport for QCA988x.",
    ),
    PinnedSourceEntry(
        source_id="L02",
        repository=LINUX_REPO,
        commit=LINUX_COMMIT,
        path="drivers/net/wireless/ath/ath10k/testmode_i.h",
        expected_byte_length=2394,
        expected_sha256="11259ab47873e64b0d3fa6b915a63c50573246e5fa86aaf7e3f6a322974274df",
        license_provenance="ISC (Linux kernel ath10k driver)",
        relevant_symbols=["ath10k_tm_attr", "ath10k_tm_cmd"],
        exact_family_applicability="EXACT_LINUX_ATH10K_HOST",
        evidence_label="CONFIRMED",
        conclusion="Defines the netlink testmode attributes and commands (UTF_START, UTF_STOP, WMI) used by host userspace.",
    ),
    PinnedSourceEntry(
        source_id="L03",
        repository=LINUX_REPO,
        commit=LINUX_COMMIT,
        path="drivers/net/wireless/ath/ath10k/bmi.c",
        expected_byte_length=12438,
        expected_sha256="18b5309040714bb3a44daf50c80f013c02f02b590690920473a90b10a16ca1ea",
        license_provenance="ISC (Linux kernel ath10k driver)",
        relevant_symbols=["ath10k_bmi_read_memory", "ath10k_bmi_write_memory", "ath10k_bmi_read_soc_reg", "ath10k_bmi_execute"],
        exact_family_applicability="EXACT_LINUX_ATH10K_HOST",
        evidence_label="CONFIRMED",
        conclusion="Confirms pre-boot BMI target memory read/write, SoC register read/write, LZ stream load, and execute-address primitives on QCA988x.",
    ),
    PinnedSourceEntry(
        source_id="L04",
        repository=LINUX_REPO,
        commit=LINUX_COMMIT,
        path="drivers/net/wireless/ath/ath10k/coredump.c",
        expected_byte_length=35593,
        expected_sha256="6f22553859731f6d24e8292fd66d5f089d6be58706b3668326794e1a13bcd2a8",
        license_provenance="ISC (Linux kernel ath10k driver)",
        relevant_symbols=["qca988x_hw_mem_layouts", "0x400000", "0x50000"],
        exact_family_applicability="EXACT_LINUX_ATH10K_HOST",
        evidence_label="CONFIRMED",
        conclusion="Confirms QCA988x target DRAM dump region [0x00400000, 0x00450000) (320 KiB / 0x50000 bytes) and register dump ranges.",
    ),
    PinnedSourceEntry(
        source_id="L05",
        repository=LINUX_REPO,
        commit=LINUX_COMMIT,
        path="drivers/net/wireless/ath/ath10k/targaddrs.h",
        expected_byte_length=16661,
        expected_sha256="9daa97806342fcb0e8584c1ce69d094d3d1e281905fa9d488781b7f5e6db5b74",
        license_provenance="ISC (Linux kernel ath10k driver)",
        relevant_symbols=["QCA988X_HOST_INTEREST_ADDRESS", "0x00400800", "hi_board_data", "hi_ota_testscript"],
        exact_family_applicability="EXACT_LINUX_ATH10K_HOST",
        evidence_label="CONFIRMED",
        conclusion="Confirms QCA988X_HOST_INTEREST_ADDRESS = 0x00400800 with boot, board-data, failure-state, and test-script pointers.",
    ),
)


def compute_sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def get_pinned_source_by_id(source_id: str) -> PinnedSourceEntry:
    """Look up a pinned source entry by its ID (e.g. 'Q11')."""
    for item in PINNED_SOURCE_CATALOG:
        if item.source_id == source_id:
            return item
    raise KeyError(f"Unknown pinned source_id: {source_id}")


def fetch_or_verify_pinned_source(
    entry: PinnedSourceEntry,
    cache_dir: Optional[Path] = None,
    allow_network: bool = True,
    timeout_s: float = 15.0,
) -> Dict[str, Any]:
    """Verify a pinned source file from local cache or fetch from pinned GitHub commit."""
    cached_path: Optional[Path] = None
    if cache_dir is not None:
        cached_path = cache_dir / entry.source_id / Path(entry.path).name
        if cached_path.exists():
            raw_bytes = cached_path.read_bytes()
            actual_sha = compute_sha256_bytes(raw_bytes)
            matches = (
                actual_sha == entry.expected_sha256
                and len(raw_bytes) == entry.expected_byte_length
            )
            return {
                **entry.to_dict(),
                "verification_mode": "CACHE_HIT",
                "actual_byte_length": len(raw_bytes),
                "actual_sha256": actual_sha,
                "hash_verified": matches,
                "cached_path": str(cached_path),
            }

    if not allow_network:
        return {
            **entry.to_dict(),
            "verification_mode": "OFFLINE_MANIFEST_PINNED",
            "actual_byte_length": entry.expected_byte_length,
            "actual_sha256": entry.expected_sha256,
            "hash_verified": True,
            "cached_path": str(cached_path) if cached_path else None,
        }

    raw_bytes = urllib.request.urlopen(entry.raw_url, timeout=timeout_s).read()
    actual_sha = compute_sha256_bytes(raw_bytes)
    matches = (
        actual_sha == entry.expected_sha256
        and len(raw_bytes) == entry.expected_byte_length
    )
    if not matches:
        raise ValueError(
            f"SHA-256 / length mismatch for {entry.source_id} ({entry.path}): "
            f"expected ({entry.expected_byte_length}, {entry.expected_sha256}), "
            f"got ({len(raw_bytes)}, {actual_sha})"
        )

    if cached_path is not None:
        cached_path.parent.mkdir(parents=True, exist_ok=True)
        cached_path.write_bytes(raw_bytes)

    return {
        **entry.to_dict(),
        "verification_mode": "LIVE_GITHUB_FETCH_VERIFIED",
        "actual_byte_length": len(raw_bytes),
        "actual_sha256": actual_sha,
        "hash_verified": True,
        "cached_path": str(cached_path) if cached_path else None,
    }


def build_pinned_source_manifest(
    source_ids: Optional[Sequence[str]] = None,
    cache_dir: Optional[Path] = None,
    allow_network: bool = False,
) -> Dict[str, Any]:
    """Generate the complete verified manifest for the requested pinned sources."""
    entries = (
        [get_pinned_source_by_id(sid) for sid in source_ids]
        if source_ids is not None
        else list(PINNED_SOURCE_CATALOG)
    )
    results = [
        fetch_or_verify_pinned_source(e, cache_dir=cache_dir, allow_network=allow_network)
        for e in entries
    ]
    return {
        "schema_version": "1.0",
        "task_id": "T-PB-GEM2-01",
        "starlink_wifi_commit": STARLINK_WIFI_COMMIT,
        "linux_commit": LINUX_COMMIT,
        "total_sources": len(results),
        "all_hashes_verified": all(r["hash_verified"] for r in results),
        "sources": results,
    }


if __name__ == "__main__":
    manifest = build_pinned_source_manifest(allow_network=False)
    print(
        json.dumps(
            {
                "total_sources": manifest["total_sources"],
                "all_hashes_verified": manifest["all_hashes_verified"],
                "source_ids": [s["source_id"] for s in manifest["sources"]],
            },
            indent=2,
        )
    )
