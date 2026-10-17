"""Binary wire protocol serializer and deserializer for airMAX AC / QCA988x.

Based on the verified static datapath analysis and reverse engineering findings
documented in docs/UMAC_DATAPATH.md:
- WMI Native Rate Schedule: 188-byte payload (Gen1 opcode 0x9044, Gen2 opcode 0x9045)
- airMAX Poll Subtype 0x1E: 16-byte Rate Override matching Xtensa firmware deserializer at 0x009b7684
- airMAX Poll Subtype 0x17: 20-byte Contention / TXQ parameters (AIFS, CWmin, CWmax, Qflags 0x3a10)
- HTT Type 5 Aggregation Config: Packed 32-bit word 5 | (max_ampdu << 8) | (max_amsdu << 16)
- Endianness swap: 32-bit dword byte reversal between Big-Endian MIPS host and Little-Endian Xtensa target
"""

from __future__ import annotations

import struct
from typing import Sequence, Union

# WMI Command Identifiers
WMI_RATE_SCHED_CMDID_GEN1 = 0x9044  # WA / XC (Gen1)
WMI_RATE_SCHED_CMDID_GEN2 = 0x9045  # 2WA / 2XC (Gen2)

WMI_UBNT_POLL_CMDID_GEN1 = 0x9064   # WA / XC
WMI_UBNT_POLL_CMDID_GEN2 = 0x9070   # 2WA / 2XC

# airMAX Poll Subtype Identifiers
POLL_SUBTYPE_TXQ = 0x0017           # 20-byte contention parameters
POLL_SUBTYPE_RATE_OVERRIDE = 0x001E # 16-byte rate override

# HTT Aggregation Tag
HTT_TAG_AGGR_CFG = 5

# TXQ Contention Bitmask (bits 4, 9, 11, 12, 13)
TXQ_QFLAGS_MASK = 0x3A10

# WHAL Rate Table Base Indices (VHT)
WHAL_VHT20_BASE_INDEX = 60
WHAL_VHT40_BASE_INDEX = 90
WHAL_VHT80_BASE_INDEX = 120

WHAL_HT20_BASE_INDEX = 12
WHAL_HT40_BASE_INDEX = 36


def normalize_bw(bw: Union[int, str]) -> int:
    """Normalize bandwidth to integer MHz (20, 40, or 80)."""
    if isinstance(bw, str):
        cleaned = bw.strip().lower().replace("mhz", "")
        try:
            bw = int(cleaned)
        except ValueError:
            raise ValueError(f"Invalid bandwidth specification: {bw}")
    if bw in (20, 0x14):
        return 20
    elif bw in (40, 0x28):
        return 40
    elif bw in (80, 0x50):
        return 80
    else:
        raise ValueError(f"Unsupported bandwidth: {bw} MHz. Must be 20, 40, or 80.")


def get_whal_rate_index(mcs: int, nss: int = 1, bw: Union[int, str] = 20, is_vht: bool = True) -> int:
    """Compute the WHAL rate table row index (0..149).

    Based on UMAC_DATAPATH.md Table B:
    - Group 4 (VHT20): rows 60..89 (10 MCS per stream)
    - Group 5 (VHT40): rows 90..119 (10 MCS per stream)
    - Group 6 (VHT80): rows 120..149 (10 MCS per stream)
    - Group 2 (HT20): rows 12..35 (8 MCS per stream)
    - Group 3 (HT40): rows 36..59 (8 MCS per stream)
    """
    bw_mhz = normalize_bw(bw)
    if not (1 <= nss <= 3):
        raise ValueError(f"NSS must be 1, 2, or 3, got {nss}")

    if is_vht:
        if not (0 <= mcs <= 9):
            raise ValueError(f"VHT MCS must be 0..9, got {mcs}")
        if bw_mhz == 20:
            base = WHAL_VHT20_BASE_INDEX
        elif bw_mhz == 40:
            base = WHAL_VHT40_BASE_INDEX
        elif bw_mhz == 80:
            base = WHAL_VHT80_BASE_INDEX
        else:
            raise ValueError(f"Unsupported VHT bandwidth: {bw_mhz}")
        return base + (nss - 1) * 10 + mcs
    else:
        if not (0 <= mcs <= 7):
            raise ValueError(f"HT MCS must be 0..7, got {mcs}")
        if bw_mhz == 20:
            base = WHAL_HT20_BASE_INDEX
        elif bw_mhz == 40:
            base = WHAL_HT40_BASE_INDEX
        else:
            raise ValueError(f"Unsupported HT bandwidth: {bw_mhz}")
        return base + (nss - 1) * 8 + mcs


