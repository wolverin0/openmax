"""Disposable SSH fixtures for the observed pre-window EXEC-ACK hang."""
import ast
from pathlib import Path
from types import SimpleNamespace
import threading
import time
import hashlib
import secrets
import shlex

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


def test_legacy_guard_readiness_does_not_require_a_second_rpc_after_transition():
    tree = ast.parse(RUNNER.read_text(encoding='utf8'))
    arm = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name=='arm_legacy')
    factory = ast.parse('def factory():\n legacy_end=None\n').body[0]
    factory.body.extend([arm, ast.Return(value=ast.Name(id='arm_legacy',ctx=ast.Load()))])
    module = ast.fix_missing_locations(ast.Module(body=[factory],type_ignores=[]))
    rec, calls = dict(legacy_guards={}), []
    def remote(client, command, **kwargs):
        assert rec['legacy_guards']['LBM5']['intent_recorded']
        calls.append(command)
        if len(calls)>1:
            raise EOFError('RF transition prevents a second EXEC-ACK')
        return dict(exit_code=0,stdout='123 456 900\n',stderr='')
    namespace=dict(time=time,hashlib=hashlib,secrets=secrets,shlex=shlex,
        sha=lambda b:hashlib.sha256(b).hexdigest(),require=require,remote=remote,
        intake=dict(devices=dict(LBM5=dict(system_md5='a'*32))),rec=rec,
        legacy_program=lambda *args:'#!/bin/sh\n',save=lambda:None)
    exec(compile(module,'<legacy-arm-only>','exec'),namespace)
    namespace['factory']()('LBM5',object())
    assert len(calls)==1 and rec['legacy_guards']['LBM5']['pid']==123
    assert 'guard.id' in calls[0] and 'deadline' in calls[0]


def m5_function(name):
    source=RUNNER.with_name('preprod1_r5aa_M5_recovery_window_20261022.py')
    fn=next(n for n in ast.parse(source.read_text(encoding='utf8')).body
            if isinstance(n,ast.FunctionDef) and n.name==name)
    import re
    namespace=dict(threading=threading,time=time,SimpleNamespace=SimpleNamespace,re=re,hashlib=hashlib)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'<m5-recovery-only>','exec'),namespace)
    return namespace[name]


@pytest.mark.parametrize('raw',['','123','0 456','123 0','-1 2','1 2 3','1 x','1;false 2'])
def test_m5_guard_identity_cannot_turn_malformed_input_into_ended(raw):
    with pytest.raises(RuntimeError,match='M5_GUARD_ID_PROTOCOL'):
        m5_function('guard_identity')(raw)


def test_m5_guard_identity_accepts_exact_positive_pid_and_start():
    assert m5_function('guard_identity')('123 456\n')==['123','456']


@pytest.mark.parametrize('late_success',[False,True])
def test_m5_connect_deadline_closes_only_new_socket_and_rejects_late_client(late_success):
    channel=Channel()
    ap_closes=[]
    transport=SimpleNamespace(open_channel=lambda *args,**kwargs:channel,
                              close=lambda:ap_closes.append('AP_TRANSPORT_CLOSED'))
    client_closes=[]
    client=SimpleNamespace(close=lambda:client_closes.append('CLOSED'))
    def connect(proxy,name,pin,**kwargs):
        proxy.get_transport().open_channel('direct-tcpip',('fixture',22),('fixture',0),timeout=8)
        assert channel.closed.wait(.2)
        if late_success:
            return client,pin
        raise EOFError('socket closed during banner/auth/identity')
    access=SimpleNamespace(require=require,connect_legacy=connect)
    started=time.monotonic()
    with pytest.raises(RuntimeError,match='M5_CONNECT_DEADLINE'):
        m5_function('connect_before_deadline')(access,SimpleNamespace(get_transport=lambda:transport),
                                               'fixture-pin',started+.04)
    assert time.monotonic()-started<.15 and channel.closed.is_set() and not ap_closes
    assert client_closes==(['CLOSED'] if late_success else [])


@pytest.mark.parametrize('mutation',['same','changed','missing_newline','oversized'])
def test_m5_local_sha256_binds_native_md5_to_the_exact_original_guard(mutation):
    original=b'#!/bin/sh\necho fixture\n'
    body={'same':original,'changed':original.replace(b'fixture',b'changed'),
          'missing_newline':original.rstrip(b'\n'),'oversized':b'x'*8193}[mutation]
    expected=hashlib.sha256(original if mutation!='oversized' else body).hexdigest()
    if mutation=='same':
        assert m5_function('guard_native_md5')(body.decode('ascii'),expected)==hashlib.md5(original).hexdigest()
    else:
        with pytest.raises(RuntimeError,match='M5_GUARD_LOCAL_SHA256_MISMATCH'):
            m5_function('guard_native_md5')(body.decode('ascii'),expected)
