#!/usr/bin/env python3
"""Stage 388A — airFiber / LTU asymmetric TDD frame, cyclic prefix and strict timing.

Four things are asserted by the stage, and they resolve very differently:

  1. asymmetric TDD ratios **75/25**, **67/33**, **50/50** — as named values;
  2. cyclic prefix **cp = 4 / 8 / 16**;
  3. `stricttiming`;
  4. an AF4X Invictus firmware/rootfs to read them from.

What the artefacts actually contain:

  * **no AF4X / Invictus firmware or rootfs**. The name search returns PNG product images, a
    MIB text file and JSON receipts. Nothing executable.
  * the **AirFIBER MIB** has **no** TDD, cyclic-prefix or strict-timing objects — it is the
    Ethernet/radio configuration group.
  * the **LTU kernel modules do carry the frame parameters**, as attribute names rather than
    ratios: `duty_cycle`, `cpsample`, `frame_len`, `dl_symbols`, `ul_symbols`, `gap0`,
    `sync_mode`, `gps_sync_timeout`. `ame_core.ko` even exports `ame_bbp_get_duty_cycle`.
  * `ame_dfs.ko` **validates** duty against load: `duty cycle (%d%%) too low for %d%% traffic
    load`. That is a real behavioural constraint, not a table.

So the honest output is: the parameter names are recovered, the ratio table and the CP table are
not, and the product the stage names is absent from the corpus.

Radio safety: static only. No module loaded, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LTU = (REPO_ROOT / "artifacts/firmware_re_xc_ltu/ltu_extracted/afltu_2.4.2"
       / "rootfs_extracted/lib/modules/3.14.65")
MIB = (REPO_ROOT / "artifacts/firmware_re_xw_m5/xw_636_rootfs/usr/share/tinysnmp/mibs"
       / "UBNT-AirFIBER-MIB.txt")
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage388a_af4x_invictus2_tdd_cp_re.json"

MODULES = ["ame_core.ko", "ame_dev.ko", "ame_dfs.ko", "cds_mac_mod.ko", "ubnthal.ko"]

# the frame contract, as attribute names rather than ratios
PARAMS = ["duty_cycle", "cpsample", "frame_len", "dl_symbols", "ul_symbols", "gap0",
          "sync_mode", "gps_sync_timeout", "frame_period", "sample_rate"]

# the literal forms the stage asserts
RATIOS = ["75/25", "67/33", "50/50", "75:25", "67:33", "50:50"]
CP_LITERALS = ["cp=4", "cp=8", "cp=16", "cyclic prefix", "cp_len", "cp_prefix", "cyclic"]
STRICT = ["stricttiming", "strict_timing", "strict timing"]
TDD = ["TDD", "tdd"]


def ctx(b: bytes, tok: str, n: int = 3, w: int = 72) -> list[str]:
    out: list[str] = []
    needle = tok.encode()
    i = b.find(needle)
    while i >= 0 and len(out) < n:
        out.append("".join(chr(c) if 32 <= c < 127 else "."
                           for c in b[max(0, i - w):i + len(needle) + w]))
        i = b.find(needle, i + 1)
    return out


def inventory(skip: Path | None = None) -> list[dict[str, Any]]:
    """Every artefact whose name mentions the product family, excluding this receipt.

    The receipt is excluded because its own filename contains `invictus`: including it would make
    the run non-deterministic, since on the first run the file does not yet exist.
    """
    out = []
    skip_r = skip.resolve() if skip is not None else None
    for p in (REPO_ROOT / "artifacts").rglob("*"):
        if not p.is_file():
            continue
        if skip_r is not None and p.resolve() == skip_r:
            continue
        low = p.name.lower()
        if any(k in low for k in ("invictus", "airfiber")) or low.startswith(("af4", "af5")):
            out.append(dict(path=p.relative_to(REPO_ROOT).as_posix(),
                            bytes=p.stat().st_size, suffix=p.suffix.lower()))
    return sorted(out, key=lambda r: r["path"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for name in MODULES:
        p = LTU / name
        if not p.exists():
            rows.append(dict(module=name, status="absent"))
            continue
        d = p.read_bytes()
        params = {k: d.count(k.encode()) for k in PARAMS}
        rows.append(dict(module=name, status="ok", bytes=len(d),
                         sha256=hashlib.sha256(d).hexdigest(),
                         params={k: v for k, v in params.items() if v},
                         param_contexts={k: ctx(d, k, 2) for k, v in params.items() if v},
                         ratios={k: d.count(k.encode()) for k in RATIOS},
                         cp_literals={k: d.count(k.encode()) for k in CP_LITERALS},
                         strict={k: d.count(k.encode()) for k in STRICT},
                         tdd={k: d.count(k.encode()) for k in TDD},
                         tdd_contexts=ctx(d, "TDD", 2),
                         duty_warn=dict(count=d.count(b"too low for"),
                                        contexts=ctx(d, "too low for", 2, 90))))

    mib = None
    if MIB.exists():
        raw = MIB.read_bytes()
        text = raw.decode("latin1")
        mib = dict(path=MIB.relative_to(REPO_ROOT).as_posix(), bytes=len(raw),
                   sha256=hashlib.sha256(raw).hexdigest(),
                   object_types=len(re.findall(r"OBJECT-TYPE", text)),
                   revision=next(iter(re.findall(r'REVISION\s+"([^"]+)"', text)), None),
                   tdd=len(re.findall(r"(?i)\btdd\b", text)),
                   cyclic=len(re.findall(r"(?i)cyclic", text)),
                   strict=len(re.findall(r"(?i)strict", text)),
                   duty=len(re.findall(r"(?i)duty", text)))

    ok = [r for r in rows if r.get("status") == "ok"]
    inv = inventory(args.out)
    firmware = [r for r in inv if r["suffix"] in (".bin", ".img", ".fw", ".tar", ".gz",
                                                  ".ipk", ".ko")]
    ratio_hits = sum(sum(m["ratios"].values()) for m in ok)
    cp_hits = sum(sum(m["cp_literals"].values()) for m in ok)
    strict_hits = sum(sum(m["strict"].values()) for m in ok)

    report = dict(
        meta=dict(stage="388A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/af4x_invictus2_fpga_tdd_cyclic_prefix_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  premise_corrections=[
                      "no AF4X / Invictus firmware or rootfs exists in the corpus: the name "
                      "search returns PNG product images, one MIB and JSON receipts",
                      "the AirFIBER MIB carries no TDD, cyclic-prefix or strict-timing object, so "
                      "the documented contract is not available either",
                  ],
                  radio_safety="static only"),
        modules=rows,
        mib=mib,
        inventory=inv,
        summary=dict(modules_ok=len(ok),
                     modules_with_duty_cycle=sum(1 for m in ok if m["params"].get("duty_cycle")),
                     modules_with_cpsample=sum(1 for m in ok if m["params"].get("cpsample")),
                     modules_with_frame_symbols=sum(1 for m in ok
                                                    if m["params"].get("dl_symbols")),
                     param_names_found=len({k for m in ok for k, v in m["params"].items() if v}),
                     ratio_string_hits=ratio_hits,
                     cp_literal_hits=cp_hits,
                     strict_timing_hits=strict_hits,
                     tdd_token_hits=sum(sum(m["tdd"].values()) for m in ok),
                     modules_with_duty_validation=sum(1 for m in ok
                                                      if m["duty_warn"]["count"]),
                     mib_object_types=(mib or {}).get("object_types", 0),
                     mib_tdd_objects=(mib or {}).get("tdd", 0),
                     airfiber_artifacts=len(inv),
                     airfiber_firmware_binaries=len(firmware),
                     ratio_table_recovered=0,
                     cp_table_recovered=0),
        gaps=["no 75/25, 67/33 or 50/50 ratio appears anywhere in the LTU module set",
              "the cyclic prefix exists as `cpsample` and nothing else: no cp=4/8/16 enumeration "
              "and no CP table was recovered",
              "the single `TDD` token in ame_core.ko sits inside the mangled symbol fragment "
              "`bbp_mrx_foe_TDDeRotCFO`, not in any frame-control context",
              "stricttiming appears in no artefact, so its default and its effect are unknown",
              "the ratio and CP are runtime values: `duty_cycle` and `cpsample` are attribute "
              "names, and no numeric table was bound to them",
              "no AF4X/Invictus image exists to read, so the airFiber side of the stage cannot be "
              "answered from this corpus at all",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[388A] modules={s['modules_ok']} duty={s['modules_with_duty_cycle']} "
          f"cpsample={s['modules_with_cpsample']} sym={s['modules_with_frame_symbols']} "
          f"names={s['param_names_found']} ratios={s['ratio_string_hits']} "
          f"cp_lit={s['cp_literal_hits']} strict={s['strict_timing_hits']} "
          f"tdd={s['tdd_token_hits']}")
    print(f"        mib_objs={s['mib_object_types']} mib_tdd={s['mib_tdd_objects']} "
          f"artifacts={s['airfiber_artifacts']} firmware={s['airfiber_firmware_binaries']}")
    for m in ok:
        print(f"        {m['module']:<16} {m['bytes']:>8}B params={sorted(m['params'])}")
    print(f"[388A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
