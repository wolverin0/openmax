#!/bin/sh
set -eu
D=/tmp/fmx-step1c-ap-observer-dd46959f8caaed48c413806195ddfade
TOKEN=dd46959f8caaed48c413806195ddfade
test ! -L "$D"; test -d "$D"
test "$(ls -ldn "$D" | awk '{print $1,$3,$4}')" = "drwx------ 0 0"
test ! -L "$D/owner"; test "$(cat "$D/owner")" = "$TOKEN"


compat_time() {
 if test -n "${compat_end:-}"; then
  test "$(cut -d. -f1 /proc/uptime)" -lt "$((compat_end-$1))" || exit 90
 fi
}
compat_surface() {
 test "$(sha256sum /etc/init.d/wpad | awk '{print $1}')" = b6679419287fa73cfbf808a5330ee329a246af17efbb5d9ab31a1647743d3855 || exit 91
 test "$(sha256sum /etc/capabilities/wpad.json | awk '{print $1}')" = 57a727e5c7e3c6c5ce22ccd9b9f8ed2d4371c80e5d8dce3e0e67d5908657c69e || exit 91
 test "$(awk '$5=="/tmp" && $0 ~ / - tmpfs /{n++} END{print n+0}' /proc/self/mountinfo)" = 1 || exit 91
}
compat_nomount() {
 test "$(awk '$5=="/usr/sbin/wpad"{n++} END{print n+0}' /proc/self/mountinfo)" = 0 || exit 92
}
compat_file() {
 test ! -L "$D/wpad.compat" && test -f "$D/wpad.compat" || exit 93
 test "$(ls -ldn "$D/wpad.compat" | awk '{print $1,$2,$3,$4,$5}')" = '-rwxr-xr-x 1 0 0 864320' || exit 93
 test "$(sha256sum "$D/wpad.compat" | awk '{print $1}')" = e86a3aafe2ac427e01ee402d1da0df5b7f37e1dbe113bd2d90109ff5ac72ea09 || exit 93
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
 test "$(sha256sum /usr/sbin/wpad | awk '{print $1}')" = e86a3aafe2ac427e01ee402d1da0df5b7f37e1dbe113bd2d90109ff5ac72ea09 || exit 94
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
  test "$h" = f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12 -o "$h" = e86a3aafe2ac427e01ee402d1da0df5b7f37e1dbe113bd2d90109ff5ac72ea09 || exit 95
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

if test "$#" -gt 0; then
 test "$#" = 1 || exit 89
 case "$1" in
 compat.activate)

compat_surface; compat_nomount; compat_file
test -f "$D/ready"; test ! -e "$D/restored"; test ! -L "$D/restored"
test "$(cat "$D/deadline")" -ge "$(($(cut -d. -f1 /proc/uptime)+25))"
compat_end=$(($(cut -d. -f1 /proc/uptime)+22))
wanted=f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12; compat_roles; test "$compat_ready" = 1
test ! -e "$D/compat.intent"; test ! -L "$D/compat.intent"
case "${COMPAT_GUARD_PID-}" in ''|*[!0-9]*) exit 91;; esac
case "${COMPAT_GUARD_START-}" in ''|*[!0-9]*) exit 91;; esac
test "$COMPAT_GUARD_PID" -gt 0 && test "$COMPAT_GUARD_START" -gt 0 || exit 91
test ! -L "$D/guard.id" && test -f "$D/guard.id" || exit 91
read guard_p guard_s guard_extra < "$D/guard.id"
test "$guard_p $guard_s" = "$COMPAT_GUARD_PID $COMPAT_GUARD_START" && test -z "$guard_extra" || exit 91
test ! -L "$D/guard.sh" && test -f "$D/guard.sh" || exit 91
test "$(sha256sum "$D/guard.sh" | awk '{print $1}')" = f3c5c07788629586f547cb1a03b893cb42a8a827f75336b333e4916b13436446 || exit 91
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
wanted=e86a3aafe2ac427e01ee402d1da0df5b7f37e1dbe113bd2d90109ff5ac72ea09; compat_start
compat_time 0
echo COMPAT_ACTIVE_RADIO_OFF

 ;;
 compat.adopt)
test -f "$D/ready"; test ! -e "$D/restored"; test ! -L "$D/restored"
compat_surface; compat_ownedmount
wanted=e86a3aafe2ac427e01ee402d1da0df5b7f37e1dbe113bd2d90109ff5ac72ea09
compat_roles
test "$compat_ready" = 1
test "$(cat "$D/compat.intent")" = "$TOKEN"
echo COMPAT_GUARD_ADOPTED

 ;;
 compat.verify)

