"""Disposable SSH fixtures for the observed pre-window EXEC-ACK hang."""
import ast
from pathlib import Path
from types import SimpleNamespace
import threading
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'artifacts/canary_panel1_guarida/preprod1_trial_20261022.py'
ACCESS = RUNNER.with_name('root_four_cpe_access_20261022.py')


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def load_remote():
    tree = ast.parse(RUNNER.read_text(encoding='utf8'))
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'remote']
    if not functions:
        functions = [n for n in ast.parse(ACCESS.read_text(encoding='utf8')).body
                     if isinstance(n, ast.FunctionDef) and n.name == 'remote']
    namespace = dict(threading=threading, time=time, require=require)
    exec(compile(ast.Module(body=functions, type_ignores=[]), '<remote-only>', 'exec'), namespace)
    return namespace['remote']


class Channel:
    def __init__(self):
        self.closed = threading.Event()
        self.out, self.err = [], []
        self.commands = []

    def close(self):
        self.closed.set()

    def settimeout(self, timeout):
        pass

    def exec_command(self, command):
        self.commands.append(command)

    def shutdown_write(self):
        pass

    def recv_ready(self):
        return bool(self.out)

    def recv_stderr_ready(self):
        return bool(self.err)

    def recv(self, limit):
        return self.out.pop(0)

    def recv_stderr(self, limit):
        return self.err.pop(0)

    def exit_status_ready(self):
        return not self.out and not self.err

    def recv_exit_status(self):
        return 0


def fixture(channel):
    opened = []
    def open_session(timeout):
        opened.append(timeout)
        return channel
    transport = SimpleNamespace(open_session=open_session)
    def old_high_level(command, timeout):
        # Model Paramiko's unbounded ACK, with an external test-only bailout.
        channel.closed.wait(.15)
        raise EOFError('external test bailout; old helper did not close its channel')
    return SimpleNamespace(get_transport=lambda: transport, exec_command=old_high_level), opened


def test_stalled_exec_ack_is_closed_by_its_own_absolute_deadline():
    channel = Channel()
    def blocked(command):
        channel.commands.append(command)
        assert channel.closed.wait(.15)
        raise EOFError('owned channel closed')
    channel.exec_command = blocked
    client, opened = fixture(channel)
    start = time.monotonic()
    with pytest.raises(RuntimeError, match='REMOTE_ABSOLUTE_DEADLINE'):
        load_remote()(client, 'read-only-fixture', timeout=.04)
    assert time.monotonic()-start < .12
    assert channel.closed.is_set() and opened == [.04]


def test_stdout_and_stderr_are_both_drained_with_exact_bounds():
    channel = Channel()
    channel.out, channel.err = [b'ok\n'], [b'diagnostic\n']
    client, _ = fixture(channel)
    result = load_remote()(client, 'fixture', timeout=.2, check=False)
    assert result == dict(exit_code=0, stdout='ok\n', stderr='diagnostic\n')
    assert channel.closed.is_set()


def test_audit_rejection_prevents_even_opening_the_channel():
    channel = Channel()
    client, opened = fixture(channel)
    def rejected(command):
        raise RuntimeError('FORBIDDEN_XC_EXEC_DURING_ZERO_TOUCH_WINDOW')
    client.record_command = rejected
    with pytest.raises(RuntimeError, match='FORBIDDEN_XC_EXEC_DURING_ZERO_TOUCH_WINDOW'):
        load_remote()(client, 'fixture', timeout=.04)
    assert opened == [] and channel.commands == []


def test_output_overflow_closes_only_the_owned_channel():
    channel = Channel()
    channel.out = [b'12345']
    client, _ = fixture(channel)
    with pytest.raises(RuntimeError, match='OUTPUT_BOUND'):
        load_remote()(client, 'fixture', timeout=.2, limit=4)
    assert channel.closed.is_set()
