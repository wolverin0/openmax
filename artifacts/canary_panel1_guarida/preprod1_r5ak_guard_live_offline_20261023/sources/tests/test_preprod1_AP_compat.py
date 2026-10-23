"""Disposable host shell/mock-channel checks. Never connects to a radio."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'artifacts/canary_panel1_guarida/preprod1_AP_compat_20261023.py'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return load(PATH, 'compat_fixture')


def helper():
    # Existing module has only definitions/constants and local nonce generation.
    module = load(ROOT / 'artifacts/canary_panel1_guarida/root_four_cpe_ap_window_20261022.py', 'ap_fixture')
    original_guard = module.guard_body
    module.guard_body = lambda: original_guard().replace('+480)', '+1200)')
    module.off = lambda ap: dict(status='OFF')
    module.client_pin = lambda ap: None
    module.guard_identity = lambda ap: [12, 34, 1200]
    return module


def instance(mod, tmp_path, monkeypatch, rpc=None):
    payload = b'fixture-code'
    monkeypatch.setattr(mod, 'COMPAT_SHA', mod.sha(payload))
    monkeypatch.setattr(mod, 'COMPAT_BYTES', len(payload))
    binary = tmp_path / 'input'
    binary.write_bytes(payload)
    return mod.Compat(helper(), tmp_path / 'out', rpc or (lambda *a, **k: b''), binary)


def test_same_guard_hook_and_command_budget(mod, tmp_path, monkeypatch):
    value = instance(mod, tmp_path, monkeypatch)
    restore = value.helper.restore_body()
    normal = restore[restore.index('fi\nwifi down radio0'):]
    assert normal.index('wifi down radio0') < normal.index('compat_stop\n') < normal.index(': > "$D/restored"')
    assert value.record['prepare_command_bytes'] <= 4096
    assert '+1200)' in value.original_prepare()
    assert not value.prepared and not value.created
    assert value.cleanup_names == ['wpad.compat', 'compat.intent', 'compat.mount.id', 'compat.restored']
    assert 'killall' not in restore and 'umount -' not in restore
    assert '/proc/$p/task/' not in restore


class Channel:
    def __init__(self, mode='ok'):
        self.mode, self.sent, self.closed, self.done = mode, bytearray(), False, False

    def settimeout(self, timeout):
        assert 0 < timeout <= 20

    def exec_command(self, command):
        self.command = command

    def send(self, data):
        if self.mode == 'zero':
            return 0
        n = min(3, len(data))
        self.sent.extend(data[:n])
        return n

    def shutdown_write(self):
        self.done = True

    def recv_ready(self):
        return self.done

    def recv(self, size):
        self.done = False
        return b'x' * 4097 if self.mode == 'overflow' else b'COMPAT_UPLOAD_VERIFIED\n'

    def recv_stderr_ready(self):
        return False

    def exit_status_ready(self):
        return not self.done

    def recv_exit_status(self):
        return 0

    def close(self):
        self.closed = True


def client(channel):
    def session(timeout):
        assert 0 < timeout <= 20
        return channel
    return SimpleNamespace(get_transport=lambda: SimpleNamespace(open_session=session))


def test_partial_send_full_payload_and_close(mod, tmp_path, monkeypatch):
    value = instance(mod, tmp_path, monkeypatch)
    channel = Channel()
    value.stage(client(channel))
    assert bytes(channel.sent) == value.binary
    assert channel.closed and value.record['upload_verified']
    assert channel.command.index('sha256sum') < channel.command.index('chmod 0755')


@pytest.mark.parametrize('mode,gate', [('zero', 'SHORT_SEND'), ('overflow', 'OUTPUT_BOUND')])
def test_failed_transfer_retains_uncertain_evidence(mod, tmp_path, monkeypatch, mode, gate):
    value = instance(mod, tmp_path, monkeypatch)
    channel = Channel(mode)
    with pytest.raises(RuntimeError, match=gate):
        value.stage(client(channel))
    assert channel.closed and value.record['upload_intent']
    assert not value.record.get('upload_verified')


def test_upload_absolute_deadline_closes_channel(mod, tmp_path, monkeypatch):
    value = instance(mod, tmp_path, monkeypatch)
    channel = Channel()
    clock = iter(range(0, 100, 5))
    monkeypatch.setattr(mod.time, 'monotonic', lambda: next(clock))
    with pytest.raises(RuntimeError, match='DEADLINE'):
        value.stage(client(channel))
    assert channel.closed and not value.record.get('upload_verified')


def test_exec_ack_is_bounded_by_independent_owned_channel_timer(mod, tmp_path, monkeypatch):
    value = instance(mod, tmp_path, monkeypatch)
    monkeypatch.setattr(mod, 'STREAM_SECONDS', .03)
    class AckWait(Channel):
        def exec_command(self, command):
            self.command = command
            fallback = time.monotonic() + .3
            while not self.closed and time.monotonic() < fallback:
                time.sleep(.001)
            assert self.closed, 'EXEC_ACK_NOT_BOUNDED'
    channel = AckWait()
    with pytest.raises(RuntimeError, match='DEADLINE'):
        value.stage(client(channel))
    assert channel.closed and not value.record.get('upload_verified')


def test_activation_failure_has_creation_intent_and_durable_failure(mod, tmp_path, monkeypatch):
    calls = []
    def rpc(ap, command, timeout=25):
        calls.append(command)
        if 'compat.activate' in command:
            return dict(exit_code=1, stdout='', stderr='fixture failed start')
        return b''
    value = instance(mod, tmp_path, monkeypatch, rpc)
    original = value.helper.prepare
    monkeypatch.setattr(value, 'stage', lambda ap: None)
    with pytest.raises(RuntimeError, match='RPC_FAILED'):
        value.prepare_and_activate(None)
    assert value.prepared and value.created and not value.activated
    assert value.helper.prepare is original
    receipt = json.loads((value.out / 'receipt.json').read_text())
    assert receipt['status'] == 'INCOMPLETE_COMPAT_LIFECYCLE' and receipt['errors']
    assert all(len(command.encode()) <= 4096 for command in calls)
    activation = value.mode_body('activate')
    assert activation.index('> "$D/compat.intent"') < activation.index('compat_stop\n') < activation.index('mount -o bind')


def shell(source, syntax=False):
    executable = Path('C:/Program Files/Git/bin/sh.exe')
    if not executable.is_file():
        pytest.skip('Existing Git POSIX shell unavailable')
    # WSL launches timed out in separately preserved runs, at varying fixtures.
    # No shared service repair: use the already installed local POSIX shell.
    with tempfile.TemporaryDirectory(prefix='fmx-compat-shell-') as directory:
        path = Path(directory) / 'fixture.sh'
        path.write_bytes(source.encode())
        run = subprocess.run([str(executable)] + (['-n'] if syntax else []) + [path.as_posix()],
                             capture_output=True, timeout=20)
    return SimpleNamespace(returncode=run.returncode, stdout=run.stdout.decode(), stderr=run.stderr.decode())


def test_all_rendered_shell_syntax(mod, tmp_path, monkeypatch):
    value = instance(mod, tmp_path, monkeypatch)
    script = value.original_prepare()
    run = shell(script, syntax=True)
    assert run.returncode == 0, run.stderr


@pytest.mark.parametrize('state,expected_rc', [('S', 0), ('Z', 91), ('wrong_start', 91),
                                            ('wrong_argv', 91), ('wrong_sha', 91), ('zero_id', 91)])
def test_guard_died_during_stage_rejects_before_intent(mod, tmp_path, monkeypatch, state, expected_rc):
    value = instance(mod, tmp_path, monkeypatch)
    # Run the actual activation mode against a disposable proc fixture. All
    # service/mount operations are recording stubs, never native commands.
    setup = r'''set -eu
D=$(mktemp -d /tmp/fmx-compat-fixture-XXXXXX)
trap 'rm -rf "$D"' EXIT
TOKEN=fixture
mkdir -p "$D/proc/123"
printf '100.00 0.00\n' > "$D/proc/uptime"
printf '123 777\n' > "$D/guard.id"
printf '1200\n' > "$D/deadline"
touch "$D/ready" "$D/log"
printf '/bin/sh\000%s/guard.sh\000' "$D" > "$D/proc/123/cmdline"
COMPAT_GUARD_PID=123
COMPAT_GUARD_START=777
compat_surface() { :; }
compat_nomount() { :; }
compat_file() { :; }
compat_roles() { compat_ready=1; }
compat_stop() { echo stop >> "$D/log"; }
compat_ownedmount() { mount_id=1; }
compat_start() { :; }
compat_time() { :; }
mount() { echo mount >> "$D/log"; }
'''
    fields = ['123', '(guard)', state if state in ('S', 'Z') else 'S'] + ['0'] * 18 + [
        '778' if state == 'wrong_start' else '777']
    setup += "printf '%s\\n' '" + ' '.join(fields) + "' > \"$D/proc/123/stat\"\n"
    setup += "printf '%s' " + mod.shlex.quote(value.helper.guard_body()) + ' > "$D/guard.sh"\n'
    if state == 'wrong_argv':
        setup += 'printf "/bin/sh\\000/foreign/guard.sh\\000" > "$D/proc/123/cmdline"\n'
    if state == 'wrong_sha':
        setup += 'printf "#foreign\\n" >> "$D/guard.sh"\n'
    if state == 'zero_id':
        setup += 'COMPAT_GUARD_PID=0\n'
    body = value.mode_body('activate').replace('/proc/', '$D/proc/')
    source = setup + 'set +e\n( set -e\n' + body + '\n); rc=$?\nset -e\n'
    source += 'test "$rc" = ' + str(expected_rc) + '\n'
    if expected_rc:
        source += 'test ! -e "$D/compat.intent"\ntest ! -s "$D/log"\n'
    else:
        source += 'test -f "$D/compat.intent"\ntest "$(cat "$D/log")" = "stop\nmount"\n'
    run = shell(source)
    assert run.returncode == 0, (run.stdout, run.stderr)


@pytest.mark.parametrize('intent,mounted,fail_start', [(False, False, False), (True, False, False),
                                                     (True, True, False), (True, True, True)])
def test_real_restore_partial_lifecycle(mod, intent, mounted, fail_start):
    # Execute the actual restoration control flow, replacing only OS operations
    # with recording stubs and a disposable mount table. No service/device call.
    setup = r'''set -eu
D=$(mktemp -d /tmp/fmx-compat-fixture-XXXXXX)
case "$D" in /tmp/fmx-compat-fixture-*) ;; *) exit 1;; esac
trap 'rm -rf "$D"' EXIT
TOKEN=fixture
touch "$D/mountinfo" "$D/log"
compat_surface() { echo surface >> "$D/log"; }
compat_nomount() { test ! -s "$D/mountinfo"; }
compat_file() { :; }
compat_ownedmount() { echo owned >> "$D/log"; }
compat_roles() { compat_ready=1; echo roles >> "$D/log"; }
compat_stop() { echo stop >> "$D/log"; }
compat_start() { echo start >> "$D/log"; FAIL_START; }
sha256sum() { printf '%s  fixture\n' 'STOCK_SHA'; }
ls() { echo '-rw------- 1 0 0 8 fixture'; }
umount() { echo unmount >> "$D/log"; : > "$D/mountinfo"; }
'''.replace('STOCK_SHA', mod.STOCK_SHA).replace('FAIL_START', 'return 1' if fail_start else ':')
    if intent:
        setup += 'printf "%s\\n" "$TOKEN" > "$D/compat.intent"\n'
    if mounted:
        setup += 'echo "10 2 0:1 /fixture /usr/sbin/wpad rw - tmpfs tmpfs rw" > "$D/mountinfo"\n'
    body = mod.restoration()[len(mod.functions()):].replace('/proc/self/mountinfo', '"$D/mountinfo"')
    # Subshell preserves the failed path so the fixture can inspect its markers.
    source = setup + 'set +e\n( set -e\n' + body + '\n); rc=$?\nset -e\ncat "$D/log"\n'
    source += 'test "$rc" = ' + ('1' if fail_start else '0') + '\n'
    source += ('test ! -e "$D/compat.restored"\n' if fail_start or not intent else 'test "$(cat "$D/compat.restored")" = "$TOKEN"\n')
    run = shell(source)
    assert run.returncode == 0, (run.stdout, run.stderr)
    lines = run.stdout.splitlines()
    assert ('stop' in lines) == intent and ('start' in lines) == intent
    assert ('unmount' in lines) == mounted
    if mounted:
        assert lines.index('owned') < lines.index('unmount') < lines.index('start')


@pytest.mark.parametrize('foreign_root,saved_id,owner', [(False, False, 0), (False, True, 0),
                                                       (True, False, 0), (False, False, 1)])
def test_real_mount_ownership_requires_root_inode_device_id(mod, foreign_root, saved_id, owner):
    source = r'''set -eu
D=$(mktemp -d /tmp/fmx-compat-fixture-XXXXXX)
case "$D" in /tmp/fmx-compat-fixture-*) ;; *) exit 1;; esac
trap 'rm -rf "$D"' EXIT
printf fixture > "$D/wpad.compat"
chmod 755 "$D/wpad.compat"
ln "$D/wpad.compat" "$D/target"
printf '5 1 0:99 / /tmp rw - tmpfs tmpfs rw\n7 5 0:99 ROOT /usr/sbin/wpad rw - tmpfs tmpfs rw\n' > "$D/mountinfo"
ls() {
 if test "$2" = /usr/sbin/wpad; then set -- "$1" "$D/target"; fi
 case "$1" in *i*) /bin/ls "$@";; *)
  if test "$2" = "$D/compat.mount.id"; then printf '%s\n' '-rw------- 1 OWNER 0 2 fixture'
  else printf '%s\n' '-rwxr-xr-x 1 OWNER 0 7 fixture'; fi
 ;; esac
}
sha256sum() {
 if test "$1" = /usr/sbin/wpad; then /usr/bin/sha256sum "$D/target"; else /usr/bin/sha256sum "$@"; fi
}
'''.replace('OWNER', str(owner))
    source += 'sed -i "s|ROOT|' + ('/foreign' if foreign_root else '${D#/tmp}/wpad.compat') + '|" "$D/mountinfo"\n'
    if saved_id:
        source += 'echo 8 > "$D/compat.mount.id"\nchmod 600 "$D/compat.mount.id"\n'
    functions = mod.functions().replace('/proc/self/mountinfo', '"$D/mountinfo"')
    functions = functions.replace(mod.COMPAT_SHA, mod.sha(b'fixture')).replace(str(mod.COMPAT_BYTES), '7')
    run = shell(source + functions + '\ncompat_ownedmount\n')
    expected = 93 if owner else 94 if foreign_root or saved_id else 0
    assert run.returncode == expected, (run.stdout, run.stderr)


def test_extra_procd_instance_is_rejected_before_any_stop(mod):
    source = 'set -eu\n' + mod.functions() + r'''
ubus() { echo '{"wpad":{"instances":{}}}'; }
jsonfilter() {
 case "$*" in *'instances.hostapd.pid'*) echo 101;; *'instances.supplicant.pid'*) echo 102;; *'instances[*].pid'*) printf '101\n102\n999\n';; *) echo '{}';; esac
}
wanted=
compat_roles
echo UNSAFE_REACHED
'''
    run = shell(source)
    assert run.returncode == 95 and 'UNSAFE_REACHED' not in run.stdout
