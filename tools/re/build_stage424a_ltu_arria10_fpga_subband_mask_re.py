#!/usr/bin/env python3
"""Stage 424A — Arria 10 subband puncturing masks and tone-nulling ioctls in the LTU fabric.

The stage points at `firmware/extracted/af-ltu/`, expecting `ame_core.ko`, `eab_driver.ko` and
`libltu`, plus FPGA mask registers and tone-nulling ioctl handlers.

What the corpus holds, checked before any token work:

  * **`eab_driver.ko` does not exist** — 0 files. This is the fifth independent confirmation.
  * **`libltu` does not exist** — 0 files.
  * **no `af-ltu` tree exists** — 0 paths.
  * **no FPGA bitstream exists** — 0 `.rbf`, 0 `.sof`.
  * the LTU modules *are* present, under `ltu_extracted/afltu_2.4.2/.../3.14.65/`.

So the EAB interface is not a separate driver in this corpus. It is **compiled into `ame_core.ko`**,
which carries **359** `eab` tokens including real ISR and helper symbols.

The vocabulary, however, does not mean what the stage assumes:

  * **`subband` is OFDMA**, not an FPGA mask: every hit sits beside `ofdma_en`, `ofdma_start` and
    `ofdma_len` in the same log format string, as `ofdma_subband_type`;
  * **`mask`** has 2 hits, both `GEM queue intr mask` — an interrupt mask, not a puncturing mask;
  * **`null`** has 11 hits, all `null cpe %u qid %u sym %d last_cpe_null %u` — null-CPE
    scheduling, not tone nulling;
  * **`arria` and `fpga` appear 0 times** in the module.

The tool reports the EAB surface that is real, the three misreadings above with their contexts, and
the cross-reference to Stage 376A's 195 FPGA mailbox symbols — which is where the fabric control
actually lives.

Radio safety: static only. No module loaded, no radio contacted.
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
LTU = (REPO_ROOT / "artifacts/firmware_re_xc_ltu/ltu_extracted/afltu_2.4.2"
       / "rootfs_extracted/lib/modules/3.14.65")
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage424a_ltu_arria10_fpga_subband_mask_re.json")
PRIOR = (REPO_ROOT / "artifacts" / "autoresearch"
         / "stage376a_ltu_rocket_arria10_fpga_mailbox_re.json")

MODULE = "ame_core.ko"
TOKENS = ["eab", "EAB", "subband", "ofdma_subband_type", "punctur", "mask", "tone",
          "null", "notch", "arria", "fpga", "ioctl", "gem"]
MISSING = ["eab_driver.ko", "libltu", "af-ltu"]
BITSTREAMS = ["*.rbf", "*.sof"]


def ctx(b: bytes, tok: str, n: int = 3, w: int = 70) -> list[str]:
    out: list[str] = []
    needle = tok.encode()
    i = b.find(needle)
    while i >= 0 and len(out) < n:
        out.append("".join(chr(c) if 32 <= c < 127 else "."
                           for c in b[max(0, i - w):i + len(needle) + w]))
        i = b.find(needle, i + 1)
    return out


class Syms:
    def __init__(self, path: Path) -> None:
        self.data = d = path.read_bytes()
        E = "<" if d[5] == 1 else ">"
        shoff = struct.unpack(E + "I", d[32:36])[0]
        shent, shnum, shstr = struct.unpack(E + "HHH", d[46:52])
        secs = []
        for i in range(shnum):
            o = shoff + i * shent
            nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                E + "IIIIIIIIII", d[o:o + 40])
            secs.append(dict(name_off=nm, type=typ, off=off, size=sz, link=link))
        stro = secs[shstr]["off"]
        for h in secs:
            e = d.find(b"\0", stro + h["name_off"])
            h["name"] = d[stro + h["name_off"]:e].decode("latin1")
        self.secs = secs
        self.names: list[str] = []
        st = next((h for h in secs if h["name"] == ".symtab"), None)
        if st:
            ss = secs[st["link"]]
            for i in range(st["size"] // 16):
                o = st["off"] + i * 16
                nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", d[o:o + 16])
                if shndx == 0:
                    continue
                e = d.find(b"\0", ss["off"] + nm)
                self.names.append(d[ss["off"] + nm:e].decode("latin1"))

    def matching(self, pattern: str, cap: int = 60) -> list[str]:
        return sorted({n for n in self.names if re.search(pattern, n)})[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    absent = {n: len([p for p in (REPO_ROOT / "artifacts").rglob(n)]) for n in MISSING}
    bitstreams = {pat: len([p for p in (REPO_ROOT / "artifacts").rglob(pat) if p.is_file()])
                  for pat in BITSTREAMS}
    af_paths = [p for p in (REPO_ROOT / "artifacts").rglob("*af-ltu*")]
    af_dirs = sum(1 for p in af_paths if p.is_dir())
    af_files = [p for p in af_paths if p.is_file()]
    af_tokens: dict[str, int] = {}
    for f in af_files:
        try:
            raw = f.read_bytes()
        except OSError:
            continue
        for t in ("subband", "fpga", "mask", "tone", "eab", "arria"):
            af_tokens[t] = af_tokens.get(t, 0) + raw.count(t.encode())

    p = LTU / MODULE
    row: dict[str, Any] = dict(module=MODULE, status="absent")
    if p.exists():
        b = p.read_bytes()
        syms = Syms(p)
        row = dict(module=MODULE, status="ok", bytes=len(b),
                   sha256=hashlib.sha256(b).hexdigest(),
                   defined_symbols=len(syms.names),
                   tokens={t: b.count(t.encode()) for t in TOKENS},
                   contexts={t: ctx(b, t) for t in ("subband", "mask", "null", "eab")
                             if b.count(t.encode())},
                   eab_symbols=syms.matching(r"eab", 40),
                   no_tone_nullion=dict(tone=b.count(b"tone"), notch=b.count(b"notch"),
                                        punctur=b.count(b"punctur")))

    prior = None
    if PRIOR.exists():
        r = json.loads(PRIOR.read_text(encoding="utf-8"))
        prior = dict(path=PRIOR.relative_to(REPO_ROOT).as_posix(),
                     mailbox_symbol_count=r.get("fpga_mailbox_symbol_count"),
                     fabric=(r.get("dual_soc_fpga_architecture", {}) or {}).get(
                         "fpga_baseband_subsystem"),
                     partition_blobs=len(r.get("partition_blobs_inspected", []) or []))

    tok = row.get("tokens", {})
    report = dict(
        meta=dict(stage="424A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage424a_ltu_arria10_fpga_subband_mask_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="absence inventory for the named tree, driver, library and bitstreams; "
                         "token sweep of ame_core.ko with context; EAB symbol extraction; "
                         "cross-reference of the Stage 376A FPGA mailbox receipt",
                  premise_corrections=[
                      "eab_driver.ko, libltu and any af-ltu tree are absent; the EAB interface "
                      "is compiled into ame_core.ko, which carries 359 eab tokens",
                      "no FPGA bitstream exists (.rbf 0, .sof 0), so no mask register can be "
                      "read from a fabric image",
                  ],
                  radio_safety="static only"),
        absence=dict(names=absent, af_ltu_paths=len(af_paths), af_ltu_dirs=af_dirs,
                     af_ltu_config_files=len(af_files), af_ltu_tokens=af_tokens,
                     bitstreams=bitstreams),
        modules=[row],
        prior_art=prior,
        summary=dict(eab_driver_present=absent["eab_driver.ko"] > 0,
                     libltu_present=absent["libltu"] > 0,
                     af_ltu_tree_present=af_dirs > 0,
                     af_ltu_config_files=len(af_files),
                     af_ltu_subband_keys=af_tokens.get("subband", 0),
                     af_ltu_fpga_keys=af_tokens.get("fpga", 0),
                     bitstreams=sum(bitstreams.values()),
                     module_ok=int(row.get("status") == "ok"),
                     eab_tokens=tok.get("eab", 0),
                     eab_upper_tokens=tok.get("EAB", 0),
                     subband_tokens=tok.get("subband", 0),
                     ofdma_subband_type=tok.get("ofdma_subband_type", 0),
                     mask_tokens=tok.get("mask", 0),
                     null_tokens=tok.get("null", 0),
                     tone_tokens=tok.get("tone", 0),
                     puncture_tokens=tok.get("punctur", 0),
                     arria_tokens=tok.get("arria", 0),
                     fpga_tokens=tok.get("fpga", 0),
                     eab_symbol_count=len(row.get("eab_symbols", [])),
                     eab_symbols_sample=row.get("eab_symbols", [])[:12],
                     prior_mailbox_symbols=(prior or {}).get("mailbox_symbol_count"),
                     subband_mask_registers_recovered=0,
                     tone_null_ioctl_recovered=0),
        gaps=["eab_driver.ko does not exist, so the stage's named ioctl entry point has no bytes",
              "no FPGA bitstream exists, so no Arria 10 subband mask register can be read",
              "subband in ame_core.ko is OFDMA (ofdma_subband_type beside ofdma_en/start/len), "
              "not a puncturing mask",
              "the two mask hits are GEM interrupt masks; the eleven null hits are null-CPE "
              "scheduling, not tone nulling",
              "tone, notch and punctur appear 0 times in ame_core.ko",
              "the real fabric control surface is the EAB ISR/helper family in ame_core.ko and "
              "the 195 FPGA mailbox symbols recorded by Stage 376A, which this stage does not "
              "re-derive",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[424A] eab_driver={s['eab_driver_present']} libltu={s['libltu_present']} "
          f"af_ltu_dirs={s['af_ltu_tree_present']} cfg={s['af_ltu_config_files']} "
          f"bitstreams={s['bitstreams']} "
          f"eab={s['eab_tokens']} subband={s['subband_tokens']} "
          f"ofdma_type={s['ofdma_subband_type']} mask={s['mask_tokens']} null={s['null_tokens']} "
          f"tone={s['tone_tokens']} arria={s['arria_tokens']}")
    print(f"        cfg_keys subband={s['af_ltu_subband_keys']} fpga={s['af_ltu_fpga_keys']}")
    print(f"        eab_symbols={s['eab_symbol_count']} sample={s['eab_symbols_sample'][:5]}")
    print(f"        prior376a_mailbox={s['prior_mailbox_symbols']}")
    print(f"[424A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
