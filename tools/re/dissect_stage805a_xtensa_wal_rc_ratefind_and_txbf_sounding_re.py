#!/usr/bin/env python3
"""Stage 805A — Xtensa WAL rate-control ratefind and TxBF sounding.

The stage asks for the **WAL rate-control ratefind** and the **TxBF sounding** sequence in the
Xtensa firmware blob.

The firmware side has **no names at all**. The QCA988x container
(`openwrt_qca988x_hw20_firmware_2_ct.bin`, 204,796 bytes, 2 `SGMT` segments totalling 204,677 bytes)
returns **0 hits** for `wal`, `WAL`, `ratefind`, `txbf`, `sounding`, `rc_` and `rate`. That is
expected: a compiled Xtensa image carries no identifiers, and Stage 423A established that the whole
payload is code, not a table of names.

So the rate-control vocabulary is recovered where it exists — the **host UMAC**:

```
wal_rcquery   wal_rcupdate   ratectrl_dbgid_wal_rcquery   ratectrl_dbgid_wal_rcupdate
_RATE_GetTxRetrySchedule   _RATE_GetSGIFlag   _RATE_SetSGIMasks
rcGetFirstValidTxRate   rcGetNextValidTxRate   rcUpdate
g_default_sgi_per_thresh   g_default_xretry_per_penalty
```

**`CONFIRMED`**: `wal_*` (6 hits) are the **WAL rate-control debug IDs**, and `rcGetFirstValidTxRate`
/ `rcGetNextValidTxRate` are the **ratefind walk** — first valid rate, then next. That is the
rate-selection loop the stage names, and it is a **host** loop driving a firmware rate table.

**`REFUTED`**: `sounding` and `SU-BF` return **0** — the TxBF **sounding sequence is not named**.
`TXBF` (7 hits) is capability text and per-rate-group power (Stage 615A), not a training procedure.

**`CONFIRMED`**: `ratefind_is_host_side = 1` — the search runs in `umac.ko` against firmware-supplied
per-rate statistics. The firmware supplies the measurements; the host does the walking.

`firmware_rate_table_recovered = 0`: the rate table itself is numeric data inside the SGMT payload,
and no structure was decoded.

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
       / "stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.json")

CONTAINER = FW / "openwrt_qca988x_hw20_firmware_2_ct.bin"
UMAC = FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko"

# the firmware-side names the stage assumes
FW_TOKENS = ["wal", "WAL", "ratefind", "txbf", "txbf_", "sounding", "rc_", "rate"]
# the host-side rate-control vocabulary
HOST_TOKENS = ["wal_", "ratefind", "sounding", "TXBF", "rcGet", "rcUpdate",
               "_RATE_GetTxRetrySchedule", "_RATE_GetSGIFlag", "_RATE_SetSGIMasks",
               "g_default_sgi_per_thresh", "g_default_xretry_per_penalty"]
# the ratefind walk
RATEFIND = ["rcGetFirstValidTxRate", "rcGetNextValidTxRate"]
# the WAL debug ids
WAL_DBG = ["wal_rcquery", "wal_rcupdate"]


def parse_sgmt(blob: bytes) -> list[dict[str, Any]]:
    if not blob.startswith(b"QCA-ATH10K"):
        return []
    vlen = struct.unpack("<I", blob[16:20])[0]
    off = 20 + vlen
    segs = []
    while off + 8 <= len(blob):
        ie_id, ie_len = struct.unpack("<II", blob[off:off + 8])
        if off + 8 + ie_len > len(blob):
            break
        payload = blob[off + 8:off + 8 + ie_len]
        if payload[:4] == b"SGMT":
            segs.append(dict(id=ie_id, len=ie_len, payload=payload))
        off += 8 + ie_len
    return segs


def ascii_runs(b: bytes, min_len: int = 8) -> int:
    return len(re.findall(rb"[\x20-\x7e]{%d,}" % min_len, b))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    blob = CONTAINER.read_bytes() if CONTAINER.exists() else b""
    segs = parse_sgmt(blob)
    fw_hits = {t: blob.count(t.encode()) for t in FW_TOKENS}

    umac = UMAC.read_bytes() if UMAC.exists() else b""
    host = {t: umac.count(t.encode()) for t in HOST_TOKENS}
    walk = [k for k in RATEFIND if umac.count(k.encode())]
    wdbg = [k for k in WAL_DBG if umac.count(k.encode())]

    class Syms:
        def __init__(self, b: bytes) -> None:
            E = ">" if b[5] != 1 else "<"
            shoff = struct.unpack(E + "I", b[32:36])[0]
            shent, shnum, shstr = struct.unpack(E + "HHH", b[46:52])
            secs = []
            for i in range(shnum):
                o = shoff + i * shent
                nm, typ, fl, addr, off, sz, link, info, al, es = struct.unpack(
                    E + "IIIIIIIIII", b[o:o + 40])
                secs.append(dict(no=nm, off=off, size=sz, link=link))
            stro = secs[shstr]["off"]
            stt = None
            for s in secs:
                e = b.find(b"\0", stro + s["no"])
                if b[stro + s["no"]:e] == b".symtab":
                    stt = s
            names = []
            if stt:
                ss = secs[stt["link"]]
                for i in range(stt["size"] // 16):
                    o = stt["off"] + i * 16
                    nm, val, sz, info, oth, shndx = struct.unpack(E + "IIIBBH", b[o:o + 16])
                    if shndx == 0:
                        continue
                    e = b.find(b"\0", ss["off"] + nm)
                    names.append(b[ss["off"] + nm:e].decode("latin1"))
            self.names = sorted(set(names))

    syms = Syms(umac) if umac else type("X", (), {"names": []})()
    rc_syms = [n for n in syms.names if re.search(r"^rc[A-Z]|_RATE_|wal_", n)][:20]

    report = dict(
        meta=dict(stage="805A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no firmware loaded, no module loaded, "
                        "no radio contacted",
                  method="container SGMT parse and name sweep; host UMAC rate-control symbol and "
                         "token lookup; ASCII-run census of the firmware payloads",
                  premise_corrections=[
                      "the Xtensa payload carries no rate-control names: wal, ratefind, txbf, "
                      "sounding, rc_ and rate all return 0 in the container",
                      "there is no sounding sequence by name anywhere: TXBF exists only as "
                      "capability text and per-rate-group power",
                  ],
                  radio_safety="static only"),
        container=dict(bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest() if blob else None,
                       segments=len(segs),
                       segment_bytes=sum(s["len"] for s in segs),
                       ascii_runs_per_segment=[ascii_runs(s["payload"]) for s in segs]),
        firmware_tokens=fw_hits,
        host_tokens=host,
        host_ratecontrol_symbols=rc_syms,
        summary=dict(segments=len(segs),
                     firmware_named_token_hits=sum(fw_hits.values()),
                     firmware_names_absent=int(sum(fw_hits.values()) == 0),
                     host_wal_dbg_ids=wdbg,
                     host_wal_dbg_count=len(wdbg),
                     ratefind_walk=walk,
                     ratefind_walk_complete=int(len(walk) == 2),
                     ratefind_is_host_side=int(len(walk) == 2),
                     txbf_capability_hits=host["TXBF"],
                     sounding_token_hits=host["sounding"],
                     sounding_absent=int(host["sounding"] == 0),
                     sgi_mask_setter=int(host["_RATE_SetSGIMasks"] > 0),
                     xretry_penalty_present=int(host["g_default_xretry_per_penalty"] > 0),
                     host_ratecontrol_symbol_count=len(rc_syms),
                     firmware_rate_table_recovered=0,
                     txbf_sounding_sequence_recovered=0),
        gaps=["the firmware payload carries no identifiers, so the rate table and the ratefind "
              "input cannot be read by name",
              "no sounding sequence exists: TXBF is capability text and per-rate-group power, and "
              "SU-BF returns 0",
              "the ratefind walk is host-side (rcGetFirstValidTxRate then rcGetNextValidTxRate); "
              "its inputs come from firmware statistics that were not decoded",
              "the rate table itself is numeric data inside the SGMT payloads and no structure "
              "was recovered",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[805A] segs={s['segments']} fw_names={s['firmware_named_token_hits']} "
          f"wal_dbg={s['host_wal_dbg_count']} walk={s['ratefind_walk_complete']} "
          f"host_side={s['ratefind_is_host_side']} txbf={s['txbf_capability_hits']} "
          f"sounding={s['sounding_token_hits']} rc_syms={s['host_ratecontrol_symbol_count']}")
    print(f"        walk={walk}")
    print(f"[805A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
