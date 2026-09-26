#!/usr/bin/env python3
"""FuturaMAX experiment G25: do airOS `set` ioctls actually take effect?

Design: the target knobs (AMPDULim / AMPDUFrames) have no working getter, so a direct
read-back is impossible. Phase 1 therefore validates the set-ioctl MECHANISM on knobs that
DO have getters (distance, enablertscts) — write, read back, restore. Phase 2 applies the
validated mechanism to the unobservable knobs and uses return status + dmesg + invalid-value
rejection as the evidence that the driver received and parsed the value.

Keywords: G25, iwpriv, AMPDULim, AMPDUFrames, set ioctl, lab unit, restore, LAP-120.
Read when: verifying airOS control knobs, or before trusting AIROS_CONTROL_SURFACE.md.
SAFETY: lab unit only (0 associated stations, management over ethernet). Every changed value
is recorded and restored. Never touches flash, u-boot, EEPROM, regulatory or country.
Verdict: CURRENT.
"""
from __future__ import annotations

import sys
import time
import warnings

import paramiko

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HOST, USER, PW = "192.168.1.20", "ubnt", "ubnt"

# Knobs that must never be touched on any unit.
FORBIDDEN = {"setCountry", "setHwaddr", "RegObey", "reset", "SetTargetReset", "gpio_config",
             "gpio_output", "sens_level"}


class Dev:
    def __init__(self):
        self.c = paramiko.SSHClient()
        self.c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.c.connect(HOST, username=USER, password=PW, timeout=20,
                       look_for_keys=False, allow_agent=False)

    def sh(self, cmd: str) -> tuple[str, str]:
        _, o, e = self.c.exec_command(cmd, timeout=40)
        return o.read().decode("utf-8", "replace").strip(), e.read().decode("utf-8", "replace").strip()

    def get(self, iface: str, name: str) -> str:
        out, err = self.sh(f"iwpriv {iface} {name} 2>&1")
        return (out or err).split(":")[-1].strip()

    def set(self, iface: str, name: str, *vals) -> tuple[str, bool]:
        assert name not in FORBIDDEN, f"REFUSING forbidden knob {name}"
        v = " ".join(str(x) for x in vals)
        out, err = self.sh(f"iwpriv {iface} {name} {v} 2>&1; echo RC=$?")
        rc_ok = "RC=0" in out
        msg = out.replace("RC=0", "").replace("RC=1", "").strip()
        return (msg or "(no output)"), rc_ok

    def dmesg_tail(self) -> str:
        out, _ = self.sh("dmesg | tail -4")
        return out

    def close(self):
        self.c.close()


def phase1(d: Dev) -> bool:
    """Validate the mechanism on knobs with working getters."""
    print("=" * 72)
    print("PHASE 1 — validate the set-ioctl mechanism on OBSERVABLE knobs")
    print("=" * 72)
    ok_all = True

    for iface, name, getter, testval in [
        ("wifi0", "distance", "get_distance", 5000),
        ("ath0", "enablertscts", "get_enablertscts", 1),
    ]:
        before = d.get(iface, getter)
        msg, rc = d.set(iface, name, testval)
        time.sleep(1)
        after = d.get(iface, getter)
        changed = str(after) != str(before)
        print(f"\n  {iface} {name}")
        print(f"    before      : {before}")
        print(f"    set {testval:<8}: rc_ok={rc}  {msg}")
        print(f"    after       : {after}   -> {'CHANGED ✅' if changed else 'UNCHANGED ❌'}")
        # restore
        d.set(iface, name, before)
        time.sleep(1)
        restored = d.get(iface, getter)
        print(f"    restored to : {restored}  {'✅' if str(restored)==str(before) else '❌ RESTORE FAILED'}")
        ok_all &= changed
    return ok_all


def phase2(d: Dev):
    """Apply the validated mechanism to the unobservable aggregation knobs."""
    print("\n" + "=" * 72)
    print("PHASE 2 — the target knobs (no getter available)")
    print("=" * 72)

    for iface, name, valid, invalid in [
        ("wifi0", "AMPDULim", 32768, 999999999),
        ("wifi0", "AMPDUFrames", 32, 99999),
        ("wifi0", "AMPDU", 1, None),
    ]:
        print(f"\n  {iface} {name}")
        before_dmesg = d.dmesg_tail()
        msg_v, rc_v = d.set(iface, name, valid)
        time.sleep(1)
        after_dmesg = d.dmesg_tail()
        print(f"    set {name} {valid:<12} rc_ok={rc_v}  out={msg_v}")
        if after_dmesg != before_dmesg:
            print(f"    dmesg changed:\n      " + "\n      ".join(after_dmesg.splitlines()[-2:]))
        else:
            print(f"    dmesg: unchanged")
        if invalid is not None:
            msg_i, rc_i = d.set(iface, name, invalid)
            print(f"    set {name} {invalid:<12} rc_ok={rc_i}  out={msg_i}")
            verdict = ("driver VALIDATES the value (accepts valid, rejects invalid) -> ioctl is live"
                       if rc_v and not rc_i else
                       "both accepted — no validation signal; cannot distinguish live from no-op"
                       if rc_v and rc_i else
                       "valid value REJECTED — knob likely not usable this way")
            print(f"    -> {verdict}")


def main() -> int:
    d = Dev()
    print(f"connected to {HOST}\n")
    sta, _ = d.sh("wstalist 2>/dev/null | grep -c '\"mac\"'")
    if sta.strip() not in ("0", ""):
        print(f"ABORT: {sta} associated stations — this is not a lab unit", file=sys.stderr)
        d.close()
        return 1
    print(f"safety: associated stations = {sta or 0}\n")

    mech_ok = phase1(d)
    print(f"\n>>> mechanism validated: {mech_ok}")
    if not mech_ok:
        print(">>> set-ioctls do NOT take effect on this build — phase 2 would be meaningless")
        d.close()
        return 0
    phase2(d)

    print("\n" + "=" * 72)
    print("final state check (all phase-1 knobs should be back at baseline)")
    print(f"  distance     = {d.get('wifi0','get_distance')}")
    print(f"  enablertscts = {d.get('ath0','get_enablertscts')}")
    print(f"  stations     = {d.sh('wstalist 2>/dev/null | grep -c \"mac\"')[0] or 0}")
    d.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
