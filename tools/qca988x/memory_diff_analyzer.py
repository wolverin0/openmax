"""Workstream E5: QCA988x Target DRAM Memory-Diff & Channel-Dump / CFR Packing Analyzer.

Offline analysis engine for:
1. 4-byte aligned QCA988x Target DRAM snapshots (`0x00400000..0x0044ffff`,
   `QCA988X_DRAM_ADDR` / `QCA988X_DRAM_LEN` in `L01` `pci.c`) and Host-Interest
   table decoding (`0x00400800`, `L02` `hw.h`).
2. Multi-snapshot differential region clustering, monotonic counter identification,
   target DRAM/ROM pointer discovery, and Pearson correlation against packet /
   sounding frame counters.
3. Baseband Channel-Info table (`PHY_BB_CHAN_INFO_CHAN_TAB_B0 = 0x00009b00`,
   `PHY_BB_CHAN_INFO_CHAN_TAB_B1 = 0x0000ab00`) and `rx_ppdu_end.bb_length`
   complex tone-packing hypothesis scorer (`H_10BIT_IQ`, `H_12BIT_IQ`,
   `H_8BIT_IQ`, and `H_EXP_MANTISSA_CFR`).
"""

from __future__ import annotations

import json
import math
import struct
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

QCA988X_DRAM_ADDR = 0x00400000
QCA988X_DRAM_LEN = 0x00050000  # 327,680 bytes (0x00400000..0x0044ffff)
QCA988X_HOST_INTEREST_ADDR = 0x00400800
QCA988X_HOST_INTEREST_LEN = 312  # 78 uint32 words in struct host_interest (L02 hw.h)

QCA988X_ROM_ADDR_MIN = 0x00940000
QCA988X_ROM_ADDR_MAX = 0x009A0000

PHY_BB_CHAN_TAB_B0_ADDR = 0x00009B00
PHY_BB_CHAN_TAB_B1_ADDR = 0x0000AB00
PHY_BB_CHANINFO_CTRL_ADDR = 0x0000A370

OFDM_TONE_COUNTS = {
    "L_HT20_52": 52,
    "HT20_VHT20_56": 56,
    "HT40_108": 108,
    "VHT40_114": 114,
    "VHT80_234": 234,
    "VHT80_FULL_242": 242,
}

HOST_INTEREST_KNOWN_OFFSETS: Dict[int, Tuple[str, str]] = {
    0x00: ("hi_app_host_interest", "Pointer to application host interest area"),
    0x04: ("hi_failure_state", "Target assertion/crash state dump pointer"),
    0x08: ("hi_ubic_flags", "Target boot/interconnect flags"),
    0x1C: ("hi_board_data", "Target DRAM pointer to calibration board data"),
    0x20: ("hi_board_data_initialized", "1 when board data is loaded and valid"),
    0x4C: ("hi_dbglog_config", "Firmware debuglog ring configuration pointer"),
    0x70: ("hi_option_flag", "Firmware feature/mode option flags"),
    0xB0: ("hi_serial_enable", "Target UART serial console enable flag"),
    0xC4: ("hi_ACS_flags", "Automatic Channel Selection / spectral flags"),
    0x110: ("hi_ early_alloc", "Early target DRAM allocator state"),
}


@dataclass(frozen=True)
class MemoryDiffRegion:
    """Contiguous target memory region exhibiting changes across snapshots."""

    region_id: str
    start_address_hex: str
    end_address_hex: str
    start_offset: int
    byte_length: int
    word_count: int
    changed_word_count: int
    total_word_transitions: int
    monotonic_word_count: int
    dram_pointer_word_count: int
    rom_pointer_word_count: int
    packet_count_correlation: float
    classification: str
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TonePackingHypothesisScore:
    """Evaluation of a candidate complex tone-packing format on a channel dump."""

    hypothesis_id: str
    description: str
    family_applicability: str
    decoded_tone_count: int
    matched_ofdm_bandwidth_mode: str
    mean_magnitude: float
    magnitude_smoothness_cv: float
    adjacent_phase_step_std_rad: float
    linear_phase_coherence: float
    reserved_bits_zero_ratio: float
    composite_confidence_score: float
    sample_preview_iq: List[Tuple[int, int]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "sample_preview_iq": [[int(i), int(q)] for i, q in self.sample_preview_iq],
        }


