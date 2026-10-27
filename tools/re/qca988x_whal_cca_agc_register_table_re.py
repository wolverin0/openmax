#!/usr/bin/env python3
"""Stage 373A — QCA988x WHAL analog CCA/AGC register tables and the Xtensa SGMT payload.

Two artefacts, two very different kinds of evidence:

  * `openwrt_qca988x_hw20_firmware_2_ct.bin` — the Xtensa firmware container. It parses cleanly,
    and two of its five TLVs carry an `SGMT`-tagged payload.
  * `ath_hal.ko` / `ath_dev.ko` / `umac.ko` — the host HAL. This is where the WHAL parameter
    **names** actually live (`cca_thresh`, `nf_cal`, `noise_floor`, `strong_signal`, `firstep`,
    `cycpwr`).

What this tool establishes:

  * the container layout, verified by **tiling**: the TLV chain must consume the file down to a
    tiny tail pad, otherwise the parser is wrong;
  * the exact `SGMT` payload prefix, identical across both segments except one u32;
  * which module carries which WHAL token, with string context.

What it refuses to claim:

  * that any numeric array inside an SGMT payload is a CCA/AGC register table. Firmware payloads
    carry no names; a run of small integers is not a register table until it is mapped.
  * that `cca_thresh` being present means the PB040 override is live. A name is a name.

`analog_register_table_recovered = 0` and `name_to_register_map = 0` are the honest outputs.

Radio safety: static only. No firmware loaded, no module loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5" / "xw_636_rootfs" / "lib" / "modules" / "2.6.32.71"
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage373a_qca988x_whal_cca_agc_re.json"

CONTAINER = FW / "openwrt_qca988x_hw20_firmware_2_ct.bin"

MODULES = {
    "WA:ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:ath_hal.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "XW:ath_hal.ko": XW / "ath_hal.ko",
}

# the five WHAL parameters the stage names, plus their shorter spellings
TOKENS = ["cca_thresh", "thresh62", "nf_cal", "noise_floor", "strong_signal",
          "firstep", "cycpwr_thr1", "cycpwr", "cca", "agc"]

MAGIC = b"QCA-ATH10K"


def parse_container(blob: bytes) -> dict[str, Any]:
    """Parse `QCA-ATH10K` + u32 version_len + version + (u32 id, u32 len, payload)*.

    The parse is only accepted if it tiles: the chain must end within 16 bytes of EOF.
    """
    if not blob.startswith(MAGIC):
        return dict(parsed=False, reason="magic mismatch")
    vlen = struct.unpack("<I", blob[16:20])[0]
    version = blob[20:20 + vlen].decode("latin1")
    off = 20 + vlen
    ies: list[dict[str, Any]] = []
    while off + 8 <= len(blob):
        ie_id, ie_len = struct.unpack("<II", blob[off:off + 8])
        if off + 8 + ie_len > len(blob) or ie_len > len(blob):
            break
        payload = blob[off + 8:off + 8 + ie_len]
        ies.append(dict(id=ie_id, len=ie_len, at=f"0x{off:06x}",
                        tag=payload[:4].decode("latin1", "replace"),
                        head=payload[:16].hex(),
                        at_offset_12=(struct.unpack("<I", payload[12:16])[0]
                                      if ie_len >= 16 else None)))
        off += 8 + ie_len
    tail = len(blob) - off
    return dict(parsed=True, magic=MAGIC.decode(), version_len=vlen, version=version,
                ie_count=len(ies), ies=ies, end=f"0x{off:06x}", file_len=len(blob),
                tail_pad=tail, tiled=0 <= tail < 16,
                sgmt=[ie for ie in ies if ie["tag"] == "SGMT"])


class Ko:
    """Minimal ELF section reader, enough to attribute a byte hit to a section."""

    def __init__(self, path: Path) -> None:
        self.data = d = path.read_bytes()
        E = "<" if d[5] == 1 else ">"
        self.endian = E
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        self.secs: list[dict[str, Any]] = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            self.secs.append(dict(name_off=nm, type=typ, off=off, size=sz))
        if shnum:
            stro = self.secs[shstr]["off"]
            for h in self.secs:
                e = d.find(b"\0", stro + h["name_off"])
                h["name"] = d[stro + h["name_off"]:e].decode("latin1")

    def section_of(self, pos: int) -> str:
        for h in self.secs:
            if h["off"] <= pos < h["off"] + h["size"] and h["type"] == 1:
                return h["name"]
        return ""

    def token_sweep(self, tokens: list[str], max_contexts: int = 3) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for tok in tokens:
            needle = tok.encode()
            n = self.data.count(needle)
            if not n:
                continue
            ctxs: list[dict[str, str]] = []
            i = self.data.find(needle)
            while i >= 0 and len(ctxs) < max_contexts:
                lo, hi = max(0, i - 72), min(len(self.data), i + len(needle) + 72)
                raw = self.data[lo:hi]
                ctxs.append(dict(section=self.section_of(i), at=f"0x{i:06x}",
                                 context="".join(chr(c) if 32 <= c < 127 else "."
                                                 for c in raw)))
                i = self.data.find(needle, i + 1)
            out[tok] = dict(count=n, contexts=ctxs)
        return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    container = None
    if CONTAINER.exists():
        blob = CONTAINER.read_bytes()
        container = dict(path=str(CONTAINER.relative_to(REPO_ROOT)).replace("\\", "/"),
                         bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
                         token_sweep={t: blob.count(t.encode()) for t in TOKENS},
                         **parse_container(blob))

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        ko = Ko(path)
        sweep = ko.token_sweep(TOKENS)
        rows.append(dict(module=label, status="ok", bytes=len(ko.data),
                         sha256=hashlib.sha256(ko.data).hexdigest(),
                         tokens=sweep, token_count=len(sweep)))

    ok = [r for r in rows if r.get("status") == "ok"]
    sgmt = container["sgmt"] if container else []
    report = dict(
        meta=dict(stage="373A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/qca988x_whal_cca_agc_register_table_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware loaded, no module loaded, "
                        "no radio contacted",
                  method="container TLV parse accepted only if it tiles; SGMT payload prefix "
                         "fingerprint; raw token sweep over the HAL modules with section "
                         "attribution and string context",
                  radio_safety="static only"),
        container=container,
        modules=rows,
        summary=dict(container_parsed=bool(container and container["parsed"]),
                     container_tiled=bool(container and container["tiled"]),
                     tlvs=max((container["ie_count"] if container else 0), 0),
                     sgmt_segments=len(sgmt),
                     sgmt_bytes=sum(ie["len"] for ie in sgmt),
                     sgmt_prefixes=[ie["head"][:24] for ie in sgmt],
                     sgmt_u32_at_12=[ie["at_offset_12"] for ie in sgmt],
                     modules_ok=len(ok),
                     modules_with_whal_tokens=sum(1 for r in ok if r["token_count"]),
                     cca_thresh_modules=sum(1 for r in ok if "cca_thresh" in r["tokens"]),
                     firstep_modules=sum(1 for r in ok if "firstep" in r["tokens"]),
                     cycpwr_modules=sum(1 for r in ok if "cycpwr" in r["tokens"]),
                     nf_cal_modules=sum(1 for r in ok if "nf_cal" in r["tokens"]),
                     firmware_whal_tokens=sum((container or {}).get("token_sweep", {}).values()),
                     analog_register_table_recovered=0,
                     name_to_register_map=0),
        gaps=["the SGMT payloads carry no parameter names; no numeric array inside them was "
              "mapped to a WHAL register, so the CCA/AGC table is not recovered",
              "the u32 at SGMT payload offset 12 differs between the two segments (148 vs 5484) "
              "and was not interpreted",
              "the WHAL token names live in ath_hal.ko and umac.ko, not in the firmware blob, so "
              "presence of a name and presence of a table are separate facts",
              "no Xtensa disassembly was performed",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[373A] container={s['container_parsed']} tiled={s['container_tiled']} "
          f"tlvs={s['tlvs']} sgmt={s['sgmt_segments']} sgmt_bytes={s['sgmt_bytes']} "
          f"u32@12={s['sgmt_u32_at_12']}")
    print(f"        modules={s['modules_ok']} whal={s['modules_with_whal_tokens']} "
          f"cca_thresh={s['cca_thresh_modules']} firstep={s['firstep_modules']} "
          f"cycpwr={s['cycpwr_modules']} nf_cal={s['nf_cal_modules']} table=0")
    for r in ok:
        print(f"        {r['module']:<16} {r['bytes']:>8}B tokens={sorted(r['tokens'])}")
    print(f"[373A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