def get_whal_code_byte(mcs: int, nss: int = 1, is_vht: bool = True) -> int:
    """Compute WHAL rate code byte (UMAC_DATAPATH.md line 257).

    Prefix: 0xC0 for VHT, 0x80 for HT.
    Bits 4..5: NSS - 1.
    Low 4 bits: MCS.
    """
    if not (1 <= nss <= 3):
        raise ValueError(f"NSS must be 1, 2, or 3, got {nss}")
    prefix = 0xC0 if is_vht else 0x80
    stream_block = (nss - 1) & 0x03
    return prefix | (stream_block << 4) | (mcs & 0x0F)


def encode_rate_byte(mcs: int, bw: Union[int, str] = 20, nss: int = 1) -> int:
    """Encode airMAX rate override byte matching Xtensa firmware deserializer at 0x009b7684.

    Formula from UMAC_DATAPATH.md line 445:
    RateByte = ((MCS << 1) & 0x1E) | BandwidthFlag | StreamFlag
    where:
    - BandwidthFlag = 0x20 for 40MHz (0x28), 0x40 for 80MHz (0x50), 0x00 for 20MHz
    - StreamFlag = 1 for 2 streams (NSS >= 2), 0 for 1 stream
    - MCS ordinal is placed in bits 1..4
    """
    if not (0 <= mcs <= 9):
        raise ValueError(f"MCS must be 0..9, got {mcs}")

    bw_mhz = normalize_bw(bw)
    if bw_mhz == 40:
        bw_flag = 0x20
    elif bw_mhz == 80:
        bw_flag = 0x40
    else:
        bw_flag = 0x00

    stream_flag = 1 if nss > 1 else 0
    return ((mcs << 1) & 0x1E) | bw_flag | stream_flag


def decode_rate_byte(rate_byte: int) -> tuple[int, int, int]:
    """Decode airMAX rate override byte into (mcs, bw_mhz, nss)."""
    stream_flag = rate_byte & 0x01
    nss = 2 if stream_flag else 1

    mcs = (rate_byte & 0x1E) >> 1

    bw_flag = rate_byte & 0x60
    if bw_flag == 0x20:
        bw_mhz = 40
    elif bw_flag == 0x40:
        bw_mhz = 80
    else:
        bw_mhz = 20

    return (mcs, bw_mhz, nss)


def endian_swap_dword(data: Union[bytes, bytearray, int], pad: bool = False) -> Union[bytes, int]:
    """Perform 32-bit dword endianness swap between Big-Endian MIPS and Little-Endian Xtensa.

    In UMAC_DATAPATH.md:
    "Send length is (prepared_length+3)&~3; the exact dword-swap function reverses
     every four-byte chunk IN PLACE before the WMI send."
    """
    if isinstance(data, int):
        return (
            ((data & 0x000000FF) << 24)
            | ((data & 0x0000FF00) << 8)
            | ((data & 0x00FF0000) >> 8)
            | ((data & 0xFF000000) >> 24)
        )

    b = bytearray(data)
    rem = len(b) % 4
    if rem != 0:
        if pad:
            b.extend(b"\x00" * (4 - rem))
        else:
            raise ValueError(f"Data length ({len(b)}) must be a multiple of 4 bytes for dword swap")

    for i in range(0, len(b), 4):
        b[i], b[i + 1], b[i + 2], b[i + 3] = b[i + 3], b[i + 2], b[i + 1], b[i]

    return bytes(b)


