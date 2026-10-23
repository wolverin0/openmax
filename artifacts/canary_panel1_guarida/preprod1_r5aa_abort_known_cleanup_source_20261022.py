rocket = access.load('root_step1c_rocket_observer_20261021.py').connect()
script = (RUN / 'executed-source/Rocket_guard.sh').read_text(encoding='utf8')
expected = '/bin/sh\n-c\n' + script.rstrip('\n')
command = 'set -eu\nfound=\nfor p in /proc/[0-9]*; do\n test -r "$p/cmdline" || continue\n args=$(tr \'\\000\' \'\\n\' < "$p/cmdline")\n test "$args" = ' + shlex.quote(expected) + ' || continue\n test -z "$found"\n found=${p##*/}\ndone\nif test -n "$found"; then printf "OWNED_GUARD %s %s\\n" "$found" "$(awk \'{print $22}\' /proc/$found/stat)"; kill -USR1 "$found"; else echo OWNED_GUARD_ALREADY_ENDED; fi\n'
record['Rocket_guard_signal'] = remote(rocket, command, timeout=12)
time.sleep(3)
identity = record['Rocket_guard_signal']['stdout'].split()
if len(identity) == 3 and identity[0] == 'OWNED_GUARD':
    pid, ticks = identity[1:]
    require(pid.isdigit() and ticks.isdigit(), 'ROCKET_GUARD_ID')
    record['Rocket_guard_ended'] = remote(rocket, 'if test -r /proc/' + pid + '/stat && test "$(awk \'{print $22}\' /proc/' + pid + '/stat)" = ' + ticks + ' && test "$(awk \'{print $3}\' /proc/' + pid + '/stat)" != Z; then echo LIVE; else echo ENDED; fi')['stdout'].strip()
    require(record['Rocket_guard_ended'] == 'ENDED', 'ROCKET_GUARD_STILL_LIVE')
old = access.load('root_multi_cpe_trial_20261022.py')
after = {k: remote(rocket, cmd)['stdout'] for k, cmd in {'hashes': 'md5sum ' + old.HASH_FILES, 'bridge': 'brctl show; ifconfig br0 | head -n 4', 'addresses': 'ip -4 addr show dev br0; route -n', 'rules': 'ebtables -L FORWARD'}.items()}
require(after == rec['rocket_baseline'], 'ROCKET_EXACT_RESTORE_CHANGED')
record['rocket_restoration'] = dict(status='PASS_EXACT_HASHES_RULES_BRIDGE_ORDERED_IPv4_ROUTES', evidence=after)
for d, token, inode, digest, mtime in rows:
    command = 'set -eu\nd=' + shlex.quote(d) + '\ntest ! -L "$d"\ntest "$(ls -lidn "$d" | awk \'{print $1,$2,$4,$5}\')" = ' + shlex.quote(inode) + '\ntest "$(cat "$d/owner")" = ' + token + '\ntest "$(sha256sum "$d/cli" | cut -d\' \' -f1)" = ' + digest + '\ntest "$(ls -A "$d" | sort | tr \'\\n\' \' \')" = "cli owner "\ntest ! -L "$d/cli"; test ! -L "$d/owner"\nrm "$d/cli" "$d/owner"\nrmdir "$d"\ntest ! -e "$d"\necho STAGED_ONLY_RAM_REMOVED\n'
    record['events'].append(dict(action='staged_only_RAM_cleanup', directory=d, evidence=remote(ap, command)))
record['AP_restoration'] = helper.restore(ap)
require(remote(ap, 'nft list tables')['stdout'] == rec['bridge_isolation']['original_tables'], 'AP_NFT_NOT_RESTORED')
command = 'set -eu\n' + helper.header() + helper.file_guards()
for file in ['owner', 'ready', 'guard.id', 'deadline', 'guard.sh', 'restore.sh', 'guard.log', 'restore.log', 'restored']:
    command += 'test ! -L "$D/' + file + '"; rm -f "$D/' + file + '"\n'
record['AP_guard_RAM_cleanup'] = remote(ap, command + 'rmdir "$D"\ntest ! -e "$D"\necho AP_OWNED_RAM_REMOVED\n')
