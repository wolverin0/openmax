#!/usr/bin/env python3
"""Stage 113A — full `athbox` audit: 15 applets, 69 PLT stubs, ioctl surface and sinks.

`athbox` is the sibling multicall binary of `ubntbox`: 202,920 bytes, `ET_EXEC` MIPS32
big-endian, section-header stripped, non-PIC. It exports 15 applets, three of which are the
ones the W4D task was actually asking about:

    radartool   athstats   pktlogconf

plus the rest of the Atheros tooling (`athchans`, `80211stats`, `athdebug`, `haldebug`,
`wlanconfig`, `regdomain`, `apstats`, `upollstats`, …).

Import resolution uses the non-PIC PLT stub pattern established in W4D:

    lui   $t7, hi        ; 0x3c0f....
    lw    $t9, lo($t7)   ; 0x8df9....
    jr    $t9            ; 0x03200008
    addiu $t8, $t7, lo   ; 0x25f8....

`target_got = (hi << 16) + sign_extend16(lo)`, then `DT_JMPREL` names the slot. No `_gp` is
involved, so every attribution here is deterministic.

For each applet the tool records, at depth 2 of the local `jal` graph:

  * **ioctl requests**: every `ioctl` call site with `$a1` resolved to an immediate, so the
    Atheros-specific request codes (`SIOCGATHSTATS`, `SIOCGATHDIAG`, `SIOCG80211STATS`, …)
    are computed from the binary rather than assumed;
  * **execution sinks**: `system`, `popen`, `exec*`;
  * **file sinks**: `fopen`, `open`, `unlink`, `rename`, `chmod`, `stat`;
  * **string literals** the handler references, which is how the hidden `radartool`
    sub-commands surface.

Radio safety: this is static analysis only. It reads files under `artifacts/` and never
opens a socket. `.241` and `.242` are not contacted, and no `mtd` is touched.

Read-only: the only write is the receipt JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
ATHBOX = {"WA.v8.7.25": FW / "wa_8725_rootfs/bin/athbox",
          "XC.v8.7.25": FW / "xc_8725_rootfs/bin/athbox"}
DEFAULT_OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage113a_athbox_15applets_plt_and_ioctl_audit.json"

_spec = importlib.util.spec_from_file_location(
    "w4d", REPO_ROOT / "tools" / "re" / "audit_stage81a_w4d_wa_xc_standalone_elfs.py")
w4d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w4d)

EXECUTION = {"system", "popen", "execl", "execle", "execlp", "execv", "execve", "execvp"}
FILE_SINKS = {"fopen", "fopen64", "open", "open64", "openat", "creat", "unlink", "rename",
              "chmod", "fchmod", "chown", "symlink", "link", "truncate", "ftruncate",
              "stat", "lstat", "access", "opendir"}
NETWORK = {"socket", "connect", "bind", "listen", "accept", "sendto", "recvfrom",
           "setsockopt", "getsockopt"}

# known Atheros/SIOC request names. Values are NOT assumed: each is only attached to a site
# when the site's resolved $a1 equals the value listed here, and the mapping is reported as
# INFERRED because <linux/wireless.h> / <ath_ioctl.h> were not read from this image.
SIOC_NAMES = {
    0x8946: "SIOCGIWNAME", 0x8947: "SIOCSIWNWID", 0x8B01: "SIOCGIWAP",
    0x8B02: "SIOCSIWSCAN", 0x8B03: "SIOCGIWSCAN", 0x8B04: "SIOCSIWESSID",
    0x8B05: "SIOCGIWESSID", 0x8B06: "SIOCSIWNICKN", 0x8B07: "SIOCGIWNICKN",
    0x8B08: "SIOCSIWRATE", 0x8B09: "SIOCGIWRATE", 0x8B0A: "SIOCSIWRTS",
    0x8B0B: "SIOCGIWRTS", 0x8B0C: "SIOCSIWFRAG", 0x8B0D: "SIOCGIWFRAG",
    0x8B0E: "SIOCSIWTXPOW", 0x8B0F: "SIOCGIWTXPOW", 0x8B10: "SIOCSIWRETRY",
    0x8B11: "SIOCGIWRETRY", 0x8B12: "SIOCSIWENCODE", 0x8B13: "SIOCGIWENCODE",
    0x8B14: "SIOCSIWPOWER", 0x8B15: "SIOCGIWPOWER", 0x8B1A: "SIOCSIWGENIE",
    0x8B1B: "SIOCGIWGENIE", 0x8B1C: "SIOCSIWMLME", 0x8B1D: "SIOCGIWSTATS",
    0x8B1E: "SIOCSIWAUTH", 0x8B1F: "SIOCGIWAUTH", 0x8B20: "SIOCSIWENCODEEXT",
    0x8B21: "SIOCGIWENCODEEXT",
    0x89F0: "SIOCGATHSTATS", 0x89F1: "SIOCGATHDIAG", 0x89F2: "SIOCGATHSTATS_EXT",
    0x89F3: "SIOCGATHRADAR", 0x89F4: "SIOCSATHRADAR",
    0x8B30: "SIOCG80211STATS",
}
RADAR_HINT = re.compile(r"radar|dfs|chan|spectral|pulse|chirp|fft|phyerr|ani|nf|noise",
                        re.IGNORECASE)


def signed16(v: int) -> int:
    return v - 0x10000 if v >= 0x8000 else v


def imm_arg(e: Any, site: int, reg: int) -> int | None:
    """Resolve an argument register at a call site: li / ori / lui+addiu / move from a li."""
    for back in range(4, 0x40, 4):
        va = site - back
        w = e.u32(va)
        if w is None:
            continue
        op, rs, rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, (w >> 16) & 0x1F, w & 0xFFFF
        if rt != reg:
            continue
        if op == 0x09 and rs == 0:                       # li reg, imm
            return signed16(imm) & 0xFFFFFFFF
        if op == 0x0D and rs == 0:                       # ori reg, $zero, imm
            return imm
        if op == 0x0F:                                   # lui reg, hi  -> look for addiu
            hi = imm
            for fwd in range(4, 0x18, 4):
                w2 = e.u32(va + fwd)
                if w2 is None:
                    continue
                op2, rs2, rt2, imm2 = (w2 >> 26) & 0x3F, (w2 >> 21) & 0x1F, \
                                      (w2 >> 16) & 0x1F, w2 & 0xFFFF
                if op2 in (0x09, 0x0D) and rt2 == reg and rs2 == reg:
                    base = (hi << 16)
                    return (base + (signed16(imm2) if op2 == 0x09 else imm2)) & 0xFFFFFFFF
            return None
        if op == 0x00 and ((w >> 11) & 0x1F) == reg:      # move reg, rs
            src = rs
            for back2 in range(back + 4, back + 0x40, 4):
                v2 = site - back2
                w3 = e.u32(v2)
                if w3 is None:
                    continue
                op3, rs3, rt3, imm3 = (w3 >> 26) & 0x3F, (w3 >> 21) & 0x1F, \
                                      (w3 >> 16) & 0x1F, w3 & 0xFFFF
                if rt3 == src and op3 == 0x09 and rs3 == 0:
                    return signed16(imm3) & 0xFFFFFFFF
            return None
    return None


def collect(e: Any, fn: int, depth: int = 2) -> dict[str, Any]:
    """Walk the local jal graph from `fn` and gather ioctls, sinks and strings."""
    ioctls: list[dict[str, Any]] = []
    execs: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    nets: list[dict[str, Any]] = []
    strings: set[str] = set()
    seen: set[int] = set()
    frontier = [fn]
    for level in range(depth + 1):
        nxt: list[int] = []
        for base in frontier:
            if base in seen:
                continue
            seen.add(base)
            hi = e.extent(base)
            for site, tgt, imp in e.calls:
                if not (base <= site < hi):
                    continue
                if imp is None:
                    if e.tlo <= tgt < e.thi:
                        nxt.append(tgt)
                    continue
                if imp == "ioctl":
                    req = imm_arg(e, site, 5)                # $a1
                    ioctls.append(dict(
                        site=f"0x{site:08x}", level=level,
                        request=(f"0x{req:08x}" if req is not None else None),
                        request_dec=req,
                        name=SIOC_NAMES.get(req) if req is not None else None))
                elif imp in EXECUTION:
                    execs.append(dict(site=f"0x{site:08x}", import_=imp, level=level))
                elif imp in FILE_SINKS:
                    files.append(dict(site=f"0x{site:08x}", import_=imp, level=level))
                elif imp in NETWORK:
                    nets.append(dict(site=f"0x{site:08x}", import_=imp, level=level))
            # string literals addressed by lui/addiu inside this function
            for k in range(0, max(0, hi - base - 8), 4):
                va = base + k
                w = e.u32(va)
                if w is None or (w & 0xFC000000) != 0x3C000000:
                    continue
                rt = (w >> 16) & 0x1F
                for fwd in (4, 8):
                    w2 = e.u32(va + fwd)
                    if w2 is None:
                        continue
                    op2, rs2, rt2, imm2 = (w2 >> 26) & 0x3F, (w2 >> 21) & 0x1F, \
                                          (w2 >> 16) & 0x1F, w2 & 0xFFFF
                    if op2 in (0x09, 0x0D) and rt2 == rt and rs2 == rt:
                        addr = (((w & 0xFFFF) << 16) +
                                (signed16(imm2) if op2 == 0x09 else imm2)) & 0xFFFFFFFF
                        s = e.cstr(addr)
                        if s and 2 <= len(s) <= 48:
                            strings.add(s)
                        break
        frontier = nxt
        if not frontier:
            break
    return dict(ioctls=ioctls, execs=execs, files=files, nets=nets,
                strings=sorted(strings))


def audit(e: Any) -> dict[str, Any]:
    groups = e.applets()
    applets = [a for g in groups for a in g["applets"]]
    rows = []
    for a in applets:
        c = collect(e, a["fn"])
        radar = sorted(s for s in c["strings"] if RADAR_HINT.search(s))
        rows.append(dict(
            name=a["name"], fn=f"0x{a['fn']:08x}", entry_va=f"0x{a['entry_va']:08x}",
            extent=f"0x{e.extent(a['fn']):08x}",
            ioctls=c["ioctls"], ioctl_count=len(c["ioctls"]),
            ioctl_requests=sorted({i["request"] for i in c["ioctls"] if i["request"]}),
            execution=c["execs"], execution_count=len(c["execs"]),
            file_sinks=c["files"], file_sink_count=len(c["files"]),
            network_sinks=c["nets"],
            strings_count=len(c["strings"]),
            radar_strings=radar,
        ))
    all_ioctls = [i for r in rows for i in r["ioctls"]]
    req_hist = Counter(i["request"] for i in all_ioctls if i["request"])
    named = {k: v for k, v in req_hist.items() if SIOC_NAMES.get(int(k, 16))}
    unnamed = {k: v for k, v in req_hist.items() if not SIOC_NAMES.get(int(k, 16))}
    return dict(
        bytes=len(e.d), sha256=hashlib.sha256(e.d).hexdigest(),
        plt_stubs=len(e.plt), jal_total=len(e.calls),
        jal_resolved=sum(1 for c in e.calls if c[2]),
        imports=len(e.got),
        applet_tables=len(groups), applet_count=len(applets),
        applets=rows,
        ioctl_requests=named, ioctl_requests_unnamed=unnamed,
        ioctl_sites=len(all_ioctls),
        ioctl_unresolved=sum(1 for i in all_ioctls if i["request"] is None),
        execution_total=sum(r["execution_count"] for r in rows),
        file_sink_total=sum(r["file_sink_count"] for r in rows),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    images = []
    for label, path in ATHBOX.items():
        if not path.exists():
            images.append(dict(image=label, status="absent"))
            continue
        blob = path.read_bytes()
        e = w4d.Elf(blob)
        images.append(dict(image=label, status="ok", **audit(e)))

    ok = [i for i in images if i.get("status") == "ok"]
    first = ok[0]
    report = dict(
        meta=dict(
            stage="113A", phase="113A",
            generated_utc="2026-10-26T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/re/audit_stage113a_athbox_15applets_plt_and_ioctl_audit.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(DEFAULT_OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            scope="offline static analysis; zero network traffic; zero radio contact; "
                  "no mtd access; .241/.242 never contacted",
            method="ET_EXEC program headers; non-PIC PLT stubs (lui $t7 / lw $t9 / jr $t9 / "
                   "addiu $t8) resolved through DT_JMPREL; $a1 resolved at each ioctl site by "
                   "backward slice (li / ori / lui+addiu / move-from-li); jal call graph to "
                   "depth 2",
            ioctl_name_caveat="SIOC names are attached only when the resolved request matches "
                              "a known value; the header that defines them was not read from "
                              "this image, so the mapping is INFERRED while the numeric "
                              "request itself is CONFIRMED",
            radio_safety="static only; no socket opened, no ioctl issued, no device touched",
        ),
        images=images,
        summary=dict(
            images=len(images),
            images_ok=len(ok),
            applets=first["applet_count"],
            plt_stubs=first["plt_stubs"],
            jal_resolved=first["jal_resolved"],
            jal_total=first["jal_total"],
            ioctl_sites=first["ioctl_sites"],
            ioctl_distinct_requests=len(first["ioctl_requests"]) +
                                    len(first["ioctl_requests_unnamed"]),
            ioctl_named=len(first["ioctl_requests"]),
            ioctl_unnamed=len(first["ioctl_requests_unnamed"]),
            ioctl_unresolved=first["ioctl_unresolved"],
            execution_sites=first["execution_total"],
            file_sink_sites=first["file_sink_total"],
            applets_with_ioctl=sum(1 for a in first["applets"] if a["ioctl_count"]),
            applets_with_execution=sum(1 for a in first["applets"] if a["execution_count"]),
            applets_with_radar_strings=sum(1 for a in first["applets"] if a["radar_strings"]),
        ),
        gaps=[
            "`$a1` is resolved only when it comes from an immediate or a move-from-immediate; "
            "requests loaded from a struct or computed at runtime stay null and are counted "
            "in ioctl_unresolved",
            "the SIOC constant-to-name mapping is INFERRED: it matches known Atheros values "
            "but the defining header was not extracted from this image",
            "depth is capped at 2 in the local jal graph; indirection through function "
            "pointers is not followed",
            "no dynamic validation: no ioctl was issued and no radio was contacted",
        ],
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[113A] applets={s['applets']} plt={s['plt_stubs']} "
          f"jal={s['jal_resolved']}/{s['jal_total']}")
    print(f"       ioctl_sites={s['ioctl_sites']} distinct={s['ioctl_distinct_requests']} "
          f"named={s['ioctl_named']} unnamed={s['ioctl_unnamed']} "
          f"unresolved={s['ioctl_unresolved']}")
    print(f"       execution={s['execution_sites']} file={s['file_sink_sites']} "
          f"applets_with_ioctl={s['applets_with_ioctl']} "
          f"applets_with_exec={s['applets_with_execution']}")
    for a in first["applets"]:
        print(f"       {a['name']:<16} {a['fn']} ioctl={a['ioctl_count']:<3} "
              f"exec={a['execution_count']:<2} file={a['file_sink_count']:<2} "
              f"reqs={a['ioctl_requests'][:4]}")
    print(f"[113A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
