"""Pure offline information and non-actuating campaign contracts."""
import importlib
from copy import deepcopy
from dataclasses import FrozenInstanceError
import json
import math
from pathlib import Path
import pytest


def scheduler():return importlib.import_module('orchestration.autoresearch.fmx_knob_campaign_scheduler')


def test_ideal_binary_information_is_one_bit():
    assert scheduler().expected_information_gain([.5,.5],[[1,0],[0,1]])==1


def test_original_frontier_default50_remains_blocked():
    s=scheduler();frontier=s.load_frontier(s.DEFAULT_MATRIX,s.FRONTIER_SHA256)
    plan=s.build_campaign_schedule(frontier)
    assert len(plan['campaigns'])==50 and plan['physical_ready_count']==0
    assert all(c['status']=='BLOCKED'and c['expected_information_gain_bits']is None for c in plan['campaigns'])


@pytest.fixture(scope='module')
def frontier():
    s=scheduler();return s.load_frontier(s.DEFAULT_MATRIX,s.FRONTIER_SHA256)


def test_uninformative_channel_zero_and_nonuniform_bayes():
    s=scheduler()
    assert s.expected_information_gain([.9,.1],[[.5,.5],[.5,.5]])==pytest.approx(0,abs=1e-14)
    entropy=lambda p:-sum(x*math.log2(x)for x in p if x)
    assert s.expected_information_gain([.9,.1],[[.8,.2],[.2,.8]])==pytest.approx(entropy([.74,.26])-entropy([.8,.2]))
    assert s.expected_information_gain([1,0],[[1,0],[0,1]])==0
    assert s.expected_information_gain([1],[[1]])==0


def test_joint_hypothesis_and_outcome_permutation_invariance():
    s=scheduler();p=[.7,.2,.1];likelihood=[[.8,.1,.1],[.2,.6,.2],[.1,.1,.8]]
    expected=s.expected_information_gain(p,likelihood)
    assert s.expected_information_gain(p[::-1],likelihood[::-1])==pytest.approx(expected)
    assert s.expected_information_gain(p,[r[::-1]for r in likelihood])==pytest.approx(expected)


@pytest.mark.parametrize('prior,likelihood',[
    ([True,False],[[1,0],[0,1]]),([.4,.4],[[1,0],[0,1]]),([-1,2],[[1,0],[0,1]]),
    ([float('nan'),1],[[1,0],[0,1]]),([float('inf'),0],[[1,0],[0,1]]),
    ([10**1000,0],[[1,0],[0,1]]),([.5,.5],[[1,0]]),([.5,.5],[[1,0],[1]]),
    ([.5,.5],[[1,0],[.2,.2]]),([.5,.5],[[1,0],[True,False]]),([],[]),([1],[[]])])
def test_invalid_probability_models_fail_closed(prior,likelihood):
    with pytest.raises(ValueError):scheduler().expected_information_gain(prior,likelihood)


def test_exact248_81_167_and_no_build_or_namespace_alias(frontier):
    s=scheduler();plan=s.build_campaign_schedule(frontier)
    eligible={r['id']for r in frontier.matrix['rows']if r['classification']['status']==s.UNTESTED}
    assert len(eligible)==81 and len(plan['excluded_control_ids'])==167
    assert {r['control_id']for r in plan['ranked_controls']}==eligible
    assert not eligible.intersection(plan['excluded_control_ids'])
    assert [r['control_id']for r in plan['ranked_controls']]==sorted(eligible)
    assert all(r['hypothetical_information_gain_bits']==1 and r['expected_information_gain_bits']is None for r in plan['ranked_controls'])
    assert plan==s.build_campaign_schedule(frontier)and s.validate_schedule(plan,frontier)
    for c in plan['campaigns']:
        assert c['prospective_recipe']['exactly_one_varied_control']==c['control_id']
        assert c['physical_command']is c['treatment_value']is c['restore_value']is c['approved_safe_range']is None
        assert c['treatment_authorized']is c['physical_ready']is c['automatic_execution_allowed']is False
        assert all(p['satisfied']is False for p in c['prerequisites'])


def test_bound_source_copies_cannot_mutate_frontier(frontier):
    before=scheduler().build_campaign_schedule(frontier)
    view=frontier.matrix;view['rows'].clear()
    assert scheduler().build_campaign_schedule(frontier)==before
    with pytest.raises(FrozenInstanceError):frontier.matrix_bytes=b'{}'


def test_original_row_identity_units_and_help_only_are_provenance_not_effect(frontier):
    s=scheduler();original={r['id']:r for r in frontier.original_catalog['knobs']}
    rows={r['id']:r for r in frontier.matrix['rows']}
    # Vary hypothetical scores to include all eligible IDs in selected finite batches.
    for chosen in ('codel_target','codel_interval','cake_bandwidth','ct_special_5'):
        models={key:dict(prior=[1],likelihoods=[[1]])for key,row in rows.items()if row['classification']['status']==s.UNTESTED}
        models[chosen]=dict(prior=[.5,.5],likelihoods=[[1,0],[0,1]])
        c=s.build_campaign_schedule(frontier,limit=1,models=models)['campaigns'][0]
        assert c['control_id']==chosen and c['source_identity']['interface']==original[chosen]['interface']
        assert c['source_identity']['source_unit']==original[chosen]['encoding_domain'].get('unit')
        assert c['source_identity']['original_row_sha256']==s.canonical_sha(original[chosen])
        assert c['status']=='BLOCKED'and c['expected_information_gain_bits']is None


@pytest.mark.parametrize('limit',[True,0,51,81,50.0,None])
def test_invalid_limit_not_silently_coerced(frontier,limit):
    with pytest.raises(ValueError):scheduler().build_campaign_schedule(frontier,limit=limit)


