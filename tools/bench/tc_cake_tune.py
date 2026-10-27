#!/usr/bin/env python3
"""Linux Traffic Control (tc) CAKE / FQ Tuning and Inspection Tool.

Automates configuration of CAKE / FQ-CoDel / FQ pacing on network interfaces
connected to the Ubiquiti airMAX AC hardware (e.g. CPE or AP facing interfaces).
Parses `tc -s qdisc show dev <iface>` output into structured telemetry
(drops, backlogs, memory, and latency statistics).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CakeTinStats:
    """Telemetry for an individual CAKE DiffServ tin."""
    tin_id: int
    name: str
    thresh_kbps: Optional[int] = None
    target_ms: Optional[float] = None
    interval_ms: Optional[float] = None
    pk_delay_ms: Optional[float] = None
    av_delay_ms: Optional[float] = None
    sp_delay_ms: Optional[float] = None
    backlog_bytes: int = 0
    backlog_pkts: int = 0
    pkts: int = 0
    bytes: int = 0
    drops: int = 0
    marks: int = 0
    ack_drops: int = 0


@dataclass
class TcQdiscStats:
    """Structured telemetry from `tc -s qdisc show`."""
    qdisc_type: str
    handle: str
    iface: str
    params: Dict[str, Any] = field(default_factory=dict)
    bytes_sent: int = 0
    packets_sent: int = 0
    dropped: int = 0
    overlimits: int = 0
    requeues: int = 0
    backlog_bytes: int = 0
    backlog_packets: int = 0
    memory_used_bytes: Optional[int] = None
    memory_limit_bytes: Optional[int] = None
    capacity_estimate_bps: Optional[int] = None
    tin_stats: List[CakeTinStats] = field(default_factory=list)
    peak_delay_ms: Optional[float] = None
    avg_delay_ms: Optional[float] = None
    raw_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _parse_time_unit_to_ms(val_str: str) -> Optional[float]:
    """Converts tc duration strings like '1.2ms', '450us', '0us' to milliseconds."""
    m = re.match(r"^([0-9\.]+)\s*(us|ms|s)$", val_str.strip())
    if not m:
        return None
    val, unit = float(m.group(1)), m.group(2)
    if unit == "us":
        return round(val / 1000.0, 4)
    elif unit == "ms":
        return round(val, 4)
    elif unit == "s":
        return round(val * 1000.0, 4)
    return None


def _parse_size_to_bytes(size_str: str) -> Optional[int]:
    """Converts tc size strings like '1514b', '4Mb', '128Kb' to bytes."""
    m = re.match(r"^([0-9\.]+)\s*([bBkKmMgGtT]b?)?$", size_str.strip())
    if not m:
        return None
    val = float(m.group(1))
    unit = (m.group(2) or "b").lower()
    if unit in ("b", ""):
        return int(val)
    elif unit in ("kb", "k"):
        return int(val * 1024)
    elif unit in ("mb", "m"):
        return int(val * 1024 * 1024)
    elif unit in ("gb", "g"):
        return int(val * 1024 * 1024 * 1024)
    return int(val)


def _parse_bandwidth_to_bps(bw_str: str) -> Optional[int]:
    """Converts tc rate strings like '50Mbit', '3125Kbit' to bits per second."""
    m = re.match(r"^([0-9\.]+)\s*([kKmMgG]?)bit$", bw_str.strip(), re.IGNORECASE)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "k":
        return int(val * 1_000)
    elif unit == "m":
        return int(val * 1_000_000)
    elif unit == "g":
        return int(val * 1_000_000_000)
    return int(val)


def build_cake_cmd(
    iface: str,
    bandwidth: str,
    diffserv: str = "diffserv4",
    ack_filter: bool = True,
    rtt: Optional[str] = None,
    memlimit: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
) -> List[str]:
    """Builds `tc qdisc replace dev <iface> root cake ...` command."""
    cmd = ["tc", "qdisc", "replace", "dev", iface, "root", "cake", "bandwidth", bandwidth]
    if diffserv:
        cmd.append(diffserv)
    if ack_filter:
        cmd.append("ack-filter")
    if rtt:
        cmd.extend(["rtt", rtt])
    if memlimit:
        cmd.extend(["memlimit", memlimit])
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def build_fq_cmd(
    iface: str,
    pacing: bool = True,
    limit: Optional[int] = None,
    flow_limit: Optional[int] = None,
    extra_args: Optional[List[str]] = None,
) -> List[str]:
    """Builds `tc qdisc replace dev <iface> root fq ...` command."""
    cmd = ["tc", "qdisc", "replace", "dev", iface, "root", "fq"]
    if pacing:
        cmd.append("pacing")
    if limit is not None:
        cmd.extend(["limit", str(limit)])
    if flow_limit is not None:
        cmd.extend(["flow_limit", str(flow_limit)])
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def build_fq_codel_cmd(
    iface: str,
    limit: Optional[int] = None,
    target: Optional[str] = None,
    interval: Optional[str] = None,
    ecn: bool = True,
    extra_args: Optional[List[str]] = None,
) -> List[str]:
    """Builds `tc qdisc replace dev <iface> root fq_codel ...` command."""
    cmd = ["tc", "qdisc", "replace", "dev", iface, "root", "fq_codel"]
    if limit is not None:
        cmd.extend(["limit", str(limit)])
    if target:
        cmd.extend(["target", target])
    if interval:
        cmd.extend(["interval", interval])
    if not ecn:
        cmd.append("noecn")
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def build_del_cmd(iface: str) -> List[str]:
    """Builds `tc qdisc del dev <iface> root` command."""
    return ["tc", "qdisc", "del", "dev", iface, "root"]


def build_show_cmd(iface: str) -> List[str]:
    """Builds `tc -s qdisc show dev <iface>` command."""
    return ["tc", "-s", "qdisc", "show", "dev", iface]


def parse_tc_qdisc_output(output: str) -> List[TcQdiscStats]:
    """Parses `tc -s qdisc show dev <iface>` output into TcQdiscStats objects."""
    results: List[TcQdiscStats] = []
    blocks = re.split(r"(?=^qdisc\s+)", output, flags=re.MULTILINE)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.splitlines()
        header = lines[0].strip()

        # Match qdisc <type> <handle> dev <iface> root ...
        m_head = re.match(r"^qdisc\s+(\w+)\s+([0-9a-fA-F:]+)\s+dev\s+([^\s]+)", header)
        if not m_head:
            continue

        q_type, handle, iface = m_head.group(1), m_head.group(2), m_head.group(3)
        stats = TcQdiscStats(qdisc_type=q_type, handle=handle, iface=iface, raw_text=block)

        # Parse parameters from header
        if "bandwidth" in header:
            m_bw = re.search(r"bandwidth\s+([^\s]+)", header)
            if m_bw:
                stats.params["bandwidth"] = m_bw.group(1)
        if "diffserv" in header:
            m_diff = re.search(r"(diffserv\d+|besteffort)", header)
            if m_diff:
                stats.params["diffserv"] = m_diff.group(1)
        if "ack-filter" in header:
            stats.params["ack_filter"] = True
        if "pacing" in header:
            stats.params["pacing"] = True

        # Parse Sent line
        m_sent = re.search(
            r"Sent\s+(\d+)\s+bytes\s+(\d+)\s+pkt\s+\(dropped\s+(\d+),\s*overlimits\s+(\d+)\s+requeues\s+(\d+)\)",
            block,
        )
        if m_sent:
            stats.bytes_sent = int(m_sent.group(1))
            stats.packets_sent = int(m_sent.group(2))
            stats.dropped = int(m_sent.group(3))
            stats.overlimits = int(m_sent.group(4))
            stats.requeues = int(m_sent.group(5))

        # Parse backlog line
        m_backlog = re.search(r"backlog\s+(\d+)[bB]\s+(\d+)[pP]", block)
        if m_backlog:
            stats.backlog_bytes = int(m_backlog.group(1))
            stats.backlog_packets = int(m_backlog.group(2))

        # Parse memory used/limit
        m_mem = re.search(r"memory used:\s+([0-9\.]+[a-zA-Z]*)\s+of\s+([0-9\.]+[a-zA-Z]*)", block)
        if m_mem:
            stats.memory_used_bytes = _parse_size_to_bytes(m_mem.group(1))
            stats.memory_limit_bytes = _parse_size_to_bytes(m_mem.group(2))

        # Parse capacity estimate
        m_cap = re.search(r"capacity estimate:\s+([^\s]+)", block)
        if m_cap:
            stats.capacity_estimate_bps = _parse_bandwidth_to_bps(m_cap.group(1))

        # Parse CAKE per-tin stats
        tin_blocks = re.split(r"(?=Tin\s+\d+:)", block)
        peak_delays: List[float] = []
        avg_delays: List[float] = []

        for tb in tin_blocks[1:]:
            m_tid = re.search(r"Tin\s+(\d+):\s*([^\n\r]+)", tb)
            if not m_tid:
                continue
            tid = int(m_tid.group(1))
            tname = m_tid.group(2).strip()

            tin = CakeTinStats(tin_id=tid, name=tname)

            m_thresh = re.search(r"thresh\s+([^\s]+)", tb)
            if m_thresh:
                bps = _parse_bandwidth_to_bps(m_thresh.group(1))
                if bps:
                    tin.thresh_kbps = bps // 1000

            m_tgt = re.search(r"target\s+([0-9\.]+[a-zA-Z]+)\s+interval\s+([0-9\.]+[a-zA-Z]+)", tb)
            if m_tgt:
                tin.target_ms = _parse_time_unit_to_ms(m_tgt.group(1))
                tin.interval_ms = _parse_time_unit_to_ms(m_tgt.group(2))

            m_del = re.search(r"pk_delay\s+([0-9\.]+[a-zA-Z]+)\s+av_delay\s+([0-9\.]+[a-zA-Z]+)", tb)
            if m_del:
                pk_ms = _parse_time_unit_to_ms(m_del.group(1))
                av_ms = _parse_time_unit_to_ms(m_del.group(2))
                tin.pk_delay_ms = pk_ms
                tin.av_delay_ms = av_ms
                if pk_ms is not None:
                    peak_delays.append(pk_ms)
                if av_ms is not None:
                    avg_delays.append(av_ms)

            m_sp = re.search(r"sp_delay\s+([0-9\.]+[a-zA-Z]+)", tb)
            if m_sp:
                tin.sp_delay_ms = _parse_time_unit_to_ms(m_sp.group(1))

            m_tback = re.search(r"backlog\s+(\d+)[bB]\s+(\d+)[pP]", tb)
            if m_tback:
                tin.backlog_bytes = int(m_tback.group(1))
                tin.backlog_pkts = int(m_tback.group(2))

            m_tpkts = re.search(r"pkts\s+(\d+)\s+bytes\s+(\d+)", tb)
            if m_tpkts:
                tin.pkts = int(m_tpkts.group(1))
                tin.bytes = int(m_tpkts.group(2))

            m_tdrops = re.search(r"drops\s+(\d+)\s+marks\s+(\d+)", tb)
            if m_tdrops:
                tin.drops = int(m_tdrops.group(1))
                tin.marks = int(m_tdrops.group(2))

            m_tack = re.search(r"ack_drop\s+(\d+)", tb)
            if m_tack:
                tin.ack_drops = int(m_tack.group(1))

            stats.tin_stats.append(tin)

        if peak_delays:
            stats.peak_delay_ms = max(peak_delays)
        if avg_delays:
            stats.avg_delay_ms = round(sum(avg_delays) / len(avg_delays), 4)

        results.append(stats)

    return results


def apply_tc_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Executes a tc command on the local host with root privileges if required."""
    is_linux = sys.platform.startswith("linux")
    exec_cmd = list(cmd)
    if is_linux and os.geteuid() != 0:
        exec_cmd.insert(0, "sudo")

    return subprocess.run(
        exec_cmd,
        capture_output=True,
        text=True,
        check=check,
    )


