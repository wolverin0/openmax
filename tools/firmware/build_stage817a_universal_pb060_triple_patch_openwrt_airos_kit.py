#!/usr/bin/env python3
"""Compose PB040 CCA + PB050 + PB060 locally; never load a radio."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEM = "stage817a_universal_pb060_triple_patch_openwrt_airos_kit"
HELPER = "firmware/openwrt/common/fmx_pb060_triple_patch_loader.sh"
PB040_BEFORE = bytes.fromhex("009e0200a016721320137213109e0200")
PB040_AFTER = bytes.fromhex("009e0200a016721320137613109e0200")


def local(root: Path, label: str) -> Path:
    root = root.resolve()
    path = (root / label).resolve()
    path.relative_to(root)
    if str(path).startswith("\\\\"):
        raise ValueError("network paths forbidden")
    return path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def package_files(root: Path, package: Path) -> list[dict]:
    records = []
    for path in sorted(package.iterdir()):
        if path.is_file():
            label = path.relative_to(root).as_posix()
            data = local(root, label).read_bytes()
            records.append({"path": label, "sha256": sha(data), "bytes": len(data)})
    return records


def pillars(stage: str) -> dict:
    return {
        "pillar_a_ground_up_re_and_knob_catalog": {"status": "CONFIRMED", "scope": "local byte provenance only"},
        "pillar_b_hyperresearch_and_scholar_reactor": {"status": "UNKNOWN", "scope": "offline; no new scholar/research claim"},
        "pillar_c_karpathy_autoresearch_and_watchdog": {"status": "CONFIRMED", "scope": "offline only; A1 B1 A2 B2 and 45s/120s watchdog required before activation"},
        "pillar_d_scientific_pareto_validation": {"status": "CONFIRMED", "scope": "byte invariants only; no performance inference"},
        "pillar_e_memory_master_claim_id": {"status": "UNKNOWN", "scope": "project:futuramax", "local_ledger_key": stage, "ingested": False},
    }


def write_report(root: Path, stem: str, report: dict, doc: str) -> dict:
    receipt = local(root, f"artifacts/autoresearch/{stem}.json")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    dest = local(root, f"docs/{stem.upper()}.md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if len(doc.splitlines()) >= 180 or doc.count("<!-- doc-head:") != 1 or doc.count("<!-- /doc-head -->") != 1:
        raise ValueError("document contract")
    dest.write_text(doc, encoding="utf-8", newline="\n")
    return report


def compose(target: str, original: bytes) -> tuple[bytes, list[dict]]:
    from firmware.xtensa_sgmt_surgical_patcher import SgmtContainer, SgmtSurgicalPatcher, SurgicalPatchSpec
    from tools.firmware.build_stage474a_pb050_xtensa_rc_probe_dampener_sgmt_patch import get_pb050_rc_probe_dampen_specs_for_target
    from tools.firmware.build_stage650a_pb060_xtensa_txop_and_tid_sched_sgmt_patch import get_pb060_specs_for_target

    before = SgmtContainer.from_bytes(original)
    segment = before.segments[3]
    if segment.decoded_bytes.count(PB040_BEFORE) != 1:
        raise ValueError("PB040 exact byte motif not unique in segment 3")
    offset = segment.decoded_bytes.index(PB040_BEFORE)
    specs = [SurgicalPatchSpec(
        patch_id="PB040-CCA-AGC-OVERRIDE", pb_stage="Stage817A", description="Exact unique modal CCA tuple",
        target_symbol=target, segment_index=3, virtual_address=segment.destination + offset,
        expected_orig_bytes=PB040_BEFORE, patched_bytes=PB040_AFTER, sibling_addresses={},
        safety_rationale="Exact bytes, unique match, unchanged length; runtime acceptance pending",
    )] + get_pb050_rc_probe_dampen_specs_for_target(target) + get_pb060_specs_for_target(target)
    ranges = []
    for spec in specs:
        start, end = spec.virtual_address, spec.virtual_address + len(spec.expected_orig_bytes)
        if any(start < b and a < end for a, b in ranges):
            raise ValueError("overlapping patch sites")
        ranges.append((start, end))
    current, evidence = before, []
    for spec in specs:
        current, rec = SgmtSurgicalPatcher.validate_and_apply(current, spec)
        evidence.append(rec)
    output = current.to_bytes(recompress=False)
    after = SgmtContainer.from_bytes(output)
    if before.entry_point != after.entry_point or len(before.segments) != len(after.segments):
        raise ValueError("SGMT layout changed")
    for old, new in zip(before.segments, after.segments):
        if (old.destination, old.decoded_size) != (new.destination, new.decoded_size):
            raise ValueError("segment layout changed")
    for spec in specs:
        seg = after.segments[spec.segment_index]
        off = spec.virtual_address - seg.destination
        if seg.decoded_bytes[off:off + len(spec.patched_bytes)] != spec.patched_bytes:
            raise ValueError("roundtrip patch verification")
    return output, evidence


def originals(root: Path):
    """Read local originals, never execute their producers."""
    from tools.firmware.build_stage441a_xtensa_wmi_0x9064_polling_hook_composer import parse_fw2_ct_sgmt_ies
    from tools.firmware.build_stage474a_pb050_xtensa_rc_probe_dampener_sgmt_patch import extract_sgmt_blob
    fw = "artifacts/firmware_re_xc_ltu/openwrt_qca988x_hw20_firmware_2_ct.bin"
    if local(root, fw).is_file():
        data = local(root, fw).read_bytes()
        yield "OpenWrt_10.1.467-ct_IE3", parse_fw2_ct_sgmt_ies(data)[3].to_bytes(recompress=False), fw, sha(data)
    for family in ("WA", "XC"):
        label = f"artifacts/firmware_re_xc_ltu/{family.lower()}_8725_rootfs/lib/modules/2.6.32.68/umac.ko"
        path = local(root, label)
        if path.is_file():
            digest = sha(path.read_bytes())
            for role in ("ptp", "ptmp_ap", "ptmp_sta"):
                yield f"{family}.v8.7.25_{role}", extract_sgmt_blob(path, f"athwlan_AR9888v2_{role}_bin"), label, digest


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    package = local(root, "artifacts/autoresearch/kits/stage817a")
    package.mkdir(parents=True, exist_ok=True)
    helper = local(root, HELPER).read_bytes()
    (package / "fmx_pb060_triple_patch_loader.sh").write_bytes(helper)
    images, blocked = [], []
    for target, data, source, source_sha in originals(root):
        try:
            output, patches = compose(target, data)
        except ValueError as exc:
            blocked.append({"target_id": target, "reason": str(exc)})
            continue
        name = f"{target}_pb040_pb050_pb060.sgmt.bin"
        (package / name).write_bytes(output)
        images.append({"target_id": target, "source": source, "source_sha256": source_sha,
                       "original_sgmt_sha256": sha(data), "path": str((package / name).relative_to(root)).replace("\\", "/"),
                       "sha256": sha(output), "size_bytes": len(output), "patches_applied": patches,
                       "runtime_verified": False})
    sums = [f"{sha(helper)}  fmx_pb060_triple_patch_loader.sh"]
    sums += [f"{item['sha256']}  {Path(item['path']).name}" for item in images]
    (package / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="ascii", newline="\n")
    report = {"stage": "817A", "status": "CONFIRMED" if len(images) == 7 and not blocked else "UNKNOWN",
              "execution_mode": "OFFLINE_PACKAGING", "claim_scope": "local SGMT triple-patch composition only",
              "attribution": ["QCA firmware", "external controller"], "images": images, "blocked_targets": blocked,
              "expected_targets": 7, "helper_script": HELPER, "helper_sha256": sha(helper),
              "package_files": package_files(root, package),
              "boundary": {"network_access": False, "live_devices_touched": False, "activation_available": False,
                           "physical_acceptance": False, "protected_partitions_modified": False},
              "five_pillar_compliance": pillars("stage817a")}
    return write_report(root, STEM, report, f"""<!-- doc-head: Stage817A local PB040 PB050 PB060 composition; activation gated -->
