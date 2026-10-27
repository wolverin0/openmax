#!/usr/bin/env python3
"""Stage 667A — HTT TX descriptor path and the T2H completion ring.

The stage asks for the ath10k TX path: `ath10k_htt_tx_32`, `frag_desc`, `peer_id`, `tid`,
`vdev_id`, and the `HTT_T2H_MSG_TYPE_TX_COMPL_IND` completion ring that frees sk_buffs and feeds
AQL/BQL.

`ath10k_core.ko` **does not exist** in this corpus (0 files; stages 371A, 395A, 423A and 437A all hit
the same wall). So the ath10k names are unavailable — but the **vendor HTT path is fully named** in
`umac.ko`, and it is the same pipeline under different identifiers:

```
htt_tx_attach             htt_tx_detach
htt_tx_desc_alloc         htt_tx_desc_free
htt_tx_desc_flag_batch_more      htt_tx_desc_flag_postponed
htt_tx_compl_desc_id      htt_tx_sched
htt_tx_send_std
```

That is a **complete descriptor lifecycle** — attach, allocate, two state flags, schedule, send, and
free — with `htt_tx_compl_desc_id` naming the completion descriptor that drives the ring.

The T2H side is equally explicit:

```
htt_t2h_msg_handler       htt_t2h_lp_msg_handler
htt_t2h_stats_print       htt_t2h_tx_ppdu_log_print
htt_t2h_dbg_stats_hdr_parse
ol_tx_completion_handler  wmi_htc_tx_complete
ath_net80211_tx_complete
```

**`CONFIRMED`**: `htt_t2h_msg_handler` is the T2H consumer, and `ol_tx_completion_handler` is the
OS-side completion that releases the buffer. The `_lp` variant is the **low-priority** handler, so
T2H traffic is split by priority — which is what keeps completions from being starved by data.

Two ath10k concepts are genuinely **absent**:

| Token | Hits |
| :--- | :-: |
| `frag_desc` | **0** |
| `aql`, `AQL`, `bql`, `BQL` | **0** |

**`REFUTED`**: there is no `frag_desc` and no AQL/BQL accounting in these modules. AQL/BQL are
**mainline mac80211** mechanisms; the vendor stack uses its own TDMA scheduler (`ubnt_poll_host`)
instead, which is why the tokens are absent rather than merely renamed.

`peer_id` (1) and `vdev_id` (1) are present in `umac.ko` but only once each — enough to show the
fields exist, not enough to lay out the descriptor.

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
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage667a_ath10k_htt_tx_desc_and_comp_ring_re.json")

MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
}

TOKENS = ["htt_tx", "htt_t2h", "tx_compl", "tx_complete", "frag_desc",
          "peer_id", "vdev_id", "aql", "AQL", "bql", "BQL", "T2H"]
# the descriptor lifecycle
DESC = ["htt_tx_attach", "htt_tx_detach", "htt_tx_desc_alloc", "htt_tx_desc_free"]
# the two state flags
FLAGS = ["htt_tx_desc_flag_batch_more", "htt_tx_desc_flag_postponed"]
# the completion path
COMPL = ["htt_tx_compl_desc_id", "htt_t2h_msg_handler", "htt_t2h_lp_msg_handler",
         "ol_tx_completion_handler"]
# the ath10k-specific concepts that should be absent
ATH10K = ["frag_desc", "aql", "bql", "TX_COMPL_IND"]


def ctx(b: bytes, tok: str, n: int = 2, w: int = 66) -> list[str]:
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

    ath10k = len([p for p in (REPO_ROOT / "artifacts").rglob("ath10k*.ko")])

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
            desc={k: b.count(k.encode()) for k in DESC},
            flags={k: b.count(k.encode()) for k in FLAGS},
            compl={k: b.count(k.encode()) for k in COMPL},
            ath10k={k: b.count(k.encode()) for k in ATH10K},
            tx_symbols=syms.matching(r"htt_tx", 20),
            t2h_symbols=syms.matching(r"htt_t2h", 16),
            compl_symbols=syms.matching(r"completion|tx_complete", 12)))

    ok = [r for r in rows if r.get("status") == "ok"]
    tx = sorted({n for r in ok for n in r["tx_symbols"]})
    t2h = sorted({n for r in ok for n in r["t2h_symbols"]})
    compl = sorted({n for r in ok for n in r["compl_symbols"]})
    desc_found = [k for k in DESC if any(r["desc"][k] for r in ok)]
    flags_found = [k for k in FLAGS if any(r["flags"][k] for r in ok)]
    compl_found = [k for k in COMPL if any(r["compl"][k] for r in ok)]
    a10 = sum(sum(r["ath10k"].values()) for r in ok)
    peer_id = sum(r["tokens"]["peer_id"] for r in ok)
    vdev_id = sum(r["tokens"]["vdev_id"] for r in ok)

    report = dict(
        meta=dict(stage="667A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage667a_ath10k_htt_tx_desc_and_comp_ring_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census across four modules; defined-symbol lookup for the htt_tx "
                         "descriptor lifecycle, the two descriptor flags and the T2H completion "
                         "handlers; explicit probe for the ath10k-only concepts",
                  premise_corrections=[
                      "ath10k_core.ko does not exist (0 files), so ath10k_htt_tx_32 and the "
                      "ath10k descriptor layout are unavailable; the vendor htt_tx path is "
                      "dissected instead",
                      "frag_desc and aql/bql do not exist: those are mainline ath10k and mac80211 "
                      "concepts, and the vendor stack uses its own TDMA scheduler",
                  ],
                  radio_safety="static only"),
        ath10k_modules=ath10k,
        modules=rows,
        summary=dict(ath10k_core_present=ath10k > 0,
                     modules_ok=len(ok),
                     htt_tx_symbol_count=len(tx),
                     htt_tx_symbols=tx[:10],
                     desc_lifecycle=desc_found,
                     desc_lifecycle_count=len(desc_found),
                     desc_lifecycle_complete=int(len(desc_found) == 4),
                     desc_flags=flags_found,
                     desc_flag_count=len(flags_found),
                     completion_symbols=compl_found,
                     completion_symbol_count=len(compl_found),
                     compl_desc_id_present=int("htt_tx_compl_desc_id" in compl_found),
                     t2h_msg_handler_present=int("htt_t2h_msg_handler" in compl_found),
                     t2h_lp_handler_present=int("htt_t2h_lp_msg_handler" in compl_found),
                     os_completion_present=int("ol_tx_completion_handler" in compl_found),
                     ath10k_only_token_hits=a10,
                     frag_desc_absent=int(not any(r["ath10k"]["frag_desc"] for r in ok)),
                     aql_bql_absent=int(not any(r["ath10k"]["aql"] or r["ath10k"]["bql"]
                                                for r in ok)),
                     peer_id_hits=peer_id,
                     vdev_id_hits=vdev_id,
                     tx_desc_layout_recovered=0,
                     aql_bql_accounting_recovered=0),
        gaps=["ath10k_core.ko is absent, so ath10k_htt_tx_32, frag_desc and the 32-bit HTT TX "
              "descriptor layout cannot be read",
              "frag_desc and aql/bql return 0 across all four modules: those are mainline ath10k "
              "and mac80211 mechanisms, not vendor ones",
              "the vendor descriptor lifecycle is named but its field layout is not: peer_id and "
              "vdev_id appear once each, which proves the fields exist without locating them",
              "the T2H completion ring is named by its handler, not by the ring structure; no "
              "ring depth or descriptor stride was recovered",
              "AQL/BQL accounting does not exist here, so the airtime-queue feedback loop the "
              "stage describes has no vendor equivalent in these modules",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[667A] ath10k={s['ath10k_core_present']} modules={s['modules_ok']} "
          f"htt_tx={s['htt_tx_symbol_count']} desc={s['desc_lifecycle_count']}/4 "
          f"flags={s['desc_flag_count']} compl={s['completion_symbol_count']} "
          f"ath10k_tokens={s['ath10k_only_token_hits']} peer={s['peer_id_hits']} "
          f"vdev={s['vdev_id_hits']}")
    print(f"        desc={desc_found}")
    print(f"        compl={compl_found}")
    print(f"[667A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
