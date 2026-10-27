#!/usr/bin/env python3
"""Package saved LTU 12X/LDPC evidence and a guarded br1 DHCP shield."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.firmware.build_stage817a_universal_pb060_triple_patch_openwrt_airos_kit import local, sha, pillars, write_report, package_files

STEM = "stage818a_ltu_4096qam_12x_ldpc_and_super4096_safe_kit"
HELPER = "firmware/ltu_safe_kit/fmx_ltu_4096qam_12x_safe_kit.sh"
SOURCES = (
    "artifacts/autoresearch/stage651a_ltu_4096qam_ldpc_and_phase_noise_tracker_re.json",
    "artifacts/autoresearch/stage546a_ltu_tx_power_lut_dpd_and_super4096_helper.json",
)


def blocks_dhcp_offer(bridge: str, chain: str, protocol: str, source_port: int, destination_port: int) -> bool:
    """Model the proposed br1 rule, not a statement about a running firewall."""
    return (bridge == "br1" and chain in ("OUTPUT", "FORWARD") and protocol == "udp"
            and (source_port, destination_port) in ((67, 68), (547, 546)))


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    package = local(root, "artifacts/autoresearch/kits/stage818a")
    package.mkdir(parents=True, exist_ok=True)
    helper = local(root, HELPER).read_bytes()
    (package / "fmx_ltu_4096qam_12x_safe_kit.sh").write_bytes(helper)
    evidence, missing, modules = [], [], []
    sums = [f"{sha(helper)}  fmx_ltu_4096qam_12x_safe_kit.sh"]
    for label in SOURCES:
        path = local(root, label)
        if not path.is_file():
            missing.append(label)
            continue
        data = path.read_bytes()
        source = json.loads(data)
        (package / path.name).write_bytes(data)
        evidence.append({"path": label, "sha256": sha(data), "bytes": len(data), "producer_executed": False})
        sums.append(f"{sha(data)}  {path.name}")
        if "builds_dissected" in source:
            for build_row in source["builds_dissected"]:
                for key in ("ame_core_ko", "ame_dev_ko"):
                    record = build_row.get(key, {})
                    if not record:
                        continue
                    module = local(root, record["path"])
                    digest = sha(module.read_bytes()) if module.is_file() else None
                    modules.append({"path": record["path"], "sha256": digest,
                                    "recorded_sha256": record.get("sha256"),
                                    "matches_saved_re": digest is not None and digest == record.get("sha256")})
    (package / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="ascii", newline="\n")
    matched = bool(modules) and all(item["matches_saved_re"] for item in modules)
    report = {"stage": "818A", "status": "CONFIRMED" if not missing and matched else "UNKNOWN",
              "execution_mode": "OFFLINE_PACKAGING", "claim_scope": "saved RE provenance and DHCP policy model only",
              "attribution": ["Linux", "proprietary airMAX/LTU module", "external controller"],
              "source_evidence": evidence, "missing_inputs": missing, "module_provenance": modules,
              "helper_script": HELPER, "helper_sha256": sha(helper),
              "package_files": package_files(root, package),
              "ltu_features": {"qam4096_12x": "saved static symbol/table evidence", "ldpc": "saved static evidence",
                               "super4096": "saved static symbols; activation UNKNOWN", "modulation_unlocked": False},
              "rogue_dhcp_remediation": {"interface": "br1", "fallback_ip": "192.168.1.20",
                  "policy": "proposed OUTPUT/FORWARD UDP 67->68 and 547->546 drop on br1 only",
                  "policy_model_verified": all(blocks_dhcp_offer("br1", chain, "udp", port, dest)
                                               for chain in ("OUTPUT", "FORWARD") for port, dest in ((67, 68), (547, 546))),
                  "unrelated_dhcp_preserved_in_model": not blocks_dhcp_offer("br0", "OUTPUT", "udp", 67, 68),
                  "rogue_leases_emitted": None, "zero_rogue_dhcp_verified": False,
                  "runtime_acceptance": "UNKNOWN", "apply_available": True,
                  "apply_executed": False, "persistence_verified": False,
                  "apply_guard": "uid0, explicit confirmation, exact br1 address, known backend, own-chain readback and rollback"},
              "boundary": {"network_access": False, "live_devices_touched": False, "dev_ame_touched": False,
                           "target_commands_executed": False, "protected_partitions_modified": False,
                           "physical_acceptance": False},
              "five_pillar_compliance": pillars("stage818a")}
    return write_report(root, STEM, report, f"""<!-- doc-head: Stage818A static LTU 12X LDPC provenance and br1-only DHCP shield plan -->
<!-- /doc-head -->
# Stage 818A LTU 4096QAM 12X / LDPC / Super4096 safe kit

`{report['status']}` applies to offline packaging only. Attribution: `Linux` / `proprietary airMAX/LTU module`.
Saved Stage651A and Stage546A receipts are hashed and copied into `artifacts/autoresearch/kits/stage818a`.
The RE module hashes are rechecked against actual local files; no producer or radio was executed.
4096QAM/12X tables, LDPC and Super4096 symbols are static evidence, not an unlock or radio acceptance.
The shell helper defaults to inspection, reports unavailable telemetry UNKNOWN and rejects modulation activation.
`--plan-zero-dhcp` prints a proposed br1-only filter; it executes no firewall command or daemon stop.
`--apply-zero-dhcp --confirm-br1-192.168.1.20` is packaged but was exercised only with local command stubs.
It requires uid0, exact br1 fallback address and a known ebtables backend; only its dedicated chain and
br1-only OUTPUT/FORWARD first-rule jumps change, preceding existing ACCEPT rules. Repeats require exact
rule and first-position readback; partial failures roll back.
Unrelated firewall chains, DHCP daemons and client requests remain untouched. No persistent service is installed.
The policy model blocks DHCPv4/v6 server offers on br1 in OUTPUT/FORWARD and preserves br0 DHCP.
The target fallback identity is `br1` / `192.168.1.20`. Actual service binding and firewall behavior remain UNKNOWN.
`zero_rogue_dhcp_verified=false`; no observed lease count is invented. A future authorized bench must test leases,
daemon respawn, restart persistence, unrelated LAN DHCP, IPv4/IPv6 and rollback before deployment.
No `/dev/ame*`, firmware, calibration, modem, LDPC, modulation or transmit-power writes are provided.
No SSH, live measurement, online scholar query or durable MemoryMaster ingestion occurred.
""")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    result = build(parser.parse_args().root)
    print(f"Stage818A offline kit: {result['status']}; zero-rogue-DHCP runtime=UNKNOWN")
    return 0 if result["status"] == "CONFIRMED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
