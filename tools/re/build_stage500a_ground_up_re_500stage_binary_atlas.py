#!/usr/bin/env python3
"""Stage 500A — the 500-stage Ground-Up Binary RE Atlas, derived from the receipts themselves.

This stage does **not** re-dissect binaries. Every number it publishes is read back out of the
`stage*_re.json` receipts this series produced, so the atlas cannot drift away from the evidence:

  * each receipt contributes its `meta.stage`, its `meta.tool`, and every module entry that carries
    a `bytes` and a `sha256`;
  * modules are grouped into **platform families** by the module filenames they contain;
  * duplicate work is removed by **SHA-256**, so the same `umac.ko` analysed by six stages counts
    once toward the byte total;
  * every `*_recovered` flag in every receipt is tallied, which yields a **recovery scorecard** —
    how many of the series' stated goals actually closed versus stayed `UNKNOWN`;
  * the two systemic corpus gaps (`firmware-2/5.bin`, `eab_driver.ko`) are counted rather than
    asserted.

An atlas that claims more than its receipts support is worthless, so the honest-output rule applies
here too: `families_recovered` counts what was **located**, and `gaps` states what never was.

Radio safety: static only. Nothing is opened except JSON the series already wrote.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
AR = REPO_ROOT / "artifacts" / "autoresearch"
OUT = AR / "stage500a_ground_up_re_500stage_binary_atlas.json"

# family inference by module filename; order matters (first match wins)
FAMILIES: list[tuple[str, str]] = [
    ("invictus_af", r"invictus|af4x|af5x|airfiber"),
    ("beetle_ltu", r"ame_core|ame_dev|ame_dfs|ame_radio|ame_gpio|cds_mac|ad9361|ltu"),
    ("ar9344_xw", r"xw_6|2\.6\.32\.71|ubnt_poll|ubnt_ewma|ath_spectral_xw"),
    ("qca988x_ac", r"umac\.ko|ath10k|qca988x|ath_hal|ath_dev|ath_spectral\.ko|ath_dfs|wa_8|xc_8"),
]


def family_of(module_names: list[str]) -> str:
    blob = " ".join(module_names).lower()
    for fam, pat in FAMILIES:
        if re.search(pat, blob):
            return fam
    return "unclassified"


def load(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    receipts = sorted(AR.glob("stage*_re.json"))
    entries: list[dict[str, Any]] = []
    modules_by_sha: dict[str, dict[str, Any]] = {}
    fam_receipts: Counter[str] = Counter()
    fam_bytes: Counter[int] = Counter()
    fam_modules: defaultdict[str, set[str]] = defaultdict(set)
    recovered: Counter[str] = Counter()
    unrecovered: Counter[str] = Counter()
    fw_absent = 0
    eab_absent = 0
    skipped: list[str] = []

    for p in receipts:
        r = load(p)
        if r is None:
            skipped.append(p.name)
            continue
        meta = r.get("meta", {}) or {}
        stage = meta.get("stage") or p.stem
        mods = [m for m in (r.get("modules") or []) if isinstance(m, dict)]
        names = [str(m.get("module") or m.get("version") or m.get("image") or "") for m in mods]
        # module names are the strongest signal; the receipt text is only a fallback for stages
        # that record findings without carrying a module with a sha256
        fam = family_of(names) if names else family_of([json.dumps(r)[:6000]])

        seen_sha = 0
        for m in mods:
            sha = m.get("sha256")
            size = m.get("bytes")
            if not sha or not isinstance(size, int):
                continue
            seen_sha += 1
            fam_modules[fam].add(str(m.get("module") or m.get("version") or m.get("image")))
            if sha not in modules_by_sha:
                modules_by_sha[sha] = dict(sha256=sha, bytes=size, family=fam,
                                           first_stage=stage,
                                           name=str(m.get("module") or m.get("version")
                                                    or m.get("image") or ""))

        fam_receipts[fam] += 1
        summary = r.get("summary", {}) or {}
        for k, v in summary.items():
            if not k.endswith("_recovered"):
                continue
            if v == 1 or v is True:
                recovered[k] += 1
            elif v == 0 or v is False:
                unrecovered[k] += 1

        text = json.dumps(r)
        if "firmware-2.bin" in text or "firmware-5.bin" in text:
            if '"firmware-2.bin": 0' in text or '"firmware-5.bin": 0' in text:
                fw_absent += 1
        if "eab_driver.ko" in text and '"eab_driver.ko": 0' in text:
            eab_absent += 1

        entries.append(dict(stage=stage, receipt=p.name, family=fam,
                            tool=meta.get("tool"), modules=len(mods),
                            sha_count=seen_sha,
                            bytes_analysed=sum(int(m["bytes"]) for m in mods
                                               if isinstance(m.get("bytes"), int)) ))

    entries.sort(key=lambda e: e["stage"])
    unique_bytes = sum(v["bytes"] for v in modules_by_sha.values())
    fam_summary = {f: dict(receipts=fam_receipts[f],
                           unique_modules=len(fam_modules[f]),
                           unique_bytes=sum(v["bytes"] for v in modules_by_sha.values()
                                            if v["family"] == f))
                   for f in sorted(fam_receipts)}

    report = dict(
        meta=dict(stage="500A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage500a_ground_up_re_500stage_binary_atlas.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; reads only the JSON receipts this series produced",
                  method="receipt read-back: per-stage modules with bytes+sha256, family "
                         "inference by module filename, SHA-256 de-duplication, and a tally of "
                         "every *_recovered flag declared by any stage",
                  note="the atlas is derived, not narrated: every figure below is a sum over "
                       "receipt fields",
                  radio_safety="static only"),
        stages=entries,
        families=fam_summary,
        unique_modules=sorted(modules_by_sha.values(), key=lambda m: (m["family"], m["name"])),
        recovered_flags={k: dict(present=recovered[k], absent=unrecovered[k])
                         for k in sorted(set(recovered) | set(unrecovered))},
        summary=dict(receipts_found=len(receipts),
                     receipts_parsed=len(entries),
                     receipts_unparsable=len(skipped),
                     stages_covered=len({e["stage"] for e in entries}),
                     families_present=sorted(fam_receipts),
                     family_count=len(fam_receipts),
                     unique_module_files=len(modules_by_sha),
                     unique_bytes_analysed=unique_bytes,
                     total_module_analyses=sum(e["modules"] for e in entries),
                     recovery_flags_declared=len(set(recovered) | set(unrecovered)),
                     recovery_flags_closed=len(recovered),
                     recovery_flags_open=len(unrecovered),
                     receipts_declaring_firmware_absent=fw_absent,
                     receipts_declaring_eab_driver_absent=eab_absent,
                     largest_module_bytes=max((v["bytes"] for v in modules_by_sha.values()),
                                              default=0),
                     atlas_complete=0),
        gaps=["the atlas only covers what the receipts recorded; a module never opened by any "
              "stage is absent from it",
              "firmware-2.bin and firmware-5.bin were never available, so no firmware-side claim "
              "appears anywhere in this atlas",
              "eab_driver.ko was never available either, which removes the entire EAB driver "
              "column from the LTU family",
              "several figures are name-level only (functions located, not decoded); the "
              "recovery scorecard counts goals closed, not depth of proof",
              "no AF-4X/5X firmware or rootfs exists, so the Invictus2 family contributes "
              "artefacts and receipts but no executable analysis",
              "no dynamic validation backs any entry"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[500A] receipts={s['receipts_found']}/{s['receipts_parsed']} "
          f"stages={s['stages_covered']} families={s['families_present']}")
    print(f"        unique_modules={s['unique_module_files']} "
          f"unique_bytes={s['unique_bytes_analysed']} "
          f"analyses={s['total_module_analyses']}")
    print(f"        recovered_flags closed={s['recovery_flags_closed']} "
          f"open={s['recovery_flags_open']} of {s['recovery_flags_declared']}")
    print(f"        fw_absent_in={s['receipts_declaring_firmware_absent']} "
          f"eab_absent_in={s['receipts_declaring_eab_driver_absent']}")
    for f, v in fam_summary.items():
        print(f"        {f:<14} receipts={v['receipts']:<3} modules={v['unique_modules']:<3} "
              f"bytes={v['unique_bytes']}")
    print(f"[500A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
