"""Shared local evidence contract; never acquires RF or runs a device command."""
import ast
from pathlib import Path
import pytest
from tools.verify import run_stage358a_ground_up_regression as gate


@pytest.mark.parametrize('stage', range(353,359))
def test_each_stage_has_own_script_compact_doc_and_dedicated_suite(stage):
    if stage in gate.STAGES:
        script, _, doc = gate.STAGES[stage]; doc = 'docs/'+doc
    else: script, doc = gate.SCRIPT, gate.DOC
    for label in (script, f'tests/test_stage{stage}a.py'):
        text = gate.c.read(gate.ROOT/label).decode('utf-8'); ast.parse(text)
    text = gate.c.read(gate.ROOT/doc).decode('utf-8')
    assert len(text.splitlines()) < 220 and text.startswith('<!-- doc-head:')
    assert text.count('<!-- doc-head:') == text.count('<!-- /doc-head -->') == 1
    assert '<!-- /doc-head -->' in text.splitlines()[1:8]


@pytest.mark.parametrize('stage', range(353,358))
def test_saved_receipts_keep_physical_and_source_boundaries(stage):
    _, filename, _ = gate.STAGES[stage]
    r = gate.c.load(gate.ROOT/'artifacts/autoresearch'/filename)
    assert r['stage'] == str(stage)+'A'
    assert r['boundary']['physical_acceptance'] is False
    assert r['summary'].get('hardware_results', r['summary'].get('new_hardware_results', 0)) == 0
    for source in r['static_sources']:
        assert gate.c.sha(gate.c.read(gate.ROOT/source['path'])) == source['sha256']


def test_no_model_to_native_or_ledger_to_acceptance_promotion():
    def receipt(stage): return gate.c.load(gate.ROOT/'artifacts/autoresearch'/gate.STAGES[stage][1])
    rate = receipt(354); hopping = receipt(355); bundle = receipt(356); ledger = receipt(357)
    assert rate['boundary']['native_188b_wmi_abi'] == 'BLOCKED'
    assert rate['boundary']['native_wmi_payload_hex'] is None
    assert not hopping['assumptions']['parameters_are_measured']
    assert not hopping['boundary']['native_channel_or_TDD_executor']
    assert bundle['summary']['current_kits_flash_approved'] == 0
    assert not bundle['boundary']['zero_brick_guarantee']
    assert ledger['cutoff_stage'] == 350 and ledger['summary']['numeric_stage_ids_missing']
    assert 'PRESENCE_HEURISTIC' in ledger['structural_gate_meaning']


def test_simulators_use_real_libraries_with_explicit_synthetic_qualification():
    import simpy
    from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
    assert simpy.__version__ and NonDominatedSorting().do(__import__('numpy').array([[1,2],[2,1]]))[0].size == 2
    for stage in (354,355):
        text = gate.c.read(gate.ROOT/gate.STAGES[stage][0]).decode('utf-8')
        assert 'simpy.Environment' in text
