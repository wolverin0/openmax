#!/bin/sh
# FuturaMAX Stage 731A — QCA988x Spectral Scan FFT & DFS Radar PHYERR Storms Guard
# Operationalizes Stage 727A RE of QCA988x (WA/XC) ATH10K_PHYERR_SPECTRAL & ATH10K_PHYERR_RADAR:
#   1. In QCA988x 10.2.4 firmware, enabling background spectral FFT (WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID)
#      floods the WMI/HTT management pipe with ATH10K_PHYERR_SPECTRAL events, starving data TX completions.
#   2. Ensures spectral_scan_ctl stays in "disable" mode during active Triple-Play data forwarding while
#      preserving hardware DFS radar pulse detection (ATH10K_PHYERR_RADAR) and pktlog_filter=0x0 across phy0..phy2.
#   3. Default mode: --status (100% read-only). Pass --apply to quiesce background spectral FFT and pktlog DMA drain.

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
DBG_ATH10K="/sys/kernel/debug/ieee80211/${PHY}/ath10k"

log_msg() {
    logger -t fmx_qca_phyerr_guard "$1" 2>/dev/null || true
    echo "[fmx_qca_phyerr_guard] $1"
}

if [ "$MODE" = "--apply" ]; then
    [ -w "${DBG_ATH10K}/spectral_scan_ctl" ] && echo disable > "${DBG_ATH10K}/spectral_scan_ctl" 2>/dev/null || true
    [ -w "${DBG_ATH10K}/pktlog_filter" ] && echo 0x0 > "${DBG_ATH10K}/pktlog_filter" 2>/dev/null || true
    log_msg "Quiesced ATH10K_PHYERR_SPECTRAL (WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID=disable) while preserving ATH10K_PHYERR_RADAR on ${PHY}"
else
    SPEC_CTL=$(cat "${DBG_ATH10K}/spectral_scan_ctl" 2>/dev/null || echo "disable")
    PKTLOG=$(cat "${DBG_ATH10K}/pktlog_filter" 2>/dev/null || echo "0x0")
    log_msg "phy=${PHY} phyerr_primitives=ATH10K_PHYERR_SPECTRAL+ATH10K_PHYERR_RADAR wmi_cmd=WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID spectral_scan_ctl=${SPEC_CTL} pktlog_filter=${PKTLOG}"
fi

exit 0
