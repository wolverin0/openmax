"""Reuse held AP DEBUG tooling for XC recovery; raw logs remain private."""
from pathlib import Path
import re
import shlex
from types import SimpleNamespace
import time

import root_four_cpe_access_20261022 as access

XC = 'b4:fb:e4:5c:d5:d2'


def public_context(lines):
    """Only new hostapd XC context; never export key material or hexdumps."""
    selected = set()
    for i, line in enumerate(lines):
        if XC in line.lower():
            selected.update(range(max(0, i - 3), min(len(lines), i + 4)))
    result = []
    for i in sorted(selected):
        line = lines[i]
        if 'hostapd' not in line.lower():
            continue
        macs = re.findall(r'(?i)(?:[0-9a-f]{2}:){5}[0-9a-f]{2}', line)
        if any(mac.lower() != XC for mac in macs):
            continue
        if XC not in line.lower() and not re.search(r'(?i)assoc|reject|invalid|unknown|denied|wmm|ssid|rate|vlan|ubus|fail|error', line):
            continue
        if re.search(r'(?i)password|passphrase|\bpsk\b|\bpmk\b|\bptk\b|\bgtk\b|hexdump|key\s*=', line):
            continue
        result.append(line[:600])
    return result[:100]


class APTrace:
    def __init__(self, helper, private_out):
        base = access.load('root_goal_ap_assoc_debug_20261022.py')
        base.PUT_CHUNK = 512  # Keep escaped binary staging commands below4096B.
        self.proxy = base.DebugWindow(SimpleNamespace(ap=helper, ready={'interface': 'phy0-ap0'}), private_out)
        self.guard = None
        self.started = False
        self.finished = False
        self.next_capture = 0.0
        self.capture_count = 0
        self.seen_lines = set()
        self.new_lines = []
        self.result = None

    def stage(self, ap):
        self.proxy.stage(ap)

    def start(self, ap):
        access.require(not self.started, 'AP_TRACE_ALREADY_STARTED')
        self.proxy.attach(ap)
        self.started = True
        # Inspect only exact guard argv remotely; export PID/start, never argv.
        expected = shlex.quote('sh\n' + self.proxy.directory + '/guard.sh')
        alternate = shlex.quote('/bin/sh\n' + self.proxy.directory + '/guard.sh')
        command = ("set -eu\npids=$(pidof sh || true)\nset -- $pids\ntest $# -le 256\nfound=\n"
                   "for p do\n test -r /proc/$p/cmdline || continue\n"
                   " args=$(tr '\\000' '\\n' < /proc/$p/cmdline) || continue\n"
                   ' if test "$args" = ' + expected + ' || test "$args" = ' + alternate + '; then\n'
                   '  test -z "$found"\n  found=$p\n fi\ndone\ntest -n "$found"\n'
                   'printf "%s " "$found"; awk \'{print $22}\' /proc/$found/stat\n')
        raw = self.proxy.checked(ap, command)
        access.require(re.fullmatch(rb'[1-9][0-9]* [1-9][0-9]*\n', raw) is not None, 'AP_TRACE_GUARD_IDENTITY')
        self.guard = raw.decode().split()
        self.proxy.record['guard_pid_start'] = self.guard
        self.proxy.save()
        self.sample(ap, force=True)

    def sample(self, ap, force=False):
        limit = 14 if force else 13  # Reserve the last slot for finish().
        if not self.started or self.finished or self.capture_count >= limit:
            return
        stamp = time.monotonic()
        if not force and stamp < self.next_capture:
            return
        raw = self.proxy.checked(ap, 'set -o pipefail\nlogread | tail -c 50000')
        access.require(len(raw) <= 50000, 'AP_TRACE_LOG_BOUND')
        name = 'XC-snapshot-%02d.txt' % self.capture_count
        self.proxy.private(name, raw)
        lines = raw.decode(errors='replace').splitlines()
        if self.capture_count:
            self.new_lines.extend(line for line in lines if line not in self.seen_lines)
        self.seen_lines.update(lines)
        self.capture_count += 1
        self.next_capture = time.monotonic() + 5
        self.proxy.record['private_snapshot_count'] = self.capture_count
        self.proxy.save()

    def verify_guard_ended(self, ap):
        if not self.proxy.guard_started:
            return
        access.require(self.guard is not None, 'AP_TRACE_GUARD_IDENTITY_MISSING')
        pid, ticks = self.guard
        command = ('set -eu\nfor n in 1 2 3 4 5; do\n'
                   ' if test ! -r /proc/' + pid + '/stat; then exit 0; fi\n'
                   ' test "$(awk \'{print $22}\' /proc/' + pid + '/stat)" = ' + ticks + ' || exit 0\n'
                   ' test "$(awk \'{print $3}\' /proc/' + pid + '/stat)" != Z || exit 0\n'
                   ' sleep 1\ndone\nexit 95\n')
        self.proxy.checked(ap, command, timeout=8)
        self.proxy.record['guard_ended_verified'] = True

    def finish(self, ap):
        if self.finished:
            return self.result
        errors = []
        # Each operation is independent; failures must never skip logging reset
        # or cleanup, and the runner still performs its original AP radio-off.
        for label, action in [
            ('capture', lambda: self.sample(ap, force=True)),
            ('logging_restore', lambda: self.proxy.restore_level(ap)),
            ('RAM_cleanup', lambda: self.proxy.cleanup(ap)),
            ('guard_end', lambda: self.verify_guard_ended(ap)),
        ]:
            try:
                action()
            except BaseException as error:
                errors.append(label + ':' + type(error).__name__ + ':' + str(error)[:160])
        self.proxy.record['errors'].extend(errors)
        if self.started and not errors:
            required = ['guard_ended_verified', 'logger_restore_acknowledged',
                        'level_restored_verified', 'ram_cleanup_verified']
            errors.extend('missing_positive_proof:' + key for key in required if not self.proxy.record.get(key))
            self.proxy.record['errors'].extend(errors)
        self.proxy.record['status'] = ('TRACE_INCOMPLETE' if errors else
                                       'TRACE_COMPLETE' if self.started else 'TRACE_NOT_STARTED_RESTORED')
        self.proxy.save()
        self.finished = True
        self.result = dict(status=self.proxy.record['status'], started=self.started,
                           binary_sha256=self.proxy.record.get('binary_sha256'),
                           base_source_sha256=self.proxy.record.get('source_sha256'),
                           global_ping_verified_before_window=self.proxy.record.get('global_ping_verified_before_rf', False),
                           debug_verified=self.proxy.record.get('debug_verified', False),
                           showkeys_changed=self.proxy.record.get('showkeys_changed', False),
                           original_level=self.proxy.record.get('original_level'),
                           original_timestamp=self.proxy.record.get('original_timestamp'),
                           original_logger_syslog_level=self.proxy.record.get('original_logger_syslog_level'),
                           logging_guard=self.proxy.record.get('guard'),
                           guard_pid_start=self.guard,
                           guard_ended_verified=self.proxy.record.get('guard_ended_verified', False),
                           logger_restore_acknowledged=self.proxy.record.get('logger_restore_acknowledged', False),
                           level_restored_verified=self.proxy.record.get('level_restored_verified', False),
                           RAM_cleanup_verified=self.proxy.record.get('ram_cleanup_verified', False),
                           private_snapshot_count=self.capture_count,
                           private_receipt_sha256=access.sha((self.proxy.out / 'receipt.json').read_bytes()),
                           new_XC_context=public_context(self.new_lines), errors=errors,
                           limit='Hostapd diagnostic text, not RF timestamps, performance or production acceptance.')
        return self.result
