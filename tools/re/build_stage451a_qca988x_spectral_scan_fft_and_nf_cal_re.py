#!/usr/bin/env python3
"""Stage 451A — spectral scan FFT bin packer, WMI spectral commands, periodic NF calibration.

The stage names four things:

  * the **FFT bin packer**;
  * `WMI_PDEV_SPECTRAL_SCAN_CONFIGURE_CMDID` and `..._ENABLE_CMDID`;
  * **periodic noise-floor calibration**;
  * the sources `firmware-2.bin` / `firmware-5.bin` and `ath_dev.ko`.

Two of those sources do not exist: both firmware images are **absent** (Stages 423A, 437A). The
vendor modules are read instead, and the spectral surface turns out to be **split across three** of
them, which is itself the finding:

  * `ath_spectral.ko` owns the **FFT and NF maths** — `get_fft_bin_count`,
    `process_search_fft_report`, `dump_search_fft_report`, `spectral_dump_fft`,
    `spectral_get_noise_power`, `adjust_rssi_with_nf_dbm`, `get_nfc_ctl_rssi`, `get_nfc_ext_rssi`;
  * `ath_dev.ko` owns the **enable path** — `spectral_scan_enable`,
    `spectral_scan_enable_params`, `spectral_check_hw_capability`, `spectral_detach`;
  * `umac.ko` carries the WMI plumbing.

And one trap is worth naming up front: `bin_` in `umac.ko` is **not** an FFT bin. Every hit is a
**firmware blob**: `ol_transfer_bin_file`, `otp_AR9888v2_bin_len`,
`athwlan_AR9888v2_ptmp_sta_bin_len`. The tool classifies those separately so they cannot be
mistaken for the packer.

`fft_bin_format_recovered = 0` and `nf_cal_table_recovered = 0`: the routines are located and
named, the byte layout and the calibration table are not.

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
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage451a_qca988x_spectral_scan_fft_and_nf_cal_re.json")

MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "WA:ath_spectral.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_spectral.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC:ath_spectral.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_spectral.ko",
}

TOKENS = ["SPECTRAL", "spectral", "FFT", "fft", "nf_cal", "noise_floor",
          "scan_enable", "bin_", "PDEV_SPECTRAL", "VDEV_SPECTRAL", "SPECTRAL_SCAN"]

# the two command names the stage asks for, and the prefix variant actually present
COMMANDS = ["WMI_PDEV_SPECTRAL_SCAN_CONFIGURE_CMDID",
            "WMI_PDEV_SPECTRAL_SCAN_ENABLE_CMDID",
            "WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID",
            "WMI_VDEV_SPECTRAL_SCAN_ENABLE_CMDID"]

# symbols that belong to the bin packer, the NF calibration, and the enable path
PACKER = r"fft|bin_count|search_report|dump_search"
NFCAL = r"noise|nf_|nfc_|rssi_with_nf"
ENABLE = r"scan_enable|scan_capab|spectral_detach|spectral_attach"

# a `bin_` hit is a firmware blob if its context names one of these
BLOB_MARKERS = ("bin_len", "ol_transfer", "AR9888v2", "otp_")


def ctx(b: bytes, tok: str, n: int = 4, w: int = 68) -> list[str]:
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

    def matching(self, pattern: str, cap: int = 30) -> list[str]:
        return sorted({n for n in self.names if re.search(pattern, n, re.I)})[:cap]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    fw_images = {n: len([p for p in (REPO_ROOT / "artifacts").rglob(n) if p.is_file()])
                 for n in ("firmware-2.bin", "firmware-5.bin")}

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        bin_ctx = ctx(b, "bin_")
        rows.append(dict(
            module=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            tokens={t: b.count(t.encode()) for t in TOKENS},
            commands={c: b.count(c.encode()) for c in COMMANDS},
            bin_contexts=bin_ctx,
            bin_is_firmware_blob=bool(bin_ctx) and all(
                any(m in c for m in BLOB_MARKERS) for c in bin_ctx),
            packer_symbols=syms.matching(PACKER, 20),
            nfcal_symbols=syms.matching(NFCAL, 20),
            enable_symbols=syms.matching(ENABLE, 20),
            spectral_symbols=syms.matching(r"spectral", 20)))

    ok = [r for r in rows if r.get("status") == "ok"]
    packer = sorted({n for r in ok for n in r["packer_symbols"]})
    nfcal = sorted({n for r in ok for n in r["nfcal_symbols"]})
    enable = sorted({n for r in ok for n in r["enable_symbols"]})
    wmi_hits = sum(r["tokens"]["PDEV_SPECTRAL"] + r["tokens"]["SPECTRAL_SCAN"] for r in ok)
    pdev_hits = sum(r["tokens"]["PDEV_SPECTRAL"] for r in ok)
    vdev_hits = sum(r["tokens"]["VDEV_SPECTRAL"] for r in ok)
    start_cmds = sum(r["commands"]["WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID"] +
                     r["commands"]["WMI_VDEV_SPECTRAL_SCAN_ENABLE_CMDID"] for r in ok)
    wrong_cmds = sum(r["commands"]["WMI_PDEV_SPECTRAL_SCAN_CONFIGURE_CMDID"] +
                     r["commands"]["WMI_PDEV_SPECTRAL_SCAN_ENABLE_CMDID"] for r in ok)
    spectral_hits = sum(r["tokens"]["spectral"] for r in ok)
    blob_bins = sum(1 for r in ok if r["bin_is_firmware_blob"])

    report = dict(
        meta=dict(stage="451A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage451a_qca988x_spectral_scan_fft_and_nf_cal_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware loaded, no module loaded, "
                        "no radio contacted",
                  method="string census across the three spectral modules; defined-symbol "
                         "lookup for the fft/bin-count, nf-cal and scan-enable families; "
                         "context classification separating FFT bins from firmware blobs",
                  premise_corrections=[
                      "firmware-2.bin and firmware-5.bin are absent, so no FFT bin layout can be "
                      "read from a firmware image",
                      "the command names exist but with a VDEV prefix, not PDEV: umac.ko carries "
                      "WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID and ..._ENABLE_CMDID, and "
                      "PDEV_SPECTRAL has 0 hits",
                      "bin_ in umac.ko is not an FFT bin: every hit is a firmware blob name "
                      "(ol_transfer_bin_file, otp_AR9888v2_bin_len, athwlan_..._bin_len)",
                  ],
                  radio_safety="static only"),
        firmware_images=fw_images,
        modules=rows,
        summary=dict(firmware_images_present=sum(fw_images.values()),
                     modules_ok=len(ok),
                     spectral_token_hits=spectral_hits,
                     wmi_spectral_name_hits=wmi_hits,
                     pdev_spectral_hits=pdev_hits,
                     vdev_spectral_hits=vdev_hits,
                     pdev_prefix_refuted=int(pdev_hits == 0 and vdev_hits > 0),
                     wmi_vdev_command_hits=start_cmds,
                     wmi_pdev_command_hits=wrong_cmds,
                     wmi_spectral_names_absent=(pdev_hits == 0 and vdev_hits == 0),
                     packer_symbols=packer,
                     packer_symbol_count=len(packer),
                     nfcal_symbols=nfcal,
                     nfcal_symbol_count=len(nfcal),
                     enable_symbols=enable,
                     enable_symbol_count=len(enable),
                     modules_with_bin_as_blob=blob_bins,
                     fft_packer_located=int(bool(packer)),
                     nf_cal_located=int(bool(nfcal)),
                     scan_enable_located=int(bool(enable)),
                     fft_bin_format_recovered=0,
                     nf_cal_table_recovered=0),
        gaps=["firmware-2.bin and firmware-5.bin are absent, so the FFT bin byte layout cannot be "
              "read from the image the stage names",
              "the spectral commands are per-VDEV, not per-PDEV: the stage's WMI_PDEV_* names have "
              "0 hits while WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID and ..._ENABLE_CMDID are real, "
              "so the scan is configured per virtual interface",
              "get_fft_bin_count is located by name, but its return domain (32/64/128/256/512) was "
              "not read; Stage 327A found 32/64/256/512 as immediates and 128 absent",
              "the NF calibration routines are named, but no dBm offset table or interpolation "
              "curve was recovered",
              "bin_ in umac.ko belongs to firmware download, not to the spectral packer",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[451A] fw={s['firmware_images_present']} modules={s['modules_ok']} "
          f"spectral={s['spectral_token_hits']} wmi_names={s['wmi_spectral_name_hits']} "
          f"packer={s['packer_symbol_count']} nfcal={s['nfcal_symbol_count']} "
          f"enable={s['enable_symbol_count']} blob_bins={s['modules_with_bin_as_blob']}")
    print(f"        packer: {packer}")
    print(f"        nfcal : {nfcal}")
    print(f"        enable: {enable}")
    print(f"[451A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
