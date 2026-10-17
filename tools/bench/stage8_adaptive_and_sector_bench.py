#!/usr/bin/env python3
"""Stage 8 — Closed-Loop Adaptive Sector Controller, Spectral FFT & Channel-Width Optimizer,
and Peak-Hour Bidirectional 6-Flow WISP Sector Stress Test.

Runs across the 3-station heterogeneous PtMP bench:
  - AP        : Ubiquiti LiteAP AC (LAP-120, 192.168.1.2 / 10.99.0.1, OpenWrt 24.10.4 ath10k-ct)
  - Station 1 : Ubiquiti NanoStation 5AC Loco (10.99.0.2, OpenWrt 24.10.4 ath10k-ct, 802.11ac VHT80 2x2, Room)
  - Station 2 : MikroTik SXT Lite5 (10.99.0.3, OpenWrt 24.10.4 ath9k, 802.11n HT40 2x2, Behind Wall/Door)
  - Station 3 : Ubiquiti LiteBeam M5 (10.99.0.4, Stock airOS 6.1.4 ath_hal, 802.11n HT40 1x1, Behind Wall/Door)
"""
import datetime
import json
import os
import re
import statistics
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage7_ptmp_bench as S7

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "artifacts" / "stage8_ptmp"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CONTROLLER_SCRIPT = ROOT / "controller" / "fmx_adaptive_controller.sh"


def deploy_and_manage_controller(enable: bool):
    """Push controller/fmx_adaptive_controller.sh to LAP-120 AP and start or stop it."""
    S7.ap_ssh("killall fmx_adaptive_controller.sh 2>/dev/null || true; rm -f /tmp/fmx_controller_state.json")
    if not enable:
        return
    script_bytes = CONTROLLER_SCRIPT.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")
    subprocess.run(
        S7.SSH_BASE + [f"root@{S7.AP_MGMT}", "cat > /usr/sbin/fmx_adaptive_controller.sh && sed -i 's/\\r$//' /usr/sbin/fmx_adaptive_controller.sh && chmod +x /usr/sbin/fmx_adaptive_controller.sh"],
        input=script_bytes,
        capture_output=True,
        timeout=15,
    )
    S7.ap_ssh("start-stop-daemon -S -b -x /usr/sbin/fmx_adaptive_controller.sh -- phy0-ap0")
    time.sleep(2.0)


def wait_all_stations_associated(timeout: int = 60) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        out, _, _ = S7.ap_ssh("iw dev phy0-ap0 station dump | grep ^Station | wc -l; ping -c 1 -W 1 10.99.0.2 >/dev/null 2>&1 && ping -c 1 -W 1 10.99.0.3 >/dev/null 2>&1 && ping -c 1 -W 1 10.99.0.4 >/dev/null 2>&1 && echo ALL_PING_OK")
        if "ALL_PING_OK" in out:
            return True
        time.sleep(2.0)
    return False


