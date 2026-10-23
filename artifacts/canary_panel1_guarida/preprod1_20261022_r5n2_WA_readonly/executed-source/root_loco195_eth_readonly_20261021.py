"""Pinned, read-only Ethernet observation; no imported peer-script execution."""
import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parent
CREDENTIAL_REFERENCE = Path(r"C:\Users\pauol\.gemini\antigravity-cli\brain\b4ba8682-71fb-47ac-b696-032051582544\scratch\readonly_loco195_probe_20261021.py")
PIN = "a2fe45b5fcdbcffd1399c668912c2e7ec241e6fd03e62a0a11f12a018a7d3269"
TARGETS = ("192.168.100.195", "fe80::feec:daff:fec2:540a%27")
IDENTITY = "grep -E '^board\\.(name|sysid|hwaddr)=' /etc/board.info; cat /etc/version"
QUERIES = {
    "uptime": "cat /proc/uptime",
    "eth0_carrier": "cat /sys/class/net/eth0/carrier",
    "eth0_operstate": "cat /sys/class/net/eth0/operstate",
    "eth0_mac": "cat /sys/class/net/eth0/address",
    "bridge_mac": "cat /sys/class/net/br0/address",
    "eth0_interface": "ifconfig eth0",
    "bridge_ports": "brctl show",
    "bridge_macs": "brctl showmacs br0",
    "arp_neighbors": "cat /proc/net/arp",
    "ipv4_routes": "route -n",
}


class PinnedKey(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        if hashlib.sha256(key.asbytes()).hexdigest() != PIN:
            raise paramiko.SSHException("HOST_KEY_MISMATCH")


def credentials():
    # Read only literal auth fields from the existing same-bench credential reference.
    # Never execute/import it, copy the secret to disk, or print its contents.
    tree = ast.parse(CREDENTIAL_REFERENCE.read_text(encoding="utf-8-sig"))
    for call in ast.walk(tree):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "connect":
            fields = {kw.arg: kw.value for kw in call.keywords}
            if all(isinstance(fields.get(k), ast.Constant) and isinstance(fields[k].value, str) for k in ("username", "password")):
                return fields["username"].value, fields["password"].value
    raise RuntimeError("No literal bench SSH credential reference found; no connection attempted")


def command(client, cmd):
    _, stdout, stderr = client.exec_command(cmd, timeout=8)
    return {"stdout": stdout.read(16384).decode(errors="replace"), "stderr": stderr.read(4096).decode(errors="replace"), "exit_code": stdout.channel.recv_exit_status()}


def main():
    username, password = credentials()
    report = {"observed_utc": datetime.now(timezone.utc).isoformat(), "mode": "READ_ONLY", "device_writes": False, "attempts": []}
    for target in TARGETS:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(PinnedKey())
        attempt = {"target": target}
        report["attempts"].append(attempt)
        try:
            client.connect(target, username=username, password=password, allow_agent=False, look_for_keys=False, timeout=6, auth_timeout=6, banner_timeout=6)
            identity = command(client, IDENTITY)
            attempt["identity"] = identity
            observed = identity["stdout"].lower()
            if identity["exit_code"] != 0 or "board.sysid=0xe7fa" not in observed or "fcecda" not in observed.replace(":", ""):
                raise RuntimeError("DEVICE_IDENTITY_MISMATCH")
            attempt["host_key_verified"] = True
            attempt["queries"] = {name: command(client, cmd) for name, cmd in QUERIES.items()}
            report["status"] = "OBSERVED"
            break
        except Exception as exc:
            attempt["error"] = {"type": type(exc).__name__, "message": str(exc).replace(password, "[redacted]")[:200]}
            if isinstance(exc, paramiko.SSHException) or "MISMATCH" in str(exc):
                break
        finally:
            client.close()
    report.setdefault("status", "NOT_OBSERVED")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ROOT / ("root_loco195_eth_readonly_" + stamp + ".json")
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "artifact": str(output), "attempts": len(report["attempts"])}))


if __name__ == "__main__":
    main()
