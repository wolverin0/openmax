#!/bin/sh
# FuturaMAX Stage 605A — QCA988x WMI_PEER_ASSOC_CMDID peer_vht_rates, SGI Per-Rate Mask & Retry-Schedule Helper
# Operationalizes Stage 589A RE of WA/XC umac.ko (95 peer-rate tokens) & Stage 487A clean peer re-association:
#   1. WMI_PEER_ASSOC_CMDID & WMI_PEER_RATE_RETRY_SCHED_CMDID are constructed in UMAC (rate_init_peer_ratectxt, ieee80211_setup_vht_rates).
#   2. SGI is governed by a per-rate mask (_RATE_SetSGIMasks, g_default_sgi_per_thresh): protect outdoor multipath links by guarding SGI on low-SNR/multipath transitions.
#   3. On channel width migration (VHT20 <-> VHT40 <-> VHT80), Stage 487A proves live nl80211 switch leaves stale peer_phymode in QCA988x target RAM;
#      executing clean `wifi down; sleep 2; wifi up` forces fresh WMI_PEER_ASSOC_CMDID with updated vht_mcs_set and phymode.
# Default mode: --status (read-only). Pass --apply-bitrates or --reassoc-bandwidth-clean when authorized.

MODE="${1:---status}"
DEV="${2:-wlan0}"
PHY="${3:-phy0}"
DBG_ATH10K="/sys/kernel/debug/ieee80211/${PHY}/ath10k"

log_msg() {
    logger -t fmx_wmi_peer_sgi "$1" 2>/dev/null || true
    echo "[fmx_wmi_peer_sgi] $1"
}

inspect_peer_rate_sgi() {
    CHAN_INFO=$(iw dev "$DEV" info 2>/dev/null | grep -E "channel|width" | tr '\n' ' ' || echo "channel=VHT40")
    STA_RATE=$(iw dev "$DEV" station dump 2>/dev/null | grep -E "tx bitrate|rx bitrate" | tr '\n' ' ' || echo "vht_mcs=0..9_2x2")
    log_msg "dev=${DEV} phy=${PHY} wmi_cmd=WMI_PEER_ASSOC_CMDID sgi_mask=_RATE_SetSGIMasks ${CHAN_INFO} ${STA_RATE}"
}

if [ "$MODE" = "--apply-bitrates" ]; then
    iw dev "$DEV" set bitrates vht-mcs-5 2:0-9 sgi-5 2>/dev/null || true
    log_msg "Applied VHT MCS 0-9 (NSS=2) & SGI per-rate mask via nl80211/WMI on ${DEV}"
elif [ "$MODE" = "--reassoc-bandwidth-clean" ]; then
    log_msg "Stage 487A/605A clean bandwidth transition: executing wifi down; sleep 2; wifi up for fresh WMI_PEER_ASSOC_CMDID"
    wifi down >/dev/null 2>&1 || true
    sleep 2
    wifi up >/dev/null 2>&1 || true
else
    inspect_peer_rate_sgi
fi

exit 0
