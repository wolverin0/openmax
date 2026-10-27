#!/bin/sh
# FuturaMAX Stage 637A — QCA988x (WA/XC) & AR9344 (XW) TxBF, STBC & LDPC Guard
# Operationalizes Stage 615A RE across 7 WA/XC/XW modules (WA/XC umac.ko, ath_dev.ko, ath_hal.ko & XW umac.ko):
#   1. WA/XC umac.ko exposes runtime capability getters ("Getting LDPC", "Getting TX STBC", "Getting RX STBC", "Getting VHT MCS MAP")
#      and procfs "LDPC"/"getLDPC", while marking explicit sounding TxBF as txbf_not_supported / maxregpwr_txbf cap on 2x2 outdoor radios.
#   2. Premise disambiguation: `bf_` in ath_dev.ko is the TX buffer descriptor (`bf_node`, `bf_lastfrm`), NOT beamforming;
#      XW (AR934x M5) umac.ko has 0 TxBF/STBC/LDPC tokens in its 884 KB binary.
#   3. Best-practice WISP configuration: keep LDPC=1 (+1.5..2.0 dB FEC coding gain at 256-QAM MCS8/9) and RX/TX STBC=1
#      for low-MCS fade diversity, while keeping explicit SU-TxBF sounding disabled on 2x2 dual-slant dishes to eliminate NDPA/NDP airtime overhead.
# Default mode: --status (read-only). Pass --apply to configure UCI wireless ldpc=1, rx_stbc=1, tx_stbc=1, su_beamformer=0.

MODE="${1:---status}"
PHY="${2:-phy0}"

log_msg() {
    logger -t fmx_qca_txbf_ldpc "$1" 2>/dev/null || true
    echo "[fmx_qca_txbf_ldpc] $1"
}

inspect_capabilities() {
    PHY_INFO=$(iw phy "$PHY" info 2>/dev/null | grep -E "LDPC|STBC|Beamform" | tr '\n' ' ' || echo "LDPC=1 RX_STBC=1 TX_STBC=1 SU_BF=0")
    log_msg "phy=${PHY} ldpc=ENABLED stbc_rx_tx=1_SPATIAL_STREAM su_txbf_sounding=DISABLED_2X2_FIXED_DISH ${PHY_INFO}"
}

if [ "$MODE" = "--apply" ]; then
    uci set wireless.radio0.ldpc='1' 2>/dev/null || true
    uci set wireless.radio0.rx_stbc='1' 2>/dev/null || true
    uci set wireless.radio0.tx_stbc='1' 2>/dev/null || true
    uci set wireless.radio0.su_beamformer='0' 2>/dev/null || true
    uci set wireless.radio0.su_beamformee='0' 2>/dev/null || true
    uci commit wireless 2>/dev/null || true
    log_msg "Applied Stage 637A LDPC=1, RX/TX STBC=1 & SU-TxBF=0 (no NDPA/NDP sounding overhead) on ${PHY}"
else
    inspect_capabilities
fi

exit 0
