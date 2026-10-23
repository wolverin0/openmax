#!/bin/sh
# Only the exact five-unit bench. All admission/recovery decisions are AP-local.
set -eu
trap '' HUP
D=${1:?owned RAM directory required}
case "$D" in /tmp/fmx-admitter-*) ;; *) exit 70;; esac
test -d "$D" && test ! -L "$D"
test "$(ls -ldn "$D" | awk '{print $1,$3,$4}')" = 'drwx------ 0 0'
OBJ=hostapd.phy0-ap0
IE=dd3a002722ffffff020100300206e82099038138fb0a23214c3513a4a15bfabc3725b021af9049751e2eb3835ff0ff254ecf491a67c5e7e4235a8f4a
WA=fc:ec:da:c2:54:0a
XC=b4:fb:e4:5c:d5:d2
MACS="$WA $XC 64:d1:54:1b:96:97 f0:9f:c2:b2:b6:ba"
listener=; listener_ticks=; reason=error
now() { cut -d. -f1 /proc/uptime; }
log() { printf '%s %s\n' "$(cut -d' ' -f1 /proc/uptime)" "$*" >> "$D/actions.log"; }
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
ubus -t 1000 subscribe "$OBJ" > "$D/events.fifo" 2> "$D/listener.stderr" &
listener=$!
listener_ticks=$(awk '{print $22}' /proc/$listener/stat)
exec 3< "$D/events.fifo"
: > "$D/events.jsonl"
printf '%s %s\n' "$listener" "$listener_ticks" > "$D/listener.pid"
collect() {
 rows=$(ubus -t 4 call "$OBJ" get_clients)
 object=$(jsonfilter -s "$rows" -e '@.clients')
 case "$object" in \{*\}) ;; *) reason=invalid_clients; exit 71;; esac
 GOOD=
 for mac in $MACS; do
  ok=1
  for flag in auth assoc authorized; do
   value=$(jsonfilter -s "$rows" -e "@.clients[\"$mac\"].$flag") || value=false
   test "$value" = true || ok=0
  done
  case "$mac" in "$WA"|"$XC")
   value=$(jsonfilter -s "$rows" -e "@.clients[\"$mac\"].wds") || value=false
   test "$value" = true || ok=0
  ;; esac
  test "$ok" = 0 || GOOD="$GOOD $mac"
 done
}
good() { case " $GOOD " in *" $1 "*) return 0;; *) return 1;; esac; }
all_good() { for m in $MACS; do good "$m" || return 1; done; }
protect_peers() {
 for m in $MACS; do
  if test "$m" != "$target" && ! good "$m"; then
   reason=unexpected_peer_loss; log "UNEXPECTED_PEER_LOSS $m target=$target phase=$phase"; exit 72
  fi
 done
}
clear_window() { set_ie ''; ie_on=0; next_pulse=$(($(now)+35)); }
pulse_missing() {
 t=$(now)
 if test "$ie_on" = 1; then
  test "$t" -lt "$clear_at" || clear_window
 elif test "$t" -ge "$next_pulse"; then
  set_ie "$IE"; ie_on=1; pulses=$((pulses+1)); seen_xc=0; seen_wa=0
  duration=2
  if test "$phase" = ADMIT && ! good "$WA"; then duration=60; fi
  clear_at=$(($(now)+duration))
  log "PULSE $pulses phase=$phase target=$target seconds=$duration"
 fi
}
start=$(now); end=$((start+780)); phase_end=$((start+120))
phase=ADMIT; target=; protected=; ie_on=0; next_pulse=$start
clear_at=0; pulses=0; drop_n=0; epoch=0; seen_xc=0; seen_wa=0
buf=
: > "$D/ready"
log "START_ADMIT deadline=$phase_end"
while test "$(now)" -lt "$end"; do
 kill -0 "$listener" 2>/dev/null || { reason=listener_lost; exit 73; }
 test "$(wc -c < "$D/events.jsonl")" -le 2097152 || { reason=event_bound; exit 74; }
 probe_address=; probe_target=
 if IFS= read -r -t 1 line <&3; then
  printf '%s\n' "$line" >> "$D/events.jsonl"
  buf="$buf