# ==============================================================================
# STAGE 8A: Closed-Loop Adaptive Sector Controller vs Static Policies
# ==============================================================================
def run_stage8a_adaptive_controller():
    print("\n=== RUNNING STAGE 8A: Closed-Loop Adaptive Sector Controller (3-Phase Workload) ===")
    results_8a = {}
    policies = [
        {
            "id": "Policy_1_Static_Unbounded_NoATF",
            "desc": "Static Unbounded Single-CPE Config (ATF=Off, AQL 24000/48000, Agg 3x64, No AC_VO Bypass)",
            "controller": False,
            "vo_bypass": False,
            "cfg": dict(txpower_dbm=5, airtime_flags=0, aql_low=24000, aql_high=24000, aql_thresh=48000, amsdu=3, ampdu=64,
                        weights={"loco5ac": 256, "sxt": 256, "lbm5": 256}),
        },
        {
            "id": "Policy_2_Static_Equal_ATF_SmallAgg",
            "desc": "Static Conservative Multi-CPE Config (ATF=On, Equal 256:256:256, AQL 1000/2000, Agg 1x8, No AC_VO Bypass)",
            "controller": False,
            "vo_bypass": False,
            "cfg": dict(txpower_dbm=5, airtime_flags=3, aql_low=1000, aql_high=2000, aql_thresh=4000, amsdu=1, ampdu=8,
                        weights={"loco5ac": 256, "sxt": 256, "lbm5": 256}),
        },
        {
            "id": "Policy_3_FuturaMAX_ClosedLoop_Adaptive",
            "desc": "FuturaMAX Closed-Loop Adaptive Controller Daemon (Auto SINGLE_STA_TURBO <-> MULTI_STA_ADAPTIVE + Proportional ATF + WMM AC_VO Bypass)",
            "controller": True,
            "vo_bypass": True,
            "cfg": dict(txpower_dbm=5, airtime_flags=3, aql_low=3000, aql_high=6000, aql_thresh=12000, amsdu=3, ampdu=64,
                        weights={"loco5ac": 768, "sxt": 128, "lbm5": 256}),
        },
    ]

    try:
        for pol in policies:
            print(f"\n--- Testing {pol['id']}: {pol['desc']} ---")
            deploy_and_manage_controller(False)
            S7.apply_ap_config(**pol["cfg"])
            S7.set_vo_diffserv_bypass(pol["vo_bypass"])
            if pol["controller"]:
                deploy_and_manage_controller(True)

            # Phase 1: Single-Station Burst (loco5ac alone, 6s)
            p1 = S7.run_single_or_multi_cell(["loco5ac"], direction="down", secs=6)
            st1, _, _ = S7.ap_ssh("cat /tmp/fmx_controller_state.json 2>/dev/null || true")
            p1["controller_state"] = st1
            print(f"  [Phase 1: Single-Station Burst (loco5ac)] goodput={p1['goodput_mbps']['loco5ac']} Mbps loco_p50={p1['loaded_rtt']['loco5ac']['p50_ms']} ms state={st1}")

            # Phase 2: All-3 Simultaneous Contention Burst (loco5ac + sxt + lbm5, 8s)
            p2 = S7.run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="down", secs=8)
            st2, _, _ = S7.ap_ssh("cat /tmp/fmx_controller_state.json 2>/dev/null || true")
            p2["controller_state"] = st2
            print(
                f"  [Phase 2: All-3 Contention Burst] goodput={p2['goodput_mbps']} total={p2['total_goodput_mbps']} Mbps "
                f"sxt_p50/p95={p2['loaded_rtt']['sxt']['p50_ms'] if p2['loaded_rtt']['sxt'] else None}/{p2['loaded_rtt']['sxt']['p95_ms'] if p2['loaded_rtt']['sxt'] else None} ms "
                f"lbm5_p50/p95={p2['loaded_rtt']['lbm5']['p50_ms'] if p2['loaded_rtt']['lbm5'] else None}/{p2['loaded_rtt']['lbm5']['p95_ms'] if p2['loaded_rtt']['lbm5'] else None} ms "
                f"loco_p50/p95={p2['loaded_rtt']['loco5ac']['p50_ms'] if p2['loaded_rtt']['loco5ac'] else None}/{p2['loaded_rtt']['loco5ac']['p95_ms'] if p2['loaded_rtt']['loco5ac'] else None} ms "
                f"state={st2}"
            )

            # Phase 3: Return to Single-Station Burst (loco5ac alone, 6s)
            time.sleep(1.5)
            p3 = S7.run_single_or_multi_cell(["loco5ac"], direction="down", secs=6)
            st3, _, _ = S7.ap_ssh("cat /tmp/fmx_controller_state.json 2>/dev/null || true")
            p3["controller_state"] = st3
            print(f"  [Phase 3: Recovery Single-Station (loco5ac)] goodput={p3['goodput_mbps']['loco5ac']} Mbps loco_p50={p3['loaded_rtt']['loco5ac']['p50_ms']} ms state={st3}")

            results_8a[pol["id"]] = {
                "description": pol["desc"],
                "phase1_single_sta": p1,
                "phase2_all3_contention": p2,
                "phase3_single_sta_recovery": p3,
            }
    finally:
        deploy_and_manage_controller(False)
        S7.set_vo_diffserv_bypass(True)
        S7.apply_ap_config(txpower_dbm=11, airtime_flags=3, aql_low=1500, aql_high=3000, aql_thresh=6000, amsdu=2, ampdu=32)

    return results_8a


