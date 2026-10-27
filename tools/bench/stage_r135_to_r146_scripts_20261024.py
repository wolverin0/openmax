#!/usr/bin/env python3
"""Harden R136..R140 scripts and generate R141..R146 (Batch 5 PB-021/031/050) bench scripts."""

from __future__ import annotations

import py_compile
from pathlib import Path

BENCH_DIR = Path(__file__).resolve().parent

SPECS = [
    {
        "r_b4": 135,
        "r_b5": 141,
        "cov": 2,
        "dist": 1000,
        "dist_km": "1.0",
        "slot_us": 15,
        "ack_us": 36,
        "ap_be_low": 1550,
        "ap_be_high": 3100,
        "ap_thresh": 6200,
        "cpe_be_low": 2100,
        "cpe_be_high": 4200,
        "cpe_thresh": 8400,
        "codel_ms": 8,
        "interval_ms": 40,
        "rc_thresh": 24,
        "ampdu_frames": 32,
        "sgi_mode": "SGI-enabled",
    },
    {
        "r_b4": 136,
        "r_b5": 142,
        "cov": 6,
        "dist": 3000,
        "dist_km": "3.0",
        "slot_us": 27,
        "ack_us": 48,
        "ap_be_low": 1550,
        "ap_be_high": 3100,
        "ap_thresh": 6200,
        "cpe_be_low": 2100,
        "cpe_be_high": 4200,
        "cpe_thresh": 8400,
        "codel_ms": 8,
        "interval_ms": 40,
        "rc_thresh": 24,
        "ampdu_frames": 32,
        "sgi_mode": "SGI-enabled",
    },
    {
        "r_b4": 137,
        "r_b5": 143,
        "cov": 13,
        "dist": 6000,
        "dist_km": "6.0",
        "slot_us": 48,
        "ack_us": 69,
        "ap_be_low": 1550,
        "ap_be_high": 3100,
        "ap_thresh": 6200,
        "cpe_be_low": 2100,
        "cpe_be_high": 4200,
        "cpe_thresh": 8400,
        "codel_ms": 10,
        "interval_ms": 50,
        "rc_thresh": 24,
        "ampdu_frames": 32,
        "sgi_mode": "SGI-enabled",
    },
    {
        "r_b4": 138,
        "r_b5": 144,
        "cov": 20,
        "dist": 9000,
        "dist_km": "9.0",
        "slot_us": 69,
        "ack_us": 90,
        "ap_be_low": 1550,
        "ap_be_high": 3100,
        "ap_thresh": 6200,
        "cpe_be_low": 2100,
        "cpe_be_high": 4200,
        "cpe_thresh": 8400,
        "codel_ms": 12,
        "interval_ms": 60,
        "rc_thresh": 24,
        "ampdu_frames": 16,
        "sgi_mode": "LGI-preferred",
    },
    {
        "r_b4": 139,
        "r_b5": 145,
        "cov": 26,
        "dist": 12000,
        "dist_km": "12.0",
        "slot_us": 87,
        "ack_us": 108,
        "ap_be_low": 1550,
        "ap_be_high": 3100,
        "ap_thresh": 6200,
        "cpe_be_low": 2100,
        "cpe_be_high": 4200,
        "cpe_thresh": 8400,
        "codel_ms": 14,
        "interval_ms": 70,
        "rc_thresh": 24,
        "ampdu_frames": 16,
        "sgi_mode": "LGI-preferred",
    },
    {
        "r_b4": 140,
        "r_b5": 146,
        "cov": 31,
        "dist": 14000,
        "dist_km": "14.0",
        "slot_us": 102,
        "ack_us": 123,
        "ap_be_low": 1550,
        "ap_be_high": 3100,
        "ap_thresh": 6200,
        "cpe_be_low": 2100,
        "cpe_be_high": 4200,
        "cpe_thresh": 8400,
        "codel_ms": 16,
        "interval_ms": 80,
        "rc_thresh": 24,
        "ampdu_frames": 16,
        "sgi_mode": "LGI-preferred",
    },
]


