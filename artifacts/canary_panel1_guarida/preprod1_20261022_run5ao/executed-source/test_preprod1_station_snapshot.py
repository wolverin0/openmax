"""Station retirement must not conceal a peer loss or an unknown iw failure."""
import ast
from pathlib import Path
import re

import pytest


SOURCE = Path(__file__).resolve().parents[1] / 'artifacts/canary_panel1_guarida/preprod1_trial_20261022.py'
BASE = 'phy0-ap0'
CHILD = BASE + '.sta2'
XC = 'b4:fb:e4:5c:d5:d2'
WA = 'fc:ec:da:c2:54:0a'
SXT = '64:d1:54:1b:96:97'


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def snapshot_fixture(*, state='ABSENT\n', target=XC, dump_code=237,
                     dump_error='command failed: No such device (-19)\n',
                     probe_code=0, recovered=False, station_fields='',
                     clock='\n__FMX_AP_UPTIME__200.10\n', omit_required=False):
    node = next(n for n in ast.walk(ast.parse(SOURCE.read_text(encoding='utf8')))
                if isinstance(n, ast.FunctionDef) and n.name == 'station_snapshot')
    actions = (f'1 OLD_WDS_BIND n=2 target={target} child={CHILD} ifindex=100\n'
               f'2 DROP_REQUEST n=2 target={target} reason=3 deauth=true ban_time=0\n'
               f'3 DROP_OBSERVED n=2 target={target}\n')
    if recovered:
        actions += f'4 RECOVERED n=2 target={target}\n'
    calls = []
    record = {}

    def remote(_ap, command, check=True, **_kwargs):
        calls.append(command)
        code, out, err = 0, '', ''
        if command == 'iw dev':
            out = f'\tInterface {BASE}\n\tInterface {CHILD}\n'
        elif command.startswith(f'iw dev {BASE} station dump && '):
            out = (f'Station {SXT} (on {BASE})\n'
                   '\tconnected time: 90 seconds\n\trx bytes: 400\n'
                   + ('' if omit_required else '\ttx bytes: 600\n') + station_fields + clock)
        elif command.startswith(f'iw dev {CHILD} station dump && '):
            code, err = dump_code, dump_error
        elif command == 'cat /tmp/fmx-native/actions.log':
            out = actions
        elif '/sys/class/net/' + CHILD in command:
            code, out = probe_code, state
        else:
            raise AssertionError('Unexpected RPC: ' + command)
        require(not check or code == 0, 'REMOTE_EXIT_' + str(code) + '_' + err)
        require(not check or not err, 'REMOTE_STDERR_' + err)
        return dict(exit_code=code, stdout=out, stderr=err)

    env = dict(remote=remote, ap=object(), interface=BASE, re=re, MACS={XC, WA, SXT},
               require=require, rec=record, daemon_dir='/tmp/fmx-native', XC=XC, WA=WA)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), 'exec'), env)
    return env['station_snapshot'], record, calls


@pytest.mark.parametrize('state', ['ABSENT\n', 'INDEX 101\n'])
def test_expected_xc_old_wds_retirement_does_not_abort_snapshot(state):
    collect, record, _calls = snapshot_fixture(state=state)
    rows, raw = collect()
    assert set(rows) == {SXT}
    assert rows[SXT]['rx_bytes'] == 400
    assert raw[CHILD] == ''
    evidence = record['station_retirement_observations']
    assert len(evidence) == 1
    assert evidence[0]['target'] == XC
    assert evidence[0]['old_ifindex'] == 100


@pytest.mark.parametrize('options', [
    {'target': SXT},
    {'dump_code': 1},
    {'dump_error': 'netlink receive failed\n'},
    {'state': 'INDEX 100\n'},
    {'state': 'INDEX 0\n'},
    {'state': 'INDEX 101\ntrailing\n'},
    {'probe_code': 88},
    {'recovered': True},
    pytest.param({'dump_code': 0, 'dump_error': 'netlink warning\n'}, id='success_with_stderr'),
])
def test_unknown_or_unproven_interface_failure_still_fails_closed(options):
    collect, record, _calls = snapshot_fixture(**options)
    with pytest.raises(RuntimeError):
        collect()
    assert not record.get('station_retirement_observations')


COUNTERS = ['tx_failed', 'tx_retries', 'rx_drop_misc', 'rx_packets', 'tx_packets']


def test_delivery_counters_use_existing_rpc_and_ap_clock():
    fields = ('\ttx failed: 2\n\ttx retries: 7\n\trx drop misc: 3\n'
              '\trx packets: 91\n\ttx packets: 88\n')
    collect, _record, calls = snapshot_fixture(station_fields=fields)
    rows, _raw = collect()
    assert [rows[SXT][k] for k in COUNTERS] == [2, 7, 3, 91, 88]
    assert rows[SXT]['observed_AP_uptime_s'] == 200.10
    assert sum(c.startswith('iw dev ' + BASE + ' station dump') for c in calls) == 1
    assert sum('/proc/uptime' in c for c in calls) == 2  # same two dump calls
    assert all(' && ' in c for c in calls if '/proc/uptime' in c)


def test_unsupported_delivery_counters_stay_null_and_real_zero_is_preserved():
    collect, _record, _calls = snapshot_fixture(station_fields='\ttx failed: 0\n')
    rows, _raw = collect()
    assert rows[SXT]['tx_failed'] == 0
    assert all(rows[SXT][k] is None for k in COUNTERS if k != 'tx_failed')


@pytest.mark.parametrize('clock', ['', '\n__FMX_AP_UPTIME__nan\n',
                                  '\n__FMX_AP_UPTIME__200.10\n__FMX_AP_UPTIME__200.11\n',
                                  '\n__FMX_AP_UPTIME__200.10garbage\n'])
def test_unbound_or_ambiguous_ap_clock_fails_closed(clock):
    collect, _record, _calls = snapshot_fixture(clock=clock)
    with pytest.raises(RuntimeError, match='STATION_SNAPSHOT_AP_CLOCK_INVALID'):
        collect()


def test_optional_diagnostics_do_not_replace_required_session_counters():
    collect, _record, _calls = snapshot_fixture(omit_required=True,
                                               station_fields='\ttx failed: 0\n')
    with pytest.raises(RuntimeError, match='STATION_COUNTER_MISSING'):
        collect()
