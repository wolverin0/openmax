"""Fixed offered-load phases must preserve every original packet qualification."""
import ast
import math
from pathlib import Path
import re
import time

import pytest


SOURCE = Path(__file__).resolve().parents[1] / 'artifacts/canary_panel1_guarida/preprod1_trial_20261022.py'
MACS = ['wa', 'xc', 'sxt', 'm5']
LABELS = dict(zip(MACS, ['WA', 'XC', 'SXT', 'LBM5']))


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def actual_function(name):
    node = next(n for n in ast.walk(ast.parse(SOURCE.read_text(encoding='utf8')))
                if isinstance(n, ast.FunctionDef) and n.name == name)
    env = dict(require=require, MACS=MACS, LABELS=LABELS, time=time, math=math, re=re)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), 'exec'), env)
    return env[name]


class Clock:
    def __init__(self):
        self.value = 500.0
        self.waits = []

    def now(self):
        return self.value

    def pause(self, seconds):
        self.waits.append(seconds)
        self.value += seconds


def test_actual_launcher_uses_fixed_phases_without_extra_packets_or_collapsed_starts():
    clock = Clock()
    launched = []

    def launch(item):
        launched.append((item[0], clock.now()))
        clock.value += .03  # finite exec acknowledgement cost
        return item

    captures = [(m, 'unchanged-command-and-capture') for m in MACS]
    paths, timing = actual_function('phased_echo_launch')(
        captures, launch, 550, now=clock.now, pause=clock.pause)
    assert paths == captures and [m for m, _ in launched] == MACS
    assert [t - 500 for _, t in launched] == [0, .25, .5, .75]
    assert 0 <= sum(clock.waits) <= .75
    assert [timing['peers'][LABELS[m]]['planned_offset_s'] for m in MACS] == [0, .25, .5, .75]


def test_insufficient_capture_budget_fails_before_any_launch():
    clock = Clock()
    launched = []
    with pytest.raises(RuntimeError, match='PHASED_CAPTURE_BUDGET_INSUFFICIENT'):
        actual_function('phased_echo_launch')([(m,) for m in MACS], launched.append,
                                             533, now=clock.now, pause=clock.pause)
    assert not launched and not clock.waits


def test_late_acknowledgement_aborts_instead_of_collapsing_remaining_phases():
    clock = Clock()
    launched = []

    def launch(item):
        launched.append(item)
        clock.value += .4

    with pytest.raises(RuntimeError, match='PHASED_LAUNCH_CLOCK_OR_LATENESS_INVALID'):
        actual_function('phased_echo_launch')([(m,) for m in MACS], launch,
                                             550, now=clock.now, pause=clock.pause)
    assert len(launched) == 1


def test_target_order_is_fixed_before_any_launch():
    launched = []
    with pytest.raises(RuntimeError, match='PHASED_TARGET_ORDER_INVALID'):
        actual_function('phased_echo_launch')([(m,) for m in reversed(MACS)],
                                             launched.append, 550)
    assert not launched


@pytest.mark.parametrize('origin,deadline', [(math.nan, 550), (500, math.inf)])
def test_invalid_clock_does_not_launch(origin, deadline):
    launched = []
    with pytest.raises(RuntimeError, match='PHASED_CLOCK_INVALID'):
        actual_function('phased_echo_launch')([(m,) for m in MACS], launched.append,
                                             deadline, now=lambda: origin)
    assert not launched


@pytest.mark.parametrize('missing', [None, 16])
def test_capture_timestamps_do_not_rescue_a_missing_echo_or_radio_pair(missing):
    ping = b''.join(f'seq={i} time=1.0 ms\n'.encode() for i in range(32) if i != missing)
    ping += f'32 packets transmitted, {32 - (missing is not None)} packets received\n'.encode()
    capture = b''
    for i in range(32):
        capture += f'{100 + i}.000 IP a > b: ICMP echo request, id 1, seq {i}, length 64\n'.encode()
        if i != missing:
            capture += f'{100 + i}.001 IP b > a: ICMP echo reply, id 1, seq {i}, length 64\n'.encode()
    result = actual_function('stream_quality')(ping, b'', 0, capture, b'', 0, 'XC')
    assert (result['first_request_capture_wall_s'], result['last_request_capture_wall_s']) == (100, 131)
    assert result['transmitted'] == 32
    assert result['received'] == result['paired'] == 32 - (missing is not None)
    assert result['qualifying'] is (missing is None)
    if missing is not None:
        assert result['failures'] == ['QUALIFY_ECHO_FAILED_XC', 'QUALIFY_RADIO_PAIRS_FAILED_XC']