<!-- /doc-head -->
# Stage 817A Universal PB060 triple-patch kit

`{report['status']}` applies to offline byte composition only. Attribution: `QCA firmware` / `external controller`.
Built {len(images)}/7 target SGMT payloads: OpenWrt CT IE3 and airOS 8.7.25 WA/XC PtP/AP/STA.
PB040 is the exact unique CCA tuple; PB050 and PB060 use existing target-specific surgical specifications.
All sites must be disjoint, match original bytes and survive parse/repack with unchanged segment layout.
Hashes and individual patch receipts are in `artifacts/autoresearch/{STEM}.json`.
Package: `artifacts/autoresearch/kits/stage817a`; `SHA256SUMS` covers its helper and payloads.
The shell loader defaults to inspection and supports checksum verification. Activation is refused.
These SGMT payloads are not complete flash images. airOS signature acceptance and OpenWrt container embedding are UNKNOWN.
No SSH, target writes, module reloads, flash or new performance measurements occurred.
Unsupported or missing target inputs stay UNKNOWN; no fallback binary is synthesized.
Online scholar grounding and durable MemoryMaster ingestion remain UNKNOWN.
""")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    result = build(parser.parse_args().root)
    print(f"Stage817A offline composition: {len(result['images'])}/7; runtime=UNKNOWN")
    return 0 if result["status"] == "CONFIRMED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
