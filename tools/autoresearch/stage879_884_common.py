# PUBLIC_REDACTED_DERIVATIVE; original_sha256=3f38b62d8a2e8aa57a7dc3073a6651c13bc7d68bcc5d9fafadbaf18cc086406e
# Private originals are required for native replay.
"""Allowlisted read-only telemetry for879..884; JSON utilities reuse frozen861 code."""
from __future__ import annotations
import base64
import hashlib
import socket
import time
import paramiko
from tools.autoresearch import stage861_866_common as c
ROOT = c.ROOT
HOSTS = frozenset(('198.18.0.45', '198.18.0.46', '198.18.0.48', '198.18.0.43', '198.18.0.47', '198.18.0.3', '198.18.0.4', '198.18.0.5', '198.18.0.6', '198.18.0.7'))
TOPOLOGY = dict(rocket2ac='198.18.0.48', mk1='198.18.0.41', powerbeam_ap='198.18.0.45', powerbeam_sta='198.18.0.46', wa_ap='198.18.0.43', wa_sta='198.18.0.47')
PROBE = 'probe() { printf \'\\n===%s===\\n\' "$1"; label=$1; shift; "$@"; rc=$?; printf \'\\nEXIT_%s=%s\\n\' "$label" "$rc"; }\n'
BENCH = PROBE + 'probe BOARD ubus call system board\nprobe BOOT cat /proc/sys/kernel/random/boot_id\nprobe UPTIME cat /proc/uptime\nprobe IW iw dev\nfor p in /sys/kernel/debug/ieee80211/phy*/ath10k; do [ -d "$p" ] || continue; echo "DYNAMIC_PATH=$p"; probe FW_CHECKSUMS cat "$p/fw_checksums"; probe PKTLOG cat "$p/pktlog_filter"; done\nfor f in /lib/firmware/ath10k/QCA988X/hw2.0/firmware-*.bin; do [ -f "$f" ] && probe FIRMWARE sha256sum "$f"; done\nprobe ADDRESS ip -4 address show\nprobe ROUTE ip -4 route show\nfor n in /sys/class/net/phy*; do [ -d "$n" ] || continue; i=${n##*/}; probe "LINK_$i" iw dev "$i" link; probe "STATIONS_$i" iw dev "$i" station dump; done\nfor s in dnsmasq odhcpd; do probe "PID_$s" pidof "$s"; done\n'
OPENWRT = PROBE + 'probe BOARD ubus call system board\nprobe BOOT cat /proc/sys/kernel/random/boot_id\nprobe UPTIME cat /proc/uptime\nprobe IW iw dev\nprobe ROUTE ip -4 route show\nfor n in /sys/class/net/phy*; do [ -d "$n" ] || continue; i=${n##*/}; probe "STATIONS_$i" iw dev "$i" station dump; probe "LINK_$i" iw dev "$i" link; done\n'
AIROS = PROBE + "probe BOARD sed -n '/^board.name=/p;/^board.sysid=/p' /etc/board.info\nprobe VERSION cat /etc/version\nprobe BOOT cat /proc/sys/kernel/random/boot_id\nprobe UPTIME cat /proc/uptime\nprobe STATUS mca-status\nprobe STATIONS wstalist\n"
COMMANDS = dict(bench=BENCH, openwrt=OPENWRT, airos=AIROS)

def capture(host, kind, username='root', password=''):
    raise RuntimeError('PUBLIC_TRANSPORT_OR_CREDENTIAL_DISABLED: capture')

def save(stage, rows):
    path = c.evidence_path(stage)
    c.write(path, dict(stage=stage.upper(), results=rows, target_writes=False, captured_utc=c.utc(), topology=TOPOLOGY))
    return c.pin(path)