def main() -> None:
    r135_path = next(BENCH_DIR.glob("run_live_autoresearch_r135_*.py"))
    r135_src = r135_path.read_text(encoding="utf-8")

    compiled = []

    # 1. Ensure R135..R140 all share the exact hardened R135 structure
    for sp in SPECS:
        r_b4 = sp["r_b4"]
        b4_files = list(BENCH_DIR.glob(f"run_live_autoresearch_r{r_b4}_*.py"))
        assert len(b4_files) == 1, f"Expected 1 file for r{r_b4}"
        b4_path = b4_files[0]
        if r_b4 != 135:
            # Transform R135 source to r_b4
            src = r135_src
            src = src.replace("135", str(r_b4))
            src = src.replace("covclass2", f"covclass{sp['cov']}")
            src = src.replace("COVCLASS2", f"COVCLASS{sp['cov']}")
            src = src.replace("coverage 2", f"coverage {sp['cov']}")
            src = src.replace("coverage_class=2", f"coverage_class={sp['cov']}")
            src = src.replace('"coverage_class": 2', f'"coverage_class": {sp["cov"]}')
            src = src.replace("1000m", f"{sp['dist']}m")
            src = src.replace("1000M", f"{sp['dist']}M")
            src = src.replace("1000 m", f"{sp['dist']} m")
            src = src.replace("1.0 km", f"{sp['dist_km']} km")
            src = src.replace("1.0km", f"{sp['dist_km']}km")
            src = src.replace('"distance_m": 1000', f'"distance_m": {sp["dist"]}')
            src = src.replace("slot_time_us=15", f"slot_time_us={sp['slot_us']}")
            src = src.replace("slot=15us", f"slot={sp['slot_us']}us")
            src = src.replace('"slot_time_us": 15', f'"slot_time_us": {sp["slot_us"]}')
            src = src.replace("ack_timeout_us=30", f"ack_timeout_us={sp['ack_us']}")
            src = src.replace("ACK=30us", f"ACK={sp['ack_us']}us")
            src = src.replace('"ack_timeout_us": 30', f'"ack_timeout_us": {sp["ack_us"]}')
            src = src.replace("codel8", f"codel{sp['codel_ms']}")
            src = src.replace("CODEL8", f"CODEL{sp['codel_ms']}")
            src = src.replace("8/40ms", f"{sp['codel_ms']}/{sp['interval_ms']}ms")
            src = src.replace("fq_target_us=8000", f"fq_target_us={sp['codel_ms'] * 1000}")
            src = src.replace("fq_interval_us=40000", f"fq_interval_us={sp['interval_ms'] * 1000}")
            b4_path.write_text(src, encoding="utf-8")
        py_compile.compile(str(b4_path), doraise=True)
        compiled.append(b4_path.name)

    # 2. Generate R141..R146 (Batch 5 PB-021 / PB-031 / PB-050 live scripts)
    for sp in SPECS:
        r_b5 = sp["r_b5"]
        ampdu = sp["ampdu_frames"]
        b5_name = (
            f"run_live_autoresearch_r{r_b5}_pb021_pb031_pb050_phy_ampdu{ampdu}_ldpc_stbc_"
            f"bidir_8flow_voip_covclass{sp['cov']}_{sp['dist']}m_be1550_2100_q1514_"
            f"codel{sp['codel_ms']}_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py"
        )
        b5_path = BENCH_DIR / b5_name

        src = r135_src
        src = src.replace("135", str(r_b5))
        src = src.replace("covclass2", f"covclass{sp['cov']}")
        src = src.replace("COVCLASS2", f"COVCLASS{sp['cov']}")
        src = src.replace("coverage 2", f"coverage {sp['cov']}")
        src = src.replace("coverage_class=2", f"coverage_class={sp['cov']}")
        src = src.replace('"coverage_class": 2', f'"coverage_class": {sp["cov"]}')
        src = src.replace("1000m", f"{sp['dist']}m")
        src = src.replace("1000M", f"{sp['dist']}M")
        src = src.replace("1000 m", f"{sp['dist']} m")
        src = src.replace("1.0 km", f"{sp['dist_km']} km")
        src = src.replace("1.0km", f"{sp['dist_km']}km")
        src = src.replace('"distance_m": 1000', f'"distance_m": {sp["dist"]}')
        src = src.replace("slot_time_us=15", f"slot_time_us={sp['slot_us']}")
        src = src.replace("slot=15us", f"slot={sp['slot_us']}us")
        src = src.replace('"slot_time_us": 15', f'"slot_time_us": {sp["slot_us"]}')
        src = src.replace("ack_timeout_us=30", f"ack_timeout_us={sp['ack_us']}")
        src = src.replace("ACK=30us", f"ACK={sp['ack_us']}us")
        src = src.replace('"ack_timeout_us": 30', f'"ack_timeout_us": {sp["ack_us"]}')
        src = src.replace("codel8", f"codel{sp['codel_ms']}")
        src = src.replace("CODEL8", f"CODEL{sp['codel_ms']}")
        src = src.replace("8/40ms", f"{sp['codel_ms']}/{sp['interval_ms']}ms")
        src = src.replace("fq_target_us=8000", f"fq_target_us={sp['codel_ms'] * 1000}")
        src = src.replace("fq_interval_us=40000", f"fq_interval_us={sp['interval_ms'] * 1000}")

        # Inject PB-021 / PB-031 / PB-050 hardware configuration and silicon register readback
        old_peer_extra = """echo 1 > /sys/kernel/debug/ieee80211/phy0/ath10k/ani_enable 2>/dev/null || true
echo {airtime_flags} > /sys/kernel/debug/ieee80211/phy0/airtime_flags 2>/dev/null || true
echo "fq_limit {fq_limit}" > /sys/kernel/debug/ieee80211/phy0/aqm 2>/dev/null || true
echo {force_tx_status} > /sys/kernel/debug/ieee80211/phy0/force_tx_status 2>/dev/null || true
iw phy phy0 set retry short {short_retry} long {long_retry} 2>/dev/null || true"""

        new_peer_extra = f"""echo 1 > /sys/kernel/debug/ieee80211/phy0/ath10k/ani_enable 2>/dev/null || true
echo {{airtime_flags}} > /sys/kernel/debug/ieee80211/phy0/airtime_flags 2>/dev/null || true
echo "fq_limit {{fq_limit}}" > /sys/kernel/debug/ieee80211/phy0/aqm 2>/dev/null || true
echo {{force_tx_status}} > /sys/kernel/debug/ieee80211/phy0/force_tx_status 2>/dev/null || true
iw phy phy0 set retry short {{short_retry}} long {{long_retry}} 2>/dev/null || true
if [ "{{force_tx_status}}" = "1" ]; then
  echo "3 {ampdu}" > /sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu 2>/dev/null || true
else
  echo "3 64" > /sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu 2>/dev/null || true
fi
cat /sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu 2>/dev/null || true
for reg in 0x21070 0x28014 0x280f8 0x29c08 0x2a370 0x29b00 0x2ab00; do
  echo $reg > /sys/kernel/debug/ieee80211/phy0/ath10k/reg_addr 2>/dev/null || true
  cat /sys/kernel/debug/ieee80211/phy0/ath10k/reg_value 2>/dev/null || true
done"""

        assert old_peer_extra in src, "Expected old_peer_extra in template"
        src = src.replace(old_peer_extra, new_peer_extra)
        src = src.replace(
            "Experiment #14 (openMAX_QCA988x_physical_boundary_research_2026-10-24.md)",
            f"PB-021 / PB-031 / PB-050 Joint PHY + A-MPDU ({ampdu} frames, {sp['sgi_mode']}) + Silicon Register Verification",
        )
        b5_path.write_text(src, encoding="utf-8")
        py_compile.compile(str(b5_path), doraise=True)
        compiled.append(b5_path.name)

    print(f"STAGED_AND_COMPILED_{len(compiled)}_SCRIPTS:")
    for name in compiled:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
