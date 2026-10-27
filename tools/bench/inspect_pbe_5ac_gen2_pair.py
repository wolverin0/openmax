#!/usr/bin/env python3
"""Full inspection of the two PowerBeam 5AC Gen2 units (87:73 and 8a:01)."""
import ast
import socket
import sys
from pathlib import Path

import paramiko

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CANDIDATES = [
    ("ptp-guarida-ap (87:73)", "fe80::ae8b:a9ff:fec2:8773%29"),
    ("PTP-ALMA-STA (8a:01)", "fe80::ae8b:a9ff:fec2:8a01%29"),
]


def load_vault_passwords():
    provider = REPO_ROOT / "artifacts/canary_panel1_guarida/panel1_cutover_preflight_20261019.py"
    fn = next(
        n for n in ast.parse(provider.read_text(encoding="utf-8")).body
        if isinstance(n, ast.FunctionDef) and n.name == "credentials"
    )
    assign = next(
        n for n in fn.body
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "pointer" for t in n.targets)
    )
    pointer = Path(ast.literal_eval(assign.value.args[0]))
    pws = []
    for line in pointer.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.strip().partition("=")
        if sep:
            v = value.strip().strip('"').strip("'")
            if v and v not in pws:
                pws.append(v)
    return pws


def run_ssh_cmd(host: str, pws: list[str], cmd: str) -> str:
    addrinfo = socket.getaddrinfo(host, 22, socket.AF_INET6, socket.SOCK_STREAM)
    sockaddr = addrinfo[0][4]
    for pw in pws:
        for user in ["ubnt", "admin", "root"]:
            s = None
            t = None
            try:
                s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                s.settimeout(4.0)
                s.connect(sockaddr)
                t = paramiko.Transport(s)
                t.start_client(timeout=4.0)
                t.auth_password(user, pw)
                if t.is_authenticated():
                    ch = t.open_session()
                    ch.exec_command(cmd)
                    chunks = []
                    while True:
                        data = ch.recv(16384)
                        if not data:
                            break
                        chunks.append(data.decode("utf-8", errors="ignore"))
                    ch.close()
                    t.close()
                    return "".join(chunks)
                t.close()
            except Exception:
                if t:
                    try:
                        t.close()
                    except Exception:
                        pass
                elif s:
                    try:
                        s.close()
                    except Exception:
                        pass
    return "AUTH_FAILED"


def main():
    pws = load_vault_passwords()
    cmd = (
        "cat /etc/version; "
        "cat /etc/board.info | grep -E 'board.name|board.sysid|board.hwaddr|board.subtype'; "
        "ip -4 addr show; "
        "iwconfig ath0 2>/dev/null; "
        "wstalist 2>/dev/null | head -n 35; "
        "grep -E 'resolv.host.1.name|wireless.1.ssid|wireless.1.mode|wpasupplicant.profile.1.network.1.psk|radio.1.mode|radio.1.freq|radio.1.chanbw|radio.1.txpower|radio.1.polling|netmode|netconf|dhcpc|bridge.1' /tmp/system.cfg"
    )
    for label, host in CANDIDATES:
        print(f"================ {label} ({host}) ================")
        print(run_ssh_cmd(host, pws, cmd))


if __name__ == "__main__":
    main()