def build_htt_type5_aggr_cfg(max_ampdu: int, max_amsdu: int) -> int:
    """Build HTT type 5 aggregation configuration 32-bit packed word.

    From UMAC_DATAPATH.md lines 189-194:
    htt_h2t_aggr_cfg_msg constructs a four-byte CPU word:
    tag 5 | (max_ampdu << 8) | (max_amsdu << 16)
    where max_ampdu is bounded (1..64) and max_amsdu is bounded (1..31).
    """
    if not (0 <= max_ampdu <= 64):
        raise ValueError(f"max_ampdu must be 0..64, got {max_ampdu}")
    if not (0 <= max_amsdu <= 31):
        raise ValueError(f"max_amsdu must be 0..31, got {max_amsdu}")

    return HTT_TAG_AGGR_CFG | ((max_ampdu & 0xFF) << 8) | ((max_amsdu & 0xFF) << 16)


def parse_htt_type5_aggr_cfg(word: Union[int, bytes]) -> tuple[int, int]:
    """Parse HTT type 5 packed word into (max_ampdu, max_amsdu)."""
    if isinstance(word, bytes):
        if len(word) != 4:
            raise ValueError(f"Expected 4 bytes for HTT aggr cfg, got {len(word)}")
        val = struct.unpack(">I", word)[0]
    else:
        val = word

    tag = val & 0xFF
    if tag != HTT_TAG_AGGR_CFG:
        raise ValueError(f"Expected HTT tag {HTT_TAG_AGGR_CFG}, got {tag}")

    max_ampdu = (val >> 8) & 0xFF
    max_amsdu = (val >> 16) & 0xFF
    return (max_ampdu, max_amsdu)


def build_poll_subtype_17_txq(
    aifs: int,
    cwmin: int,
    cwmax: int,
    qflags: int,
    q_id: int = 0,
    swap_endian: bool = False,
) -> bytes:
    """Serialize 20-byte contention parameters for airMAX Poll Subtype 0x17.

    From UMAC_DATAPATH.md lines 87-100, 411-436:
    Header (9 bytes):
      offset 0..3: 00 00 00 01 (Version 1, big endian)
      offset 4:    00          (record+4)
      offset 5..6: 00 17       (Subtype 0x17, big endian)
      offset 7..8: 00 00       (record+8)
    Payload fields (11 bytes):
      offset 9:     q_id       (record+c)
      offset 10..11: aifs      (unsigned halfword, big endian)
      offset 12..13: cwmin     (unsigned halfword, big endian)
      offset 14..15: cwmax     (unsigned halfword, big endian)
      offset 16..19: qflags    (unsigned word, big endian, bitmasked with 0x3a10)
    Total: exactly 20 bytes (already 4-byte aligned).
    """
    if not (0 <= aifs <= 0xFFFF):
        raise ValueError(f"aifs must be 0..65535, got {aifs}")
    if not (0 <= cwmin <= 0xFFFF):
        raise ValueError(f"cwmin must be 0..65535, got {cwmin}")
    if not (0 <= cwmax <= 0xFFFF):
        raise ValueError(f"cwmax must be 0..65535, got {cwmax}")

    # Enforce verified hardware bitmask 0x3a10 (bits 4, 9, 11, 12, 13)
    masked_qflags = qflags & TXQ_QFLAGS_MASK

    buf = bytearray(20)
    # Header: bytes 0..3 = 00 00 00 01
    struct.pack_into(">I", buf, 0, 1)
    buf[4] = 0x00
    # Bytes 5..6 = subtype 0x0017
    struct.pack_into(">H", buf, 5, POLL_SUBTYPE_TXQ)
    struct.pack_into(">H", buf, 7, 0x0000)

    # Payload
    buf[9] = q_id & 0xFF
    struct.pack_into(">H", buf, 10, aifs)
    struct.pack_into(">H", buf, 12, cwmin)
    struct.pack_into(">H", buf, 14, cwmax)
    struct.pack_into(">I", buf, 16, masked_qflags)

    out = bytes(buf)
    if swap_endian:
        out = endian_swap_dword(out)
    return out


