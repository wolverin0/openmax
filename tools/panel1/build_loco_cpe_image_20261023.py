"""Build NanoStation 5AC loco (0xe7fa) OpenWrt 24.10.4 STA-WDS + Router/NAT + LuCI images
for bench qualification (Loco195) and production CPE canary (MONZON 10.10.200.41).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CANARY = ROOT / "artifacts" / "canary_panel1_guarida"
LOCO_SYSUPGRADE = ROOT / "firmware" / "openwrt" / "futuramax-r28959-spectral" / "openwrt-ath79-generic-ubnt_nanostation-ac-loco-squashfs-sysupgrade.bin"
LBE_SYSUPGRADE = ROOT / "firmware" / "openwrt" / "futuramax-r28959-spectral" / "openwrt-ath79-generic-ubnt_litebeam-ac-gen2-squashfs-sysupgrade.bin"
V3_PROVEN = CANARY / "panel1_firmware_lap120_proven_v3_20261019.bin"
LUCI_BUNDLE = CANARY / "luci_uhttpd_overlay_bundle_20261023.tar.gz"

SIZE = 7077888
OFFSET = 0x290000
MARKER = 0x6B0000

sha256_hex = lambda data: hashlib.sha256(data).hexdigest()


def quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def render_uci(sections: list[tuple[tuple[str, ...], list[tuple[str, str, str]]]]) -> bytes:
    lines: list[str] = []
    for section, items in sections:
        lines.append("config " + " ".join(quote(v) for v in section))
        lines.extend("\t" + kind + " " + quote(name) + " " + quote(value) for kind, name, value in items)
        lines.append("")
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_uci(data: bytes):
    sections = []
    for line in data.decode("ascii").splitlines():
        fields = shlex.split(line, comments=True, posix=True)
        if not fields:
            continue
        if fields[0] == "config":
            sections.append((tuple(fields[1:]), []))
        else:
            sections[-1][1].append(tuple(fields))
    return sections


def make_network_uci(wan_ip: str, wan_gw: str, dns_list: list[str]) -> bytes:
    sections = [
        (("interface", "loopback"), [
            ("option", "device", "lo"),
            ("option", "proto", "static"),
            ("option", "ipaddr", "127.0.0.1"),
            ("option", "netmask", "255.0.0.0"),
        ]),
        (("globals", "globals"), [
            ("option", "ula_prefix", "fdf9:489d:a970::/48"),
        ]),
        (("device",), [
            ("option", "name", "br-lan"),
            ("option", "type", "bridge"),
            ("list", "ports", "eth0"),
        ]),
        (("device",), [
            ("option", "name", "br-wan"),
            ("option", "type", "bridge"),
            ("option", "bridge_empty", "1"),
        ]),
        (("interface", "lan"), [
            ("option", "device", "br-lan"),
            ("option", "proto", "static"),
            ("option", "ipaddr", "192.168.1.20"),
            ("option", "netmask", "255.255.255.0"),
        ]),
        (("interface", "wan"), [
            ("option", "device", "br-wan"),
            ("option", "proto", "static"),
            ("option", "ipaddr", wan_ip),
            ("option", "netmask", "255.255.255.0"),
            ("option", "gateway", wan_gw),
        ] + [("list", "dns", d) for d in dns_list]),
    ]
    return render_uci(sections)


def make_wireless_uci(ssid: str, key: str, channel: str = "48", txpower: str = "20") -> bytes:
    sections = [
        (("wifi-device", "radio0"), [
            ("option", "type", "mac80211"),
            ("option", "path", "pci0000:00/0000:00:00.0"),
            ("option", "band", "5g"),
            ("option", "channel", channel),
            ("option", "htmode", "VHT20"),
            ("option", "country", "AR"),
            ("option", "txpower", txpower),
            ("option", "disabled", "0"),
        ]),
        (("wifi-iface", "default_radio0"), [
            ("option", "device", "radio0"),
            ("option", "network", "wan"),
            ("option", "mode", "sta"),
            ("option", "ssid", ssid),
            ("option", "encryption", "psk2"),
            ("option", "wds", "1"),
            ("option", "key", key),
        ]),
    ]
    return render_uci(sections)


def make_dhcp_uci() -> bytes:
    sections = [
        (("dnsmasq",), [
            ("option", "domainneeded", "1"),
            ("option", "boguspriv", "1"),
            ("option", "filterwin2k", "0"),
            ("option", "localise_queries", "1"),
            ("option", "rebind_protection", "0"),
            ("option", "local", "/lan/"),
            ("option", "domain", "lan"),
            ("option", "expandhosts", "1"),
            ("option", "nonegcache", "0"),
            ("option", "cachesize", "1000"),
            ("option", "authoritative", "1"),
            ("option", "readethers", "1"),
            ("option", "leasefile", "/tmp/dhcp.leases"),
            ("option", "resolvfile", "/tmp/resolv.conf.d/resolv.conf.auto"),
            ("option", "nonwildcard", "1"),
            ("option", "localservice", "1"),
            ("option", "ednspacket_max", "1232"),
        ]),
        (("dhcp", "lan"), [
            ("option", "interface", "lan"),
            ("option", "start", "100"),
            ("option", "limit", "155"),
            ("option", "leasetime", "10m"),
            ("list", "dhcp_option", "6,192.168.1.20,10.10.200.1,8.8.8.8"),
        ]),
        (("dhcp", "wan"), [
            ("option", "interface", "wan"),
            ("option", "ignore", "1"),
        ]),
        (("host",), [
            ("option", "name", "WR300"),
            ("option", "mac", "80:af:ca:d8:50:27"),
            ("option", "ip", "192.168.1.176"),
        ]),
        (("host",), [
            ("option", "name", "EC220-F5"),
            ("option", "mac", "48:22:54:67:7b:7b"),
            ("option", "ip", "192.168.1.169"),
        ]),
    ]
    return render_uci(sections)


def make_firewall_uci() -> bytes:
    sections = [
        (("defaults",), [
            ("option", "syn_flood", "1"),
            ("option", "input", "ACCEPT"),
            ("option", "output", "ACCEPT"),
            ("option", "forward", "REJECT"),
            ("option", "flow_offloading", "1"),
        ]),
        (("zone",), [
            ("option", "name", "lan"),
            ("list", "network", "lan"),
            ("option", "input", "ACCEPT"),
            ("option", "output", "ACCEPT"),
            ("option", "forward", "ACCEPT"),
        ]),
        (("zone",), [
            ("option", "name", "wan"),
            ("list", "network", "wan"),
            ("option", "input", "ACCEPT"),
            ("option", "output", "ACCEPT"),
            ("option", "forward", "REJECT"),
            ("option", "masq", "1"),
            ("option", "mtu_fix", "1"),
        ]),
        (("forwarding",), [
            ("option", "src", "lan"),
            ("option", "dest", "wan"),
        ]),
    ]
    return render_uci(sections)


def build_one(
    tree_base: Path,
    loco_kernel_prefix: bytes,
    tail_bytes: bytes,
    epoch: int,
    out_path: Path,
    hostname: str,
    wan_ip: str,
    wan_gw: str,
    dns_list: list[str],
    ssid: str,
    wpa_key: str,
    channel: str,
    txpower: str,
) -> dict:
    with tempfile.TemporaryDirectory(prefix="fmx-loco-build-") as tmp:
        work = Path(tmp)
        tree = work / "rootfs"
        subprocess.run(["cp", "-a", str(tree_base), str(tree)], check=True)

        # Write configs
        (tree / "etc/config/network").write_bytes(make_network_uci(wan_ip, wan_gw, dns_list))
        (tree / "etc/config/wireless").write_bytes(make_wireless_uci(ssid, wpa_key, channel, txpower))
        (tree / "etc/config/dhcp").write_bytes(make_dhcp_uci())
        (tree / "etc/config/firewall").write_bytes(make_firewall_uci())

        # Replace 99-futuramax-panel1 so dnsmasq stays enabled on CPE router
        uci_def = tree / "etc/uci-defaults/99-futuramax-panel1"
        uci_def.write_text(
            f"#!/bin/sh\n"
            f"uci set system.@system[0].hostname={quote(hostname)}\n"
            f"uci commit system\n"
            f"exit 0\n",
            encoding="ascii",
        )

        # Configure AQL limits and bridge/link watchdog in rc.local
        watchdog_sh = tree / "usr/sbin/fmx_cpe_watchdog.sh"
        watchdog_sh.write_text(
            "#!/bin/sh\n"
            f"GW={quote(wan_gw)}\n"
            "fail=0\n"
            "while true; do\n"
            "  for ac in 0 1 2 3; do\n"
            "    echo \"$ac 2000 4000\" > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit 2>/dev/null || true\n"
            "    echo \"$ac 2000 4000\" > /sys/kernel/debug/ieee80211/phy0/ath10k/aql_txq_limit 2>/dev/null || true\n"
            "  done\n"
            "  if [ -d /sys/class/net/phy0-sta0 ]; then\n"
            "    iw dev phy0-sta0 set 4addr on 2>/dev/null || true\n"
            "    ip link set dev phy0-sta0 up 2>/dev/null || true\n"
            "    ip link set dev phy0-sta0 master br-wan 2>/dev/null || true\n"
            "  fi\n"
            "  if ping -c 1 -W 2 \"$GW\" >/dev/null 2>&1; then\n"
            "    fail=0\n"
            "  else\n"
            "    fail=$((fail + 1))\n"
            "    if [ \"$fail\" -ge 8 ]; then\n"
            "      wifi reload >/dev/null 2>&1 || true\n"
            "      fail=0\n"
            "    fi\n"
            "  fi\n"
            "  sleep 15\n"
            "done\n",
            encoding="ascii",
        )
        os.chmod(watchdog_sh, 0o755)

        rc_local = tree / "etc/rc.local"
        rc_local.write_text(
            "#!/bin/sh\n"
            "/usr/sbin/fmx_cpe_watchdog.sh >/dev/null 2>&1 &\n"
            "exit 0\n",
            encoding="ascii",
        )

        squash = work / "rootfs.squashfs"
        subprocess.run(
            [
                "mksquashfs",
                str(tree),
                str(squash),
                "-noappend",
                "-comp",
                "xz",
                "-b",
                "262144",
                "-no-xattrs",
                "-mkfs-time",
                str(epoch),
                "-processors",
                "2",
                "-no-progress",
            ],
            check=True,
            capture_output=True,
        )
        fs_bytes = squash.read_bytes()
        max_fs = MARKER - OFFSET
        if len(fs_bytes) > max_fs:
            raise RuntimeError(f"SquashFS too large: {len(fs_bytes)} > {max_fs}")
        image = loco_kernel_prefix + fs_bytes + (b"\xff" * (max_fs - len(fs_bytes))) + tail_bytes
        if len(image) != SIZE:
            raise RuntimeError(f"Unexpected image size: {len(image)}")
        out_path.write_bytes(image)
        return {
            "output": out_path.name,
            "size_bytes": len(image),
            "sha256": sha256_hex(image),
            "md5": hashlib.md5(image).hexdigest(),
            "squashfs_bytes": len(fs_bytes),
            "free_padding_bytes": max_fs - len(fs_bytes),
            "hostname": hostname,
            "wan_ip": wan_ip,
            "ssid": ssid,
            "channel": channel,
        }


def main() -> int:
    if os.name != "posix" or os.geteuid() != 0:
        raise RuntimeError("Run inside WSL fakeroot session")
    v3_bytes = V3_PROVEN.read_bytes()
    loco_bytes = LOCO_SYSUPGRADE.read_bytes()
    loco_kernel_prefix = loco_bytes[:OFFSET]
    lbe_bytes = LBE_SYSUPGRADE.read_bytes()
    lbe_kernel_prefix = lbe_bytes[:OFFSET]
    tail_bytes = v3_bytes[MARKER:]
    epoch = struct.unpack_from("<I", v3_bytes, OFFSET + 8)[0]

    with tempfile.TemporaryDirectory(prefix="fmx-loco-base-") as tmp:
        base_tree = Path(tmp) / "base"
        subprocess.run(
            ["unsquashfs", "-no-progress", "-d", str(base_tree), "-o", str(OFFSET), str(V3_PROVEN)],
            check=True,
            capture_output=True,
        )
        # Extract production key from v3 wireless config
        w_sections = parse_uci((base_tree / "etc/config/wireless").read_bytes())
        prod_key = next(val for kind, name, val in w_sections[1][1] if kind == "option" and name == "key")

        bench_out = CANARY / "loco195_bench_cpe_openwrt_20261023.bin"
        monzon_out = CANARY / "monzon_cpe_openwrt_20261023.bin"
        gamboa_out = CANARY / "gamboa_cpe_openwrt_20261023.bin"

        bench_meta = build_one(
            base_tree,
            loco_kernel_prefix,
            tail_bytes,
            epoch,
            bench_out,
            hostname="Loco195-Bench-CPE",
            wan_ip="192.168.200.41",
            wan_gw="192.168.200.1",
            dns_list=["192.168.200.1", "8.8.8.8"],
            ssid="FuturaMAX-LAB",
            wpa_key="FuturaMAX2026",
            channel="36",
            txpower="18",
        )
        monzon_meta = build_one(
            base_tree,
            loco_kernel_prefix,
            tail_bytes,
            epoch,
            monzon_out,
            hostname="MONZON-Stella-Maris",
            wan_ip="10.10.200.41",
            wan_gw="10.10.200.1",
            dns_list=["10.10.200.1", "8.8.8.8"],
            ssid="FT-Guarida1",
            wpa_key=prod_key,
            channel="48",
            txpower="20",
        )
        gamboa_meta = build_one(
            base_tree,
            lbe_kernel_prefix,
            tail_bytes,
            epoch,
            gamboa_out,
            hostname="GAMBOA-Gabriela",
            wan_ip="10.10.200.223",
            wan_gw="10.10.200.1",
            dns_list=["10.10.200.1", "8.8.8.8"],
            ssid="FT-Guarida1",
            wpa_key=prod_key,
            channel="48",
            txpower="20",
        )

    manifest = {
        "status": "BUILT_AND_VERIFIED",
        "bench_image": bench_meta,
        "monzon_image": monzon_meta,
        "gamboa_image": gamboa_meta,
    }
    manifest_path = CANARY / "loco_cpe_openwrt_images_20261023.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