def inspect_qdisc(iface: str) -> List[TcQdiscStats]:
    """Inspects and parses `tc -s qdisc show dev <iface>`."""
    cmd = build_show_cmd(iface)
    res = apply_tc_command(cmd, check=False)
    if res.returncode != 0:
        return []
    return parse_tc_qdisc_output(res.stdout)


def tune_cake(
    iface: str,
    bandwidth: str,
    diffserv: str = "diffserv4",
    ack_filter: bool = True,
) -> Optional[TcQdiscStats]:
    """Applies CAKE qdisc and returns parsed stats."""
    cmd = build_cake_cmd(iface, bandwidth, diffserv=diffserv, ack_filter=ack_filter)
    apply_tc_command(cmd, check=True)
    stats_list = inspect_qdisc(iface)
    for s in stats_list:
        if s.qdisc_type == "cake" and s.iface == iface:
            return s
    return stats_list[0] if stats_list else None


def tune_fq(iface: str, pacing: bool = True) -> Optional[TcQdiscStats]:
    """Applies FQ pacing qdisc and returns parsed stats."""
    cmd = build_fq_cmd(iface, pacing=pacing)
    apply_tc_command(cmd, check=True)
    stats_list = inspect_qdisc(iface)
    for s in stats_list:
        if s.qdisc_type == "fq" and s.iface == iface:
            return s
    return stats_list[0] if stats_list else None


