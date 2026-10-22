#!/bin/sh
# FMX-0017 bounded RAM-only hostapd admission. Invocation: sh this /tmp/owned-dir
set -eu
trap '' HUP
D=${1:?private tmpfs directory required}
case "$D" in /tmp/fmx-admitter-*) ;; *) exit 70;; esac
test -d "$D" && test ! -L "$D"
test "$(ls -ldn "$D" | awk '{print $1,$3,$4}')" = 'drwx------ 0 0'
OBJ=hostapd.phy0-ap0
case "${2:-operator}" in
 operator) IE=dd1e00156d0203020000800500340a16b0000a8000000018e8297455a2000400 ;;
 run8) IE=dd3a002722ffffff020100300206e82099038138fb0a23214c3513a4a15bfabc3725b021af9049751e2eb3835ff0ff254ecf491a67c5e7e4235a8f4a ;;
 *) exit 70 ;;
esac
WA=fc:ec:da:c2:54:0a
XC=b4:fb:e4:5c:d5:d2
MACS="$WA $XC 64:d1:54:1b:96:97 f0:9f:c2:b2:b6:ba"
listener=
listener_ticks=
reason=error
now() { cut -d. -f1 /proc/uptime; }
log() { printf '%s %s\n' "$(cat /proc/uptime | cut -d' ' -f1)" "$*" >> "$D/actions.log"; }
set_ie() {
 ubus -t 4 call "$OBJ" set_vendor_elements "{\"vendor_elements\":\"$1\"}" >/dev/null || return $?
 ubus -t 4 call "$OBJ" update_beacon >/dev/null || return $?
 if test -n "$1"; then log IE_SET_ACK; else log IE_CLEAR_ACK; fi
}
cleanup() {
 status=$?
 trap - EXIT TERM INT USR1
 set +e
 set_ie ''
 clear_rc=$?
 if test -n "$listener" && test -r "/proc/$listener/stat"; then
  if test "$(awk '{print $22}' /proc/$listener/stat)" = "$listener_ticks"; then
   kill "$listener" 2>/dev/null
   wait "$listener" 2>/dev/null
  fi
 fi
 exec 3<&-
 test ! -p "$D/events.fifo" || rm "$D/events.fifo"
 printf '%s\n' "$clear_rc" > "$D/restore.rc"
 printf '%s\n' "$status" > "$D/exit.rc"
 printf '%s\n' "$reason" > "$D/stop.reason"
 log ENDED
 exit "$status"
}
trap cleanup EXIT
trap 'reason=operator_signal; exit 0' TERM INT USR1
printf '%s %s\n' "$$" "$(awk '{print $22}' /proc/$$/stat)" > "$D/daemon.id"
mkfifo "$D/events.fifo"
ubus -t 200 subscribe "$OBJ" > "$D/events.fifo" 2> "$D/listener.stderr" &
listener=$!
listener_ticks=$(awk '{print $22}' /proc/$listener/stat)
exec 3< "$D/events.fifo"
printf '%s %s\n' "$listener" "$listener_ticks" > "$D/listener.pid"
start=$(now)
end=$((start+180))
phase=WA_DISCOVERY
set_ie "$IE"
: > "$D/ready"
log START_WA_DISCOVERY
buf=
while test "$(now)" -lt "$end"; do
 if IFS= read -r -t 1 line <&3; then
  printf '%s\n' "$line" >> "$D/events.jsonl"
  buf="$buf
$line"
  # Parse only complete JSON objects; ubus subscribe uses multiline JSON.
  case "$line" in *'}'*)
   if jsonfilter -s "$buf" -e '@' >/dev/null 2>&1; then
    address=$(jsonfilter -s "$buf" -e '@.probe.address' 2>/dev/null || true)
    target=$(jsonfilter -s "$buf" -e '@.probe.target' 2>/dev/null || true)
    if test "$phase" = WA_DISCOVERY && test "$address" = "$WA" && test "$target" = ff:ff:ff:ff:ff:ff; then
     log WA_BROADCAST_PROBE
     ucode -e 'sleep(500)'
     set_ie ''
     phase=WA_AUTH
    fi
    buf=
   fi;;
  esac
 fi
 test "${#buf}" -lt 8192 || exit 71
 kill -0 "$listener" 2>/dev/null || exit 73
 rows=$(ubus -t 4 call "$OBJ" get_clients)
 if test "$phase" = WA_AUTH; then
  authorized=$(jsonfilter -s "$rows" -e '@.clients["fc:ec:da:c2:54:0a"].authorized') || authorized=false
  if test "$authorized" = true; then
   log WA_AUTHORIZED
   set_ie "$IE"
   clear_at=$(($(now)+35))
   phase=XC_DISCOVERY
   log XC_HELD_WINDOW_35S
  fi
 fi
 if test "$phase" = XC_DISCOVERY && test "$(now)" -ge "$clear_at"; then
  set_ie ''
  phase=ALL_AUTH
  log XC_WINDOW_CLOSED
 fi
 if test "$phase" = ALL_AUTH || test "$phase" = OBSERVE; then
  all=1
  for mac in $MACS; do
   for flag in auth assoc authorized; do
    value=$(jsonfilter -s "$rows" -e "@.clients[\"$mac\"].$flag") || value=false
    test "$value" = true || all=0
   done
  done
  if test "$all" = 1; then
   if test "$phase" = ALL_AUTH; then
    : > "$D/admitted"
    phase=OBSERVE
    log FOUR_ADMITTED
   fi
  elif test "$phase" = OBSERVE; then
   reason=association_lost
   log ASSOCIATION_LOST
   exit 72
  fi
 fi
done
reason=deadline
log DEADLINE
exit 74
