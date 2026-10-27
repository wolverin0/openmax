#!/bin/sh
# FuturaMAX Stage 586A — WMI_PEER_ASSOC_CMDID Channel-Width Transition Guard (PBE-5AC-Gen2 0xe3d6 / LBE-5AC-Gen2 0xe4d6)
# Prevents QCA9882 Xtensa peer_phymode desync during VHT40/VHT80 <-> VHT20 transitions by enforcing clean wifi down/up.

TARGET_HTMODE="${1:-VHT20}"
ROLE="${2:-ap}"
BW_IDX=0
[ "$TARGET_HTMODE" = "VHT40" ] && BW_IDX=1
[ "$TARGET_HTMODE" = "VHT80" ] && BW_IDX=2

CUR_HTMODE="$(uci -q get wireless.radio0.htmode)"
if [ "$CUR_HTMODE" != "$TARGET_HTMODE" ]; then
    uci set wireless.radio0.htmode="$TARGET_HTMODE"
    uci set wireless.radio0.short_gi_20="0"
    uci set wireless.radio0.short_gi_40="0"
    uci set wireless.radio0.short_gi_80="0"
    uci commit wireless
    wifi down
    sleep 2
    wifi up
    sleep 12
fi

/etc/hotplug.d/net/99-fmx-wa-ptp-champion-v3 "$BW_IDX" "$ROLE"
