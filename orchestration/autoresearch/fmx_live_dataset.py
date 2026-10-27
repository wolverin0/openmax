"""Frozen R1-R92 saved-evidence corpus; no acquisition or device operations.

The established offline normalizer and its revision APIs remain unchanged.
This additive interface authenticates the previous sealed corpus and every
new input. Recipe bytes are provenance only and are never imported/executed.
Declared timing distances do not establish physical RF separation.
"""
from copy import deepcopy
from dataclasses import asdict, replace
import ast
import csv
import io
import re
import hashlib
import json
from pathlib import Path

import numpy as np

from orchestration.autoresearch import fmx_offline_data as old

ROOT = old.ROOT
ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_ak_to_an_20261024'
INPUTS = ARTIFACTS / 'inputs'
INPUT_MANIFEST = ARTIFACTS / 'inputs_manifest.json'
INPUT_MANIFEST_SHA256 = '88c7b54b781e53b9747d704ea75a880f85984aa4a335fe36c06f8042bb5c9bef'
PRIOR = old.AGAJ_ARTIFACTS
R47_RECORDS = PRIOR / 'normalized_r1_to_r47_measurements_20261024.json'
R47_BLOCKS = PRIOR / 'normalized_r16_to_r47_block_observations_20261024.json'
R47_VALIDATION = PRIOR / 'final_validation.json'
PRIOR_VALIDATION_SHA256 = '3b2a343722cd6e258e375172424607a52d0e5cd03363a2a076673f8dfa153d5d'
RECORDS_OUTPUT = ARTIFACTS / 'normalized_r1_to_r56_measurements_20261024.json'
BLOCKS_OUTPUT = ARTIFACTS / 'normalized_r16_to_r56_block_observations_20261024.json'

