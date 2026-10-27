#!/usr/bin/env python3
"""Four-technology cell runner: LAP-120 AP (ath10k-ct) with three stations of different stacks.

Summary: measures each station ALONE and then ALL THREE LOADED at once against the LAP-120 AP:
loco 5AC (ath10k-ct, VHT80), SXT Lite5 (ath9k OpenWrt, HT40) and LiteBeam M5 (airOS 6 proprietary
driver, HT40, bridge mode — traffic comes from this PC through it via the 10.99.0.155 alias and the
Windows iperf3.exe). Per cell: TCP goodput per station + loaded RTT on the loco. A/B blocks:
alone / all / alone / all. Keywords: C6 contention, mixed stack, airOS, ath9k, ath10k, four-tech.
Read when: running the mixed-vendor cell. Usage: python tools/bench/fourtech.py [--secs 12] [--rounds 2] [--dir down|up]
Logs kind=fourtech rows into research/raw/bench/<date>/bench.jsonl (shared with bench.py).
"""
import argparse, json, re, statistics, subprocess, sys, threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench as B

STA = {
    "loco5ac": {"kind": "ssh", "host": B.CPE, "port": 5201},
    "sxt":     {"kind": "ssh", "host": {"name": "fmx-sta-n1", "mgmt": "192.168.1.4", "wlink": "10.99.0.3"}, "port": 5202},
    "lbm5":    {"kind": "pc",  "bind": "10.99.0.155", "port": 5203,
                "exe": r"C:\Users\pauol\AppData\Local\Microsoft\WinGet\Packages\ar51an.iPerf3_Microsoft.Winget.Source_8wekyb3d8bbwe\iperf3.exe"},
}


def servers():
    B.ssh(B.AP, "for p in 5201 5202 5203; do netstat -ltn 2>/dev/null | grep -q \":$p \" || iperf3 -s -D -p $p; done")


def parse(out):
    try:
        j = json.loads(out[out.find("{"):])
        return round(j["end"]["sum_received"]["bits_per_second"] / 1e6, 1)
    except Exception:
        return None


def run_sta(name, direction, secs, res):
    s = STA[name]
    flags = f"-c {B.AP['wlink']} -p {s['port']} -t {secs} -i 0 -J -P 1" + (" -R" if direction == "down" else "")
    if s["kind"] == "ssh":
        out, err, rc = B.ssh(s["host"], f"iperf3 {flags}", timeout=secs + 60)
    else:
        r = subprocess.run([s["exe"], "-B", s["bind"]] + flags.split(), capture_output=True, text=True, timeout=secs + 60)
        out = r.stdout
    res[name] = parse(out)


def rtt_loco(secs, res):
    out, _, _ = B.ssh(B.CPE, f"ping -c {max(secs - 2, 3)} -i 1 -W 1 {B.AP['wlink']} | grep -E 'time=' | sed 's/.*time=//; s/ ms//'", timeout=secs + 30)
    r = sorted(float(x) for x in out.split() if re.fullmatch(r"[0-9.]+", x))
    res["rtt"] = {"n": len(r), "p50": statistics.median(r), "p95": r[int(0.95 * (len(r) - 1))], "max": r[-1]} if r else None


def cell(names, direction, secs):
    res = {}
    th = [threading.Thread(target=run_sta, args=(n, direction, secs, res)) for n in names]
    th.append(threading.Thread(target=rtt_loco, args=(secs, res)))
    for t in th: t.start()
    for t in th: t.join()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--secs", type=int, default=12); ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--dir", default="down", choices=["down", "up"])
    a = ap.parse_args()
    servers()
    for rnd in range(a.rounds):
        for label, names in (("alone", None), ("all", ["loco5ac", "sxt", "lbm5"])):
            if names is None:
                for n in STA:
                    r = cell([n], a.dir, a.secs)
                    print(B.log({"kind": "fourtech", "block": "alone", "round": rnd, "dir": a.dir, "secs": a.secs, "sta": n, **r}))
            else:
                r = cell(names, a.dir, a.secs)
                print(B.log({"kind": "fourtech", "block": "all", "round": rnd, "dir": a.dir, "secs": a.secs, **r}))


if __name__ == "__main__":
    main()