def parse_poll_subtype_17_txq(data: bytes, is_swapped: bool = False) -> dict:
    """Parse 20-byte airMAX Poll Subtype 0x17 message."""
    if len(data) != 20:
        raise ValueError(f"Expected 20 bytes for Subtype 0x17, got {len(data)}")

    raw = endian_swap_dword(data) if is_swapped else data

    version = struct.unpack_from(">I", raw, 0)[0]
    subtype = struct.unpack_from(">H", raw, 5)[0]
    if subtype != POLL_SUBTYPE_TXQ:
        raise ValueError(f"Expected subtype 0x{POLL_SUBTYPE_TXQ:04x}, got 0x{subtype:04x}")

    q_id = raw[9]
    aifs = struct.unpack_from(">H", raw, 10)[0]
    cwmin = struct.unpack_from(">H", raw, 12)[0]
    cwmax = struct.unpack_from(">H", raw, 14)[0]
    qflags = struct.unpack_from(">I", raw, 16)[0]

    return {
        "version": version,
        "subtype": subtype,
        "q_id": q_id,
        "aifs": aifs,
        "cwmin": cwmin,
        "cwmax": cwmax,
        "qflags": qflags,
        "qflags_valid_mask": (qflags & ~TXQ_QFLAGS_MASK) == 0,
    }


def build_poll_subtype_1e_rate_override(
    mcs: int,
    bw: Union[int, str] = 20,
    nss: int = 1,
    secondary_mcs: int | None = None,
    secondary_bw: Union[int, str, None] = None,
    secondary_nss: int | None = None,
    node_id: int = 0,
    flags: int = 0,
    raw_entry_1b: int = 0,
    swap_endian: bool = False,
) -> bytes:
    """Serialize 16-byte airMAX rate override matching Xtensa firmware deserializer at 0x009b7684.

    From UMAC_DATAPATH.md lines 411-447:
    Header (9 bytes):
      offset 0..3: 00 00 00 01 (Version 1, big endian)
      offset 4:    00          (record+4)
      offset 5..6: 00 1E       (Subtype 0x1E, big endian)
      offset 7..8: 00 00       (record+8)
    Payload fields (5 bytes, offsets 9..13):
      offset 9:    node_id     (record+c, original a1 byte)
      offset 10:   flags       (record+d, original a2 byte)
      offset 11:   RateByte    (record+e, primary rate override)
      offset 12:   raw_entry   (record+f, entry_stack[1b])
      offset 13:   SecRateByte (record+10, secondary rate override or 0)
    Padding (2 bytes, offsets 14..15):
      00 00 (aligned from 14 to 16 bytes: (14+3)&~3 = 16)
    Total: exactly 16 bytes.
    """
    primary_rate_byte = encode_rate_byte(mcs, bw, nss)

    if secondary_mcs is not None:
        sec_bw = bw if secondary_bw is None else secondary_bw
        sec_nss = nss if secondary_nss is None else secondary_nss
        secondary_rate_byte = encode_rate_byte(secondary_mcs, sec_bw, sec_nss)
    else:
        secondary_rate_byte = 0x00

    buf = bytearray(16)
    # Header: bytes 0..3 = 00 00 00 01
    struct.pack_into(">I", buf, 0, 1)
    buf[4] = 0x00
    # Bytes 5..6 = subtype 0x001E
    struct.pack_into(">H", buf, 5, POLL_SUBTYPE_RATE_OVERRIDE)
    struct.pack_into(">H", buf, 7, 0x0000)

    # Payload
    buf[9] = node_id & 0xFF
    buf[10] = flags & 0xFF
    buf[11] = primary_rate_byte & 0xFF
    buf[12] = raw_entry_1b & 0xFF
    buf[13] = secondary_rate_byte & 0xFF
    # Offsets 14..15 are 0x00 zero padding
    buf[14] = 0x00
    buf[15] = 0x00

    out = bytes(buf)
    if swap_endian:
        out = endian_swap_dword(out)
    return out


