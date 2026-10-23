"""Native retirement observation with disposable sysfs and recording stubs.

Never reads real /sys, starts a service, sends RF or connects to a device.
"""
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'tools/bench/preprod1_admitter.sh'


def source_functions():
    source = NATIVE.read_text(encoding='utf8')
    function = 'old_wds_retired() {' + source.split('old_wds_retired() {', 1)[1].split('\npulse_missing()', 1)[0]
    return source, function.replace('/sys/class/net/', '$F/sys/class/net/')


def shell(body):
    executable = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/bin/sh.exe'
    if not executable.is_file():
        pytest.skip('Existing Git POSIX shell unavailable; no installation attempted')
    with tempfile.TemporaryDirectory(prefix='fmx-retirement-shell-') as directory:
        path = Path(directory) / 'fixture.sh'
        path.write_bytes(body.encode())
        return subprocess.run([str(executable), path.as_posix()], capture_output=True, timeout=10)


def fixture(body, *, present=True, fail_read=True, value='300', link=''):
    _, native = source_functions()
    setup = r'''set -eu
F=$(mktemp -d /tmp/fmx-retirement-XXXXXX)
case "$F" in /tmp/fmx-retirement-*) ;; *) exit 98;; esac
trap 'rc=$?; printf "FIXTURE_END rc=%s reason=%s\n" "$rc" "${reason-}"; rm -rf "$F"' EXIT
mkdir -p "$F/sys/class/net"
old_child=phy0-ap0.sta4; old_ifindex=300; old_wait_logged=0
drop_n=1; target=WA; phase=RECOVER; phase_end=160; t=100
read_fail=FAIL_READ; read_value=VALUE; fake_link=LINK
log() { printf '%s\n' "$*"; }
now() { echo "$t"; }
protect_peers() { :; }
good() { return 0; }
clear_window() { echo UNEXPECTED_PULSE_OR_RECOVERY; }
pulse_missing() { echo UNEXPECTED_PULSE_OR_RECOVERY; }
cat() {
 if [ "$1" = "$F/sys/class/net/$old_child/ifindex" ]; then
  [ "$read_fail" = 0 ] || return 1
  printf '%s' "$read_value"
 else command cat "$@"; fi
}
# Explicit dangling-link model avoids requiring Windows symlink privileges.
# Other existence checks use the real disposable filesystem.
test() {
 if [ "$#" = 2 ] && [ "$1" = -L ]; then
  case "$fake_link:$2" in
   interface:"$F/sys/class/net/$old_child"|ifindex:"$F/sys/class/net/$old_child/ifindex") return 0;;
  esac
 fi
 command test "$@"
}
'''
    setup = setup.replace('FAIL_READ', '1' if fail_read else '0').replace('VALUE', shlex.quote(value)).replace('LINK', shlex.quote(link))
    if present:
        setup += 'mkdir "$F/sys/class/net/$old_child"\n'
    return shell(setup + native + '\n' + body)


def test_transient_attribute_read_failure_waits_until_exact_absence():
    run = fixture('''
if old_wds_retired; then exit 91; else test "$?" = 1; fi
test "$old_child" = phy0-ap0.sta4
if old_wds_retired; then exit 91; else test "$?" = 1; fi
rmdir "$F/sys/class/net/$old_child"
if old_wds_retired; then :; else exit 92; fi
test -z "$old_child"
''')
    assert run.returncode == 0, (run.returncode, run.stdout.decode(), run.stderr.decode())
    lines = run.stdout.decode().splitlines()
    assert sum(line.startswith('WAIT_OLD_WDS_READ ') for line in lines) == 1
    assert sum(line.startswith('OLD_WDS_RETIRED ') for line in lines) == 1
    assert not any('UNEXPECTED_PULSE_OR_RECOVERY' in line for line in lines)


@pytest.mark.parametrize('link', ['interface', 'ifindex'])
def test_dangling_sysfs_link_is_wait_not_retired(link):
    run = fixture('''
if old_wds_retired; then exit 91; else test "$?" = 1; fi
test "$old_child" = phy0-ap0.sta4
''', present=False, link=link)
    assert run.returncode == 0, (run.returncode, run.stdout.decode(), run.stderr.decode())
    assert b'OLD_WDS_RETIRED ' not in run.stdout


@pytest.mark.parametrize('present,fail_read,value,retired', [
    (True, True, '300', False), (False, True, '', True),
    (True, False, '301', True), (True, False, '300', False)])
def test_readable_replacement_or_absence_required(present, fail_read, value, retired):
    body = 'if old_wds_retired; then rc=0; else rc=$?; fi\n'
    body += 'test "$rc" = ' + ('0' if retired else '1') + '\n'
    body += ('test -z "$old_child"\n' if retired else 'test "$old_child" = phy0-ap0.sta4\n')
    run = fixture(body, present=present, fail_read=fail_read, value=value)
    assert run.returncode == 0, (run.returncode, run.stdout.decode(), run.stderr.decode())
    assert (b'OLD_WDS_RETIRED ' in run.stdout) is retired


@pytest.mark.parametrize('value', ['', '0', 'bad-index', '00', '-1', '300 extra'])
def test_successful_invalid_ifindex_still_fails_closed_88(value):
    run = fixture('old_wds_retired\necho UNEXPECTED_SUCCESS\n', fail_read=False, value=value)
    assert run.returncode == 88, (run.returncode, run.stdout.decode(), run.stderr.decode())
    assert b'reason=old_wds_ifindex_read_invalid' in run.stdout
    assert b'OLD_WDS_RETIRED ' not in run.stdout and b'UNEXPECTED_SUCCESS' not in run.stdout


def test_persistent_unreadable_uses_original_recovery_deadline_without_pulse():
    source, _ = source_functions()
    recovery = source.split('\n RECOVER)\n', 1)[1].split('\n ;;\n STABLE)', 1)[0]
    run = fixture('for t in 100 120 159 160; do\n' + recovery + '\ndone\necho UNEXPECTED_SUCCESS\n')
    assert run.returncode == 78, (run.returncode, run.stdout.decode(), run.stderr.decode())
    assert b'reason=recovery_timeout' in run.stdout
    assert b'OLD_WDS_RETIRED ' not in run.stdout
    assert b'UNEXPECTED_PULSE_OR_RECOVERY' not in run.stdout and b'UNEXPECTED_SUCCESS' not in run.stdout
    assert 'phase_end=$(($(now)+60))' in source
