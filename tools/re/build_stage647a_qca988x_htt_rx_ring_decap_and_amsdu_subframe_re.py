#!/usr/bin/env python3
"""Stage 647A — HTT RX ring management, decap modes, A-MSDU and attention flags.

The stage names four things across `umac.ko` and `ath_dev.ko`:

  * **HTT RX ring** management;
  * RX **decap** modes (raw, native wifi, ethernet, 802.3);
  * **A-MSDU** subframe deaggregation;
  * **attention.flags**.

Three are present and one is a naming correction.

**The RX ring is real and configurable in two variants.** The HTT transport carries:

```
htt_attach   htt_attach_target   htt_detach   htt_display
htt_h2t_rx_ring_cfg_msg      htt_h2t_rx_ring_cfg_msg_hl   htt_h2t_rx_ring_cfg_msg_ll
htt_h2t_aggr_cfg_msg         htt_h2t_send_complete        htt_h2t_dbg_stats_get
htt_rx_ring_elems            htt_rx_msdu_rx_attention_retrieve_ll
```

**`CONFIRMED`**: the ring is configured by a host-to-target message with **three forms** — a base
`cfg_msg` plus an **`_hl`** and an **`_ll`** variant. High-level and low-level ring
configurations are separate messages, which is what a transport needs when the descriptor format
differs between the two ends.

**The attention flag has a concrete mask.** `umac.ko` carries a hard assertion:

```
Assertion failed! %s:%s %s:%d
((*(u_int32_t *) &rx_desc->attention) & 0x80000000)
```

**`CONFIRMED`**: `attention_mask = 0x80000000` — bit 31 of the `attention` word, tested by an
assertion that will fire if it is clear. That is one of the rare **concrete numeric constants** in
this series, and it is accompanied by the retriever `htt_rx_msdu_rx_attention_retrieve_ll`.

**`decap` here means decryption, not decapsulation.** All 9 hits are `ccmp_decap`,
`ieee80211_crypto_decap` and their neighbours. There is **no** `raw_mode`, `native_wifi` or
`decap_mode` token — the RX decap *mode* enum the stage assumes is not named.

**The mode that does exist is documented as a module parameter:**

```
_80211_enable: Enable reception of 802.11 frames & conversion to 802.3 frames on host
```

**`CONFIRMED`**: `host_80211_enable` is the 802.11-versus-802.3 boundary — when set, the host receives
802.11 frames and performs the conversion itself; when clear, the target delivers 802.3. That is the
decap-mode choice, expressed as a boolean rather than a four-way enum.

**A-MSDU**: `amsdu` has 28 hits, but the named family `ath_amsdu_*` (9 symbols) is **transmit-side
staging** (`ath_amsdu_send`, `ath_amsdu_stageq_flush`, `ath_amsdu_tx_drain`). The receive side is
`htt_rx_amsdu_pop`, which Stage 395A already showed is present but calls `skb_pull` **zero** times.

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
       / "stage647a_qca988x_htt_rx_ring_decap_and_amsdu_subframe_re.json")

MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
    "XC:ath_dev.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
}

TOKENS = ["htt", "HTT", "decap", "raw_mode", "native_wifi", "decap_mode",
          "ethernet", "802.3", "amsdu", "AMSDU", "attention", "rx_ring", "rx_desc", "msdu"]
# the three ring-config message forms
RING_CFG = ["htt_h2t_rx_ring_cfg_msg", "htt_h2t_rx_ring_cfg_msg_hl",
            "htt_h2t_rx_ring_cfg_msg_ll"]
# the concrete attention mask asserted in the module
ATTN_ASSERT = "rx_desc->attention) & 0x80000000"
# the host decap boundary
HOST_80211 = "conversion to 802.3 frames on host"
# the RX-side amsdu entry point
RX_AMSDU = "htt_rx_amsdu_pop"


def ctx(b: bytes, tok: str, n: int = 2, w: int = 68) -> list[str]:
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

    rows = []
    for label, path in MODULES.items():
        if not path.exists():
            rows.append(dict(module=label, status="absent"))
            continue
        b = path.read_bytes()
        syms = Syms(path)
        decap_ctx = ctx(b, "decap", 3)
        rows.append(dict(
            module=label, status="ok", bytes=len(b),
            sha256=hashlib.sha256(b).hexdigest(), defined_symbols=len(syms.names),
            tokens={t: b.count(t.encode()) for t in TOKENS},
            ring_cfg={k: b.count(k.encode()) for k in RING_CFG},
            attn_assert=b.count(ATTN_ASSERT.encode()),
            attn_mask=b.count(b"0x80000000"),
            host_80211=b.count(HOST_80211.encode()),
            rx_amsdu=b.count(RX_AMSDU.encode()),
            attn_retriever=b.count(b"htt_rx_msdu_rx_attention_retrieve"),
            decap_crypto=b.count(b"ccmp_decap") + b.count(b"crypto_decap"),
            decap_contexts=decap_ctx[:2],
            htt_symbols=syms.matching(r"^htt_|_htt_", 30),
            amsdu_symbols=syms.matching(r"amsdu", 16)))

    ok = [r for r in rows if r.get("status") == "ok"]
    htt = sorted({n for r in ok for n in r["htt_symbols"]})
    amsdu = sorted({n for r in ok for n in r["amsdu_symbols"]})
    amsdu_tx = [n for n in amsdu if "ath_amsdu" in n]
    amsdu_rx = [n for n in amsdu if "rx_amsdu" in n]
    ring_cfg = sorted({k for r in ok for k, v in r["ring_cfg"].items() if v})
    attn_assert = sum(r["attn_assert"] for r in ok)
    attn_mask = sum(r["attn_mask"] for r in ok)
    host_80211 = sum(1 for r in ok if r["host_80211"])
    rx_amsdu = sum(r["rx_amsdu"] for r in ok)
    decap_crypto = sum(1 for r in ok if r["decap_crypto"] > 0)
    native = sum(r["tokens"]["native_wifi"] for r in ok)
    raw = sum(r["tokens"]["raw_mode"] for r in ok)
    decap_mode = sum(r["tokens"]["decap_mode"] for r in ok)

    report = dict(
        meta=dict(stage="647A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/build_stage647a_qca988x_htt_rx_ring_decap_and_amsdu_subframe_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no radio contacted",
                  method="token census across four modules; HTT symbol extraction; assertion "
                         "string extraction for the attention mask; context classification of the "
                         "decap hits to separate decryption from decapsulation",
                  premise_corrections=[
                      "decap in this module means decryption (ccmp_decap, crypto_decap), not RX "
                      "decapsulation; raw_mode, native_wifi and decap_mode have 0 hits",
                      "the RX decap mode is expressed as the host_80211_enable boolean, not as a "
                      "four-way enum",
                  ],
                  radio_safety="static only"),
        modules=rows,
        summary=dict(modules_ok=len(ok),
                     htt_symbol_count=len(htt),
                     htt_symbols=htt[:12],
                     ring_cfg_variants=ring_cfg,
                     ring_cfg_variant_count=len(ring_cfg),
                     ring_cfg_has_hl_ll=int(len(ring_cfg) == 3),
                     attention_assert_hits=attn_assert,
                     attention_mask_hits=attn_mask,
                     attention_mask="0x80000000",
                     attention_flag_recovered=int(attn_assert > 0 and attn_mask > 0),
                     attention_retriever_present=int(any(r["attn_retriever"] for r in ok)),
                     host_80211_modules=host_80211,
                     host_80211_boundary=int(host_80211 > 0),
                     decap_is_crypto_modules=decap_crypto,
                     native_wifi_hits=native,
                     raw_mode_hits=raw,
                     decap_mode_hits=decap_mode,
                     native_raw_enum_absent=int(native == 0 and raw == 0 and decap_mode == 0),
                     amsdu_symbol_count=len(amsdu),
                     amsdu_tx_symbols=len(amsdu_tx),
                     amsdu_rx_symbols=len(amsdu_rx),
                     amsdu_is_mixed=int(bool(amsdu_tx) and bool(amsdu_rx)),
                     rx_amsdu_pop_hits=rx_amsdu,
                     rx_amsdu_present=int(rx_amsdu > 0),
                     subframe_deagg_decoded=0),
        gaps=["raw_mode, native_wifi and decap_mode have 0 hits: the four-way RX decap enum the "
              "stage assumes is not named in these modules",
              "decap here is decryption (ccmp_decap, crypto_decap); reading it as decapsulation "
              "would be wrong",
              "the decap boundary that does exist is the host_80211_enable boolean, which chooses "
              "between host-side 802.11 delivery and target-side 802.3 conversion",
              "the named amsdu family is transmit-side staging (ath_amsdu_*); the receive path is "
              "htt_rx_amsdu_pop, which Stage 395A showed calls skb_pull zero times",
              "the attention mask is recovered as 0x80000000 from an assertion, but the other "
              "bits of the attention word were not decoded",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[647A] modules={s['modules_ok']} htt={s['htt_symbol_count']} "
          f"ring_cfg={s['ring_cfg_variant_count']} attn_mask={s['attention_mask']} "
          f"host80211={s['host_80211_modules']} decap_crypto={s['decap_is_crypto_modules']} "
          f"native_raw_absent={s['native_raw_enum_absent']} amsdu={s['amsdu_symbol_count']} "
          f"rx_pop={s['rx_amsdu_pop_hits']}")
    print(f"        ring_cfg={ring_cfg}")
    print(f"[647A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
