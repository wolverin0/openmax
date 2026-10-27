#!/bin/sh
# SPDX-License-Identifier: MIT
# Offline selector/state-machine model. There is intentionally NO live backend.
set -eu
umask 077

usage() {
    printf '%s\n' 'PLAN_ONLY: no GPIO, radio, config, module or network access.' \
      'Usage: fmx-airprism-tuner.sh --dry-run CENTER_MHZ WIDTH_MHZ' \
      '       fmx-airprism-tuner.sh --fixture NEW_DIRECTORY CENTER_MHZ WIDTH_MHZ [FAIL_AT]' \
      'FAIL_AT: blank|gpio15|gpio16|gpio13|gpio14|verify|unblank (fixture only)'
}

# Original six records in original order: index stage start end mask value
# gpio15 gpio16 gpio13 gpio14 max_width. Stage is a bitmask in native code.
table() {
    cat <<'TABLE'
0 1 5150 5250 98304 98304 1 1 0 0 160
1 1 5470 5860 98304 32768 1 0 0 0 50
2 2 5200 5300 24576 8192 0 0 1 0 160
3 2 5725 5860 24576 16384 0 0 0 1 160
4 1 3000 6200 98304 65536 0 1 0 0 160
5 2 3000 6200 24576 24576 0 0 1 1 160
TABLE
}

select_stage() {
    wanted=$1
    while read -r idx stage start end mask value p15 p16 p13 p14 max_width; do
        if [ "$((stage & wanted))" -ne 0 ] && [ "$lower" -ge "$start" ] &&
           [ "$upper" -le "$end" ] && [ "$width" -le "$max_width" ]; then
            printf '%s\n' "$idx $p15 $p16 $p13 $p14"
            return 0
        fi
    done <<TABLE
$(table)
TABLE
    return 1
}

emit() {
    printf '%s\n' "$*"
    if [ -n "$fixture" ]; then printf '%s\n' "$*" >> "$fixture/trace.log"; fi
}

save_state() {
    if [ -n "$fixture" ]; then
        printf 'model_blanked=%s\nrf_enabled=0\nstatus=%s\n' "$blanked" "$status" > "$fixture/state.txt"
    fi
}

fail() {
    status=HOLD_OFFLINE
    emit "ERROR $1 model_blanked=$blanked rf_enabled=0"
    exit 1
}

finish() {
    rc=$?
    trap - EXIT HUP INT TERM
    # Never attempt to unblank from an error/signal handler.
    if [ "$rc" -ne 0 ]; then status=HOLD_OFFLINE; fi
    save_state
    exit "$rc"
}

step() {
    [ "$fail_at" != "$1" ] || fail "INJECTED_$1"
}

write_pin() {
    pin=$1 value=$2
    [ "$blanked" = 1 ] || fail WRITE_WITHOUT_CONFIRMED_BLANK
    step "gpio$pin"
    emit "GPIO_MODEL pin=$pin value=$value"
}

fixture= fail_at= blanked=unknown status=PLAN_ONLY
[ "$#" -ne 0 ] || { usage; exit 0; }
case "$1" in
    --dry-run)
        [ "$#" = 3 ] || { usage; exit 2; }
        center=$2 width=$3 ;;
    --fixture)
        [ "$#" = 4 ] || [ "$#" = 5 ] || { usage; exit 2; }
        fixture=$2 center=$3 width=$4 fail_at=${5-}
        case "$fixture" in ''|/|/sys|/sys/*|/proc|/proc/*|/dev|/dev/*) exit 2 ;; esac
        case "$fail_at" in ''|blank|gpio15|gpio16|gpio13|gpio14|verify|unblank) ;; *) exit 2 ;; esac
        [ ! -e "$fixture" ] && [ ! -L "$fixture" ] || exit 2
        mkdir -- "$fixture" || exit 2
        printf '%s\n' 'fmx-offline-fixture-v1' > "$fixture/owner.txt" ;;
    *) printf '%s\n' 'LIVE_BACKEND_REFUSED: offline delivery only' >&2; exit 2 ;;
esac
trap finish EXIT
trap 'exit 130' HUP INT TERM

# Reject shell expressions, signs and leading-zero/octal interpretation.
for number in "$center" "$width"; do
    case "$number" in ''|0*|*[!0-9]*) fail INVALID_CANONICAL_INTEGER ;; esac
    [ "${#number}" -le 5 ] || fail INTEGER_BOUND
done
[ "$center" -le 10000 ] && [ "$width" -le 160 ] || fail INPUT_BOUND

# Native .text+0xac920 uses width >> 1 (integer floor), also for odd widths.
half=$((width / 2))
lower=$((center - half)) upper=$((center + half))
s1=$(select_stage 1) || fail NO_STAGE1_MATCH
s2=$(select_stage 2) || fail NO_STAGE2_MATCH
set -- $s1
entry1=$1 gpio15=$2 gpio16=$3
set -- $s2
entry2=$1 gpio13=$4 gpio14=$5
bits=$((gpio13 + 2 * gpio14 + 4 * gpio15 + 8 * gpio16))
emit "SELECT center=$center width=$width lower=$lower upper=$upper stage1_entry=$entry1 stage2_entry=$entry2 bits_gpio16_to_13=$bits"

# The requested wifi1/GPIO7 is a logical interlock only: polarity/routing UNKNOWN.
# Keeping model RF disabled is independent of releasing the simulated blank.
step blank
blanked=1
emit 'BLANK_CONFIRMED_MODEL radio=wifi1 requested_pin=7 polarity=UNKNOWN rf_enabled=0'
write_pin 15 "$gpio15"
write_pin 16 "$gpio16"
write_pin 13 "$gpio13"
write_pin 14 "$gpio14"
step verify
emit 'VERIFY_MODEL selector_matches=1 rf_enabled=0'
step unblank
blanked=0
emit 'UNBLANK_MODEL_ONLY rf_enabled=0 hardware_control=NONE'
status=PASS_OFFLINE_SEQUENCE
emit "$status"