def validate_four_byte_alignment(base_address: int, blob: bytes) -> None:
    """Enforce the 4-byte alignment invariant required by `ath10k_pci_diag_read_mem` (`L01`)."""
    if base_address % 4 != 0:
        raise ValueError(
            f"Base address 0x{base_address:08x} violates 4-byte CE diagnostic alignment."
        )
    if len(blob) == 0 or len(blob) % 4 != 0:
        raise ValueError(
            f"Snapshot byte length {len(blob)} must be non-zero and a multiple of 4 bytes."
        )


def unpack_le_words(blob: bytes) -> List[int]:
    """Unpack 4-byte aligned little-endian `uint32` words."""
    count = len(blob) // 4
    return list(struct.unpack(f"<{count}I", blob))


def is_target_dram_pointer(word: int) -> bool:
    """Return True if `word` falls inside QCA988x target DRAM (`0x00400000..0x0044ffff`) and is 4B-aligned."""
    return (QCA988X_DRAM_ADDR <= word < (QCA988X_DRAM_ADDR + QCA988X_DRAM_LEN)) and (
        word % 4 == 0
    )


def is_target_rom_pointer(word: int) -> bool:
    """Return True if `word` falls inside QCA988x target ROM (`0x00940000..0x0099ffff`)."""
    return QCA988X_ROM_ADDR_MIN <= word < QCA988X_ROM_ADDR_MAX


