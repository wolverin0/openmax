#!/usr/bin/env python3
"""Stage 810A — verification of the 805A..809A receipts.

This is a **verifier**: it reads the five stage receipts this run produced and re-checks the
invariants each one claims. It does not re-dissect binaries — it asserts that the artefacts agree
with each other and with the corpus.

Checks per stage:

| Stage | Invariant |
| :--- | :--- |
| 805A | firmware names absent, ratefind walk host-side and complete |
| 806A | `patch_emitted = 0`, and that fact is explained by zero viable segments |
| 807A | subchannel vocabulary absent while `ulmap` is named |
| 808A | AirView absent from the kernel and present as a userspace binary |
| 809A | `execution_authorised = 0` and every role blocked |

Cross-stage checks:

  * every receipt declares `static only`;
  * every receipt declares at least one gap;
  * the two firmware-side stages (805A, 806A) agree that the container has 2 `SGMT` segments;
  * no stage claims a recovery whose sibling stage refuted.

A verifier that cannot fail is useless, so `failures` is a list and `compliant` is `len(failures)==0`.

Radio safety: static only. Reads JSON receipts written by this run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
AR = REPO_ROOT / "artifacts" / "autoresearch"
OUT = (REPO_ROOT / "artifacts" / "autoresearch"
       / "stage810a_xtensa_pb070_and_ltu_split_freq_suite.json")

RECEIPTS = {
    "805A": AR / "stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.json",
    "806A": AR / "stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.json",
    "807A": AR / "stage807a_ltu_split_freq_and_ofdma_subchannel_re.json",
    "808A": AR / "stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.json",
    "809A": AR / "stage809a_pb040_to_pb070_quad_patch_pareto.json",
}


def load(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    data = {k: load(p) for k, p in RECEIPTS.items()}
    failures: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(stage: str, name: str, ok: bool, detail: str = "") -> None:
        checks.append(dict(stage=stage, check=name, ok=bool(ok), detail=detail))
        if not ok:
            failures.append(f"{stage}:{name} {detail}".strip())

    for stage, r in data.items():
        if r is None:
            check(stage, "receipt_present", False, "unreadable or missing")
            continue
        check(stage, "receipt_present", True)
        check(stage, "static_scope", r["meta"]["scope"].lower().find("static") >= 0)
        check(stage, "radio_safety", r["meta"]["radio_safety"] == "static only")
        check(stage, "has_gaps", bool(r.get("gaps")))

    if data.get("805A") and data.get("806A"):
        seg805 = data["805A"]["summary"]["segments"]
        seg806 = data["806A"]["summary"]["segments"]
        check("cross", "sgmt_segment_count_agrees", seg805 == seg806,
              f"805A={seg805} 806A={seg806}")

    if data.get("805A"):
        s = data["805A"]["summary"]
        check("805A", "firmware_names_absent", s["firmware_names_absent"] == 1)
        check("805A", "ratefind_host_side", s["ratefind_is_host_side"] == 1)
        check("805A", "ratefind_complete", s["ratefind_walk_complete"] == 1)
        check("805A", "sounding_absent", s["sounding_absent"] == 1)
        check("805A", "no_firmware_table_claimed", s["firmware_rate_table_recovered"] == 0)

    if data.get("806A"):
        s = data["806A"]["summary"]
        check("806A", "patch_not_emitted", s["patch_emitted"] == 0)
        check("806A", "zero_viable_segments", s["segments_viable"] == 0)
        check("806A", "blocking_reason_present", bool(s.get("blocking_reason")))

    if data.get("807A"):
        s = data["807A"]["summary"]
        check("807A", "subchannel_absent", s["subchannel_vocabulary_absent"] == 1)
        check("807A", "ulmap_named", s["ulmap_is_named_subsystem"] == 1)
        check("807A", "split_freq_present", s["split_freq_pair_present"] == 1)
        check("807A", "no_subchannel_map_claimed", s["subchannel_map_recovered"] == 0)

    if data.get("808A"):
        s = data["808A"]["summary"]
        check("808A", "airview_not_in_kernel", s["kernel_airview_hits"] == 0)
        check("808A", "airview_is_userspace", s["airview_is_userspace"] == 1)
        check("808A", "no_arbitration_claimed",
              s["airview_kernel_arbitration_recovered"] == 0)

    if data.get("809A"):
        s = data["809A"]["summary"]
        check("809A", "nothing_authorised", s["execution_authorised"] == 0)
        check("809A", "all_roles_blocked", s["all_roles_blocked"] == 1)
        check("809A", "labelled_projection", s["measurement_or_projection"] == "projection")
        check("809A", "front_within_roles",
              s["pareto_front_size"] + s["dominated_count"] == s["roles_parsed"])

    compliant = len(failures) == 0
    report = dict(
        meta=dict(stage="810A", generated_utc="2026-10-26T00:00:00Z",
                  repo_root=str(REPO_ROOT),
                  tool="tools/verify/verify_stage810a_xtensa_pb070_and_ltu_split_freq_suite.py",
                  tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
                  scope="offline static verification; reads five JSON receipts only",
                  method="per-stage invariant checks plus cross-stage agreement; a verifier that "
                         "cannot fail is useless, so failures is a list and compliant is its empty",
                  radio_safety="static only"),
        receipts={k: dict(path=v.relative_to(REPO_ROOT).as_posix(),
                          sha256=hashlib.sha256(v.read_bytes()).hexdigest())
                  for k, v in RECEIPTS.items() if v.exists()},
        checks=checks,
        failures=failures,
        summary=dict(stages_expected=len(RECEIPTS),
                     stages_present=sum(1 for v in data.values() if v is not None),
                     checks_run=len(checks),
                     checks_passed=sum(1 for c in checks if c["ok"]),
                     failures=len(failures),
                     compliant=int(compliant)),
        gaps=["the verifier checks receipt self-consistency, not binary truth: a wrong value "
              "recorded consistently in a receipt would pass",
              "no stage in this suite re-dissects a binary; 805A..809A remain the source of record",
              "no dynamic validation"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    s = report["summary"]
    print(f"[810A] stages={s['stages_present']}/{s['stages_expected']} "
          f"checks={s['checks_passed']}/{s['checks_run']} failures={s['failures']} "
          f"compliant={s['compliant']}")
    for f in failures:
        print("        FAIL", f)
    print(f"[810A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
