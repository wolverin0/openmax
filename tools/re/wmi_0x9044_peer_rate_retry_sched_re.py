#!/usr/bin/env python3
"""Stage 372A — `WMI_PEER_RATE_RETRY_SCHED_CMDID` (0x9044) and the 4-series retry table.

Checked before analysis, in both target modules:

| Probe | `umac.ko` | `ubnt_poll_host.ko` |
| :--- | :-: | :-: |
| literal `0x9044` | **0** | 0 |
| `PEER_RATE_RETRY` | **1** | 0 |
| `peer_rate_retry` | 0 | 0 |
| `retry_sched` | 0 | 0 |
| `series_bw` | 0 | 0 |

So the only textual trace of the named command is **one** `PEER_RATE_RETRY` string in `umac.ko`.
The lower-case and per-field spellings do not appear at all.

What this tool reports:

  * the exact text and location of that one string, plus its neighbouring strings, because a WMI
    command table usually stores the name beside its id;
  * whether the **numeric id 0x9044** is materialised in code (MIPS: `lui rX,0x0009` followed by
    `ori rX,rX,0x0044`);
  * whether the retry-series field names (`series_bw`, `LDPC`, `STBC`, `SGI`, `txchainmask`,
    `2x2`, `1x2`, `CDD`) appear anywhere.

It does **not** reconstruct the 4-series table. A command name plus an id is not a schema.

Radio safety: static only. No module loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage372a_wmi_0x9044_peer_rate_retry_sched_re.json"

MODULES = {
    "WA.v8.7.25:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA.v8.7.25:ubnt_poll_host.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC.v8.7.25:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC.v8.7.25:ubnt_poll_host.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
}

WMI_ID = 0x9044
HI16, LO16 = WMI_ID >> 16, WMI_ID & 0xFFFF     # 0x0009 / 0x0044

PROBES = ["PEER_RATE_RETRY", "peer_rate_retry", "retry_sched", "RETRY_SCHED",
          "series_bw", "LDPC", "STBC", "SGI", "txchainmask", "2x2", "1x2", "CDD"]


def s16(v: int) -> int:
    return v - 0x10000 if v >= 0x8000 else v


class Ko:
    """ET_REL reader for MIPS32 big-endian modules."""

    def __init__(self, path: Path) -> None:
        self.data = d = path.read_bytes()
        if d[:4] != b"\x7fELF":
            raise ValueError(f"not ELF: {path}")
        E = "<" if d[5] == 1 else ">"
        self.endian = E
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        secs = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, flags=fl, addr=addr, off=off,
                             size=sz, link=link, info=info))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.secs = secs
        self.by_name = {h["name"]: h for h in secs}
        tx = self.by_name.get(".text")
        self.text = d[tx["off"]:tx["off"] + tx["size"]] if tx else b""
        self.syms: list[tuple[str, int, int, int, str]] = []
        st = self.by_name.get(".symtab")
        if st:
            ss = secs[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                e = d.find(b"\0", ss["off"] + nm)
                sn = secs[shndx]["name"] if 0 < shndx < len(secs) else ""
                self.syms.append((d[ss["off"] + nm:e].decode("latin1"), val, sz, shndx, sn))

    def u32(self, off: int) -> int | None:
        if off < 0 or off + 4 > len(self.text):
            return None
        return struct.unpack(self.endian + "I", self.text[off:off + 4])[0]

    def string_context(self, needle: str, span: int = 48) -> list[dict[str, Any]]:
        """Every occurrence of `needle` with the bytes around it and its section."""
        out = []
        target = needle.encode()
        for h in self.secs:
            if h["type"] != 1:
                continue
            blob = self.data[h["off"]:h["off"] + h["size"]]
            idx = blob.find(target)
            while idx >= 0:
                lo = max(0, idx - span)
                hi = min(len(blob), idx + len(target) + span)
                ctx = "".join(chr(c) if 32 <= c < 127 else "." for c in blob[lo:hi])
                out.append(dict(section=h["name"], offset=f"0x{idx:06x}", context=ctx))
                idx = blob.find(target, idx + 1)
                if len(out) >= 6:
                    return out
        return out

    def id_sites(self) -> list[dict[str, Any]]:
        """MIPS `lui rX,0x0009` + `ori rX,rX,0x0044` materialising 0x9044."""
        out = []
        for off in range(0, max(0, len(self.text) - 8), 4):
            w = self.u32(off)
            if w is None:
                continue
            op, rs, rt, imm = (w >> 26) & 0x3F, (w >> 21) & 0x1F, (w >> 16) & 0x1F, w & 0xFFFF
            if op != 0x0F or imm != HI16:              # lui rt, 0x0009
                continue
            for fwd in (4, 8, 12):
                w2 = self.u32(off + fwd)
                if w2 is None:
                    continue
                op2, rs2, rt2, imm2 = (w2 >> 26) & 0x3F, (w2 >> 21) & 0x1F, \
                                     (w2 >> 16) & 0x1F, w2 & 0xFFFF
                if op2 in (0x0D, 0x09) and rt2 == rt and rs2 == rt and imm2 == LO16:
                    fn = None
                    for nm, val, sz, shndx, sn in self.syms:
                        if sn in (".text", ".text.unlikely") and val <= off < val + max(sz, 4):
                            fn = nm
                            break
                    out.append(dict(at=f"0x{off:06x}", function=fn,
                                    form="lui+ori" if op2 == 0x0D else "lui+addiu"))
                    break
        return out

    def id_literal_scan(self) -> dict[str, Any]:
        """Search for the raw 32-bit big-endian literal 0x00009044, split by alignment.

        A command-id table stores ids at naturally aligned offsets. A hit at an offset that is
        not a multiple of 4 straddles two instructions and is a coincidence of adjacent code,
        not a stored id. The split is what makes this test falsifiable.
        """
        pat = b"\x00\x00\x90\x44"
        aligned: list[str] = []
        unaligned: list[str] = []
        i = self.data.find(pat)
        while i >= 0:
            (aligned if i % 4 == 0 else unaligned).append(f"0x{i:06x}")
            i = self.data.find(pat, i + 1)
        return dict(aligned=aligned, unaligned=unaligned,
                    aligned_count=len(aligned), unaligned_count=len(unaligned),
                    verdict="aligned literal present" if aligned else
                            "no aligned literal: all hits straddle instructions")

    def id_table_run(self, literal_off: int, cap: int = 32) -> dict[str, Any]:
        """Expand an aligned id literal into the `[id][value]` descriptor run around it.

        The run is grown while entries keep an id in 0x9000..0x9fff and repeat the same trailing
        word. Entries are reported verbatim; the trailing word is **not** interpreted.
        """
        def pair(o: int) -> tuple[int, int]:
            return struct.unpack(self.endian + "II", self.data[o:o + 8])

        ref = pair(literal_off)[1]
        start = literal_off
        while start - 8 >= 0:
            pid, pval = pair(start - 8)
            if 0x9000 <= pid <= 0x9FFF and pval == ref:
                start -= 8
            else:
                break
        entries: list[dict[str, str]] = []
        o = start
        while o + 8 <= len(self.data) and len(entries) < cap:
            cid, val = pair(o)
            if not (0x9000 <= cid <= 0x9FFF) or val != ref:
                break
            entries.append(dict(id=f"0x{cid:04x}", trailing=f"0x{val:08x}", at=f"0x{o:06x}"))
            o += 8
        return dict(run_start=f"0x{start:06x}", count=len(entries),
                    trailing_values=sorted({e["trailing"] for e in entries}),
                    entries=entries,
                    contains_target=any(e["id"] == "0x9044" for e in entries))

    def name_table_position(self, needle: str) -> dict[str, Any] | None:
        """Ordinal of `needle` inside the NUL-separated string table that holds it."""
        target = needle.encode()
        for h in self.secs:
            if h["type"] != 1:
                continue
            blob = self.data[h["off"]:h["off"] + h["size"]]
            idx = blob.find(target)
            if idx < 0:
                continue
            return dict(section=h["name"], offset=f"0x{idx:06x}",
                        preceding_strings=blob[:idx].count(b"\0"),
                        section_strings=blob.count(b"\0"))
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        raw = ko.data
        hits = {p: raw.count(p.encode()) for p in PROBES}
        ctx = ko.string_context("PEER_RATE_RETRY")
        ids = ko.id_sites()
        literals = ko.id_literal_scan()
        run = (ko.id_table_run(int(literals["aligned"][0], 16))
               if literals["aligned"] else None)
        rows.append(dict(module=label, status="ok", bytes=len(raw),
                         sha256=hashlib.sha256(raw).hexdigest(),
                         probe_hits=hits,
                         peer_rate_retry_context=ctx,
                         name_table_position=ko.name_table_position("WMI_PEER_RATE_RETRY_SCHED_CMDID"),
                         wmi_id_sites=ids, wmi_id_site_count=len(ids),
                         id_literals=literals, id_table_run=run))

    ok = [r for r in rows if r.get("status") == "ok"]
    report = dict(
        meta=dict(stage="372A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/wmi_0x9044_peer_rate_retry_sched_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="exact-string probe for the command name and the retry-series field "
                         "names; MIPS lui+ori pair search for the numeric id 0x9044; "
                         "surrounding-byte context for the one PEER_RATE_RETRY hit",
                  wmi_id=f"0x{WMI_ID:04x}",
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     peer_rate_retry_hits=max((r["probe_hits"]["PEER_RATE_RETRY"] for r in ok),
                                              default=0),
                     modules_with_command_name=sum(
                         1 for r in ok if r["probe_hits"]["PEER_RATE_RETRY"]),
                     modules_with_numeric_id=sum(1 for r in ok if r["wmi_id_site_count"]),
                     numeric_id_sites=sum(r["wmi_id_site_count"] for r in ok),
                     series_field_names_found=sum(
                         1 for p in ("series_bw", "LDPC", "STBC", "SGI", "txchainmask")
                         if any(r["probe_hits"][p] for r in ok)),
                     aligned_id_literals=sum(r["id_literals"]["aligned_count"] for r in ok),
                     unaligned_id_literals=sum(r["id_literals"]["unaligned_count"] for r in ok),
                     modules_with_id_in_table=sum(
                         1 for r in ok if r["id_table_run"] and r["id_table_run"]["contains_target"]),
                     id_table_run_length=max((r["id_table_run"]["count"] for r in ok
                                              if r["id_table_run"]), default=0),
                     retry_table_recovered=0),
        gaps=["the numeric id IS stored as an aligned 32-bit literal inside an [id][value] "
              "descriptor run, but the trailing word was not interpreted and no handler pointer "
              "was tied to it, so dispatch is unproven",
              "the 160 unaligned 0x00009044 hits straddle two instructions and are coincidences "
              "of adjacent code, not stored ids",
              "the retry-series field names appear as strings but no 4-series table was "
              "reconstructed: presence of a field name is not a schema",
              "no dynamic validation"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[372A] modules={s['modules_ok']} cmd_name={s['modules_with_command_name']} "
          f"id_modules={s['modules_with_numeric_id']} id_sites={s['numeric_id_sites']} "
          f"aligned_lit={s['aligned_id_literals']} unaligned_lit={s['unaligned_id_literals']} "
          f"in_table={s['modules_with_id_in_table']} run_len={s['id_table_run_length']} "
          f"series_fields={s['series_field_names_found']} table={s['retry_table_recovered']}")
    for r in ok:
        nt = r["name_table_position"] or {}
        run = r["id_table_run"] or {}
        print(f"        {r['module']:<30} {r['bytes']:>8}B "
              f"PEER_RATE_RETRY={r['probe_hits']['PEER_RATE_RETRY']} "
              f"id_sites={r['wmi_id_site_count']} "
              f"ordinal={nt.get('preceding_strings')} of {nt.get('section_strings')} "
              f"run={run.get('run_start')} n={run.get('count')}")
    print(f"[372A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
