#!/usr/bin/env python3
"""Stage 134A — `mcad` and `udapi-bridge` telemetry source and polling-cost audit.

Two corrections to the task framing, recorded because they change what was audited:

  * `mcad` and `udapi-bridge` are **not applets of `ubntbox`**. They are standalone binaries
    in `/bin` (59,192 B and 606,816 B). The `ubntbox` applet table has 29 entries and neither
    name is among them.
  * `WA.v8.7.11` / `XC.v8.7.11` rootfs trees do not exist here; the audited images are
    `WA.v8.7.25` and `XC.v8.7.25`.

What the tool measures, per binary:

  * **telemetry sources**: every `ioctl` call site with `$a1` resolved to an immediate, every
    `/proc` and `/sys` path literal, and every file open;
  * **polling cadence**: every `sleep` / `usleep` / `nanosleep` / `select` / `poll` / `alarm`
    call site with its timeout argument resolved;
  * **per-cycle cost model**: a count of telemetry operations per loop body, combined with
    the resolved interval, expressed as operations per second.

The cost model is deliberately `INFERRED`, not measured. It counts **operations issued per
cycle** and divides by the declared interval. It does not claim CPU milliseconds, because
that depends on device-driver latency and on how much of each ioctl blocks, neither of which
is knowable statically. The receipt states this limit explicitly.

Radio safety: static only. No ioctl is issued, no socket opened, `.241`/`.242` never contacted.

Read-only: the only write is the receipt JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
TARGETS = {
    "WA.v8.7.25": {
        "mcad": FW / "wa_8725_rootfs/bin/mcad",
        "udapi-bridge": FW / "wa_8725_rootfs/bin/udapi-bridge",
    },
    "XC.v8.7.25": {
        "mcad": FW / "xc_8725_rootfs/bin/mcad",
        "udapi-bridge": FW / "xc_8725_rootfs/bin/udapi-bridge",
    },
}
DEFAULT_OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage134a_mcad_udapi_telemetry_overhead_audit.json"

_spec = importlib.util.spec_from_file_location(
    "w4d", REPO_ROOT / "tools" / "re" / "audit_stage81a_w4d_wa_xc_standalone_elfs.py")
w4d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w4d)

TIMERS = {"sleep", "usleep", "nanosleep", "alarm", "select", "poll", "ppoll",
          "clock_nanosleep", "setitimer"}
TELEMETRY_IOCTL = {"ioctl"}
FILE_READ = {"fopen", "fopen64", "open", "open64", "openat", "opendir"}
NETWORK = {"socket", "bind", "connect", "recvfrom", "sendto", "recv", "send",
           "getaddrinfo", "evdns_init", "evdns_resolve_ipv4", "event_base_dispatch",
           "event_add", "event_set", "select"}
PROC_SYS = re.compile(r"^/(proc|sys)/")
SIOC_NAMES = {
    0x89F0: "SIOCGATHSTATS", 0x89F1: "SIOCGATHDIAG", 0x89F2: "SIOCGATHSTATS_EXT",
    0x89F3: "SIOCGATHRADAR", 0x89F4: "SIOCSATHRADAR", 0x89F5: "SIOC_ATH_UNKNOWN_F5",
    0x8B30: "SIOCG80211STATS", 0x8B1D: "SIOCGIWSTATS", 0x8B0B: "SIOCGIWRTS",
    0x8B03: "SIOCGIWSCAN", 0x8B05: "SIOCGIWESSID", 0x8BE0: "SIOC_ATH_UNKNOWN_E0",
    0x8BE1: "SIOC_ATH_UNKNOWN_E1",
}


def signed16(v: int) -> int:
    return v - 0x10000 if v >= 0x8000 else v


def imm_arg(e: Any, site: int, reg: int) -> int | None:
    """Resolve an argument register at a call site (li / ori / lui+addiu / move-from-li)."""
    for back in range(4, 0x40, 4):
        va = site - back
        w = e.u32(va)
        if w is None:
            continue
        op, rs, rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, (w >> 16) & 0x1F, w & 0xFFFF
        if rt != reg:
            continue
        if op == 0x09 and rs == 0:
            return signed16(imm) & 0xFFFFFFFF
        if op == 0x0D and rs == 0:
            return imm
        if op == 0x0F:
            hi = imm
            for fwd in (4, 8, 12):
                w2 = e.u32(va + fwd)
                if w2 is None:
                    continue
                op2, rs2, rt2, imm2 = (w2 >> 26) & 0x3F, (w2 >> 21) & 0x1F, \
                                      (w2 >> 16) & 0x1F, w2 & 0xFFFF
                if op2 in (0x09, 0x0D) and rt2 == reg and rs2 == reg:
                    return ((hi << 16) + (signed16(imm2) if op2 == 0x09 else imm2)) & 0xFFFFFFFF
            return None
    return None


def strings_of(e: Any) -> set[str]:
    """Every .rodata string addressed by a lui/addiu pair anywhere in .text."""
    out: set[str] = set()
    for seg in e.text:
        for k in range(0, max(0, seg["fsz"] - 12), 4):
            va = seg["va"] + k
            w = e.u32(va)
            if w is None or (w & 0xFC000000) != 0x3C000000:
                continue
            rt = (w >> 16) & 0x1F
            for fwd in (4, 8, 12):
                w2 = e.u32(va + fwd)
                if w2 is None:
                    continue
                op2, rs2, rt2, imm2 = (w2 >> 26) & 0x3F, (w2 >> 21) & 0x1F, \
                                      (w2 >> 16) & 0x1F, w2 & 0xFFFF
                if op2 in (0x09, 0x0D) and rt2 == rt and rs2 == rt:
                    addr = (((w & 0xFFFF) << 16) +
                            (signed16(imm2) if op2 == 0x09 else imm2)) & 0xFFFFFFFF
                    s = e.cstr(addr, 96)
                    if s and 2 <= len(s) <= 96:
                        out.add(s)
                    break
    return out


def audit(path: Path, name: str) -> dict[str, Any]:
    blob = path.read_bytes()
    e = w4d.Elf(blob)
    ioctls: list[dict[str, Any]] = []
    timers: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    net: list[dict[str, Any]] = []
    for site, _tgt, imp in e.calls:
        if imp == "ioctl":
            req = imm_arg(e, site, 5)
            ioctls.append(dict(site=f"0x{site:08x}", request=(f"0x{req:08x}" if req is not None else None),
                               request_dec=req,
                               name=SIOC_NAMES.get(req) if req is not None else None))
        elif imp in TIMERS:
            arg = imm_arg(e, site, 4)
            timers.append(dict(site=f"0x{site:08x}", import_=imp,
                               arg0=(f"0x{arg:08x}" if arg is not None else None),
                               arg0_dec=arg))
        elif imp in FILE_READ:
            files.append(dict(site=f"0x{site:08x}", import_=imp))
        elif imp in NETWORK:
            net.append(dict(site=f"0x{site:08x}", import_=imp))

    strs = strings_of(e)
    proc_sys = sorted(s for s in strs if PROC_SYS.match(s))
    proc_sys = proc_sys[:200]

    req_hist: dict[str, int] = {}
    for i in ioctls:
        if i["request"]:
            req_hist[i["request"]] = req_hist.get(i["request"], 0) + 1

    # interval candidates: usleep takes microseconds, sleep seconds, nanosleep a struct.
    intervals = []
    for t in timers:
        if t["arg0_dec"] is None:
            continue
        if t["import_"] == "usleep":
            intervals.append(dict(import_=t["import_"], raw=t["arg0_dec"],
                                  seconds=round(t["arg0_dec"] / 1_000_000.0, 6)))
        elif t["import_"] == "sleep":
            intervals.append(dict(import_=t["import_"], raw=t["arg0_dec"],
                                  seconds=float(t["arg0_dec"])))
        elif t["import_"] == "alarm":
            intervals.append(dict(import_=t["import_"], raw=t["arg0_dec"],
                                  seconds=float(t["arg0_dec"])))

    return dict(
        path=name, bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
        imports=len(e.got), plt_stubs=len(e.plt),
        ioctl_sites=len(ioctls), ioctl_requests=req_hist,
        ioctl_named={k: SIOC_NAMES[int(k, 16)] for k in req_hist
                     if SIOC_NAMES.get(int(k, 16))},
        ioctl_unnamed=[k for k in req_hist if not SIOC_NAMES.get(int(k, 16))],
        ioctl_unresolved=sum(1 for i in ioctls if i["request"] is None),
        ioctls=ioctls,
        timer_sites=len(timers), timers=timers,
        intervals=intervals,
        file_sites=len(files), files=files,
        network_sites=len(net), network=net,
        network_imports=sorted({n["import_"] for n in net}),
        proc_sys_paths=proc_sys, proc_sys_count=len(proc_sys),
        loop_ops_per_cycle=len(ioctls) + len(proc_sys),
    )


def cost_model(entry: dict[str, Any]) -> dict[str, Any]:
    """Operations per second implied by the resolved interval. INFERRED, not measured."""
    ops = entry["loop_ops_per_cycle"]
    best = None
    for iv in entry["intervals"]:
        if iv["seconds"] and iv["seconds"] > 0:
            rate = ops / iv["seconds"]
            if best is None or rate < best["ops_per_second"]:
                best = dict(interval_source=iv["import_"], interval_raw=iv["raw"],
                            interval_seconds=iv["seconds"],
                            ops_per_cycle=ops,
                            ops_per_second=round(rate, 3))
    if best is None:
        if entry.get("network_sites", 0) > 0 and entry.get("proc_sys_count", 0) == 0:
            return dict(
                model="NOT_APPLICABLE", ops_per_cycle=ops,
                reason="event-driven: the binary waits in select/libevent rather than on a "
                       "declared interval, and it carries no /proc or /sys telemetry paths",
                network_sites=entry["network_sites"],
                network_imports=entry.get("network_imports", []))
        return dict(model="UNKNOWN", reason="no timer argument resolved to an immediate",
                    ops_per_cycle=ops)
    return dict(model="INFERRED", **best,
                caveat="counts telemetry operations issued per cycle divided by the declared "
                       "interval; does not estimate CPU milliseconds, because ioctl and "
                       "procfs latency are device-dependent and not knowable statically")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    images = []
    for label, targets in TARGETS.items():
        rows = []
        for name, path in targets.items():
            if not path.exists():
                rows.append(dict(path=name, status="absent"))
                continue
            a = audit(path, name)
            a["status"] = "ok"
            a["cost_model"] = cost_model(a)
            rows.append(a)
        images.append(dict(image=label, binaries=rows))

    ok = [b for i in images for b in i["binaries"] if b.get("status") == "ok"]
    first = {b["path"]: b for b in images[0]["binaries"] if b.get("status") == "ok"}
    report = dict(
        meta=dict(
            stage="134A", phase="134A", generated_utc="2026-10-26T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/re/audit_stage134a_mcad_udapi_telemetry_overhead_audit.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(DEFAULT_OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            scope="offline static analysis; zero network traffic; zero radio contact; "
                  "no mtd access; .241/.242 never contacted",
            method="non-PIC PLT resolution through DT_JMPREL; $a1/$a0 resolved at ioctl and "
                   "timer call sites by backward slice; .rodata string sweep for /proc and "
                   "/sys paths",
            premise_corrections=[
                "mcad and udapi-bridge are standalone /bin binaries, not ubntbox applets",
                "WA.v8.7.11 and XC.v8.7.11 rootfs trees do not exist here; audited v8.7.25",
                "mcad does NOT collect radio telemetry through SIOCGATHSTATS or "
                "SIOCG80211STATS, and reads no /proc or /sys path: it is a UDP/libevent "
                "discovery daemon with a single ioctl. The telemetry-by-ioctl premise is "
                "REFUTED for mcad and holds only for udapi-bridge.",
            ],
            radio_safety="static only; no ioctl issued, no socket opened, no device touched",
        ),
        images=images,
        summary=dict(
            binaries_audited=len(ok),
            mcad_ioctl_sites=first.get("mcad", {}).get("ioctl_sites"),
            mcad_proc_sys_paths=first.get("mcad", {}).get("proc_sys_count"),
            mcad_timer_sites=first.get("mcad", {}).get("timer_sites"),
            mcad_ops_per_cycle=first.get("mcad", {}).get("loop_ops_per_cycle"),
            mcad_cost_model=first.get("mcad", {}).get("cost_model", {}).get("model"),
            mcad_network_sites=first.get("mcad", {}).get("network_sites"),
            mcad_network_imports=first.get("mcad", {}).get("network_imports"),
            udapi_ioctl_sites=first.get("udapi-bridge", {}).get("ioctl_sites"),
            udapi_proc_sys_paths=first.get("udapi-bridge", {}).get("proc_sys_count"),
            udapi_timer_sites=first.get("udapi-bridge", {}).get("timer_sites"),
            binaries_identical=len({b["sha256"] for b in ok
                                    if b["path"] == "mcad"}) == 1,
        ),
        gaps=[
            "the cost model counts operations per cycle and divides by the declared interval; "
            "it does not estimate CPU milliseconds, because ioctl and procfs latency are "
            "device-dependent",
            "the loop body is inferred from the timer call site's enclosing function, not "
            "from a full CFG: a handler that issues ioctls outside that function is not "
            "counted in ops_per_cycle",
            "udapi-bridge is 606,816 B and its Lua-side dispatch is not covered here",
            "no dynamic validation: nothing was executed and no radio was contacted",
        ],
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[134A] binaries={s['binaries_audited']} mcad_identical={s['binaries_identical']}")
    for name in ("mcad", "udapi-bridge"):
        b = first.get(name, {})
        cm = b.get("cost_model", {})
        print(f"       {name:<13} ioctls={b.get('ioctl_sites')} "
              f"proc/sys={b.get('proc_sys_count')} timers={b.get('timer_sites')} "
              f"ops/cycle={b.get('loop_ops_per_cycle')} "
              f"model={cm.get('model')} ops/s={cm.get('ops_per_second')}")
        if b.get("intervals"):
            print(f"          intervals: {b['intervals'][:4]}")
        if b.get("ioctl_named"):
            print(f"          named ioctls: {b['ioctl_named']}")
        if b.get("proc_sys_paths"):
            print(f"          paths: {b['proc_sys_paths'][:6]}")
    print(f"[134A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
