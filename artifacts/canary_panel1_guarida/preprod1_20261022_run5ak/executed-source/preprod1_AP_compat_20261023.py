"""Bench-only RAM wpad lifecycle using the already owned AP window guard.

No connections or actions on import. The coordinator supplies a pinned client,
the configured frozen AP helper, and its bounded RPC function. This is not a
deployment driver; the original radio/config restoration runs before this hook.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import threading
import time

STOCK_SHA = 'f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12'
STOCK_BYTES = 864296
COMPAT_SHA = '99122e15246efc0006c82fc23a8667f7ccdcdf9d15bd2f46edc7e95c0f7b6923'
COMPAT_BYTES = 864312
INIT_SHA = 'b6679419287fa73cfbf808a5330ee329a246af17efbb5d9ab31a1647743d3855'
CAPS_SHA = '57a727e5c7e3c6c5ce22ccd9b9f8ed2d4371c80e5d8dce3e0e67d5908657c69e'
CLEANUP_NAMES = ['wpad.compat', 'compat.intent', 'compat.mount.id', 'compat.restored']
STREAM_SECONDS = 20


def require(value, gate):
    if not value:
        raise RuntimeError(gate)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def functions():
    """Bounded shell primitives; only the named procd wpad service is stopped."""
    return r'''
compat_time() {
 if test -n "${compat_end:-}"; then
  test "$(cut -d. -f1 /proc/uptime)" -lt "$((compat_end-$1))" || exit 90
 fi
}
compat_surface() {
 test "$(sha256sum /etc/init.d/wpad | awk '{print $1}')" = INIT_SHA || exit 91
 test "$(sha256sum /etc/capabilities/wpad.json | awk '{print $1}')" = CAPS_SHA || exit 91
 test "$(awk '$5=="/tmp" && $0 ~ / - tmpfs /{n++} END{print n+0}' /proc/self/mountinfo)" = 1 || exit 91
}
compat_nomount() {
 test "$(awk '$5=="/usr/sbin/wpad"{n++} END{print n+0}' /proc/self/mountinfo)" = 0 || exit 92
}
compat_file() {
 test ! -L "$D/wpad.compat" && test -f "$D/wpad.compat" || exit 93
 test "$(ls -ldn "$D/wpad.compat" | awk '{print $1,$2,$3,$4,$5}')" = '-rwxr-xr-x 1 0 0 COMPAT_BYTES' || exit 93
 test "$(sha256sum "$D/wpad.compat" | awk '{print $1}')" = COMPAT_SHA || exit 93
}
compat_ownedmount() {
 compat_file
 test "$(awk '$5=="/usr/sbin/wpad"{n++} END{print n+0}' /proc/self/mountinfo)" = 1 || exit 94
 row=$(awk '$5=="/usr/sbin/wpad"{print $1,$3,$4}' /proc/self/mountinfo)
 set -- $row; test "$#" = 3 || exit 94
 mount_id=$1
 test "$3" = "${D#/tmp}/wpad.compat" || exit 94
 test "$2" = "$(awk '$5=="/tmp"{print $3}' /proc/self/mountinfo)" || exit 94
 test "$(ls -idnL /usr/sbin/wpad | awk '{print $1}')" = "$(ls -idnL "$D/wpad.compat" | awk '{print $1}')" || exit 94
 test "$(sha256sum /usr/sbin/wpad | awk '{print $1}')" = COMPAT_SHA || exit 94
 if test -e "$D/compat.mount.id" || test -L "$D/compat.mount.id"; then
  test ! -L "$D/compat.mount.id" && test -f "$D/compat.mount.id" || exit 94
  test "$(ls -ldn "$D/compat.mount.id" | awk '{print $1,$2,$3,$4}')" = '-rw------- 1 0 0' || exit 94
  test "$(cat "$D/compat.mount.id")" = "$mount_id" || exit 94
 fi
}
compat_status() {
 test "$(awk '$1=="Uid:"{print $2,$3,$4,$5}' /proc/$p/status)" = "$uid $uid $uid $uid" || exit 95
 test "$(awk '$1=="Gid:"{print $2,$3,$4,$5}' /proc/$p/status)" = "$uid $uid $uid $uid" || exit 95
 test "$(awk '$1=="NoNewPrivs:"{print $2}' /proc/$p/status)" = "$nnp" || exit 95
 test "$(awk '$1=="CapEff:"{print $2}' /proc/$p/status)" = "$caps" || exit 95
 test "$(awk '$1=="CapBnd:"{print $2}' /proc/$p/status)" = "$caps" || exit 95
 test "$(awk '{print $3}' /proc/$p/stat)" != Z || exit 95
}
compat_roles() {
 compat_time 3
 j=$(ubus -t 3 call service list '{"name":"wpad","verbose":true}') || exit 95
 jsonfilter -s "$j" -e '@' >/dev/null || exit 95
 if test "$(printf '%s' "$j" | tr -d ' \r\n\t')" = '{}'; then hp=; sp=; all=
 else
  instances=$(jsonfilter -s "$j" -e '@.wpad.instances') || exit 95
  case "$instances" in \{*\}) ;; *) exit 95;; esac
  hp=$(jsonfilter -s "$j" -e '@.wpad.instances.hostapd.pid' || :)
  sp=$(jsonfilter -s "$j" -e '@.wpad.instances.supplicant.pid' || :)
  all=$(jsonfilter -s "$j" -e '@.wpad.instances[*].pid' || :)
 fi
 parents=0; children=0; hc=0; sc=0
 for p in $all; do
  case "$p" in ''|*[!0-9]*|0) exit 95;; esac
  test "$p" = "$hp" -o "$p" = "$sp" || exit 95
 done
 test -z "$hp" -o "$hp" != "$sp" || exit 95
 for role in hostapd supplicant; do
  if test "$role" = hostapd; then p=$hp; name=hostapd; args='/usr/sbin/hostapd|-s|-g|/var/run/hostapd/global|'
  else p=$sp; name=wpa_supplicant; args='/usr/sbin/wpa_supplicant|-n|-s|-g|/var/run/wpa_supplicant/global|'; fi
  if test -z "$p"; then continue; fi
  for pair in user:network group:network no_new_privs:true capabilities:/etc/capabilities/wpad.json jail.name:$name; do
   field=${pair%%:*}; value=${pair#*:}
   test "$(jsonfilter -s "$j" -e "@.wpad.instances.$role.$field")" = "$value" || exit 95
  done
  for field in procfs sysfs ubus log ronly netns userns cgroupsns console; do
   test "$(jsonfilter -s "$j" -e "@.wpad.instances.$role.jail.$field")" = false || exit 95
  done
  test "$(jsonfilter -s "$j" -e "@.wpad.instances.$role.command[*]" | tr '\n' '|')" = "$args" || exit 95
  if test ! -r /proc/$p/stat; then continue; fi
  ticks=$(awk '{print $22}' /proc/$p/stat)
  test "$(readlink /proc/$p/exe)" = /sbin/ujail || exit 95
  test "$(tr '\000' '|' < /proc/$p/cmdline)" = "/sbin/ujail|-t|5|-n|$name|-U|network|-G|network|-C|/etc/capabilities/wpad.json|-c|--|$args" || exit 95
  uid=0; nnp=0; caps=000001ffffffffff; compat_status
  test "$(awk '{print $22}' /proc/$p/stat)" = "$ticks" || exit 95
  parents=$((parents+1))
 done
 seen=' '
 for p in $(pidof hostapd 2>/dev/null || :) $(pidof wpa_supplicant 2>/dev/null || :) $(pidof wpad 2>/dev/null || :); do
  case "$seen" in *" $p "*) continue;; esac; seen="$seen$p "
  test "$p" != "$hp" -a "$p" != "$sp" || continue
  ticks=$(awk '{print $22}' /proc/$p/stat)
  exe=$(readlink /proc/$p/exe)
  test "$exe" = /usr/sbin/wpad -o "$exe" = "$D/wpad.compat" || exit 95
  args=$(tr '\000' '|' < /proc/$p/cmdline)
  case "$args" in
   '/usr/sbin/hostapd|-s|-g|/var/run/hostapd/global|') parent=$hp; hc=$((hc+1));;
   '/usr/sbin/wpa_supplicant|-n|-s|-g|/var/run/wpa_supplicant/global|') parent=$sp; sc=$((sc+1));;
   *) exit 95;;
  esac
  test -n "$parent" && test -r /proc/$parent/stat || exit 95
  test "$(awk '$1=="PPid:"{print $2}' /proc/$p/status)" = "$parent" || exit 95
  uid=101; nnp=1; caps=0000000000003000; compat_status
  h=$(sha256sum /proc/$p/exe | awk '{print $1}')
  test "$h" = STOCK_SHA -o "$h" = COMPAT_SHA || exit 95
  if test -n "$wanted"; then test "$h" = "$wanted" || exit 95; fi
  test "$(awk '{print $22}' /proc/$p/stat)" = "$ticks" || exit 95
  children=$((children+1))
 done
 test "$hc" -le 1 -a "$sc" -le 1 || exit 95
 compat_ready=0
 if test "$parents" = 2 -a "$children" = 2; then compat_ready=1; fi
 compat_time 0
}
compat_stop() {
 wanted=; compat_roles
 compat_time 6
 /etc/init.d/wpad stop
 stop_end=$(($(cut -d. -f1 /proc/uptime)+6))
 for n in 1 2 3 4 5 6; do
  compat_time 0
  test "$(cut -d. -f1 /proc/uptime)" -lt "$stop_end" || exit 96
  if test -z "$(pidof hostapd 2>/dev/null || :)$(pidof wpa_supplicant 2>/dev/null || :)$(pidof wpad 2>/dev/null || :)"; then return; fi
  sleep 1
 done
 exit 96
}
compat_start() {
 compat_time 6
 /etc/init.d/wpad start
 start_end=$(($(cut -d. -f1 /proc/uptime)+6))
 for n in 1 2 3 4 5 6; do
  test "$(cut -d. -f1 /proc/uptime)" -lt "$start_end" || exit 97
  compat_roles
  test "$(cut -d. -f1 /proc/uptime)" -lt "$start_end" || exit 97
  if test "$compat_ready" = 1; then return; fi
  sleep 1
 done
 exit 97
}
'''.replace('INIT_SHA', INIT_SHA).replace('CAPS_SHA', CAPS_SHA).replace('STOCK_SHA', STOCK_SHA).replace('COMPAT_SHA', COMPAT_SHA).replace('COMPAT_BYTES', str(COMPAT_BYTES))


def restoration():
    return functions() + r'''
compat_surface
if test -e "$D/compat.intent" || test -L "$D/compat.intent"; then
 test ! -L "$D/compat.intent" && test -f "$D/compat.intent" || exit 98
 test "$(cat "$D/compat.intent")" = "$TOKEN" || exit 98
 test "$(ls -ldn "$D/compat.intent" | awk '{print $1,$2,$3,$4}')" = '-rw------- 1 0 0' || exit 98
 if test -e "$D/compat.restored" || test -L "$D/compat.restored"; then
  test ! -L "$D/compat.restored" && test "$(cat "$D/compat.restored")" = "$TOKEN" || exit 98
 else
  compat_stop
  if awk '$5=="/usr/sbin/wpad"{found=1} END{exit !found}' /proc/self/mountinfo; then
   compat_ownedmount
   umount /usr/sbin/wpad
  fi
  compat_nomount
  test "$(sha256sum /usr/sbin/wpad | awk '{print $1}')" = STOCK_SHA || exit 98
  wanted=STOCK_SHA; compat_start
  umask 077; (set -C; printf '%s\n' "$TOKEN" > "$D/compat.restored")
 fi
fi
compat_nomount
test "$(sha256sum /usr/sbin/wpad | awk '{print $1}')" = STOCK_SHA || exit 98
wanted=STOCK_SHA; compat_roles; test "$compat_ready" = 1 || exit 98
'''.replace('STOCK_SHA', STOCK_SHA)


class Compat:
    cleanup_names = CLEANUP_NAMES

    def __init__(self, helper, out, rpc, binary_path):
        require(re.fullmatch(r'/tmp/fmx-[A-Za-z0-9_-]+', helper.DIR), 'COMPAT_DIR_UNSAFE')
        self.helper, self.rpc = helper, rpc
        self.out = Path(out)
        self.out.mkdir(mode=0o700, parents=True, exist_ok=False)
        self.binary_path = Path(binary_path)
        require(self.binary_path.is_file() and not self.binary_path.is_symlink(), 'COMPAT_BINARY_NOT_REGULAR')
        self.binary = self.binary_path.read_bytes()
        require(len(self.binary) == COMPAT_BYTES and sha(self.binary) == COMPAT_SHA, 'COMPAT_BINARY_CHANGED')
        self.prepared = self.created = self.activated = False
        self.record = dict(status='LOCAL_PREPARED_NO_DEVICE_ACTION', errors=[], execution_driver='root_injected_client',
                           binary_sha256=COMPAT_SHA, binary_bytes=COMPAT_BYTES, prepared=False, created=False)
        self.original_prepare = helper.prepare
        original_restore = helper.restore_body
        source = original_restore()
        marker = ': > "$D/restored"\n'
        require(source.count(marker) == 1, 'RESTORE_MARKER_AMBIGUOUS')
        require('wifi down radio0' in source[:source.index(marker)], 'ORIGINAL_RADIO_OFF_MISSING')
        dispatch = functions() + '\nif test "$#" -gt 0; then\n test "$#" = 1 || exit 89\n case "$1" in\n'
        for mode in ['activate', 'adopt', 'verify']:
            dispatch += ' compat.' + mode + ')\n' + self.mode_body(mode) + '\n ;;\n'
        dispatch += ' *) exit 89;;\n esac\n exit 0\nfi\n'
        wrapped = source.replace(marker, restoration()[len(functions()):] + '\n' + marker)
        wrapped = wrapped.replace('wifi down radio0\n', dispatch + 'wifi down radio0\n', 1)
        helper.restore_body = lambda: wrapped
        prepare = self.original_prepare()
        tail = ''
        for name, body in [('restore.sh', wrapped), ('guard.sh', helper.guard_body())]:
            tail += 'printf %s ' + shlex.quote(body) + ' > ' + helper.DIR + '/' + name + '\n'
        self.guard_dispatch = ('/bin/sh ' + helper.DIR + '/guard.sh </dev/null >' +
                               helper.DIR + '/guard.log 2>&1 &\necho GUARD_DISPATCHED')
        tail += self.guard_dispatch
        require(prepare.endswith(tail), 'ORIGINAL_PREPARE_TAIL_CHANGED')
        self.prepare_prefix = prepare[:-len(tail)]
        require(0 < len(self.prepare_prefix.encode()) <= 4096, 'PREPARE_PREFIX_BOUND')
        self.record.update(restore_sha256=sha(wrapped.encode()), prepare_source_sha256=sha(prepare.encode()),
                           prepare_source_bytes=len(prepare.encode()), prepare_command_sha256=sha(self.prepare_prefix.encode()),
                           prepare_command_bytes=len(self.prepare_prefix.encode()), exec_limit=4096,
                           script_transport='verified_original_prefix_512_octals_short_guard_dispatch')
        self.save()

    def save(self):
        value = json.dumps(self.record, indent=2) + '\n'
        temporary = self.out / 'receipt.tmp'
        with temporary.open('w', encoding='utf8') as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(self.out / 'receipt.json')

    def checked(self, ap, command, timeout=25):
        require(len(command.encode()) <= 4096, 'RPC_COMMAND_BOUND')
        result = self.rpc(ap, command, timeout=timeout)
        if isinstance(result, dict):
            output, error = result['stdout'], result['stderr']
            output = output.encode() if isinstance(output, str) else output
            error = error.encode() if isinstance(error, str) else error
            require(result['exit_code'] == 0 and not error, 'COMPAT_RPC_FAILED')
        else:
            output = result
        require(isinstance(output, bytes) and len(output) <= 65536, 'COMPAT_RPC_OUTPUT_BOUND')
        return output

    def prefix(self):
        return 'set -eu\n' + self.helper.header() + self.helper.file_guards()

    def stream(self, ap, command, payload, expected):
        """Bounded existing SSH stdin path; no large Dropbear exec argument."""
        end = time.monotonic() + STREAM_SECONDS
        channel = None
        expired = threading.Event()
        output, error = bytearray(), bytearray()

        def remaining():
            value = end - time.monotonic()
            require(value > 0 and not expired.is_set(), 'COMPAT_UPLOAD_DEADLINE')
            return value

        def terminate_owned_channel():
            expired.set()
            if channel is not None:
                channel.close()

        require(len(command.encode()) <= 4096 and len(payload) <= COMPAT_BYTES, 'STREAM_INPUT_BOUND')
        timer = threading.Timer(STREAM_SECONDS, terminate_owned_channel)
        timer.daemon = True
        timer.start()
        try:
            channel = ap.get_transport().open_session(timeout=remaining())
            channel.settimeout(remaining())
            channel.exec_command(command)
            remaining()  # exec ACK ignores Channel.settimeout; the timer closes it.
            offset = 0
            while offset < len(payload):
                channel.settimeout(remaining())
                sent = channel.send(payload[offset:offset + 65536])
                require(0 < sent <= min(65536, len(payload) - offset), 'UPLOAD_SHORT_SEND')
                offset += sent
                remaining()
            channel.shutdown_write()
            while True:
                remaining()
                if channel.recv_ready():
                    output.extend(channel.recv(4097))
                if channel.recv_stderr_ready():
                    error.extend(channel.recv_stderr(4097))
                require(len(output) <= 4096 and len(error) <= 4096, 'UPLOAD_OUTPUT_BOUND')
                if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():
                    break
                time.sleep(0.01)
            require(channel.recv_exit_status() == 0 and not error and
                    bytes(output).endswith(expected), 'COMPAT_STREAM_UNVERIFIED')
            remaining()
            return bytes(output)
        finally:
            timer.cancel()
            if channel is not None:
                channel.close()

    def stage(self, ap):
        """One bounded stdin transfer; a timeout preserves the nonexecutable file."""
        command = (self.prefix() + 'test ! -e "$D/wpad.compat"; test ! -L "$D/wpad.compat"\n'
                   'umask 077\nset -C\ncat > "$D/wpad.compat"\n'
                   'test "$(wc -c < "$D/wpad.compat")" = ' + str(COMPAT_BYTES) + '\n'
                   'test "$(sha256sum "$D/wpad.compat" | awk \'{print $1}\')" = ' + COMPAT_SHA + '\n'
                   'chmod 0755 "$D/wpad.compat"\necho COMPAT_UPLOAD_VERIFIED\n')
        self.record['upload_intent'] = True
        self.save()
        self.stream(ap, command, self.binary, b'COMPAT_UPLOAD_VERIFIED\n')
        self.record['upload_verified'] = True
        self.save()

    def stock_ready(self, ap):
        # Complete procd/jail/child proof runs in the guarded activation script,
        # before intent/stop. Here no owned script exists yet: only source pins.
        source = ('set -eu\n'
                  'test "$(sha256sum /etc/init.d/wpad | awk \'{print $1}\')" = ' + INIT_SHA + '\n'
                  'test "$(sha256sum /etc/capabilities/wpad.json | awk \'{print $1}\')" = ' + CAPS_SHA + '\n'
                  'test "$(awk \'$5=="/usr/sbin/wpad"{n++} END{print n+0}\' /proc/self/mountinfo)" = 0\n'
                  'test "$(sha256sum /usr/sbin/wpad | awk \'{print $1}\')" = ' + STOCK_SHA +
                  '\necho COMPAT_STOCK_READY\n')
        return self.checked(ap, source)

    def prepare_guard(self, ap):
        self.checked(ap, self.prepare_prefix)
        for name, body in [('restore.sh', self.helper.restore_body()), ('guard.sh', self.helper.guard_body())]:
            data = body.encode()
            require(len(data) <= 32768, 'OWNED_SCRIPT_SOURCE_BOUND')
            path = '"$D/' + name + '"'
            base = 'set -eu\n' + self.helper.header()
            self.checked(ap, base + 'test ! -e ' + path + '; test ! -L ' + path +
                         '\numask 077\nset -C\nprintf %s "" > ' + path + '\n')
            for offset in range(0, len(data), 512):
                octals = ''.join('\\%03o' % value for value in data[offset:offset + 512])
                self.checked(ap, base + 'test ! -L ' + path + '; test -f ' + path + '\n'
                             "printf '" + octals + "' >> " + path + '\n')
            self.checked(ap, base + 'test "$(wc -c < ' + path + ')" = ' + str(len(data)) + '\n'
                         'test "$(sha256sum ' + path + ' | awk \'{print $1}\')" = ' + sha(data) + '\n')
        self.checked(ap, self.prefix() + self.guard_dispatch)

    def prepare_and_activate(self, ap):
        require(not self.prepared, 'COMPAT_SINGLE_USE')
        try:
            self.helper.off(ap)
            self.stock_ready(ap)
            self.prepared = self.created = True  # Reserve before RPC: ACK may be lost.
            self.record.update(prepared=True, created=True, resource_intent=True, status='GUARD_CREATION_INTENT')
            self.save()
            self.prepare_guard(ap)
            guard = None
            for _ in range(4):
                try:
                    guard = self.helper.guard_identity(ap)
                    break
                except RuntimeError:
                    time.sleep(0.25)
            require(guard is not None, 'COMPAT_EXISTING_GUARD_NOT_READY')
            self.record['guard_pid_start_deadline'] = guard
            self.save()
            self.stage(ap)
            require(all(type(value) is int and value > 0 for value in guard[:2]) and len(guard) >= 2,
                    'COMPAT_GUARD_ID_INVALID')
            activation = (self.prefix() + 'COMPAT_GUARD_PID=' + str(guard[0]) +
                          ' COMPAT_GUARD_START=' + str(guard[1]) +
                          ' /bin/sh "$D/restore.sh" compat.activate\n')
            self.checked(ap, activation, timeout=25)
            self.helper.off(ap)
            self.activated = True
            adoption = self.prefix() + '/bin/sh "$D/restore.sh" compat.adopt\n'
            require(len(adoption.encode()) <= 4096, 'ADOPTION_COMMAND_BOUND')
            self.helper.prepare = lambda: adoption
            self.record.update(status='COMPAT_ACTIVE_RADIO_OFF', adoption_command_sha256=sha(adoption.encode()),
                               adoption_command_bytes=len(adoption.encode()), activated=True)
            self.save()
            return self.record
        except BaseException as error:
            self.record['status'] = 'INCOMPLETE_COMPAT_LIFECYCLE'
            self.record['errors'].append(type(error).__name__ + ':' + str(error)[:200])
            self.save()
            raise

    def mode_body(self, mode):
        if mode == 'activate':
            return r'''
compat_surface; compat_nomount; compat_file
test -f "$D/ready"; test ! -e "$D/restored"; test ! -L "$D/restored"
test "$(cat "$D/deadline")" -ge "$(($(cut -d. -f1 /proc/uptime)+25))"
compat_end=$(($(cut -d. -f1 /proc/uptime)+22))
wanted=STOCK_SHA; compat_roles; test "$compat_ready" = 1
test ! -e "$D/compat.intent"; test ! -L "$D/compat.intent"
case "${COMPAT_GUARD_PID-}" in ''|*[!0-9]*) exit 91;; esac
case "${COMPAT_GUARD_START-}" in ''|*[!0-9]*) exit 91;; esac
test "$COMPAT_GUARD_PID" -gt 0 && test "$COMPAT_GUARD_START" -gt 0 || exit 91
test ! -L "$D/guard.id" && test -f "$D/guard.id" || exit 91
read guard_p guard_s guard_extra < "$D/guard.id"
test "$guard_p $guard_s" = "$COMPAT_GUARD_PID $COMPAT_GUARD_START" && test -z "$guard_extra" || exit 91
test ! -L "$D/guard.sh" && test -f "$D/guard.sh" || exit 91
test "$(sha256sum "$D/guard.sh" | awk '{print $1}')" = GUARD_SHA || exit 91
test -r /proc/$guard_p/stat || exit 91
test "$(awk '{print $22}' /proc/$guard_p/stat)" = "$guard_s" || exit 91
case "$(awk '{print $3}' /proc/$guard_p/stat)" in ''|Z|X) exit 91;; esac
test "$(tr '\000' ' ' < /proc/$guard_p/cmdline)" = "/bin/sh $D/guard.sh " || exit 91
test "$(awk '{print $22}' /proc/$guard_p/stat)" = "$guard_s" || exit 91
umask 077; (set -C; printf '%s\n' "$TOKEN" > "$D/compat.intent")
compat_stop
compat_nomount
mount -o bind "$D/wpad.compat" /usr/sbin/wpad
compat_ownedmount
umask 077; (set -C; printf '%s\n' "$mount_id" > "$D/compat.mount.id")
wanted=COMPAT_SHA; compat_start
compat_time 0
echo COMPAT_ACTIVE_RADIO_OFF
'''.replace('STOCK_SHA', STOCK_SHA).replace('COMPAT_SHA', COMPAT_SHA).replace(
                'GUARD_SHA', sha(self.helper.guard_body().encode()))
        if mode == 'adopt':
            return ('test -f "$D/ready"; test ! -e "$D/restored"; '
                       'test ! -L "$D/restored"\ncompat_surface; compat_ownedmount\n'
                       'wanted=' + COMPAT_SHA + '\ncompat_roles\ntest "$compat_ready" = 1\n'
                       'test "$(cat "$D/compat.intent")" = "$TOKEN"\necho COMPAT_GUARD_ADOPTED\n')
        require(mode == 'verify', 'COMPAT_MODE_UNKNOWN')
        return r'''
compat_surface; compat_nomount
test "$(sha256sum /usr/sbin/wpad | awk '{print $1}')" = STOCK_SHA
wanted=STOCK_SHA; compat_roles; test "$compat_ready" = 1
if test -e "$D/compat.intent" || test -L "$D/compat.intent"; then
 test ! -L "$D/compat.restored" && test -f "$D/compat.restored"
 test "$(cat "$D/compat.restored")" = "$TOKEN"
fi
test -f "$D/restored"; test ! -L "$D/restored"
read p ticks < "$D/guard.id"
if test -r /proc/$p/stat && test "$(awk '{print $22}' /proc/$p/stat)" = "$ticks" && test "$(awk '{print $3}' /proc/$p/stat)" != Z; then exit 99; fi
echo COMPAT_STOCK_RESTORED_GUARD_ENDED
'''.replace('STOCK_SHA', STOCK_SHA)

    def verify_restored(self, ap):
        self.helper.off(ap)
        command = self.prefix() + '/bin/sh "$D/restore.sh" compat.verify\n'
        self.checked(ap, command)
        require(not self.record.get('upload_intent') or self.record.get('upload_verified'), 'UPLOAD_COMPLETION_UNKNOWN_PRESERVE_RAM')
        self.record.update(status='PASS_COMPAT_STOCK_RESTORED', stock_sha256=STOCK_SHA,
                           stock_service_healthy=True, owned_mount_absent=True, guard_ended_verified=True)
        self.save()
        return self.record

    def restore_if_needed(self, ap):
        """No foreign cleanup. Incomplete guard creation remains HOLD for root."""
        self.helper.client_pin(ap)
        probe = ('set -eu\nif test ! -e ' + shlex.quote(self.helper.DIR) +
                 ' && test ! -L ' + shlex.quote(self.helper.DIR) + '; then echo ABSENT; else\n' +
                 self.helper.header() + 'echo OWNED\nfi\n')
        state = self.checked(ap, probe).strip()
        require(state in [b'ABSENT', b'OWNED'], 'COMPAT_RESOURCE_STATE_UNKNOWN')
        if state == b'ABSENT':
            require(not self.activated, 'ACTIVE_COMPAT_DIR_VANISHED')
            self.helper.off(ap)
            self.stock_ready(ap)
            self.record['absence_and_stock_verified'] = True
            self.save()
            return dict(status='PASS_NO_COMPAT_REMOTE_RESOURCES_CREATED')
        self.helper.restore(ap)
        return self.verify_restored(ap)
