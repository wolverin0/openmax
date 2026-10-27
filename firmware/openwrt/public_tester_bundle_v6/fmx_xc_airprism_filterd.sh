#!/bin/sh
# FuturaMAX Stage 305A Active-AirPrism 2-Bank GPIO (GPIO 13..16) Filter Daemon
# Reverse-engineered from XC.v8.7.25 umac.ko:
#   - ubnt_prism_hook    (.text+0x0ac874)
#   - ubnt_prism_filters (.data+0x001510, 6 entries x 24 bytes)
#
# 2-Bank GPIO 13..16 Cascade Truth Table (Combined 4-pin mask 0x1e000):
#   Bank 1 (GPIO 15, GPIO 16, mask 0x18000):
#     Entry 0: 5150..5250 MHz (BW <= 160 MHz) -> g15=1, g16=1 (0x18000)
#     Entry 1: 5470..5860 MHz (BW <=  50 MHz) -> g15=1, g16=0 (0x08000)
#     Entry 2: 3000..6200 MHz (BW <= 160 MHz) -> g15=0, g16=1 (0x10000, wideband fallback)
#   Bank 2 (GPIO 13, GPIO 14, mask 0x06000):
#     Entry 3: 5200..5300 MHz (BW <= 160 MHz) -> g13=1, g14=0 (0x02000)
#     Entry 4: 5725..5860 MHz (BW <= 160 MHz) -> g13=0, g14=1 (0x04000)
#     Entry 5: 3000..6200 MHz (BW <= 160 MHz) -> g13=1, g14=1 (0x06000, wideband fallback)
#
# Active-AirPrism XC sysids (18 records): 0xe3f5, 0xe7e5, 0xe7e6, 0xe7e8, 0xe7e7, 0xe7e9, 0xdc97
#   (plus aliases 0xe7f9, 0xe7f8, 0xe2f5)
# Passive XC sysids (16 records, safe no-op): 0xe1f5, 0xe3d5, 0xe5f5, 0xe4f5, 0xe3d7, 0xe3d8

FMX_PRISM_POLL_SEC="${FMX_PRISM_POLL_SEC:-5}"
FMX_PRISM_GPIO_BASE="${FMX_PRISM_GPIO_BASE:-0}"
FMX_PRISM_STATE_FILE="${FMX_PRISM_STATE_FILE:-/tmp/fmx_xc_airprism_filterd.state}"

detect_xc_sysid() {
	if [ -n "$FMX_PRISM_SYSID" ]; then
		echo "$FMX_PRISM_SYSID" | tr 'A-Z' 'a-z'
		return
	fi
	if [ -f /etc/board.info ]; then
		sid=$(sed -n 's/^board\.sysid=//p' /etc/board.info 2>/dev/null | head -n 1 | tr 'A-Z' 'a-z')
		if [ -n "$sid" ]; then
			echo "$sid"
			return
		fi
	fi
	if [ -f /tmp/sysinfo/board_name ]; then
		bn=$(cat /tmp/sysinfo/board_name 2>/dev/null)
		case "$bn" in
			*rocket-prism*|*rp-5ac*) echo "0xe7e9"; return ;;
			*prismstation*|*ps-5ac*) echo "0xe7e8"; return ;;
			*prismap*) echo "0xdc97"; return ;;
			*r5ac-prism*) echo "0xe7e5"; return ;;
			*r5ac-ptp*|*r5ac-ptmp*) echo "0xe3f5"; return ;;
		esac
	fi
	echo "unknown"
}

is_active_airprism_xc() {
	sid="$1"
	case "$sid" in
		0xe3f5|0xe7e5|0xe7e6|0xe7e8|0xe7e7|0xe7e9|0xdc97|0xe7f9|0xe7f8|0xe2f5)
			return 0
			;;
		0xe1f5|0xe3d5|0xe5f5|0xe4f5|0xe3d7|0xe3d8|*)
			return 1
			;;
	esac
}

compute_prism_gpio_pins() {
	freq="$1"
	bw="$2"
	[ -z "$freq" ] && freq=5500
	[ -z "$bw" ] && bw=40

	# Bank 1 (GPIO 15, GPIO 16, bitmask 0x18000)
	if [ "$freq" -ge 5150 ] && [ "$freq" -le 5250 ] && [ "$bw" -le 160 ]; then
		g15=1; g16=1; b1_hex="0x18000"; b1_entry=0
	elif [ "$freq" -ge 5470 ] && [ "$freq" -le 5860 ] && [ "$bw" -le 50 ]; then
		g15=1; g16=0; b1_hex="0x08000"; b1_entry=1
	else
		g15=0; g16=1; b1_hex="0x10000"; b1_entry=2
	fi

	# Bank 2 (GPIO 13, GPIO 14, bitmask 0x06000)
	if [ "$freq" -ge 5200 ] && [ "$freq" -le 5300 ] && [ "$bw" -le 160 ]; then
		g13=1; g14=0; b2_hex="0x02000"; b2_entry=3
	elif [ "$freq" -ge 5725 ] && [ "$freq" -le 5860 ] && [ "$bw" -le 160 ]; then
		g13=0; g14=1; b2_hex="0x04000"; b2_entry=4
	else
		g13=1; g14=1; b2_hex="0x06000"; b2_entry=5
	fi

	mask_val=$(( (g13 << 13) | (g14 << 14) | (g15 << 15) | (g16 << 16) ))
	mask_hex=$(printf "0x%05x" "$mask_val")
	echo "g13=$g13 g14=$g14 g15=$g15 g16=$g16 bank1=$b1_hex(e$b1_entry) bank2=$b2_hex(e$b2_entry) mask=$mask_hex"
}

