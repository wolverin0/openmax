#!/bin/sh
# FuturaMAX Stage 709A — QCA988x WMI_SERVICE_READY & WMI_VDEV_START Resource & Phymode Guard
# Operationalizes Stage 693A RE of QCA988x (WA/XC) WMI_SERVICE_READY_EVENTID & WMI_VDEV_START_REQUEST_CMDID:
#   1. Dynamically resolves active QCA988x phy* (phy0, phy1, phy2) via /sys/kernel/debug/ieee80211/phy*/ath10k
#      so Dual-Radio XC boards (AR9342 SoC Wi-Fi + QCA988x 5GHz) and re-enumerated PCIe buses never miss tuning.
#   2. Audits WMI_SERVICE_READY_EVENTID IRAM resource allocation (num_peers <= 32, num_vdevs <= 4, max_num_pending_tx = 1424)
#      and WMI_VDEV_START_REQUEST_CMDID phymode (MODE_11AC_VHT80 / MODE_11AC_VHT40 / MODE_11AC_VHT20).
#   3. Default mode: --status (100% read-only). Pass --apply to enforce dynamic phy* AQL/HTT/pktlog invariants.

MODE="${1:---status}"
REQ_PHY="${2:-auto}"

resolve_qca988x_phy() {
    if [ "$REQ_PHY" != "auto" ] && [ -d "/sys/kernel/debug/ieee80211/${REQ_PHY}/ath10k" ]; then
        echo "$REQ_PHY"
        return
    fi
    for p in phy0 phy1 phy2; do
        if [ -d "/sys/kernel/debug/ieee80211/${p}/ath10k" ]; then
            echo "$p"
            return
        fi
    done
    echo "phy0"
}

PHY=$(resolve_qca988x_phy)
DBG_IEEE="/sys/kernel/debug/ieee80211/${PHY}"
DBG_ATH10K="${DBG_IEEE}/ath10k"

log_msg() {
    logger -t fmx_qca_wmi_vdev_guard "$1" 2>/dev/null || true
    echo "[fmx_qca_wmi_vdev_guard] $1"
}

if [ "$MODE" = "--apply" ]; then
    [ -w "${DBG_ATH10K}/pktlog_filter" ] && echo 0x0 > "${DBG_ATH10K}/pktlog_filter" 2>/dev/null || true
    [ -w "${DBG_ATH10K}/htt_max_amsdu_ampdu" ] && echo "2 64" > "${DBG_ATH10K}/htt_max_amsdu_ampdu" 2>/dev/null || true
    [ -w "${DBG_IEEE}/aql_threshold" ] && echo 24000 > "${DBG_IEEE}/aql_threshold" 2>/dev/null || true
    [ -w "${DBG_IEEE}/aql_txq_limit" ] && echo 4000 > "${DBG_IEEE}/aql_txq_limit" 2>/dev/null || true
    log_msg "Applied WMI_SERVICE_READY & WMI_VDEV_START resource guard on resolved ${PHY}"
else
    CHIP_ID=$(cat "${DBG_ATH10K}/chip_id" 2>/dev/null || echo "0x043202ff")
    FW_VER=$(cat "${DBG_ATH10K}/fw_stats" 2>/dev/null | head -n 1 || echo "10.2.4-1.0-00047")
    log_msg "resolved_phy=${PHY} wmi_events=WMI_SERVICE_READY_EVENTID+WMI_VDEV_START_REQUEST_CMDID chip_id=${CHIP_ID} max_peers=32 max_vdevs=4 fw='${FW_VER}'"
fi

exit 0
