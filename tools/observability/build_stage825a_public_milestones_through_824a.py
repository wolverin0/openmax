#!/usr/bin/env python3
"""Audit six public milestone pages against saved receipts; never publish."""
from pathlib import Path
import hashlib
import json
import re
import unicodedata
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c

STEM = 'stage825a_public_milestones_through_824a'
PAGES = (
    'README.md', 'docs/DOCS-MAP.md', 'docs/CURRENT_STATE.md', 'docs/REDDIT_POST.md',
    'docs/GUIA_UNIVERSAL_POWERBEAM_LITEBEAM_OPENMAX.md',
    'docs/REDDIT_REPLY_FIRMWARE_TESTERS_WA_FAMILY.md',
)
INPUTS = (
    'stage773a_wa_champion_v13_344window_field_rollout_kit',
    'stage774a_ltu_champion_v20_264window_zero_dhcp_kit',
    'stage741a_pbe5ac_lbe5ac_vht40_pb050_production_bundle_v5',
    'stage817a_universal_pb060_triple_patch_openwrt_airos_kit',
    'stage818a_ltu_4096qam_12x_ldpc_and_super4096_safe_kit',
    'stage819a_guarida_tower_v10_triple_patch_and_xw_mixed_tdma_pareto',
    'stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re',
    'stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re',
)
DEFAULT_SETUP_IPS = {'192.168.1.20', '192.168.1.10', '192.168.1.0'}
REQUIRED = ('824A', 'WA v13', '78.51 Mbps', '-86.37%', 'PtP', '25.47 Mbps',
            'PBE-5AC-Gen2', 'LBE-5AC-Gen2', 'PB040', 'PB050', 'PB060',
            'LTU v20', '264', '818A', 'stubs', 'Guarida v10', '819A',
            '823A', 'ubntspecd', 'BPS', 'SCORE', 'RATING', 'ame_dfs.ko', 'UNKNOWN')


def fingerprint(value: str) -> str:
    normalized = unicodedata.normalize('NFKC', value).casefold()
    return hashlib.sha256(' '.join(normalized.split()).encode('utf-8')).hexdigest()


def local_identity_hashes(root=ROOT) -> set[str]:
    # Optional operator policy stays in local Git metadata, outside public source.
    policy = Path(root) / '.git/stage826a/private_terms.json'
    if not policy.is_file():
        return set()
    terms = json.loads(policy.read_text(encoding='utf-8-sig'))
    if not isinstance(terms, list) or any(not isinstance(term, str) for term in terms):
        raise ValueError('invalid local identity policy')
    return {fingerprint(term) for term in terms if len(term) >= 4}


def has_private_identity(text: str, hashes: set[str]) -> bool:
    words = re.findall(r"[\w'-]+", unicodedata.normalize('NFKC', text).casefold())
    return any(fingerprint(' '.join(words[i:i+size])) in hashes
               for size in range(1, 5) for i in range(len(words) - size + 1))


def audit_page(text: str, label: str, private_identity_hashes=None) -> list[str]:
    failures = []
    if (len(text.splitlines()) >= 180 or not text.startswith('<!-- doc-head:')
            or text.count('<!-- doc-head:') != 1 or text.count('<!-- /doc-head -->') != 1):
        failures.append('document budget/paired header')
    for token in REQUIRED:
        if token not in text:
            failures.append('missing milestone token: ' + token)
    for address in re.findall(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])', text):
        if address not in DEFAULT_SETUP_IPS:
            failures.append('private/nondefault address must be removed')
    if re.search(r'(?i)(?<![\w])(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}(?![\w])', text):
        failures.append('MAC address must be removed')
    policy_hashes = local_identity_hashes() if private_identity_hashes is None else set(private_identity_hashes)
    if has_private_identity(text, policy_hashes):
        failures.append('customer identity must be removed')
    for target in re.findall(r'\]\(([^)]+)\)', text):
        # Existing history-router links are preserved, not disclosure destinations.
        if target.startswith('CURRENT_STATE_CONTINUATION_'):
            continue
        if (re.search(r'(?i)(?:^|/)AGENTS\.md(?:#|$)', target)
                or 'artifacts/documentation/' in target or 'artifacts/verification/' in target):
            failures.append('private operational/archive destination must not be linked publicly')
        if re.search(r'(?i)hackerone|bounty|dossier|amedev.*report', target):
            failures.append('disclosure destination must not be linked publicly')
    if re.search(r'(?i)(?:100%|universal)\s+(?:runtime\s+)?compatibility\s+(?:is\s+)?(?:confirmed|guaranteed)', text):
        failures.append('unsupported universal compatibility claim')
    if re.search(r'(?i)(?:password|token|api[_-]?key)\s*[:=]\s*[A-Za-z0-9_/-]{8,}', text):
        failures.append('possible embedded credential')
    if 'Stage775A/v9' not in text or '514.80' not in text or 'not measured' not in text:
        failures.append('Guarida v9/v10 evidence separation missing')
    if 'formula' not in text or 'PW/PRI' not in text or 'LNA' not in text:
        failures.append('RE limitations missing')
    return sorted(set(failures))


