"""Disposable seven-knot API checks; fixtures cannot certify a physical curve."""
import pytest
from orchestration.autoresearch.fmx_distance_slot_surface import build_distance_surface, PRIMARY_KNOTS
from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import load_operator_evidence
from orchestration.autoresearch.fmx_pareto_decomposer import decompose_extended_distance_grid
from tests.test_fmx_multi_regime_dyadic_selector import make_as_operator_view


def test_one_saved_knot_does_not_fabricate_remaining_six(tmp_path):
    cfg,_,_=make_as_operator_view(tmp_path,round_id='R104',regime='unidir_dl_2flow',distance=6000)
    out=build_distance_surface(load_operator_evidence(current=cfg),regime='unidir_dl_2flow')
    assert len(out['points'])==7 and len(out['missing_or_blocked_knots'])==6
    assert out['qualified_knots']==1
    assert out['complete_curve_qualified'] is out['all_seven_primary_points_qualified'] is False
    assert out['physical_acceptance'] is out['automatic_execution_allowed'] is out['interpolated'] is False
    assert out['points'][1]['distance_meters']==1000 and out['points'][1]['selected'] is None


def test_extended_grid_retains_both12km_declarations_and_ul8_separation(tmp_path):
    cfg,_,_=make_as_operator_view(tmp_path,round_id='R120',regime='unidir_ul_2flow',distance=12000,coverage_class=26)
    out=decompose_extended_distance_grid(load_operator_evidence(current=cfg))
    assert (out['context_count'],out['supported_policy_context_count'],out['historical_unsupported_context_count'])==(98,91,7)
    cells=[p for p in out['cells'] if p['regime']=='unidir_ul_2flow' and p['distance_meters']==12000]
    assert {p['requested_coverage_class']:p['selected'] is not None for p in cells}=={26:True,27:False}
    assert all(p['selected'] is None for p in out['cells'] if p['regime']=='unidir_ul_8flow_hammer')
    assert out['all_supported_cells_qualified'] is False


@pytest.mark.parametrize('knots',[[],[(100,0),(100,0)],[(100,False)],[(100,)],'100,0'])
def test_invalid_surface_request_rejects_without_reading(knots):
    class NoRead:
        def parse(self):raise AssertionError('Invalid knots must not open evidence')
    assert build_distance_surface(NoRead(),regime='unidir_dl_2flow',knots=knots)['status']=='BLOCKED'
