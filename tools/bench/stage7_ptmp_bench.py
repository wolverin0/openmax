#!/usr/bin/env python3
"""Stage 7 Multi-Station PtMP Benchmark Suite (3 Heterogeneous Stations + Power/Attenuation Sweep).

Stations connected to LAP-120 AP (192.168.1.2 / 10.99.0.1, Channel 36 VHT80):
  1. loco5ac : Ubiquiti NanoStation 5AC Loco (10.99.0.2) — OpenWrt 24.10.4, ath10k-ct, 802.11ac VHT80 2x2
  2. sxt     : MikroTik SXT Lite5 (10.99.0.3)            — OpenWrt 24.10.4, ath9k,     802.11n  HT40  2x2 (behind wall/door)
  3. lbm5    : Ubiquiti LiteBeam M5 (10.99.0.4)          — airOS 6.1.4,     ath_hal,   802.11n  HT40  1x1 (behind wall/door)

Traffic generator:
  Omarchy Linux host (192.168.1.171) routed via LAP-120 AP (192.168.1.2 -> phy0-ap0 -> 10.99.0.0/24)
  with stateless nftables `notrack` fastpath on LAP-120 so the AP CPU only performs kernel L3 forwarding.
"""
import argparse
import datetime
import json
import math
import re
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path
import paramiko

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "artifacts" / "stage7_ptmp"
OUT_DIR.mkdir(parents=True, exist_ok=True)

AP_MGMT = "192.168.1.2"
AP_WLINK = "10.99.0.1"
LOCAL_BIND = "192.168.1.155"
OMARCHY_HOST = "192.168.100.159"
OMARCHY_LAN_IP = "192.168.1.171"

STATIONS = {
    "loco5ac": {
        "ip": "10.99.0.2",
        "mac": "fc:ec:da:c2:54:0a",
        "desc": "NanoStation 5AC Loco (ath10k-ct VHT80 2x2)",
    },
    "sxt": {
        "ip": "10.99.0.3",
        "mac": "64:d1:54:1b:96:97",
        "desc": "MikroTik SXT Lite5 (ath9k HT40 2x2, wall/door)",
    },
    "lbm5": {
        "ip": "10.99.0.4",
        "mac": "f0:9f:c2:b2:b6:ba",
        "desc": "Ubiquiti LiteBeam M5 (airOS 6.1.4 HT40 1x1, wall/door)",
    },
}

SSH_BASE = [
    "ssh",
    "-b", LOCAL_BIND,
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "ConnectTimeout=10",
    "-o", "LogLevel=ERROR",
]


def ap_ssh(cmd: str, timeout: int = 30) -> tuple[str, str, int]:
    r = subprocess.run(
        SSH_BASE + [f"root@{AP_MGMT}", cmd],
        capture_output=True,
        text=True,
        timeout=timeout,
        stdin=subprocess.DEVNULL,
    )
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def omarchy_ssh(cmd: str, timeout: int = 60) -> tuple[str, str, int]:
    import os
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    gw_pass = os.environ.get("FMX_GATEWAY_PASS", "")
    c.connect(OMARCHY_HOST, username="ggorbalan", password=gw_pass, timeout=10)
    _, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    rc = stdout.channel.recv_exit_status()
    c.close()
    return out, err, rc


