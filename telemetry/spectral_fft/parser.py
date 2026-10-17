"""ath10k Baseband Spectral FFT and airOS Spectral Parser & RF Analyzer.

Parses raw binary RelayFS streams emitted by ath10k / ath10k-ct via
/sys/kernel/debug/ieee80211/phyX/ath10k/spectral_scan_ctl (both TLV Type 2 and Type 3),
as well as Ubiquiti airOS / airView spectral FFT JSON feeds.

Calculates:
- Per-bin calibrated power (dBm)
- Estimated / measured noise floor (dBm)
- Peak interference frequency (MHz)
- Channel occupancy percentage (%)
- Embedded sub-millisecond RF anomaly classification (DFS radar, CW jammer, adjacent spill, noise)

Memory Footprint: < 500 KB RAM (designed for embedded MIPS 74Kc @ 533 MHz).
Dependencies: Pure Python standard library (struct, math, json, dataclasses). No CUDA, no heavy ML.
"""

from __future__ import annotations

import json
import math
import struct
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

# TLV Types from Linux spectral_common.h
ATH_FFT_SAMPLE_HT20 = 1
ATH_FFT_SAMPLE_ATH10K = 2       # 29-byte struct fft_sample_ath10k
ATH_FFT_SAMPLE_ATH10K_TYPE3 = 3 # 24-byte struct fft_sample_ath10k (OpenWrt/ath10k-ct relay dump)

# Format for ATH_FFT_SAMPLE_ATH10K (Type 2, 29 bytes):
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

# Format for ATH_FFT_SAMPLE_ATH10K_TYPE3 (Type 3, 24-byte payload following 3-byte TLV header):
# chan_width_mhz: B (1 byte)
# freq1: >H (2 bytes)
# freq2: >H (2 bytes)
# noise: >h (2 bytes, signed)
# max_magnitude: >H (2 bytes)
# total_gain_db: >H (2 bytes)
# base_pwr_db: >H (2 bytes)
# tsf: >q (8 bytes, int64)
# max_index: b (1 byte, signed)
# rssi: b (1 byte, signed)
# relpwr_db: B (1 byte)
# avgpwr_db: B (1 byte)
# max_exp: B (1 byte)
# Total payload: 1+2+2+2+2+2+2+8+1+1+1+1+1 = 24 bytes
HEADER_TYPE3_PAYLOAD_FORMAT = ">BHHhHHHqbBBBB"
HEADER_TYPE3_PAYLOAD_SIZE = struct.calcsize(HEADER_TYPE3_PAYLOAD_FORMAT)


@dataclass
class SpectralSample:
    """Parsed single FFT report from ath10k baseband DSP or airOS airView."""
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
    bins: List[int]       # Raw 8-bit bin values
    bin_dbm: List[float]  # Calibrated power in dBm per subcarrier bin


@dataclass
class SpectralAnalysisReport:
    """Consolidated RF spectral analysis report."""
    center_freq_mhz: float
    chan_width_mhz: float
    noise_floor_dbm: float
    per_bin_power_dbm: List[float]
    peak_power_dbm: float
    peak_interference_freq_mhz: float
    channel_occupancy_pct: float
    interference_class: str
    confidence: float
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "center_freq_mhz": self.center_freq_mhz,
            "chan_width_mhz": self.chan_width_mhz,
            "noise_floor_dbm": self.noise_floor_dbm,
            "per_bin_power_dbm": self.per_bin_power_dbm,
            "peak_power_dbm": self.peak_power_dbm,
            "peak_interference_freq_mhz": self.peak_interference_freq_mhz,
            "channel_occupancy_pct": self.channel_occupancy_pct,
            "interference_class": self.interference_class,
            "confidence": self.confidence,
            "metrics": self.metrics,
        }


class InterferenceClass:
    CLEAN = "CLEAN_CHANNEL"
    RADAR_DFS = "DFS_WEATHER_RADAR"
    NARROWBAND_CW = "NARROWBAND_CW_JAMMER"
    ADJACENT_CHANNEL = "ADJACENT_CHANNEL_SPILL"
    BROADBAND_NOISE = "ELEVATED_NOISE_FLOOR"


