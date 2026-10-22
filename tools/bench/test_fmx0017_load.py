"""Offline extracted-function tests: never import the device acquisition module."""
import ast
import hashlib
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
import threading
import time
from types import SimpleNamespace

import pytest

SOURCE = Path(__file__).resolve().parents[2] / 'artifacts/canary_panel1_guarida/fmx0017_trial_20261022.py'


@pytest.fixture
def helpers():
    names = {'adaptive_ping_wrapper', '_write_all', 'PingDrain', 'parse_adaptive_ping'}
    nodes = [n for n in ast.parse(SOURCE.read_text()).body
             if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    assert len(nodes) == len(names)
    def require(ok, gate):
        if not ok:
            raise RuntimeError(gate)
    ns = dict(os=os, Path=Path, math=math, re=re, time=time, threading=threading,
              require=require, sha=lambda b: hashlib.sha256(b).hexdigest())
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), ns)
    return SimpleNamespace(**ns)


class Channel:
    def __init__(self, stdout=b'', stderr=b'', end=True):
        self.out, self.err, self.end, self.closed = stdout, stderr, end, False
    def settimeout(self, seconds): pass
    def recv_ready(self): return bool(self.out)
    def recv_stderr_ready(self): return bool(self.err)
    def recv(self, size):
        data, self.out = self.out[:size], self.out[size:]
        return data
    def recv_stderr(self, size):
        data, self.err = self.err[:size], self.err[size:]
        return data
    def exit_status_ready(self): return self.end
    def recv_exit_status(self): return 0
    def close(self): self.closed = True


def test_concurrent_drain_handles_partial_file_writes(helpers, tmp_path, monkeypatch):
    original = os.write
    monkeypatch.setattr(os, 'write', lambda fd, data: original(fd, data[:7]))
    channel = Channel(b'packet\n' * 300, b'diagnostic')
    drain = helpers.PingDrain(channel, tmp_path, 'flow', seconds=1)
    row = drain.finish()
    assert row['error'] is None and row['exit_code'] == 0
    assert drain.paths[0].read_bytes() == b'packet\n' * 300
    assert drain.paths[1].read_bytes() == b'diagnostic'
    assert len(row['files']) == 2 and all('sha256' in f for f in row['files'])


def test_output_cap_closes_channel_and_preserves_failure(helpers, tmp_path):
    channel = Channel(b'x' * 101)
    drain = helpers.PingDrain(channel, tmp_path, 'flow', limit=100, seconds=1)
    row = drain.finish()
    assert 'LOAD_OUTPUT_BOUND' in row['error'] and channel.closed
    assert sum(p.stat().st_size for p in drain.paths) <= 100


def test_drain_timeout_is_bounded(helpers, tmp_path):
    channel = Channel(end=False)
    drain = helpers.PingDrain(channel, tmp_path, 'flow', seconds=.03)
    row = drain.finish()
    assert 'LOAD_DRAIN_TIMEOUT' in row['error'] and channel.closed
    assert not drain.thread.is_alive()


def ping_text(count=6001, received=None, elapsed=60.5, times=None):
    received = count if received is None else received
    times = [float(i % 100 + 1) for i in range(received)] if times is None else times
    return ('__FMX_START__100.00\n' + ''.join('1208 bytes from bench: icmp_seq=%s time=%s ms\n' % (i, v)
        for i, v in enumerate(times)) + '%s packets transmitted, %s packets received, 0%% packet loss\n' % (count, received)
        + '__FMX_END__%s\n' % (100 + elapsed))


def test_nearest_rank_quantile_and_full_minimum(helpers, tmp_path):
    path = tmp_path / 'ping'
    path.write_text(ping_text())
    row = helpers.parse_adaptive_ping(path)
    assert row['pass_parsed'] and row['rtt_samples'] == row['received'] == 6001
    assert row['rtt_ms']['0.95'] == 95
    assert row['ap_elapsed_seconds'] == 60.5


@pytest.mark.parametrize('kwargs', [dict(count=6000), dict(elapsed=59.99),
    dict(received=5900), dict(times=[1] * 6000), dict(times=[1] * 6002),
    dict(times=[float('inf')] + [1] * 6000)])
def test_missing_load_duration_delivery_or_rtts_cannot_accept(helpers, tmp_path, kwargs):
    path = tmp_path / 'ping'; path.write_text(ping_text(**kwargs))
    assert not helpers.parse_adaptive_ping(path)['pass_parsed']


def test_shell_is_bounded_and_pid_start_owned(helpers):
    script = helpers.adaptive_ping_wrapper('ping -A -i 1 -s 1200 -c 200000 -I br-lan bench')
    assert len(script.encode()) < 6000
    assert 'now-start>=60' in script and "ucode -e 'sleep(500)'" in script
    assert "awk '{print $22}'" in script and 'kill -INT "$p"' in script
    assert 'trap cleanup EXIT' in script and "trap '' HUP" in script
    # Syntax only; never execute the script or send ICMP.
    command = (['wsl.exe', '-d', 'Ubuntu', '--exec', 'sh', '-n']
               if os.name == 'nt' else ['sh', '-n'])
    result = subprocess.run(command,
                            input=script.encode(), capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr
