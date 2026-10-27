#!/usr/bin/env python3
"""Stage 118A — full `ubntbox` audit: 29 applets, PLT stubs, process/file/IPC sinks.

Target reality check, recorded because the task named a different image:

  * the requested `WA.v8.7.11` / `XC.v8.7.11` rootfs trees **do not exist** in this
    repository. What exists for 8.7.11 is `artifacts/autoresearch/fwupdate.real.wa8711`
    and `artifacts/firmware_re_xc_ltu/2xc_8711_modules/*.ko` — no multicall binary.
  * the audited images are therefore `WA.v8.7.25` and `XC.v8.7.25`, which do ship
    `bin/ubntbox` (899,180 B each, and **not** byte-identical, unlike `athbox`).
  * three names in the task are not applets of `ubntbox`: `mcad` is a separate binary,
    `udapi-bridge` is a separate daemon, and the SNMP applet is called `snmp`, not
    `tinysnmpd`.

Import resolution is the non-PIC PLT pattern from W4D/113A:

    lui $t7, hi ; lw $t9, lo($t7) ; jr $t9 ; addiu $t8, $t7, lo

`target_got = (hi << 16) + sign_extend16(lo)`, named through `DT_JMPREL`. No `_gp` is
involved, so every attribution is deterministic.

For each applet the tool records, at depth 2 of the local `jal` graph:

  * **process sinks**: `system`, `popen`, `exec*`, `fork`, `waitpid`;
  * **file sinks**: `fopen`, `open`, `unlink`, `rename`, `chmod`, `stat`, `opendir`;
  * **shared-memory / IPC sinks**: `shmget`, `shmat`, `shmdt`, `shmctl`, `msgget`,
    `msgsnd`, `msgrcv`, `msgctl`, `semget`, `semop`, `semctl`, `mmap`, `munmap`,
    `mq_open`;
  * **network sinks**: `socket`, `connect`, `bind`, `listen`, `accept`, `sendto`.

Radio safety: static only. No socket is opened, `.241`/`.242` are never contacted, and no
`mtd` is touched.

Read-only: the only write is the receipt JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
IMAGES = {
    "WA.v8.7.25": FW / "wa_8725_rootfs/bin/ubntbox",
    "XC.v8.7.25": FW / "xc_8725_rootfs/bin/ubntbox",
}
DEFAULT_OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage118a_ubntbox_29applets_plt_and_sink_audit.json"

_spec = importlib.util.spec_from_file_location(
    "w4d", REPO_ROOT / "tools" / "re" / "audit_stage81a_w4d_wa_xc_standalone_elfs.py")
w4d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(w4d)

PROCESS = {"system", "popen", "execl", "execle", "execlp", "execv", "execve", "execvp",
           "fork", "vfork", "waitpid", "wait"}
FILE = {"fopen", "fopen64", "open", "open64", "openat", "creat", "unlink", "rename",
        "chmod", "fchmod", "chown", "symlink", "link", "truncate", "ftruncate",
        "stat", "lstat", "access", "opendir", "readdir"}
IPC = {"shmget", "shmat", "shmdt", "shmctl", "msgget", "msgsnd", "msgrcv", "msgctl",
       "semget", "semop", "semctl", "mmap", "munmap", "mq_open", "mq_send",
       "mq_receive", "pipe", "mkfifo"}
NETWORK = {"socket", "socketpair", "connect", "bind", "listen", "accept", "accept4",
           "sendto", "recvfrom", "sendmsg", "recvmsg", "setsockopt", "getsockopt"}

CATEGORIES = {"process": PROCESS, "file": FILE, "ipc_shared_memory": IPC, "network": NETWORK}


def collect(e: Any, fn: int, depth: int = 2) -> dict[str, Any]:
    found: dict[str, list[dict[str, Any]]] = {k: [] for k in CATEGORIES}
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
                for name, table in CATEGORIES.items():
                    if imp in table:
                        found[name].append(dict(site=f"0x{site:08x}", import_=imp,
                                                level=level))
                        break
        frontier = nxt
        if not frontier:
            break
    return found


def audit(e: Any) -> dict[str, Any]:
    groups = e.applets()
    applets = [a for g in groups for a in g["applets"]]
    rows = []
    for a in applets:
        c = collect(e, a["fn"])
        rows.append(dict(
            name=a["name"], fn=f"0x{a['fn']:08x}", entry_va=f"0x{a['entry_va']:08x}",
            extent=f"0x{e.extent(a['fn']):08x}",
            process=c["process"], process_count=len(c["process"]),
            file_sinks=c["file"], file_count=len(c["file"]),
            ipc=c["ipc_shared_memory"], ipc_count=len(c["ipc_shared_memory"]),
            network=c["network"], network_count=len(c["network"]),
        ))
    totals = {k: sum(r[f"{k}_count" if k != "ipc_shared_memory" else "ipc_count"]
                     for r in rows) for k in CATEGORIES}
    return dict(
        bytes=len(e.d), sha256=hashlib.sha256(e.d).hexdigest(),
        plt_stubs=len(e.plt), jal_total=len(e.calls),
        jal_resolved=sum(1 for c in e.calls if c[2]),
        imports=len(e.got), applet_tables=len(groups), applet_count=len(applets),
        applets=rows,
        totals=dict(process=totals["process"], file=totals["file"],
                    ipc_shared_memory=totals["ipc_shared_memory"],
                    network=totals["network"]),
        applets_with_process=[r["name"] for r in rows if r["process_count"]],
        applets_with_ipc=[r["name"] for r in rows if r["ipc_count"]],
        applets_with_file=[r["name"] for r in rows if r["file_count"]],
        import_universe=sorted(set(e.got.values())),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    images = []
    for label, path in IMAGES.items():
        if not path.exists():
            images.append(dict(image=label, status="absent"))
            continue
        e = w4d.Elf(path.read_bytes())
        images.append(dict(image=label, status="ok", **audit(e)))

    ok = [i for i in images if i.get("status") == "ok"]
    first = ok[0]
    report = dict(
        meta=dict(
            stage="118A", phase="118A", generated_utc="2026-10-26T00:00:00Z",
            repo_root=str(REPO_ROOT),
            tool="tools/re/audit_stage118a_ubntbox_29applets_plt_and_sink_audit.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(DEFAULT_OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            scope="offline static analysis; zero network traffic; zero radio contact; "
                  "no mtd access; .241/.242 never contacted",
            method="ET_EXEC program headers; non-PIC PLT stubs resolved through DT_JMPREL; "
                   "jal call graph to depth 2; sinks classified into process / file / "
                   "ipc_shared_memory / network",
            version_correction=[
                "WA.v8.7.11 and XC.v8.7.11 rootfs trees do not exist in this repository",
                "8.7.11 material present: artifacts/autoresearch/fwupdate.real.wa8711 and "
                "artifacts/firmware_re_xc_ltu/2xc_8711_modules/*.ko, with no multicall binary",
                "audited images are WA.v8.7.25 and XC.v8.7.25, which do ship bin/ubntbox",
            ],
            applet_name_corrections=[
                "mcad is a separate binary (bin/mcad), not an ubntbox applet",
                "udapi-bridge is a separate daemon, not an ubntbox applet",
                "the SNMP applet is named snmp, not tinysnmpd",
            ],
            radio_safety="static only; no socket opened, no device touched",
        ),
        images=images,
        summary=dict(
            images=len(images), images_ok=len(ok),
            applets=first["applet_count"],
            plt_stubs=first["plt_stubs"],
            jal_resolved=first["jal_resolved"], jal_total=first["jal_total"],
            process_sites=first["totals"]["process"],
            file_sites=first["totals"]["file"],
            ipc_sites=first["totals"]["ipc_shared_memory"],
            network_sites=first["totals"]["network"],
            applets_with_process=len(first["applets_with_process"]),
            applets_with_ipc=len(first["applets_with_ipc"]),
            applets_with_file=len(first["applets_with_file"]),
            images_identical=len({i["sha256"] for i in ok}) == 1,
        ),
        gaps=[
            "depth is capped at 2 in the local jal graph; function-pointer indirection is "
            "not followed",
            "sink attribution proves which import a handler can reach, not that its "
            "arguments are unvalidated",
            "the 8.7.11 build could not be audited: no ubntbox for that version exists here",
            "no dynamic validation: nothing was executed",
        ],
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[118A] images={s['images_ok']} applets={s['applets']} plt={s['plt_stubs']} "
          f"jal={s['jal_resolved']}/{s['jal_total']} identical={s['images_identical']}")
    print(f"       process={s['process_sites']} file={s['file_sites']} "
          f"ipc={s['ipc_sites']} network={s['network_sites']}")
    print(f"       applets_with_process={s['applets_with_process']} "
          f"ipc={s['applets_with_ipc']} file={s['applets_with_file']}")
    for a in first["applets"]:
        if a["process_count"] or a["ipc_count"] or a["file_count"]:
            print(f"       {a['name']:<16} proc={a['process_count']:<2} "
                  f"file={a['file_count']:<2} ipc={a['ipc_count']:<2} "
                  f"net={a['network_count']:<2}")
    print(f"[118A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
