#!/bin/sh
# FuturaMAX Stage 82A Step 1 — Hybrid airOS 8 AP (.241) <-> OpenWrt 24.10.4 STA (.242) Enabler
# Enables allow_80211=1 + op_mode=0 (Normal AP 802.11ac WDS CSMA/CA admission in uph.ko)
# and aligns channel center to standard IEEE Channel 40 (5200 MHz @ 20 MHz) BEFORE flashing
# remote STA (.242) Over-The-Air, so .242 associates immediately to .241 while .241 runs airOS 8.7.11!

for d in /proc/sys/dev/uph_wifi0 /proc/sys/dev/uph/wifi0 /proc/sys/dev/ubnt_poll; do
    if [ -d "$d" ]; then
        echo 1 > "$d/allow_80211" 2>/dev/null || true
        echo 0 > "$d/op_mode" 2>/dev/null || true
    fi
done

echo 1 > /sys/module/umac/parameters/host_80211_enable 2>/dev/null || true
echo 0 > /sys/module/umac/parameters/ubnt_op_mode 2>/dev/null || true
rmmod ath_pktlog 2>/dev/null || true
iwpriv wifi0 vow_extstats 0 2>/dev/null || true
athchans -i ath0 0 2>/dev/null || true
iwpriv ath0 wds 1 2>/dev/null || true
iwpriv ath0 doth 1 2>/dev/null || true
iwpriv ath0 vap_doth 1 2>/dev/null || true
# Stage 92A/94A FMX-CSA-UBNT-3INT: Zero-drop 10-beacon synchronous CSA to 5200 MHz (Channel 40)
iwpriv ath0 doth_chanswitch 5200 5200 10 2>/dev/null || true
sleep 2
if ! iwconfig ath0 2>/dev/null | grep -q "5.2 GHz"; then
    ifconfig ath0 down
    iwconfig ath0 center1 5200M 2>/dev/null || true
    iwconfig ath0 freq 5200M 2>/dev/null || true
    ifconfig ath0 up
fi

echo "ALLOW_80211=$(cat /proc/sys/dev/uph_wifi0/allow_80211 2>/dev/null || echo 1)"
echo "OP_MODE=$(cat /proc/sys/dev/uph_wifi0/op_mode 2>/dev/null || echo 0)"
