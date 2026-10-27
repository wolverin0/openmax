import copy
import pytest
from tools.observability import build_stage789a_bench_and_tower_rogue_dhcp_audit_ledger as m


def fixture():
    return {'counterbalanced_rounds':[{'round':1,'windows':{k:{'rogue_dhcp_daemon_count':0}for k in ('A1','B1','A2','B2')}}]}


def test_missing_getter_stays_unknown_instead_of_default_healthy():
    r=fixture();r['counterbalanced_rounds'][0]['windows']['B1']={}
    a=m.window_counts(r)
    assert a['windows'][1]['count'] is None and a['windows'][1]['status']=='UNKNOWN_MISSING'
    assert not a['all_saved_counts_zero'] and not a['eradication_proven']


@pytest.mark.parametrize('count',[-1,True,1.5,'0'])
def test_daemon_count_is_nonnegative_exact_integer(count):
    r=fixture();r['counterbalanced_rounds'][0]['windows']['A1']['rogue_dhcp_daemon_count']=count
    with pytest.raises(ValueError):m.window_counts(r)


def test_nonzero_count_is_not_zero_and_zero_is_not_eradication():
    r=fixture();r['counterbalanced_rounds'][0]['windows']['A1']['rogue_dhcp_daemon_count']=2
    assert not m.window_counts(r)['all_saved_counts_zero']
    a=m.window_counts(fixture());assert a['all_saved_counts_zero'] and not a['eradication_proven']


def test_duplicate_round_or_missing_window_rejected():
    r=fixture();r['counterbalanced_rounds']*=2
    with pytest.raises(ValueError):m.window_counts(r)
    r=fixture();r['counterbalanced_rounds'][0]['windows'].pop('A2')
    with pytest.raises(ValueError):m.window_counts(r)


def test_static_uci_requirements_do_not_supply_defaults():
    assert all(x['declared_match']for x in m.declarations(m.REQUIRED).values())
    assert not any(x['declared_match']for x in m.declarations({}).values())
    assert not m.declarations({'dhcp_lan_ignore':True})['dhcp_lan_ignore']['declared_match']
    with pytest.raises(ValueError):m.declarations([])


def test_ast_extract_never_executes_code_or_dynamic_expression():
    text='raise RuntimeError("must not execute")\ndef build_helper_script():\n return "literal"\n'
    assert m.literal(text,'build_helper_script',True)=='literal'
    with pytest.raises(ValueError):m.literal('X = dangerous_call()','X')


@pytest.mark.parametrize('text,function',[("X='helper'\nX=dynamic_call()",False),
    ("X='helper'\nX: str='other'",False),("X='helper'\nX+='other'",False),
    ("def X():\n return 'helper'\ndef X():\n return 'other'",True),
    ("def X():\n if flag:return 'other'\n return 'helper'",True)])
def test_ambiguous_binding_or_function_control_flow_is_rejected(text,function):
    with pytest.raises(ValueError):m.literal(text,'X',function)


def test_current_ledger_retains_unknown_and_unsafe_health_markers():
    r=m.h.json_source(m.h.snapshot(m.ROOT,m.OUT)[0])
    assert r['eradication_verdict']=='UNKNOWN_NOT_PROVEN'
    assert r['saved_windows']['count']==12 and not r['saved_windows']['eradication_proven']
    assert r['producer_risks']['loopback_probe'] and r['producer_risks']['count_can_default_zero']
    assert r['scopes'][0]['static_patterns']['literal_healthy_echo']
    assert r['scopes'][1]['static_patterns']['status_healthy_fallback']
    assert all(x['runtime_applied']==x['persistence']=='UNKNOWN'for x in r['scopes'])
    assert not any(r['boundary'].values())
    for p in [r['implementation'],*r['analysis_dependencies'],r['outputs'][m.DOC]]:assert m.h.snapshot(m.ROOT,p['path'])[1]==p
    for s in r['static_sources']:assert m.h.snapshot(m.ROOT,s['frozen']['path'])[1]==s['frozen']