def calculate_peak_interference_frequency(
    bin_dbm: List[float],
    center_freq_mhz: float,
    chan_width_mhz: float,
) -> float:
    """Calculates RF frequency (MHz) of the peak power subcarrier bin."""
    if not bin_dbm:
        return center_freq_mhz

    nbins = len(bin_dbm)
    max_idx = max(range(nbins), key=lambda idx: bin_dbm[idx])

    # Subcarriers are spaced evenly across chan_width centered at center_freq_mhz
    # Bin 0 corresponds to center_freq - chan_width/2 + bin_width/2
    # Bin nbins - 1 corresponds to center_freq + chan_width/2 - bin_width/2
    bin_step = chan_width_mhz / nbins
    freq = (center_freq_mhz - (chan_width_mhz / 2.0)) + ((max_idx + 0.5) * bin_step)
    return round(freq, 3)


def calculate_channel_occupancy(
    bin_dbm: List[float],
    noise_floor_dbm: float,
    threshold_delta_db: float = 10.0,
    absolute_threshold_dbm: Optional[float] = None,
) -> float:
    """Calculates channel occupancy percentage based on bins exceeding noise threshold."""
    if not bin_dbm:
        return 0.0

    threshold = (
        absolute_threshold_dbm
        if absolute_threshold_dbm is not None
        else (noise_floor_dbm + threshold_delta_db)
    )

    occupied_count = sum(1 for pwr in bin_dbm if pwr >= threshold)
    occupancy_pct = (occupied_count / len(bin_dbm)) * 100.0
    return round(occupancy_pct, 2)


class SpectralParser:
    """Stream parser for ath10k RelayFS and debugfs spectral binary dumps."""

    def __init__(self):
        self.buffer = bytearray()

    def feed(self, data: bytes) -> Generator[SpectralSample, None, None]:
        """Feed raw bytes from RelayFS file descriptor and yield parsed samples."""
        self.buffer.extend(data)

        while len(self.buffer) >= 3:
            tlv_type = self.buffer[0]
            payload_len = struct.unpack_from(">H", self.buffer, 1)[0]
            total_sample_len = 3 + payload_len

            if tlv_type == ATH_FFT_SAMPLE_ATH10K:
                # Type 2 format
                if len(self.buffer) < HEADER_SIZE:
                    break
                if len(self.buffer) < total_sample_len:
                    break
                sample_bytes = self.buffer[:total_sample_len]
                del self.buffer[:total_sample_len]

                sample = self.parse_single_sample(sample_bytes)
                if sample:
                    yield sample

            elif tlv_type == ATH_FFT_SAMPLE_ATH10K_TYPE3:
                # Type 3 format (OpenWrt/ath10k-ct debugfs dump)
                if len(self.buffer) < 3 + HEADER_TYPE3_PAYLOAD_SIZE:
                    break
                if len(self.buffer) < total_sample_len:
                    break
                sample_bytes = self.buffer[:total_sample_len]
                del self.buffer[:total_sample_len]

                sample = self._parse_type3_sample(sample_bytes)
                if sample:
                    yield sample

            else:
                # Seek to next potential valid TLV
                del self.buffer[0]

    @staticmethod
    def parse_single_sample(data: bytes) -> Optional[SpectralSample]:
        """Parse a complete Type 2 binary packet into a SpectralSample object."""
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
        # On QCA9880, bin value is proportional to power, calibrated relative to measured noise floor
        bin_dbm = []
        for b in bins:
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
            bin_dbm=bin_dbm,
        )

    @staticmethod
    def _parse_type3_sample(data: bytes) -> Optional[SpectralSample]:
        """Parse an ath10k Type 3 binary packet (relayfs debugfs dump)."""
        if len(data) < 3 + HEADER_TYPE3_PAYLOAD_SIZE:
            return None

        tlv_type, payload_len = struct.unpack_from(">BH", data, 0)
        body = data[3:]
        (
            width, f1, f2, noise, maxmag, gain, basepwr, tsf, maxidx, rssi, relpwr, avgpwr, maxexp
        ) = struct.unpack_from(HEADER_TYPE3_PAYLOAD_FORMAT, body, 0)

        bins = list(body[HEADER_TYPE3_PAYLOAD_SIZE:])
        if not bins:
            return None

        # Userspace convention for ath10k type 3 magnitude -> dBm calibration:
        mags = [(b << maxexp) for b in bins]
        sq = sum(m * m for m in mags) or 1
        bin_dbm = []
        for m in mags:
            if m > 0:
                val = 10.0 * math.log10((m * m) / sq) + noise + rssi
                bin_dbm.append(round(val, 2))
            else:
                bin_dbm.append(float(noise))

        return SpectralSample(
            tlv_type=tlv_type,
            length=payload_len,
            chan_width_mhz=width,
            relpwr_db=relpwr,
            avgpwr_db=avgpwr,
            max_magnitude=maxmag,
            max_index=maxidx,
            rssi=rssi,
            total_gain_db=gain,
            base_pwr_db=basepwr,
            freq1_mhz=f1,
            freq2_mhz=f2,
            max_exp=maxexp,
            noise_dbm=noise,
            tsf_us=tsf,
            bins=bins,
            bin_dbm=bin_dbm,
        )


