"""RAM-only LOG_LEVEL DEBUG proxy for an already reviewed AP Window.

Root injects the pinned client/window. No connection, credentials or RF on import.
LOG_LEVEL is global to this daemon; showkeys is never changed. Existing syslog
filters can still suppress some diagnostics: an empty log is not a diagnosis.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shlex

HERE = Path(__file__).resolve().parent
BINARY = HERE / 'root_goal_hostapd_cli_20261022.bin'
BINARY_SHA = 'b168f06e135a598e2a61b4c170fd4cd77e58072bf0e5d149c182a177ccb39e52'
WPAD_SHA = 'f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12'
PUT_CHUNK = 1024  # Dropbear rejects the prior >16KiB escaped exec strings.
sha = lambda b: hashlib.sha256(b).hexdigest()
q = shlex.quote


def require(ok, gate):
    if not ok:
        raise RuntimeError(gate)


def level(raw):
    match = re.fullmatch(r'Current level: (EXCESSIVE|MSGDUMP|DEBUG|INFO|WARNING|ERROR)\nTimestamp: ([01])\n?', raw.decode('ascii'))
    require(match is not None, 'LOG_LEVEL_PROTOCOL')
    return match.group(1), match.group(2)


class DebugWindow:
    """Proxy: stage before arm; restore DEBUG before radio-off, even on errors."""
    def __init__(self, window, out):
        self.window = window
        self.out = Path(out)
        self.out.mkdir(mode=0o700, exist_ok=False)
        self.token = secrets.token_hex(16)
        self.directory = '/tmp/fmx-assoc-debug-' + self.token
        self.record = {'status': 'INCOMPLETE_DEBUG', 'binary_sha256': BINARY_SHA,
                       'source_sha256': sha(Path(__file__).read_bytes()), 'showkeys_changed': False,
                       'persistent_writes': False, 'errors': [], 'diagnostic_reason_guaranteed': False}
        self.created = self.changed = self.guard_started = False
        self.original = self.daemon = self.inode = None
        self.save()

    def __getattr__(self, name):
        return getattr(self.window, name)

    def save(self):
        p = self.out / 'receipt.pending'
        with p.open('w', encoding='utf-8') as f:
            json.dump(self.record, f, indent=2); f.flush(); os.fsync(f.fileno())
        p.replace(self.out / 'receipt.json')

    def private(self, name, data):
        with (self.out / name).open('xb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        self.record[name] = {'bytes': len(data), 'sha256': sha(data)}

    def checked(self, client, command, timeout=6):
        return self.window.ap.checked(client, command, timeout=timeout)

    def identity(self, client):
        self.window.ap.identity(client)
        # Print only PID/starttime; argv is inspected remotely, never exported.
        raw = self.checked(client, "set -eu\npids=$(pidof hostapd || true)\nselected=' '\n"
            "for p in $pids; do\n exe=$(readlink /proc/$p/exe) || exit 92\n"
            " test \"$exe\" = /usr/sbin/wpad || continue\n"
            " case \"$selected\" in *\" $p \"*) ;; *) selected=\"$selected$p \";; esac\ndone\n"
            "set -- $selected\ntest $# = 1\np=$1\ntest \"$(readlink /proc/$p/exe)\" = /usr/sbin/wpad\n"
            "test \"$(awk '/^Uid:/{print $2,$3,$4,$5}' /proc/$p/status)\" = '101 101 101 101'\n"
            "test \"$(awk '/^Gid:/{print $2,$3,$4,$5}' /proc/$p/status)\" = '101 101 101 101'\n"
            "test \"$(sha256sum /usr/sbin/wpad | cut -d' ' -f1)\" = " + WPAD_SHA + "\n"
            "if tr '\\000' '\\n' < /proc/$p/cmdline | grep -q '^-[^-]*K'; then exit 92; fi\n"
            "printf '%s ' \"$p\"; awk '{print $22}' /proc/$p/stat")
        require(re.fullmatch(rb'[1-9][0-9]* [0-9]+\n', raw), 'DAEMON_IDENTITY_PROTOCOL')
        if self.daemon is not None:
            require(raw == self.daemon, 'DAEMON_CHANGED')
        return raw

    def put(self, client, name, data, mode):
        # Only bounded SSH exec commands: no unbounded SFTP subsystem handshake.
        require(name in ('owner', 'cli', 'guard.sh'), 'RAM_FILE_NAME')
        path = q(self.directory + '/' + name)
        self.checked(client, 'set -eu\numask 077\nset -C\n: >' + path)
        for off in range(0, len(data), PUT_CHUNK):
            escaped = ''.join('\\%03o' % b for b in data[off:off + PUT_CHUNK])
            self.checked(client, 'set -eu\ntest ! -L ' + path + '\ntest -f ' + path
                + '\ntest "$(wc -c <' + path + ')" -eq ' + str(off)
                + '\nprintf ' + q(escaped) + ' >>' + path)
        self.checked(client, 'set -eu\nchmod ' + oct(mode)[2:] + ' ' + path
            + '\ntest "$(ls -ldn ' + path + " | awk '{print $1,$2,$3,$4,$5}')\" = "
            + q(('-rwx------' if mode == 0o700 else '-rw-------') + ' 1 0 0 ' + str(len(data)))
            + '\ntest "$(sha256sum ' + path + " | cut -d' ' -f1)\" = " + sha(data))

    def stage(self, client):
        require(not self.created, 'ONE_DEBUG_STAGE')
        data = BINARY.read_bytes()
        require(len(data) == 59016 and sha(data) == BINARY_SHA, 'LOCAL_CLI_CHANGED')
        self.daemon = self.identity(client)
        self.checked(client, "set -eu\nawk '$2==\"/tmp\"{n++;if($3!=\"tmpfs\")bad=1} END{exit(n!=1||bad)}' /proc/mounts\n"
            "test -S /var/run/hostapd/global\numask 077\nmkdir " + q(self.directory))
        self.created = True
        # Exact native daemon uid/gid101 needs search, not listing, on this NEW
        # private IPC directory. Binary700/owner600 remain root-only.
        self.checked(client, 'set -eu\nchgrp 101 ' + q(self.directory)
            + '\nchmod 710 ' + q(self.directory))
        self.inode = self.checked(client, 'ls -lidn ' + q(self.directory)
            + " | awk '{print $1,$2,$4,$5}'").decode().strip()
        require(re.fullmatch(r'[0-9]+ drwx--x--- 0 101', self.inode), 'RAM_DIRECTORY_IDENTITY')
        self.put(client, 'owner', self.token.encode(), 0o600)
        self.put(client, 'cli', data, 0o700)
        require(self.checked(client, 'sha256sum ' + q(self.directory + '/cli')).split()[0].decode() == BINARY_SHA, 'REMOTE_CLI_SHA')
        require(self.checked(client, self.global_control('PING')).strip() == b'PONG', 'GLOBAL_CONTROL_PING_FAILED')
        self.record['global_ping_verified_before_rf'] = True
        self.record['staged'] = True
        self.save()

    def global_control(self, command):
        return (q(self.directory + '/cli') + ' -p /var/run/hostapd -i global -s '
                + q(self.directory) + ' raw ' + q(command))

    def control(self, command):
        return self.global_control('IFNAME=' + self.interface + ' ' + command)

    def cli(self, command):
        return self.control('LOG_LEVEL' + command)

    def attach(self, client):
        self.identity(client)
        self.interface = self.window.ready['interface']
        require(re.fullmatch(r'[a-zA-Z0-9_.-]{1,15}', self.interface), 'INTERFACE_PROTOCOL')
        self.original = level(self.checked(client, self.cli('')))
        require(self.original[0] not in ('EXCESSIVE', 'MSGDUMP'), 'BASELINE_TOO_VERBOSE')
        self.record['original_level'], self.record['original_timestamp'] = self.original
        filtered = self.checked(client, "set -eu\nf=/var/run/hostapd-phy0.conf\ntest -f \"$f\"\n"
            "awk '/^(interface|bss|logger_syslog_level)=/{print}' \"$f\"").decode()
        rows = filtered.splitlines()
        require(rows.count('interface=' + self.interface) == 1
                and sum(s.startswith(('interface=', 'bss=')) for s in rows) == 1, 'LOGGER_BSS_SCOPE')
        levels = [s.split('=', 1)[1] for s in rows if s.startswith('logger_syslog_level=')]
        require(len(levels) == 1 and re.fullmatch('[0-4]', levels[0]), 'LOGGER_ORIGINAL_LEVEL')
        self.syslog_original = levels[0]
        self.record['original_logger_syslog_level'] = self.syslog_original
        self.private('log.before.txt', self.checked(client, 'set -o pipefail\nlogread -l 180 | tail -c 50000'))
        pid, start = self.daemon.decode().split()
        restore = self.cli(' ' + ' '.join(self.original))
        # Best effort only: no daemon restart, global reset or radio operation.
        guard = ("#!/bin/sh\ntrap '' HUP\ntrap 'touch " + q(self.directory + '/guard.done') + "' EXIT\n"
            "n=0\nwhile test $n -lt 90; do\n test ! -e " + q(self.directory + '/disarm')
            + " || exit 0\n sleep 1\n n=$((n+1))\ndone\n"
            "test \"$(awk '{print $22}' /proc/" + pid + "/stat)\" = " + start + " || exit 92\n"
            + self.cli('') + " | grep -Eq '^Current level: (DEBUG|" + self.original[0] + ")$' || exit 93\n"
            + self.control('SET logger_syslog_level ' + self.syslog_original)
            + ' >' + q(self.directory + '/guard.log') + ' 2>&1\n'
            + restore + ' >>' + q(self.directory + '/guard.log') + ' 2>&1\n')
        self.put(client, 'guard.sh', guard.encode(), 0o700)
        self.checked(client, "sh " + q(self.directory + '/guard.sh') + ' </dev/null >/dev/null 2>&1 &')
        self.guard_started = True
        self.changed = True  # Uncertain dispatch must still restore.
        require(self.checked(client, self.control('SET logger_syslog_level 0')).strip() == b'OK', 'LOGGER_SET_FAILED')
        require(self.checked(client, self.cli(' DEBUG')).strip() == b'OK', 'DEBUG_SET_FAILED')
        require(level(self.checked(client, self.cli(''))) == ('DEBUG', self.original[1]), 'DEBUG_VERIFY_FAILED')
        self.record['debug_verified'] = True
        self.record['guard'] = '90s_best_effort_same_daemon_and_existing_BSS_only'
        self.save()

    def arm(self, client):
        try:
            self.stage(client)
            ready = self.window.arm(client)
            self.attach(client)
            return ready
        except BaseException:
            self.restore(client)
            raise

    def restore_level(self, client):
        if self.changed:
            self.identity(client)
            current = level(self.checked(client, self.cli('')))
            require(current in (('DEBUG', self.original[1]), self.original), 'LOG_LEVEL_CONCURRENT_CHANGE')
            errors = []
            try:
                require(self.checked(client, self.control('SET logger_syslog_level ' + self.syslog_original)).strip() == b'OK', 'LOGGER_RESTORE_FAILED')
                self.record['logger_restore_acknowledged'] = True
            except BaseException as e:
                errors.append(str(e))
            try:
                require(self.checked(client, self.cli(' ' + ' '.join(self.original))).strip() == b'OK', 'DEBUG_RESTORE_FAILED')
                require(level(self.checked(client, self.cli(''))) == self.original, 'DEBUG_RESTORE_VERIFY_FAILED')
                self.record['level_restored_verified'] = True
            except BaseException as e:
                errors.append(str(e))
            require(not errors, 'LOGGING_RESTORE_ERRORS:' + ';'.join(errors))

    def cleanup(self, client):
        if not self.created:
            return
        d = q(self.directory)
        guard = ('touch "$d/disarm"\nn=0\nwhile test ! -f "$d/guard.done"; do\n'
                 ' test $n -lt 3 || exit 94\n sleep 1\n n=$((n+1))\ndone\n') if self.guard_started else ''
        self.checked(client, 'set -eu\nd=' + d + '\ntest ! -L "$d"\ntest -d "$d"\n'
            'test "$(ls -lidn "$d" | awk \'{print $1,$2,$4,$5}\')" = ' + q(self.inode) + '\n'
            'test "$(cat "$d/owner")" = ' + q(self.token) + '\n' + guard
            + 'for f in "$d"/* "$d"/.[!.]* "$d"/..?*; do\n'
            ' if test ! -e "$f" && test ! -L "$f"; then continue; fi\n'
            ' case "${f##*/}" in cli|owner|guard.sh|guard.done|guard.log|disarm) ;; *) exit 95;; esac\n'
            ' test ! -L "$f"; test -f "$f"; test "$(ls -ldn "$f" | awk \'{print $2,$3,$4}\')" = "1 0 0"\ndone\n'
            'for n in cli owner guard.sh guard.done guard.log disarm; do\n'
            ' if test -f "$d/$n"; then rm "$d/$n"; fi\ndone\nrmdir "$d"', timeout=10)
        self.record['ram_cleanup_verified'] = True
        self.created = False

    def restore(self, client):
        if self.record.get('restore_finished'):
            return self.record['result']
        try:
            self.restore_level(client)
        except BaseException as e:
            self.record['errors'].append('level:' + type(e).__name__ + ':' + str(e))
        # Always attempt frozen radio-off, even if logging restoration failed.
        try:
            self.record['frozen_restoration'] = self.window.restore(client)
        except BaseException as e:
            self.record['errors'].append('radio:' + type(e).__name__ + ':' + str(e))
        try:
            if self.created:
                self.private('log.after.txt', self.checked(client, 'set -o pipefail\nlogread -l 300 | tail -c 50000'))
        except BaseException as e:
            self.record['errors'].append('log_capture:' + type(e).__name__ + ':' + str(e))
        try:
            self.cleanup(client)
        except BaseException as e:
            self.record['errors'].append('cleanup:' + type(e).__name__ + ':' + str(e))
        result = self.record.get('frozen_restoration')
        if self.record['errors']:
            result = {'status': 'INCOMPLETE_DEBUG_RESTORATION', 'frozen_radio_restoration': result}
        self.record.update(status='DEBUG_PROXY_COMPLETE' if not self.record['errors'] else 'INCOMPLETE_DEBUG_RESTORATION',
                           restore_finished=True, result=result)
        self.save()
        return result


if __name__ == '__main__':
    print(json.dumps({'status': 'PLAN_ONLY', 'binary_sha256': BINARY_SHA,
                      'api': 'DebugWindow(existing_window, exclusive_local_out)',
                      'device_actions': False, 'diagnostic_reason_guaranteed': False}))