def reset_qdisc(iface: str) -> None:
    """Deletes existing root qdisc on interface."""
    cmd = build_del_cmd(iface)
    apply_tc_command(cmd, check=False)


def main():
    parser = argparse.ArgumentParser(description="FuturaMAX Linux tc CAKE & FQ Tuning Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: cake
    p_cake = subparsers.add_parser("cake", help="Configure CAKE qdisc")
    p_cake.add_argument("--iface", required=True, help="Network interface (e.g. eth0, enp3s0)")
    p_cake.add_argument("--bw", required=True, help="Bandwidth limit (e.g. 50Mbit, 100Mbit)")
    p_cake.add_argument("--diffserv", default="diffserv4", help="DiffServ mode (default: diffserv4)")
    p_cake.add_argument("--no-ack-filter", action="store_true", help="Disable ACK filtering")

    # Subcommand: fq
    p_fq = subparsers.add_parser("fq", help="Configure FQ pacing qdisc")
    p_fq.add_argument("--iface", required=True, help="Network interface (e.g. eth0)")
    p_fq.add_argument("--no-pacing", action="store_true", help="Disable pacing")

    # Subcommand: show
    p_show = subparsers.add_parser("show", help="Inspect qdisc statistics")
    p_show.add_argument("--iface", required=True, help="Network interface")
    p_show.add_argument("--json", action="store_true", help="Output results in JSON format")

    # Subcommand: reset
    p_reset = subparsers.add_parser("reset", help="Reset root qdisc to default")
    p_reset.add_argument("--iface", required=True, help="Network interface")

    args = parser.parse_args()

    if args.command == "cake":
        print(f"[*] Applying CAKE on {args.iface}: bandwidth={args.bw}, diffserv={args.diffserv}, ack-filter={not args.no_ack_filter}...")
        st = tune_cake(args.iface, args.bw, diffserv=args.diffserv, ack_filter=not args.no_ack_filter)
        print(f"[+] CAKE configured! Dropped: {st.dropped if st else 0}, Backlog: {st.backlog_bytes if st else 0} bytes")

    elif args.command == "fq":
        print(f"[*] Applying FQ on {args.iface}: pacing={not args.no_pacing}...")
        st = tune_fq(args.iface, pacing=not args.no_pacing)
        print(f"[+] FQ configured! Dropped: {st.dropped if st else 0}")

    elif args.command == "show":
        stats_list = inspect_qdisc(args.iface)
        if args.json:
            print(json.dumps([s.to_dict() for s in stats_list], indent=2))
        else:
            for s in stats_list:
                print(f"Interface: {s.iface} | Qdisc: {s.qdisc_type} ({s.handle})")
                print(f"  Sent: {s.bytes_sent} B / {s.packets_sent} pkts | Dropped: {s.dropped} | Overlimits: {s.overlimits}")
                print(f"  Backlog: {s.backlog_bytes} B / {s.backlog_packets} pkts")
                if s.peak_delay_ms is not None:
                    print(f"  Peak Delay: {s.peak_delay_ms} ms | Avg Delay: {s.avg_delay_ms} ms")
                for tin in s.tin_stats:
                    print(f"    Tin {tin.tin_id} ({tin.name}): {tin.bytes} B, drops={tin.drops}, ack_drops={tin.ack_drops}, pk_delay={tin.pk_delay_ms} ms")

    elif args.command == "reset":
        print(f"[*] Resetting qdisc on {args.iface}...")
        reset_qdisc(args.iface)
        print("[+] Qdisc reset successfully.")


if __name__ == "__main__":
    main()
