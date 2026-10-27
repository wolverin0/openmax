"""Offline advice never grants actuation or fills unobserved contexts."""
import pytest
from controller.airmax_aql_autotuner import advise_airmax_aql
from tests.test_fmx_pareto_decomposer import NoRead,bound


@pytest.mark.parametrize('execute',[True,0,1,None,'false'])
def test_every_nonfalse_execution_option_rejects_before_evidence_access(execute):
    out=advise_airmax_aql(NoRead(),regime='bidir_6flow',distance_meters=7500,execute=execute)
    assert out['status']=='BLOCKED' and out['reason']=='OFFLINE_EXECUTION_DISABLED'
    assert out['candidate_policy'] is None and out['automatic_execution_allowed'] is False


def test_qualified_observed_package_is_advice_only(tmp_path):
    evidence,_,target,_=bound(tmp_path,gp_loss=1.25)
    out=advise_airmax_aql(evidence,regime='bidir_6flow',distance_meters=7500)
    assert out['selected']['policy_id']==target
    assert len(out['candidate_policy'])==2
    assert out['advisory_only'] is True
    assert out['automatic_execution_allowed'] is out['physical_acceptance'] is False
    assert out['distance_interpretation']=='DECLARED_TIMING_CONTEXT_ONLY'


@pytest.mark.parametrize('loss',[2,2.01,4.211])
def test_budget_failures_cannot_emit_a_policy(tmp_path,loss):
    evidence,_,_,_=bound(tmp_path,gp_loss=loss)
    out=advise_airmax_aql(evidence,regime='bidir_6flow',distance_meters=7500)
    assert out['selected'] is out['candidate_policy'] is None
    assert not out['automatic_execution_allowed']


def test_no_nearest_distance_or_unobserved_flow_fallback(tmp_path):
    evidence,_,_,_=bound(tmp_path,gp_loss=1.25)
    out=advise_airmax_aql(evidence,regime='bidir_8flow',distance_meters=7500)
    assert out['selected'] is out['candidate_policy'] is None
    assert out['reason']=='NO_OBSERVED_CONTEXT'


def test_no_nonunanimity_exception_for_af3_or_positive_gp(tmp_path):
    evidence,_,_,_=bound(tmp_path,round_id='R80',gp_loss=-1,p50_reversal=True)
    out=advise_airmax_aql(evidence,regime='bidir_6flow',distance_meters=7500)
    assert out['candidate_policy'] is None


@pytest.mark.parametrize('regime,round_id',[('unidir_dl_2flow','R81'),('unidir_ul_2flow','R82')])
def test_bk_active_direction_observed_package_is_advice_with_execution_disabled(tmp_path,regime,round_id):
    evidence,_,target,_=bound(tmp_path,regime=regime,round_id=round_id,distance=100)
    out=advise_airmax_aql(evidence,regime=regime,distance_meters=100)
    assert out['selected']['policy_id']==target and len(out['candidate_policy'])==2
    assert out['automatic_execution_allowed'] is out['physical_acceptance'] is False
    assert out['advisory_only'] is True
    stopped=advise_airmax_aql(NoRead(),regime=regime,distance_meters=100,execute=True)
    assert stopped['status']=='BLOCKED' and stopped['candidate_policy'] is None


@pytest.mark.parametrize('round_id,regime,distance',[('R87','unidir_dl_2flow',100),('R88','bidir_4flow',12000),('R89','bidir_4flow',14000),('R90','bidir_6flow',14000),('R91','bidir_2flow',3000),('R92','bidir_2flow',6000)])
def test_bo_new_observed_package_stays_nonactuating(tmp_path,round_id,regime,distance):
    evidence,_,target,_=bound(tmp_path,round_id=round_id,regime=regime,distance=distance)
    out=advise_airmax_aql(evidence,regime=regime,distance_meters=distance)
    assert out['selected']['policy_id']==target
    assert out['candidate_policy'] and out['advisory_only'] is True
    assert out['automatic_execution_allowed'] is out['physical_acceptance'] is False
    assert advise_airmax_aql(NoRead(),regime=regime,distance_meters=distance,execute=True)['reason']=='OFFLINE_EXECUTION_DISABLED'


def test_bo_advice_class33_policy_block_is_not_a_hardware_claim():
    out=advise_airmax_aql(NoRead(),regime='bidir_6flow',distance_meters=15000)
    assert out['selected'] is out['candidate_policy'] is None
    assert out['reason']=='COVERAGE_CLASS_EXCEEDS_SUPPORTED_POLICY_MAX31'
    assert out['coverage_policy']['hardware_ceiling_verified'] is False