$line"
  case "$line" in *'}'*)
   if jsonfilter -s "$buf" -e '@' >/dev/null 2>&1; then
    probe_address=$(jsonfilter -s "$buf" -e '@.probe.address' 2>/dev/null || true)
    probe_target=$(jsonfilter -s "$buf" -e '@.probe.target' 2>/dev/null || true)
    buf=
   fi
  ;; esac
 fi
 test "${#buf}" -lt 8192 || { reason=event_json_bound; exit 84; }
 collect
 t=$(now)
 if test "$phase" = ADMIT && test "$probe_address" = "$WA"; then
  log "WA_PROBE target=$probe_target ie_on=$ie_on good=$GOOD"
 fi
 if test "$ie_on" = 1; then
  relevant=0; valid_probe=0
  case "$probe_target" in ff:ff:ff:ff:ff:ff|18:e8:29:74:55:a2) valid_probe=1;; esac
  if test "$phase" = ADMIT; then
   # Both stock airOS 8 clients must discover the same live IE window.
   if test "$valid_probe" = 1; then
    if ! good "$XC" && test "$probe_address" = "$XC" && test "$seen_xc" = 0; then
     seen_xc=1; log "SEEN_XC pulse=$pulses target=$probe_target"
    fi
    if ! good "$WA" && test "$probe_address" = "$WA" && test "$probe_target" = ff:ff:ff:ff:ff:ff && test "$seen_wa" = 0; then
     seen_wa=1; log "SEEN_WA pulse=$pulses target=$probe_target"
    fi
   fi
   if { good "$XC" || test "$seen_xc" = 1; } && { good "$WA" || test "$seen_wa" = 1; }; then
    relevant=1; log "BOTH_DISCOVERY_READY pulse=$pulses seen_xc=$seen_xc seen_wa=$seen_wa good=$GOOD"
   fi
  elif test "$phase" = RECOVER && test "$valid_probe" = 1 && test "$probe_address" = "$target"; then relevant=1
  fi
  if test "$relevant" = 1; then
   log "MISSING_CPE_PROBE $probe_address target=$probe_target"
   ucode -e 'sleep(500)'
   clear_window
  fi
 fi
 printf '%s phase=%s epoch=%s target=%s good=%s\n' "$t" "$phase" "$epoch" "$target" "$GOOD" >> "$D/state.log"
 case "$phase" in
 ADMIT)
  test "$t" -lt "$phase_end" || { reason=admission_timeout; exit 76; }
  for m in $protected; do
   good "$m" || { reason=initial_peer_loss; log "INITIAL_PEER_LOSS $m"; exit 75; }
  done
  protected=$GOOD
  if all_good; then
   clear_window; : > "$D/admitted"; phase=STABLE; stable_end=$(($(now)+61))
   log 'FOUR_ADMITTED'; log 'STABLE_START epoch=0'
  else
   pulse_missing
  fi
 ;;
 WAIT_LOSS)
  protect_peers
  if ! good "$target"; then
   log "DROP_OBSERVED n=$drop_n target=$target"; : > "$D/drop$drop_n.observed"
   phase=RECOVER; phase_end=$(($(now)+60)); next_pulse=$(now); pulse_missing
  else
   test "$t" -lt "$phase_end" || { reason=drop_not_observed; exit 77; }
  fi
 ;;
 RECOVER)
  test "$t" -lt "$phase_end" || { reason=recovery_timeout; exit 78; }
  protect_peers
  if good "$target"; then
   clear_window; log "RECOVERED n=$drop_n target=$target"
   phase=STABLE; epoch=$drop_n; stable_end=$(($(now)+61))
   log "STABLE_START epoch=$epoch"
  else
   pulse_missing
  fi
 ;;
 STABLE)
  all_good || { reason=stable_station_loss; log 'STABLE_STATION_LOSS'; exit 79; }
  if test "$t" -ge "$stable_end"; then
   log "STABLE_DONE epoch=$epoch"
   if test "$drop_n" = 4; then
    phase=COMPLETE; target=; : > "$D/complete"; log COMPLETE
   else
    drop_n=$((drop_n+1))
    case "$drop_n" in 1) target=$WA;; 2) target=$XC;; 3) target=64:d1:54:1b:96:97;; 4) target=f0:9f:c2:b2:b6:ba;; esac
    good "$target" || { reason=drop_target_missing; exit 80; }
    log "DROP_REQUEST n=$drop_n target=$target reason=3 deauth=true ban_time=0"
    ubus -t 4 call "$OBJ" del_client "{\"addr\":\"$target\",\"reason\":3,\"deauth\":true,\"ban_time\":0}" > "$D/drop$drop_n.ack"
    phase=WAIT_LOSS; phase_end=$(($(now)+5))
    # Do not interpret the method ACK as observed station loss.
    collect; protect_peers
    if ! good "$target"; then
     log "DROP_OBSERVED n=$drop_n target=$target"; : > "$D/drop$drop_n.observed"
     phase=RECOVER; phase_end=$(($(now)+60)); next_pulse=$(now); pulse_missing
    fi
   fi
  fi
 ;;
 COMPLETE)
  all_good || { reason=postcomplete_station_loss; exit 81; }
 ;;
 *) reason=invalid_phase; exit 82;;
 esac
done
reason=deadline
log DEADLINE
exit 83
