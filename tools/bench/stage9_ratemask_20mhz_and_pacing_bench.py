#!/usr/bin/env python3
"""Stage 9 — QCA988x Rate-Mask Authority & Bounding (FMX-0009 / Campaign C4),
20 MHz Real-WISP Sector Width Characterization (VHT20 vs VHT40 vs VHT80),
CoTSQ + Station Egress Pacing (FMX-0013 / Campaign C3), and Production procd + Watchdog Verification.
"""
import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage7_ptmp_bench as S7
import stage8_adaptive_and_sector_bench as S8

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "artifacts" / "stage9_ptmp"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# STAGE 9A: FMX-0009 QCA988x Rate-Mask Authority & Bounded Rate Envelope
# ==============================================================================
def run_stage9a_ratemask_authority_and_bounding():
    print("\n=== RUNNING STAGE 9A: FMX-0009 QCA988x Rate-Mask Authority & Bounded Rate Envelope ===")
    results_9a = {}
    S8.deploy_and_manage_controller(False)
    S7.set_vo_diffserv_bypass(True)
    S7.apply_ap_config(txpower_dbm=11, airtime_flags=3, aql_low=1500, aql_high=3000, aql_thresh=6000, amsdu=1, ampdu=16)

    try:
        # 1. Fixed-Rate Authority Proof (Clamp VHT to MCS 3 and HT to MCS 3 / MCS 11)
        print("\n--- 9A.1: Testing Fixed-Rate Mask Authority (VHT MCS 3, HT MCS 3/11) ---")
        S7.ap_ssh("iw dev phy0-ap0 set bitrates legacy-5 6 12 24 ht-mcs-5 3 11 vht-mcs-5 1:3 2:3")
        time.sleep(1.0)
        r_fixed = S7.run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="down", secs=6)
        tx_rates_fixed = {k: v["tx_bitrate"] for k, v in r_fixed["station_deltas"].items()}
        print(f"  [Fixed MCS 3/11 Mask] goodput={r_fixed['goodput_mbps']} total={r_fixed['total_goodput_mbps']} Mbps observed_tx_rates={tx_rates_fixed}")
        results_9a["fixed_rate_authority_mcs3"] = {
            "command": "iw dev phy0-ap0 set bitrates legacy-5 6 12 24 ht-mcs-5 3 11 vht-mcs-5 1:3 2:3",
            "observed_tx_bitrates": tx_rates_fixed,
            "trial": r_fixed,
        }

        # 2. Rate-Envelope Bounding Comparison under 3-Station Contention (11 dBm)
        envelope_modes = [
            (
                "Unbounded_Default_MCS_0_to_9",
                "iw dev phy0-ap0 set bitrates",
            ),
            (
                "Bounded_Envelope_No256QAM_MCS_0_to_5",
                "iw dev phy0-ap0 set bitrates legacy-5 6 12 24 ht-mcs-5 0 1 2 3 4 5 8 9 10 11 12 13 vht-mcs-5 1:0-5 2:0-5",
            ),
        ]
        results_9a["envelope_comparison_11dbm"] = {}
        for mode_name, cmd in envelope_modes:
            print(f"\n--- 9A.2: Testing {mode_name} ---")
            S7.ap_ssh(cmd)
            time.sleep(1.0)
            trials = []
            for t_idx in range(2):
                r = S7.run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="down", secs=8)
                trials.append(r)
                tot_retries = sum(v["tx_retries_delta"] for v in r["station_deltas"].values())
                tot_retrans = sum(v for v in r["tcp_retransmits"].values() if v >= 0)
                print(
                    f"  [{mode_name} Trial {t_idx+1}] total={r['total_goodput_mbps']} Mbps goodput={r['goodput_mbps']} "
                    f"hw_retries={tot_retries} tcp_retrans={tot_retrans} "
                    f"rtt_p50(loco/lbm5/sxt)={r['loaded_rtt']['loco5ac']['p50_ms']}/{r['loaded_rtt']['lbm5']['p50_ms']}/{r['loaded_rtt']['sxt']['p50_ms']} ms"
                )
            results_9a["envelope_comparison_11dbm"][mode_name] = trials
    finally:
        S7.ap_ssh("iw dev phy0-ap0 set bitrates")
        time.sleep(1.0)

    return results_9a