def parse_poll_subtype_1e_rate_override(data: bytes, is_swapped: bool = False) -> dict:
    """Parse 16-byte airMAX Poll Subtype 0x1E message."""
    if len(data) != 16:
        raise ValueError(f"Expected 16 bytes for Subtype 0x1E, got {len(data)}")

    raw = endian_swap_dword(data) if is_swapped else data

    version = struct.unpack_from(">I", raw, 0)[0]
    subtype = struct.unpack_from(">H", raw, 5)[0]
    if subtype != POLL_SUBTYPE_RATE_OVERRIDE:
        raise ValueError(f"Expected subtype 0x{POLL_SUBTYPE_RATE_OVERRIDE:04x}, got 0x{subtype:04x}")

    node_id = raw[9]
    flags = raw[10]
    primary_rate_byte = raw[11]
    raw_entry_1b = raw[12]
    secondary_rate_byte = raw[13]

    p_mcs, p_bw, p_nss = decode_rate_byte(primary_rate_byte)
    s_mcs, s_bw, s_nss = decode_rate_byte(secondary_rate_byte) if secondary_rate_byte else (None, None, None)

    return {
        "version": version,
        "subtype": subtype,
        "node_id": node_id,
        "flags": flags,
        "primary_rate_byte": primary_rate_byte,
        "primary_mcs": p_mcs,
        "primary_bw": p_bw,
        "primary_nss": p_nss,
        "secondary_rate_byte": secondary_rate_byte,
        "secondary_mcs": s_mcs,
        "secondary_bw": s_bw,
        "secondary_nss": s_nss,
        "raw_entry_1b": raw_entry_1b,
    }


class WmiRateSchedule(bytes):
    """188-byte WMI Native Rate Schedule payload with command metadata."""

    opcode: int
    gen: int
    row_index: int
    code_byte: int
    mcs: int
    nss: int
    bw: int

    def __new__(
        cls,
        data: bytes,
        opcode: int,
        gen: int,
        row_index: int,
        code_byte: int,
        mcs: int,
        nss: int,
        bw: int,
    ):
        obj = super().__new__(cls, data)
        obj.opcode = opcode
        obj.gen = gen
        obj.row_index = row_index
        obj.code_byte = code_byte
        obj.mcs = mcs
        obj.nss = nss
        obj.bw = bw
        return obj


