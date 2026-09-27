"""
Test suite and synthetic benchmark for ath10k Spectral FFT Parser and Classifier.
Verifies binary unpack correctness, detection thresholds, and execution speed.
"""

import struct
import time
from telemetry.spectral_fft.parser import (
    SpectralParser, LightweightInterferenceClassifier, InterferenceClass,
    ATH_FFT_SAMPLE_ATH10K, HEADER_FORMAT, HEADER_SIZE
)


def build_synthetic_sample(
    chan_width: int = 20,
    noise_dbm: int = -95,
    bin_pattern: str = "clean",
    bin_count: int = 56
) -> bytes:
    """Generate a byte buffer matching ath10k RelayFS wire format."""
    tlv_type = ATH_FFT_SAMPLE_ATH10K
    payload_len = (HEADER_SIZE - 3) + bin_count
    
    relpwr = 10
    avgpwr = 25
    max_mag = 120
    max_idx = 0
    rssi = -65
    gain = 40
    base_pwr = 15
    freq1 = 5500
    freq2 = 0
    max_exp = 2
    tsf = 1234567890123

    # Generate bin bytes
    if bin_pattern == "clean":
        # Flat noise with slight OFDM variance (around 30-40)
        bins = bytearray([35 + (i % 5) for i in range(bin_count)])
    elif bin_pattern == "radar":
        # Flat noise, but bin 28 has a massive single-tone spike (240)
        bins = bytearray([25 for _ in range(bin_count)])
        bins[bin_count // 2] = 245
        max_idx = 0
    elif bin_pattern == "adjacent_tilt":
        # Left side clean (20), right side heavily jammed by adjacent sector (180)
        bins = bytearray([20 if i < bin_count // 2 else 170 for i in range(bin_count)])
    elif bin_pattern == "high_noise":
        noise_dbm = -75
        bins = bytearray([80 for _ in range(bin_count)])
    else:
        bins = bytearray([30 for _ in range(bin_count)])

    header = struct.pack(
        HEADER_FORMAT,
        tlv_type, payload_len, chan_width, relpwr, avgpwr,
        max_mag, max_idx, rssi, gain, base_pwr,
        freq1, freq2, max_exp, noise_dbm, tsf
    )
    return header + bytes(bins)


def test_parser_and_classifier():
    print("==================================================")
    print("  TESTING ath10k SPECTRAL FFT PARSER & CLASSIFIER")
    print("==================================================")

    parser = SpectralParser()
    classifier = LightweightInterferenceClassifier()

    # 1. Test Clean Channel
    raw_clean = build_synthetic_sample(bin_pattern="clean")
    samples_clean = list(parser.feed(raw_clean))
    assert len(samples_clean) == 1, "Should parse exactly 1 clean sample"
    s = samples_clean[0]
    assert s.chan_width_mhz == 20
    assert s.noise_dbm == -95
    assert len(s.bins) == 56
    label, conf, metrics = classifier.classify(s)
    print(f"[+] Clean Channel: {label} (conf={conf:.2f}, sfm={metrics['sfm']:.4f}, max_med={metrics['max_med_db']} dB)")
    assert label == InterferenceClass.CLEAN, f"Expected CLEAN, got {label}"

    # 2. Test Radar DFS Spike
    raw_radar = build_synthetic_sample(bin_pattern="radar")
    samples_radar = list(parser.feed(raw_radar))
    s_radar = samples_radar[0]
    label, conf, metrics = classifier.classify(s_radar)
    print(f"[+] Radar Spike:   {label} (conf={conf:.2f}, papr={metrics['papr_db']} dB, max_med={metrics['max_med_db']} dB)")
    assert label in [InterferenceClass.RADAR_DFS, InterferenceClass.NARROWBAND_CW], f"Expected RADAR, got {label}"

    # 3. Test Adjacent Channel Interference (Tilt)
    raw_tilt = build_synthetic_sample(bin_pattern="adjacent_tilt")
    samples_tilt = list(parser.feed(raw_tilt))
    s_tilt = samples_tilt[0]
    label, conf, metrics = classifier.classify(s_tilt)
    print(f"[+] Adjacent Tilt: {label} (conf={conf:.2f}, asym={metrics['asym_ratio']:.3f})")
    assert label == InterferenceClass.ADJACENT_CHANNEL, f"Expected ADJACENT_CHANNEL, got {label}"

    # 4. Test High Noise Floor
    raw_noise = build_synthetic_sample(bin_pattern="high_noise")
    samples_noise = list(parser.feed(raw_noise))
    s_noise = samples_noise[0]
    label, conf, metrics = classifier.classify(s_noise)
    print(f"[+] Elevated Noise:{label} (conf={conf:.2f}, floor={metrics['noise_floor_dbm']} dBm)")
    assert label == InterferenceClass.BROADBAND_NOISE, f"Expected BROADBAND_NOISE, got {label}"

    # 5. Embedded CPU Execution Benchmark
    N_RUNS = 2000
    t0 = time.perf_counter()
    for _ in range(N_RUNS):
        classifier.classify(s_radar)
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000.0
    us_per_sample = (elapsed_ms * 1000.0) / N_RUNS
    print(f"[+] Benchmark: {N_RUNS} classifications in {elapsed_ms:.2f} ms ({us_per_sample:.2f} µs per sample)")
    assert us_per_sample < 50.0, "Classification must be under 50 µs for embedded MIPS CPU"

    print("\n>>> ALL SPECTRAL TESTS PASSED WITH 100% SUCCESS <<<\n")


if __name__ == "__main__":
    test_parser_and_classifier()