# ==============================================================================
# STAGE 9B: 20 MHz Real-WISP Sector Channel Width (VHT20 / HT20) Characterization
# ==============================================================================
def run_stage9b_20mhz_wisp_sector():
    print("\n=== RUNNING STAGE 9B: 20 MHz Real-WISP Production Channel Width (VHT20 / HT20) ===")
    results_9b = {"width_mhz": 20}
    try:
        print("\n--- Switching Sector AP to VHT20 (20 MHz) ---")
        ok = S8.set_ap_channel_width("VHT20")
        print(f"  [VHT20] All 3 stations associated: {ok}")
        S7.apply_ap_config(txpower_dbm=11, airtime_flags=3, aql_low=1500, aql_high=3000, aql_thresh=6000, amsdu=1, ampdu=16)
        S7.set_vo_diffserv_bypass(True)

        # Standalone Downlink per station at 20 MHz
        alone_dl = {}
        for st in ["loco5ac", "sxt", "lbm5"]:
            r_st = S7.run_single_or_multi_cell([st], direction="down", secs=6)
            alone_dl[st] = r_st
            print(
                f"  [VHT20 Alone DL {st}] sig={r_st['station_deltas'][st]['signal_dbm']} dBm "
                f"rate='{r_st['station_deltas'][st]['tx_bitrate']}' "
                f"goodput={r_st['goodput_mbps'][st]} Mbps p50={r_st['loaded_rtt'][st]['p50_ms']} ms"
            )
        results_9b["standalone_dl"] = alone_dl

        # 3-Station Simultaneous Downlink at 20 MHz
        dl_trials = []
        for t_idx in range(2):
            r_dl = S7.run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="down", secs=8)
            r_dl["spectral_efficiency_bps_per_hz"] = round(r_dl["total_goodput_mbps"] / 20.0, 3)
            dl_trials.append(r_dl)
            print(
                f"  [VHT20 All-3 DL Trial {t_idx+1}] goodput={r_dl['goodput_mbps']} "
                f"total={r_dl['total_goodput_mbps']} Mbps ({r_dl['spectral_efficiency_bps_per_hz']} bit/s/Hz) "
                f"jain={r_dl['jain_fairness']} "
                f"rtt_p50(loco/lbm5/sxt)={r_dl['loaded_rtt']['loco5ac']['p50_ms']}/{r_dl['loaded_rtt']['lbm5']['p50_ms']}/{r_dl['loaded_rtt']['sxt']['p50_ms']} ms"
            )
        results_9b["all3_dl_trials"] = dl_trials

        # 3-Station Simultaneous Uplink at 20 MHz
        ul_trials = []
        for t_idx in range(2):
            r_ul = S7.run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="up", secs=8)
            r_ul["spectral_efficiency_bps_per_hz"] = round(r_ul["total_goodput_mbps"] / 20.0, 3)
            ul_trials.append(r_ul)
            print(
                f"  [VHT20 All-3 UL Trial {t_idx+1}] goodput={r_ul['goodput_mbps']} "
                f"total={r_ul['total_goodput_mbps']} Mbps ({r_ul['spectral_efficiency_bps_per_hz']} bit/s/Hz) "
                f"jain={r_ul['jain_fairness']} "
                f"rtt_p50(loco/lbm5/sxt)={r_ul['loaded_rtt']['loco5ac']['p50_ms']}/{r_ul['loaded_rtt']['lbm5']['p50_ms']}/{r_ul['loaded_rtt']['sxt']['p50_ms']} ms"
            )
        results_9b["all3_ul_trials"] = ul_trials
    finally:
        print("\n--- Restoring Sector AP to VHT80 (80 MHz) ---")
        S8.set_ap_channel_width("VHT80")

    return results_9b