def build_wmi_rate_schedule_188b(
    mcs: int,
    nss: int = 1,
    bw: Union[int, str] = 20,
    gen: int = 1,
    opcode: int | None = None,
    node_id: int = 0,
    mac: Union[bytes, str, None] = None,
    retry_count: int = 4,
    series_indices: Sequence[int] | None = None,
    swap_endian: bool = False,
) -> WmiRateSchedule:
    """Serialize 188-byte native rate schedule (Gen1 opcode 0x9044, Gen2 opcode 0x9045).

    From UMAC_DATAPATH.md lines 135-186:
    Total size: 0xBC (188 bytes).
    Layout:
      +0x00: word store (incoming a2, node_id / handle)
      +0x04: word (MAC address bytes 0..3)
      +0x08: word (MAC address bytes 4..5, 2 zero padding bytes)
      +0x0C..0x20: 6 words (rate series row indices from WHAL table)
      +0x24..0x38: 6 words (retry counts per stage, expanded from halfwords)
      +0x3C..0x50: 6 words (per-stage flags / power, expanded from bytes)
      +0x54..0x68: 6 words (per-stage antenna / stream mask, expanded from bytes)
      +0x6C..0x80: 6 words (third array cursor / modulation, expanded from bytes)
      +0x84..0xB8: 14 words (56 bytes scalar configuration copies)
    """
    bw_mhz = normalize_bw(bw)
    primary_row_index = get_whal_rate_index(mcs, nss, bw_mhz, is_vht=True)
    code_byte = get_whal_code_byte(mcs, nss, is_vht=True)

    if opcode is None:
        if gen == 2:
            resolved_opcode = WMI_RATE_SCHED_CMDID_GEN2
        else:
            resolved_opcode = WMI_RATE_SCHED_CMDID_GEN1
    else:
        resolved_opcode = opcode

    resolved_gen = 2 if resolved_opcode == WMI_RATE_SCHED_CMDID_GEN2 else 1

    buf = bytearray(188)

    # +0x00: Node ID / handle word store
    struct.pack_into(">I", buf, 0x00, node_id)

    # +0x04, +0x08: MAC address (6 bytes)
    mac_bytes = b"\x00" * 6
    if mac is not None:
        if isinstance(mac, str):
            cleaned_mac = mac.replace(":", "").replace("-", "")
            mac_bytes = bytes.fromhex(cleaned_mac)
        elif isinstance(mac, (bytes, bytearray)):
            mac_bytes = bytes(mac)[:6].ljust(6, b"\x00")
    buf[0x04:0x08] = mac_bytes[0:4]
    buf[0x08:0x0A] = mac_bytes[4:6]
    buf[0x0A:0x0C] = b"\x00\x00"

    # +0x0C..0x20: Six words for rate row indices
    if series_indices is not None:
        indices = list(series_indices)[:6]
        while len(indices) < 6:
            indices.append(indices[-1] if indices else primary_row_index)
    else:
        indices = [primary_row_index] * 6

    for i, idx in enumerate(indices):
        struct.pack_into(">I", buf, 0x0C + i * 4, idx)

    # +0x24..0x38: Six halfwords expanded to 32-bit word slots (retry counts)
    for i in range(6):
        struct.pack_into(">I", buf, 0x24 + i * 4, retry_count)

    # +0x3C..0x50: Six bytes expanded to 32-bit word slots (power/flags)
    for i in range(6):
        struct.pack_into(">I", buf, 0x3C + i * 4, 0)

    # +0x54..0x68: Six bytes expanded to 32-bit word slots (stream masks)
    for i in range(6):
        struct.pack_into(">I", buf, 0x54 + i * 4, nss)

    # +0x6C..0x80: Six bytes expanded to 32-bit word slots (modulation/cursor)
    for i in range(6):
        struct.pack_into(">I", buf, 0x6C + i * 4, 0)

    # +0x84..0xB8: 14 scalar configuration words (offsets 0x84, 0x88, ..., 0xB8)
    for i in range(14):
        struct.pack_into(">I", buf, 0x84 + i * 4, 0)

    payload = bytes(buf)
    if swap_endian:
        payload = endian_swap_dword(payload)

    return WmiRateSchedule(
        payload,
        opcode=resolved_opcode,
        gen=resolved_gen,
        row_index=primary_row_index,
        code_byte=code_byte,
        mcs=mcs,
        nss=nss,
        bw=bw_mhz,
    )


def parse_wmi_rate_schedule_188b(data: bytes, is_swapped: bool = False) -> dict:
    """Parse 188-byte native rate schedule payload."""
    if len(data) != 188:
        raise ValueError(f"Expected 188 bytes for native rate schedule, got {len(data)}")

    raw = endian_swap_dword(data) if is_swapped else data

    node_id = struct.unpack_from(">I", raw, 0x00)[0]
    mac_bytes = raw[0x04:0x0A]
    mac_str = ":".join(f"{b:02x}" for b in mac_bytes)

    rate_series = [struct.unpack_from(">I", raw, 0x0C + i * 4)[0] for i in range(6)]
    retry_counts = [struct.unpack_from(">I", raw, 0x24 + i * 4)[0] for i in range(6)]
    power_flags = [struct.unpack_from(">I", raw, 0x3C + i * 4)[0] for i in range(6)]
    stream_masks = [struct.unpack_from(">I", raw, 0x54 + i * 4)[0] for i in range(6)]
    cursors = [struct.unpack_from(">I", raw, 0x6C + i * 4)[0] for i in range(6)]
    scalar_words = [struct.unpack_from(">I", raw, 0x84 + i * 4)[0] for i in range(14)]

    return {
        "node_id": node_id,
        "mac": mac_str,
        "primary_row_index": rate_series[0],
        "rate_series": rate_series,
        "retry_counts": retry_counts,
        "power_flags": power_flags,
        "stream_masks": stream_masks,
        "cursors": cursors,
        "scalar_words": scalar_words,
    }
