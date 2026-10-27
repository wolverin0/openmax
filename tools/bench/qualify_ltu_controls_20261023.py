"""Exact LTU-Lite bench observation; no scan, production route or persistence."""
import json
import hashlib
import re
import shlex
import socket
import time
import uuid
from pathlib import Path

import paramiko

from qualify_uisp_bridge_20261023 import ROOT, password, put, rpc, sha, utc

TARGET = "fe80::e063:daff:febf:5399%27"
BASE = "/sys/class/ame/ame_ctrl_dev/"
EXPECTED = {"board.name": "LTU-Lite", "board.sysid": "0xae08",
            "board.rev": "9", "board.hwaddr": "E063DABF5399"}
ART = ROOT / "artifacts"
PIN = "a2db0ab6dff457121b196178a8a9fd6232a473b34cfff93832af6bc4ce4fe128"


class LTU:
    def __init__(self, pin=None):
        self.expected_pin = pin
        self.socket = self.transport = self.client = None

    def __enter__(self):
        try:
            address = socket.getaddrinfo(TARGET, 22, socket.AF_INET6, socket.SOCK_STREAM)[0][4]
            assert address[0] == "fe80::e063:daff:febf:5399" and address[3] == 27
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.socket.settimeout(8)
            self.socket.connect(address)
            self.transport = paramiko.Transport(self.socket)
            self.transport.auth_timeout = self.transport.banner_timeout = 8
            self.transport.start_client(timeout=8)
            self.pin = sha(self.transport.get_remote_server_key().asbytes())
            if self.expected_pin:
                assert self.pin == self.expected_pin, "LTU_SSH_KEY_CHANGED"
            self.transport.auth_password("ubnt", password())
            self.client = paramiko.SSHClient()
            self.client._transport = self.transport
            command = "awk -F= '$1==\"board.name\" || $1==\"board.sysid\" || $1==\"board.rev\" || $1==\"board.hwaddr\" {print}' /etc/board.info"
            self.identity = dict(line.split("=", 1) for line in rpc(self.client, command)["stdout"].splitlines())
            assert self.identity == EXPECTED, "WRONG_LTU_HARDWARE"
            return self
        except BaseException:
            self.__exit__()
            raise

    def __exit__(self, *unused):
        if self.client:
            self.client.close()
        if self.transport:
            self.transport.close()
        if self.socket:
            self.socket.close()


def inspect():
    output = ART / "stage11_ltulite_inspection_20261023.json"
    assert not output.exists(), "LTU_RECEIPT_COLLISION"
    result = dict(utc=utc(), target=TARGET, production_contact=False,
                  status="NOT_OBSERVED", writes_performed=False)
    try:
        with LTU() as bench:
            result.update(status="OBSERVED_EXACT_LTU_LITE", identity=bench.identity,
                          ssh_host_key_sha256=bench.pin,
                          key_trust="First-seen key on the fixed operator-named EUI64 bench address; bound to freshly verified board/MAC, then pinned for any subsequent treatment")
            queries = {
                "version_boot": "cat /etc/version; uname -r; cat /proc/sys/kernel/random/boot_id; cat /proc/uptime",
                "network": "ip -o addr show; ip route show",
                "controls_directory": "readlink -f " + BASE.rstrip("/") + "; ls -1 " + BASE,
                "debug_directory": "ls -1 /sys/kernel/debug/ame",
                "mcs_decoded": "/usr/bin/ame_adj.sh mcs",
                "af_ceiling": "/bin/af get automcsceil",
                "scheduler": "dd if=/sys/kernel/debug/ame/sched_mcs bs=256 count=1",
                "config_hashes": "md5sum /tmp/system.cfg /tmp/ame.cfg /etc/inittab /usr/bin/ame_adj.sh",
                "dmesg": "dmesg | tail -n 60",
                "ram_tools": "df -k /tmp; head -n 5 /proc/meminfo; command -v sha256sum; command -v md5sum; command -v timeout",
            }
            for field in ["hw_features", "autoMcsCeiling", "adj_mcs", "autoMcs4096", "ofdma_subbands", "ofdma_en", "reg_info", "reg_obey", "rxfreq", "txfreq"]:
                queries[field] = "dd if=" + BASE + field + " bs=1024 count=1"
            result["queries"] = {}
            for name, command in queries.items():
                result["queries"][name] = rpc(bench.client, command, timeout=8, check=False)
    except Exception as error:
        result.update(status="BLOCKED_LTU_OBSERVATION", error=type(error).__name__ + ": " + str(error))
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(status=result["status"], error=result.get("error"), receipt=str(output),
                         identity=result.get("identity"), ssh_host_key_sha256=result.get("ssh_host_key_sha256"))))


