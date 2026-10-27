"""New source scope cannot bypass strict budget, workload or execution gates."""
import pytest
from controller.airmax_aql_autotuner import advise_airmax_aql
from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import load_operator_evidence
from tests.test_fmx_multi_regime_dyadic_selector import make_as_operator_view, source_package_mutation


@pytest.mark.parametrize('execute',[True,1,None,'yes'])
def test_extended_facade_execute_request_rejects_before_evidence(execute):
    class NoRead:
        def parse(self):raise AssertionError('Execution request cannot read evidence')
    out=advise_airmax_aql(NoRead(),regime='unidir_ul_8flow_hammer',distance_meters=1000,coverage_class=2,execute=execute)
    assert out['reason']=='OFFLINE_EXECUTION_DISABLED'
    assert out['candidate_policy'] is None and out['automatic_execution_allowed'] is False


def test_extended_facade_selects_literal_ul8_package_only(tmp_path):
    cfg,_,_=make_as_operator_view(tmp_path,round_id='R134',regime='unidir_ul_8flow_hammer',distance=1000,
                                mutate=source_package_mutation())
    evidence=load_operator_evidence(current=cfg)
    out=advise_airmax_aql(evidence,regime='unidir_ul_8flow_hammer',distance_meters=1000,coverage_class=2)
    assert out['status']=='ELIGIBLE_OFFLINE_STRICT_CONTEXT',out
    assert out['candidate_policy'][0]['new_source_controls']=={'rts_threshold':'256','ap_ack_clocking':True}
    assert out['candidate_policy'][1]['new_source_controls']=={'rts_threshold':'256'}
    assert out['selected']['profile_contrast_scope']['excluded_inapplicable_metrics']==['jain_fairness','dl_goodput_mbps']
    wrong=advise_airmax_aql(evidence,regime='unidir_ul_2flow',distance_meters=1000,coverage_class=2)
    assert wrong['status']=='ABSTAIN' and wrong['candidate_policy'] is None


def test_extension_does_not_rescue_goodput_budget_failure(tmp_path):
    cfg,_,_=make_as_operator_view(tmp_path,round_id='R96',regime='bidir_2flow',distance=14000,gp_loss=2.01)
    out=advise_airmax_aql(load_operator_evidence(current=cfg),regime='bidir_2flow',distance_meters=14000)
    assert out['status']=='BLOCKED' and out['candidate_policy'] is None
    assert any('OPERATOR_GOODPUT_DROP_LIMIT_EXCEEDED' in x['reasons'] for x in out['structural_profiles'])
