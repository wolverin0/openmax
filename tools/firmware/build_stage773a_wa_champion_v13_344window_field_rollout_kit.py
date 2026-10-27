#!/usr/bin/env python3
"""Package the canonical, fail-closed WA queue helper; historical claims stay imported."""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c

HELPER_REL = 'firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh'
HELPER_PATH = ROOT / HELPER_REL
STEM = 'stage773a_wa_champion_v13_344window_field_rollout_kit'
RECEIPT_PATH = ROOT / f'artifacts/autoresearch/{STEM}.json'
DOC_PATH = ROOT / f'docs/{STEM.upper()}.md'


def build_helper_script(root: Path = ROOT) -> str:
    """The maintained shell file is the single source; never regenerate a legacy copy."""
    text = c.local(Path(root), HELPER_REL).read_text(encoding='utf-8')
    if ('PLANNED' not in text or 'APPLIED_VERIFIED' not in text
            or '_KIT_OK' in text or '|| true' in text or 'initial_quantum' in text):
        raise ValueError('canonical WA helper safety contract')
    return text


def build(root: Path = ROOT) -> dict:
    root = Path(root)
    text = build_helper_script(root)
    history = dict(vht20_peak_tcp_mbps=78.51, vht20_mean_tcp_mbps=76.55,
                   loaded_p50_rtt_reduction_e2e_mk1_251_pct=86.37)
    data = c.receipt(773, 'WA v13 identity-bound transient queue kit', [c.snapshot(root, HELPER_REL)])
    data.update(execution_mode='OFFLINE_PACKAGING', helper_script=HELPER_REL,
                helper_sha256=hashlib.sha256(text.encode()).hexdigest(), champion_version='WA-Champion-v13',
                runtime_acceptance='UNKNOWN', target_patch_execution='UNKNOWN',
                historical_reported_windows=344, historical_reported_metrics=history,
                historical_claim_scope='Imported Stage773A summary; not remeasured or independently reaccepted',
                dhcp_services_changed=False, profile_scope='Transient AQL/BQL/pktlog/fq_codel/three sysctls only',
                apply_contract=dict(default='PLANNED', explicit_apply=True,
                    identity_fields=['board','revision','kernel','driver','firmware','radio','phy','egress',
                                     'radio_ifindex','egress_ifindex','fingerprint'],
                    exact_getters_required=True, snapshot_required=True, rollback_readback_required=True,
                    states=['PLANNED','FAILED_PRECONDITION','APPLIED_VERIFIED','FAILED_ROLLED_BACK','ROLLBACK_FAILED']),
                evidence_limitations=['Command stubs establish software control flow only.',
                    'Missing board_revision getter or unsupported fq_codel output refuses application.',
                    'No PB040/PB050/PB060 target execution, hardware QoE, coldboot or power-cut proof.',
                    'Snapshot restores configuration, not already queued packets or driver counters.'])
    data['attribution'] = ['Linux','mac80211','ath10k']
    return c.save(root, STEM, data, 'Default/inspect/dry-run returns PLANNED without getters or writes.\n'
        'Explicit --apply requires --identity FILE and --state-dir ABSOLUTE_DIRECTORY.\n'
        'Identity is eleven unique key=value records: ten exact getter fields and their SHA256 fingerprint.\n'
        'Fingerprint input is the ten fields in receipt order, one UTF-8 value per line with final newline.\n'
        'board_revision must be exposed by ubus system board; unavailable revision means refusal.\n'
        'Snapshots cover four AQL ACs, pktlog_filter, BQL limit_max, complete supported root fq_codel\n'
        'configuration/handle and all three sysctls. Unknown options, child qdiscs or auto handle0 refuse apply.\n'
        'The qdisc remains fq_codel, with supported quantum/target/interval options; no switch to fq.\n'
        'Errors trigger restoration/readback: FAILED_ROLLED_BACK or ROLLBACK_FAILED, never decorative success.\n'
        '--rollback with the same identity/state-dir restores the retained snapshot idempotently.\n'
        'No DHCP/UCI/service persistence, firmware patch loader or device access occurs during packaging.\n'
        '344 windows,78.51/76.55Mbps and86.37% loaded-p50 reduction are imported historical claims only.\n'
        'Actual radio behavior and runtime acceptance remain UNKNOWN.\n')


def main() -> int:
    build()
    print('Stage773A LOCAL_PACKAGED runtime=UNKNOWN historical_claims=IMPORTED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