# ==============================================================================
# STAGE 8B: Live Spectral FFT Capture & VHT80 vs VHT40 Channel-Width Optimizer
# ==============================================================================
def capture_ap_spectral_fft() -> dict:
    """Capture a live hardware Spectral FFT scan from LAP-120 QCA9882 debugfs."""
    sys.path.insert(0, str(ROOT))
    from telemetry.spectral_fft.parser import SpectralParser, analyze_spectral_sample

    cmd = """
echo background > /sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan_ctl 2>/dev/null
echo trigger > /sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan_ctl 2>/dev/null
iw dev phy0-ap0 scan freq 5180 5200 5220 5240 ap-force >/dev/null 2>&1
echo disable > /sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan_ctl 2>/dev/null
cat /sys/kernel/debug/ieee80211/phy0/ath10k/spectral_scan0 > /tmp/fft_stage8.bin 2>/dev/null
ls -la /tmp/fft_stage8.bin
"""
    S7.ap_ssh(cmd, timeout=30)
    r = subprocess.run(S7.SSH_BASE + [f"root@{S7.AP_MGMT}", "cat /tmp/fft_stage8.bin"], capture_output=True, timeout=15)
    raw = r.stdout
    parser = SpectralParser()
    samples = list(parser.feed(raw))
    per_freq = {}
    for freq in sorted(list({s.freq1_mhz for s in samples})):
        f_samples = [s for s in samples if s.freq1_mhz == freq]
        rep = analyze_spectral_sample(f_samples[len(f_samples) // 2])
        per_freq[str(freq)] = {
            "count": len(f_samples),
            "mean_noise_dbm": round(statistics.mean(s.noise_dbm for s in f_samples), 2),
            "mean_rssi_db": round(statistics.mean(s.rssi for s in f_samples), 2),
            "interference_class": rep.interference_class,
            "channel_occupancy_pct": rep.channel_occupancy_pct,
            "peak_power_dbm": rep.peak_power_dbm,
        }
    wait_all_stations_associated(timeout=20)
    return {
        "total_bytes": len(raw),
        "frames_parsed": len(samples),
        "frequencies_scanned_mhz": sorted(list({s.freq1_mhz for s in samples})) if samples else [],
        "mean_noise_dbm": round(statistics.mean(s.noise_dbm for s in samples), 2) if samples else None,
        "mean_rssi_db": round(statistics.mean(s.rssi for s in samples), 2) if samples else None,
        "per_frequency_summary": per_freq,
    }


def set_ap_channel_width(htmode: str):
    """Switch LAP-120 AP between VHT80 and VHT40 and restore wlink IP + fastpath after reload."""
    cmd = f"""
uci set wireless.radio0.htmode='{htmode}'
uci commit wireless
wifi reload
sleep 6
ip addr del 10.99.0.1/30 dev phy0-ap0 2>/dev/null || true
ip addr add 10.99.0.1/24 dev phy0-ap0 2>/dev/null || true
ip route replace 10.99.0.0/24 dev phy0-ap0 src 10.99.0.1
"""
    S7.ap_ssh(cmd, timeout=30)
    ok = wait_all_stations_associated(timeout=45)
    S7.apply_ap_config(txpower_dbm=11, airtime_flags=3, aql_low=1500, aql_high=3000, aql_thresh=6000, amsdu=2, ampdu=32)
    S7.set_vo_diffserv_bypass(True)
    return ok


def run_stage8b_spectral_and_width():
    print("\n=== RUNNING STAGE 8B: Live Hardware Spectral FFT & Channel-Width Optimizer (VHT80 vs VHT40) ===")
    fft_info = capture_ap_spectral_fft()
    print(f"  [Spectral FFT] bytes={fft_info['total_bytes']} frames={fft_info['frames_parsed']} noise={fft_info['mean_noise_dbm']} dBm")

    width_results = {}
    try:
        for mode, mhz in [("VHT80", 80), ("VHT40", 40)]:
            print(f"\n--- Switching Sector AP to {mode} ({mhz} MHz) ---")
            ok = set_ap_channel_width(mode)
            print(f"  [{mode}] All 3 stations associated: {ok}")
            dl_trials = []
            ul_trials = []
            for t_idx in range(2):
                r_dl = S7.run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="down", secs=8)
                r_dl["spectral_efficiency_bps_per_hz"] = round(r_dl["total_goodput_mbps"] / mhz, 3)
                dl_trials.append(r_dl)
                print(
                    f"  [{mode} All-3 DL Trial {t_idx+1}] goodput={r_dl['goodput_mbps']} "
                    f"total={r_dl['total_goodput_mbps']} Mbps ({r_dl['spectral_efficiency_bps_per_hz']} bit/s/Hz) "
                    f"jain={r_dl['jain_fairness']}"
                )
            for t_idx in range(2):
                r_ul = S7.run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="up", secs=8)
                r_ul["spectral_efficiency_bps_per_hz"] = round(r_ul["total_goodput_mbps"] / mhz, 3)
                ul_trials.append(r_ul)
                print(
                    f"  [{mode} All-3 UL Trial {t_idx+1}] goodput={r_ul['goodput_mbps']} "
                    f"total={r_ul['total_goodput_mbps']} Mbps ({r_ul['spectral_efficiency_bps_per_hz']} bit/s/Hz) "
                    f"jain={r_ul['jain_fairness']}"
                )
            width_results[mode] = {
                "width_mhz": mhz,
                "all3_dl_trials": dl_trials,
                "all3_ul_trials": ul_trials,
            }
    finally:
        print("\n--- Restoring Sector AP to VHT80 (80 MHz) ---")
        set_ap_channel_width("VHT80")

    return {"spectral_fft_capture": fft_info, "channel_width_comparison": width_results}