def test_partial_unknown_or_physical_model_metadata_rejected(frontier):
    s=scheduler();model=dict(prior=[.5,.5],likelihoods=[[1,0],[0,1]])
    with pytest.raises(ValueError):s.build_campaign_schedule(frontier,models={'ct_special_5':model})
    models={r['control_id']:deepcopy(model)for r in s.build_campaign_schedule(frontier)['ranked_controls']}
    models['unknown']=model
    with pytest.raises(ValueError):s.build_campaign_schedule(frontier,models=models)
    del models['unknown'];models['ct_special_5']['authority']=True
    with pytest.raises(ValueError):s.build_campaign_schedule(frontier,models=models)


@pytest.mark.parametrize('mutation',[
    lambda p:p['campaigns'][0].update(physical_command='device-write'),
    lambda p:p['campaigns'][0].update(treatment_value=1),
    lambda p:p['campaigns'][0].update(physical_ready=True),
    lambda p:p['campaigns'][0].update(control_id='ct_special_7'),
    lambda p:p['campaigns'][0].update(control_id='ct_special_6'),
    lambda p:p['campaigns'][0].update(control_id='unknown'),
    lambda p:p['campaigns'][0]['source_identity']['interface'].update(selector='999'),
    lambda p:p['campaigns'].reverse(),
    lambda p:p['campaigns'].append(deepcopy(p['campaigns'][0])),
    lambda p:p['ranked_controls'][0].update(hypothetical_information_gain_bits=2),
    lambda p:p['campaigns'][0].update(expected_information_gain_bits=1),
    lambda p:p.update(physical_ready_count=50),
    lambda p:p.update(limit=True),
    lambda p:p.update(models={'unknown':{'prior':[.5,.5],'likelihoods':[[1,0],[0,1]]}})])
def test_artifact_tampering_never_overrides_source_or_authority(frontier,mutation):
    s=scheduler();plan=s.build_campaign_schedule(frontier);mutation(plan)
    with pytest.raises(ValueError):s.validate_schedule(plan,frontier)


def test_no_metadata_path_following_or_authority_override(frontier,monkeypatch):
    s=scheduler();plan=s.build_campaign_schedule(frontier)
    def forbidden(*args,**kwargs):pytest.fail('Validation must use caller-bound bytes, not metadata paths')
    monkeypatch.setattr(Path,'read_bytes',forbidden)
    assert s.validate_schedule({'plan':plan,'status':'untrusted metadata','bindings':[{'path':'never-open-this'}]},frontier)
    with pytest.raises(ValueError):s.validate_schedule({'plan':plan,'automatic_execution_allowed':True},frontier)
    with pytest.raises(ValueError):s.validate_schedule({'plan':plan,'software_verification':{'physical_ready':True}},frontier)
    with pytest.raises(ValueError):s.validate_schedule({'plan':plan,'software_verification':{'score':float('nan')}},frontier)


def test_wrong_pin_rejects_before_path_read_and_corruption_rejects(tmp_path,monkeypatch):
    s=scheduler()
    with monkeypatch.context()as m:
        m.setattr(Path,'read_bytes',lambda *args:pytest.fail('Wrong trusted pin must not access files'))
        with pytest.raises(ValueError):s.load_frontier('never-open-this','0'*64)
    raw=s.DEFAULT_MATRIX.read_bytes();bad=tmp_path/'matrix.json';bad.write_bytes(raw[:-1]+b' ')
    with pytest.raises(ValueError):s.load_frontier(bad,s.FRONTIER_SHA256)
    with pytest.raises(ValueError):s.load_frontier(s.DEFAULT_MATRIX,s.FRONTIER_SHA256,bad)


def test_cli_generate_validate_and_explicit_offline_command(tmp_path,capsys):
    s=scheduler();output=tmp_path/'plan.json'
    assert s.main(['--generate',str(output)])==0
    plan=json.loads(output.read_text());assert s.validate_schedule(plan,s.load_frontier(),artifact_path=output)
    command=plan['campaigns'][0]['offline_validation_command']
    assert command[:4]==['python','-B','-m','orchestration.autoresearch.fmx_knob_campaign_scheduler']
    assert '--generate'not in command and command[command.index('--validate')+1]==str(output.resolve())
    assert s.main(command[4:])==0
    with pytest.raises(FileExistsError):s.main(['--generate',str(output)])
    with pytest.raises(ValueError):s.main(['--validate',str(output),'--campaign-id','unknown'])
    output.write_text(output.read_text().replace('"physical_ready_count": 0','"physical_ready_count": 50'))
    with pytest.raises(ValueError):s.main(['--validate',str(output)])


@pytest.mark.parametrize('entry',['matrix','catalog','artifact'])
def test_resolved_remote_path_rejected_before_content_access(tmp_path,monkeypatch,entry):
    s=scheduler();fake=tmp_path/'local-reparse-looking.json'
    resolved_remote=Path(r'\\offline-test.invalid\share\never-open.json')
    real_resolve=Path.resolve;real_read=Path.read_bytes
    remote_reads=[]
    def resolve(path,*args,**kwargs):
        return resolved_remote if path==fake else real_resolve(path,*args,**kwargs)
    def read(path,*args,**kwargs):
        if str(path).startswith(('\\\\','//')):
            remote_reads.append(str(path))
            raise AssertionError('Resolved remote path reached content access')
        return real_read(path,*args,**kwargs)
    monkeypatch.setattr(Path,'resolve',resolve);monkeypatch.setattr(Path,'read_bytes',read)
    with pytest.raises(ValueError):
        if entry=='matrix':s.load_frontier(fake)
        elif entry=='catalog':s.load_frontier(original_catalog_path=fake)
        else:s.main(['--validate',str(fake)])
    assert remote_reads==[]