def _pearson_corr(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x <= 1e-12 or den_y <= 1e-12:
        return 0.0
    return max(-1.0, min(1.0, num / (den_x * den_y)))


def decode_host_interest_table(
    snapshot: bytes,
    base_address: int = QCA988X_DRAM_ADDR,
) -> Dict[str, Any]:
    """Decode known `QCA988X_HOST_INTEREST_ADDRESS` (`0x00400800`) fields if covered by snapshot."""
    validate_four_byte_alignment(base_address, snapshot)
    hi_start = QCA988X_HOST_INTEREST_ADDR - base_address
    hi_end = hi_start + QCA988X_HOST_INTEREST_LEN
    if hi_start < 0 or hi_end > len(snapshot):
        return {"covered_by_snapshot": False, "fields": {}}

    fields: Dict[str, Any] = {}
    for rel_offset, (name, desc) in HOST_INTEREST_KNOWN_OFFSETS.items():
        pos = hi_start + rel_offset
        val = struct.unpack_from("<I", snapshot, pos)[0]
        fields[name] = {
            "address_hex": f"0x{QCA988X_HOST_INTEREST_ADDR + rel_offset:08x}",
            "relative_offset_hex": f"0x{rel_offset:03x}",
            "value_hex": f"0x{val:08x}",
            "value_int": val,
            "is_dram_pointer": is_target_dram_pointer(val),
            "description": desc,
        }
    return {
        "covered_by_snapshot": True,
        "table_address_hex": f"0x{QCA988X_HOST_INTEREST_ADDR:08x}",
        "table_size_bytes": QCA988X_HOST_INTEREST_LEN,
        "fields": fields,
    }


def analyze_memory_snapshots(
    snapshots: Sequence[bytes],
    packet_counts: Sequence[int],
    base_address: int = QCA988X_DRAM_ADDR,
    max_gap_words: int = 4,
) -> Dict[str, Any]:
    """Diff a sequence of aligned memory snapshots and classify dynamic vs static regions."""
    if len(snapshots) < 2:
        raise ValueError("At least 2 snapshots are required for differential analysis.")
    if len(snapshots) != len(packet_counts):
        raise ValueError("snapshots and packet_counts must have identical length.")

    snap_len = len(snapshots[0])
    for snap in snapshots:
        validate_four_byte_alignment(base_address, snap)
        if len(snap) != snap_len:
            raise ValueError("All snapshots must have identical byte length.")

    word_matrices = [unpack_le_words(s) for s in snapshots]
    num_words = len(word_matrices[0])
    num_snaps = len(snapshots)
    pkt_deltas = [
        float(packet_counts[k] - packet_counts[k - 1]) for k in range(1, num_snaps)
    ]

    changed_indices: List[int] = []
    word_transitions: Dict[int, int] = {}
    word_is_monotonic: Dict[int, bool] = {}
    word_corr: Dict[int, float] = {}

    for w_idx in range(num_words):
        series = [word_matrices[s][w_idx] for s in range(num_snaps)]
        diffs = [series[k] - series[k - 1] for k in range(1, num_snaps)]
        transitions = sum(1 for d in diffs if d != 0)
        if transitions > 0:
            changed_indices.append(w_idx)
            word_transitions[w_idx] = transitions
            is_mono = all(d >= 0 for d in diffs) and any(d > 0 for d in diffs)
            word_is_monotonic[w_idx] = is_mono
            if is_mono:
                word_corr[w_idx] = _pearson_corr(
                    [float(d) for d in diffs], pkt_deltas
                )
            else:
                activity = [1.0 if d != 0 else 0.0 for d in diffs]
                pkt_active = [1.0 if p > 0 else 0.0 for p in pkt_deltas]
                if activity == pkt_active and any(p > 0 for p in pkt_deltas):
                    word_corr[w_idx] = 1.0
                else:
                    word_corr[w_idx] = _pearson_corr(activity, pkt_active)

    # Cluster changed word indices separated by at most max_gap_words
    clusters: List[Tuple[int, int]] = []
    if changed_indices:
        cur_start = changed_indices[0]
        cur_end = changed_indices[0]
        for idx in changed_indices[1:]:
            if idx - cur_end <= max_gap_words:
                cur_end = idx
            else:
                clusters.append((cur_start, cur_end))
                cur_start = idx
                cur_end = idx
        clusters.append((cur_start, cur_end))

    regions: List[MemoryDiffRegion] = []
    for r_num, (w_start, w_end) in enumerate(clusters, start=1):
        start_off = w_start * 4
        end_off = (w_end + 1) * 4
        start_addr = base_address + start_off
        end_addr = base_address + end_off
        word_span = w_end - w_start + 1

        c_words = [w for w in range(w_start, w_end + 1) if w in word_transitions]
        tot_trans = sum(word_transitions[w] for w in c_words)
        mono_cnt = sum(1 for w in c_words if word_is_monotonic.get(w, False))
        dram_ptr_cnt = sum(
            1
            for w in range(w_start, w_end + 1)
            if is_target_dram_pointer(word_matrices[-1][w])
        )
        rom_ptr_cnt = sum(
            1
            for w in range(w_start, w_end + 1)
            if is_target_rom_pointer(word_matrices[-1][w])
        )
        mean_corr = (
            sum(word_corr.get(w, 0.0) for w in c_words) / len(c_words)
            if c_words
            else 0.0
        )

        overlaps_hi = not (
            end_addr <= QCA988X_HOST_INTEREST_ADDR
            or start_addr >= QCA988X_HOST_INTEREST_ADDR + QCA988X_HOST_INTEREST_LEN
        )
        if overlaps_hi:
            classification = "HOST_INTEREST_TABLE"
            notes = "Overlaps QCA988X_HOST_INTEREST_ADDRESS (0x00400800)."
        elif mono_cnt >= max(1, len(c_words) // 2) and mean_corr >= 0.75:
            classification = "MONOTONIC_COUNTER_BLOCK"
            notes = "Monotonically increasing target counters strongly correlated with packet/sounding arrivals."
        elif dram_ptr_cnt >= 2:
            classification = "TARGET_DRAM_POINTER_RING"
            notes = "Contains valid 4-byte aligned target DRAM pointers (0x00400000..0x0044ffff) indicative of a DMA/HTT ring."
        elif len(c_words) >= 16 and mean_corr >= 0.5:
            classification = "PACKET_CORRELATED_DESCRIPTOR_OR_CSI_BUFFER"
            notes = "Multi-dword payload/descriptor/channel-dump region updating on packet bursts."
        else:
            classification = "DYNAMIC_SCRATCH_REGION"
            notes = "Dynamic target state region."

        regions.append(
            MemoryDiffRegion(
                region_id=f"REG-{r_num:02d}",
                start_address_hex=f"0x{start_addr:08x}",
                end_address_hex=f"0x{end_addr:08x}",
                start_offset=start_off,
                byte_length=end_off - start_off,
                word_count=word_span,
                changed_word_count=len(c_words),
                total_word_transitions=tot_trans,
                monotonic_word_count=mono_cnt,
                dram_pointer_word_count=dram_ptr_cnt,
                rom_pointer_word_count=rom_ptr_cnt,
                packet_count_correlation=round(mean_corr, 4),
                classification=classification,
                notes=notes,
            )
        )

    hi_decoded = decode_host_interest_table(snapshots[-1], base_address=base_address)

    return {
        "base_address_hex": f"0x{base_address:08x}",
        "snapshot_count": num_snaps,
        "snapshot_size_bytes": snap_len,
        "total_words": num_words,
        "total_changed_words": len(changed_indices),
        "packet_counts": list(packet_counts),
        "host_interest_summary": hi_decoded,
        "regions": [r.to_dict() for r in regions],
    }


def _sign_extend(val: int, bits: int) -> int:
    sign_bit = 1 << (bits - 1)
    return (val & (sign_bit - 1)) - (val & sign_bit)


def _wrap_phase(rad: float) -> float:
    while rad > math.pi:
        rad -= 2.0 * math.pi
    while rad < -math.pi:
        rad += 2.0 * math.pi
    return rad


def _match_ofdm_tone_mode(tone_count: int) -> str:
    for mode_name, expected in OFDM_TONE_COUNTS.items():
        if tone_count == expected:
            return mode_name
    return f"NON_STANDARD_{tone_count}_TONES"


def _score_iq_sequence(
    hypothesis_id: str,
    description: str,
    family_applicability: str,
    iq_pairs: Sequence[Tuple[int, int]],
    reserved_zero_ratio: float,
) -> TonePackingHypothesisScore:
    n = len(iq_pairs)
    if n < 4:
        return TonePackingHypothesisScore(
            hypothesis_id=hypothesis_id,
            description=description,
            family_applicability=family_applicability,
            decoded_tone_count=n,
            matched_ofdm_bandwidth_mode="INSUFFICIENT_TONES",
            mean_magnitude=0.0,
            magnitude_smoothness_cv=99.0,
            adjacent_phase_step_std_rad=math.pi,
            linear_phase_coherence=0.0,
            reserved_bits_zero_ratio=round(reserved_zero_ratio, 4),
            composite_confidence_score=0.0,
            sample_preview_iq=list(iq_pairs[:4]),
        )

    mags = [math.hypot(float(i), float(q)) for i, q in iq_pairs]
    mean_mag = sum(mags) / n
    if mean_mag <= 1e-9:
        mag_cv = 99.0
    else:
        adj_mag_diffs = [abs(mags[k + 1] - mags[k]) for k in range(n - 1)]
        mag_cv = (sum(adj_mag_diffs) / len(adj_mag_diffs)) / mean_mag

    phases = [math.atan2(float(q), float(i)) for i, q in iq_pairs]
    phase_steps = [_wrap_phase(phases[k + 1] - phases[k]) for k in range(n - 1)]

    # Vector strength (circular coherence) of adjacent phase steps:
    # A physical OFDM channel H(f_k) = A_k * exp(j*(phi_0 + k*delta_phi)) has
    # nearly constant phase step delta_phi across adjacent subcarriers, so
    # |mean(exp(j * step_k))| is close to 1.0. Wrong bit-packing scrambles phase_steps.
    mean_cos = sum(math.cos(s) for s in phase_steps) / len(phase_steps)
    mean_sin = sum(math.sin(s) for s in phase_steps) / len(phase_steps)
    coherence = math.hypot(mean_cos, mean_sin)

    mean_step = math.atan2(mean_sin, mean_cos)
    step_var = sum((_wrap_phase(s - mean_step)) ** 2 for s in phase_steps) / len(
        phase_steps
    )
    step_std = math.sqrt(step_var)

    mode_str = _match_ofdm_tone_mode(n)
    mode_bonus = 1.0 if not mode_str.startswith("NON_STANDARD") else 0.5
    mag_score = max(0.0, 1.0 - min(1.0, mag_cv))
    score = (
        0.45 * coherence
        + 0.25 * mag_score
        + 0.20 * reserved_zero_ratio
        + 0.10 * mode_bonus
    )

    return TonePackingHypothesisScore(
        hypothesis_id=hypothesis_id,
        description=description,
        family_applicability=family_applicability,
        decoded_tone_count=n,
        matched_ofdm_bandwidth_mode=mode_str,
        mean_magnitude=round(mean_mag, 3),
        magnitude_smoothness_cv=round(mag_cv, 4),
        adjacent_phase_step_std_rad=round(step_std, 4),
        linear_phase_coherence=round(coherence, 4),
        reserved_bits_zero_ratio=round(reserved_zero_ratio, 4),
        composite_confidence_score=round(score, 4),
        sample_preview_iq=list(iq_pairs[:6]),
    )


def evaluate_channel_dump_packing_hypotheses(blob: bytes) -> Dict[str, Any]:
    """Evaluate complex tone-packing hypotheses on a raw `CHAN_TAB_B0/B1` or `bb_length` blob."""
    validate_four_byte_alignment(0, blob)
    words = unpack_le_words(blob)

    # 1. H_10BIT_IQ: 32-bit CHANINFO_WORD with I = bits[9:0] (signed 10-bit),
    #    Q = bits[19:10] (signed 10-bit), bits[31:20] = 0
    iq_10bit: List[Tuple[int, int]] = []
    res_10_zero = 0
    for w in words:
        i_val = _sign_extend(w & 0x3FF, 10)
        q_val = _sign_extend((w >> 10) & 0x3FF, 10)
        if (w >> 20) == 0:
            res_10_zero += 1
        iq_10bit.append((i_val, q_val))
    score_10bit = _score_iq_sequence(
        hypothesis_id="H_10BIT_IQ_WORD32",
        description="10-bit signed I [9:0] + 10-bit signed Q [19:10] per 32-bit CHANINFO_WORD (reserved [31:20]=0)",
        family_applicability="EXACT_AR9888_PEREGRINE_CANDIDATE",
        iq_pairs=iq_10bit,
        reserved_zero_ratio=res_10_zero / len(words),
    )

    # 2. H_12BIT_IQ: 32-bit CHANINFO_WORD with I = bits[11:0] (signed 12-bit),
    #    Q = bits[23:12] (signed 12-bit), bits[31:24] = 0
    iq_12bit: List[Tuple[int, int]] = []
    res_12_zero = 0
    for w in words:
        i_val = _sign_extend(w & 0xFFF, 12)
        q_val = _sign_extend((w >> 12) & 0xFFF, 12)
        if (w >> 24) == 0:
            res_12_zero += 1
        iq_12bit.append((i_val, q_val))
    score_12bit = _score_iq_sequence(
        hypothesis_id="H_12BIT_IQ_WORD32",
        description="12-bit signed I [11:0] + 12-bit signed Q [23:12] per 32-bit CHANINFO_WORD (reserved [31:24]=0)",
        family_applicability="EXACT_AR9888_PEREGRINE_CANDIDATE",
        iq_pairs=iq_12bit,
        reserved_zero_ratio=res_12_zero / len(words),
    )

    # 3. H_8BIT_IQ: Two tones per 32-bit word (int8 I0, int8 Q0, int8 I1, int8 Q1)
    iq_8bit: List[Tuple[int, int]] = []
    for w in words:
        i0 = _sign_extend(w & 0xFF, 8)
        q0 = _sign_extend((w >> 8) & 0xFF, 8)
        i1 = _sign_extend((w >> 16) & 0xFF, 8)
        q1 = _sign_extend((w >> 24) & 0xFF, 8)
        iq_8bit.append((i0, q0))
        iq_8bit.append((i1, q1))
    score_8bit = _score_iq_sequence(
        hypothesis_id="H_8BIT_DUAL_TONE_WORD32",
        description="Dual 8-bit signed I/Q pairs (2 tones per 32-bit word)",
        family_applicability="LEGACY_COMPACT_CANDIDATE",
        iq_pairs=iq_8bit,
        reserved_zero_ratio=0.5,
    )

    # 4. H_EXP_MANTISSA_CFR: Later-QCA (IPQ8074/QCA9984) 14-bit mantissa + 4-bit exponent
    iq_cfr: List[Tuple[int, int]] = []
    for w in words:
        mant_i = _sign_extend(w & 0x1FFF, 13)
        mant_q = _sign_extend((w >> 13) & 0x1FFF, 13)
        exp = (w >> 26) & 0x0F
        scale = 1 << min(exp, 6)
        iq_cfr.append((mant_i * scale, mant_q * scale))
    score_cfr = _score_iq_sequence(
        hypothesis_id="H_EXP_MANTISSA_LATER_CFR",
        description="Later-QCA CFR (13-bit I, 13-bit Q, 4-bit exponent in [29:26])",
        family_applicability="CROSS_CHIP_LATER_QCA",
        iq_pairs=iq_cfr,
        reserved_zero_ratio=0.25,
    )

    all_scores = sorted(
        [score_10bit, score_12bit, score_8bit, score_cfr],
        key=lambda s: s.composite_confidence_score,
        reverse=True,
    )
    winner = all_scores[0]
    return {
        "blob_byte_length": len(blob),
        "blob_word_count": len(words),
        "winning_hypothesis_id": winner.hypothesis_id,
        "winning_confidence_score": winner.composite_confidence_score,
        "matched_ofdm_bandwidth_mode": winner.matched_ofdm_bandwidth_mode,
        "hypotheses": [s.to_dict() for s in all_scores],
    }


def synthesize_10bit_channel_dump_blob(
    num_tones: int = 56,
    base_amplitude: float = 320.0,
    phase_slope_rad_per_tone: float = 0.18,
    initial_phase_rad: float = 0.35,
) -> bytes:
    """Synthesize a physically realistic 56-tone VHT20 `CHAN_TAB_B0` 10-bit signed I/Q dump."""
    words: List[int] = []
    for k in range(num_tones):
        # Smooth multipath envelope modulation across subcarriers
        amp = base_amplitude * (1.0 + 0.12 * math.cos(2.0 * math.pi * k / num_tones))
        phi = initial_phase_rad + k * phase_slope_rad_per_tone
        i_int = max(-511, min(511, int(round(amp * math.cos(phi)))))
        q_int = max(-511, min(511, int(round(amp * math.sin(phi)))))
        w = (i_int & 0x3FF) | ((q_int & 0x3FF) << 10)
        words.append(w)
    return struct.pack(f"<{len(words)}I", *words)


def build_synthetic_dram_and_channel_dump_fixture_report() -> Dict[str, Any]:
    """Generate the deterministic synthetic validation report for `artifacts/qca988x/memory_diff_fixture_report.json`."""
    window_size = 0x2000  # 8192 bytes covering 0x00400000..0x00401fff
    packet_counts = [0, 0, 15, 45, 90]
    snapshots: List[bytes] = []

    chan_dump_56 = synthesize_10bit_channel_dump_blob(num_tones=56)

    for snap_idx, pkt_cnt in enumerate(packet_counts):
        buf = bytearray(window_size)
        burst_idx = 0 if pkt_cnt == 0 else snap_idx

        # 1. Populate Host Interest Table at offset 0x0800 (0x00400800)
        hi_off = 0x0800
        struct.pack_into("<I", buf, hi_off + 0x00, 0x00401200)  # hi_app_host_interest
        struct.pack_into("<I", buf, hi_off + 0x04, 0x00000000)  # hi_failure_state
        struct.pack_into("<I", buf, hi_off + 0x1C, 0x00404000)  # hi_board_data
        struct.pack_into("<I", buf, hi_off + 0x20, 0x00000001)  # hi_board_data_initialized
        struct.pack_into("<I", buf, hi_off + 0x4C, 0x00418000)  # hi_dbglog_config
        struct.pack_into("<I", buf, hi_off + 0x70, 0x0000000A)  # hi_option_flag
        struct.pack_into("<I", buf, hi_off + 0xC4, burst_idx)   # hi_ACS_flags counter

        # 2. Populate Monotonic Packet / Sounding Counters at offset 0x1000 (0x00401000)
        cnt_off = 0x1000
        struct.pack_into("<I", buf, cnt_off + 0x00, pkt_cnt)          # rx_ppdu_total
        struct.pack_into("<I", buf, cnt_off + 0x04, pkt_cnt * 2)      # rx_mpdu_total
        struct.pack_into("<I", buf, cnt_off + 0x08, pkt_cnt)          # bb_captured_channel_cnt
        struct.pack_into("<I", buf, cnt_off + 0x0C, pkt_cnt * 224)    # csi_bytes_transferred

        # 3. Populate Target DRAM Pointer Ring at offset 0x1200 (0x00401200)
        ring_off = 0x1200
        for r_i in range(4):
            ptr = 0x00420000 + ((r_i + burst_idx) % 8) * 0x100
            struct.pack_into("<I", buf, ring_off + r_i * 4, ptr)

        # 4. Populate Packet-Correlated 56-tone Channel Dump Buffer at offset 0x1400 (0x00401400)
        csi_off = 0x1400
        active_dump = synthesize_10bit_channel_dump_blob(
            num_tones=56,
            base_amplitude=300.0 + burst_idx * 5.0,
            phase_slope_rad_per_tone=0.18,
            initial_phase_rad=0.25 + burst_idx * 0.08,
        )
        buf[csi_off : csi_off + len(active_dump)] = active_dump

        snapshots.append(bytes(buf))

    diff_report = analyze_memory_snapshots(
        snapshots=snapshots,
        packet_counts=packet_counts,
        base_address=QCA988X_DRAM_ADDR,
    )
    packing_report = evaluate_channel_dump_packing_hypotheses(chan_dump_56)

    return {
        "schema_version": "1.0",
        "task_id": "T-PB-GEM2-03",
        "workstream": "Physical-Boundary Phase 0 Workstream E5",
        "target_architecture": "QCA988x / AR9888 v2 (Peregrine)",
        "live_devices_touched": False,
        "dram_constants": {
            "QCA988X_DRAM_ADDR_HEX": f"0x{QCA988X_DRAM_ADDR:08x}",
            "QCA988X_DRAM_LEN_HEX": f"0x{QCA988X_DRAM_LEN:08x}",
            "QCA988X_HOST_INTEREST_ADDR_HEX": f"0x{QCA988X_HOST_INTEREST_ADDR:08x}",
            "PHY_BB_CHAN_TAB_B0_ADDR_HEX": f"0x{PHY_BB_CHAN_TAB_B0_ADDR:08x}",
            "PHY_BB_CHAN_TAB_B1_ADDR_HEX": f"0x{PHY_BB_CHAN_TAB_B1_ADDR:08x}",
        },
        "memory_diff_analysis": diff_report,
        "channel_dump_packing_analysis": packing_report,
    }


def write_memory_diff_fixture_report_json(
    output_path: Path = Path("artifacts/qca988x/memory_diff_fixture_report.json"),
) -> Dict[str, Any]:
    """Generate and write `artifacts/qca988x/memory_diff_fixture_report.json`."""
    report = build_synthetic_dram_and_channel_dump_fixture_report()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    out = Path("artifacts/qca988x/memory_diff_fixture_report.json")
    rep = write_memory_diff_fixture_report_json(out)
    print(
        json.dumps(
            {
                "artifact": str(out),
                "regions_detected": len(rep["memory_diff_analysis"]["regions"]),
                "region_classifications": [
                    r["classification"] for r in rep["memory_diff_analysis"]["regions"]
                ],
                "winning_packing_hypothesis": rep["channel_dump_packing_analysis"][
                    "winning_hypothesis_id"
                ],
                "winning_confidence_score": rep["channel_dump_packing_analysis"][
                    "winning_confidence_score"
                ],
            },
            indent=2,
        )
    )
