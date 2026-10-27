"""Disposable host-only evidence-boundary regressions, no acquisition imports."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from orchestration.autoresearch import fmx_knob_frontier_audit as audit


@pytest.fixture
def original():return audit.original_catalog()


def test_exact_original248_is_retained_not_current_first248(original):
    ids={r['id']for r in original['knobs']}
    current=json.loads(audit.CURRENT.read_text(encoding='utf-8'))
    assert len(ids)==248 and len(original['sources'])==33
    assert 'wa_8_7_25_sys_module_umac_parameters'in ids
    assert 'wa_8_7_25_sys_module_umac_parameters'not in {r['id']for r in current['knobs']}
    assert ids!={r['id']for r in current['knobs'][:248]}


def test_source_hash_rejects_same_length_modified_catalog(tmp_path):
    p=tmp_path/'catalog.json';p.write_text('{"id":1}')
    import hashlib
    pin=hashlib.sha256(p.read_bytes()).hexdigest();p.write_text('{"id":2}')
    with pytest.raises(ValueError):audit.read_pinned(p,pin)


@pytest.mark.parametrize('ref',[{'round':True},{'round':135},{'round':110},{'round_id':'R113'},
    {'round':93,'round_id':'R94'},{'round_id':'93'},{'round':93.0},{}])
def test_missing_future_or_conflicting_round_rejected_before_content(ref,monkeypatch):
    def forbidden(*args):raise AssertionError('No content read allowed')
    monkeypatch.setattr(audit,'binding',forbidden)
    with pytest.raises(ValueError):audit.frozen_receipts([dict(ref,path='artifacts/autoresearch/inputs/r135.json',sha256='0'*64)])


@pytest.mark.parametrize('path',['artifacts/autoresearch/live_r93.json','../inputs/r93.json','https://example/inputs/r93.json'])
def test_original_live_path_and_traversal_never_used_as_frozen_receipt(path,monkeypatch):
    monkeypatch.setattr(audit,'binding',lambda *args:pytest.fail('No content access'))
    with pytest.raises(ValueError):audit.frozen_receipts([dict(round=93,path=path,sha256='0'*64)])


def fixture_arm():
    return dict(commit='candidate',candidate_knobs=dict(ap_state=dict(vo_low_us=500,vo_high_us=1100,
        vi_low_us=600,vi_high_us=1200,be_low_us=1900,be_high_us=3800,bk_low_us=500,bk_high_us=1100,
        rc_per_thresh=24,rts_threshold='off',aql_threshold_us=7600,fq_quantum_bytes=256),
        cpe_state=dict(rc_per_thresh=50),coverage_class=26))


def test_explicit_coordinate_order_and_endpoint_asymmetry():
    arm=fixture_arm()
    assert audit.source_coordinate(arm,'ap','aql_by_ac')['value']==[[500,1100],[600,1200],[1900,3800],[500,1100]]
    assert audit.source_coordinate(arm,'ap','rc_per_thresh')['value']==24
    assert audit.source_coordinate(arm,'cpe','rc_per_thresh')['value']==50
    assert audit.source_coordinate(arm,'ap','coverage_class')['value']==26


def test_missing_field_never_becomes_zero_default_or_sibling_value():
    arm=fixture_arm()
    assert audit.source_coordinate(arm,'cpe','fq_quantum_bytes')is None
    assert audit.source_coordinate(arm,'ap','htt_pair')is None
    assert audit.source_coordinate(dict(candidate_knobs={}), 'ap','rts_threshold')is None
    assert audit.source_coordinate(arm,'ap','rts_threshold')['value']is None # explicit saved off


def test_explicit_flat_and_endpoint_prefixed_schema_not_fuzzy():
    shared=dict(candidate_knobs=dict(aql_low_us=1000,aql_high_us=2000,ct_rc_per_thresh=28))
    assert audit.source_coordinate(shared,'ap','aql_by_ac')['value']==[[1000,2000]]*4
    assert audit.source_coordinate(shared,'ap','rc_per_thresh')['value']==28
    prefixed=dict(candidate_knobs=dict(ap_rc_per_thresh=24,cpe_rc_per_thresh=50))
    assert audit.source_coordinate(prefixed,'cpe','rc_per_thresh')['value']==50
    assert audit.source_coordinate(dict(candidate_knobs=dict(not_really_rc_per_thresh=24)),'ap','rc_per_thresh')is None


@pytest.mark.parametrize('bad',[True,float('nan'),float('inf'),{},[False]])
def test_numeric_control_bool_nonfinite_and_object_rejected(bad):
    with pytest.raises(ValueError):audit.source_coordinate(dict(candidate_knobs=dict(rc_per_thresh=bad)),'ap','rc_per_thresh')


def test_control_id_with_different_interface_never_name_matches(original):
    row=deepcopy(next(r for r in original['knobs']if r['id']=='ct_special_7'))
    row['interface']['selector']='8'
    with pytest.raises(ValueError):audit.evidence_for_control(row,[],{}, {})


def test_closed_build_or_protected_control_never_becomes_openwrt_tested(original):
    closed=next(r for r in original['knobs']if r['id']=='xc_8_7_25_iwpriv_ath_vap_ampdu')
    protected=next(r for r in original['knobs']if r['id']=='ct_special_6')
    evidence=[dict(round_id='R93',endpoint='ap',value=4)]
    with pytest.raises(ValueError):audit.classify_control(closed,evidence)
    with pytest.raises(ValueError):audit.classify_control(protected,evidence)
    assert audit.classify_control(closed,[])['status']=='INAPPLICABLE_CLOSED_FIRMWARE_BUILD_TO_OPENWRT_CORPUS'


def test_wmi_retry_and_qdisc_codel_are_not_aliases_for_later_fields(original):
    for key in ('wmi10_1_vdev_rc_num_retries','codel_target','codel_interval'):
        row=next(r for r in original['knobs']if r['id']==key)
        assert audit.evidence_for_control(row,[dict(short_retry_limit=6,fq_target_us=8000)],{}, {})==[]
        assert audit.classify_control(row,[])['status']=='UNTESTED_EXACT_INTERFACE_IN_SAVED_CORPUS'


def test_package_variation_does_not_become_isolated_effect(original):
    knob=next(r for r in original['knobs']if r['id']=='ct_special_7')
    evidence=[dict(round_id='R116',endpoint='ap',value=v)for v in (50,24)]
    classification=audit.classify_control(knob,evidence)
    assert classification['status']=='TESTED_AS_DECLARED_PACKAGE'
    assert classification['isolated_effect_status']=='NO_QUALIFIED_ISOLATED_CAUSAL_EFFECT_ESTABLISHED'
    assert classification['treatment_authorized']is False and classification['approved_safe_range']is None


def test_constant_recorded_value_is_not_a_varied_treatment(original):
    knob=next(r for r in original['knobs']if r['id']=='ct_special_12')
    c=audit.classify_control(knob,[dict(round_id='R3',endpoint='ap',value=0)]*2)
    assert c['status']=='PACKAGE_VALUE_RECORDED_NO_VARIED_TREATMENT'


def test_explicit_unknown_numeric_value_is_not_a_recorded_treatment():
    assert audit.source_coordinate(dict(candidate_knobs=dict(rc_per_thresh=None)),'ap','rc_per_thresh')is None


def test_original_unknown_inventory_stays_unknown_even_when_excluded(original):
    knob=next(k for k in original['knobs']if k['id']=='wa_8_7_25_sys_module_umac_parameters')
    result=audit.classify_control(knob,[])
    assert result['knowledge_status']=='ORIGINAL_INTERFACE_UNKNOWN_OR_UNRESOLVED'
    assert result['treatment_authorized']is False


@pytest.mark.parametrize('knobs',[
    dict(ap_state=dict(rts_threshold=None)),
    dict(ap_rts_threshold=None,cpe_rc_per_thresh=24),
    dict(rts_threshold=None),
    dict(ap_state=dict(rc_per_thresh=24),rts_threshold=None),
])
def test_null_rts_is_unknown_not_recorded_off_in_each_source_schema(knobs):
    assert audit.source_coordinate(dict(candidate_knobs=knobs),'ap','rts_threshold')is None
    explicit_off=deepcopy(knobs)
    if 'ap_state'in explicit_off and 'rts_threshold'in explicit_off['ap_state']:
        explicit_off['ap_state']['rts_threshold']='off'
    elif 'ap_rts_threshold'in explicit_off:explicit_off['ap_rts_threshold']='off'
    else:explicit_off['rts_threshold']='off'
    result=audit.source_coordinate(dict(candidate_knobs=explicit_off),'ap','rts_threshold')
    assert result['value']is None and result['raw_coordinates'][0]['value']=='off'


def test_htt_pair_emits_two_real_normalized_json_coordinates(original):
    knob=next(k for k in original['knobs']if k['id']=='htt_aggr_size')
    arm=dict(commit='candidate',candidate_knobs=dict(ap_state=dict(htt_max_amsdu=3,htt_max_ampdu=64)))
    record=dict(window_kind='primary',round_id='R1',source_position='/iterations/0',iteration='candidate',
        ap_policy=dict(htt_max_amsdu=3,htt_max_ampdu=64),cpe_policy=None,
        workload_regime='bulk_unidirectional',active_flow_count=2)
    evidence=audit.evidence_for_control(knob,[record],{1:dict(iterations=[arm])},{1:dict(path='fixture',sha256='0'*64,bytes=1)})
    assert len(evidence)==1
    coordinates=evidence[0]['normalized_coordinates']
    assert coordinates==[
        dict(pointer='/records/0/ap_policy/htt_max_amsdu',value=3),
        dict(pointer='/records/0/ap_policy/htt_max_ampdu',value=64)]
    for coordinate in coordinates:
        assert audit.pointer_value(dict(records=[record]),coordinate['pointer'])==coordinate['value']
    assert evidence[0]['normalized_transform']=='EXPLICIT_AMSDU_AMPDU_ORDERED_PAIR'