def lbm5_exec(cmd: str, timeout: int = 20) -> str:
    proc = subprocess.Popen(
        SSH_BASE + ["-W", "10.99.0.4:22", f"root@{AP_MGMT}"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    class PipeSock:
        def __init__(self, p):
            self.p = p
            self._closed = False
        def send(self, data):
            self.p.stdin.write(data)
            self.p.stdin.flush()
            return len(data)
        def recv(self, n):
            return self.p.stdout.read1(n) if hasattr(self.p.stdout, "read1") else self.p.stdout.read(n)
        def close(self):
            self._closed = True
            self.p.terminate()
        def settimeout(self, t):
            pass

    c5 = paramiko.SSHClient()
    c5.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c5.connect("10.99.0.4", username="ubnt", password="ubnt", sock=PipeSock(proc), timeout=timeout)
    _, out, _ = c5.exec_command(cmd)
    res = out.read().decode("utf-8", errors="replace").strip()
    c5.close()
    proc.terminate()
    return res


def ensure_lbm5_ready():
    """Ensure LiteBeam M5 (10.99.0.4) has return route to 192.168.1.0/24 and iperf3 daemon running."""
    proc = subprocess.Popen(
        SSH_BASE + ["-W", "10.99.0.4:22", f"root@{AP_MGMT}"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    class PipeSock:
        def __init__(self, p):
            self.p = p
            self._closed = False
        def send(self, data):
            self.p.stdin.write(data)
            self.p.stdin.flush()
            return len(data)
        def recv(self, n):
            return self.p.stdout.read1(n) if hasattr(self.p.stdout, "read1") else self.p.stdout.read(n)
        def close(self):
            self._closed = True
            self.p.terminate()
        def settimeout(self, t):
            pass

    c5 = paramiko.SSHClient()
    c5.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c5.connect("10.99.0.4", username="ubnt", password="ubnt", sock=PipeSock(proc), timeout=15)
    _, out, _ = c5.exec_command("test -x /tmp/iperf3 && echo PRESENT || echo MISSING")
    status = out.read().decode().strip()
    if status != "PRESENT":
        for rpath, dst in [
            ("/lib/libc.so", "/tmp/libc.so"),
            ("/usr/lib/libiperf.so.0.0.0", "/tmp/libiperf.so.0"),
            ("/lib/libatomic.so.1", "/tmp/libatomic.so.1"),
            ("/lib/libgcc_s.so.1", "/tmp/libgcc_s.so.1"),
            ("/usr/bin/iperf3", "/tmp/iperf3"),
        ]:
            r = subprocess.run(SSH_BASE + [f"root@{AP_MGMT}", f"cat {rpath}"], capture_output=True)
            stdin, stdout, _ = c5.exec_command(f"cat > {dst}")
            stdin.write(r.stdout)
            stdin.channel.shutdown_write()
            stdout.read()
    cmd = (
        "chmod +x /tmp/libc.so /tmp/iperf3; "
        "ip route replace 192.168.1.0/24 via 10.99.0.1 dev br0 2>/dev/null; "
        "ps | grep -v grep | grep -q '/tmp/iperf3 -s' || /tmp/libc.so --library-path /tmp /tmp/iperf3 -s -D >/dev/null 2>&1 </dev/null; "
        "echo LBM5_OK"
    )
    _, out, _ = c5.exec_command(cmd)
    res = out.read().decode().strip()
    c5.close()
    proc.terminate()
    return res


def setup_infrastructure():
    """Configure AP fastpath, station return routes, iperf3 daemons, and Omarchy route."""
    import os
    gw_pass = os.environ.get("FMX_GATEWAY_PASS", "")
    ap_script = """
uci set network.wlink.netmask='255.255.255.0'
uci commit network
ip addr del 10.99.0.1/30 dev phy0-ap0 2>/dev/null || true
ip addr add 10.99.0.1/24 dev phy0-ap0 2>/dev/null || true
ip route del 192.168.1.170/32 2>/dev/null || true
ip route del 192.168.1.171/32 2>/dev/null || true
ip route replace 10.99.0.0/24 dev phy0-ap0 src 10.99.0.1
sysctl -w net.ipv4.ip_forward=1 >/dev/null
nft add table inet fmx_fastpath 2>/dev/null || true
nft flush table inet fmx_fastpath 2>/dev/null || true
nft 'add chain inet fmx_fastpath raw_pre { type filter hook prerouting priority -300; policy accept; }'
nft 'add rule inet fmx_fastpath raw_pre ip saddr 192.168.1.0/24 ip daddr 192.168.1.0/24 notrack'
nft 'add rule inet fmx_fastpath raw_pre ip saddr 10.99.0.0/24 ip daddr 10.99.0.0/24 notrack'
nft 'add rule inet fmx_fastpath raw_pre ip saddr 192.168.1.0/24 ip daddr 10.99.0.0/24 notrack'
nft 'add rule inet fmx_fastpath raw_pre ip saddr 10.99.0.0/24 ip daddr 192.168.1.0/24 notrack'
nft 'add chain inet fmx_fastpath in_fast { type filter hook input priority -150; policy accept; }'
nft 'add rule inet fmx_fastpath in_fast accept'
nft 'add chain inet fmx_fastpath fwd_fast { type filter hook forward priority -150; policy accept; }'
nft 'add rule inet fmx_fastpath fwd_fast accept'
for p in 5201 5202 5203; do netstat -ltn 2>/dev/null | grep -q ":$p " || iperf3 -s -D -p $p; done
ssh -y root@10.99.0.2 'ip addr del 10.99.0.2/30 dev phy0-sta0 2>/dev/null; ip addr add 10.99.0.2/24 dev phy0-sta0 2>/dev/null; ip route replace 10.99.0.0/24 dev phy0-sta0 src 10.99.0.2; ip route replace 192.168.1.0/24 via 10.99.0.1 dev phy0-sta0; netstat -ltn 2>/dev/null | grep -q ":5201 " || iperf3 -s -D'
ssh -y root@10.99.0.3 'ip route replace 192.168.1.0/24 via 10.99.0.1 dev phy0-sta0; netstat -ltn 2>/dev/null | grep -q ":5201 " || iperf3 -s -D'
echo AP_AND_OPENWRT_STATIONS_OK
"""
    out, err, _ = ap_ssh(ap_script, timeout=30)
    print("[setup_ap]", out, err)
    lbm5_res = ensure_lbm5_ready()
    print("[setup_lbm5]", lbm5_res)
    om_cmd = (
        f"echo {gw_pass} | sudo -S ip addr del 10.99.0.254/24 dev eno1 2>/dev/null || true; "
        f"echo {gw_pass} | sudo -S ip route replace 10.99.0.0/24 via 192.168.1.2 dev eno1 src 192.168.1.171; "
        "for ip in 10.99.0.1 10.99.0.2 10.99.0.3 10.99.0.4; do ping -c 2 -W 1 $ip | tail -n 2; done"
    )
    om_out, _, _ = omarchy_ssh(om_cmd, timeout=30)
    print("[setup_omarchy]\n", om_out)


def get_ap_station_telemetry() -> dict:
    out, _, _ = ap_ssh("iw dev phy0-ap0 info; iw dev phy0-ap0 station dump")
    info = {"txpower_dbm": None, "stations": {}}
    m_tx = re.search(r"txpower\s+([0-9.]+)\s+dBm", out)
    if m_tx:
        info["txpower_dbm"] = float(m_tx.group(1))
    blocks = re.split(r"(?=Station [0-9a-f:]{17})", out)
    for b in blocks:
        m_mac = re.match(r"Station ([0-9a-f:]{17})", b)
        if not m_mac:
            continue
        mac = m_mac.group(1).lower()
        st_data = {"mac": mac}
        for line in b.splitlines():
            line = line.strip()
            if line.startswith("signal:"):
                st_data["signal_raw"] = line.split(":", 1)[1].strip()
                m_s = re.search(r"(-?\d+)", line)
                if m_s:
                    st_data["signal_dbm"] = int(m_s.group(1))
            elif line.startswith("signal avg:"):
                st_data["signal_avg_raw"] = line.split(":", 1)[1].strip()
                m_sa = re.search(r"(-?\d+)", line)
                if m_sa:
                    st_data["signal_avg_dbm"] = int(m_sa.group(1))
            elif line.startswith("tx bitrate:"):
                st_data["tx_bitrate"] = line.split(":", 1)[1].strip()
            elif line.startswith("rx bitrate:"):
                st_data["rx_bitrate"] = line.split(":", 1)[1].strip()
            elif line.startswith("tx retries:"):
                st_data["tx_retries"] = int(line.split(":", 1)[1].strip())
            elif line.startswith("tx failed:"):
                st_data["tx_failed"] = int(line.split(":", 1)[1].strip())
            elif line.startswith("airtime weight:"):
                st_data["airtime_weight"] = int(line.split(":", 1)[1].strip())
            elif line.startswith("tx duration:"):
                st_data["tx_duration_us"] = int(line.split(":", 1)[1].strip().split()[0])
        for name, meta in STATIONS.items():
            if meta["mac"].lower() == mac:
                info["stations"][name] = st_data
    return info


def jain_fairness(vals: list[float]) -> float:
    vals = [v for v in vals if v is not None and v >= 0]
    if not vals or sum(vals) == 0:
        return 0.0
    n = len(vals)
    return round((sum(vals) ** 2) / (n * sum(v * v for v in vals)), 4)


def run_single_or_multi_cell(
    active_stations: list[str],
    direction: str = "down",
    secs: int = 8,
    udp_mbps: int | None = None,
) -> dict:
    """Run iperf3 from Omarchy (192.168.1.171) to active_stations in parallel + concurrent RTT ping."""
    pre_tel = get_ap_station_telemetry()
    results = {}
    retrans = {}
    rtts = {}

    def iperf_worker(name: str):
        ip = STATIONS[name]["ip"]
        rev = "-R" if direction == "up" else ""
        if udp_mbps:
            cmd = f"iperf3 -c {ip} -t {secs} -u -b {udp_mbps}M {rev} -J"
        else:
            cmd = f"iperf3 -c {ip} -t {secs} -P 2 {rev} -J"
        out, err, rc = omarchy_ssh(cmd, timeout=secs + 25)
        try:
            j = json.loads(out[out.find("{"):])
            if udp_mbps:
                if "sum_received" in j["end"] and j["end"]["sum_received"].get("bits_per_second"):
                    bps = j["end"]["sum_received"]["bits_per_second"]
                else:
                    bps = j["end"]["sum"]["bits_per_second"] * (1.0 - j["end"]["sum"].get("lost_percent", 0.0) / 100.0)
                retrans[name] = 0
            else:
                bps = j["end"]["sum_received"]["bits_per_second"]
                retrans[name] = j["end"].get("sum_sent", {}).get("retransmits", 0)
            results[name] = round(bps / 1e6, 2)
        except Exception:
            results[name] = 0.0
            retrans[name] = -1

    def ping_worker(name: str):
        ip = STATIONS[name]["ip"]
        count = max(int(secs * 4), 6)
        out, _, _ = omarchy_ssh(f"ping -i 0.2 -c {count} -W 1 {ip}", timeout=secs + 15)
        samples = [float(m.group(1)) for m in re.finditer(r"time=([0-9.]+)\s*ms", out)]
        samples.sort()
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
    for name in active_stations:
        threads.append(threading.Thread(target=iperf_worker, args=(name,)))
    for name in STATIONS:
        threads.append(threading.Thread(target=ping_worker, args=(name,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    post_tel = get_ap_station_telemetry()
    deltas = {}
    for name in STATIONS:
        pre_s = pre_tel.get("stations", {}).get(name, {})
        post_s = post_tel.get("stations", {}).get(name, {})
        deltas[name] = {
            "tx_retries_delta": post_s.get("tx_retries", 0) - pre_s.get("tx_retries", 0),
            "tx_failed_delta": post_s.get("tx_failed", 0) - pre_s.get("tx_failed", 0),
            "tx_duration_delta_us": post_s.get("tx_duration_us", 0) - pre_s.get("tx_duration_us", 0),
            "signal_dbm": post_s.get("signal_dbm"),
            "signal_avg_dbm": post_s.get("signal_avg_dbm"),
            "tx_bitrate": post_s.get("tx_bitrate"),
            "rx_bitrate": post_s.get("rx_bitrate"),
            "airtime_weight": post_s.get("airtime_weight"),
        }
    total_airtime_us = sum(max(0, d["tx_duration_delta_us"]) for d in deltas.values())
    for name in STATIONS:
        if total_airtime_us > 0:
            deltas[name]["airtime_share_pct"] = round(
                100.0 * max(0, deltas[name]["tx_duration_delta_us"]) / total_airtime_us, 1
            )
        else:
            deltas[name]["airtime_share_pct"] = 0.0

    goodputs = [results.get(n, 0.0) for n in active_stations]
    return {
        "active_stations": active_stations,
        "direction": direction,
        "secs": secs,
        "udp_mbps": udp_mbps,
        "goodput_mbps": results,
        "tcp_retransmits": retrans,
        "total_goodput_mbps": round(sum(goodputs), 2),
        "jain_fairness": jain_fairness(goodputs),
        "loaded_rtt": rtts,
        "ap_txpower_dbm": post_tel.get("txpower_dbm"),
        "station_deltas": deltas,
    }


def apply_ap_config(
    txpower_dbm: int = 11,
    airtime_flags: int = 3,
    aql_low: int = 2000,
    aql_high: int = 4000,
    aql_thresh: int = 8000,
    amsdu: int = 3,
    ampdu: int = 64,
    weights: dict[str, int] | None = None,
):
    weights = weights or {"loco5ac": 256, "sxt": 256, "lbm5": 256}
    mbm = int(txpower_dbm * 100)
    cmds = [
        f"iw dev phy0-ap0 set txpower fixed {mbm}",
        f"echo {airtime_flags} > /sys/kernel/debug/ieee80211/phy0/airtime_flags",
        f"for ac in 0 1 2 3; do echo \"$ac {aql_low} {aql_high}\" > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit; done",
        f"echo {aql_thresh} > /sys/kernel/debug/ieee80211/phy0/aql_threshold",
        f"echo \"{amsdu} {ampdu}\" > /sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu",
    ]
    for name, w in weights.items():
        mac = STATIONS[name]["mac"]
        cmds.append(f"iw dev phy0-ap0 station set {mac} airtime_weight {w}")
    ap_ssh("; ".join(cmds))
    time.sleep(1.0)


def run_full_stage7_suite():
    setup_infrastructure()
    report = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "topology": {
            "ap": "Ubiquiti LAP-120 (OpenWrt 24.10.4, ath10k-ct, Channel 36 VHT80)",
            "stations": STATIONS,
            "physical_setup": "Loco 5AC in room (~3m); MikroTik SXT Lite5 and Ubiquiti LiteBeam M5 behind wall/door (~6m)",
        },
        "exp7_1_txpower_attenuation_sweep": {},
        "exp7_2_mac_scheduling_and_aggregation": {},
        "exp7_3_uplink_multi_station_contention": {},
    }

    try:
        # =====================================================================
        # EXPERIMENT 7.1: TX Power / Wall-Attenuation Sweep (15 dBm, 11 dBm, 3 dBm)
        # =====================================================================
        print("\n=== RUNNING EXPERIMENT 7.1: TX Power & Wall-Attenuation Sweep ===")
        for txp in [15, 11, 3]:
            print(f"\n--- AP TX Power = {txp} dBm ---")
            apply_ap_config(txpower_dbm=txp, airtime_flags=3, aql_low=2000, aql_high=4000, aql_thresh=8000, amsdu=2, ampdu=32)
            alone_runs = {}
            for st_name in ["loco5ac", "sxt", "lbm5"]:
                r = run_single_or_multi_cell([st_name], direction="down", secs=6)
                alone_runs[st_name] = r
                print(
                    f"  [Alone DL {st_name}] sig={r['station_deltas'][st_name]['signal_dbm']} dBm "
                    f"goodput={r['goodput_mbps'][st_name]} Mbps "
                    f"p50={r['loaded_rtt'][st_name]['p50_ms'] if r['loaded_rtt'][st_name] else None} ms"
                )
            all_trials = []
            for trial in range(2):
                r_all = run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="down", secs=8)
                all_trials.append(r_all)
                print(
                    f"  [All-3 DL Trial {trial+1}] goodput={r_all['goodput_mbps']} "
                    f"total={r_all['total_goodput_mbps']} Mbps jain={r_all['jain_fairness']} "
                    f"airtime_pct={{k: v['airtime_share_pct'] for k, v in r_all['station_deltas'].items()}}"
                )
            report["exp7_1_txpower_attenuation_sweep"][f"txpower_{txp}dbm"] = {
                "txpower_dbm": txp,
                "alone_dl": alone_runs,
                "all3_dl_trials": all_trials,
            }

        # =====================================================================
        # EXPERIMENT 7.2: Multi-Station Scheduling, ATF & Aggregation at Edge SNR (3 dBm)
        # =====================================================================
        print("\n=== RUNNING EXPERIMENT 7.2: Multi-Station ATF, AQL & Aggregation at Low Power (3 dBm) ===")
        treatments_7_2 = [
            {
                "id": "T1_Legacy_Unbounded_NoATF",
                "desc": "Legacy Bloated Queue + ATF Disabled (airtime_flags=0, AQL 24000/48000, Agg 3x64)",
                "cfg": dict(txpower_dbm=3, airtime_flags=0, aql_low=24000, aql_high=24000, aql_thresh=48000, amsdu=3, ampdu=64,
                            weights={"loco5ac": 256, "sxt": 256, "lbm5": 256}),
            },
            {
                "id": "T2_Equal_ATF_MaxAgg",
                "desc": "Equal Airtime Fairness (256:256:256) + Max Aggregation (3x64, AQL 2000/4000)",
                "cfg": dict(txpower_dbm=3, airtime_flags=3, aql_low=2000, aql_high=4000, aql_thresh=8000, amsdu=3, ampdu=64,
                            weights={"loco5ac": 256, "sxt": 256, "lbm5": 256}),
            },
            {
                "id": "T3_FuturaMAX_BoundedAgg_Equal_ATF",
                "desc": "FuturaMAX Bounded Aggregation (1x16, AQL 1500/3000) + Equal ATF (256:256:256)",
                "cfg": dict(txpower_dbm=3, airtime_flags=3, aql_low=1500, aql_high=3000, aql_thresh=6000, amsdu=1, ampdu=16,
                            weights={"loco5ac": 256, "sxt": 256, "lbm5": 256}),
            },
            {
                "id": "T4_FuturaMAX_SLA_Weighted_ATF",
                "desc": "FuturaMAX Capacity-Protecting Weighted ATF (1024 AC : 128 SXT : 128 M5, Agg 2x32, AQL 1500/3000)",
                "cfg": dict(txpower_dbm=3, airtime_flags=3, aql_low=1500, aql_high=3000, aql_thresh=6000, amsdu=2, ampdu=32,
                            weights={"loco5ac": 1024, "sxt": 128, "lbm5": 128}),
            },
        ]
        for tr in treatments_7_2:
            print(f"\n--- Treatment {tr['id']}: {tr['desc']} ---")
            apply_ap_config(**tr["cfg"])
            trials = []
            for t_idx in range(2):
                r = run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="down", secs=8)
                trials.append(r)
                print(
                    f"  [Trial {t_idx+1}] goodput={r['goodput_mbps']} total={r['total_goodput_mbps']} Mbps "
                    f"airtime_pct={{k: v['airtime_share_pct'] for k, v in r['station_deltas'].items()}} "
                    f"sxt_p95={r['loaded_rtt']['sxt']['p95_ms'] if r['loaded_rtt']['sxt'] else None} ms "
                    f"loco_p95={r['loaded_rtt']['loco5ac']['p95_ms'] if r['loaded_rtt']['loco5ac'] else None} ms"
                )
            report["exp7_2_mac_scheduling_and_aggregation"][tr["id"]] = {
                "description": tr["desc"],
                "config": tr["cfg"],
                "trials": trials,
            }

        # =====================================================================
        # EXPERIMENT 7.3: 3-Station Simultaneous Uplink Contention & RTS/CTS Protection
        # =====================================================================
        print("\n=== RUNNING EXPERIMENT 7.3: 3-Station Simultaneous Uplink Contention (RTS/CTS Off vs 256B) ===")
        apply_ap_config(txpower_dbm=11, airtime_flags=3, aql_low=2000, aql_high=4000, aql_thresh=8000, amsdu=2, ampdu=32,
                        weights={"loco5ac": 256, "sxt": 256, "lbm5": 256})
        ul_alone = {}
        for st_name in ["loco5ac", "sxt", "lbm5"]:
            r = run_single_or_multi_cell([st_name], direction="up", secs=6)
            ul_alone[st_name] = r
            print(f"  [Alone UL {st_name}] goodput={r['goodput_mbps'][st_name]} Mbps")

        # RTS OFF on stations
        ap_ssh("ssh -y root@10.99.0.2 'iw phy phy0 set rts off'; ssh -y root@10.99.0.3 'iw phy phy0 set rts off'")
        lbm5_exec("iwconfig ath0 rts off")
        ul_rts_off = []
        for t_idx in range(2):
            r = run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="up", secs=8)
            ul_rts_off.append(r)
            print(f"  [All-3 UL RTS=OFF Trial {t_idx+1}] goodput={r['goodput_mbps']} total={r['total_goodput_mbps']} Mbps jain={r['jain_fairness']}")

        # RTS 256B on stations
        ap_ssh("ssh -y root@10.99.0.2 'iw phy phy0 set rts 256'; ssh -y root@10.99.0.3 'iw phy phy0 set rts 256'")
        lbm5_exec("iwconfig ath0 rts 256")
        ul_rts_256 = []
        for t_idx in range(2):
            r = run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="up", secs=8)
            ul_rts_256.append(r)
            print(f"  [All-3 UL RTS=256B Trial {t_idx+1}] goodput={r['goodput_mbps']} total={r['total_goodput_mbps']} Mbps jain={r['jain_fairness']}")

        # Restore RTS OFF on stations
        ap_ssh("ssh -y root@10.99.0.2 'iw phy phy0 set rts off'; ssh -y root@10.99.0.3 'iw phy phy0 set rts off'")
        lbm5_exec("iwconfig ath0 rts off")

        report["exp7_3_uplink_multi_station_contention"] = {
            "alone_ul": ul_alone,
            "all3_ul_rts_off": ul_rts_off,
            "all3_ul_rts_256": ul_rts_256,
        }

    finally:
        print("\n=== RESTORING SAFE BASELINE ON AP ===")
        apply_ap_config(txpower_dbm=11, airtime_flags=3, aql_low=2000, aql_high=4000, aql_thresh=8000, amsdu=2, ampdu=32,
                        weights={"loco5ac": 256, "sxt": 256, "lbm5": 256})

    out_path = OUT_DIR / "stage7_ptmp_3station_results.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved complete Stage 7 results to {out_path}")


def set_vo_diffserv_bypass(enable: bool):
    if enable:
        ap_cmd = """
nft flush chain inet fmx_fastpath fwd_fast
nft 'add rule inet fmx_fastpath fwd_fast ip protocol icmp ip dscp set ef counter accept'
nft 'add rule inet fmx_fastpath fwd_fast meta l4proto udp th dport { 53, 123, 5060 } ip dscp set ef accept'
nft 'add rule inet fmx_fastpath fwd_fast accept'
"""
    else:
        ap_cmd = """
nft flush chain inet fmx_fastpath fwd_fast
nft 'add rule inet fmx_fastpath fwd_fast accept'
"""
    ap_ssh(ap_cmd)


def run_exp7_4_vo_bypass():
    print("\n=== RUNNING EXPERIMENT 7.4: WMM AC_VO DiffServ Deficit Bypass Under 3-Station Saturation (3 dBm & 11 dBm) ===")
    results_7_4 = {}
    try:
        for txp in [3, 11]:
            results_7_4[f"txpower_{txp}dbm"] = {}
            for mode_name, enable_vo in [("AC_BE_Default", False), ("AC_VO_DiffServ_Bypass", True)]:
                apply_ap_config(
                    txpower_dbm=txp,
                    airtime_flags=3,
                    aql_low=1500,
                    aql_high=3000,
                    aql_thresh=6000,
                    amsdu=1,
                    ampdu=16,
                    weights={"loco5ac": 256, "sxt": 256, "lbm5": 256},
                )
                set_vo_diffserv_bypass(enable_vo)
                trials = []
                for t_idx in range(2):
                    r = run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="down", secs=8)
                    trials.append(r)
                    print(
                        f"  [txp={txp}dBm {mode_name} Trial {t_idx+1}] total={r['total_goodput_mbps']} Mbps "
                        f"goodput={r['goodput_mbps']} "
                        f"sxt_rtt(p50/p95)={r['loaded_rtt']['sxt']['p50_ms'] if r['loaded_rtt']['sxt'] else None}/"
                        f"{r['loaded_rtt']['sxt']['p95_ms'] if r['loaded_rtt']['sxt'] else None} ms "
                        f"lbm5_rtt(p50/p95)={r['loaded_rtt']['lbm5']['p50_ms'] if r['loaded_rtt']['lbm5'] else None}/"
                        f"{r['loaded_rtt']['lbm5']['p95_ms'] if r['loaded_rtt']['lbm5'] else None} ms "
                        f"loco_rtt(p50/p95)={r['loaded_rtt']['loco5ac']['p50_ms'] if r['loaded_rtt']['loco5ac'] else None}/"
                        f"{r['loaded_rtt']['loco5ac']['p95_ms'] if r['loaded_rtt']['loco5ac'] else None} ms"
                    )
                results_7_4[f"txpower_{txp}dbm"][mode_name] = trials
    finally:
        set_vo_diffserv_bypass(False)
        apply_ap_config(txpower_dbm=11, airtime_flags=3, aql_low=2000, aql_high=4000, aql_thresh=8000, amsdu=2, ampdu=32)

    out_path = OUT_DIR / "stage7_ptmp_3station_results.json"
    if out_path.exists():
        data = json.loads(out_path.read_text(encoding="utf-8"))
    else:
        data = {}
    data["exp7_4_wmm_vo_deficit_bypass"] = results_7_4
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Updated {out_path} with exp7_4_wmm_vo_deficit_bypass")


def smoke_test():
    setup_infrastructure()
    for name in ["loco5ac", "sxt", "lbm5"]:
        res = run_single_or_multi_cell([name], direction="down", secs=4)
        print(f"[SMOKE ALONE DL {name}] goodput={res['goodput_mbps']} rtt={res['loaded_rtt'].get(name)}")
    res_all = run_single_or_multi_cell(["loco5ac", "sxt", "lbm5"], direction="down", secs=5)
    print(f"[SMOKE ALL 3 DL] goodput={res_all['goodput_mbps']} total={res_all['total_goodput_mbps']} Mbps jain={res_all['jain_fairness']} rtt={res_all['loaded_rtt']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full", choices=["setup", "smoke", "full", "exp7_4"])
    args = ap.parse_args()
    if args.mode == "setup":
        setup_infrastructure()
    elif args.mode == "smoke":
        smoke_test()
    elif args.mode == "exp7_4":
        run_exp7_4_vo_bypass()
    else:
        run_full_stage7_suite()
