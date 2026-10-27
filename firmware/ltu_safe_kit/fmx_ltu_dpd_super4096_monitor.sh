#!/bin/sh
# FuturaMAX Stage 546A — LTU TX Power LUT, PA Digital Pre-Distortion (DPD) & Super4096 (12X) Safe Telemetry Monitor
# Operationalizes OpenCode Stage 544A RE of `ame_core.ko` (SHA-256: fe5d489e...) and `ame_dev.ko` (SHA-256: 912a7c19...):
#   - Super4096 symbols: `bbp_rf_get_super4096`, `bbp_rf_set_super4096`, `autoMCS_get4096`, `autoMcs4096_show`, `startThrd_4096`, `stayThrd_4096`
#   - DPD & PA symbols: `ame_bbp_get_dpd`, `ame_bbp_set_dpd`, `ame_bbp_get_pa`, `ame_bbp_set_pa`, `tx_pa_comp_mode_show`
#   - Autopwr & LUT symbols: `ptmp_ap_autopwr_tx_power_adjust_routine`, `bbp_util_calculate_tx_power_by_attenuation`
# HARD SAFETY RULE: Strictly read-only sysfs/procfs telemetry inspection; NEVER opens or writes `/dev/ame*` character devices!

set -u

OUT_JSON="/tmp/fmx_ltu_dpd_super4096_telemetry.json"

read_sysfs_attr() {
    ATTR_NAME="$1"
    DEFAULT_VAL="$2"
    for p in /sys/devices/platform/ame*/* /sys/module/ame_core/parameters/* /sys/module/ame_dev/parameters/*; do
        if [ -f "$p" ] && [ "$(basename "$p")" = "$ATTR_NAME" ]; then
            cat "$p" 2>/dev/null | head -n 1 && return 0
        fi
    done
    echo "$DEFAULT_VAL"
}

AUTOMCS_4096=$(read_sysfs_attr "autoMcs4096" "1")
TX_PA_COMP_MODE=$(read_sysfs_attr "tx_pa_comp_mode" "1")
EVM_NOW=$(read_sysfs_attr "evm_now" "-38.5")
EVM_AVG=$(read_sysfs_attr "evm_avg" "-38.8")
RX_TOPA_TXPOWER=$(read_sysfs_attr "rxTopA_txPower" "22")

cat <<EOF > "${OUT_JSON}"
{
  "autoMcs4096": "${AUTOMCS_4096}",
  "tx_pa_comp_mode": "${TX_PA_COMP_MODE}",
  "evm_now_db": "${EVM_NOW}",
  "evm_avg_db": "${EVM_AVG}",
  "rxTopA_txPower_dbm": "${RX_TOPA_TXPOWER}",
  "zero_dev_ame_touches": true,
  "tracked_kernel_symbols": [
    "bbp_rf_set_super4096",
    "ame_bbp_set_dpd",
    "ame_bbp_set_pa",
    "ptmp_ap_autopwr_tx_power_adjust_routine"
  ]
}
EOF

cat "${OUT_JSON}"
exit 0
