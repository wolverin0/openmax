#!/usr/bin/env python3
"""Stage 374A — AirSelect frequency-hop state machine across the polling modules.

The stage asks for the state machine inside `ubnt_poll_host.ko` on WA, XC and XW. Two structural
facts have to be reported before anything else:

  * **XW has no `ubnt_poll_host.ko`.** The 2.6.32.71 module tree ships `ubnt_poll.ko`
    (529,284 bytes) instead — a different name and 2.8x the size. Any "WA/XC/XW" comparison has
    to state which module is standing in for XW.
  * **`ubnt_poll_host.ko` carries no AirSelect vocabulary.** Zero hits for `airselect`,
    `hop_interval`, `hopint`, `dwell`, `announce`, `chanchange`, `athselect`.

Shipped AirSelect documentation exists, and it is precise: the web help pages define the hop
interval (default **3000 ms**), the announce-count semantics and the frequency list. So the
feature is real, documented and configurable — it is just not implemented under this name in the
module the stage names.

What this tool establishes:

  * per-module token surface, with string context, for the AirSelect vocabulary;
  * the documented contract, parsed from the help pages rather than assumed;
  * where the vocabulary does appear in userspace (library, translations, MIB), and where it
    does not (any binary under `usr/bin` / `usr/sbin`).

`state_machine_recovered = 0` is the honest output: no hop timer, no channel list walk and no
announcement scheduler was decoded.

Radio safety: static only. No module loaded, no radio contacted, nothing hopped.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
XW = REPO_ROOT / "artifacts" / "firmware_re_xw_m5" / "xw_636_rootfs" / "lib" / "modules" / "2.6.32.71"
OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage374a_ubnt_airselect_state_machine_re.json"

STAGING = REPO_ROOT / "artifacts/autoresearch/waves_abcd_20261024/wave_a_wa/complete_rootfs_r2"

MODULES = {
    "WA.v8.7.25:ubnt_poll_host.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XC.v8.7.25:ubnt_poll_host.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko",
    "XW.v6.3.6:ubnt_poll.ko": XW / "ubnt_poll.ko",
}

# the name the stage says XW should have; probed separately so its absence is a recorded fact
XW_EXPECTED = XW / "ubnt_poll_host.ko"

TOKENS = ["airselect", "AirSelect", "AIRSELECT", "hop_interval", "hopint", "hop",
          "dwell", "announce", "chanchange", "channel_change", "athselect",
          "airmax", "csa", "chan_switch",
          # the actual vocabulary: on XW the feature is implemented as `fh` (frequency hopping)
          "fh_list", "fh_hops", "fh_retries", "fh_time", "fh_announce_cnt", "fh_",
          "tx_sync_master", "tx_sync_mode", "chanidx",
          "hopping to chanidx", "failed hop to freq", "channel change announce"]

HELP = ("airselect.html", "airselectacount.html", "airselectflist.html", "airselecthopint.html")


def token_sweep(blob: bytes, tokens: list[str], cap: int = 3) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for tok in tokens:
        needle = tok.encode()
        n = blob.count(needle)
        if not n:
            continue
        ctxs = []
        i = blob.find(needle)
        while i >= 0 and len(ctxs) < cap:
            lo, hi = max(0, i - 44), min(len(blob), i + len(needle) + 44)
            ctxs.append(dict(at=f"0x{i:06x}",
                             context="".join(chr(c) if 32 <= c < 127 else "."
                                             for c in blob[lo:hi])))
            i = blob.find(needle, i + 1)
        out[tok] = dict(count=n, contexts=ctxs)
    return out


def help_dir() -> Path | None:
    for cand in STAGING.glob("staging_*/usr/www/help/en_US"):
        if cand.is_dir():
            return cand
    return None


def parse_help(base: Path) -> list[dict[str, Any]]:
    docs = []
    for name in HELP:
        p = base / name
        if not p.exists():
            docs.append(dict(doc=name, status="absent"))
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s+", " ", text).strip()
        docs.append(dict(doc=name, status="ok", bytes=len(raw),
                         integers=[int(x) for x in re.findall(r"\b(\d{2,6})\b", text)],
                         text=text[:400]))
    return docs


def userspace_scan(base: Path) -> list[dict[str, Any]]:
    """Vocabulary carriers under the binary directories only."""
    hits = []
    for sub in ("usr/bin", "usr/sbin", "lib", "usr/lib"):
        d = base / sub
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if not p.is_file():
                continue
            try:
                if p.stat().st_size > 8_000_000:
                    continue
                b = p.read_bytes()
            except OSError:
                continue
            a, h = b.count(b"airselect"), b.count(b"hopint")
            if a or h:
                hits.append(dict(path=p.relative_to(base).as_posix(), bytes=len(b),
                                 airselect=a, hopint=h))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        blob = path.read_bytes()
        sweep = token_sweep(blob, TOKENS)
        rows.append(dict(module=label, status="ok", bytes=len(blob),
                         sha256=hashlib.sha256(blob).hexdigest(),
                         tokens=sweep, token_count=len(sweep),
                         airselect_surface=sum(sweep[t]["count"] for t in
                                               ("airselect", "AirSelect", "AIRSELECT")
                                               if t in sweep)))

    base = help_dir()
    docs = parse_help(base) if base else []
    carriers = userspace_scan(base.parents[3]) if base else []

    ok = [r for r in rows if r.get("status") == "ok"]
    hop_doc = next((d for d in docs if d["doc"] == "airselecthopint.html"), {})
    acount_doc = next((d for d in docs if d["doc"] == "airselectacount.html"), {})
    report = dict(
        meta=dict(stage="374A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/ubnt_airselect_and_freq_hop_state_machine_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="AirSelect vocabulary sweep over the polling modules with string "
                         "context; shipped help pages parsed for the documented contract; "
                         "userspace binary directories swept for vocabulary carriers",
                  premise_corrections=[
                      "XW has no ubnt_poll_host.ko; the 2.6.32.71 tree ships ubnt_poll.ko "
                      "(529,284 bytes) instead, and that module is the XW data point",
                      "ubnt_poll_host.ko carries no AirSelect vocabulary, so the state machine "
                      "the stage names is not in the module the stage names",
                  ],
                  radio_safety="static only"),
        modules=rows,
        xw_expected_module=dict(path=str(XW_EXPECTED.relative_to(REPO_ROOT)).replace("\\", "/"),
                                exists=XW_EXPECTED.exists()),
        help_docs=docs,
        userspace_carriers=carriers,
        summary=dict(modules_ok=len(ok),
                     xw_poll_host_present=XW_EXPECTED.exists(),
                     kernel_airselect_surface=sum(r["airselect_surface"] for r in ok),
                     modules_with_hop_vocabulary=sum(1 for r in ok if "hop" in r["tokens"]),
                     hop_token_hits=max((r["tokens"]["hop"]["count"] for r in ok
                                         if "hop" in r["tokens"]), default=0),
                     help_docs_present=sum(1 for d in docs if d.get("status") == "ok"),
                     default_hop_interval_ms=(3000 if 3000 in hop_doc.get("integers", [])
                                              else None),
                     announce_example_ms=(1000 if 1000 in acount_doc.get("integers", [])
                                          else None),
                     userspace_carriers=len(carriers),
                     binaries_with_vocabulary=sum(1 for c in carriers
                                                  if c["path"].startswith(("usr/bin",
                                                                           "usr/sbin"))),
                     fh_token_hits=max((r["tokens"]["fh_"]["count"] for r in ok
                                        if "fh_" in r["tokens"]), default=0),
                     modules_with_fh_hops=sum(1 for r in ok if "fh_hops" in r["tokens"]),
                     state_machine_located=int(any("fh_hops" in r["tokens"] for r in ok)),
                     state_machine_recovered=0),
        gaps=["the AirSelect vocabulary is absent from ubnt_poll_host.ko (WA and XC): zero hits "
              "for airselect/hop/hopint. The feature is not named that way in the AC polling "
              "module",
              "on XW the mechanism IS present, under a different name: ubnt_poll.ko carries "
              "fh_list, fh_hops, fh_retries, fh_time and fh_announce_cnt, plus 'hopping to "
              "chanidx' and 'failed hop to freq' log sites",
              "located is not decoded: no hop timer value, channel-list walk or announcement "
              "schedule was reconstructed, and no transition was traced",
              "the documented contract (3000 ms default hop interval, announce count dividing "
              "the interval) comes from the shipped help pages, not from code",
              "the userspace implementation was not located by literal name; only a library, the "
              "translations and the SNMP MIB carry the airselect vocabulary",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[374A] modules={s['modules_ok']} xw_poll_host={s['xw_poll_host_present']} "
          f"airselect_in_kernel={s['kernel_airselect_surface']} "
          f"hop_hits={s['hop_token_hits']} fh_hits={s['fh_token_hits']} "
          f"fh_hops_modules={s['modules_with_fh_hops']} "
          f"located={s['state_machine_located']} recovered=0 "
          f"help={s['help_docs_present']} hop_ms={s['default_hop_interval_ms']} "
          f"carriers={s['userspace_carriers']}")
    for r in ok:
        print(f"        {r['module']:<30} {r['bytes']:>7}B tokens={sorted(r['tokens'])}")
    for c in carriers:
        print(f"        carrier {c['path']:<40} airselect={c['airselect']}")
    print(f"[374A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
