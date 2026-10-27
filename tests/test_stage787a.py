import copy
import math
import pytest
from tools.sim import run_stage787a_wa_vht20_78mbps_vs_vht40_channel_efficiency_sim as m


def test_saved_anchor_arithmetic_and_mean():
    payloads,_=m.h.freeze(m.ROOT,787,m.SOURCES);a=m.anchor(m.h.json_source(payloads[m.SOURCE]))
    assert a['peak_reported_mbps']==78.513 and a['peak_window']=='B1'
    assert a['peak_efficiency_bps_hz']==pytest.approx(3.92565)
    assert round(a['peak_efficiency_bps_hz'],2)==3.93
    assert a['b_mean_mbps']==pytest.approx(76.5455)
    assert all(w['metric_consistent']for w in a['windows'])


def test_no_interference_double_capacity_equal_efficiency():
    r=m.compare(80,0,0,2)
    assert [x['goodput_mbps']for x in r['rows']]==[80,160]
    assert r['rows'][0]['efficiency_bps_hz']==r['rows'][1]['efficiency_bps_hz']==4
    assert r['frontier_indices']==[1]


def test_edge_interference_reverses_throughput_preference():
    r=m.compare(80,0,.6,2)
    assert r['rows'][1]['goodput_mbps']==pytest.approx(64)
    assert r['frontier_indices']==[0]
    assert m.compare(80,.2,.1,2)['frontier_indices']==[0,1]


def test_complete_busy_channel_and_saturation():
    assert all(r['goodput_mbps']==0 for r in m.compare(80,1,1,2)['rows'])
    assert m.compare(80,.5,.8,2)['busy40']==1


@pytest.mark.parametrize('args', [(0,0,0,2),(80,-.1,0,2),(80,0,1.1,2),(80,0,0,2.1),
                                  (True,0,0,2),(80,math.nan,0,2),(math.inf,0,0,2)])
def test_invalid_inputs_rejected(args):
    with pytest.raises(ValueError):m.compare(*args)


def test_model_monotone_and_efficiency_bound():
    for b in (0,.2,.5):
        cells=[m.compare(78.513,b,e,2)for e in (0,.1,.3,.5,.8)]
        rates=[r['rows'][1]['goodput_mbps']for r in cells]
        assert rates==sorted(rates,reverse=True)
        assert all(r['rows'][1]['efficiency_bps_hz']<=r['rows'][0]['efficiency_bps_hz']+1e-12 for r in cells)


@pytest.mark.parametrize('text',[b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":1e999}'])
def test_strict_json_rejects_invalid_finite_contract(text):
    with pytest.raises(ValueError):m.h.strict(text)


def test_immutable_copy_survives_origin_change_and_rejects_corruption(tmp_path):
    p=tmp_path/'raw.json';p.write_text('{"v":1}')
    first,pins=m.h.freeze(tmp_path,787,['raw.json']);p.write_text('{"v":2}')
    assert m.h.freeze(tmp_path,787,['raw.json'])==(first,pins)
    assert m.h.origins(tmp_path,pins)[0]['status']=='CHANGED_SINCE_FROZEN_CUTOFF'
    (tmp_path/pins[0]['frozen']['path']).write_text('corrupt')
    with pytest.raises(ValueError,match='corrupted'):m.h.freeze(tmp_path,787,['raw.json'])


@pytest.mark.parametrize('label',['../x','/absolute','C:/secret','//host/share','a\\b','a/./b'])
def test_offline_path_rejection_before_any_read(tmp_path,label):
    with pytest.raises(ValueError):m.h.freeze(tmp_path,787,[label])


def test_saved_output_matches_code_and_frozen_inputs():
    r=m.h.json_source(m.h.snapshot(m.ROOT,m.OUT)[0]);assert r['stage']=='787A'
    assert not any(r['boundary'].values()) and r['new_hardware_results']==0
    assert len(r['cells'])==45 and not r['model']['empirical_calibration']
    for pin in [r['implementation'],*r['analysis_dependencies'],r['outputs'][m.DOC]]:
        assert m.h.snapshot(m.ROOT,pin['path'])[1]==pin
    for row in r['static_sources']:assert m.h.snapshot(m.ROOT,row['frozen']['path'])[1]==row['frozen']
    assert len(m.DOC_TEXT.splitlines())<200