read_iw_freq_and_bw() {
	if [ -n "$FMX_PRISM_FREQ_MHZ" ]; then
		echo "${FMX_PRISM_FREQ_MHZ} ${FMX_PRISM_BW_MHZ:-40}"
		return
	fi
	for dev in phy0-ap0 phy0-sta0 wlan0 ath0; do
		info=$(iw dev "$dev" info 2>/dev/null)
		[ -n "$info" ] || continue
		freq=$(echo "$info" | sed -n 's/.*channel [0-9]* (\([0-9]*\) MHz).*/\1/p' | head -n 1)
		bw=$(echo "$info" | sed -n 's/.*width: \([0-9]*\) MHz.*/\1/p' | head -n 1)
		if [ -n "$freq" ]; then
			[ -z "$bw" ] && bw=20
			echo "$freq $bw"
			return
		fi
	done
	echo "5500 40"
}

apply_gpio_13_16_sysfs() {
	[ "$FMX_PRISM_DRY_RUN" = "1" ] && return 0
	for pin in 13 14 15 16; do
		gnum=$(( FMX_PRISM_GPIO_BASE + pin ))
		if [ ! -d "/sys/class/gpio/gpio${gnum}" ] && [ -w /sys/class/gpio/export ]; then
			echo "$gnum" > /sys/class/gpio/export 2>/dev/null || true
		fi
		if [ -w "/sys/class/gpio/gpio${gnum}/direction" ]; then
			echo out > "/sys/class/gpio/gpio${gnum}/direction" 2>/dev/null || true
		fi
	done
	val13="$1"; val14="$2"; val15="$3"; val16="$4"
	[ -w "/sys/class/gpio/gpio$((FMX_PRISM_GPIO_BASE + 13))/value" ] && echo "$val13" > "/sys/class/gpio/gpio$((FMX_PRISM_GPIO_BASE + 13))/value" 2>/dev/null || true
	[ -w "/sys/class/gpio/gpio$((FMX_PRISM_GPIO_BASE + 14))/value" ] && echo "$val14" > "/sys/class/gpio/gpio$((FMX_PRISM_GPIO_BASE + 14))/value" 2>/dev/null || true
	[ -w "/sys/class/gpio/gpio$((FMX_PRISM_GPIO_BASE + 15))/value" ] && echo "$val15" > "/sys/class/gpio/gpio$((FMX_PRISM_GPIO_BASE + 15))/value" 2>/dev/null || true
	[ -w "/sys/class/gpio/gpio$((FMX_PRISM_GPIO_BASE + 16))/value" ] && echo "$val16" > "/sys/class/gpio/gpio$((FMX_PRISM_GPIO_BASE + 16))/value" 2>/dev/null || true
}

run_once() {
	sid=$(detect_xc_sysid)
	if ! is_active_airprism_xc "$sid"; then
		echo "PASSIVE_NOOP sysid=$sid" > "$FMX_PRISM_STATE_FILE" 2>/dev/null || true
		[ "$1" = "--print" ] && echo "PASSIVE_NOOP sysid=$sid"
		return 0
	fi
	set -- $(read_iw_freq_and_bw)
	freq="$1"; bw="$2"
	res=$(compute_prism_gpio_pins "$freq" "$bw")
	eval "$res" 2>/dev/null || true
	apply_gpio_13_16_sysfs "$g13" "$g14" "$g15" "$g16"
	line="ACTIVE_AIRPRISM sysid=$sid freq=${freq}MHz bw=${bw}MHz $res"
	echo "$line" > "$FMX_PRISM_STATE_FILE" 2>/dev/null || true
	[ "$3" = "--print" ] || [ "$1" = "--print" ] && echo "$line"
	return 0
}

if [ "$1" = "--self-test" ]; then
	FMX_PRISM_DRY_RUN=1
	for vec in "0xe7e9:5180:40" "0xe7e9:5220:40" "0xe7e9:5500:40" "0xe7e9:5500:80" "0xe7e9:5785:40" "0xe7e9:5785:80" "0xe1f5:5500:40"; do
		FMX_PRISM_SYSID=$(echo "$vec" | cut -d: -f1)
		FMX_PRISM_FREQ_MHZ=$(echo "$vec" | cut -d: -f2)
		FMX_PRISM_BW_MHZ=$(echo "$vec" | cut -d: -f3)
		if is_active_airprism_xc "$FMX_PRISM_SYSID"; then
			r=$(compute_prism_gpio_pins "$FMX_PRISM_FREQ_MHZ" "$FMX_PRISM_BW_MHZ")
			echo "ACTIVE_AIRPRISM sysid=$FMX_PRISM_SYSID freq=${FMX_PRISM_FREQ_MHZ}MHz bw=${FMX_PRISM_BW_MHZ}MHz $r"
		else
			echo "PASSIVE_NOOP sysid=$FMX_PRISM_SYSID"
		fi
	done
	exit 0
fi

if [ "$1" = "--once" ]; then
	run_once --print
	exit 0
fi

# Daemon loop
LAST_SIG=""
while true; do
	sid=$(detect_xc_sysid)
	if ! is_active_airprism_xc "$sid"; then
		echo "PASSIVE_NOOP sysid=$sid" > "$FMX_PRISM_STATE_FILE" 2>/dev/null || true
		exit 0
	fi
	fbw=$(read_iw_freq_and_bw)
	if [ "$fbw" != "$LAST_SIG" ]; then
		LAST_SIG="$fbw"
		run_once >/dev/null 2>&1 || true
	fi
	sleep "$FMX_PRISM_POLL_SEC"
done
