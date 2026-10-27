#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Stage170A public WA tester v4, using the existing pinned native image recipe.

Builds locally; never imports a VM baker or contacts a radio. Experimental
settings and saved benchmark claims remain distinct from measured acceptance.
"""
from __future__ import annotations

import argparse
from copy import copy
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from firmware.openwrt.pbe5ac_gen2_ptp_kit import build_public_openmax_release as core

PackageError = core.ReleaseError
VERSION = 4
DEFAULT_OUTPUT = core.KIT / "public_release_v4"
DEFAULT_WORK = ROOT / "artifacts/verification/stage170a_build"
DEFAULT_RECEIPT = ROOT / "artifacts/autoresearch/stage170a_public_wa_4board_release_v4_receipt.json"
SOURCE_NAME = "99-fmx-wa-universal-champion.r1-r18.source.txt"
SOURCE_PIN = "62034b4b9abaebdb615f3cb78c2f2ce7410f385e7361c31b0287c52e68a479b1"
EVIDENCE_PINS = {
    "stage145a_live_wa_round13_15_autoresearch.json": "638f5eb68ee7176c38f94fa8fe54858817707b7d5a3b2d88f4dce921a024e67b",
    "stage161a_live_wa_round16_18_autoresearch.json": "d3e683317b3bfb17fd0b8ea2c404c6a538b8e79a6f2b700d53ded6973e34bfa7",
    "stage162a_live_wa_e2e_forwarding_offload_benchmark.json": "e21826d548dad7bc685a04c9a4797c5c35574e1759621f70a265e80152463f4c",
    "stage163a_cumulative_18round_wa_champion_v2.json": "b60d21699a56ada57ebf2a5251b7a4a99d8945cb40fdf0504574cf41f913759d"}
REQUESTED = {"vm.min_free_kbytes": 4096, "aql_threshold": 4000, "distance": 300,
    "tcp_pacing_ca_ratio": 110, "tcp_pacing_ss_ratio": 150, "fq_initial_quantum": 3028,
    "packet_steering": 1, "flow_offloading": 1, "nf_conntrack_max": 16384}


def load_evidence(root=ROOT):
    root = core.safe_local(root)
    previous = core.champion_evidence(root)
    data, rounds = {}, []
    for name, pin in EVIDENCE_PINS.items():
        raw = core.safe_local(root / "artifacts/autoresearch" / name).read_bytes()
        if core.sha256(raw) != pin:
            raise PackageError("Champion-v2 evidence pin mismatch")
        item = json.loads(raw.decode("utf-8-sig"))
        data[name] = item
        for record in item.get("rounds", []):
            if [w["window"] for w in record["windows"]] != ["A1", "B1", "A2", "B2"]:
                raise PackageError("Champion-v2 window sequence mismatch")
            rounds.append({"round_id": record["round_id"], "window_count": 4,
                           "decision": record.get("decision", "UNKNOWN")})
    if [r["round_id"] for r in rounds] != ["S145A-R13", "S145A-R14", "S145A-R15", "S161A-R16", "S161A-R17", "S161A-R18", "S162A-E2E-R1"]:
        raise PackageError("Champion-v2 round identities mismatch")
    consolidated = data["stage163a_cumulative_18round_wa_champion_v2.json"]
    if consolidated.get("total_live_windows_including_stage162a_e2e") != 76:
        raise PackageError("Consolidation window count mismatch")
    return {"source_sha256": {**previous["sources"], **EVIDENCE_PINS},
        "rf_round_count": 18, "rf_window_count": 72, "e2e_round_count": 1, "e2e_window_count": 4,
        "total_comparisons": 19, "total_saved_windows": 76, "rf_rounds_r1_r12": previous["rounds"],
        "later_rounds": rounds, "requested_profile": REQUESTED,
        "offload_active": "UNKNOWN", "e2e_path_benefit": "UNPROVEN",
        "qualifications": [
            "Saved objects are hashed; native acquisition/physical validation is not repeated",
            "72 RF plus 4 E2E windows are distinct populations, not 18 homogeneous 76-window rounds",
            "R12 retained stock; cumulative profile regressed tail latency in that saved comparison",
            "Stage145 R15 retained ArmA; final163 settings do not uniformly reproduce that treatment",
            "Stage161 attempted initial_quantum on fq_codel with errors suppressed; no valid qdisc getter proves application",
            "Stage162 runner labels conntrack sizing as flow_offloading; no real flowtable activation is demonstrated",
            "Stage162 RPS mask1 selects CPU0; it does not establish multi-core parallelism",
            "Saved Boca auxiliary ping fields use 999 sentinels with samples1; E2E route/RTT benefit is unproven",
            "Configured/copy getters and final coverage/RTS snippets do not prove all requested settings",
            "These are experimental public candidates, not universal performance or four-board physical acceptance"]}


def render_champion(root=ROOT):
    root = core.safe_local(root)
    source = core.safe_local(root / "firmware/openwrt/pbe5ac_gen2_ptp_kit/public_assets" / SOURCE_NAME).read_bytes()
    if core.sha256(source) != SOURCE_PIN:
        raise PackageError("Frozen R1..R18 champion source mismatch")
    pairs = re.findall(r'^([A-Z0-9_]+)="\$\{\1:-([^}]+)\}"$', source.decode("ascii"), re.M)
    defaults = {k: v for k, v in pairs if not k.startswith("FMX_AIROS_")}
    required = {"FMX_MIN_FREE_KBYTES": "4096", "FMX_AQL_THRESHOLD": "4000", "FMX_DISTANCE_M": "300",
        "FMX_TCP_PACING_CA_RATIO": "110", "FMX_TCP_PACING_SS_RATIO": "150", "FMX_FQ_INITIAL_QUANTUM": "3028",
        "FMX_PACKET_STEERING": "1", "FMX_FLOW_OFFLOADING": "1"}
    if not all(defaults.get(k) == v for k, v in required.items()):
        raise PackageError("Champion-v2 required defaults drifted")
    # Start with the reviewed OpenWrt-only body; never copy the airOS fallback.
    body = core.safe_local(root / "firmware/openwrt/pbe5ac_gen2_ptp_kit/public_assets/wa_champion_openwrt_body.sh").read_bytes()
    if core.sha256(body) != core.CHAMPION_BODY_SHA256:
        raise PackageError("Reviewed public runtime body mismatch")
    body = body.decode("ascii").replace("profile=public-v3", "profile=public-v4")
    body = body.replace("any_ap=0\n", "active_phys=\nany_ap=0\n", 1)
    body = body.replace(' write_value "$phy_dir/aqm" "fq_quantum', ' active_phys="$active_phys $phy"\n write_value "$phy_dir/aqm" "fq_quantum', 1)
    body = body.replace('quantum=$FMX_AP_FQ_QUANTUM\nelif', 'quantum=$FMX_ETH_FQ_QUANTUM\nelif')
    body = body.replace('quantum=$FMX_STA_FQ_QUANTUM\nelse', 'quantum=$FMX_ETH_FQ_QUANTUM\nelse')
    body = body.replace('root fq_codel quantum "$quantum" limit', 'root fq_codel quantum "$quantum" target 5ms interval 100ms ecn limit')
    body = body.replace(' net.ipv4.tcp_notsent_lowat=', ' vm.min_free_kbytes="$FMX_MIN_FREE_KBYTES" \\\n net.ipv4.tcp_pacing_ca_ratio="$FMX_TCP_PACING_CA_RATIO" \\\n net.ipv4.tcp_pacing_ss_ratio="$FMX_TCP_PACING_SS_RATIO" \\\n net.netfilter.nf_conntrack_max=16384 \\\n net.ipv4.tcp_notsent_lowat=', 1)
    extra = '''
# Additional options require independent opt-ins, not inferred source success.
if grep -qx 'distance_enabled=1' /etc/openmax/champion.conf; then
 for phy in $active_phys; do
  iw phy "$phy" set distance "$FMX_DISTANCE_M" 2>/dev/null || printf 'distance_failed=%s\\n' "$phy" >> "$report"
  iw phy "$phy" info >> "$report" 2>/dev/null || true
 done
fi
if grep -qx 'forwarding_enabled=1' /etc/openmax/champion.conf; then
 # Preserve firewall zones/rules. Staging is not flowtable activation evidence.
 uci -q set network.globals.packet_steering="$FMX_PACKET_STEERING" && uci commit network || printf 'steering_stage_failed=1\\n' >> "$report"
 uci -q set 'firewall.@defaults[0].flow_offloading=1' && uci commit firewall || printf 'offload_stage_failed=1\\n' >> "$report"
 printf 'network_firewall_restart_required=1\\noffload_active=UNKNOWN\\n' >> "$report"
fi
if grep -qx 'fq_pacing_enabled=1' /etc/openmax/champion.conf && [ -n "$quantum" ]; then
 # sch_fq has initial_quantum; fq_codel does not. This is a new experiment.
 for net in eth0 br-lan; do
  tc qdisc replace dev "$net" root fq quantum "$FMX_ETH_FQ_QUANTUM" initial_quantum "$FMX_FQ_INITIAL_QUANTUM" 2>/dev/null || printf 'fq_pacing_failed=%s\\n' "$net" >> "$report"
 done
fi
for key in vm.min_free_kbytes net.ipv4.tcp_pacing_ca_ratio net.ipv4.tcp_pacing_ss_ratio net.netfilter.nf_conntrack_max; do
 sysctl "$key" >> "$report" 2>/dev/null || true
done
tc -s qdisc show >> "$report" 2>/dev/null || true
exit 0
'''
    # Replace only the final return, preserving guard exits and role fail-closed behavior.
    before, end, after = body.rpartition("exit 0\n")
    if not end or after:
        raise PackageError("Public runtime final-return anchor mismatch")
    return ("#!/bin/sh\n# Public tester v4 / qualified champion-v2 settings; no universal performance claim.\n" +
            "".join(f"{k}='{v}'\n" for k, v in defaults.items()) + before + extra).encode("ascii")


def public_payloads(profile, root=ROOT):
    files = core.public_payloads(profile, True)
    files["etc/openmax-release"] = (files["etc/openmax-release"][0].replace(b"public-v3", b"public-v4"), 0o644)
    files["etc/hotplug.d/net/99-fmx-wa-universal-champion"] = (render_champion(root), 0o755)
    files["etc/openmax/champion.conf"] = (b"# Public tester v4: explicit opt-in; desired values are not readbacks.\nenabled=0\ndistance_enabled=0\nforwarding_enabled=0\nfq_pacing_enabled=0\n", 0o644)
    files["etc/openmax/champion-v2.json"] = ((json.dumps(REQUESTED, indent=2) + "\n").encode(), 0o644)
    files["etc/openmax/qos-defaults.conf"] = (b"# Public tester v4: upstream queues until opt-in.\n# R1..R18/v2 configured profile; AP3028/STA1514, AQL4000, minfree4096.\n# sch_fq initial_quantum3028 requires separate new-experiment opt-in.\n# Flowtable activation, forwarding benefit and distance tuning remain unqualified.\n", 0o644)
    return files


def audit_tar(path, profile, root=ROOT):
    entries = core._tar_entries(path)
    for name, (member, data) in entries.items():
        if any(t in name.lower() for t in ("authorized_keys", "id_rsa", "id_ed25519", "dropbear_rsa_host_key", "dropbear_ed25519_host_key", "rc.poststart")):
            raise PackageError("Private/laboratory file forbidden")
        if data and (re.search(rb'\b(?:192\.168\.100\.[0-9]+|192\.168\.15\.[0-9]+|10\.10\.[0-9]+\.[0-9]+|10\.99\.[0-9]+\.[0-9]+)\b', data) or
                     re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\r\n]+[A-Za-z0-9+/=]{16}', data)):
            raise PackageError("Laboratory address/private key material forbidden")
    for name, (data, mode) in public_payloads(profile, root).items():
        if name not in entries or entries[name][1] != data or entries[name][0].mode != mode:
            raise PackageError("Public payload/mode mismatch")
    return {name: {"sha256": core.sha256(data) if data is not None else None, "mode": m.mode, "uid": m.uid,
                    "gid": m.gid, "type": m.type.decode("ascii"), "linkname": m.linkname}
            for name, (m, data) in entries.items()}


def _public_tar(stock, target, profile, module, root):
    entries = core._tar_entries(stock)
    module_check = core.verify_module(module, entries[core.MODULE_PATH][1], True)
    additions = {**public_payloads(profile, root), core.MODULE_PATH: (module, entries[core.MODULE_PATH][0].mode)}
    result = dict(entries)
    for name, (data, mode) in additions.items():
        member = tarfile.TarInfo("./" + name)
        member.mode, member.mtime, member.size = mode, core.SOURCE_DATE_EPOCH, len(data)
        result[name] = (member, data)
        parent = Path(name).parent.as_posix()
        while parent != ".":
            if parent not in result:
                m = tarfile.TarInfo("./" + parent)
                m.type, m.mode = tarfile.DIRTYPE, 0o755
                result[parent] = (m, None)
            parent = Path(parent).parent.as_posix()
    with tarfile.open(target, "w", format=tarfile.PAX_FORMAT) as tar:
        for name in sorted(result):
            m, data = result[name]
            m = copy(m)
            m.mtime = core.SOURCE_DATE_EPOCH
            m.pax_headers = {k: v for k, v in m.pax_headers.items() if k not in ("mtime", "atime", "ctime")}
            tar.addfile(m, io.BytesIO(data) if data is not None else None)
    if [name for name in entries if result[name][1] != entries[name][1]] != [core.MODULE_PATH]:
        raise PackageError("Unexpected stock content modification")
    return audit_tar(target, profile, root), module_check


def _images(factory, sysupgrade, squashfs, profile, champion_hash):
    out_factory, initial = core.rebuild_images(factory, sysupgrade, squashfs, profile, True)
    parsed = core.parse_sysupgrade(initial, profile)
    metadata = parsed["metadata"]
    metadata["openmax"].update({"release": "public-v4", "champion_version": 2, "champion_sha256": champion_hash})
    data = b"\0" * 8 + json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode()
    out_sys = core._append_fwx0(core._append_fwx0(parsed["payload"], data, 1), b"# fake certificate", 0)
    if core.parse_factory(out_factory)["payload"] != core.parse_sysupgrade(out_sys, profile)["payload"]:
        raise PackageError("V4 factory/sysupgrade disagree")
    return out_factory, out_sys


def build_release(*, root=ROOT, output_dir=None, work_dir=None, overwrite=False):
    root = core.safe_local(root)
    kit = root / "firmware/openwrt/pbe5ac_gen2_ptp_kit"
    output = core.safe_local(output_dir or kit / "public_release_v4")
    work = core.safe_local(work_dir or root / "artifacts/verification/stage170a_build")
    if output.parent != kit or not output.name.startswith("public_release_v4"):
        raise PackageError("Output must be a dedicated public_release_v4 directory")
    if not work.is_relative_to(root / "artifacts/verification") or work == root / "artifacts/verification":
        raise PackageError("Dedicated verification workspace required")
    if output.exists() and not overwrite:
        raise PackageError("Existing output requires explicit --force")
    if work.exists():
        for p in work.rglob("*"):
            core.safe_local(p)
    evidence = load_evidence(root)
    champion = render_champion(root)
    champion_hash = core.sha256(champion)
    module = core.safe_local(kit / "mac80211_teb_4addr_v3_6.6.110.ko").read_bytes()
    if core.sha256(module) != core.V3_SHA256:
        raise PackageError("Exact mac80211 v3 module required")
    tools = core._toolchain(root / "artifacts/verification/stage117a_tools")
    payloads, boards = {}, {}
    for board, spec in core.BOARDS.items():
        profile = spec["profile"]
        paths = {kind: core.safe_local(root / "firmware/openwrt" / (spec["base_prefix"] + kind + ".bin")) for kind in ("factory", "sysupgrade")}
        inputs = {kind: path.read_bytes() for kind, path in paths.items()}
        if any(core.sha256(data) != spec["hashes"][kind] for kind, data in inputs.items()):
            raise PackageError("Official board-specific stock input mismatch")
        body = core.parse_sysupgrade(inputs["sysupgrade"], profile)["payload"]
        if core.parse_factory(inputs["factory"])["payload"] != body:
            raise PackageError("Stock payload mismatch")
        kernel = core.inspect_board_kernel(body, board)
        directory = work / board
        directory.mkdir(parents=True, exist_ok=True)
        used = core.inspect_squashfs(body[core.ROOTFS_OFFSET:])["bytes_used"]
        stock_sqfs, stock_tar = directory / "stock.squashfs", directory / "stock.tar"
        stock_sqfs.write_bytes(body[core.ROOTFS_OFFSET:core.ROOTFS_OFFSET + used])
        with stock_tar.open("wb") as h:
            core._run_tool([tools["sqfs2tar"], "-r", ".", "-L", "-s", stock_sqfs], stdout=h)
        public_tar, public_sqfs = directory / "public.tar", directory / "public.squashfs"
        inventory, module_check = _public_tar(stock_tar, public_tar, profile, module, root)
        stock_entries = core._tar_entries(stock_tar)
        dependencies = {"tc_binary_present": any(name.rsplit("/", 1)[-1] == "tc" for name in stock_entries),
            "sch_fq_module_present": any(name.endswith("/sch_fq.ko") for name in stock_entries),
            "sch_fq_builtin_or_loadable_verified": False,
            "qdisc_tester_mode_available": "UNKNOWN_REQUIRES_MATCHING_TC_AND_KERNEL_SUPPORT"}
        with public_tar.open("rb") as h:
            core._run_tool([tools["tar2sqfs"], "-f", "-q", "-s", "-c", "xz", "-b", "262144", "-j", "1", "-k", "-d", f"uid=0,gid=0,mode=0755,mtime={core.SOURCE_DATE_EPOCH}", public_sqfs], stdin=h)
        factory, image = _images(inputs["factory"], inputs["sysupgrade"], public_sqfs.read_bytes(), profile, champion_hash)
        rebuilt = core.parse_sysupgrade(image, profile)["payload"]
        if rebuilt[:core.ROOTFS_OFFSET] != body[:core.ROOTFS_OFFSET]:
            raise PackageError("Kernel prefix changed")
        for kind, data in (("factory", factory), ("sysupgrade", image)):
            payloads[f"openwrt-24.10.4-ubnt-{board}-openmax-public-{kind}.bin"] = data
        # Carve the emitted image bytes; check every path/owner/mode, not just a source TAR.
        length = core.inspect_squashfs(rebuilt[core.ROOTFS_OFFSET:])["bytes_used"]
        emitted_sqfs, emitted_tar = directory / "emitted-image.squashfs", directory / "emitted-image.tar"
        emitted_sqfs.write_bytes(rebuilt[core.ROOTFS_OFFSET:core.ROOTFS_OFFSET + length])
        with emitted_tar.open("wb") as h:
            core._run_tool([tools["sqfs2tar"], "-r", ".", "-L", "-s", emitted_sqfs], stdout=h)
        actual = audit_tar(emitted_tar, profile, root)
        if actual != inventory:
            raise PackageError("Actual emitted rootfs inventory/modes/owners differ")
        inventory_path = directory / "inventory.json"
        inventory_path.write_text(json.dumps(actual, indent=2) + "\n", encoding="utf-8")
        boards[board] = {"profile": profile, "board_ids": spec.get("board_ids", [spec["board_id"]]),
            "input_sha256": spec["hashes"], "board_kernel": kernel, "module": module_check, "qdisc_dependencies": dependencies,
            "emitted_tar_path": emitted_tar.relative_to(root).as_posix(), "emitted_tar_sha256": core.sha256(emitted_tar.read_bytes()),
            "stock_tar_path": stock_tar.relative_to(root).as_posix(), "inventory_path": inventory_path.relative_to(root).as_posix(),
            "inventory_sha256": core.sha256(inventory_path.read_bytes()), "emitted_rootfs_sha256": core.sha256(emitted_sqfs.read_bytes()),
            "emitted_rootfs_bytes_used": length, "rootfs_member_count": len(actual), "actual_inventory_equal": True}
    payloads.update({"CHAMPION_V2_EVIDENCE.json": (json.dumps(evidence, indent=2) + "\n").encode(),
        "REQUESTED_PROFILE.json": (json.dumps(REQUESTED, indent=2) + "\n").encode(),
        "OPENMAX_WA_PUBLIC_V4_TESTER_GUIDE.md": core.safe_local(root / "docs/OPENMAX_WA_PUBLIC_V4_TESTER_GUIDE.md").read_bytes(),
        "sources/package_public_wa_tester_release.py": Path(__file__).read_bytes(),
        "sources/build_public_openmax_release.py": Path(core.__file__).read_bytes(),
        "sources/public_assets/wa_champion_openwrt_body.sh": core.safe_local(kit / "public_assets/wa_champion_openwrt_body.sh").read_bytes(),
        "sources/public_assets/99-fmx-wa-universal-champion.r1-r12.source.txt": core.safe_local(kit / "public_assets/99-fmx-wa-universal-champion.r1-r12.source.txt").read_bytes(),
        "sources/" + SOURCE_NAME: core.safe_local(kit / "public_assets" / SOURCE_NAME).read_bytes(),
        "sources/COPYING.GPL-2.0": core.safe_local(kit / "public_assets/COPYING.GPL-2.0").read_bytes(),
        "modules/mac80211_teb_4addr_v3_6.6.110.ko": module})
    payloads["DEPENDENCIES.json"] = (json.dumps({b: r["qdisc_dependencies"] for b, r in boards.items()}, indent=2) + "\n").encode()
    for board, spec in core.BOARDS.items():
        for name, (data, _) in public_payloads(spec["profile"], root).items():
            payloads["sources/public_payloads/" + board + "/" + name] = data
    # Checksum both conventional filenames, without creating a self-referential manifest.
    payloads["SHA256SUMS.txt"] = core._checksum_text(payloads).encode()
    core._publish_bundle(output, payloads, overwrite)
    sums = verify_release(output)
    return {"schema_version": 1, "stage": "170A", "task_id": "T-S170A-PUBLIC-WA-TESTER-V4", "version": VERSION,
        "status": "LOCAL_PUBLIC_WA_V4_CANDIDATES_ONLY", "boards": boards, "champion_evidence": evidence,
        "requested_profile": REQUESTED, "champion_source_sha256": SOURCE_PIN, "champion_public_sha256": champion_hash,
        "outputs": {name: {"path": (output / name).relative_to(root).as_posix(), "sha256": core.sha256(data), "size_bytes": len(data)} for name, data in payloads.items()},
        "sha256sums_verified": sums, "boundaries": {"radios_contacted": [], "flash_executed": False, "published": False,
            "hardware_acceptance": False, "offload_activation_verified": False, "gpg_verified": False},
        "five_pillars": {"scope": "Offline source/container/software validation; not new RE, literature, RF acquisition or memory acceptance"}}


def verify_release(output):
    output = core.safe_local(output)
    counts, sets = {}, {}
    for filename in ("SHA256SUMS.txt", "SHA256SUMS"):
        seen = set()
        for line in core.safe_local(output / filename).read_text(encoding="ascii").splitlines():
            digest, name = line.split("  ", 1)
            parsed = PurePosixPath(name)
            if parsed.is_absolute() or ".." in parsed.parts or "\\" in name:
                raise PackageError("Unsafe checksum path")
            path = core.safe_local(output / name)
            if not path.is_relative_to(output) or name in seen or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise PackageError("Unsafe/duplicate checksum entry")
            seen.add(name)
            if core.sha256(path.read_bytes()) != digest:
                raise PackageError("Checksum mismatch")
        counts[filename] = len(seen)
        sets[filename] = seen
    actual = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
    if actual != sets["SHA256SUMS"] | {"SHA256SUMS"} or sets["SHA256SUMS.txt"] != actual - {"SHA256SUMS", "SHA256SUMS.txt"}:
        raise PackageError("Release inventory differs from manifest")
    return {"verified": True, "entry_counts": counts}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--work-dir", type=Path, default=DEFAULT_WORK)
    p.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    p.add_argument("--force", action="store_true")
    args = p.parse_args(argv)
    try:
        receipt_path = core.safe_local(args.receipt)
        if receipt_path.parent != ROOT / "artifacts/autoresearch" or not receipt_path.name.startswith("stage170a_") or receipt_path.suffix != ".json":
            raise PackageError("Dedicated Stage170A receipt required")
        receipt = build_release(output_dir=args.output_dir, work_dir=args.work_dir, overwrite=args.force)
        receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    except (OSError, ValueError, core.subprocess.SubprocessError) as error:
        print(f"Stage170A failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"stage": "170A", "receipt": receipt_path.relative_to(ROOT).as_posix(), "images": 8, "sha256sums_verified": receipt["sha256sums_verified"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