# ==============================================================================
# STAGE 9C: CoTSQ (FMX-0013) + Station Egress fq_codel Quantum 300 Tuning
# ==============================================================================
def run_stage9c_cotsq_and_station_fq_codel():
    print("\n=== RUNNING STAGE 9C: CoTSQ (FMX-0013) + Station Egress fq_codel Quantum 300 Tuning ===")
    gw_pass = os.environ.get("FMX_GATEWAY_PASS", "")
    results_9c = {}

    try:
        # 1. Default TCP TSQ (524288 B) + Default Station Queue
        print("\n--- 9C.1: Default_TSQ_512KB_Default_CPE_Qdisc ---")
        S7.omarchy_ssh(f"echo {gw_pass} | sudo -S sysctl -w net.ipv4.tcp_limit_output_bytes=524288 >/dev/null")
        S7.ap_ssh(
            "ssh -y root@10.99.0.2 'tc qdisc del dev phy0-sta0 root 2>/dev/null || true'; "
            "ssh -y root@10.99.0.3 'tc qdisc del dev phy0-sta0 root 2>/dev/null || true'"
        )
        t_def = S7.run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="up", secs=8)
        print(
            f"  [Default TSQ 512KB UL] total={t_def['total_goodput_mbps']} Mbps goodput={t_def['goodput_mbps']} "
            f"retrans={t_def['tcp_retransmits']} "
            f"rtt_p50(loco/lbm5/sxt)={t_def['loaded_rtt']['loco5ac']['p50_ms']}/{t_def['loaded_rtt']['lbm5']['p50_ms']}/{t_def['loaded_rtt']['sxt']['p50_ms']} ms"
        )
        results_9c["Default_TSQ_512KB_Default_CPE_Qdisc"] = t_def

        # 2. CoTSQ (131072 B = ~6ms at 175 Mbps) + Station fq_codel quantum 300 target 5ms interval 50ms
        print("\n--- 9C.2: FuturaMAX_CoTSQ_128KB_Plus_CPE_FQ_CoDel_Q300 ---")
        S7.omarchy_ssh(f"echo {gw_pass} | sudo -S sysctl -w net.ipv4.tcp_limit_output_bytes=131072 >/dev/null")
        S7.ap_ssh(
            "ssh -y root@10.99.0.2 'sysctl -w net.ipv4.tcp_limit_output_bytes=131072 >/dev/null; tc qdisc replace dev phy0-sta0 root fq_codel limit 1024 quantum 300 target 5ms interval 50ms ecn'; "
            "ssh -y root@10.99.0.3 'sysctl -w net.ipv4.tcp_limit_output_bytes=131072 >/dev/null; tc qdisc replace dev phy0-sta0 root fq_codel limit 1024 quantum 300 target 5ms interval 50ms ecn'"
        )
        t_cotsq = S7.run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="up", secs=8)
        print(
            f"  [CoTSQ 128KB + CPE fq_codel Q300 UL] total={t_cotsq['total_goodput_mbps']} Mbps goodput={t_cotsq['goodput_mbps']} "
            f"retrans={t_cotsq['tcp_retransmits']} "
            f"rtt_p50(loco/lbm5/sxt)={t_cotsq['loaded_rtt']['loco5ac']['p50_ms']}/{t_cotsq['loaded_rtt']['lbm5']['p50_ms']}/{t_cotsq['loaded_rtt']['sxt']['p50_ms']} ms"
        )
        results_9c["FuturaMAX_CoTSQ_128KB_Plus_CPE_FQ_CoDel_Q300"] = t_cotsq
    finally:
        S7.omarchy_ssh(f"echo {gw_pass} | sudo -S sysctl -w net.ipv4.tcp_limit_output_bytes=131072 >/dev/null")

    return results_9c


# ==============================================================================
# STAGE 9D: Production procd Service (/etc/init.d/futuramax) & Watchdog Qualification
# ==============================================================================
def run_stage9d_procd_and_watchdog_qualification():
    print("\n=== RUNNING STAGE 9D: Production OpenWrt procd Service & Canary Watchdog Qualification ===")
    files = [
        (ROOT / "controller" / "fmx_adaptive_controller.sh", "/usr/sbin/fmx_adaptive_controller.sh"),
        (ROOT / "controller" / "fmx_watchdog.sh", "/usr/sbin/fmx_watchdog.sh"),
        (ROOT / "controller" / "futuramax.init", "/etc/init.d/futuramax"),
    ]
    for src, dst in files:
        raw_bytes = src.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")
        subprocess.run(
            S7.SSH_BASE + [f"root@{S7.AP_MGMT}", f"cat > {dst} && sed -i 's/\\r$//' {dst} && chmod +x {dst}"],
            input=raw_bytes,
            capture_output=True,
            timeout=15,
        )

    S7.ap_ssh("/etc/init.d/futuramax enable && /etc/init.d/futuramax restart")
    time.sleep(6.0)
    ubus_out, _, _ = S7.ap_ssh("ubus call service list '{\"name\":\"futuramax\"}'")
    ctrl_state, _, _ = S7.ap_ssh("cat /tmp/fmx_controller_state.json 2>/dev/null || true")
    wd_state, _, _ = S7.ap_ssh("cat /tmp/fmx_watchdog_status.json 2>/dev/null || true")
    print(f"  [procd service] controller={ctrl_state} watchdog={wd_state}")
    return {
        "procd_ubus_status": json.loads(ubus_out) if ubus_out.startswith("{") else ubus_out,
        "controller_state": json.loads(ctrl_state) if ctrl_state.startswith("{") else ctrl_state,
        "watchdog_status": json.loads(wd_state) if wd_state.startswith("{") else wd_state,
    }


def main():
    S7.setup_infrastructure()
    report = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "stage9a_ratemask_authority_and_bounding": run_stage9a_ratemask_authority_and_bounding(),
        "stage9b_20mhz_wisp_sector": run_stage9b_20mhz_wisp_sector(),
        "stage9c_cotsq_and_station_fq_codel": run_stage9c_cotsq_and_station_fq_codel(),
        "stage9d_procd_and_watchdog": run_stage9d_procd_and_watchdog_qualification(),
    }
    out_path = OUT_DIR / "stage9_ratemask_20mhz_and_pacing_results.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved complete Stage 9 results to {out_path}")


if __name__ == "__main__":
    main()
