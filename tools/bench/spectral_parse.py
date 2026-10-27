#!/usr/bin/env python3
"""Parse ath10k spectral_scan0 relay dumps (FFT sample type 3) into per-sample rows + a summary.

Summary: decodes the binary relay stream the ath10k driver writes (struct fft_sample_tlv + struct
fft_sample_ath10k, big-endian, from Linux spectral_common.h) into CSV/JSON: timestamp (tsf), freq1,
freq2, width, noise, max_magnitude, max_index, rssi, relpwr/avgpwr, per-bin magnitudes (dB-ish via
max_exp). Keywords: spectral, FFT, ath10k, QCA988x, WiFiSpectralJam comparison, campaign C1.
Read when: turning a capture from tools/bench/bench.py spectral into numbers. Usage:
  python tools/bench/spectral_parse.py <capture.bin> [--csv out.csv] [--json out.json]
Layout verified against the first LAP-120 capture (2026-10-05): 93 B per 64-bin sample.
"""
import argparse, json, struct, sys, statistics
from pathlib import Path

TLV = struct.Struct(">BH")            # type, length
HDR = struct.Struct(">BHHhHHHqbBBBB")  # chan_width_mhz, freq1, freq2, noise, max_magnitude, total_gain_db,
                                      # base_pwr_db, tsf, max_index, rssi, relpwr_db, avgpwr_db, max_exp
ATH10K_TYPE = 3


def parse(data: bytes):
    i = 0
    rows = []
    while i + TLV.size <= len(data):
        t, length = TLV.unpack_from(data, i)
        body = data[i + TLV.size:i + TLV.size + length]
        i += TLV.size + length
        if t != ATH10K_TYPE or len(body) < HDR.size:
            continue
        (width, f1, f2, noise, maxmag, gain, basepwr, tsf, maxidx, rssi, relpwr, avgpwr, maxexp) = HDR.unpack_from(body, 0)
        bins = list(body[HDR.size:])
        # magnitude -> dB-like value per ath9k/ath10k userspace convention: 20*log10(bin << max_exp) relative
        import math
        mags = [(b << maxexp) for b in bins]
        sq = sum(m * m for m in mags) or 1
        bins_db = [round(10 * math.log10((m * m) / sq) + noise + rssi, 1) if m else None for m in mags]
        rows.append({"tsf": tsf, "width_mhz": width, "freq1": f1, "freq2": f2, "noise": noise, "max_magnitude": maxmag,
                     "max_index": maxidx, "rssi": rssi, "relpwr_db": relpwr, "avgpwr_db": avgpwr, "max_exp": maxexp,
                     "nbins": len(bins), "bins_raw": bins, "bins_db": bins_db})
    return rows


def summary(rows):
    if not rows:
        return {"samples": 0}
    by_freq = {}
    for r in rows:
        by_freq.setdefault(r["freq1"], []).append(r)
    out = {"samples": len(rows), "nbins": rows[0]["nbins"], "per_freq": {}}
    for f, rs in sorted(by_freq.items()):
        out["per_freq"][str(f)] = {
            "samples": len(rs),
            "noise_med": statistics.median(r["noise"] for r in rs),
            "rssi_med": statistics.median(r["rssi"] for r in rs),
            "rssi_max": max(r["rssi"] for r in rs),
            "maxmag_med": statistics.median(r["max_magnitude"] for r in rs),
            "max_index_mode": statistics.mode(r["max_index"] for r in rs),
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("capture")
    ap.add_argument("--csv")
    ap.add_argument("--json")
    a = ap.parse_args()
    data = Path(a.capture).read_bytes()
    rows = parse(data)
    s = summary(rows)
    print(json.dumps(s, indent=1))
    if a.csv:
        import csv
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["tsf", "freq1", "freq2", "width", "noise", "max_magnitude", "max_index", "rssi", "relpwr", "avgpwr", "max_exp"] + [f"bin{i}" for i in range(rows[0]["nbins"] if rows else 0)])
            for r in rows:
                w.writerow([r["tsf"], r["freq1"], r["freq2"], r["width_mhz"], r["noise"], r["max_magnitude"], r["max_index"], r["rssi"], r["relpwr_db"], r["avgpwr_db"], r["max_exp"]] + r["bins_raw"])
    if a.json:
        Path(a.json).write_text(json.dumps({"summary": s, "rows": rows}), encoding="utf-8")


if __name__ == "__main__":
    main()
