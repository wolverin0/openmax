#!/bin/sh
# AP-local Zero-Touch Stock airOS 8 (WA.v8.7.25) Vendor-IE Admitter for Panel1-Guarida (78:45:58:a0:34:a2)
# Uses Panel1-Guarida's exact AES-128-ECB Vendor IE (key = HMAC-SHA1(ff:ff:ff:ff:ff:ff, 78:45:58:a0:34:a2)[:16])
# and the bench-proven two-stage withdrawal sequence:
#  1. IE is ON while unassociated CPEs scan Channel 48 (5240 MHz). Once both active CPEs (or all remaining
#     unassociated active CPEs) have sent a broadcast ProbeReq in the active IE window (or 22s after the first
#     CPE probes), wait 500ms so the CPE receives the Beacon with the valid 78:45:58:a0:34:a2 IE during its
#     Channel 48 dwell (adding 78:45:58:a0:34:a2 to sta_list and setting scan_list->ptpmode=1), then clear IE
#     for 45s while the CPEs finish scanning the remaining channels.
#  2. When each CPE finishes its scan, 78:45:58:a0:34:a2 is still in sta_list so scand and
#     ubnt_poll_host_is_ap_valid pass; the CPE tunes back to Channel 48 for ieee80211_mlme_join_infra_continue,
#     receives the IE-free join Beacon (which calls ubnt_poll_host_sta_list_remove), and sends AssocReq as
#     "Associating with normal AP" (with standard SSID IE 0) in 4-addr WDS mode.
set -u
trap '' HUP
D=${1:-/tmp/fmx-panel1-admitter}
mkdir -p "$D"
chmod 700 "$D"
OBJ=hostapd.phy0-ap0
AP_BSSID=78:45:58:a0:34:a2
IE=dd3a002722ffffff020100300c885a61cc8d1dc43e9f74183a4c2a47bdb46ddda4fc0f439caab4345da72229e8022acd18cba3491c75f136d9aa8f32
M1=24:5a:4c:44:77:7a
M2=24:5a:4c:e0:05:40
M3=24:5a:4c:c0:4c:f8
M4=0c:ea:14:94:a5:f0
ACTIVE_MACS="$M1 $M2"
ALL_MACS="$M1 $M2 $M3 $M4"
listener=

now() { cut -d. -f1 /proc/uptime; }
log() { printf '%s %s\n' "$(cut -d' ' -f1 /proc/uptime)" "$*" >> "$D/actions.log"; }

set_ie() {
 val="$1"
 for attempt in 1 2 3 4 5; do
  if ubus -t 4 call "$OBJ" set_vendor_elements "{\"vendor_elements\":\"$val\"}" >/dev/null 2>&1 &&
     ubus -t 4 call "$OBJ" update_beacon >/dev/null 2>&1; then
   if test -n "$val"; then log "IE_SET_ACK try=$attempt"; else log "IE_CLEAR_ACK try=$attempt"; fi
   return 0
  fi
  sleep 1
 done
 log "IE_CALL_FAILED len=${#val}"
 return 1
}

start_listener() {
 if test -n "$listener"; then
  kill "$listener" 2>/dev/null || true
  wait "$listener" 2>/dev/null || true
 fi
 rm -f "$D/events.fifo"
 mkfifo "$D/events.fifo"
 ubus -t 3600 subscribe "$OBJ" > "$D/events.fifo" 2>> "$D/listener.stderr" &
 listener=$!
 exec 3< "$D/events.fifo"
 log "LISTENER_STARTED pid=$listener"
}

cleanup() {
 status=$?
 trap - EXIT TERM INT USR1
 set +e
 set_ie '' || true
 if test -n "$listener"; then
  kill "$listener" 2>/dev/null || true
  wait "$listener" 2>/dev/null || true
 fi
 exec 3<&-
 rm -f "$D/events.fifo"
 log "ENDED rc=$status"
 exit "$status"
}
trap cleanup EXIT
trap 'exit 0' TERM INT USR1

rm -f "$D/admitted"
: > "$D/events.jsonl"
: > "$D/listener.stderr"
start_listener

GOOD=
collect() {
 rows=$(ubus -t 4 call "$OBJ" get_clients 2>/dev/null || true)
 case "$rows" in *'"clients"'*) ;; *) return 0;; esac
 GOOD=
 for mac in $ALL_MACS; do
  auth=$(jsonfilter -s "$rows" -e "@.clients[\"$mac\"].authorized" 2>/dev/null || echo false)
  wds=$(jsonfilter -s "$rows" -e "@.clients[\"$mac\"].wds" 2>/dev/null || echo false)
  if test "$auth" = true && test "$wds" = true; then
   GOOD="$GOOD $mac"
  fi
 done
}
good() { case " $GOOD " in *" $1 "*) return 0;; *) return 1;; esac; }
active_all_good() {
 for m in $ACTIVE_MACS; do
  good "$m" || return 1
 done
 return 0
}

