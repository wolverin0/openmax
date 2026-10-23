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
                     probe_code=0, recovered=False):
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
        elif command == f'iw dev {BASE} station dump':
            out = (f'Station {SXT} (on {BASE})\n'
                   '\tconnected time: 90 seconds\n\trx bytes: 400\n\ttx bytes: 600\n')
        elif command == f'iw dev {CHILD} station dump':
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
