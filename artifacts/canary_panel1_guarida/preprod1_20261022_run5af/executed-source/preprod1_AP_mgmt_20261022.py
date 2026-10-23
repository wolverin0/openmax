"""Bounded AP control RX-management trace; raw frames stay in private history."""
from pathlib import Path
import re
import shlex
import threading
import time
from types import SimpleNamespace

import root_four_cpe_access_20261022 as access

HERE = Path(__file__).resolve().parent
XC = bytes.fromhex('b4fbe45cd5d2')
AP = bytes.fromhex('18e8297455a2')
RAW_LIMIT = 262144
FRAME_LIMIT = 2000  # Below the held CLI's 4095-byte receive limit including prefix.


def frame_summary(raw):
    """Export only XC RX frame structure; never export raw IEs or foreign frames."""
    summaries = []
    for match in re.finditer(rb'AP-MGMT-FRAME-RECEIVED buf=([^\r\n ]*)', raw):
        encoded = match[1]
        access.require(re.fullmatch(rb'[0-9a-fA-F]+', encoded) is not None
                       and len(encoded) % 2 == 0 and 48 <= len(encoded) <= FRAME_LIMIT * 2,
                       'AP_MGMT_FRAME_TRUNCATED_OR_INVALID')
        frame = bytes.fromhex(encoded.decode('ascii'))
        access.require(frame[0] & 0x0c == 0, 'AP_MGMT_NOT_MANAGEMENT')
        if frame[10:16] != XC:
            continue
        access.require(frame[4:10] == AP and frame[16:22] == AP,
                       'AP_MGMT_XC_ADDRESS_CONTEXT')
        subtype = frame[0] >> 4
        item = dict(subtype=subtype, bytes=len(frame), sha256=access.sha(frame),
                    sequence_control=int.from_bytes(frame[22:24], 'little'),
                    sequence=int.from_bytes(frame[22:24], 'little') >> 4,
                    retry=bool(frame[1] & 8))
        if subtype in (0, 2):
            offset = 28 if subtype == 0 else 34
            if len(frame) < offset:
                item['association_parse_error'] = 'received_fixed_fields_too_short'
                summaries.append(item)
                continue
            item.update(capability=int.from_bytes(frame[24:26], 'little'),
                        listen_interval=int.from_bytes(frame[26:28], 'little'), ies=[])
            ssids = []
            while offset < len(frame):
                if offset + 2 > len(frame):
                    item['association_parse_error'] = 'received_IE_header_too_short'
                    break
                ident, length = frame[offset:offset + 2]
                offset += 2
                if offset + length > len(frame):
                    item['association_parse_error'] = 'received_IE_length_exceeds_body'
                    item['invalid_IE'] = dict(id=ident, declared_bytes=length, remaining_bytes=len(frame) - offset)
                    break
                value = frame[offset:offset + length]
                offset += length
                entry = dict(id=ident, bytes=length, sha256=access.sha(value))
                if ident == 0:
                    ssids.append(value == b'FuturaMAX-LAB')
                elif ident in (1, 50):
                    entry['rates_hex'] = value.hex()
                elif ident == 221 and value.startswith(b'\x00\x50\xf2\x02'):
                    entry['WMM_header_hex'] = value[:7].hex()
                elif ident == 48:
                    entry['RSN_version'] = int.from_bytes(value[:2], 'little') if length >= 2 else None
                item['ies'].append(entry)
            item['SSID_exact_one_lab_match'] = ssids == [True]
        summaries.append(item)
    return summaries


