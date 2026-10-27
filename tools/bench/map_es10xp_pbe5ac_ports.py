#!/usr/bin/env python3
"""Query ES-10XP (fe80::7683:c2ff:fe15:2a8b%29) waiting for ES-10XP# prompt."""
import socket
import sys
import time
from pathlib import Path

import paramiko

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.bench.inspect_pbe_5ac_gen2_pair import load_vault_passwords


def query_es10xp():
    pws = load_vault_passwords() + ["ubnt", "futura420"]
    host = "fe80::7683:c2ff:fe15:2a8b%29"
    addrinfo = socket.getaddrinfo(host, 22, socket.AF_INET6, socket.SOCK_STREAM)
    sockaddr = addrinfo[0][4]
    for pw in pws:
        for user in ["ubnt", "admin"]:
            s = None
            t = None
            try:
                s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                s.settimeout(5.0)
                s.connect(sockaddr)
                t = paramiko.Transport(s)
                t.start_client(timeout=5.0)
                t.auth_password(user, pw)
                if t.is_authenticated():
                    ch = t.open_session()
                    ch.get_pty()
                    ch.invoke_shell()
                    time.sleep(3.5)
                    ch.send("terminal length 0\r\nshow mac address-table\r\nshow interfaces GigabitEthernet 1-8\r\n")
                    time.sleep(3.5)
                    raw = b""
                    while ch.recv_ready():
                        raw += ch.recv(16384)
                    ch.close()
                    t.close()
                    return raw.decode("utf-8", errors="ignore")
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
    return "ES10XP_AUTH_FAILED"


if __name__ == "__main__":
    print(query_es10xp())
