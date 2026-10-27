#!/usr/bin/env python3
"""Describe a v22 LTU safe source kit; ATPC/DFS/GPS activation stays unavailable."""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.firmware import build_stage849a_universal_wa_xc_xw_v22_release_matrix as matrix

STEM = 'stage850a_ltu_safe_kit_v22_atpc_and_dfs_guard'
REQUIRED_SOURCES = (
    'firmware/ltu_safe_kit/fmx_ltu_4096qam_12x_safe_kit.sh',
    'tools/re/dissect_stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.py',
    'tools/verify/stage779_822_offline_common.py',
)
OPTIONAL_REFERENCES = (
    'artifacts/autoresearch/stage834a_ltu_ame_core_ul_power_control_and_target_evm_re.json',
    'artifacts/autoresearch/stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.json',
    'artifacts/autoresearch/stage818a_ltu_4096qam_12x_ldpc_and_super4096_safe_kit.json',
)


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    sources = matrix.required_sources(root, REQUIRED_SOURCES)
    optional = matrix.optional_references(root, OPTIONAL_REFERENCES)
    features = {
        'ATPC': dict(status='UNKNOWN', activation_available=False,
                     reason='Static references do not establish a validated power-control actuator'),
        'DFS': dict(status='UNKNOWN', activation_available=False,
                    reason='Classifier symbol presence does not prove pulse thresholds or regulatory behavior'),
        'GPS': dict(status='UNKNOWN', activation_available=False,
                    reason='No lock, timing or holdover observation is acquired by this manifest'),
        'BR1_DHCP': dict(status='UNKNOWN', activation_available=False,
                         reason='Existing guarded helper is referenced; no native firewall or lease test is executed'),
    }
    report = matrix.emit(root, 850, STEM, 'LTU v22 ATPC and DFS safe source kit', sources,
        dict(artifact_type='SOURCE_SAFE_KIT_MANIFEST', features=features,
             helper_reference=REQUIRED_SOURCES[0], optional_references=optional,
             optional_availability_definition='Eligible clean tracked JSON, not mere local presence',
             guard_policy=dict(default='MANIFEST_ONLY', actions_dispatched=0,
                 atpc_enable=False, dfs_disable=False, gps_lock_claim=False,
                 required_before_future_activation=['Exact board/revision/driver/firmware identity',
                     'Independent reviewed actuator and rollback contract',
                     'Actual readback and captured ATPC/DFS/GPS observations',
                     'Explicit authority for the proposed device action']),
             producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),
        'v22 is an offline source kit manifest, not an LTU physical champion or installable firmware.\n'
        'Mandatory references are clean tracked text sources with real byte hashes and Git blob IDs.\n'
        'The existing guarded LTU helper and static DFS analyzer are only referenced, never executed.\n'
        'ATPC control law, DFS threshold behavior, GPS lock and live zero-rogue-DHCP remain UNKNOWN.\n'
        'No enable/unlock/disable command, firmware payload, ASIC ioctl or radio transport is provided.\n'
        'Optional historical receipts may be missing or excluded without inventing compatibility evidence.\n'
        'Future activation requires an independently reviewed exact-identity actuator, rollback, readback and authority.\n'
        'No network, device, Git mutation, proprietary binary packaging or durable memory write occurs.\n')
    return report


def main() -> int:
    result = build()
    print(f'{STEM}: features={len(result["features"])}; activation=UNAVAILABLE; runtime=UNKNOWN')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