class AirOSSpectralParser:
    """Parser for Ubiquiti airOS / airView spectral FFT telemetry feeds."""

    @staticmethod
    def parse_json(payload: Union[str, dict, list]) -> List[SpectralSample]:
        """Parses airOS airView or ubntspecd JSON payloads into SpectralSample objects."""
        if isinstance(payload, str):
            data = json.loads(payload)
        else:
            data = payload

        if isinstance(data, dict):
            # Might be {"spectral": [...]} or a single record
            records = data.get("spectral", data.get("samples", [data]))
        elif isinstance(data, list):
            records = data
        else:
            return []

        samples: List[SpectralSample] = []
        for rec in records:
            if not isinstance(rec, dict):
                continue

            center_freq = int(rec.get("center_freq", rec.get("frequency", rec.get("freq1", 5200))))
            chan_width = int(rec.get("chan_width", rec.get("width", rec.get("bandwidth", 20))))
            noise = int(rec.get("noise_floor", rec.get("noise", -95)))
            tsf = int(rec.get("tsf", rec.get("timestamp", 0) * 1_000_000))
            rssi = int(rec.get("rssi", -65))

            # Bins can be raw ints or already in dBm
            raw_bins = rec.get("bins", rec.get("sweep", []))
            if not raw_bins:
                continue

            if isinstance(raw_bins[0], float) or (isinstance(raw_bins[0], int) and raw_bins[0] < 0):
                # Already in dBm
                bin_dbm = [round(float(b), 2) for b in raw_bins]
                bins = [max(0, min(255, int((b - noise) * 2))) for b in bin_dbm]
            else:
                # Raw integer magnitude
                bins = [int(b) for b in raw_bins]
                bin_dbm = [round((b * 0.5) + noise, 2) for b in bins]

            sample = SpectralSample(
                tlv_type=ATH_FFT_SAMPLE_ATH10K,
                length=len(bins) + HEADER_SIZE - 3,
                chan_width_mhz=chan_width,
                relpwr_db=int(rec.get("relpwr_db", 0)),
                avgpwr_db=int(rec.get("avgpwr_db", 0)),
                max_magnitude=int(rec.get("max_magnitude", max(bins) if bins else 0)),
                max_index=int(rec.get("max_index", 0)),
                rssi=rssi,
                total_gain_db=int(rec.get("total_gain_db", 0)),
                base_pwr_db=int(rec.get("base_pwr_db", 0)),
                freq1_mhz=center_freq,
                freq2_mhz=0,
                max_exp=int(rec.get("max_exp", 0)),
                noise_dbm=noise,
                tsf_us=tsf,
                bins=bins,
                bin_dbm=bin_dbm,
            )
            samples.append(sample)

        return samples


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


def analyze_spectral_sample(
    sample: SpectralSample,
    threshold_delta_db: float = 10.0,
    absolute_threshold_dbm: Optional[float] = None,
) -> SpectralAnalysisReport:
    """Full RF analysis of a spectral sample: power, noise, peak freq, occupancy, classification."""
    label, conf, metrics = LightweightInterferenceClassifier.classify(sample)
    peak_freq = calculate_peak_interference_frequency(
        sample.bin_dbm,
        sample.freq1_mhz,
        sample.chan_width_mhz,
    )
    occupancy = calculate_channel_occupancy(
        sample.bin_dbm,
        sample.noise_dbm,
        threshold_delta_db=threshold_delta_db,
        absolute_threshold_dbm=absolute_threshold_dbm,
    )
    peak_pwr = max(sample.bin_dbm) if sample.bin_dbm else float(sample.noise_dbm)

    return SpectralAnalysisReport(
        center_freq_mhz=float(sample.freq1_mhz),
        chan_width_mhz=float(sample.chan_width_mhz),
        noise_floor_dbm=float(sample.noise_dbm),
        per_bin_power_dbm=sample.bin_dbm,
        peak_power_dbm=peak_pwr,
        peak_interference_freq_mhz=peak_freq,
        channel_occupancy_pct=occupancy,
        interference_class=label,
        confidence=conf,
        metrics=metrics,
    )