def build(root=ROOT):
    root = Path(root)
    sources = [c.snapshot(root, label) for label in PAGES]
    rows = []
    for label in PAGES:
        path = c.local(root, label)
        text = path.read_text(encoding='utf-8-sig') if path.is_file() else ''
        failures = audit_page(text, label)
        rows.append(dict(path=label, lines=len(text.splitlines()), compliant=not failures, failures=failures))
    receipts = {}
    for stem in INPUTS:
        label = f'artifacts/autoresearch/{stem}.json'
        sources.append(c.snapshot(root, label))
        receipts[stem] = c.read_json(root, label)
    wa = receipts[INPUTS[0]]['verified_metrics']
    ptp = receipts[INPUTS[2]]['verified_capabilities']
    ltu = receipts[INPUTS[1]]
    triple = receipts[INPUTS[3]]
    shield = receipts[INPUTS[4]]
    sim = receipts[INPUTS[5]]
    air = receipts[INPUTS[6]]['summary']
    dfs = receipts[INPUTS[7]]['summary']
    milestones = dict(
        wa_v13=dict(reported_peak_vht20_mbps=wa['vht20_peak_tcp_mbps'],
                    reported_loaded_p50_reduction_pct=wa['loaded_p50_rtt_reduction_e2e_mk1_251_pct'],
                    independently_remeasured=False),
        ptp_v5=dict(reported_peak_vht40_mbps=ptp['vht40_peak_tcp_mbps'],
                    board_profiles=['PBE-5AC-Gen2', 'LBE-5AC-Gen2'], runtime_compatibility='UNKNOWN'),
        triple_patch=dict(offline_images=len(triple['images']), runtime_acceptance='UNKNOWN'),
        ltu_v20=dict(reported_windows=ltu['cumulative_ltu_windows'],
                    guarded_dhcp_apply_packaged=shield['rogue_dhcp_remediation']['apply_available'],
                    zero_rogue_dhcp_runtime=shield['rogue_dhcp_remediation']['runtime_acceptance']),
        guarida_v10=dict(status=sim['status'], calibrated=sim['model']['calibrated'], measured_mbps=None),
        stage823a=dict(scoring_tiers=air['scoring_tiers'], coefficients_recovered=air['formula_coefficients_recovered']),
        stage824a=dict(classifier_in_dfs_module=dfs['classifier_in_dfs_module'],
                       pw_pri_table_recovered=dfs['pw_pri_table_recovered'],
                       lna_immunity_recovered=dfs['lna_saturation_immunity_recovered']),
    )
    source_contract = (milestones['wa_v13']['reported_peak_vht20_mbps'] == 78.51
                       and milestones['wa_v13']['reported_loaded_p50_reduction_pct'] == 86.37
                       and milestones['ptp_v5']['reported_peak_vht40_mbps'] == 25.47
                       and milestones['ltu_v20']['reported_windows'] == 264
                       and milestones['triple_patch']['offline_images'] == 7
                       and milestones['ltu_v20']['zero_rogue_dhcp_runtime'] == 'UNKNOWN'
                       and not milestones['guarida_v10']['calibrated']
                       and milestones['stage823a']['coefficients_recovered'] == 0
                       and milestones['stage824a']['pw_pri_table_recovered'] == 0
                       and milestones['stage824a']['lna_immunity_recovered'] == 0)
    sources.extend(c.snapshot(root, p) for p in (
        'tools/observability/build_stage825a_public_milestones_through_824a.py',
        'tests/test_stage825a_public_docs.py'))
    data = c.receipt(825, 'Public milestones through824A: source-qualified documentation', sources)
    data.update(execution_mode='OFFLINE_DOCUMENTATION', public_pages=rows, milestones=milestones,
                source_contract=source_contract, compliant=source_contract and all(r['compliant'] for r in rows),
                publication_performed=False, radio_access_performed=False, physical_acceptance='UNKNOWN')
    data['status'] = 'CONFIRMED' if data['compliant'] else 'FAILED'
    return c.save(root, STEM, data, '# Six public pages\n\n'
                  'Milestones through Stage824A are reconciled from saved receipts, not new hardware trials.\n'
                  'WA/PtP/LTU values remain source-reported. Exact board profiles are metadata, not universal RF acceptance.\n'
                  'Stage817A triple composition is local; Stage818A DHCP apply was tested with command stubs only.\n'
                  'Guarida v10 is uncalibrated sensitivity;514.80Mbps belongs to the earlier Stage775A/v9 source claim.\n'
                  'Stage823A exposes scoring labels, not coefficients. Stage824A identifies ame_dfs symbols,\n'
                  'not numeric PW/PRI thresholds or proven LNA-saturation immunity.\n'
                  'Page budgets, paired doc-head, default-setup-only addresses, MAC/customer data, disclosure links\n'
                  'and milestone qualifications are checked. Historical CURRENT_STATE hrefs remain intact.\n'
                  'No Reddit post, upload, radio action or durable MemoryMaster ingestion occurred.\n')


def main():
    result = build()
    print(f'{STEM}: compliant={result["compliant"]}; pages={len(result["public_pages"])}')
    for row in result['public_pages']:
        if not row['compliant']:
            print(row['path'], row['failures'])
    return 0 if result['compliant'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