def airmac(client):
    value = rpc(client, "/usr/www/ameeng.cgi", timeout=6, limit=131072)
    text = value["stdout"]
    parsed = json.loads(text[text.index("{"):])
    flag = parsed["engineer"]["l2p"]["eabq"]["airMACEnabled"]
    assert type(flag) is int and flag == 0, "AIRMAC_NOT_ZERO"
    return dict(value=flag, utc=utc(), raw_sha256=sha(text.encode()))


def snapshot(client):
    commands = {k: "cat " + BASE + k for k in
                ["autoMcsCeiling", "adj_mcs", "autoMcs4096", "ofdma_subbands", "ofdma_en", "hw_features", "reg_info", "txfreq"]}
    commands.update(scheduler="cat /sys/kernel/debug/ame/sched_mcs",
                    af_ceiling="/bin/af get automcsceil",
                    config_hashes="md5sum /tmp/system.cfg /tmp/ame.cfg /etc/inittab /usr/bin/ame_adj.sh",
                    boot="cat /proc/sys/kernel/random/boot_id",
                    network="ip -o addr show; ip route show",
                    version="cat /etc/version; uname -r",
                    dmesg="dmesg | tail -n 60")
    result = {name: rpc(client, cmd, timeout=6) for name, cmd in commands.items()}
    result["airmac"] = airmac(client)
    return result


def profile_ok(state):
    return (state["autoMcsCeiling"]["stdout"].strip() == "23" and
            state["adj_mcs"]["stdout"].strip() == "0x20" and
            state["autoMcs4096"]["stdout"].strip() == "10" and
            state["ofdma_subbands"]["stdout"].strip() == "0xff" and
            state["scheduler"]["stdout"].strip() == "MIMO MCS:FB:1024Ql")