compat_surface; compat_nomount
test "$(sha256sum /usr/sbin/wpad | awk '{print $1}')" = f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12
wanted=f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12; compat_roles; test "$compat_ready" = 1
if test -e "$D/compat.intent" || test -L "$D/compat.intent"; then
 test ! -L "$D/compat.restored" && test -f "$D/compat.restored"
 test "$(cat "$D/compat.restored")" = "$TOKEN"
fi
test -f "$D/restored"; test ! -L "$D/restored"
read p ticks < "$D/guard.id"
if test -r /proc/$p/stat && test "$(awk '{print $22}' /proc/$p/stat)" = "$ticks" && test "$(awk '{print $3}' /proc/$p/stat)" != Z; then exit 99; fi
echo COMPAT_STOCK_RESTORED_GUARD_ENDED

 ;;
 *) exit 89;;
 esac
 exit 0
fi
wifi down radio0
if ! mkdir "$D/restoring"; then
 for n in 1 2 3 4; do test -f "$D/restored" && exit 0; sleep 1; done
 exit 80
fi
trap 'rmdir "$D/restoring"' EXIT
test "$(sha256sum /etc/config/wireless | awk '{print $1}')" = f8e679e4639fc5c26b6c96d646e1e56b57fb58064a75eb215c34ad0462285a6a
test "$(sha256sum /etc/config/network | awk '{print $1}')" = d273ab6bece9a950b119a4fc6c0f6f076543e4a88ab7346760e02d211b403015
changes=$(uci changes wireless)
printf '%s
' "$changes" | while IFS= read -r row; do
 case "$row" in ""|"wireless.radio0.disabled='0'"|"wireless.radio0.txpower='0'"|"wireless.default_radio0.wds='1'"|"wireless.default_radio0.encryption='none'"|"wireless.default_radio0.encryption='psk2'") ;; *) exit 81;; esac
done
test "$(uci -q get wireless.radio0.disabled)" = 0 -o "$(uci -q get wireless.radio0.disabled)" = 1
test "$(uci -q get wireless.radio0.txpower)" = 0 -o "$(uci -q get wireless.radio0.txpower)" = 18
if printf '%s
' "$changes" | grep -q "^wireless.radio0.disabled="; then uci revert wireless.radio0.disabled; fi
if printf '%s
' "$changes" | grep -q "^wireless.radio0.txpower="; then uci revert wireless.radio0.txpower; fi
if printf '%s
' "$changes" | grep -q "^wireless.default_radio0.wds="; then uci revert wireless.default_radio0.wds; fi
if printf '%s
' "$changes" | grep -q "^wireless.default_radio0.encryption="; then uci revert wireless.default_radio0.encryption; fi
test -z "$(uci changes wireless)"
test "$(uci -q get wireless.default_radio0.wds)" = 0
test "$(uci -q get wireless.radio0.disabled)" = 1
test "$(uci -q get wireless.radio0.txpower)" = 18
ubus call network reload >/dev/null
wifi down radio0
fmx_wireless=$(ubus -t 4 call network.wireless status)
test "$(jsonfilter -s "$fmx_wireless" -e '@.radio0.up')" = false
fmx_devs=$(iw dev)
test -z "$(printf "%s\n" "$fmx_devs" | awk '$1=="Interface" {print $2}')"
fmx_tables=$(nft list tables)
if printf "%s\n" "$fmx_tables" | grep -Fx "table bridge fmx_preprod_dd46959f8caaed48c413806195ddfade" >/dev/null; then
 fmx_table=$(nft -j list table bridge fmx_preprod_dd46959f8caaed48c413806195ddfade)
 fmx_owner=$(jsonfilter -s "$fmx_table" -e '@.nftables[*].table.comment')
 test "$fmx_owner" = dd46959f8caaed48c413806195ddfade
 nft delete table bridge fmx_preprod_dd46959f8caaed48c413806195ddfade
fi
if ip -4 addr show dev br-lan | grep -q 'inet 10.99.0.1/24 '; then ip addr del 10.99.0.1/24 dev br-lan; fi
if ip -4 addr show dev br-lan | grep -q 'inet 10.99.0.1/'; then exit 82; fi
test "$(sha256sum /etc/config/wireless | awk '{print $1}')" = f8e679e4639fc5c26b6c96d646e1e56b57fb58064a75eb215c34ad0462285a6a

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
  test "$(sha256sum /usr/sbin/wpad | awk '{print $1}')" = f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12 || exit 98
  wanted=f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12; compat_start
  umask 077; (set -C; printf '%s\n' "$TOKEN" > "$D/compat.restored")
 fi
fi
compat_nomount
test "$(sha256sum /usr/sbin/wpad | awk '{print $1}')" = f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12 || exit 98
wanted=f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12; compat_roles; test "$compat_ready" = 1 || exit 98

: > "$D/restored"
echo RESTORE_OK
