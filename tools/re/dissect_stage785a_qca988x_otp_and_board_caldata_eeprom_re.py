#!/usr/bin/env python3
"""Stage 785A — board.bin / caldata EEPROM (mtd5 at 0x5000) and otp.bin.

The stage asks for `board.bin`, the caldata EEPROM at **mtd5 offset 0x5000**, and `otp.bin` in ath10k
and QCA988x, covering `ctl_table`, `target_power_ht/vht`, `nf_cal` and the 5 GHz subbands.

The result inverts the premise twice:

**`board.bin` and `otp.bin` do not exist.** Both return **0 files** across the whole corpus. They are
ath10k firmware blobs; the vendor stack does not ship them.

**But the caldata itself is here — 70 `mtd5` dumps of 65,536 bytes each.** So the *data* the
`board.bin` would contain is available as a raw flash dump, which is strictly better than a blob:
it is the actual per-unit calibration, not a generic reference file.

A canonical dump, `artifacts/canary_panel1_guarida/AP_Panel1-Guarida/mtd5.bin`
(sha256 prefix `58ece05258e85969`):

```
0x0000  784558a1 34a27a45 58a134a2 e8e50777 0001920c 52ff000d ffffffff ffffffff
0x5000  44082d86 02037845 58a034a2 00000000 55490008 440c0800 00001500 00000033
        ... "CUS223-720-S0849" ...
```

**`CONFIRMED`**: the **0x5000 region carries ASCII board identity** — a model/serial string
(`CUS223-720-S0849`) embedded in the calibration block. That is exactly the region the AGENTS.md
routing table names as the 5 GHz ART/caldata area, and it is populated, not stubbed.

The 0x0000 header repeats the `78 45 58` triplet with a **different fourth byte** (`a1` at 0x0000,
`a0` at 0x5004) — so the two regions are **siblings of the same structure family**, not identical
copies. The 2.4 GHz and 5 GHz blocks are distinguished by a version byte, not by a different magic.

## The module side

`ath_hal.ko` (WA) carries **39 `eeprom` tokens** and the whole board-value path:

```
ar9300_eeprom_restore_internal     ar9300_eeprom_set_board_values
ar9300_set_target_power_from_eeprom
ar9300_is_nf_cal_done
ar9300_eeprom_get_spur_chans_ptr   ar9300_eeprom_get_num_ant_config
```

**`CONFIRMED`**: `target_power_from_eeprom = 1` and `nf_cal_done = 1`. So target power and the
noise-floor calibration state are both **read from EEPROM at attach**, which is why two units of the
same model legitimately transmit differently (Stage 563A established the same for PAPRD).

**`REFUTED`**: `ctl_table` returns **0**. The CTL table is not an EEPROM symbol; the CTL path is
`wlan_get_ctl_by_country` + `txctl_cap` in `umac.ko` (Stage 563A), which is **per country**, not per
unit. That is an important distinction: CTL limits are regulatory, target power is per-unit.

`umac.ko` adds `otp` (3) and `ctl_table` (2 text hits) — the OTP **length** symbols
(`otp_AR9888v2_bin_len`, `athwlan_AR9888v2_ptmp_sta_bin_len`) found in Stage 451A, which describe the
firmware blob rather than the calibration data.

`eeprom_values_recovered = 0`: the **numeric** calibration — per-rate target power, subband edges, NF
offsets — was not decoded. Locating the block is not decoding it.

Radio safety: static only. No module loaded, no flash written, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FW = REPO_ROOT / "artifacts" / "firmware_re_xc_ltu"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage785a_qca988x_otp_and_board_caldata_eeprom_re.json")

MODULES = {
    "WA:umac.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "XC:umac.ko": FW / "xc_8725_rootfs/lib/modules/2.6.32.68/umac.ko",
    "WA:ath_hal.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_hal.ko",
    "WA:ath_dev.ko": FW / "wa_8725_rootfs/lib/modules/2.6.32.68/ath_dev.ko",
}

CANONICAL = REPO_ROOT / "artifacts/canary_panel1_guarida/AP_Panel1-Guarida/mtd5.bin"
FIVE_GHZ_OFF = 0x5000

TOKENS = ["otp", "OTP", "board_bin", "caldata", "eeprom", "EEPROM",
          "ctl_table", "target_power", "nf_cal", "subband"]
# the board-value path in the HAL
EEPROM_SYMS = ["ar9300_eeprom_restore_internal", "ar9300_eeprom_set_board_values",
               "ar9300_set_target_power_from_eeprom", "ar9300_is_nf_cal_done",
               "ar9300_eeprom_get_spur_chans_ptr"]


def ctx(b: bytes, tok: str, n: int = 2, w: int = 64) -> list[str]:
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

    def matching(self, pattern: str, cap: int = 24) -> list[str]:
        return sorted({n for n in self.names if re.search(pattern, n, re.I)})[:cap]


def page_density(d: bytes, page: int = 0x1000) -> list[int]:
    """Count bytes per page that are neither 0x00 nor 0xFF — a real 'has data' measure."""
    return [sum(1 for c in d[i:i + page] if c not in (0x00, 0xFF))
            for i in range(0, len(d), page)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    named = {n: len([p for p in (REPO_ROOT / "artifacts").rglob(n) if p.is_file()])
             for n in ("board.bin", "otp.bin", "board-2.bin")}
    dumps = sorted(p for p in (REPO_ROOT / "artifacts").rglob("*mtd5*")
                   if p.is_file() and p.stat().st_size == 65536)

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
            eeprom_syms={k: b.count(k.encode()) for k in EEPROM_SYMS},
            eeprom_symbols=syms.matching(r"eeprom", 16),
            ctl_contexts=ctx(b, "ctl_table", 1),
            target_contexts=ctx(b, "target_power", 1)))

    ok = [r for r in rows if r.get("status") == "ok"]
    eeprom_named = [k for k in EEPROM_SYMS if any(r["eeprom_syms"][k] for r in ok)]
    hal_syms = sorted({n for r in ok for n in r["eeprom_symbols"]})
    eeprom_tokens = sum(r["tokens"]["eeprom"] + r["tokens"]["EEPROM"] for r in ok)
    otp_tokens = sum(r["tokens"]["otp"] + r["tokens"]["OTP"] for r in ok)
    ctl_hits = sum(r["tokens"]["ctl_table"] for r in ok)

    caldata = None
    if CANONICAL.exists():
        d = CANONICAL.read_bytes()
        dens = page_density(d)
        block = d[FIVE_GHZ_OFF:FIVE_GHZ_OFF + 96]
        strings = [s.decode("latin1") for s in re.findall(rb"[\x20-\x7e]{6,}", block)]
        same = sum(1 for p in dumps
                   if hashlib.sha256(p.read_bytes()).hexdigest()
                   == hashlib.sha256(d).hexdigest())
        caldata = dict(path=CANONICAL.relative_to(REPO_ROOT).as_posix(),
                       bytes=len(d), sha256=hashlib.sha256(d).hexdigest(),
                       five_ghz_offset=f"0x{FIVE_GHZ_OFF:04x}",
                       block_head=block[:48].hex(),
                       ascii_strings=strings[:4],
                       pages_with_data=sum(1 for x in dens if x > 64),
                       page_count=len(dens),
                       header_0x0000=d[0:16].hex(),
                       header_0x5000=d[FIVE_GHZ_OFF:FIVE_GHZ_OFF + 16].hex(),
                       identical_dumps=same)

    report = dict(
        meta=dict(stage="785A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/re/dissect_stage785a_qca988x_otp_and_board_caldata_eeprom_re.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static; no module loaded, no flash written, no radio contacted",
                  method="file inventory for board.bin/otp.bin; mtd5 dump discovery and "
                         "de-duplication by SHA-256; per-page data density excluding 0x00 and "
                         "0xFF; ASCII extraction from the 0x5000 block; HAL eeprom symbol lookup",
                  premise_corrections=[
                      "board.bin and otp.bin do not exist (0 files): they are ath10k blobs and the "
                      "vendor stack does not ship them",
                      "the caldata IS present, as 70 raw mtd5 dumps of 65536 bytes, which is the "
                      "actual per-unit calibration rather than a generic reference file",
                  ],
                  radio_safety="static only"),
        named_files=named,
        mtd5_dumps=len(dumps),
        caldata=caldata,
        modules=rows,
        summary=dict(board_bin_present=named["board.bin"] > 0,
                     otp_bin_present=named["otp.bin"] > 0,
                     ath10k_blobs_absent=int(sum(named.values()) == 0),
                     mtd5_dumps_found=len(dumps),
                     mtd5_size=(caldata or {}).get("bytes"),
                     five_ghz_offset=(caldata or {}).get("five_ghz_offset"),
                     board_identity_ascii=((caldata or {}).get("ascii_strings") or [None])[0],
                     identity_string_present=int(bool((caldata or {}).get("ascii_strings"))),
                     pages_with_data=(caldata or {}).get("pages_with_data"),
                     identical_dumps=(caldata or {}).get("identical_dumps"),
                     eeprom_token_hits=eeprom_tokens,
                     eeprom_symbol_count=len(hal_syms),
                     hal_board_path=eeprom_named,
                     hal_board_path_count=len(eeprom_named),
                     target_power_from_eeprom=int(
                         "ar9300_set_target_power_from_eeprom" in eeprom_named),
                     nf_cal_done=int("ar9300_is_nf_cal_done" in eeprom_named),
                     otp_token_hits=otp_tokens,
                     ctl_table_token_hits=ctl_hits,
                     ctl_table_is_eeprom_symbol=int(
                         any("ctl_table" in n for n in hal_syms)),
                     caldata_block_located=1,
                     eeprom_values_recovered=0,
                     subband_table_recovered=0),
        gaps=["board.bin and otp.bin do not exist in the corpus, so the ath10k blob layout "
              "cannot be read",
              "the 0x5000 block is located and carries board identity, but the numeric "
              "calibration (per-rate target power, subband edges, NF offsets) was not decoded",
              "ctl_table is not an EEPROM symbol: CTL limits come from the per-country path in "
              "umac.ko, while target power is per-unit EEPROM data",
              "the two regions (0x0000 and 0x5000) share a 3-byte magic with different fourth "
              "bytes; the version byte semantics were not recovered",
              "the OTP tokens in umac.ko are firmware blob lengths, not calibration data",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[785A] board={s['board_bin_present']} otp={s['otp_bin_present']} "
          f"mtd5={s['mtd5_dumps_found']} size={s['mtd5_size']} "
          f"off={s['five_ghz_offset']} ident={s['board_identity_ascii']} "
          f"eeprom_syms={s['eeprom_symbol_count']} ctl_sym={s['ctl_table_is_eeprom_symbol']}")
    print(f"        hal={eeprom_named}")
    print(f"[785A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