# filename, source regime, flows, direction, declared timing meters/class
ROUND_SPECS = {
    48: ('lap120_loco195_r48_covclass6_3km_abba16_dyadic_zero_loss_wds_20261024.json', 'covclass6_3km_bidir_6flow', 6, True, 3000, 6),
    49: ('lap120_loco195_r49_covclass13_6km_abba16_dyadic_zero_loss_wds_20261024.json', 'covclass13_6km_bidir_6flow', 6, True, 6000, 13),
    50: ('lap120_loco195_r50_bidir_6flow_be1500_2100_retry74_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, None, None),
    51: ('lap120_loco195_r51_bidir_6flow_be1500_2100_retry53_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, None, None),
    52: ('lap120_loco195_r52_covclass6_3km_be1500_2100_af3_retry53_abba16_dyadic_zero_loss_wds_20261024.json', 'covclass6_3km_bidir_6flow', 6, True, 3000, 6),
    53: ('lap120_loco195_r53_covclass13_6km_be1500_2100_af1_retry53_abba16_dyadic_zero_loss_wds_20261024.json', 'covclass13_6km_bidir_6flow', 6, True, 6000, 13),
    54: ('lap120_loco195_r54_bidir_2flow_symaf1_retry53_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_2flow', 2, True, None, None),
    55: ('lap120_loco195_r55_bidir_4flow_be1500_2100_af1_retry53_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_4flow', 4, True, None, None),
    56: ('lap120_loco195_r56_bidir_2flow_be1500_2100_af1_retry53_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_2flow', 2, True, None, None),
}
R48_TO_R56_RECEIPTS = tuple(INPUTS / spec[0] for spec in ROUND_SPECS.values())
R56_RECORDS_OUTPUT, R56_BLOCKS_OUTPUT = RECORDS_OUTPUT, BLOCKS_OUTPUT
AO_ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_ao_to_ar_20261024'
AO_INPUT_MANIFEST = AO_ARTIFACTS / 'inputs_manifest.json'
AO_MANIFEST_SHA256 = '5844355bb99e2dbc41c83cfb34c7c03ff5d6992679d19367470e3c761ab448d8'
R56_VALIDATION = ARTIFACTS / 'final_validation.json'
R56_VALIDATION_SHA256 = '79dfef317ca905da568510f298f7ff7f64abe3acfc69c0647c34f979ec17b92b'
ROUND60_SPECS = {
    57: ('lap120_loco195_r57_bidir_8flow_be1500_2100_af3_retry53_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_8flow', 8, True, 100, 0),
    58: ('lap120_loco195_r58_bidir_6flow_be1750_2100_af1_retry53_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 100, 0),
    59: ('lap120_loco195_r59_bidir_6flow_be1550_2100_rc24_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 100, 0),
    60: ('lap120_loco195_r60_bidir_6flow_be1520_2100_codel8_rc24_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 100, 0),
}
R57_TO_R60_RECEIPTS = tuple(AO_ARTIFACTS / 'inputs' / spec[0] for spec in ROUND60_SPECS.values())
RECORDS_OUTPUT = AO_ARTIFACTS / 'normalized_r1_to_r60_measurements_20261024.json'
BLOCKS_OUTPUT = AO_ARTIFACTS / 'normalized_r16_to_r60_block_observations_20261024.json'
R60_RECORDS_OUTPUT, R60_BLOCKS_OUTPUT = RECORDS_OUTPUT, BLOCKS_OUTPUT
R60_VALIDATION = AO_ARTIFACTS / 'final_validation.json'
R60_VALIDATION_SHA256 = '8c8577c95704bce0e1d0941b46e995aaa6a706fbb9e5c875d786bd4c233944a7'
AS_ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_as_to_av_20261024'
AS_INPUT_MANIFEST = AS_ARTIFACTS / 'inputs_manifest.json'
AS_MANIFEST_SHA256 = '902990cb6d38ca0ae66b0b78f375e16fb1bb6fecb22b4ae364b28aedd8a30ee4'
ROUND65_SPECS = {
    61: ('lap120_loco195_r61_covclass6_3km_be1520_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'covclass6_3km_bidir_6flow', 6, True, 3000, 6),
    62: ('lap120_loco195_r62_covclass13_6km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'covclass13_6km_bidir_6flow', 6, True, 6000, 13),
    63: ('lap120_loco195_r63_bidir_8flow_be1520_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_8flow', 8, True, 100, 0),
    64: ('lap120_loco195_r64_bidir_4flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_4flow', 4, True, 100, 0),
    65: ('lap120_loco195_r65_bidir_6flow_be1520_2100_codel8_rc22_retry54_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 100, 0),
}
R61_TO_R65_RECEIPTS = tuple(AS_ARTIFACTS / 'inputs' / spec[0] for spec in ROUND65_SPECS.values())
RECORDS_OUTPUT = AS_ARTIFACTS / 'normalized_r1_to_r65_measurements_20261024.json'
BLOCKS_OUTPUT = AS_ARTIFACTS / 'normalized_r16_to_r65_block_observations_20261024.json'
R65_RECORDS_OUTPUT, R65_BLOCKS_OUTPUT = RECORDS_OUTPUT, BLOCKS_OUTPUT
R65_VALIDATION = AS_ARTIFACTS / 'final_validation.json'
R65_VALIDATION_SHA256 = '260d0827b6e1d624023cec51d0cfc645c4ec95637b17b42df6fe7cfb294eed68'
AW_ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_aw_to_az_20261024'
AW_INPUT_MANIFEST = AW_ARTIFACTS / 'inputs_manifest.json'
AW_MANIFEST_SHA256 = 'fe47335f7b73c31f394d894bf246926bb4a2e79fd50efc67a28960578416df89'
ROUND70_SPECS = {
    66: ('lap120_loco195_r66_bidir_2flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_2flow', 2, True, 100, 0),
    67: ('lap120_loco195_r67_bidir_8flow_be1480_2100_codel7_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_8flow', 8, True, 100, 0),
    68: ('lap120_loco195_r68_covclass10_4500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 4500, 10),
    69: ('lap120_loco195_r69_covclass20_9km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 9000, 20),
    70: ('lap120_loco195_r70_covclass10_4500m_be1560_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 4500, 10),
}
R66_TO_R70_RECEIPTS = tuple(AW_ARTIFACTS / 'inputs' / spec[0] for spec in ROUND70_SPECS.values())
RECORDS_OUTPUT = AW_ARTIFACTS / 'normalized_r1_to_r70_measurements_20261024.json'
BLOCKS_OUTPUT = AW_ARTIFACTS / 'normalized_r16_to_r70_block_observations_20261024.json'
R70_RECORDS_OUTPUT, R70_BLOCKS_OUTPUT = RECORDS_OUTPUT, BLOCKS_OUTPUT
R70_VALIDATION = AW_ARTIFACTS / 'final_validation.json'
R70_VALIDATION_SHA256 = '716e3938b63d4ffb7dedf72bea3bd544efc545e149a975ac99378abe7c3b165d'
BA_ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_ba_to_bd_20261024'
BA_INPUT_MANIFEST = BA_ARTIFACTS / 'inputs_manifest.json'
BA_MANIFEST_SHA256 = 'c6a834e9436c9b442468492a112d1bc850831d9fc85fa06daec3f3a9289e73ae'
ROUND75_SPECS = {
    71: ('lap120_loco195_r71_bidir_2flow_be1350_2200_codel6_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_2flow', 2, True, 100, 0),
    72: ('lap120_loco195_r72_bidir_8flow_be1520_2100_codel7_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_8flow', 8, True, 100, 0),
    73: ('lap120_loco195_r73_covclass27_12km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 12000, 27),
    74: ('lap120_loco195_r74_bidir_8flow_be1510_2150_codel5_vo900_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_8flow', 8, True, 100, 0),
    75: ('lap120_loco195_r75_covclass33_15km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 15000, 33),
}
R71_TO_R75_RECEIPTS = tuple(BA_ARTIFACTS / 'inputs' / spec[0] for spec in ROUND75_SPECS.values())
RECORDS_OUTPUT = BA_ARTIFACTS / 'normalized_r1_to_r75_measurements_20261024.json'
BLOCKS_OUTPUT = BA_ARTIFACTS / 'normalized_r16_to_r75_block_observations_20261024.json'

R75_RECORDS_OUTPUT, R75_BLOCKS_OUTPUT = RECORDS_OUTPUT, BLOCKS_OUTPUT
R75_VALIDATION = BA_ARTIFACTS / 'final_validation.json'
R75_VALIDATION_SHA256 = 'd519448c7967b08c5935860bb63d4cb9c0dcfac57a2afc144c11203f54fce31a'
BE_ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_be_to_bh_20261024'
BE_INPUT_MANIFEST = BE_ARTIFACTS / 'inputs_manifest.json'
BE_MANIFEST_SHA256 = '98a66e5a52a7e952e02843bf3b0d2a80b78491df1cafd633db517fc346f6beef'
ROUND80_SPECS = {
    76: ('lap120_loco195_r76_covclass3_1500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 1500, 3),
    77: ('lap120_loco195_r77_covclass16_7500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 7500, 16),
    78: ('lap120_loco195_r78_covclass23_10500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 10500, 23),
    79: ('lap120_loco195_r79_covclass30_13500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 13500, 30),
    80: ('lap120_loco195_r80_covclass16_7500m_be1540_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 7500, 16),
}
R76_TO_R80_RECEIPTS = tuple(BE_ARTIFACTS / 'inputs' / spec[0] for spec in ROUND80_SPECS.values())
RECORDS_OUTPUT = BE_ARTIFACTS / 'normalized_r1_to_r80_measurements_20261024.json'
BLOCKS_OUTPUT = BE_ARTIFACTS / 'normalized_r16_to_r80_block_observations_20261024.json'



BI_ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_bi_to_bl_20261024'
BI_INPUT_MANIFEST = BI_ARTIFACTS / 'inputs_manifest.json'
BI_MANIFEST_SHA256 = '529168c4a6a8070ae29b0984c73ee8fef44a9e6583f9517594a121a9479a7778'
ROUND86_SPECS = {
    81: ('lap120_loco195_r81_unidir_dl_2flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'unidir_dl_2flow', 2, False, 100, 0),
    82: ('lap120_loco195_r82_unidir_ul_2flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'unidir_ul_2flow', 2, False, 100, 0),
    83: ('lap120_loco195_r83_bidir_4flow_covclass6_3000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_4flow', 4, True, 3000, 6),
    84: ('lap120_loco195_r84_bidir_4flow_covclass13_6000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_4flow', 4, True, 6000, 13),
    85: ('lap120_loco195_r85_covclass16_7500m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 7500, 16),
    86: ('lap120_loco195_r86_bidir_4flow_covclass20_9000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_4flow', 4, True, 9000, 20),
}
R81_TO_R86_RECEIPTS = tuple(BI_ARTIFACTS / 'inputs/artifacts/autoresearch' / spec[0] for spec in ROUND86_SPECS.values())
R80_RECORDS_OUTPUT, R80_BLOCKS_OUTPUT = RECORDS_OUTPUT, BLOCKS_OUTPUT
R80_VALIDATION = BE_ARTIFACTS / 'final_validation.json'
R80_VALIDATION_SHA256 = '1848112227501ace2ec6fcac2eaad53d8b78bd018ac41810ef5ce78dbd7a1876'
RECORDS_OUTPUT = BI_ARTIFACTS / 'normalized_r1_to_r86_measurements_20261024.json'
BLOCKS_OUTPUT = BI_ARTIFACTS / 'normalized_r16_to_r86_block_observations_20261024.json'


BM_ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_bm_to_bp_20261024'
BM_INPUT_MANIFEST = BM_ARTIFACTS / 'inputs_manifest.json'
BM_MANIFEST_SHA256 = 'c6ad60ddfdaf33cb0cf885fb28a46c63013dad06057ebcb37b385e1c5f9a0fb6'
ROUND92_SPECS = {
    87: ('lap120_loco195_r87_unidir_dl_2flow_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'unidir_dl_2flow', 2, False, 100, 0),
    88: ('lap120_loco195_r88_bidir_4flow_covclass27_12km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_4flow', 4, True, 12000, 27),
    89: ('lap120_loco195_r89_bidir_4flow_covclass31_14km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_4flow', 4, True, 14000, 31),
    90: ('lap120_loco195_r90_covclass31_14km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True, 14000, 31),
    91: ('lap120_loco195_r91_bidir_2flow_covclass6_3000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_2flow', 2, True, 3000, 6),
    92: ('lap120_loco195_r92_bidir_2flow_covclass13_6000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_2flow', 2, True, 6000, 13),
}
# Literal supplied names are provenance, not context authority (notably R89).
ROUND92_RECIPES = {
    87: 'run_live_autoresearch_r87_unidir_dl_2flow_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py',
    88: 'run_live_autoresearch_r88_bidir_4flow_covclass27_12km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py',
    89: 'run_live_autoresearch_r89_bidir_4flow_covclass33_15km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py',
    90: 'run_live_autoresearch_r90_covclass31_14km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py',
    91: 'run_live_autoresearch_r91_bidir_2flow_covclass6_3000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py',
    92: 'run_live_autoresearch_r92_bidir_2flow_covclass13_6000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py',
}
R87_TO_R92_RECEIPTS = tuple(BM_ARTIFACTS / 'inputs/artifacts/autoresearch' / spec[0] for spec in ROUND92_SPECS.values())
R86_RECORDS_OUTPUT, R86_BLOCKS_OUTPUT = RECORDS_OUTPUT, BLOCKS_OUTPUT
R86_VALIDATION = BI_ARTIFACTS / 'final_validation.json'
R86_VALIDATION_SHA256 = '62d7b60a15aec8dd815e53bf7c01a3fd7cdf2d8502bb0e5486054b359196dcb9'
RECORDS_OUTPUT = BM_ARTIFACTS / 'normalized_r1_to_r92_measurements_20261024.json'
BLOCKS_OUTPUT = BM_ARTIFACTS / 'normalized_r16_to_r92_block_observations_20261024.json'


def _json(path):
    path = old._offline_path(path)
    if not path.is_file() or path.stat().st_size > 15_000_000:
        raise ValueError('Missing or oversized local JSON input')
    def reject(value):
        raise ValueError('Nonfinite JSON value: ' + value)
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_bytes(), parse_constant=reject, object_pairs_hook=pairs,
                      parse_float=lambda value: old.finite_number(float(value), 'JSON number'))


def _binding(path):
    path = old._offline_path(path)
    raw = path.read_bytes()
    name = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    return dict(path=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def _prior(path, expected_name, validation_path=R47_VALIDATION):
    validation_path = old._offline_path(validation_path)
    if _binding(validation_path)['sha256'] != PRIOR_VALIDATION_SHA256:
        raise ValueError('Prior AG-AJ validation differs from the accepted external pin')
    entries = [e for e in _json(validation_path)['bindings'] if e['path'] ==
               'artifacts/autoresearch/waves_ag_to_aj_20261024/' + expected_name]
    actual = _binding(path)
    if len(entries) != 1 or any(actual[k] != entries[0][k] for k in ('bytes', 'sha256')):
        raise ValueError('Prior sealed corpus checksum or size mismatch')
    return _json(path)


def _inputs(manifest_path=INPUT_MANIFEST):
    return _authenticated_inputs(manifest_path, default_path=INPUT_MANIFEST,
        expected_sha256=INPUT_MANIFEST_SHA256, catalog=ROUND_SPECS)


def _inputs60(manifest_path=AO_INPUT_MANIFEST):
    return _authenticated_inputs(manifest_path, default_path=AO_INPUT_MANIFEST,
        expected_sha256=AO_MANIFEST_SHA256, catalog=ROUND60_SPECS)


def _inputs65(manifest_path=AS_INPUT_MANIFEST):
    return _authenticated_inputs(manifest_path, default_path=AS_INPUT_MANIFEST,
        expected_sha256=AS_MANIFEST_SHA256, catalog=ROUND65_SPECS)


def _inputs70(manifest_path=AW_INPUT_MANIFEST):
    return _authenticated_inputs(manifest_path, default_path=AW_INPUT_MANIFEST,
        expected_sha256=AW_MANIFEST_SHA256, catalog=ROUND70_SPECS)


def _inputs75(manifest_path=BA_INPUT_MANIFEST):
    return _authenticated_inputs(manifest_path, default_path=BA_INPUT_MANIFEST,
        expected_sha256=BA_MANIFEST_SHA256, catalog=ROUND75_SPECS)


def _inputs80(manifest_path=BE_INPUT_MANIFEST):
    return _authenticated_inputs(manifest_path, default_path=BE_INPUT_MANIFEST,
        expected_sha256=BE_MANIFEST_SHA256, catalog=ROUND80_SPECS)


def _authenticated_inputs(manifest_path, *, default_path, expected_sha256, catalog):
    manifest_path = old._offline_path(manifest_path)
    if (manifest_path.resolve() == default_path.resolve()
            and _binding(manifest_path)['sha256'] != expected_sha256):
        raise ValueError('Frozen default manifest checksum mismatch')
    manifest = _json(manifest_path)
    entries = manifest.get('entries')
    if not isinstance(entries, list) or len(entries) != 3 * len(catalog):
        raise ValueError('Complete explicit three-file-per-round frozen manifest required')
    allowed_root = (manifest_path.parent / 'inputs').resolve()
    identities = set()
    for entry in entries:
        if not isinstance(entry, dict) or type(entry.get('round')) is not int or entry['round'] not in catalog:
            raise ValueError('Only explicit frozen catalog round identities are allowed')
        path = old._offline_path(entry.get('path', '')).resolve()
        if not path.is_relative_to(allowed_root) or path.parent != allowed_root:
            raise ValueError('Input must stay directly inside the explicit frozen input folder')
        filename = catalog[entry['round']][0]
        permitted = {filename, filename.removesuffix('_20261024.json') + '_results.tsv',
                     'run_live_autoresearch_' + filename.removeprefix('lap120_loco195_').removesuffix('_20261024.json') + '_n160_20261024.py'}
        if path.name not in permitted or path.name in identities:
            raise ValueError('Input filename/round mismatch or duplicate identity')
        identities.add(path.name)
        actual = _binding(path)
        if (type(entry.get('bytes')) is not int or entry['bytes'] != actual['bytes']
                or entry.get('sha256') != actual['sha256']):
            raise ValueError('Frozen input checksum or size mismatch')
    if any(sum(e['round'] == n for e in entries) != 3 for n in catalog):
        raise ValueError('Every round needs exactly JSON, TSV and recipe provenance')
    return manifest


def _context(number, payload, item, *, catalog=ROUND_SPECS):
    _, source_regime, flows, bidirectional, distance, coverage = catalog[number]
    declarations = (payload, item, item.get('candidate_knobs', {}))
    for declared in declarations:
        if not isinstance(declared, dict):
            raise ValueError('Explicit saved treatment declarations required')
        for name in ('traffic_regime', 'workload_regime'):
            if name in declared and declared[name] != source_regime:
                raise ValueError('Saved workload conflicts with the round catalog')
        if 'active_flow_count' in declared and old.exact_integer(declared['active_flow_count'], 'flows', 1, 1000) != flows:
            raise ValueError('Saved flow count conflicts')
        if 'bidirectional' in declared and (type(declared['bidirectional']) is not bool or declared['bidirectional'] != bidirectional):
            raise ValueError('Saved direction conflicts')
        for key, expected in (('distance_m', distance), ('distance_meters', distance), ('coverage_class', coverage)):
            if key in declared and (expected is None or old.exact_integer(declared[key], key, 0, 100000) != expected):
                raise ValueError('Saved programmed timing declarations conflict')
    if coverage is not None and any(s.get('coverage_class') != coverage or s.get('distance_m') != distance for s in declarations):
        raise ValueError('Shared payload/treatment/knob timing provenance required')
    if coverage == 0:
        for key, expected in (('slot_time_us', 9), ('ack_timeout_us', 18)):
            if old.exact_integer(payload.get(key), key, 0, 100000) != expected:
                raise ValueError('Explicit class0 slot/ACK receipt declaration required')
            for declared in declarations:
                if key in declared and old.exact_integer(declared[key], key, 0, 100000) != expected:
                    raise ValueError('Conflicting slot/ACK declaration')
    if number >= 61:
        slot, ack = {0: (9,18), 6: (27,54), 10: (39,78), 13: (48,96), 20: (69,138),
                     27: (90,180), 33: (108,216), 3: (18,36), 16: (57,114), 23: (78,156), 30: (99,198), 31: (102,204), 2: (15,30), 26: (87,174)}[coverage]
        for declared in declarations:
            for key, expected in (('slot_time_us', slot), ('ack_timeout_us', ack)):
                if old.exact_integer(declared.get(key), key, 0, 100000) != expected:
                    raise ValueError('Shared payload/treatment/knob slot/ACK declarations required')
    if number >= 81:
        for declared in declarations:
            if (declared.get('traffic_regime') != source_regime
                    or type(declared.get('active_flow_count')) is not int or declared['active_flow_count'] != flows
                    or type(declared.get('bidirectional')) is not bool or declared['bidirectional'] != bidirectional):
                raise ValueError('Explicit shared regime/flow/direction declarations required')
    regime = 'bidir_6flow' if number < 81 and coverage in (6,13) else source_regime
    return regime, flows, bidirectional, distance, coverage


def _campaign(receipt_paths=R48_TO_R56_RECEIPTS, manifest_path=INPUT_MANIFEST):
    manifest = _inputs(manifest_path)
    yield from _campaign_catalog(receipt_paths, manifest, catalog=ROUND_SPECS, max_round=56)


def _campaign60(receipt_paths=R57_TO_R60_RECEIPTS, manifest_path=AO_INPUT_MANIFEST):
    manifest = _inputs60(manifest_path)
    yield from _campaign_catalog(receipt_paths, manifest, catalog=ROUND60_SPECS, max_round=60)


def _campaign65(receipt_paths=R61_TO_R65_RECEIPTS, manifest_path=AS_INPUT_MANIFEST):
    manifest = _inputs65(manifest_path)
    yield from _campaign_catalog(receipt_paths, manifest, catalog=ROUND65_SPECS, max_round=65)


def _campaign70(receipt_paths=R66_TO_R70_RECEIPTS, manifest_path=AW_INPUT_MANIFEST):
    manifest = _inputs70(manifest_path)
    yield from _campaign_catalog(receipt_paths, manifest, catalog=ROUND70_SPECS, max_round=70)


def _campaign75(receipt_paths=R71_TO_R75_RECEIPTS, manifest_path=BA_INPUT_MANIFEST):
    manifest = _inputs75(manifest_path)
    yield from _campaign_catalog(receipt_paths, manifest, catalog=ROUND75_SPECS, max_round=75)


def _campaign80(receipt_paths=R76_TO_R80_RECEIPTS, manifest_path=BE_INPUT_MANIFEST):
    manifest = _inputs80(manifest_path)
    yield from _campaign_catalog(receipt_paths, manifest, catalog=ROUND80_SPECS, max_round=80)


def _campaign_catalog(receipt_paths, manifest, *, catalog, max_round):
    selected = tuple(old._offline_path(p).resolve() for p in receipt_paths)
    if not 1 <= len(selected) <= len(catalog) or len(set(selected)) != len(selected):
        raise ValueError('Require bounded unique explicit frozen receipts')
    seen = set()
    for path in selected:
        entries = [e for e in manifest['entries'] if old._offline_path(e['path']).resolve() == path and path.suffix == '.json']
        if len(entries) != 1:
            raise ValueError('Receipt is not an authenticated manifest member')
        entry = entries[0]
        payload = _json(path)
        number = old._physical_round_number(payload, max_round=max_round)
        if number != entry['round'] or number not in catalog or number in seen:
            raise ValueError('Unique matching frozen receipt identity required')
        seen.add(number)
        recipe = next(e for e in manifest['entries'] if e['round'] == number and e['path'].endswith('.py'))
        recipe_text = old._offline_path(recipe['path']).read_text(encoding='utf-8')
        ref = dict(entry, round_id=f'R{number}', experiment_id=payload['experiment_id'], timestamp_utc=payload.get('timestamp_utc'))
        yield number, payload, ref, deepcopy(recipe), recipe_text


def _new_data(receipt_paths=R48_TO_R56_RECEIPTS, manifest_path=INPUT_MANIFEST):
    return _convert_campaign(_campaign(receipt_paths, manifest_path), catalog=ROUND_SPECS, max_round=56)


def _new_data60(receipt_paths=R57_TO_R60_RECEIPTS, manifest_path=AO_INPUT_MANIFEST):
    return _convert_campaign(_campaign60(receipt_paths, manifest_path), catalog=ROUND60_SPECS, max_round=60)


def _new_data65(receipt_paths=R61_TO_R65_RECEIPTS, manifest_path=AS_INPUT_MANIFEST):
    return _convert_campaign(_campaign65(receipt_paths, manifest_path), catalog=ROUND65_SPECS, max_round=65)


def _new_data70(receipt_paths=R66_TO_R70_RECEIPTS, manifest_path=AW_INPUT_MANIFEST):
    return _convert_campaign(_campaign70(receipt_paths, manifest_path), catalog=ROUND70_SPECS, max_round=70)


def _new_data75(receipt_paths=R71_TO_R75_RECEIPTS, manifest_path=BA_INPUT_MANIFEST):
    return _convert_campaign(_campaign75(receipt_paths, manifest_path), catalog=ROUND75_SPECS, max_round=75)


def _new_data80(receipt_paths=R76_TO_R80_RECEIPTS, manifest_path=BE_INPUT_MANIFEST):
    return _convert_campaign(_campaign80(receipt_paths, manifest_path), catalog=ROUND80_SPECS, max_round=80)


def _convert_campaign(campaign, *, catalog, max_round):
    records, crossed, refs = [], [], []
    for number, payload, ref, recipe, recipe_text in campaign:
        rows = old._exact_campaign_block_rows(payload, max_round=max_round)
        for position, original in enumerate(payload['iterations']):
            regime, flows, bidirectional, distance, coverage = _context(number, payload, original, catalog=catalog)
            if number < 81 and coverage in (6,13) and ('apply_r33_state_with_distance' not in recipe_text
                                         or f'distance_m={distance}' not in recipe_text):
                raise ValueError('Declared timing lacks the frozen shared recipe call')
            if number >= 66 and coverage in (3,10,16,20,23,27,30,31,33) and f'iw phy phy0 set coverage {coverage} 2>/dev/null || true' not in recipe_text:
                raise ValueError('Declared new coverage lacks its frozen recipe command')
            if number >= 76 and 'iw phy phy0 set coverage 0 2>/dev/null || true' not in recipe_text:
                raise ValueError('New saved coverage lacks its frozen reset0 command')
            if number >= 81:
                _recipe_context86(recipe_text, coverage)
            item = deepcopy(original)
            item['distance_meters'] = distance
            selected = [b for b in rows if b['treatment_id'] == item['commit']]
            window = old._physical_window(item, number, position, selected)
            if number >= 81:
                applicability = old.audit_directional_throughput(regime, total=window.goodput_mbps,
                    dl=window.dl_goodput_mbps, ul=window.ul_goodput_mbps, jain=window.jain_fairness, blocks=selected)
            values = {k: getattr(window, k) for k in old.ThreeTierMeasurement.__dataclass_fields__}
            values.update(workload_regime=regime, active_flow_count=flows, bidirectional=bidirectional)
            audit = old.audit_dyadic_block_means(window)
            evidence = old._certified_summary_evidence(window, item, selected, ref, recipe, 'phy0-ap0.sta1' in recipe_text)
            failure = deepcopy(selected[0]['source_failure_metadata'])
            deltas = [float(a-b) for a, b in zip((window.p50_ms, window.p95_ms, window.p99_ms), np.percentile(window.rtts_ms, [50,95,99]))]
            evidence.update(dyadic_mean_audit=audit, block_mean_numpy_consistent=audit['all_float_zero'],
                numpy_quantile_deltas=deltas, exact_numpy_quantiles=all(v == 0 for v in deltas),
                source_evaluation=deepcopy(original.get('evaluation', {})), source_failure_metadata=failure,
                recorded_window_observation=deepcopy(original['observation']), coverage_class=coverage,
                physical_distance_verified=False, programmed_distance_source_field='distance_m' if distance is not None else 'NOT_RECORDED',
                timing_provenance='SHARED_PAYLOAD_TREATMENT_KNOBS_AND_FROZEN_RECIPE' if distance is not None else 'UNKNOWN_NO_DEFAULT_TIMING_IMPUTED',
                original_endpoint_states_omit_distance=all('distance_meters' not in original['candidate_knobs'][k+'_state'] for k in ('ap','cpe')))
            if number >= 57:
                evidence.update(slot_time_us=payload['slot_time_us'], ack_timeout_us=payload['ack_timeout_us'],
                    slot_ack_source='ROOT_RECEIPT_ONLY', saved_context_credited=True,
                    effective_timing_independently_verified=False,
                    timing_provenance='EXPLICIT_SHARED_PAYLOAD_TREATMENT_KNOBS_NO_EFFECTIVE_TIMING_PROOF')
            if number >= 61:
                evidence.update(slot_ack_source='SHARED_PAYLOAD_TREATMENT_KNOBS',
                    frozen_recipe_distance_application_declared=number < 81 and coverage in (6,13))
            if number >= 66:
                evidence.update(frozen_recipe_coverage_command_declared=f'iw phy phy0 set coverage {coverage} 2>/dev/null || true' in recipe_text,
                    coverage_command_execution_or_readback_independently_verified=False)
            if number >= 76:
                evidence.update(frozen_recipe_coverage_reset0_declared=True,
                    coverage_reset_execution_or_readback_independently_verified=False)
            if number >= 81:
                evidence['directional_applicability'] = applicability
            flags = list(values['flags'])
            if not audit['all_fraction_zero'] or not audit['all_zero_ulp']:
                flags.append('literal_dyadic_zero_ULP_mean_certification_FAILED')
            if not evidence['mac_block_sums_match_window']:
                flags.append('window_MAC_counters_disagree_with_block_sums')
            if failure['crash'] or failure['disqualified']:
                flags.append('source_CRASH_or_disqualification_preserved')
            values['flags'] = tuple(dict.fromkeys(flags))
            records.append(old.DyadicCampaignMeasurement(**values, **old._lower_mac_declarations(item),
                lower_mac_evidence='SHARED_AP_CPE_RECIPE_FIELDS_NOT_EFFECTIVE_FIRMWARE_CONTROL_PROOF',
                rtt_pool_order='CONCATENATED_BLOCK_ORDER', block_mean_consistent=evidence['block_mean_consistent'],
                raw_rtts_matches_blocks=evidence['raw_rtts_matches_blocks'], certified_wds_evidence=evidence,
                coverage_class=coverage, source_failure_metadata=failure, dyadic_mean_audit=audit))
        crossed.extend(rows)
        refs.append(ref)
    return records, crossed, refs


def _measurement(item):
    record = old._measurement_from_normalized42(item)
    if 'dyadic_mean_audit' in item:
        values = {k: getattr(record, k) for k in old.ExactCampaignMeasurement.__dataclass_fields__}
        record = old.DyadicCampaignMeasurement(**values, dyadic_mean_audit=deepcopy(item['dyadic_mean_audit']))
    if 'new_source_controls' in item:
        record = old.SourcePackageMeasurement(**{k:getattr(record,k) for k in old.DyadicCampaignMeasurement.__dataclass_fields__},
            new_source_controls=deepcopy(item['new_source_controls']))
    return record


def load_all56_measurements(receipt_paths=R48_TO_R56_RECEIPTS, *, manifest_path=INPUT_MANIFEST,
                            base_dataset_path=R47_RECORDS, prior_validation_path=R47_VALIDATION,
                            include_auxiliary=True):
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _prior(base_dataset_path, R47_RECORDS.name, prior_validation_path)
    records = [_measurement(r) for r in base['records']]
    new, _, refs = _new_data(receipt_paths, manifest_path)
    records.extend(new)
    if not include_auxiliary:
        records = [r for r in records if r.window_kind == 'primary']
    return records, deepcopy(base['source_refs']) + refs


def load_all56_block_observations(receipt_paths=R48_TO_R56_RECEIPTS, *, manifest_path=INPUT_MANIFEST,
                                  base_dataset_path=R47_BLOCKS, prior_validation_path=R47_VALIDATION):
    base = _prior(base_dataset_path, R47_BLOCKS.name, prior_validation_path)
    _, crossed, refs = _new_data(receipt_paths, manifest_path)
    return dict(crossed=deepcopy(base['crossed']) + crossed,
                sequential=deepcopy(base['sequential']), source_refs=deepcopy(base['source_refs']) + refs)


def load_r1_to_r56_dataset():
    base = _prior(R47_RECORDS, R47_RECORDS.name)
    new, crossed, refs = _new_data()
    records = deepcopy(base['records']) + [{**asdict(r), 'policy_key': r.policy_key} for r in new]
    blocks = _prior(R47_BLOCKS, R47_BLOCKS.name)
    all_crossed = blocks['crossed'] + crossed
    return dict(schema_version=10, evidence='Frozen_sealed_AG_AJ_plus_R48_R56_saved_receipts',
        automatic_execution_allowed=False, physical_acceptance_claim=False,
        software_versions=old.software_versions(), source_refs=deepcopy(base['source_refs']) + refs,
        input_manifest=_inputs(), ac_order=list(old.AC_ORDER), records=records,
        observed_record_count=len(records), primary_window_count=sum(r['window_kind']=='primary' for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary' for r in records), new_arm_count=len(new),
        round_counts={f'R{i}':sum(r['round_id']==f'R{i}' for r in records) for i in range(1,57)},
        crossed_observation_count=len(all_crossed),
        matched_round_scoped_block_count=len({(b['round_id'],b['block_index']) for b in all_crossed}),
        sequential_repetition_count=len(blocks['sequential']),
        dyadic_exact_arm_count=sum(r.dyadic_mean_audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' for r in new),
        distance_interpretation='DECLARED_PROGRAMMED_TIMING_NOT_PHYSICAL_RANGE; absent100m/class0_not_imputed')


def _sealed56(path, *, validation_path=R56_VALIDATION):
    if _binding(validation_path)['sha256'] != R56_VALIDATION_SHA256:
        raise ValueError('Prior AK-AN validation differs from the accepted external pin')
    matches=[e for e in _json(validation_path)['bindings'] if e['path']==path.relative_to(ROOT).as_posix()]
    if len(matches)!=1 or any(_binding(path)[k]!=matches[0][k] for k in ('bytes','sha256')):
        raise ValueError('Prior sealed R56 corpus checksum or size mismatch')
    return _json(path)


def _sealed60(path, *, validation_path=R60_VALIDATION):
    if _binding(validation_path)['sha256'] != R60_VALIDATION_SHA256:
        raise ValueError('Prior AO-AR validation differs from the accepted external pin')
    matches = [e for e in _json(validation_path)['bindings'] if e['path'] == path.relative_to(ROOT).as_posix()]
    if len(matches) != 1 or any(_binding(path)[k] != matches[0][k] for k in ('bytes', 'sha256')):
        raise ValueError('Prior sealed R60 corpus checksum or size mismatch')
    return _json(path)


def load_all60_measurements(receipt_paths=R57_TO_R60_RECEIPTS, *, manifest_path=AO_INPUT_MANIFEST,
                            include_auxiliary=True):
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base=_sealed56(R56_RECORDS_OUTPUT)
    records=[_measurement(r) for r in base['records']]
    new,_,refs=_new_data60(receipt_paths,manifest_path)
    records.extend(new)
    if not include_auxiliary:records=[r for r in records if r.window_kind=='primary']
    return records,deepcopy(base['source_refs'])+refs


def load_all60_block_observations(receipt_paths=R57_TO_R60_RECEIPTS, *, manifest_path=AO_INPUT_MANIFEST):
    base=_sealed56(R56_BLOCKS_OUTPUT)
    _,crossed,refs=_new_data60(receipt_paths,manifest_path)
    return dict(crossed=deepcopy(base['crossed'])+crossed,sequential=deepcopy(base['sequential']),
                source_refs=deepcopy(base['source_refs'])+refs)


def load_r1_to_r60_dataset():
    """Revision-fixed R60 normalized dictionaries and serialized corpus metadata."""
    base=_sealed56(R56_RECORDS_OUTPUT);previous_blocks=_sealed56(R56_BLOCKS_OUTPUT)
    new,crossed,refs=_new_data60()
    normalized=[{**asdict(r),'policy_key':r.policy_key,
        'slot_time_us':r.certified_wds_evidence['slot_time_us'],
        'ack_timeout_us':r.certified_wds_evidence['ack_timeout_us']} for r in new]
    records=deepcopy(base['records'])+normalized;all_crossed=previous_blocks['crossed']+crossed
    return dict(schema_version=11,evidence='Frozen_sealed_AK_AN_plus_R57_R60_saved_receipts',
        automatic_execution_allowed=False,physical_acceptance_claim=False,software_versions=old.software_versions(),
        source_refs=deepcopy(base['source_refs'])+refs,input_manifest=_inputs60(),ac_order=list(old.AC_ORDER),records=records,
        observed_record_count=len(records),primary_window_count=sum(r['window_kind']=='primary' for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary' for r in records),new_arm_count=len(new),
        round_counts={f'R{i}':sum(r['round_id']==f'R{i}' for r in records) for i in range(1,61)},
        crossed_observation_count=len(all_crossed),matched_round_scoped_block_count=len({(b['round_id'],b['block_index']) for b in all_crossed}),
        sequential_repetition_count=len(previous_blocks['sequential']),
        dyadic_exact_arm_count=sum(r.dyadic_mean_audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' for r in new),
        distance_interpretation='EXPLICIT_SAVED_TIMING_CONTEXT_NOT_PHYSICAL_RANGE_OR_EFFECTIVE_TIMING_PROOF; prior_unknown_contexts_unchanged')


def load_all65_measurements(receipt_paths=R61_TO_R65_RECEIPTS, *, manifest_path=AS_INPUT_MANIFEST,
                            include_auxiliary=True):
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _sealed60(R60_RECORDS_OUTPUT)
    records = [_measurement(r) for r in base['records']]
    new, _, refs = _new_data65(receipt_paths, manifest_path)
    records.extend(new)
    if not include_auxiliary:
        records = [r for r in records if r.window_kind == 'primary']
    return records, deepcopy(base['source_refs']) + refs


def load_all65_block_observations(receipt_paths=R61_TO_R65_RECEIPTS, *, manifest_path=AS_INPUT_MANIFEST):
    base = _sealed60(R60_BLOCKS_OUTPUT)
    _, crossed, refs = _new_data65(receipt_paths, manifest_path)
    return dict(crossed=deepcopy(base['crossed']) + crossed, sequential=deepcopy(base['sequential']),
                source_refs=deepcopy(base['source_refs']) + refs)


def load_r1_to_r65_dataset():
    """Revision-fixed R65 normalized dictionaries and serialized corpus metadata."""
    base = _sealed60(R60_RECORDS_OUTPUT)
    previous_blocks = _sealed60(R60_BLOCKS_OUTPUT)
    new, crossed, refs = _new_data65()
    normalized = [{**asdict(r), 'policy_key': r.policy_key,
        'slot_time_us': r.certified_wds_evidence['slot_time_us'],
        'ack_timeout_us': r.certified_wds_evidence['ack_timeout_us']} for r in new]
    records = deepcopy(base['records']) + normalized
    all_crossed = previous_blocks['crossed'] + crossed
    return dict(schema_version=12, evidence='Frozen_sealed_AO_AR_plus_R61_R65_saved_receipts',
        automatic_execution_allowed=False, physical_acceptance_claim=False, software_versions=old.software_versions(),
        source_refs=deepcopy(base['source_refs']) + refs, input_manifest=_inputs65(), ac_order=list(old.AC_ORDER), records=records,
        observed_record_count=len(records), primary_window_count=sum(r['window_kind']=='primary' for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary' for r in records), new_arm_count=len(new),
        round_counts={f'R{i}':sum(r['round_id']==f'R{i}' for r in records) for i in range(1,66)},
        crossed_observation_count=len(all_crossed), matched_round_scoped_block_count=len({(b['round_id'],b['block_index']) for b in all_crossed}),
        sequential_repetition_count=len(previous_blocks['sequential']),
        dyadic_exact_arm_count=sum(r.dyadic_mean_audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' for r in new),
        distance_interpretation='EXPLICIT_SAVED_TIMING_CONTEXT_NOT_PHYSICAL_RANGE_OR_EFFECTIVE_TIMING_PROOF; prior_unknown_contexts_unchanged')


def _sealed65(path, *, validation_path=R65_VALIDATION):
    if _binding(validation_path)['sha256'] != R65_VALIDATION_SHA256:
        raise ValueError('Prior AS-AV validation differs from the accepted external pin')
    matches = [e for e in _json(validation_path)['bindings'] if e['path'] == path.relative_to(ROOT).as_posix()]
    if len(matches) != 1 or any(_binding(path)[k] != matches[0][k] for k in ('bytes','sha256')):
        raise ValueError('Prior sealed R65 corpus checksum or size mismatch')
    return _json(path)


def load_all70_measurements(receipt_paths=R66_TO_R70_RECEIPTS, *, manifest_path=AW_INPUT_MANIFEST,
                            include_auxiliary=True):
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _sealed65(R65_RECORDS_OUTPUT)
    records = [_measurement(r) for r in base['records']]
    new, _, refs = _new_data70(receipt_paths,manifest_path)
    records.extend(new)
    if not include_auxiliary:
        records = [r for r in records if r.window_kind == 'primary']
    return records, deepcopy(base['source_refs']) + refs


def load_all70_block_observations(receipt_paths=R66_TO_R70_RECEIPTS, *, manifest_path=AW_INPUT_MANIFEST):
    base = _sealed65(R65_BLOCKS_OUTPUT)
    _,crossed,refs = _new_data70(receipt_paths,manifest_path)
    return dict(crossed=deepcopy(base['crossed'])+crossed,sequential=deepcopy(base['sequential']),
                source_refs=deepcopy(base['source_refs'])+refs)


def load_r1_to_r70_dataset():
    """Revision-fixed R70 normalized dictionaries and serialized corpus metadata."""
    base = _sealed65(R65_RECORDS_OUTPUT)
    previous_blocks = _sealed65(R65_BLOCKS_OUTPUT)
    new,crossed,refs = _new_data70()
    normalized = [{**asdict(r),'policy_key':r.policy_key,
        'slot_time_us':r.certified_wds_evidence['slot_time_us'],
        'ack_timeout_us':r.certified_wds_evidence['ack_timeout_us']} for r in new]
    records = deepcopy(base['records'])+normalized
    all_crossed = previous_blocks['crossed']+crossed
    return dict(schema_version=13,evidence='Frozen_sealed_AS_AV_plus_R66_R70_saved_receipts',
        automatic_execution_allowed=False,physical_acceptance_claim=False,software_versions=old.software_versions(),
        source_refs=deepcopy(base['source_refs'])+refs,input_manifest=_inputs70(),ac_order=list(old.AC_ORDER),records=records,
        observed_record_count=len(records),primary_window_count=sum(r['window_kind']=='primary' for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary' for r in records),new_arm_count=len(new),
        round_counts={f'R{i}':sum(r['round_id']==f'R{i}' for r in records) for i in range(1,71)},
        crossed_observation_count=len(all_crossed),matched_round_scoped_block_count=len({(b['round_id'],b['block_index']) for b in all_crossed}),
        sequential_repetition_count=len(previous_blocks['sequential']),
        dyadic_exact_arm_count=sum(r.dyadic_mean_audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' for r in new),
        distance_interpretation='EXPLICIT_SAVED_TIMING_CONTEXT_NOT_PHYSICAL_RANGE_OR_EFFECTIVE_TIMING_PROOF; prior_unknown_contexts_unchanged')


def _sealed70(path, *, validation_path=R70_VALIDATION):
    if _binding(validation_path)['sha256'] != R70_VALIDATION_SHA256:
        raise ValueError('Prior AW-AZ validation differs from the accepted external pin')
    matches = [e for e in _json(validation_path)['bindings'] if e['path'] == path.relative_to(ROOT).as_posix()]
    if len(matches) != 1 or any(_binding(path)[k] != matches[0][k] for k in ('bytes','sha256')):
        raise ValueError('Prior sealed R70 corpus checksum or size mismatch')
    return _json(path)


def load_all75_measurements(receipt_paths=R71_TO_R75_RECEIPTS, *, manifest_path=BA_INPUT_MANIFEST,
                            include_auxiliary=True):
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _sealed70(R70_RECORDS_OUTPUT)
    records = [_measurement(r) for r in base['records']]
    new,_,refs = _new_data75(receipt_paths,manifest_path)
    records.extend(new)
    if not include_auxiliary:
        records = [r for r in records if r.window_kind == 'primary']
    return records,deepcopy(base['source_refs'])+refs


def load_all75_block_observations(receipt_paths=R71_TO_R75_RECEIPTS, *, manifest_path=BA_INPUT_MANIFEST):
    base = _sealed70(R70_BLOCKS_OUTPUT)
    _,crossed,refs = _new_data75(receipt_paths,manifest_path)
    return dict(crossed=deepcopy(base['crossed'])+crossed,sequential=deepcopy(base['sequential']),
                source_refs=deepcopy(base['source_refs'])+refs)


def load_r1_to_r75_dataset():
    """Revision-fixed R75 dictionary/serialized evidence, not latest80."""
    base = _sealed70(R70_RECORDS_OUTPUT)
    previous_blocks = _sealed70(R70_BLOCKS_OUTPUT)
    new,crossed,refs = _new_data75()
    normalized = [{**asdict(r),'policy_key':r.policy_key,
        'slot_time_us':r.certified_wds_evidence['slot_time_us'],
        'ack_timeout_us':r.certified_wds_evidence['ack_timeout_us']} for r in new]
    records = deepcopy(base['records'])+normalized
    all_crossed = previous_blocks['crossed']+crossed
    return dict(schema_version=14,evidence='Frozen_sealed_AW_AZ_plus_R71_R75_saved_receipts',
        automatic_execution_allowed=False,physical_acceptance_claim=False,software_versions=old.software_versions(),
        source_refs=deepcopy(base['source_refs'])+refs,input_manifest=_inputs75(),ac_order=list(old.AC_ORDER),records=records,
        observed_record_count=len(records),primary_window_count=sum(r['window_kind']=='primary' for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary' for r in records),new_arm_count=len(new),
        round_counts={f'R{i}':sum(r['round_id']==f'R{i}' for r in records) for i in range(1,76)},
        crossed_observation_count=len(all_crossed),matched_round_scoped_block_count=len({(b['round_id'],b['block_index']) for b in all_crossed}),
        sequential_repetition_count=len(previous_blocks['sequential']),
        dyadic_exact_arm_count=sum(r.dyadic_mean_audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' for r in new),
        distance_interpretation='EXPLICIT_SAVED_TIMING_CONTEXT_NOT_PHYSICAL_RANGE_OR_EFFECTIVE_TIMING_PROOF; prior_unknown_contexts_unchanged')


def _sealed75(path, *, validation_path=R75_VALIDATION):
    if _binding(validation_path)['sha256'] != R75_VALIDATION_SHA256:
        raise ValueError('Prior BA-BD validation differs from the accepted external pin')
    matches = [e for e in _json(validation_path)['bindings'] if e['path'] == path.relative_to(ROOT).as_posix()]
    if len(matches) != 1 or any(_binding(path)[k] != matches[0][k] for k in ('bytes','sha256')):
        raise ValueError('Prior sealed R75 corpus checksum or size mismatch')
    return _json(path)


def load_all80_measurements(receipt_paths=R76_TO_R80_RECEIPTS, *, manifest_path=BE_INPUT_MANIFEST,
                            include_auxiliary=True):
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _sealed75(R75_RECORDS_OUTPUT)
    records = [_measurement(r) for r in base['records']]
    new,_,refs = _new_data80(receipt_paths,manifest_path)
    records.extend(new)
    if not include_auxiliary:
        records = [r for r in records if r.window_kind == 'primary']
    return records,deepcopy(base['source_refs'])+refs


def load_all80_block_observations(receipt_paths=R76_TO_R80_RECEIPTS, *, manifest_path=BE_INPUT_MANIFEST):
    base = _sealed75(R75_BLOCKS_OUTPUT)
    _,crossed,refs = _new_data80(receipt_paths,manifest_path)
    return dict(crossed=deepcopy(base['crossed'])+crossed,sequential=deepcopy(base['sequential']),
                source_refs=deepcopy(base['source_refs'])+refs)


def load_r1_to_r80_dataset():
    """Revision-fixed R80 serialization; latest86 is separate."""
    base = _sealed75(R75_RECORDS_OUTPUT)
    previous_blocks = _sealed75(R75_BLOCKS_OUTPUT)
    new,crossed,refs = _new_data80()
    normalized = [{**asdict(r),'policy_key':r.policy_key,
        'slot_time_us':r.certified_wds_evidence['slot_time_us'],
        'ack_timeout_us':r.certified_wds_evidence['ack_timeout_us']} for r in new]
    records = deepcopy(base['records'])+normalized
    all_crossed = previous_blocks['crossed']+crossed
    return dict(schema_version=15,evidence='Frozen_sealed_BA_BD_plus_R76_R80_saved_receipts',
        automatic_execution_allowed=False,physical_acceptance_claim=False,software_versions=old.software_versions(),
        source_refs=deepcopy(base['source_refs'])+refs,input_manifest=_inputs80(),ac_order=list(old.AC_ORDER),records=records,
        observed_record_count=len(records),primary_window_count=sum(r['window_kind']=='primary' for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary' for r in records),new_arm_count=len(new),
        round_counts={f'R{i}':sum(r['round_id']==f'R{i}' for r in records) for i in range(1,81)},
        crossed_observation_count=len(all_crossed),matched_round_scoped_block_count=len({(b['round_id'],b['block_index']) for b in all_crossed}),
        sequential_repetition_count=len(previous_blocks['sequential']),
        dyadic_exact_arm_count=sum(r.dyadic_mean_audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' for r in new),
        distance_interpretation='EXPLICIT_SAVED_TIMING_CONTEXT_NOT_PHYSICAL_RANGE_OR_EFFECTIVE_TIMING_PROOF; prior_unknown_contexts_unchanged')


def load_r1_to_r86_dataset():
    """Revision-fixed R86 serialized evidence, not latest92."""
    base = _sealed80(R80_RECORDS_OUTPUT)
    previous_blocks = _sealed80(R80_BLOCKS_OUTPUT)
    new,crossed,refs = _new_data86()
    normalized = [{**asdict(r),'policy_key':r.policy_key,
        'slot_time_us':r.certified_wds_evidence['slot_time_us'],
        'ack_timeout_us':r.certified_wds_evidence['ack_timeout_us']} for r in new]
    records = deepcopy(base['records'])+normalized
    all_crossed = previous_blocks['crossed']+crossed
    return dict(schema_version=16,evidence='Frozen_sealed_BE_BH_plus_R81_R86_saved_receipts',
        automatic_execution_allowed=False,physical_acceptance_claim=False,software_versions=old.software_versions(),
        source_refs=deepcopy(base['source_refs'])+refs,input_manifest=_inputs86(),ac_order=list(old.AC_ORDER),records=records,
        observed_record_count=len(records),primary_window_count=sum(r['window_kind']=='primary' for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary' for r in records),new_arm_count=len(new),
        round_counts={f'R{i}':sum(r['round_id']==f'R{i}' for r in records) for i in range(1,87)},
        crossed_observation_count=len(all_crossed),matched_round_scoped_block_count=len({(b['round_id'],b['block_index']) for b in all_crossed}),
        sequential_repetition_count=len(previous_blocks['sequential']),
        dyadic_exact_arm_count=sum(r.dyadic_mean_audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' for r in new),
        distance_interpretation='EXPLICIT_SAVED_TIMING_CONTEXT_NOT_PHYSICAL_RANGE_OR_EFFECTIVE_TIMING_PROOF; prior_unknown_contexts_unchanged')


def load_r1_to_r92_dataset(*, through_round=92):
    """Latest92; explicit56/60/65/70/75/80/86 interfaces preserve serialized bytes."""
    if type(through_round) is not int or through_round not in (56,60,65,70,75,80,86,92):
        raise ValueError('Explicit through_round56,60,65,70,75 or80 or86 or92 required')
    historical = {56:load_r1_to_r56_dataset,60:load_r1_to_r60_dataset,
                  65:load_r1_to_r65_dataset,70:load_r1_to_r70_dataset,75:load_r1_to_r75_dataset,80:load_r1_to_r80_dataset,86:load_r1_to_r86_dataset}
    if through_round in historical:
        return historical[through_round]()
    base = _sealed86(R86_RECORDS_OUTPUT)
    previous_blocks = _sealed86(R86_BLOCKS_OUTPUT)
    new,crossed,refs = _new_data92()
    normalized = [{**asdict(r),'policy_key':r.policy_key,
        'slot_time_us':r.certified_wds_evidence['slot_time_us'],
        'ack_timeout_us':r.certified_wds_evidence['ack_timeout_us']} for r in new]
    records = deepcopy(base['records'])+normalized
    all_crossed = previous_blocks['crossed']+crossed
    return dict(schema_version=17,evidence='Frozen_sealed_BI_BL_plus_R87_R92_saved_receipts',
        automatic_execution_allowed=False,physical_acceptance_claim=False,software_versions=old.software_versions(),
        source_refs=deepcopy(base['source_refs'])+refs,input_manifest=_inputs92(),ac_order=list(old.AC_ORDER),records=records,
        observed_record_count=len(records),primary_window_count=sum(r['window_kind']=='primary' for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary' for r in records),new_arm_count=len(new),
        round_counts={f'R{i}':sum(r['round_id']==f'R{i}' for r in records) for i in range(1,93)},
        crossed_observation_count=len(all_crossed),matched_round_scoped_block_count=len({(b['round_id'],b['block_index']) for b in all_crossed}),
        sequential_repetition_count=len(previous_blocks['sequential']),
        dyadic_exact_arm_count=sum(r.dyadic_mean_audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' for r in new),
        distance_interpretation='EXPLICIT_SAVED_TIMING_CONTEXT_NOT_PHYSICAL_RANGE_OR_EFFECTIVE_TIMING_PROOF; prior_unknown_contexts_unchanged')


def _historical_crossed_dataset(*, through_round=92):
    if type(through_round) is not int or through_round not in (56,60,65,70,75,80,86,92):
        raise ValueError('Explicit through_round56,60,65,70,75 or80 or86 or92 required')
    loaders = {56:load_all56_block_observations,60:load_all60_block_observations,
               65:load_all65_block_observations,70:load_all70_block_observations,
               75:load_all75_block_observations,80:load_all80_block_observations,86:load_all86_block_observations,92:load_all92_block_observations}
    return loaders[through_round]()


def build_dataset_outputs():
    if any(path.exists() for path in (RECORDS_OUTPUT, BLOCKS_OUTPUT)):
        raise FileExistsError('Never replace either member of an existing corpus pair')
    dataset, blocks = load_live_dataset(), load_crossed_dataset()
    for path, value in ((RECORDS_OUTPUT, dataset), (BLOCKS_OUTPUT, blocks)):
        if path.exists():
            raise FileExistsError('Never replace prior generated corpus evidence: ' + str(path))
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
    return [_binding(RECORDS_OUTPUT), _binding(BLOCKS_OUTPUT)]


def _campaign86(receipt_paths=R81_TO_R86_RECEIPTS, manifest_path=BI_INPUT_MANIFEST):
    manifest = _inputs86(manifest_path)
    yield from _campaign_catalog(receipt_paths, manifest, catalog=ROUND86_SPECS, max_round=86)


def _inputs86(manifest_path=BI_INPUT_MANIFEST):
    """Authenticate nested frozen copies, never reopen logical original paths."""
    manifest_path = old._offline_path(manifest_path)
    if manifest_path.resolve() == BI_INPUT_MANIFEST.resolve() and _binding(manifest_path)['sha256'] != BI_MANIFEST_SHA256:
        raise ValueError('Frozen default manifest checksum mismatch')
    manifest = _json(manifest_path)
    entries = manifest.get('entries')
    if not isinstance(entries, list) or len(entries) != 18:
        raise ValueError('Complete eighteen-file frozen manifest required')
    result, seen = [], set()
    for source in entries:
        if not isinstance(source, dict) or type(source.get('round')) is not int or source['round'] not in ROUND86_SPECS:
            raise ValueError('Only explicit frozen R81-R86 identities allowed')
        filename = ROUND86_SPECS[source['round']][0]
        permitted = {'artifacts/autoresearch/' + filename,
            'artifacts/autoresearch/' + filename.removesuffix('_20261024.json') + '_results.tsv',
            'tools/bench/run_live_autoresearch_' + filename.removeprefix('lap120_loco195_').removesuffix('_20261024.json') + '_n160_20261024.py'}
        logical = source.get('path')
        if type(logical) is not str or logical not in permitted or logical in seen:
            raise ValueError('Input filename/round mismatch or duplicate identity')
        seen.add(logical)
        path = (manifest_path.parent / 'inputs' / logical).resolve()
        if (not path.is_relative_to((manifest_path.parent / 'inputs').resolve())
                or source.get('copy') != path.relative_to(ROOT).as_posix()):
            raise ValueError('Input must stay in its exact nested frozen copy path')
        actual = _binding(path)
        if (type(source.get('bytes')) is not int or source['bytes'] != actual['bytes']
                or source.get('sha256') != actual['sha256']):
            raise ValueError('Frozen input checksum or size mismatch')
        result.append({**source, 'original_path': logical, 'path': actual['path']})
    if any(sum(e['round'] == n for e in result) != 3 for n in ROUND86_SPECS):
        raise ValueError('Every round needs JSON, TSV and recipe provenance')
    return {**manifest, 'entries': result}


def _recipe_context86(text, coverage):
    """Prove saved prep/reset call declarations only, never execute the recipe."""
    tree = ast.parse(text)
    literal = f'iw phy phy0 set coverage {coverage} 2>/dev/null || true'
    prep = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == 'prep_cmd' for t in n.targets)
        and any(isinstance(x, ast.Constant) and isinstance(x.value, str) and literal in x.value for x in ast.walk(n))]
    if len(prep) != 1:
        raise ValueError('Missing unique frozen prep coverage command')
    users = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        and n.func.id == 'rpc' and len(n.args) >= 2
        and any(isinstance(x, ast.Name) and x.id == 'prep_cmd' for x in ast.walk(n.args[1]))]
    reset = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        and n.func.id == 'rpc' and len(n.args) >= 2
        and any(isinstance(x, ast.Constant) and isinstance(x.value, str)
                and 'iw phy phy0 set coverage 0 2>/dev/null || true' in x.value for x in ast.walk(n.args[1]))]
    for calls in (users, reset):
        if not {'b.ap', 'b.client'} <= {ast.unparse(n.args[0]) for n in calls}:
            raise ValueError('Frozen prep/reset must declare both endpoint RPCs')
    return dict(prep_coverage=coverage, prep_line=prep[0].lineno,
                both_endpoints_declared=True, reset0_declared=True, executed_or_read_back=False)


def _new_data86(receipt_paths=R81_TO_R86_RECEIPTS, manifest_path=BI_INPUT_MANIFEST):
    return _convert_campaign(_campaign86(receipt_paths, manifest_path), catalog=ROUND86_SPECS, max_round=86)


def _sealed80(path, *, validation_path=R80_VALIDATION):
    if _binding(validation_path)['sha256'] != R80_VALIDATION_SHA256:
        raise ValueError('Prior BE-BH validation differs from the accepted external pin')
    matches = [e for e in _json(validation_path)['bindings'] if e['path'] == path.relative_to(ROOT).as_posix()]
    if len(matches) != 1 or any(_binding(path)[k] != matches[0][k] for k in ('bytes','sha256')):
        raise ValueError('Prior sealed R80 corpus checksum or size mismatch')
    return _json(path)


def load_all86_measurements(receipt_paths=R81_TO_R86_RECEIPTS, *, manifest_path=BI_INPUT_MANIFEST,
                            include_auxiliary=True):
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _sealed80(R80_RECORDS_OUTPUT)
    records = [_measurement(r) for r in base['records']]
    new,_,refs = _new_data86(receipt_paths,manifest_path)
    records.extend(new)
    if not include_auxiliary:
        records = [r for r in records if r.window_kind == 'primary']
    return records,deepcopy(base['source_refs'])+refs


def load_all86_block_observations(receipt_paths=R81_TO_R86_RECEIPTS, *, manifest_path=BI_INPUT_MANIFEST):
    base = _sealed80(R80_BLOCKS_OUTPUT)
    _,crossed,refs = _new_data86(receipt_paths,manifest_path)
    return dict(crossed=deepcopy(base['crossed'])+crossed,sequential=deepcopy(base['sequential']),
                source_refs=deepcopy(base['source_refs'])+refs)


def _campaign92(receipt_paths=R87_TO_R92_RECEIPTS, manifest_path=BM_INPUT_MANIFEST):
    manifest = _inputs92(manifest_path)
    yield from _campaign_catalog(receipt_paths, manifest, catalog=ROUND92_SPECS, max_round=92)


def _new_data92(receipt_paths=R87_TO_R92_RECEIPTS, manifest_path=BM_INPUT_MANIFEST):
    return _convert_campaign(_campaign92(receipt_paths, manifest_path), catalog=ROUND92_SPECS, max_round=92)


def _inputs92(manifest_path=BM_INPUT_MANIFEST):
    """Authenticate nested frozen copies, never reopen logical original paths."""
    manifest_path = old._offline_path(manifest_path)
    if manifest_path.resolve() == BM_INPUT_MANIFEST.resolve() and _binding(manifest_path)['sha256'] != BM_MANIFEST_SHA256:
        raise ValueError('Frozen default manifest checksum mismatch')
    manifest = _json(manifest_path)
    entries = manifest.get('entries')
    if not isinstance(entries, list) or len(entries) != 18:
        raise ValueError('Complete eighteen-file frozen manifest required')
    result, seen = [], set()
    for source in entries:
        if not isinstance(source, dict) or type(source.get('round')) is not int or source['round'] not in ROUND92_SPECS:
            raise ValueError('Only explicit frozen R87-R92 identities allowed')
        filename = ROUND92_SPECS[source['round']][0]
        permitted = {'artifacts/autoresearch/' + filename,
            'artifacts/autoresearch/' + filename.removesuffix('_20261024.json') + '_results.tsv',
            'tools/bench/' + ROUND92_RECIPES[source['round']]}
        logical = source.get('path')
        if type(logical) is not str or logical not in permitted or logical in seen:
            raise ValueError('Input filename/round mismatch or duplicate identity')
        seen.add(logical)
        path = (manifest_path.parent / 'inputs' / logical).resolve()
        if (not path.is_relative_to((manifest_path.parent / 'inputs').resolve())
                or source.get('copy') != path.relative_to(ROOT).as_posix()):
            raise ValueError('Input must stay in its exact nested frozen copy path')
        actual = _binding(path)
        if (type(source.get('bytes')) is not int or source['bytes'] != actual['bytes']
                or source.get('sha256') != actual['sha256']):
            raise ValueError('Frozen input checksum or size mismatch')
        result.append({**source, 'original_path': logical, 'path': actual['path']})
    if any(sum(e['round'] == n for e in result) != 3 for n in ROUND92_SPECS):
        raise ValueError('Every round needs JSON, TSV and recipe provenance')
    return {**manifest, 'entries': result}


def _sealed86(path, *, validation_path=R86_VALIDATION):
    if _binding(validation_path)['sha256'] != R86_VALIDATION_SHA256:
        raise ValueError('Prior BI-BL validation differs from the accepted external pin')
    matches = [e for e in _json(validation_path)['bindings'] if e['path'] == path.relative_to(ROOT).as_posix()]
    if len(matches) != 1 or any(_binding(path)[k] != matches[0][k] for k in ('bytes','sha256')):
        raise ValueError('Prior sealed R86 corpus checksum or size mismatch')
    return _json(path)


def load_all92_measurements(receipt_paths=R87_TO_R92_RECEIPTS, *, manifest_path=BM_INPUT_MANIFEST,
                            include_auxiliary=True):
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _sealed86(R86_RECORDS_OUTPUT)
    records = [_measurement(r) for r in base['records']]
    new,_,refs = _new_data92(receipt_paths,manifest_path)
    records.extend(new)
    if not include_auxiliary:
        records = [r for r in records if r.window_kind == 'primary']
    return records,deepcopy(base['source_refs'])+refs


def load_all92_block_observations(receipt_paths=R87_TO_R92_RECEIPTS, *, manifest_path=BM_INPUT_MANIFEST):
    base = _sealed86(R86_BLOCKS_OUTPUT)
    _,crossed,refs = _new_data92(receipt_paths,manifest_path)
    return dict(crossed=deepcopy(base['crossed'])+crossed,sequential=deepcopy(base['sequential']),
                source_refs=deepcopy(base['source_refs'])+refs)


# Additive frozen BQ-CF saved packages. Source names are documentary, not context.
BQCF_ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_bq_to_cf_20261024'
BQCF_INPUT_MANIFEST = BQCF_ARTIFACTS / 'inputs_manifest.json'
BQCF_MANIFEST_SHA256 = 'f81036628828869df84ebb7887093ce1fff17e185ba8ddbf05d1a1701bc42d1d'
ROUND134_SPECS = {93: ('lap120_loco195_r93_covclass31_14km_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
      'bidir_6flow',
      6,
      True,
      14000,
      31),
 94: ('lap120_loco195_r94_bidir_2flow_covclass20_9000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
      'bidir_2flow',
      2,
      True,
      9000,
      20),
 95: ('lap120_loco195_r95_bidir_2flow_covclass27_12km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
      'bidir_2flow',
      2,
      True,
      12000,
      27),
 96: ('lap120_loco195_r96_bidir_2flow_covclass31_14km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
      'bidir_2flow',
      2,
      True,
      14000,
      31),
 97: ('lap120_loco195_r97_bidir_2flow_covclass20_9000m_be1800_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
      'bidir_2flow',
      2,
      True,
      9000,
      20),
 98: ('lap120_loco195_r98_bidir_8flow_covclass6_3000m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
      'bidir_8flow',
      8,
      True,
      3000,
      6),
 99: ('lap120_loco195_r99_bidir_8flow_covclass13_6000m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
      'bidir_8flow',
      8,
      True,
      6000,
      13),
 100: ('lap120_loco195_r100_bidir_8flow_covclass20_9000m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'bidir_8flow',
       8,
       True,
       9000,
       20),
 101: ('lap120_loco195_r101_bidir_8flow_covclass27_12km_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'bidir_8flow',
       8,
       True,
       12000,
       27),
 102: ('lap120_loco195_r102_bidir_8flow_covclass31_14km_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'bidir_8flow',
       8,
       True,
       14000,
       31),
 103: ('lap120_loco195_r103_unidir_dl_2flow_covclass6_3000m_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_dl_2flow',
       2,
       False,
       3000,
       6),
 104: ('lap120_loco195_r104_unidir_dl_2flow_covclass13_6000m_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_dl_2flow',
       2,
       False,
       6000,
       13),
 105: ('lap120_loco195_r105_unidir_dl_2flow_covclass20_9000m_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_dl_2flow',
       2,
       False,
       9000,
       20),
 106: ('lap120_loco195_r106_unidir_dl_2flow_covclass27_12km_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_dl_2flow',
       2,
       False,
       12000,
       27),
 107: ('lap120_loco195_r107_unidir_dl_2flow_covclass31_14km_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_dl_2flow',
       2,
       False,
       14000,
       31),
 108: ('lap120_loco195_r108_unidir_ul_2flow_covclass2_1000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_2flow',
       2,
       False,
       1000,
       2),
 109: ('lap120_loco195_r109_unidir_ul_2flow_covclass6_3000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_2flow',
       2,
       False,
       3000,
       6),
 114: ('lap120_loco195_r114_unidir_ul_2flow_covclass2_1000m_be1900_3000_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_2flow',
       2,
       False,
       1000,
       2),
 115: ('lap120_loco195_r115_unidir_ul_2flow_covclass2_1000m_be1550_2400_cperc48_af1_retry74_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_2flow',
       2,
       False,
       1000,
       2),
 116: ('lap120_loco195_r116_unidir_ul_2flow_covclass2_1000m_be1900_2650_tsq1m_rc50_af1_retry74_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_2flow',
       2,
       False,
       1000,
       2),
 117: ('lap120_loco195_r117_unidir_ul_2flow_covclass6_3000m_be1900_3150_tsq1m_rc50_af1_retry74_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_2flow',
       2,
       False,
       3000,
       6),
 118: ('lap120_loco195_r118_unidir_ul_2flow_covclass13_6000m_be1900_3550_tsq1m_rc50_af1_retry74_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_2flow',
       2,
       False,
       6000,
       13),
 119: ('lap120_loco195_r119_unidir_ul_2flow_covclass20_9000m_be1900_3800_tsq1m_rc50_af1_retry74_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_2flow',
       2,
       False,
       9000,
       20),
 120: ('lap120_loco195_r120_unidir_ul_2flow_covclass26_12000m_be1900_3950_tsq1m_rc50_af1_retry74_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_2flow',
       2,
       False,
       12000,
       26),
 121: ('lap120_loco195_r121_unidir_ul_2flow_covclass31_14000m_be1900_4100_tsq1m_rc50_af1_retry74_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_2flow',
       2,
       False,
       14000,
       31),
 122: ('lap120_loco195_r122_unidir_ul_8flow_hammer_covclass6_3000m_rts256_be1900_3150_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       3000,
       6),
 123: ('lap120_loco195_r123_unidir_ul_8flow_hammer_covclass2_1000m_rts256_be1900_2650_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       1000,
       2),
 124: ('lap120_loco195_r124_unidir_ul_8flow_hammer_covclass13_6000m_rts256_be1900_3550_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       6000,
       13),
 125: ('lap120_loco195_r125_unidir_ul_8flow_hammer_covclass20_9000m_rts256_be1900_3800_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       9000,
       20),
 126: ('lap120_loco195_r126_unidir_ul_8flow_hammer_covclass26_12000m_rts256_be1900_3950_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       12000,
       26),
 127: ('lap120_loco195_r127_unidir_ul_8flow_hammer_covclass31_14000m_rts256_be1900_4100_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       14000,
       31),
 128: ('lap120_loco195_r128_unidir_ul_8flow_hammer_covclass2_1000m_rtsoff_be1900_2650_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       1000,
       2),
 129: ('lap120_loco195_r129_unidir_ul_8flow_hammer_covclass6_3000m_rtsoff_be1900_3150_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       3000,
       6),
 130: ('lap120_loco195_r130_unidir_ul_8flow_hammer_covclass13_6000m_rtsoff_be1900_3550_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       6000,
       13),
 131: ('lap120_loco195_r131_unidir_ul_8flow_hammer_covclass20_9000m_rtsoff_be1900_3800_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       9000,
       20),
 132: ('lap120_loco195_r132_unidir_ul_8flow_hammer_covclass26_12000m_rtsoff_be1900_3950_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       12000,
       26),
 133: ('lap120_loco195_r133_unidir_ul_8flow_hammer_covclass31_14000m_rtsoff_be1900_4100_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       14000,
       31),
 134: ('lap120_loco195_r134_unidir_ul_8flow_hammer_covclass2_1000m_rtsoff_purevo_be1900_2650_abba16_dyadic_zero_loss_wds_20261024.json',
       'unidir_ul_8flow_hammer',
       8,
       False,
       1000,
       2)}
R92_RECORDS_OUTPUT, R92_BLOCKS_OUTPUT = RECORDS_OUTPUT, BLOCKS_OUTPUT
R92_VALIDATION = BM_ARTIFACTS / 'final_validation.json'
R92_VALIDATION_SHA256 = '17dec913196eb29765235d863e2be491b3247192c83f79a9ff864a3b26b0c116'
RECORDS_OUTPUT = BQCF_ARTIFACTS / 'normalized_r1_to_r134_measurements_20261024.json'
BLOCKS_OUTPUT = BQCF_ARTIFACTS / 'normalized_r16_to_r134_block_observations_20261024.json'
R134_RECORDS_OUTPUT,R134_BLOCKS_OUTPUT = RECORDS_OUTPUT,BLOCKS_OUTPUT


def _revision134(value):
    if type(value) is not int or value not in (96,102,107,134):
        raise ValueError('Explicit frozen revision96/102/107/134 required; future135 forbidden')
    return value


def _inputs134(manifest_path=BQCF_INPUT_MANIFEST):
    """Authenticate copies only; documentary original paths are never opened."""
    manifest_path = old._offline_path(manifest_path)
    if manifest_path.resolve() == BQCF_INPUT_MANIFEST.resolve() and _binding(manifest_path)['sha256'] != BQCF_MANIFEST_SHA256:
        raise ValueError('Frozen umbrella manifest checksum mismatch')
    manifest = _json(manifest_path)
    entries = manifest.get('entries')
    if not isinstance(entries,list) or len(entries) != 114:
        raise ValueError('Complete114-file frozen manifest required')
    seen,result = set(),[]
    for source in entries:
        if not isinstance(source,dict) or type(source.get('round')) is not int or source['round'] not in ROUND134_SPECS:
            raise ValueError('Only explicit frozen R93-R134 available identities allowed')
        logical,copy = source.get('path'),source.get('copy')
        if type(logical) is not str or type(copy) is not str or logical in seen:
            raise ValueError('Unique typed logical/copy paths required')
        parts = logical.split('/')
        if any(x in ('','..','.') or ':' in x or '\\' in x for x in parts) or logical.startswith('/'):
            raise ValueError('Unsafe logical path')
        number = source['round']
        if not re.search(r'(?:^|_)r'+str(number)+r'(?:_|\.)',Path(logical).name):
            raise ValueError('Round/path source identity mismatch')
        suffix = Path(logical).suffix
        if suffix not in ('.json','.tsv','.py') or not logical.startswith('tools/bench/' if suffix == '.py' else 'artifacts/autoresearch/'):
            raise ValueError('Only receipt/TSV/recipe input types allowed')
        if suffix == '.json' and Path(logical).name != ROUND134_SPECS[number][0]:
            raise ValueError('Receipt identity differs from frozen catalog')
        expected = manifest_path.parent / 'inputs' / logical
        if (copy != expected.relative_to(ROOT).as_posix() or not expected.resolve().is_relative_to((manifest_path.parent/'inputs').resolve())):
            raise ValueError('Copy must stay in exact frozen nested input path')
        actual = _binding(expected)
        if type(source.get('bytes')) is not int or any(actual[k] != source.get(k) for k in ('bytes','sha256')):
            raise ValueError('Frozen copy checksum/size mismatch')
        seen.add(logical)
        result.append({**source,'original_path':logical,'path':actual['path']})
    for number in ROUND134_SPECS:
        if sorted(Path(e['path']).suffix for e in result if e['round']==number) != ['.json','.py','.tsv']:
            raise ValueError('Every available round needs exactly receipt/recipe/TSV')
    return {**manifest,'entries':result}


def _literal_recipe_packages(text,payload):
    """Interpret a tiny AST declaration grammar, never execute/import a recipe."""
    tree = ast.parse(text)
    mains = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main']
    if len(mains) != 1:
        raise ValueError('Unique source main declaration required')
    env = {}
    def literal(node):
        if isinstance(node,ast.Constant):
            return node.value
        if isinstance(node,ast.Name) and node.id in env:
            return deepcopy(env[node.id])
        if isinstance(node,(ast.Tuple,ast.List)):
            return [literal(x) for x in node.elts]
        if isinstance(node,ast.Dict):
            keys = [literal(k) for k in node.keys]
            if len(set(keys)) != len(keys):
                raise ValueError('Duplicate source declaration key')
            return dict(zip(keys,[literal(v) for v in node.values]))
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('R11CrossLayerKnobState','R15AsymPairState') and not node.args:
            return {kw.arg:literal(kw.value) for kw in node.keywords if kw.arg is not None}
        raise ValueError('Unsupported literal source declaration')
    for node in mains[0].body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            name = node.targets[0].id
            try:
                value = literal(node.value)
            except ValueError:
                if name=='arms':
                    raise
                continue
            env[name] = value
    arms = env.get('arms')
    if not isinstance(arms,dict) or set(arms) != {'A','B'}:
        raise ValueError('Explicit literal A/B source packages required')
    results = []
    for label,item in zip(('A','B'),payload['iterations']):
        package = arms[label]
        if not isinstance(package,list) or len(package) not in (6,8):
            raise ValueError('Bounded known source package tuple required')
        pair = package[0]
        if not isinstance(pair,dict) or pair.get('name') != item.get('commit'):
            raise ValueError('Recipe/receipt treatment identity conflict')
        knobs = item['candidate_knobs']
        for endpoint in ('ap_state','cpe_state'):
            declared = pair.get(endpoint)
            if not isinstance(declared,dict) or not isinstance(knobs.get(endpoint),dict):
                raise ValueError('Both source endpoint states required')
            for key,value in declared.items():
                actual = knobs[endpoint].get(key)
                if type(value) is not type(actual) or value != actual:
                    raise ValueError('Explicit recipe/JSON endpoint field conflict: '+endpoint+'.'+key)
        for key,value in zip(('airtime_flags','fq_limit','force_tx_status','short_retry_limit','long_retry_limit'),package[1:6]):
            if type(value) is not int or type(knobs.get(key)) is not int or knobs[key] != value:
                raise ValueError('Recipe/JSON lower-control conflict')
        controls = {}
        if len(package)==8:
            controls = dict(rts_threshold=package[6],ap_ack_clocking=package[7])
        for key in ('rts_threshold','ap_ack_clocking'):
            if (key in item)!=(key in controls) or (key in knobs)!=(key in controls):
                raise ValueError('Missing/conflicting new control provenance')
            if key in controls and (type(item[key]) is not type(controls[key]) or type(knobs[key]) is not type(controls[key]) or item[key]!=controls[key] or knobs[key]!=controls[key]):
                raise ValueError('Recipe/JSON new-control conflict')
        results.append(dict(controls=controls,explicit_endpoint_fields={k:sorted(pair[k]) for k in ('ap_state','cpe_state')},
            omitted_endpoint_defaults='IMPORTED_DEFAULTS_NOT_RECONSTRUCTED_OR_INDEPENDENTLY_VERIFIED',
            source='AST_LITERAL_DECLARATIONS_ONLY',recipe_executed=False,effective_control_verified=False))
    # Literal context keys in the recipe's saved payload must agree, including
    # R115 whose old filename is not a source of context.
    for node in ast.walk(mains[0]):
        if isinstance(node,ast.Dict):
            for key,value in zip(node.keys,node.values):
                if isinstance(key,ast.Constant) and key.value in ('traffic_regime','active_flow_count','bidirectional','distance_m','coverage_class','slot_time_us','ack_timeout_us') and isinstance(value,ast.Constant):
                    actual = payload.get(key.value)
                    if type(actual) is not type(value.value) or actual != value.value:
                        raise ValueError('Recipe/receipt literal context conflict')
    return results


def _audit_tsv134(text,payload):
    rows = list(csv.DictReader(io.StringIO(text),delimiter='\t'))
    if len(rows)!=2 or len({r.get('commit') for r in rows})!=2:
        raise ValueError('Two unique frozen TSV treatment rows required')
    for row,item in zip(rows,payload['iterations']):
        obs = item['observation']
        expected = dict(commit=item['commit'],fmx_loss=f"{item['evaluation']['fmx_loss']:.6f}",
            goodput_mbps=f"{obs['goodput_rx_mbps']:.2f}",p95_rtt_ms=f"{obs['p95_rtt_ms']:.2f}",
            jain_fairness=f"{obs['jain_fairness']:.4f}",status=item['evaluation']['decision'],
            description=item['candidate_knobs']['description'])
        if any(row.get(k)!=v for k,v in expected.items()):
            raise ValueError('Frozen TSV disagrees with its documented rounded JSON projection')
    return dict(rows=2,comparison='EXACT_DECLARED_FORMAT_6DP_LOSS_2DP_GP_LATENCY_4DP_JAIN',source_repaired=False)


def _sealed92(path,validation_path=R92_VALIDATION):
    if _binding(validation_path)['sha256'] != R92_VALIDATION_SHA256:
        raise ValueError('Prior BM-BP external validation checksum mismatch')
    matches = [e for e in _json(validation_path)['bindings'] if e['path']==path.relative_to(ROOT).as_posix()]
    if len(matches)!=1 or any(_binding(path)[k]!=matches[0][k] for k in ('bytes','sha256')):
        raise ValueError('Prior sealed R92 corpus checksum or size mismatch')
    return _json(path)


def _new_data134(*,through_round=134,manifest_path=BQCF_INPUT_MANIFEST):
    _revision134(through_round)  # Before any file read, including nonexistent future inputs.
    manifest = _inputs134(manifest_path)
    records,crossed,refs,audits = [],[],[],[]
    for number in sorted(ROUND134_SPECS):
        if number>through_round:
            continue
        entries = [e for e in manifest['entries'] if e['round']==number]
        by_suffix = {Path(e['path']).suffix:e for e in entries}
        receipt,recipe,tsv = (by_suffix[s] for s in ('.json','.py','.tsv'))
        try:
            payload = _json(ROOT/receipt['path'])
            if old._physical_round_number(payload,max_round=through_round)!=number or len(payload.get('iterations',[]))!=2:
                raise ValueError('Exact round source identity and two saved arms required')
            text = (ROOT/recipe['path']).read_text(encoding='utf-8')
            context = _recipe_context86(text,ROUND134_SPECS[number][5])
            packages = _literal_recipe_packages(text,payload)
            tsv_audit = _audit_tsv134((ROOT/tsv['path']).read_text(encoding='utf-8'),payload)
            new,blocks,new_refs = _convert_campaign([(number,payload,receipt,recipe,text)],catalog=ROUND134_SPECS,max_round=through_round)
            wrapped = []
            for record,package in zip(new,packages):
                controls = package['controls']
                values = asdict(record)
                values['ap_policy'],values['cpe_policy'] = record.ap_policy,record.cpe_policy
                if 'rts_threshold' in controls:
                    raw = controls['rts_threshold']
                    # Constructor validates canonical strings before any conversion.
                    if type(raw) is not str or not (raw=='off' or raw.isascii() and raw.isdecimal() and str(int(raw))==raw and 1<=int(raw)<=65535):
                        raise ValueError('Invalid literal RTS source declaration')
                    rts = None if raw=='off' else int(raw)
                    values['ap_policy'] = replace(record.ap_policy,rts_threshold=rts)
                    values['cpe_policy'] = replace(record.cpe_policy,rts_threshold=rts)
                evidence = values['certified_wds_evidence']
                evidence.update(new_source_control_provenance=package,source_receipt=receipt,source_recipe=recipe,
                    source_tsv=tsv,recipe_context_ast=context,tsv_projection_audit=tsv_audit,
                    source_package_effective_actuation_verified=False)
                wrapped.append(old.SourcePackageMeasurement(**values,new_source_controls=deepcopy(controls)))
            records.extend(wrapped);crossed.extend(blocks);refs.extend(new_refs)
            audits.append(dict(round_id=f'R{number}',status='INGESTED_SOURCE_CHECKED_NOT_PHYSICAL_ACCEPTANCE',
                source_bindings=entries,recipe_context=context,tsv_projection=tsv_audit))
        except (ValueError,KeyError,TypeError,SyntaxError) as error:
            audits.append(dict(round_id=f'R{number}',status='BLOCKED_SOURCE_CONFLICT',reason=str(error),source_bindings=entries))
    for number in (110,111,112,113):
        if number<=through_round:
            audits.append(dict(round_id=f'R{number}',status='UNKNOWN_LOCAL_MEASUREMENT_ARTIFACT_ABSENT',
                reason='Recipe provenance is not a measurement; no JSON/TSV arm synthesized'))
    return records,crossed,refs,audits


def load_all134_measurements(*,through_round=134,manifest_path=BQCF_INPUT_MANIFEST,include_auxiliary=True):
    _revision134(through_round)
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be exact boolean')
    base = _sealed92(R92_RECORDS_OUTPUT)
    new,_,refs,_ = _new_data134(through_round=through_round,manifest_path=manifest_path)
    records = [_measurement(r) for r in base['records']]+new
    return ([r for r in records if r.window_kind=='primary'] if not include_auxiliary else records),deepcopy(base['source_refs'])+refs


def load_all134_block_observations(*,through_round=134,manifest_path=BQCF_INPUT_MANIFEST):
    _revision134(through_round)
    base = _sealed92(R92_BLOCKS_OUTPUT)
    _,crossed,refs,_ = _new_data134(through_round=through_round,manifest_path=manifest_path)
    return dict(crossed=deepcopy(base['crossed'])+crossed,sequential=deepcopy(base['sequential']),source_refs=deepcopy(base['source_refs'])+refs)


def load_all96_measurements(**kwargs):
    return load_all134_measurements(through_round=96,**kwargs)


def load_all102_measurements(**kwargs):
    return load_all134_measurements(through_round=102,**kwargs)


def load_all107_measurements(**kwargs):
    return load_all134_measurements(through_round=107,**kwargs)


def load_all96_block_observations(**kwargs):
    return load_all134_block_observations(through_round=96,**kwargs)


def load_all102_block_observations(**kwargs):
    return load_all134_block_observations(through_round=102,**kwargs)


def load_all107_block_observations(**kwargs):
    return load_all134_block_observations(through_round=107,**kwargs)


def load_live_dataset(*,through_round=134):
    if type(through_round) is not int:
        raise ValueError('Exact integer frozen revision required')
    if through_round in (56,60,65,70,75,80,86,92):
        return load_r1_to_r92_dataset(through_round=through_round)
    _revision134(through_round)
    base = _sealed92(R92_RECORDS_OUTPUT);previous = _sealed92(R92_BLOCKS_OUTPUT)
    new,crossed,refs,audits = _new_data134(through_round=through_round)
    normalized = [{**asdict(r),'policy_key':r.policy_key,
        'slot_time_us':r.certified_wds_evidence['slot_time_us'],
        'ack_timeout_us':r.certified_wds_evidence['ack_timeout_us']} for r in new]
    records = deepcopy(base['records'])+normalized
    blocks = previous['crossed']+crossed
    return dict(schema_version=18,evidence='SEALED_R92_PLUS_SOURCE_AUTHENTICATED_AVAILABLE_R93_R134',
        automatic_execution_allowed=False,physical_acceptance_claim=False,software_versions=old.software_versions(),
        source_refs=deepcopy(base['source_refs'])+refs,input_manifest=_inputs134(),ac_order=list(old.AC_ORDER),records=records,
        observed_record_count=len(records),primary_window_count=sum(r['window_kind']=='primary' for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary' for r in records),new_arm_count=len(new),
        round_counts={f'R{i}':sum(r['round_id']==f'R{i}' for r in records) for i in range(1,through_round+1)},
        crossed_observation_count=len(blocks),matched_round_scoped_block_count=len({(b['round_id'],b['block_index']) for b in blocks}),
        sequential_repetition_count=len(previous['sequential']),round_audits=audits,
        distance_interpretation='SAVED_PROGRAMMED_TIMING_NOT_PHYSICAL_RANGE_OR_EFFECTIVE_CONTROL_PROOF')


def load_crossed_dataset(*,through_round=134):
    if type(through_round) is not int:
        raise ValueError('Exact integer frozen revision required')
    if through_round in (56,60,65,70,75,80,86,92):
        return _historical_crossed_dataset(through_round=through_round)
    return load_all134_block_observations(through_round=_revision134(through_round))


# Additive available-input revision. Historical defaults and serializers above stay unchanged.
HMAC_ARTIFACTS=ROOT/'artifacts/autoresearch/waves_cg_to_cj_20261024'
HMAC_MANIFEST=HMAC_ARTIFACTS/'inputs_manifest_v2.json'
HMAC_MANIFEST_SHA256='dfbf6115a13e33a15a4fd902d884df02836452d73e4a59c537528b4df6a3ddf5'
HMAC_PRIOR_RECORDS=BQCF_ARTIFACTS/'normalized_r1_to_r134_measurements_20261024.json'
HMAC_PRIOR_BLOCKS=BQCF_ARTIFACTS/'normalized_r16_to_r134_block_observations_20261024.json'
HMAC_PRIOR_PINS={HMAC_PRIOR_RECORDS.name:'ded87ff26e14138236b156919bb809805b9398bfe6f501e2dd74e6809b70bf7b',
                 HMAC_PRIOR_BLOCKS.name:'89f8fc33cd565cc62679ff28fe26df654b553d99a7ff3ca7051f94754d14dbbf'}
HMAC_CONTEXTS={135:(1000,2,15,30),136:(3000,6,27,48),137:(6000,13,48,69),
               138:(9000,20,69,90),139:(12000,26,87,108)}


def _hmac_rounds(round_ids):
    result=tuple(HMAC_CONTEXTS)if round_ids is None else tuple(round_ids)
    if not result or any(type(n)is not int or n not in HMAC_CONTEXTS for n in result)or len(set(result))!=len(result):
        raise ValueError('Only unique explicitly available R135-R139; reject before any input access')
    return tuple(sorted(result))


def _hmac_inputs(manifest_path=HMAC_MANIFEST,expected_manifest_sha256=HMAC_MANIFEST_SHA256):
    path=old._offline_path(manifest_path)
    if expected_manifest_sha256!=HMAC_MANIFEST_SHA256 or _binding(path)['sha256']!=expected_manifest_sha256:
        raise ValueError('Fixed cutoff manifest checksum mismatch')
    manifest=_json(path)
    if ([r.get('round_id')for r in manifest.get('available',[])]!=[f'R{n}'for n in HMAC_CONTEXTS]
            or manifest.get('missing_at_cutoff')!=list(range(140,147)) or len(manifest.get('bindings',[]))!=18):
        raise ValueError('Exact available cutoff and18frozen members required')
    seen=set();validated={}
    # Validate every path before opening any member, including filenames outside cutoff.
    for ref in manifest['bindings']:
        logical=ref.get('path');copy=ref.get('frozen_path')
        if not isinstance(logical,str)or '\\'in logical or ':'in logical or Path(logical).is_absolute()or '..'in Path(logical).parts or logical in seen:
            raise ValueError('Unique safe frozen logical path required')
        match=re.search(r'(?:^|_)r(\d+)(?:_|\.)',Path(logical).name)
        if match and int(match[1])not in HMAC_CONTEXTS:raise ValueError('Input filename outside available cutoff')
        expected=HMAC_ARTIFACTS/'inputs'/logical
        if copy!=expected.relative_to(ROOT).as_posix()or expected.is_symlink()or not expected.resolve().is_relative_to((HMAC_ARTIFACTS/'inputs').resolve()):
            raise ValueError('Exact frozen nested path required')
        if type(ref.get('bytes'))is not int or not isinstance(ref.get('sha256'),str):raise ValueError('Typed source pin required')
        seen.add(logical)
    for ref in manifest['bindings']:
        actual=_binding(ROOT/ref['frozen_path'])
        if any(actual[k]!=ref[k]for k in ('bytes','sha256')):raise ValueError('Frozen input size/hash mismatch')
        validated[ref['path']]={**deepcopy(ref),'original_path':ref['path'],'path':actual['path']}
    for item in manifest['available']:
        for logical in (item['receipt'],item['tsv_path'],item['recipe_paths'][0]):
            if logical not in validated:raise ValueError('Missing authenticated per-round receipt/TSV/recipe')
    return manifest,validated


def _hmac_recipe_packages(text,payload,*,max_round=139):
    """Adapt only the new literal seven-tuple (last coordinate=fq_flows), not execution."""
    tree=ast.parse(text)
    number=old._physical_round_number(payload,max_round=max_round)
    appliers=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==f'apply_r{number}_hmac_state']
    if len(appliers)!=1:raise ValueError('tx_aggr_factor recipe derivation must be explicit')
    derived=[value for node in ast.walk(appliers[0])if isinstance(node,ast.Return)and isinstance(node.value,ast.Dict)
             for key,value in zip(node.value.keys,node.value.values)if isinstance(key,ast.Constant)and key.value=='tx_aggr_factor']
    if len(derived)!=1 or not isinstance(derived[0],ast.Name)or derived[0].id!='airtime_flags':
        raise ValueError('tx_aggr_factor recipe must derive from airtime_flags')
    mains=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main']
    if len(mains)!=1:raise ValueError('Unique frozen main required')
    assignments=[n for n in mains[0].body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='arms'for t in n.targets)]
    if len(assignments)!=1 or not isinstance(assignments[0].value,ast.Dict):raise ValueError('Literal source A/B packages required')
    arms=assignments[0].value
    if [ast.literal_eval(k)for k in arms.keys]!=['A','B']:raise ValueError('Exact source A/B package order required')
    flows=[]
    for value in arms.values:
        if not isinstance(value,(ast.Tuple,ast.List))or len(value.elts)!=7:raise ValueError('Explicit seven-coordinate package required')
        flows.append(old.exact_integer(ast.literal_eval(value.elts[-1]),'source fq_flows',1,1_000_000))
        value.elts=value.elts[:6]
    # The old AST-only endpoint/control comparator remains byte-identical.
    packages=_literal_recipe_packages(ast.unparse(tree),payload)
    constants=[n.value for n in ast.walk(ast.parse(text))if isinstance(n,ast.Constant)and isinstance(n.value,str)]
    for package,item,fq_flows in zip(packages,payload['iterations'],flows):
        controls={}
        for key in ('tx_aggr_factor','fq_flows'):
            declarations=[old.exact_integer(obj[key],key,0 if key=='tx_aggr_factor'else 1,1_000_000)
                          for obj in (item,item['candidate_knobs'],item.get('readback',{}))if key in obj]
            if not declarations or len(set(declarations))!=1:raise ValueError('Conflicting or absent hMAC source control: '+key)
            controls[key]=declarations[0]
        if controls['fq_flows']!=fq_flows:raise ValueError('Recipe/receipt fq_flows mismatch')
        # The six-coordinate comparator already proved this AF equals the literal arm tuple.
        if controls['tx_aggr_factor']!=item['candidate_knobs']['airtime_flags']:
            raise ValueError('tx_aggr_factor differs from recipe-derived airtime_flags')
        package.update(controls=controls,tuple_adapter='AST_SEVEN_TO_SIX_PLUS_EXPLICIT_FQ_FLOWS_CHECK',
            queue_control_effect_verified=False,
            ping_TOS_0xb8_command_declared=any('ping 'in s and '-Q 0xb8'in s for s in constants),
            counter_interface_declared=any('phy0-ap0.sta1'in s for s in constants))
    return packages


def _convert_available_hmac_payload(number,payload,ref,recipe,text,tsv_text,*,contexts=None,max_round=139,measurement_type=None):
    contexts=HMAC_CONTEXTS if contexts is None else contexts
    measurement_type=old.HmacVoIPMeasurement if measurement_type is None else measurement_type
    if number not in contexts or old._physical_round_number(payload,max_round=max_round)!=number:
        raise ValueError('Exact available hMAC round identity required')
    if not isinstance(payload.get('iterations'),list)or len(payload['iterations'])!=2:raise ValueError('Two complete saved arms required')
    distance,coverage,slot,ack=contexts[number]
    for item in payload['iterations']:
        for declared in (payload,item,item.get('candidate_knobs')):
            if not isinstance(declared,dict):raise ValueError('Explicit shared context required')
            for key,expected in (('traffic_regime','bidir_8flow_voip_hmac'),('active_flow_count',8),('bidirectional',True),
                                 ('distance_m',distance),('coverage_class',coverage),('slot_time_us',slot),('ack_timeout_us',ack)):
                if type(declared.get(key))is not type(expected)or declared[key]!=expected:raise ValueError('Conflicting exact hMAC context: '+key)
        for endpoint in ('ap_state','cpe_state'):
            state=item['candidate_knobs'].get(endpoint)
            if not isinstance(state,dict):raise ValueError('Separate saved endpoints required')
            for key,expected in (('distance_m',distance),('distance_meters',distance),('coverage_class',coverage),('slot_time_us',slot),('ack_timeout_us',ack)):
                if key in state and(type(state[key])is not type(expected)or state[key]!=expected):raise ValueError('Conflicting endpoint context')
        for obj in (item,item['candidate_knobs']):
            if obj.get('voip_probe_tos')not in ('0xb8','0xb8 (DSCP EF -> AC_VO Queue 0 TID 6)'):
                raise ValueError('Exact saved TOS declaration required; queue mapping remains unverified')
        for raw in item.get('repetition_blocks',[]):
            if type(raw.get('crossover_step'))is not int or raw['crossover_step']not in (0,1):raise ValueError('Exact binary crossover step required')
            health=raw.get('observation',{})
            if not isinstance(health,dict):raise ValueError('Nested recorded observation must be an object')
            if health.get('restoration_ok')is not None and type(health['restoration_ok'])is not bool:raise ValueError('Reported restoration_ok must be boolean or unknown')
            if health.get('station_reset_count')is not None:old.exact_integer(health['station_reset_count'],'reported station_reset_count')
    packages=_hmac_recipe_packages(text,payload,max_round=max_round)
    tsv_audit=_audit_tsv134(tsv_text,payload)
    rows=old._exact_campaign_block_rows(payload,max_round=max_round)
    if len(rows)!=32 or {b['block_index']for b in rows}!=set(range(16)):raise ValueError('Exactly16genuine matched block IDs required')
    actual_schedule=[]
    ids=[item['commit']for item in payload['iterations']]
    for block in range(16):
        ordered=sorted((b for b in rows if b['block_index']==block),key=lambda b:b['crossover_step'])
        if len(ordered)!=2 or [b['crossover_step']for b in ordered]!=[0,1]:raise ValueError('Missing matched crossover coordinate')
        actual_schedule.append(['AB'[ids.index(b['treatment_id'])]for b in ordered])
    if payload.get('crossover_schedule')!=actual_schedule:raise ValueError('Declared schedule conflicts with saved coordinates')
    records=[]
    for position,(item,package)in enumerate(zip(payload['iterations'],packages)):
        selected=[b for b in rows if b['treatment_id']==item['commit']]
        rawblocks=item['repetition_blocks']
        for row,raw in zip(selected,rawblocks):
            counters={k:old.exact_integer(raw[k],k,0,10**12)if k in raw else None for k in
                ('tid0_be_tx_pkts_delta','tid0_be_drops_delta','tid6_vo_tx_pkts_delta','tid6_vo_drops_delta')}
            row.update(workload_regime='bidir_8flow_voip_hmac',active_flow_count=8,bidirectional=True,
                voip_probe_tos='0xb8',tid_counters=counters,hmac_source_controls=deepcopy(package['controls']),
                reported_block_health={k:raw.get('observation',{}).get(k)for k in ('restoration_ok','station_reset_count')},
                separate_voice_metrics=dict(latency_ms=None,jitter_ms=None,packet_loss_pct=None,mos=None),
                effective_AC_mapping_verified=False)
        source=deepcopy(item);source['distance_meters']=distance
        window=old._physical_window(source,number,position,selected)
        values={k:getattr(window,k)for k in old.ThreeTierMeasurement.__dataclass_fields__}
        values.update(workload_regime='bidir_8flow_voip_hmac',active_flow_count=8,bidirectional=True)
        audit=old.audit_dyadic_block_means(window)
        evidence=old._certified_summary_evidence(window,source,selected,ref,recipe,package['counter_interface_declared'])
        tid={k:old.exact_integer(item[k],k,0,10**12)if k in item else None for k in selected[0]['tid_counters']}
        tid_sums={k:sum(b['tid_counters'][k]for b in selected)if all(b['tid_counters'][k]is not None for b in selected)else None for k in tid}
        evidence.update(dyadic_mean_audit=audit,coverage_class=coverage,slot_time_us=slot,ack_timeout_us=ack,
            slot_ack_source='SHARED_PAYLOAD_TREATMENT_KNOBS',physical_distance_verified=False,
            effective_timing_independently_verified=False,source_tsv_audit=tsv_audit,
            recipe_literal_package=package,recorded_candidate_knobs=deepcopy(item['candidate_knobs']),
            recorded_window_observation=deepcopy(item['observation']),source_evaluation=deepcopy(item.get('evaluation',{})),
            tid_counter_window=tid,tid_counter_block_sums=tid_sums,tid_counter_sums_match=tid==tid_sums,
            frozen_recipe_coverage_command_declared=f'iw phy phy0 set coverage {coverage} 'in text,
            coverage_command_execution_or_readback_independently_verified=False,
            timing_formula_transfer_qualified=False,cross_source_PB_timing_authority='UNKNOWN_SEPARATE_SOURCE_AUDIT_REQUIRED',
            hmac_scheduler_effect_verified=False)
        readbacks={end:re.findall(r'\bfq_flows_cnt\s+(\d+)',item.get('readback',{}).get(end+'_readback',''))for end in ('ap','cpe')}
        evidence['fq_flows_readback_text_values']={end:[int(v)for v in found]for end,found in readbacks.items()}
        evidence['fq_flows_declared_vs_text_readback_match']={end:bool(found)and all(int(v)==package['controls']['fq_flows']for v in found)for end,found in readbacks.items()}
        voip=dict(probe_tos='0xb8',latency_ms=None,jitter_ms=None,packet_loss_pct=None,mos=None,
            generic_RTTs_retained_without_voice_alias=True,tid_counters=tid,
            effective_AC_mapping_verified=False,status='UNKNOWN_SEPARATELY_IDENTIFIED_VOICE_QOE_NOT_RETAINED')
        values['flags']=tuple(values['flags'])+('hmac_label_not_firmware_scheduler_authority','VoIP_QoE_unknown_no_ordinary_bidir8_alias')
        record=measurement_type(**values,**old._lower_mac_declarations(item),
            lower_mac_evidence='RECORDED_SHARED_DECLARATIONS_NOT_EFFECTIVE_CONTROL_PROOF',rtt_pool_order='CONCATENATED_BLOCK_ORDER',
            block_mean_consistent=evidence['block_mean_consistent'],raw_rtts_matches_blocks=evidence['raw_rtts_matches_blocks'],
            certified_wds_evidence=evidence,coverage_class=coverage,source_failure_metadata=deepcopy(selected[0]['source_failure_metadata']),
            dyadic_mean_audit=audit,hmac_source_controls=deepcopy(package['controls']),voip_probe_tos='0xb8',voip_evidence=voip)
        records.append({**asdict(record),'policy_key':record.policy_key,'slot_time_us':slot,'ack_timeout_us':ack})
    return records,rows,dict(round_id=f'R{number}',status='INGESTED_SAVED_PACKAGE_NOT_HMAC_OR_VOICE_QUALIFICATION',
        receipt=ref,recipe=recipe,tsv_audit=tsv_audit,recipe_executed=False)


def _available_hmac_new(round_ids=None,manifest_path=HMAC_MANIFEST,expected_manifest_sha256=HMAC_MANIFEST_SHA256):
    selected=_hmac_rounds(round_ids)
    manifest,refs=_hmac_inputs(manifest_path,expected_manifest_sha256)
    records=[];blocks=[];sources=[];audits=[]
    for item in manifest['available']:
        number=int(item['round_id'][1:])
        if number not in selected:continue
        receipt=refs[item['receipt']];recipe=refs[item['recipe_paths'][0]];tsv=refs[item['tsv_path']]
        new,crossed,audit=_convert_available_hmac_payload(number,_json(ROOT/receipt['path']),receipt,recipe,
            (ROOT/recipe['path']).read_text(encoding='utf-8'),(ROOT/tsv['path']).read_text(encoding='utf-8'))
        records.extend(new);blocks.extend(crossed);sources.append({**receipt,'round_id':f'R{number}','source_recipe':recipe,'source_tsv':tsv});audits.append(audit)
    return records,blocks,sources,audits


def _hmac_prior(path):
    if _binding(path)['sha256']!=HMAC_PRIOR_PINS[path.name]:raise ValueError('Sealed R134 corpus checksum mismatch')
    return _json(path)


def load_available_hmac_dataset(*,round_ids=None,manifest_path=HMAC_MANIFEST,expected_manifest_sha256=HMAC_MANIFEST_SHA256):
    """Cumulative saved records; explicit available hMAC/VoIP revision, old defaults unchanged."""
    _hmac_rounds(round_ids)
    new,blocks,refs,audits=_available_hmac_new(round_ids,manifest_path,expected_manifest_sha256)
    prior=_hmac_prior(HMAC_PRIOR_RECORDS);records=deepcopy(prior['records'])+new
    return dict(schema_version=19,evidence='SEALED_R134_PLUS_FROZEN_AVAILABLE_HMAC_VOIP_PACKAGES',
        records=records,source_refs=deepcopy(prior['source_refs'])+refs,input_manifest=_binding(Path(manifest_path)),
        new_round_audits=audits,available_at_cutoff=list(HMAC_CONTEXTS),missing_at_cutoff=list(range(140,147)),
        observed_record_count=len(records),primary_window_count=sum(r['window_kind']=='primary'for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary'for r in records),new_crossed_observation_count=len(blocks),
        automatic_execution_allowed=False,physical_acceptance=False,software_versions=old.software_versions())


def load_available_hmac_blocks(*,round_ids=None,manifest_path=HMAC_MANIFEST,expected_manifest_sha256=HMAC_MANIFEST_SHA256):
    _hmac_rounds(round_ids)
    _,blocks,refs,audits=_available_hmac_new(round_ids,manifest_path,expected_manifest_sha256)
    prior=_hmac_prior(HMAC_PRIOR_BLOCKS)
    return dict(crossed=deepcopy(prior['crossed'])+blocks,sequential=deepcopy(prior['sequential']),
        source_refs=deepcopy(prior['source_refs'])+refs,input_manifest=_binding(Path(manifest_path)),
        available_at_cutoff=list(HMAC_CONTEXTS),missing_at_cutoff=list(range(140,147)),new_round_audits=audits,
        automatic_execution_allowed=False,physical_acceptance=False)
