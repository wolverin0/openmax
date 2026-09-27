"""
ath10k Baseband Spectral FFT Parser and Lightweight Interference Classifier.
Parses raw binary RelayFS streams emitted by ath10k / ath10k-ct via
/sys/kernel/debug/ieee80211/phyX/ath10k/spectral_scan_ctl.

Memory Footprint: < 500 KB RAM (designed for embedded MIPS 74Kc @ 533 MHz).
Dependencies: Pure Python standard library (struct, math, dataclasses). No CUDA, no heavy ML.
"""

import struct
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Generator
import math

# TLV Types from Linux spectral_common.h
ATH_FFT_SAMPLE_HT20 = 1
ATH_FFT_SAMPLE_ATH10K = 2

# Struct format string for fft_sample_ath10k header:
# tlv.type: B (1 byte)
# tlv.length: >H (2 bytes, big-endian)
# chan_width_mhz: B (1 byte)
# relpwr_db: B (1 byte)
# avgpwr_db: B (1 byte)
# max_magnitude: >H (2 bytes)
# max_index: b (1 byte, signed)
# rssi: b (1 byte, signed)
# total_gain_db: >H (2 bytes)
# base_pwr_db: >H (2 bytes)
# freq1: >H (2 bytes)
# freq2: >H (2 bytes)
# max_exp: B (1 byte)
# noise: >h (2 bytes, signed)
# tsf: >Q (8 bytes, uint64)
# Total size: 1 + 2 + 1 + 1 + 1 + 2 + 1 + 1 + 2 + 2 + 2 + 2 + 1 + 2 + 8 = 29 bytes
HEADER_FORMAT = ">BHBBBHbbHHHHBhQ"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


@dataclass
class SpectralSample:
    """Parsed single FFT report from ath10k baseband DSP."""
    tlv_type: int
    length: int
    chan_width_mhz: int
    relpwr_db: int
    avgpwr_db: int
    max_magnitude: int
    max_index: int
    rssi: int
    total_gain_db: int
    base_pwr_db: int
    freq1_mhz: int
    freq2_mhz: int
    max_exp: int
    noise_dbm: int
    tsf_us: int
    bins: List[int]  # Raw 8-bit bin values
    bin_dbm: List[float]  # Calibrated power in dBm per subcarrier bin


class InterferenceClass:
    CLEAN = "CLEAN_CHANNEL"
    RADAR_DFS = "DFS_WEATHER_RADAR"
    NARROWBAND_CW = "NARROWBAND_CW_JAMMER"
    ADJACENT_CHANNEL = "ADJACENT_CHANNEL_SPILL"
    BROADBAND_NOISE = "ELEVATED_NOISE_FLOOR"


class SpectralParser:
    """Stream parser for ath10k RelayFS spectral data."""

    def __init__(self):
        self.buffer = bytearray()

    def feed(self, data: bytes) -> Generator[SpectralSample, None, None]:
        """Feed raw bytes from RelayFS file descriptor and yield parsed samples."""
        self.buffer.extend(data)
        
        while len(self.buffer) >= HEADER_SIZE:
            # Inspect TLV length
            tlv_type = self.buffer[0]
            if tlv_type != ATH_FFT_SAMPLE_ATH10K:
                # Seek to next potential valid TLV
                del self.buffer[0]
                continue
                
            payload_len = struct.unpack_from(">H", self.buffer, 1)[0]
            total_sample_len = 3 + payload_len  # 1 (type) + 2 (len) + payload
            
            if len(self.buffer) < total_sample_len:
                # Need more bytes
                break
                
            sample_bytes = self.buffer[:total_sample_len]
            del self.buffer[:total_sample_len]
            
            sample = self.parse_single_sample(sample_bytes)
            if sample:
                yield sample

    @staticmethod
    def parse_single_sample(data: bytes) -> Optional[SpectralSample]:
        """Parse a complete binary packet into a SpectralSample object."""
        if len(data) < HEADER_SIZE:
            return None
            
        unpacked = struct.unpack_from(HEADER_FORMAT, data, 0)
        (
            tlv_type, length, chan_width_mhz, relpwr_db, avgpwr_db,
            max_magnitude, max_index, rssi, total_gain_db, base_pwr_db,
            freq1, freq2, max_exp, noise, tsf
        ) = unpacked
        
        # Remaining bytes are raw FFT bins
        bin_bytes = data[HEADER_SIZE:]
        bins = list(bin_bytes)
        bin_count = len(bins)
        
        if bin_count == 0:
            return None
            
        # Calibrate subcarrier power to dBm
        # P_bin(i) = noise_dbm + (bins[i] - 128) * scale + relpwr
        bin_dbm = []
        for b in bins:
            # On QCA9880, bin value is proportional to power
            # Calibrated relative to measured noise floor
            val_db = (b * 0.5) + noise
            bin_dbm.append(round(val_db, 2))
            
        return SpectralSample(
            tlv_type=tlv_type,
            length=length,
            chan_width_mhz=chan_width_mhz,
            relpwr_db=relpwr_db,
            avgpwr_db=avgpwr_db,
            max_magnitude=max_magnitude,
            max_index=max_index,
            rssi=rssi,
            total_gain_db=total_gain_db,
            base_pwr_db=base_pwr_db,
            freq1_mhz=freq1,
            freq2_mhz=freq2,
            max_exp=max_exp,
            noise_dbm=noise,
            tsf_us=tsf,
            bins=bins,
            bin_dbm=bin_dbm
        )