def execute(label):
    assert label.isalnum() and len(label) <= 8
    output = ART / ("stage11_ltulite_4096qam_ofdma_live_20261023_" + label + ".json")
    assert not output.exists(), "LIVE_RECEIPT_COLLISION"
    d = "/tmp/fmx-ltu-" + uuid.uuid4().hex
    q = shlex.quote
    result = dict(utc=utc(), status="INCOMPLETE", label=label, target=TARGET,
                  operator_context="Operator confirms isolated indoor bench, no active LTU AP, no RF TX and airMACEnabled0; explicitly authorizes this native RAM/sysfs probe",
                  production_contact=False, firmware_flash=False, persistent_config_write=False,
                  owned_ram=d, steps={}, errors=[])
    with LTU(PIN) as bench:
        c = bench.client
        result.update(identity=bench.identity, ssh_host_key_sha256=bench.pin)
        before = result["before"] = snapshot(c)
        assert profile_ok(before), "ORIGINAL_BASELINE_PROFILE_CHANGED"
        assert "4c5e1f0a1a17d38b15d734fef63bd0aa  /usr/bin/ame_adj.sh" in before["config_hashes"]["stdout"], "NATIVE_HELPER_SOURCE_CHANGED"
        flags = json.loads(before["hw_features"]["stdout"])
        assert flags["NO_LDPC"] == flags["NO_OFDMA"] == 0, "HARDWARE_FEATURE_GUARD_SET"
        result["native_mcs_parser"] = rpc(c, "awk '/^f_MCS_STR_TO_NUM/{p=1} p{print} p && /^}/{exit}' /usr/bin/ame_adj.sh")
        assert "4096|4096qam|4096l|4096qaml)" in result["native_mcs_parser"]["stdout"], "MCS_NATIVE_PARSER_CHANGED"
        rpc(c, "set -eu; umask 077; mkdir " + q(d) + "; printf '%s\\n' " + q(d) + " >" + q(d + "/owner"))
        common = r"""D=__D__
B=/sys/class/ame/ame_ctrl_dev
test "$(cat "$D/owner")" = "$D" || exit 90
airzero() {
  raw=$(/usr/www/ameeng.cgi) || return 61
  value=$(printf '%s\n' "$raw" | awk '/"airMACEnabled"[[:space:]]*:/{n++; v=$0; sub(/^.*:[[:space:]]*/, "", v); sub(/,[[:space:]]*$/, "", v); gsub(/[[:space:]]/, "", v)} END{if(n!=1 || v!="0") exit 1; print v}') || return 62
  test "$value" = 0 || return 63
  printf '%s %s %s\n' "$1" "$(cut -d' ' -f1 /proc/uptime)" "$value" >> "$D/airmac.log"
}
stopop() {
  test -f "$D/op.pid" || return 0
  p=$(cat "$D/op.pid"); expected=$(cat "$D/op.start")
  if test -r /proc/$p/cmdline && tr '\000' '\n' < /proc/$p/cmdline | grep -Fxq "$D/op.sh"; then
    test "$(awk '{print $22}' /proc/$p/stat)" = "$expected" || return 70
    # Direct children belong to this verified, private operation shell only.
    children=$(cat /proc/$p/task/$p/children 2>/dev/null)
    : > "$D/children.owned"
    for child in $children; do
      test -r /proc/$child/stat || continue
      stamp=$(awk '{print $22}' /proc/$child/stat)
      printf '%s %s\n' "$child" "$stamp" >> "$D/children.owned"
      kill "$child" 2>/dev/null || :
    done
    kill "$p" 2>/dev/null || :; sleep 1
    while read -r child stamp; do
      test -r /proc/$child/stat || continue
      test "$(awk '{print $22}' /proc/$child/stat)" != "$stamp" || kill -KILL "$child" 2>/dev/null || :
    done < "$D/children.owned"
    if test -r /proc/$p/cmdline && tr '\000' '\n' < /proc/$p/cmdline | grep -Fxq "$D/op.sh"; then kill -KILL "$p" 2>/dev/null || :; fi
    sleep 1
  fi
  if test -r /proc/$p/cmdline; then ! tr '\000' '\n' < /proc/$p/cmdline | grep -Fxq "$D/op.sh" || return 71; fi
}
""".replace("__D__", q(d))
        restore = r"""#!/bin/sh
. __COMMON__
touch "$D/stopping"
stopop || exit 72
if ! mkdir "$D/restore.lock" 2>/dev/null; then
  n=0
  while test ! -f "$D/restore.rc" && test "$n" -lt 4; do sleep 1; n=$((n+1)); done
  test -f "$D/restore.rc" && test "$(cat "$D/restore.rc")" = 0
  exit $?
fi
rc=0
/usr/bin/ame_adj.sh mcs 1024l || rc=73
printf '%s\n' 23 > "$B/autoMcsCeiling" || rc=74
printf '%s\n' 0x20 > "$B/adj_mcs" || rc=75
printf '%s\n' 0xff > "$B/ofdma_subbands" || rc=76
test "$(cat "$B/autoMcsCeiling")" = 23 || rc=77
test "$(cat "$B/adj_mcs")" = 0x20 || rc=78
test "$(cat "$B/autoMcs4096")" = 10 || rc=79
test "$(cat "$B/ofdma_subbands")" = 0xff || rc=80
test "$(cat /sys/kernel/debug/ame/sched_mcs | tr -d '\n ')" = MIMOMCS:FB:1024Ql || rc=81
printf '%s\n' "$rc" > "$D/restore.rc"
exit "$rc"
""".replace("__COMMON__", q(d + "/common.sh"))
        guard = r"""#!/bin/sh
trap '' HUP
. __COMMON__
awk '{print $22}' /proc/$$/stat > "$D/guard.start"
cut -d. -f1 /proc/uptime > "$D/guard.uptime"
echo READY > "$D/guard.ready"
n=0
while test "$n" -lt 80; do
  test ! -f "$D/done" || exit 0
  sleep 1; n=$((n+1))
done
echo DEADLINE > "$D/guard.reason"
touch "$D/expired"
sh "$D/restore.sh" > "$D/guard.restore.log" 2>&1
""".replace("__COMMON__", q(d + "/common.sh"))
        operation = r"""#!/bin/sh
set -eu
. __COMMON__
test ! -e "$D/expired" && test ! -e "$D/stopping"
g=$(cat "$D/guard.pid")
test "$(awk '{print $22}' /proc/$g/stat)" = "$(cat "$D/guard.start")"
tr '\000' '\n' < /proc/$g/cmdline | grep -Fxq "$D/guard.sh"
now=$(cut -d. -f1 /proc/uptime); start=$(cat "$D/guard.uptime")
test $((now-start)) -lt 50
echo $$ > "$D/op.pid"
awk '{print $22}' /proc/$$/stat > "$D/op.start"
airzero "before_$1"
case "$1" in
ceiling31) printf '%s\n' 31 > "$B/autoMcsCeiling";;
fixed_requested) /usr/bin/ame_adj.sh mcs 4096L;;
fixed_native) /usr/bin/ame_adj.sh mcs 4096l;;
ofdma_ff) printf '%s\n' 0xff > "$B/ofdma_subbands";;
*) exit 64;;
esac
airzero "after_$1"
rm "$D/op.pid" "$D/op.start"
""".replace("__COMMON__", q(d + "/common.sh"))
        scripts = {"common.sh": common, "restore.sh": restore, "guard.sh": guard, "op.sh": operation}
        result["scripts"] = {name: dict(source=text, sha256=sha(text.encode()), md5=hashlib.md5(text.encode()).hexdigest()) for name, text in scripts.items()}
        scripts_verified = controls_may_have_changed = False
        try:
            for name, text in scripts.items():
                put(c, d + "/" + name, text.encode())
                rpc(c, "sh -n " + q(d + "/" + name))
            got = rpc(c, "md5sum " + " ".join(q(d + "/" + name) for name in scripts))
            result["remote_source_hashes"] = got
            assert [line.split()[0] for line in got["stdout"].splitlines()] == [v["md5"] for v in result["scripts"].values()], "REMOTE_SCRIPT_HASH_MISMATCH"
            scripts_verified = True
            rpc(c, "sh " + q(d + "/guard.sh") + " </dev/null >" + q(d + "/guard.log") + " 2>&1 & echo $! >" + q(d + "/guard.pid"))
            time.sleep(.25)
            result["guard_ready"] = rpc(c, "set -eu; test \"$(cat " + q(d + "/guard.ready") + ")\" = READY; g=$(cat " + q(d + "/guard.pid") + "); test \"$(awk '{print $22}' /proc/$g/stat)\" = \"$(cat " + q(d + "/guard.start") + ")\"; tr '\\000' '\\n' < /proc/$g/cmdline | grep -Fxq " + q(d + "/guard.sh"))
            for step in ["ceiling31", "fixed_requested", "fixed_native", "ofdma_ff"]:
                item = result["steps"][step] = dict(command="sh " + q(d + "/op.sh") + " " + step)
                controls_may_have_changed = True
                item["write"] = rpc(c, item["command"], timeout=8, check=False)
                item["state"] = snapshot(c)
                assert item["write"]["exit_code"] == 0, "NATIVE_WRITE_FAILED_" + step
                state = item["state"]
                new_kernel_lines = set(state["dmesg"]["stdout"].splitlines()) - set(before["dmesg"]["stdout"].splitlines())
                item["new_kernel_faults"] = [line for line in sorted(new_kernel_lines) if re.search(r"BUG:|Oops:|Kernel panic|Call Trace:|WARNING:|SIGSEGV", line)]
                assert not item["new_kernel_faults"], "NEW_KERNEL_FAULT_" + step
                assert state["autoMcsCeiling"]["stdout"].strip() == "31", "CEILING_READBACK"
                if step == "fixed_requested":
                    assert state["adj_mcs"]["stdout"].strip() == "0x20", "UNEXPECTED_UPPERCASE_BEHAVIOR"
                    item["interpretation"] = "Requested uppercase alias returned usage/rc0 without fixed-rate application; native lowercase spelling follows"
                if step in ["fixed_native", "ofdma_ff"]:
                    assert state["adj_mcs"]["stdout"].strip() == "0x1f", "FIXED_RATE_READBACK"
                    assert "4096l" in state["scheduler"]["stdout"], "SCHEDULER_READBACK"
                if step == "ofdma_ff":
                    assert state["ofdma_subbands"]["stdout"].strip() == "0xff", "OFDMA_READBACK"
            result["status"] = "NATIVE_CONTROLS_ACCEPTED_PENDING_RESTORATION"
        except Exception as error:
            result["errors"].append(type(error).__name__ + ": " + str(error))
            result["status"] = "NOT_ACCEPTED_NATIVE_TREATMENT"
            if hasattr(error, "rpc_result"):
                result["rpc_failure"] = error.rpc_result
        finally:
            def recover(name, command, timeout=8):
                try:
                    value = rpc(c, command, timeout=timeout, check=False)
                except Exception as error:
                    value = dict(exit_code=-1, error=str(error), stdout="")
                result[name] = value
                return value
            # A partial upload is never an executable recovery program.
            result["scripts_verified"] = scripts_verified
            result["controls_dispatched"] = controls_may_have_changed
            if controls_may_have_changed and scripts_verified:
                restore_result = recover("restore", "sh " + q(d + "/restore.sh"), timeout=12)
            else:
                restore_result = result["restore"] = dict(exit_code=0, stdout="No native control dispatched; baseline check only", stderr="")
            try:
                after = result["after"] = snapshot(c)
                stable = ["autoMcsCeiling", "adj_mcs", "autoMcs4096", "ofdma_subbands", "ofdma_en", "hw_features", "reg_info", "txfreq", "scheduler", "af_ceiling", "config_hashes", "boot", "network", "version"]
                result["baseline_equal"] = all(before[k]["stdout"] == after[k]["stdout"] for k in stable) and profile_ok(after)
            except Exception as error:
                result["postcheck_error"] = str(error)
                result["baseline_equal"] = False
            recover("airmac_samples", "test ! -f " + q(d + "/airmac.log") + " || cat " + q(d + "/airmac.log"))
            recover("guard_reason", "test ! -f " + q(d + "/guard.reason") + " || cat " + q(d + "/guard.reason"))
            result["restored"] = restore_result["exit_code"] == 0 and result["baseline_equal"]
            if result["restored"]:
                stop = recover("guard_stop", "set -eu; touch " + q(d + "/done") + "; if test -f " + q(d + "/guard.pid") + "; then p=$(cat " + q(d + "/guard.pid") + "); if test -r /proc/$p/cmdline && tr '\\000' '\\n' < /proc/$p/cmdline | grep -Fxq " + q(d + "/guard.sh") + "; then test \"$(awk '{print $22}' /proc/$p/stat)\" = \"$(cat " + q(d + "/guard.start") + ")\"; kill $p; fi; sleep 1; if test -r /proc/$p/cmdline; then ! tr '\\000' '\\n' < /proc/$p/cmdline | grep -Fxq " + q(d + "/guard.sh") + "; fi; fi")
                if stop["exit_code"] == 0:
                    recover("ram_remove", "test \"$(cat " + q(d + "/owner") + ")\" = " + q(d) + " && rm -r " + q(d))
                    result["ram_absent"] = recover("ram_check", "test ! -e " + q(d))["exit_code"] == 0
            if not result["restored"] or not result.get("ram_absent"):
                result["status"] = "FAIL_RESTORATION_OR_CLEANUP"
            elif result["guard_reason"].get("stdout", "ERROR").strip():
                result["status"] = "NOT_ACCEPTED_GUARD_TRIGGERED"
            elif result["status"] == "NATIVE_CONTROLS_ACCEPTED_PENDING_RESTORATION":
                result["status"] = "PASS_NATIVE_CONTROLS_RESTORED_NO_RF_CLAIM"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(status=result["status"], errors=result["errors"], restored=result.get("restored"), receipt=str(output))))


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--inspect"]:
        inspect()
    elif len(sys.argv) == 3 and sys.argv[1] == "--execute":
        execute(sys.argv[2])
    else:
        print("READONLY_INSPECTION_ONLY; --inspect on the fixed bench LTU-Lite")