class APTrace:
    def __init__(self, helper, private_out, guard_seconds=90):
        private_out = Path(private_out)
        parent = HERE / 'preprod_guarida_20261022' / 'history'
        access.require(private_out.parent == parent and parent.is_dir()
                       and not parent.is_symlink() and not parent.parent.is_symlink()
                       and re.fullmatch(r'preprod1_[A-Za-z0-9_-]+_AP_mgmt', private_out.name),
                       'AP_MGMT_PRIVATE_SCOPE')
        access.require(type(guard_seconds) is int and guard_seconds in (90, 180), 'AP_MGMT_GUARD_DURATION')
        self.guard_seconds = guard_seconds
        base = access.load('root_goal_ap_assoc_debug_20261022.py')
        base.PUT_CHUNK = 512
        self.wpad_sha = base.WPAD_SHA
        self.proxy = base.DebugWindow(SimpleNamespace(ap=helper, ready={'interface': 'phy0-ap0'}), private_out)
        self.proxy.record.update(status='INCOMPLETE_MGMT_TRACE', purpose='RX management only',
                                 trace_source_sha256=access.sha(Path(__file__).read_bytes()),
                                 debug_level_changed=False)
        self.stream = None
        self.listener = self.guard = None
        self.raw = bytearray()
        self.error = bytearray()
        self.started = self.finished = False
        self.changed = False
        self.result = None

    def stage(self, ap):
        self.proxy.stage(ap)

    def _ended(self, ap, identity, terminate=False):
        pid, ticks = identity
        test = ('test -r /proc/' + pid + '/stat && test "$(awk \'{print $22}\' /proc/'
                + pid + '/stat)" = ' + ticks + ' && test "$(awk \'{print $3}\' /proc/'
                + pid + '/stat)" != Z')
        command = 'set -eu\n'
        if terminate:
            command += ('if ' + test + '; then\n test "$(readlink /proc/' + pid
                        + '/exe)" = ' + shlex.quote(self.proxy.directory + '/cli')
                        + '\n kill -TERM ' + pid + '\nfi\n')
        command += ('for n in 1 2 3 4 5; do\n if ! { ' + test
                    + '; }; then echo ENDED; exit 0; fi\n sleep 1\ndone\nexit 95\n')
        access.require(self.proxy.checked(ap, command, timeout=8).strip() == b'ENDED',
                       'AP_MGMT_OWNED_PROCESS_NOT_ENDED')

    def _drain(self):
        if self.stream is None:
            return
        channel = self.stream[1].channel
        while channel.recv_ready():
            access.require(len(self.raw) <= RAW_LIMIT, 'AP_MGMT_STREAM_BOUND')
            part = channel.recv(min(8192, RAW_LIMIT + 1 - len(self.raw)))
            access.require(bool(part), 'AP_MGMT_STREAM_EOF')
            self.raw.extend(part)
            access.require(len(self.raw) <= RAW_LIMIT, 'AP_MGMT_STREAM_BOUND')
        if channel.recv_stderr_ready():
            access.require(len(self.error) <= 8192, 'AP_MGMT_LISTENER_STDERR')
            self.error.extend(channel.recv_stderr(max(1, 8193 - len(self.error))))
            access.require(len(self.error) <= 8192 and not self.error, 'AP_MGMT_LISTENER_STDERR')

    def sample(self, ap=None):
        if self.stream is None or self.finished:
            return
        self._drain()
        channel = self.stream[1].channel
        access.require(not channel.exit_status_ready(), 'AP_MGMT_LISTENER_ENDED_EARLY')

    def start(self, ap, previous_trace=None):
        access.require(not self.started and self.proxy.created, 'AP_MGMT_START_STATE')
        self.started = True
        self.proxy.identity(ap)
        self.proxy.interface = 'phy0-ap0'
        # This BSS was freshly reloaded by the exclusive runner. No previous
        # notify SET is allowed; absent configuration uses the exact source's 0.
        settings = self.proxy.checked(ap, "set -eu\nf=/var/run/hostapd-phy0.conf\n"
            "test -f \"$f\"\nawk '/^(interface|bss|notify_mgmt_frames)=/{print}' \"$f\"").decode().splitlines()
        access.require(settings.count('interface=phy0-ap0') == 1
                       and sum(s.startswith(('interface=', 'bss=')) for s in settings) == 1
                       and [s for s in settings if s.startswith('notify_mgmt_frames=')] in ([], ['notify_mgmt_frames=0']),
                       'AP_MGMT_BASELINE_CONFIG_NOT_ZERO')
        self.proxy.record['original_notify'] = 0
        self.proxy.record['guard_seconds'] = self.guard_seconds
        if previous_trace is None:
            self.proxy.record['original_provenance'] = 'Fresh exclusive BSS reload/config/default0; no RAM getter or prior SET.'
        else:
            proof = previous_trace.result if previous_trace.finished else None
            access.require(previous_trace is not self and isinstance(proof, dict)
                           and proof.get('status') == 'TRACE_COMPLETE'
                           and all(proof.get(k) is True for k in ['notify_restore_acknowledged',
                               'listener_ended_verified', 'guard_ended_verified', 'ram_cleanup_verified'])
                           and re.fullmatch(r'[0-9a-f]{64}', proof.get('private_receipt_sha256', '')),
                           'AP_MGMT_PREVIOUS_TRACE_RESET_NOT_PROVEN')
            self.proxy.record['original_provenance'] = 'Exact exclusive prior trace reset0 ACK and listener/guard/RAM ended; no intervening writer.'
            self.proxy.record['previous_trace_private_receipt_sha256'] = proof['private_receipt_sha256']
        pid, ticks = self.proxy.daemon.decode().split()
        guard = ("#!/bin/sh\nset -eu\ntest $# = 2\nlp=$1; lt=$2\n"
                 "case $lp:$lt in *[!0-9:]*|:*|*:) exit 92;; esac\n"
                 "trap '' HUP\ntrap 'touch " + shlex.quote(self.proxy.directory + '/guard.done') + "' EXIT\n"
                 'n=0\nwhile test $n -lt ' + str(self.guard_seconds) + '; do\n test ! -e ' + shlex.quote(self.proxy.directory + '/disarm')
                 + ' || exit 0\n sleep 1\n n=$((n+1))\ndone\n'
                 'if test -r /proc/' + pid + '/stat && test "$(awk \'{print $22}\' /proc/' + pid + '/stat)" = ' + ticks
                 + ' && test "$(readlink /proc/' + pid + '/exe)" = /usr/sbin/wpad'
                 + ' && test "$(sha256sum /usr/sbin/wpad | cut -d\' \' -f1)" = ' + self.wpad_sha
                 + '; then\n if ' + self.proxy.control('SET notify_mgmt_frames 0') + ' >'
                 + shlex.quote(self.proxy.directory + '/guard.log') + ' 2>&1; then :; else\n'
                 + '  echo NOTIFY_RESET_FAILED >>' + shlex.quote(self.proxy.directory + '/guard.log') + '\n fi\nfi\n'
                 'if test -r /proc/$lp/stat && test "$(awk \'{print $22}\' /proc/$lp/stat)" = "$lt"'
                 + ' && test "$(readlink /proc/$lp/exe)" = ' + shlex.quote(self.proxy.directory + '/cli')
                 + '; then kill -TERM "$lp"; fi\n')
        self.proxy.private('guard-source.sh', guard.encode())
        self.proxy.put(ap, 'guard.sh', guard.encode(), 0o700)
        command = ('set -eu\nlp=$$; lt=$(awk \'{print $22}\' /proc/$$/stat)\nsh '
                   + shlex.quote(self.proxy.directory + '/guard.sh')
                   + ' "$lp" "$lt" </dev/null >/dev/null 2>&1 &\ngp=$!\ngt=$(awk \'{print $22}\' /proc/$gp/stat)\n'
                   'printf \'MGMT_LISTENER %s %s %s %s\\n\' "$lp" "$lt" "$gp" "$gt"\nexec '
                   + shlex.quote(self.proxy.directory + '/cli')
                   + ' -p /var/run/hostapd -i global -s ' + shlex.quote(self.proxy.directory))
        deadline = time.monotonic() + 5
        channel = ap.get_transport().open_session(timeout=5)
        self.stream = (channel.makefile_stdin('wb', -1), channel.makefile('r', -1),
                       channel.makefile_stderr('r', -1))
        expired = threading.Event()
        def expire():
            expired.set()
            channel.close()  # Only this published acquisition channel.
        timer = threading.Timer(max(.001, deadline - time.monotonic()), expire)
        timer.daemon = True
        try:
            access.require(time.monotonic() < deadline, 'AP_MGMT_ATTACH_PING_DEADLINE')
            channel.settimeout(max(.01, deadline - time.monotonic()))
            timer.start()  # Exec-ACK waits are not bounded by settimeout alone.
            self.proxy.guard_started = True  # Native launch may dispatch uncertainly.
            channel.exec_command(command)
            header = self.stream[1].readline(129)
            access.require(re.fullmatch(r'MGMT_LISTENER(?: [1-9][0-9]*){4}\n', header), 'AP_MGMT_LISTENER_ID')
            values = header.split()[1:]
            self.listener, self.guard = values[:2], values[2:]
            self.proxy.record['listener_pid_start'] = self.listener
            self.proxy.record['guard_pid_start'] = self.guard
            self.stream[0].write('ping\n'); self.stream[0].flush()
            while time.monotonic() < deadline:
                self.sample(ap)
                if re.search(rb'(?:^|[\r\n])(?:>\s*)?PONG(?:[\r\n]|$)', self.raw):
                    break
                time.sleep(.05)
            else:
                raise RuntimeError('AP_MGMT_ATTACH_PING_DEADLINE')
            access.require(not expired.is_set() and time.monotonic() < deadline,
                           'AP_MGMT_ATTACH_PING_DEADLINE')
        except BaseException:
            access.require(not expired.is_set(), 'AP_MGMT_ATTACH_PING_DEADLINE')
            raise
        finally:
            timer.cancel()
        self.proxy.record['interactive_attach_ping_ready'] = True
        gp, gt = self.guard
        lp, lt = self.listener
        expected = shlex.quote('sh\n' + self.proxy.directory + '/guard.sh\n' + lp + '\n' + lt)
        alternate = shlex.quote('/bin/sh\n' + self.proxy.directory + '/guard.sh\n' + lp + '\n' + lt)
        live = ('set -eu\ntest -r /proc/' + gp + '/stat\n'
                'test "$(awk \'{print $22}\' /proc/' + gp + '/stat)" = ' + gt + '\n'
                'test "$(awk \'{print $3}\' /proc/' + gp + '/stat)" != Z\n'
                'test ! -f ' + shlex.quote(self.proxy.directory + '/guard.done') + '\n'
                'test "$(sha256sum ' + shlex.quote(self.proxy.directory + '/guard.sh')
                + ' | cut -d\' \' -f1)" = ' + access.sha(guard.encode()) + '\n'
                'args=$(tr \'\\000\' \'\\n\' < /proc/' + gp + '/cmdline)\n'
                'test "$args" = ' + expected + ' || test "$args" = ' + alternate + '\n'
                'echo MGMT_GUARD_LIVE_SOURCE_BOUND\n')
        access.require(self.proxy.checked(ap, live).strip() == b'MGMT_GUARD_LIVE_SOURCE_BOUND',
                       'AP_MGMT_GUARD_NOT_LIVE_SOURCE_BOUND')
        self.proxy.record['guard_live_source_bound_before_enable'] = True
        self.changed = True  # An uncertain SET dispatch must still restore.
        access.require(self.proxy.checked(ap, self.proxy.control('SET notify_mgmt_frames 1')).strip() == b'OK',
                       'AP_MGMT_NOTIFY_ENABLE_FAILED')
        self.proxy.record['notify_enable_acknowledged'] = True
        self.proxy.save()

    def _restore_notify(self, ap):
        if self.changed:
            self.proxy.identity(ap)
            access.require(self.proxy.checked(ap, self.proxy.control('SET notify_mgmt_frames 0')).strip() == b'OK',
                           'AP_MGMT_NOTIFY_RESTORE_FAILED')
            self.proxy.record['notify_restore_acknowledged'] = True

    def _stop_listener(self, ap):
        if self.stream is None:
            return
        try:
            if not self.stream[1].channel.exit_status_ready():
                self.stream[0].write('quit\n'); self.stream[0].flush()
        except Exception:
            pass
        try:
            access.require(self.listener is not None, 'AP_MGMT_LISTENER_ID_MISSING')
            self._ended(ap, self.listener, terminate=True)
            self.proxy.record['listener_ended_verified'] = True
            self._drain()
        finally:
            for file in self.stream:
                try:
                    file.close()
                except Exception:
                    pass
            self.stream[1].channel.close()

    def _archive(self):
        self.proxy.record['raw_observed_bytes_at_least'] = len(self.raw)
        self.proxy.record['raw_capture_truncated'] = len(self.raw) > RAW_LIMIT
        self.proxy.record['stderr_capture_truncated'] = len(self.error) > 8192
        if not (self.proxy.out / 'mgmt-stream.txt').exists():
            self.proxy.private('mgmt-stream.txt', bytes(self.raw[:RAW_LIMIT]))
        if self.error and not (self.proxy.out / 'listener-stderr.txt').exists():
            self.proxy.private('listener-stderr.txt', bytes(self.error[:8192]))
        access.require(len(self.raw) <= RAW_LIMIT, 'AP_MGMT_STREAM_BOUND')
        access.require(len(self.error) <= 8192, 'AP_MGMT_LISTENER_STDERR')
        frames = frame_summary(bytes(self.raw))
        self.proxy.record['XC_RX_frames'] = frames
        if self.proxy.record.get('notify_enable_acknowledged'):
            access.require(any(f['subtype'] in (0, 2) for f in frames), 'AP_MGMT_NO_XC_ASSOC_REQUEST')

    def _cleanup(self, ap):
        # Never cancel the native reset after an unconfirmed host reset, or
        # remove its source files before proving this exact process ended.
        access.require(not self.changed or self.proxy.record.get('notify_restore_acknowledged'),
                       'AP_MGMT_RESET_UNCONFIRMED_KEEP_NATIVE_GUARD')
        if self.proxy.guard_started:
            access.require(self.guard is not None, 'AP_MGMT_GUARD_ID_MISSING')
            if self.started and self.stream is not None:
                access.require(self.proxy.record.get('listener_ended_verified'), 'AP_MGMT_KEEP_FILES_FOR_UNVERIFIED_LISTENER')
            self.proxy.checked(ap, 'touch ' + shlex.quote(self.proxy.directory + '/disarm'))
            self._ended(ap, self.guard)
            self.proxy.record['guard_ended_verified'] = True
            log = self.proxy.checked(ap, 'if test -f ' + shlex.quote(self.proxy.directory + '/guard.log')
                + '; then head -c 1025 ' + shlex.quote(self.proxy.directory + '/guard.log') + '; fi')
            access.require(len(log) <= 1024, 'AP_MGMT_GUARD_LOG_BOUND')
            if log:
                self.proxy.private('guard-log.txt', log)
        self.proxy.cleanup(ap)

    def finish(self, ap):
        if self.finished:
            return self.result
        errors = []
        actions = [('notify_restore', lambda: self._restore_notify(ap)),
                   ('listener_end', lambda: self._stop_listener(ap)),
                   ('private_archive', self._archive),
                   ('RAM_cleanup', lambda: self._cleanup(ap))]
        for label, action in actions:
            try:
                action()
            except BaseException as error:
                errors.append(label + ':' + type(error).__name__ + ':' + str(error)[:160])
        if self.started and not errors:
            errors.extend('missing_positive_proof:' + key for key in
                ['interactive_attach_ping_ready', 'notify_enable_acknowledged', 'notify_restore_acknowledged',
                 'guard_live_source_bound_before_enable', 'listener_ended_verified',
                 'guard_ended_verified', 'ram_cleanup_verified']
                if not self.proxy.record.get(key))
        self.proxy.record.update(errors=errors, status='TRACE_INCOMPLETE' if errors else
                                 'TRACE_COMPLETE' if self.started else 'TRACE_NOT_STARTED_RESTORED')
        self.proxy.save()
        self.finished = True
        self.result = {k: v for k, v in self.proxy.record.items()
                       if k not in ('log.before.txt', 'log.after.txt')}
        self.result.update(started=self.started, private_raw=True,
                           private_receipt_sha256=access.sha((self.proxy.out / 'receipt.json').read_bytes()),
                           limit='RX management/host delivery only; not TX response, RF timestamp, performance or recovery proof.')
        return self.result
