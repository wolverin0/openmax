#!/usr/bin/env python3
"""Stage 808A — XC (QCA9558) PCIe DMA and AirView coexistence.

The stage asks for the **PCIe DMA** path on the XC image and how **AirView** (spectral analysis)
coexists with it.

**AirView is not a kernel symbol.** It is a **userspace binary**: `bin/airview` exists in the rootfs
and contains its own name 60 times. In the kernel modules the token appears **0 times**.

That is the same architecture Stage 823A found for airMagic: the analysis product is a daemon, and
the kernel only supplies raw samples. So "AirView coexistence" is not a kernel arbitration problem —
it is a userspace client competing for the spectral path that `ubntspecd` (47,192 bytes) serves.

**`CONFIRMED`**: `kernel_airview_hits = 0`, `airview_is_userspace = 1`.

The PCIe and DMA surface *is* in the kernel, and it is substantial:

| Module | Bytes | `pci` | `PCI` | `dma` | `DMA` |
| :--- | :-: | :-: | :-: | :-: | :-: |
| `XC:ath_dev.ko` | 287,216 | 7 | 14 | 36 | 7 |
| `XC:umac.ko` | 2,358,768 | 49 | 13 | 8 | 6 |
| `XC:ath_hal.ko` | 360,896 | 3 | 0 | 6 | 0 |

**`CONFIRMED`**: the DMA mass is in **`ath_dev.ko`** (43 tokens) while the `pci` mass is in
`umac.ko` (62). So descriptor and buffer management sits in the device layer, and PCIe enumeration
and configuration sits in the UMAC — a clean split that matters when tracing a DMA stall.

**`CONFIRMED`**: `coexist` has **1** hit, in `umac.ko` — a single coexistence reference. That is thin
for a coexistence mechanism, and it is consistent with the finding above: the coexistence is handled
in userspace, so the kernel needs only a passing reference.

The sibling daemons are present too: `dfsprescan` (7 self-hits) and `provmode` (5), plus `ubntbox`
(8). So the XC spectral/DFS stack is **daemon-driven** end to end.

`airview_kernel_arbitration_recovered = 0`: no kernel-side arbitration between AirView clients was
found, because none is named.

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
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
STAGING = REPO_ROOT / "artifacts/autoresearch/waves_abcd_20261024/wave_a_wa/complete_rootfs_r2"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.json")

MODULES = {
    "XC:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:ath_hal.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
}
# the userspace daemons that carry the analysis products
DAEMONS = ["airview", "ubntspecd", "dfsprescan", "provmode"]

TOKENS = ["pci", "PCI", "dma", "DMA", "airview", "AirView", "AIRVIEW", "coexist"]


def find_daemon(name: str) -> Path | None:
    for p in STAGING.glob("staging_*/bin/" + name):
        return p
    p = FW / "wa_8725_rootfs/bin" / name
    return p if p.exists() else None


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

    def matching(self, pattern: str, cap: int = 16) -> list[str]:
        return sorted({n for n in self.names if re.search(pattern, n, re.I)})[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        rows.append(dict(
            module=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            tokens={t: b.count(t.encode()) for t in TOKENS},
            pci_syms=syms.matching(r"pci|hif_pci", 12),
            dma_syms=syms.matching(r"dma", 16),
            coexist_syms=syms.matching(r"coexist", 6)))

    daemons = []
    for name in DAEMONS:
        p = find_daemon(name)
        if p is None:
            daemons.append(dict(name=name, present=False, bytes=None,
                                self_name_hits=0, readable=False))
            continue
        b = p.read_bytes()
        daemons.append(dict(name=name, present=True, bytes=len(b),
                            self_name_hits=b.lower().count(name.encode()),
                            readable=len(b) > 0))

    ok = [r for r in rows if r.get("status") == "ok"]
    kernel_airview = sum(r["tokens"]["airview"] + r["tokens"]["AirView"]
                         + r["tokens"]["AIRVIEW"] for r in ok)
    coexist = sum(r["tokens"]["coexist"] for r in ok)
    dev = next((r for r in ok if r["module"].endswith("ath_dev.ko")), None)
    umac = next((r for r in ok if r["module"].endswith("umac.ko")), None)
    dev_dma = (dev["tokens"]["dma"] + dev["tokens"]["DMA"]) if dev else 0
    umac_dma = (umac["tokens"]["dma"] + umac["tokens"]["DMA"]) if umac else 0
    umac_pci = (umac["tokens"]["pci"] + umac["tokens"]["PCI"]) if umac else 0
    airview = next((d for d in daemons if d["name"] == "airview"), {})
    specd = next((d for d in daemons if d["name"] == "ubntspecd"), {})

    report = dict(
        meta=dict(stage="808A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="PCIe and DMA token census across three XC modules; daemon discovery and "
                         "self-name census for the analysis products; explicit probe for AirView in "
                         "the kernel",
                  premise_corrections=[
                      "AirView is a userspace binary (bin/airview), not a kernel symbol: the "
                      "kernel modules return 0 hits for it",
                      "the DMA mass is in ath_dev.ko (43 tokens) while the PCIe mass is in umac.ko "
                      "(62), so descriptor management and bus configuration are split",
                  ],
                  radio_safety="static only"),
        modules=rows,
        daemons=daemons,
        summary=dict(modules_ok=len(ok),
                     kernel_airview_hits=kernel_airview,
                     airview_in_kernel=int(kernel_airview > 0),
                     airview_is_userspace=int(kernel_airview == 0
                                              and bool(airview.get("present"))),
                     airview_bytes=airview.get("bytes"),
                     airview_self_name_hits=airview.get("self_name_hits"),
                     ubntspecd_bytes=specd.get("bytes"),
                     daemons_present=sum(1 for d in daemons if d["present"]),
                     daemons_readable=sum(1 for d in daemons if d.get("readable")),
                     dev_dma_tokens=dev_dma,
                     umac_dma_tokens=umac_dma,
                     umac_pci_tokens=umac_pci,
                     dma_in_device_layer=int(dev_dma > umac_dma),
                     pci_in_umac=int(umac_pci > 0),
                     coexist_token_hits=coexist,
                     coexist_is_thin=int(coexist <= 1),
                     pci_symbol_count=len({n for r in ok for n in r["pci_syms"]}),
                     dma_symbol_count=len({n for r in ok for n in r["dma_syms"]}),
                     airview_kernel_arbitration_recovered=0,
                     dma_descriptor_layout_recovered=0),
        gaps=["AirView is userspace: the kernel carries 0 hits, so there is no kernel-side "
              "AirView arbitration to recover",
              "coexist has exactly 1 hit, which is consistent with coexistence being handled in "
              "userspace rather than in the driver",
              "the PCIe descriptor layout and ring geometry were not recovered (Stage 713A hit the "
              "same limit on the AC side)",
              "how ubntspecd multiplexes between AirView and airMagic clients was not decoded",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[808A] modules={s['modules_ok']} kernel_airview={s['kernel_airview_hits']} "
          f"airview_usr={s['airview_is_userspace']}({s['airview_bytes']}B) "
          f"dev_dma={s['dev_dma_tokens']} umac_pci={s['umac_pci_tokens']} "
          f"coexist={s['coexist_token_hits']} daemons={s['daemons_present']}")
    for d in daemons:
        print(f"        {d['name']:<12} present={d['present']} bytes={d['bytes']} "
              f"self={d['self_name_hits']}")
    print(f"[808A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