class LightweightInterferenceClassifier:
    """
    Sub-millisecond RF anomaly classifier executing on MIPS 74Kc.
    Extracts 4 summary statistics:
    1. Peak-to-Average Power Ratio (PAPR)
    2. Spectral Flatness Measure (SFM)
    3. Spectral Asymmetry (Left vs Right half energy)
    4. Max-to-Median Delta
    """

    @staticmethod
    def classify(sample: SpectralSample) -> Tuple[str, float, Dict[str, float]]:
        """
        Classifies interference type.
        Returns: (classification_label, confidence, metrics_dict)
        """
        powers = sample.bin_dbm
        N = len(powers)
        if N < 16:
            return (InterferenceClass.CLEAN, 0.5, {})

        # Convert dBm to linear scale for spectral moments
        linear_pwr = [10.0 ** (p / 10.0) for p in powers]
        p_mean = sum(linear_pwr) / N
        p_max = max(linear_pwr)
        p_median = sorted(linear_pwr)[N // 2]

        # 1. Peak-to-Average Power Ratio (in dB)
        papr_db = 10.0 * math.log10(p_max / max(p_mean, 1e-12))

        # 2. Max-to-Median Delta (in dB)
        max_med_db = 10.0 * math.log10(p_max / max(p_median, 1e-12))

        # 3. Spectral Asymmetry: Energy in lower half vs upper half
        mid = N // 2
        p_left = sum(linear_pwr[:mid])
        p_right = sum(linear_pwr[mid:])
        asym_ratio = (p_left - p_right) / max(p_left + p_right, 1e-12)

        # 4. Spectral Flatness: Geometric Mean / Arithmetic Mean
        # High for noise/flat OFDM, low for narrow tonal spikes
        log_sum = sum(math.log(max(p, 1e-12)) for p in linear_pwr) / N
        geom_mean = math.exp(log_sum)
        sfm = geom_mean / max(p_mean, 1e-12)

        metrics = {
            "papr_db": round(papr_db, 2),
            "max_med_db": round(max_med_db, 2),
            "asym_ratio": round(asym_ratio, 3),
            "sfm": round(sfm, 4),
            "noise_floor_dbm": sample.noise_dbm
        }

        # Decision Tree for Embedded Evaluation:
        # Rule 1: Narrowband DFS Radar or Continuous Wave (CW) Spike
        if max_med_db > 18.0 and sfm < 0.15:
            # Check pulse/burst vs persistent
            if papr_db > 22.0:
                return (InterferenceClass.RADAR_DFS, 0.95, metrics)
            else:
                return (InterferenceClass.NARROWBAND_CW, 0.90, metrics)

        # Rule 2: Adjacent Channel Interference (heavy energy tilt across center frequency)
        if abs(asym_ratio) > 0.50:
            return (InterferenceClass.ADJACENT_CHANNEL, 0.88, metrics)

        # Rule 3: High Noise Floor / Jamming
        if sample.noise_dbm > -82.0:
            return (InterferenceClass.BROADBAND_NOISE, 0.82, metrics)

        # Default: Channel is clean / normal OFDM traffic
        return (InterferenceClass.CLEAN, 0.90, metrics)