ie_on=0
next_pulse=0
clear_at=0
first_probe_clear_at=0
next_poll=0
seen_m1=0
seen_m2=0

enable_ie() {
 set_ie "$IE" || true
 ie_on=1
 seen_m1=0
 seen_m2=0
 first_probe_clear_at=0
 t_now=$(now)
 clear_at=$((t_now+60))
 log "IE_WINDOW_OPEN clear_at=$clear_at good=$GOOD"
}

clear_window() {
 set_ie '' || true
 ie_on=0
 seen_m1=0
 seen_m2=0
 first_probe_clear_at=0
 t_now=$(now)
 next_pulse=$((t_now+45))
 log "IE_WINDOW_CLOSED next_pulse=$next_pulse good=$GOOD"
}

collect
enable_ie
: > "$D/ready"

while true; do
 if ! kill -0 "$listener" 2>/dev/null; then
  log "LISTENER_DIED_RESTARTING"
  start_listener
 fi
 if IFS= read -r -t 1 line <&3; then
  printf '%s\n' "$line" >> "$D/events.jsonl"
  if test "$ie_on" = 1; then
   case "$line" in
    *'"probe"'*'"target":"ff:ff:ff:ff:ff:ff"'*|*'"probe"'*'"target":"FF:FF:FF:FF:FF:FF"'*)
     t_p=$(now)
     if ! good "$M1"; then
      case "$line" in *"$M1"*)
       if test "$seen_m1" = 0; then
        seen_m1=1
        test "$first_probe_clear_at" != 0 || first_probe_clear_at=$((t_p+18))
        log "SEEN_M1_BCAST_PROBE first_probe_clear_at=$first_probe_clear_at"
       fi
      ;; esac
     fi
     if ! good "$M2"; then
      case "$line" in *"$M2"*)
       if test "$seen_m2" = 0; then
        seen_m2=1
        test "$first_probe_clear_at" != 0 || first_probe_clear_at=$((t_p+18))
        log "SEEN_M2_BCAST_PROBE first_probe_clear_at=$first_probe_clear_at"
       fi
      ;; esac
     fi
     if { good "$M1" || test "$seen_m1" = 1; } && { good "$M2" || test "$seen_m2" = 1; }; then
      log "BOTH_DISCOVERY_READY_SLEEP_500MS_AND_CLEAR seen_m1=$seen_m1 seen_m2=$seen_m2 good=$GOOD"
      ucode -e 'sleep(500)' 2>/dev/null || sleep 1
      clear_window
     fi
     ;;
    *'"auth"'*)
     log "AUTH_SEEN_WHILE_IE_ON_CLEARING_IMMEDIATELY line=$line"
     clear_window
     ;;
   esac
  fi
 fi

 t=$(now)
 if test "$t" -lt "$next_poll"; then
  continue
 fi
 next_poll=$((t+1))

 prev_good="$GOOD"
 collect
 printf '%s ie_on=%s good=%s\n' "$t" "$ie_on" "$GOOD" >> "$D/state.log"

 if active_all_good; then
  if test "$ie_on" = 1; then
   log "ALL_ACTIVE_ADMITTED_CLEARING_IE good=$GOOD"
   clear_window
  fi
  if test ! -f "$D/admitted"; then
   : > "$D/admitted"
   log "ADMITTED_FILE_CREATED good=$GOOD"
  fi
 else
  rm -f "$D/admitted"
  if test "$ie_on" = 1; then
   if test "$first_probe_clear_at" != 0 && test "$t" -ge "$first_probe_clear_at"; then
    log "SINGLE_CPE_PROBE_TIMEOUT_18S_CLEARING seen_m1=$seen_m1 seen_m2=$seen_m2"
    clear_window
   elif test "$t" -ge "$clear_at"; then
    log "IE_MAX_60S_REACHED_CLEARING"
    clear_window
   fi
  else
   # If one CPE just finished associating while IE was off, reopen IE pulse immediately for the remaining CPE!
   if test "$GOOD" != "$prev_good" && test -n "$GOOD"; then
    log "PARTIAL_CPE_ADMITTED_REOPENING_IE_FOR_REMAINING good=$GOOD"
    enable_ie
   elif test "$t" -ge "$next_pulse"; then
    log "REOPENING_IE_PULSE good=$GOOD"
    enable_ie
   fi
  fi
 fi
done
