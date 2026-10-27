# PUBLIC_REDACTED_DERIVATIVE; original_sha256=e2fbc70cc6c4983158fe93d2e3c66f2bb41f4a4f9697fd6a815b5cd874e2c54e
# Private originals are required for native replay.
"""Bounded SSH acquisition for the five explicitly authorized897..900 bench nodes."""
from __future__ import annotations
import base64
import hashlib
from pathlib import Path
import socket
import time
import paramiko
from tools.autoresearch import stage861_866_common as c
ROOT = c.ROOT
HOSTS = frozenset(('198.18.0.43', '198.18.0.42', '198.18.0.47', '198.18.0.45', '198.18.0.46', '198.18.0.48'))
PROBE = 'probe() { printf \'\\n===%s===\\n\' "$1"; label=$1; shift; "$@"; rc=$?; printf \'\\nEXIT_%s=%s\\n\' "$label" "$rc"; }\n'
OPENWRT_PREFLIGHT = PROBE + 'probe BOARD ubus call system board\nprobe BOOT cat /proc/sys/kernel/random/boot_id\nprobe UPTIME cat /proc/uptime\nprobe IW iw dev\nprobe ADDRESS ip -4 address show\nprobe ROUTE ip -4 route show\nprobe FDB bridge fdb show\nprobe TC_REQUESTED_ATH0 tc -s qdisc show dev ath0\nfor d in /sys/class/net/*; do n=${d##*/}; case "$n" in eth*|phy*|br-lan|ath*) probe "QDISC_$n" tc -s -d qdisc show dev "$n"; probe "DRIVER_$n" ethtool -i "$n"; probe "IFINDEX_$n" cat "$d/ifindex"; probe "PHY_$n" readlink -f "$d/phy80211"; probe "MAP_$n" readlink -f "$d/device/driver";; esac; done\nfor p in /sys/kernel/debug/ieee80211/phy*; do [ -d "$p/ath10k" ] || continue; echo "PHY_DEBUG=$p"; for f in aql_txq_limit aqm; do [ -f "$p/$f" ] && probe "$f" cat "$p/$f"; done; probe PKTLOG cat "$p/ath10k/pktlog_filter"; done\nfor k in net.core.netdev_tstamp_prequeue net.ipv4.tcp_autocorking net.ipv4.tcp_recovery; do probe "$k" sysctl -n "$k"; done\nfor f in /sys/class/net/eth*/queues/tx-0/byte_queue_limits/limit_max; do [ -f "$f" ] && probe BQL cat "$f"; done\nprobe TOOLS sh -c \'for x in tc ethtool jsonfilter iperf3 iperf tcpdump ping arping timeout sha256sum curl uclient-fetch uhttpd; do command -v "$x"; done\'\n'
AIROS_PREFLIGHT = PROBE + 'probe BOARD sed -n \'/^board.name=/p;/^board.sysid=/p\' /etc/board.info\nprobe VERSION cat /etc/version\nprobe BOOT cat /proc/sys/kernel/random/boot_id\nprobe UPTIME cat /proc/uptime\nprobe STATUS mca-status\nprobe STATIONS wstalist\nprobe ADDRESS ip -4 address show\nprobe ROUTE ip -4 route show\nprobe QDISC tc -s qdisc show dev ath0\nprobe TOOLS sh -c \'for x in iperf3 iperf tcpdump ping arping timeout curl wget; do command -v "$x"; done\'\n'

def connect(host, password='', username='root', allow_empty=False):
    raise RuntimeError('PUBLIC_TRANSPORT_OR_CREDENTIAL_DISABLED: connect')

def run(host, command, *, password='', username='root', allow_empty=False, timeout=25, input_bytes=None):
    raise RuntimeError('PUBLIC_TRANSPORT_OR_CREDENTIAL_DISABLED: run')

def save(stage, phase, results, **extra):
    path = c.evidence_path(stage)
    c.write(path, dict(stage=stage.upper(), phase=phase, results=results, captured_utc=c.utc(), **extra))
    return c.pin(path)
