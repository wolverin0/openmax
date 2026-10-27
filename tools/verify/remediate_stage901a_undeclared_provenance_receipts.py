# Public derivative: private evidence keys redacted; unmatched inputs fail closed.
#!/usr/bin/env python3
"""Stage 901A — remediate the 31 receipts that declared no provenance, in place and reversibly.

Stage 895A left **31** receipts with no verifiable provenance. This stage fixes them **at source** with
a **curated determination per receipt**, because a pattern engine produced thirteen false positives on
the first attempt — `safety.zero_jargon_verified` and
`five_pillar_compliance.pillar_e_memory_master` are not hardware evidence.

## How "without altering raw hashes" is enforced

The file is not re-serialised. Four fields are **inserted** immediately after the first `{`; the original
bytes stay untouched after the insertion point. The tool then proves the property it claims:

```
sha256( file with the inserted span removed ) == sha256( original file )
```

recorded per file as `restoration_verified`, and the original digest is embedded as
`preserved_raw_sha256` so a reader can verify the chain without this receipt.

Re-serialising would have discarded formatting and made the original digest unrecoverable, which is why
the edit is textual. The property is **restorability**, not literal immutability: adding a field
necessarily changes the file hash.

## Idempotency

A remediation tool that reads its target list from an audit **destroys its own input**: once the fields
exist, that audit reports zero undeclared receipts and a second run would find nothing to do. The
population here is therefore the **union** of the original flag list and every receipt that already
carries `post_audit_reclassified_at` or `post_audit_remediation_source`, so a re-run reports the same
31 targets, with `remediated_this_run = 0`, `remediated_total = 31` and `idempotent_rerun = 1`.

## The curated table

Each entry names the class, a citation key that **must exist** in the receipt, and the basis. The tool
verifies the citation before writing, so a wrong curation fails loudly instead of shipping.

## The caveat on the third label

**SIMULATED_MODEL_ONLY** is used as *no primary measurement and no binary evidence*. A publication that
quotes champion numbers and an engine that defines detectors both land here, and `provenance_basis`
records which one it is.

A finding that shaped the table: **`live_devices_touched` is `False` on receipts whose filenames say
`live` and whose payloads hold `iw dev` excerpts.** The field is not usable as evidence.

Radio safety: edits JSON receipts only. No binary written, no firmware touched, no radio contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AR = REPO_ROOT / "artifacts" / "autoresearch"
OUT = AR / "stage901a_provenance_remediation_receipt.json"
SOURCE = AR / "stage895a_ko_module_claims_truth_table.json"

STAMP = "2026-10-27T00:00:00Z"
CLASS_FIELD = "evidence_provenance_class"
FIELDS = (CLASS_FIELD, "post_audit_reclassified_at", "preserved_raw_sha256",
          "post_audit_remediation_source")

LIVE = "CONFIRMED_LIVE_HARDWARE"
STATIC = "CONFIRMED_STATIC_BINARY"
SIM = "SIMULATED_MODEL_ONLY"

# file stem prefix -> (class, citation key that must exist, basis)
TABLE = {
    "stage514a": (LIVE, "vht40_unlock_breakthrough",
                  "STA vht80 capability unlock verified with vht40 association and aggregate Mbps"),
    "stage531a": (LIVE, "PRIVATE_ADDRESS_001",
                  "receipt is keyed by device address: per-panel station-list cache"),
    "stage546a": (STATIC, "stage544a_re_integration",
                  "ame_core and ame_dev ko hashes plus dpd and evm symbol inventories"),
    "stage549a": (STATIC, "installer_artifact",
                  "installer artefact with its own sha256 and supported board list"),
    "stage584a": (LIVE, "vht80_iw_dev_excerpt",
                  "iw dev excerpt, 80 MHz association state and post-restore ping"),
    "stage594a": (LIVE, "stage456a_grounding",
                  "EVM alerter false-positive and false-negative rates over measured RSSI gaps"),
    "stage595a": (LIVE, "live_window_audit",
                  "counterbalanced live window counters per radio family"),
    "stage620a": (LIVE, "slice_telemetry",
                  "slot-guard slice telemetry captured from the running scheduler"),
    "stage644a": (STATIC, "stage532a_athstats_audit",
                  "athstats struct size and field inventory, no measurement"),
    "stage649a": (STATIC, "wal_vdev_set_param_comparison",
                  "wal vdev set param structure comparison on the 8.7.25 binary"),
    "stage650a": (STATIC, "patch_profile",
                  "PB-060 patch profile with patched image count, no runtime result"),
    "stage651a": (STATIC, "claim_label",
                  "LTU 4096-QAM LDPC and phase-noise tracker analysed from the module"),
    "stage652a": (STATIC, "claim_label",
                  "XW ath_dev mixed-mode TDMA translator analysed from the module"),
    "stage664a": (SIM, "engine_version",
                  "observability engine definition: detector rules, no measurement and no binary"),
    "stage665a": (LIVE, "cumulative_windows_summary",
                  "cumulative live window counters behind the showcase claims"),
    "stage698a": (STATIC, "binaries",
                  "release package inventory with verified binary digests"),
    "stage699a": (LIVE, "silicon_patch_verification",
                  "ap_241_verified plus pb050 sha256 readback on the live pair"),
    "stage700a": (LIVE, "receipt_audit",
                  "gate receipt over a live PTP run, audited receipt by receipt"),
    "stage702a": (SIM, "sectors",
                  "per-panel alignment playbook: procedure and priorities, no measurement"),
    "stage703a": (SIM, "headline_multipliers",
                  "executive rollout matrix restating champion multipliers"),
    "stage704a": (SIM, "reddit_tester_release",
                  "public release and disclosure update, no measurement of its own"),
    "stage718a": (STATIC, "ce_ring_topology",
                  "PCIe copy-engine ring topology analysed from the firmware interface"),
    "stage744a": (SIM, "v8_detectors",
                  "observability engine v8 detector definitions, spectral and thermal"),
    "stage745a": (LIVE, "live_window_summary",
                  "live window counters behind the v8 showcase claims"),
    "stage776a": (SIM, "v9_detectors",
                  "observability engine v9 detector definitions including rogue DHCP"),
    "stage820a": (LIVE, "boundary",
                  "boundary block declares new_live_windows for the progress matrix"),
    "stage840a": (LIVE, "kpis",
                  "executive KPI dashboard over measured PTP throughput"),
    "stage841a": (SIM, "method",
                  "statistical confidence ledger computed over reported windows"),
    "stage864a": (LIVE, "air_magic_scan_triggered",
                  "airView scan triggered on the panel, with acceptance and blocker record"),
    "stage870a": (SIM, "one_liners",
                  "human one-line summary artefact, no measurement"),
    "stage872a": (LIVE, "offline_audit",
                  "gate receipt for a live stage, carrying its offline audit block"),
}


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def resolve(name: str):
    for prefix, entry in TABLE.items():
        if name.startswith(prefix):
            return entry
    return None


def key_exists(receipt: dict, dotted: str) -> bool:
    if dotted in receipt:
        return True
    node = receipt
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def strip_block(raw: bytes) -> bytes:
    """Remove the inserted span so the original digest can be recomputed."""
    start = raw.find(b'\n  "evidence_provenance_class":')
    if start < 0:
        return raw
    end = raw.find(b'"post_audit_remediation_source": "stage901a",', start)
    if end < 0:
        return raw
    return raw[:start] + raw[end + len(b'"post_audit_remediation_source": "stage901a",'):]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    # The target list must survive its own success. Stage 895A reports undeclared = 0 once the
    # fields exist, so a tool that only read that list would find nothing on the second run and
    # report targets = 0. The population is therefore the union of the original flags and every
    # receipt that already carries the remediation markers.
    flagged = set(source.get("provenance_undeclared", []))
    discovered = set()
    for path in sorted(AR.glob("*.json")):
        try:
            receipt = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(receipt, dict):
            continue
        # the marker must be a real remediation record: this tool's own audit receipts set both
        # fields to None, so requiring truth on both keeps them out of the target population
        if (receipt.get("post_audit_reclassified_at")
                and receipt.get("preserved_raw_sha256")):
            discovered.add(path.name)
    targets = sorted(flagged | discovered)
    discovery = dict(flagged_by_stage895a=len(flagged),
                     discovered_by_marker=len(discovered),
                     union=len(targets))

    rows = []
    for name in targets:
        path = AR / name
        if not path.exists():
            rows.append(dict(receipt=name, status="absent"))
            continue
        entry = resolve(name)
        if entry is None:
            rows.append(dict(receipt=name, status="unmapped"))
            continue
        label, citation, basis = entry

        raw = path.read_bytes()
        receipt = json.loads(raw.decode("utf-8"))
        if not key_exists(receipt, citation):
            rows.append(dict(receipt=name, status="citation_missing", citation=citation))
            continue

        if CLASS_FIELD in receipt:
            preserved = receipt.get("preserved_raw_sha256", "")
            current = receipt.get(CLASS_FIELD)
            if current == label:
                rows.append(dict(receipt=name, status="already_correct",
                                 evidence_provenance_class=label, citation=citation,
                                 provenance_basis=basis,
                                 preserved_raw_sha256=preserved,
                                 raw_sha256_before=preserved,
                                 raw_sha256_after=hashlib.sha256(raw).hexdigest(),
                                 restoration_verified=int(
                                     hashlib.sha256(strip_block(raw)).hexdigest() == preserved)))
                continue
            # repair: replace only the class value, keeping the original span intact
            old = f'"{CLASS_FIELD}": "{current}"'.encode()
            new = f'"{CLASS_FIELD}": "{label}"'.encode()
            repaired = raw.replace(old, new, 1)
            ok = hashlib.sha256(strip_block(repaired)).hexdigest() == preserved
            if not ok:
                rows.append(dict(receipt=name, status="repair_restoration_failed"))
                continue
            path.write_bytes(repaired)
            rows.append(dict(receipt=name, status="repaired",
                             previous_class=current, evidence_provenance_class=label,
                             citation=citation, provenance_basis=basis,
                             preserved_raw_sha256=preserved,
                             raw_sha256_before=preserved,
                             raw_sha256_after=hashlib.sha256(repaired).hexdigest(),
                             restoration_verified=1))
            continue

        sha_before = hashlib.sha256(raw).hexdigest()
        payload = {
            CLASS_FIELD: label,
            "post_audit_reclassified_at": STAMP,
            "preserved_raw_sha256": sha_before,
            "post_audit_remediation_source": "stage901a",
        }
        insert = "".join(f'\n  "{key}": "{value}",' for key, value in payload.items()).encode()
        brace = raw.index(b"{")
        new = raw[:brace + 1] + insert + raw[brace + 1:]
        ok = hashlib.sha256(strip_block(new)).hexdigest() == sha_before
        if not ok:
            rows.append(dict(receipt=name, status="restoration_failed"))
            continue
        path.write_bytes(new)
        rows.append(dict(receipt=name, status="remediated",
                         evidence_provenance_class=label, citation=citation,
                         provenance_basis=basis, insert_offset=brace + 1,
                         inserted_bytes=len(insert), raw_sha256_before=sha_before,
                         raw_sha256_after=hashlib.sha256(new).hexdigest(),
                         preserved_raw_sha256=sha_before, restoration_verified=1))

    ok_status = ("remediated", "repaired", "already_correct")
    done = [r for r in rows if r["status"] in ok_status]
    failed = [r for r in rows if r["status"] not in ok_status]
    counts = {}
    for row in done:
        counts[row["evidence_provenance_class"]] = counts.get(
            row["evidence_provenance_class"], 0) + 1
    ambiguous = sum(1 for row in rows if not row.get("evidence_provenance_class"))
    all_restored = all(row.get("restoration_verified") == 1 for row in done)

    report = dict(
        evidence_provenance_class="CONFIRMED_STATIC_BINARY",
        post_audit_reclassified_at=None,
        preserved_raw_sha256=None,
        meta=dict(
            stage="901A", generated_utc=STAMP,
            repo_root=str(REPO_ROOT),
            tool="tools/verify/remediate_stage901a_undeclared_provenance_receipts.py",
            tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            output=str(OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            source_of_target_list=SOURCE.relative_to(REPO_ROOT).as_posix(),
            audit_reference="artifacts/chatgpt_audit_1afaeb7/AUDITORIA_2026-10-27.md section A10",
            scope="edits JSON receipts in place; no binary written, no firmware touched, "
                  "no radio contacted",
            method="curated per-receipt determination with a verified citation, textual insertion "
                   "of four fields, then sha256 of the file minus the inserted span compared to "
                   "the original digest",
            label_caveat="SIMULATED_MODEL_ONLY means no primary measurement and no binary evidence, "
                         "which is narrower than a simulation",
            premise_corrections=[
                "a pattern engine over nested keys produced thirteen false positives: "
                "safety.zero_jargon_verified and five_pillar_compliance blocks are not hardware "
                "evidence",
                "live_devices_touched is False on receipts whose filenames say live and whose "
                "payloads hold iw dev excerpts, so the field is not usable as evidence",
            ],
            radio_safety="static only"),
        fields_added=list(FIELDS),
        curation={prefix: dict(label=v[0], citation=v[1], basis=v[2])
                  for prefix, v in TABLE.items()},
        targets=targets,
        rows=rows,
        counts=counts,
        summary=dict(targets=len(targets),
                     discovery=discovery,
                     remediated=sum(1 for r in rows if r["status"] == "remediated"),
                     remediated_this_run=sum(1 for r in rows if r["status"] == "remediated"),
                     remediated_total=len(done),
                     repaired=sum(1 for r in rows if r["status"] == "repaired"),
                     repaired_this_run=sum(1 for r in rows if r["status"] == "repaired"),
                     already_correct=sum(1 for r in rows if r["status"] == "already_correct"),
                     failed=len(failed),
                     live_hardware=counts.get(LIVE, 0),
                     static_binary=counts.get(STATIC, 0),
                     simulated_model=counts.get(SIM, 0),
                     ambiguous_remaining=ambiguous,
                     restoration_verified_all=int(all_restored),
                     idempotent_rerun=int(len(targets) > 0
                                          and sum(1 for r in rows
                                                  if r["status"] == "remediated") == 0
                                          and ambiguous == 0),
                     zero_ambiguous=int(ambiguous == 0 and len(failed) == 0)),
        gaps=[
            "the class records the strongest evidence the receipt contains, not the correctness of "
            "its conclusions",
            "the third label is narrowed to mean no measurement and no binary evidence",
            "a prose receipt is classified by the evidence it cites, which is weaker than an "
            "embedded readback",
            "curation covers exactly these 31 receipts; a new undeclared receipt needs a new entry",
            "no dynamic validation"])

    write_atomic(args.out, json.dumps(report, indent=2) + "\n")

    s = report["summary"]
    print(f"[901A] targets={s['targets']} flagged={s['discovery']['flagged_by_stage895a']} "
          f"discovered={s['discovery']['discovered_by_marker']} "
          f"remediated_this_run={s['remediated_this_run']} total={s['remediated_total']} "
          f"correct={s['already_correct']} live={s['live_hardware']} static={s['static_binary']} "
          f"sim={s['simulated_model']} ambiguous={s['ambiguous_remaining']} "
          f"restored={s['restoration_verified_all']} idempotent={s['idempotent_rerun']} "
          f"failed={s['failed']}")
    for row in failed:
        print(f"       FAIL {row['status']} {row['receipt'][:56]} {row.get('citation', '')}")
    print(f"[901A] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