# ==============================================================================
# STAGE 8C: Peak-Hour Bidirectional 6-Flow WISP Sector Stress Test (3 DL + 3 UL + Interactive)
# ==============================================================================
def run_bidirectional_6flow_cell(secs: int = 10) -> dict:
    """Simultaneously run 3 Downlink TCP streams + 3 Uplink TCP streams + 3 Interactive Ping flows."""
    # Ensure each station has two iperf3 servers (port 5201 for DL, port 5202 for UL)
    S7.ap_ssh(
        "ssh -y root@10.99.0.2 'netstat -ltn 2>/dev/null | grep -q \":5202 \" || iperf3 -s -D -p 5202'; "
        "ssh -y root@10.99.0.3 'netstat -ltn 2>/dev/null | grep -q \":5202 \" || iperf3 -s -D -p 5202'"
    )
    S7.lbm5_exec("ps | grep -v grep | grep -q 'iperf3 -s -D -p 5202' || /tmp/libc.so --library-path /tmp /tmp/iperf3 -s -D -p 5202 >/dev/null 2>&1 </dev/null")

    dl_res = {}
    ul_res = {}
    rtts = {}

    def dl_worker(name: str):
        ip = S7.STATIONS[name]["ip"]
        out, _, _ = S7.omarchy_ssh(f"iperf3 -c {ip} -p 5201 -t {secs} -P 1 -J", timeout=secs + 25)
        try:
            j = json.loads(out[out.find("{"):])
            dl_res[name] = round(j["end"]["sum_received"]["bits_per_second"] / 1e6, 2)
        except Exception:
            dl_res[name] = 0.0

    def ul_worker(name: str):
        ip = S7.STATIONS[name]["ip"]
        out, _, _ = S7.omarchy_ssh(f"iperf3 -c {ip} -p 5202 -t {secs} -P 1 -R -J", timeout=secs + 25)
        try:
            j = json.loads(out[out.find("{"):])
            ul_res[name] = round(j["end"]["sum_received"]["bits_per_second"] / 1e6, 2)
        except Exception:
            ul_res[name] = 0.0

    def ping_worker(name: str):
        ip = S7.STATIONS[name]["ip"]
        count = max(int(secs * 4), 8)
        out, _, _ = S7.omarchy_ssh(f"ping -i 0.2 -c {count} -W 1 {ip}", timeout=secs + 15)
        samples = sorted(float(m.group(1)) for m in re.finditer(r"time=([0-9.]+)\s*ms", out))
        if samples:
            rtts[name] = {
                "n": len(samples),
                "p50_ms": round(statistics.median(samples), 2),
                "p95_ms": round(samples[min(len(samples) - 1, int(0.95 * (len(samples) - 1)))], 2),
                "p99_ms": round(samples[-1], 2),
                "mean_ms": round(statistics.mean(samples), 2),
            }
        else:
            rtts[name] = None

    threads = []
    for name in S7.STATIONS:
        threads.append(threading.Thread(target=dl_worker, args=(name,)))
        threads.append(threading.Thread(target=ul_worker, args=(name,)))
        threads.append(threading.Thread(target=ping_worker, args=(name,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    total_dl = round(sum(dl_res.values()), 2)
    total_ul = round(sum(ul_res.values()), 2)
    return {
        "dl_goodput_mbps": dl_res,
        "ul_goodput_mbps": ul_res,
        "total_dl_mbps": total_dl,
        "total_ul_mbps": total_ul,
        "total_bidirectional_sector_mbps": round(total_dl + total_ul, 2),
        "loaded_rtt": rtts,
    }


def run_stage8c_bidirectional_sector_sim():
    print("\n=== RUNNING STAGE 8C: Peak-Hour Bidirectional 6-Flow WISP Sector Simulation (3 DL + 3 UL + Interactive) ===")
    gw_pass = os.environ.get("FMX_GATEWAY_PASS", "")
    results_8c = {}
    try:
        # 1. Unoptimized Stock OpenWrt Sector
        print("\n--- Mode 1: Unoptimized_Stock_OpenWrt_Sector ---")
        deploy_and_manage_controller(False)
        S7.set_vo_diffserv_bypass(False)
        S7.apply_ap_config(txpower_dbm=11, airtime_flags=0, aql_low=24000, aql_high=24000, aql_thresh=48000, amsdu=3, ampdu=64)
        S7.ap_ssh("ssh -y root@10.99.0.2 'iw phy phy0 set rts off'; ssh -y root@10.99.0.3 'iw phy phy0 set rts off'")
        S7.lbm5_exec("iwconfig ath0 rts off")
        S7.omarchy_ssh(f"echo {gw_pass} | sudo -S tc qdisc del dev eno1 root 2>/dev/null || true")

        unopt_trials = []
        for t_idx in range(2):
            r = run_bidirectional_6flow_cell(secs=8)
            unopt_trials.append(r)
            print(
                f"  [Unoptimized BiDir Trial {t_idx+1}] DL={r['total_dl_mbps']} Mbps UL={r['total_ul_mbps']} Mbps "
                f"Total={r['total_bidirectional_sector_mbps']} Mbps "
                f"RTT(p50/p95): loco={r['loaded_rtt']['loco5ac']['p50_ms']}/{r['loaded_rtt']['loco5ac']['p95_ms']} ms "
                f"sxt={r['loaded_rtt']['sxt']['p50_ms']}/{r['loaded_rtt']['sxt']['p95_ms']} ms "
                f"lbm5={r['loaded_rtt']['lbm5']['p50_ms']}/{r['loaded_rtt']['lbm5']['p95_ms']} ms"
            )
        results_8c["Unoptimized_Stock_OpenWrt_Sector"] = unopt_trials

        # 2. FuturaMAX Full Stage 8 Stack (Adaptive Controller + ATF + AQL + WMM AC_VO Bypass + Station RTS 256B + Gateway CAKE)
        print("\n--- Mode 2: FuturaMAX_Full_Stage8_Sector_Stack ---")
        S7.apply_ap_config(txpower_dbm=11, airtime_flags=3, aql_low=1000, aql_high=2000, aql_thresh=4000, amsdu=1, ampdu=16)
        S7.set_vo_diffserv_bypass(True)
        deploy_and_manage_controller(True)
        S7.ap_ssh("ssh -y root@10.99.0.2 'iw phy phy0 set rts 256'; ssh -y root@10.99.0.3 'iw phy phy0 set rts 256'")
        S7.lbm5_exec("iwconfig ath0 rts 256")
        S7.omarchy_ssh(f"echo {gw_pass} | sudo -S tc qdisc replace dev eno1 root cake bandwidth 110Mbit diffserv4 nat ack-filter")

        fmx_trials = []
        for t_idx in range(2):
            r = run_bidirectional_6flow_cell(secs=8)
            fmx_trials.append(r)
            print(
                f"  [FuturaMAX Full Stack BiDir Trial {t_idx+1}] DL={r['total_dl_mbps']} Mbps UL={r['total_ul_mbps']} Mbps "
                f"Total={r['total_bidirectional_sector_mbps']} Mbps "
                f"RTT(p50/p95): loco={r['loaded_rtt']['loco5ac']['p50_ms']}/{r['loaded_rtt']['loco5ac']['p95_ms']} ms "
                f"sxt={r['loaded_rtt']['sxt']['p50_ms']}/{r['loaded_rtt']['sxt']['p95_ms']} ms "
                f"lbm5={r['loaded_rtt']['lbm5']['p50_ms']}/{r['loaded_rtt']['lbm5']['p95_ms']} ms"
            )
        results_8c["FuturaMAX_Full_Stage8_Sector_Stack"] = fmx_trials
    finally:
        S7.omarchy_ssh(f"echo {gw_pass} | sudo -S tc qdisc del dev eno1 root 2>/dev/null || true")
        deploy_and_manage_controller(True)

    return results_8c


def main():
    S7.setup_infrastructure()
    report = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "stage8a_closed_loop_adaptive_controller": run_stage8a_adaptive_controller(),
        "stage8b_spectral_fft_and_channel_width": run_stage8b_spectral_and_width(),
        "stage8c_bidirectional_6flow_sector_simulation": run_stage8c_bidirectional_sector_sim(),
    }
    out_path = OUT_DIR / "stage8_adaptive_and_sector_results.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved complete Stage 8 results to {out_path}")


if __name__ == "__main__":
    main()
