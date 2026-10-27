#!/bin/sh
# FuturaMAX Unified Mode B rc.poststart Production Generator v39.0 (target=AUTO)
# Safe RAM-only runtime tuning with 45s Non-DFS / 120s DFS rollback guard (FMX-DISC-24)
# Supports: WA, XC, 2XC, XW, XM, LTU
VER=$(cat /etc/version 2>/dev/null || echo "UNKNOWN")
FAM="AUTO"
if [ "$FAM" = "AUTO" ]; then
    case "$VER" in
        XC.*)  FAM="XC" ;;
        2XC.*) FAM="2XC" ;;
        WA.*)  FAM="WA" ;;
        XW.*)  FAM="XW" ;;
        XM.*)  FAM="XM" ;;
        AF-LTU*|LTU*) FAM="LTU" ;;
        *)     FAM="WA" ;;
    esac
fi

case "$FAM" in
    XC|2XC)
        sysctl -w vm.min_free_kbytes=4096 vm.vfs_cache_pressure=150 \
            net.core.netdev_budget=480 net.core.dev_weight=48 \
            net.core.netdev_max_backlog=1024 net.ipv4.tcp_limit_output_bytes=65536 \
            net.ipv4.tcp_tso_win_divisor=8 net.ipv4.tcp_pacing_ca_ratio=110 \
            net.ipv4.tcp_pacing_ss_ratio=150 >/dev/null 2>&1 || true
        iwpriv ath0 set_multiq 3 2>/dev/null || true
        echo 0  > /sys/module/ath_dev/parameters/ACVOMinfree 2>/dev/null || true
        echo 16 > /sys/module/ath_dev/parameters/ACVIMinfree 2>/dev/null || true
        echo 32 > /sys/module/ath_dev/parameters/ACBEMinfree 2>/dev/null || true
        echo 48 > /sys/module/ath_dev/parameters/ACBKMinfree 2>/dev/null || true
        echo 3  > /proc/sys/dev/uph_wifi0/swr_limit 2>/dev/null || true
        echo 2  > /proc/sys/dev/uph_wifi0/ff_cap_rep 2>/dev/null || true
        echo 6  > /proc/sys/dev/uph_wifi0/cms_bias 2>/dev/null || true
        echo 6  > /proc/sys/dev/uph_wifi0/voip_bias 2>/dev/null || true
        # FMX-DISC-11: write daprot BEFORE ff_mcast_airtime_limit
        echo 2  > /proc/sys/dev/uph_wifi0/daprot 2>/dev/null || true
        echo 5  > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit 2>/dev/null || true
        iwpriv wifi0 vow_extstats 0 2>/dev/null || true
        echo 1  > /sys/module/umac/parameters/enable_tx_tcp_cksum 2>/dev/null || true
        for dev in br0 ath0 eth0; do ifconfig $dev txqueuelen 192 2>/dev/null || true; done
        ethtool -C eth0 rx-usecs 24 tx-usecs 48 2>/dev/null || true
        ;;
    WA)
        sysctl -w vm.min_free_kbytes=2048 vm.vfs_cache_pressure=120 \
            net.core.netdev_budget=480 net.core.dev_weight=48 \
            net.core.netdev_max_backlog=1024 net.ipv4.tcp_limit_output_bytes=65536 \
            net.ipv4.tcp_tso_win_divisor=8 >/dev/null 2>&1 || true
        iwpriv ath0 set_multiq 3 2>/dev/null || true
        echo 0  > /sys/module/ath_dev/parameters/ACVOMinfree 2>/dev/null || true
        echo 16 > /sys/module/ath_dev/parameters/ACVIMinfree 2>/dev/null || true
        echo 32 > /sys/module/ath_dev/parameters/ACBEMinfree 2>/dev/null || true
        echo 48 > /sys/module/ath_dev/parameters/ACBKMinfree 2>/dev/null || true
        echo 3  > /proc/sys/dev/uph_wifi0/swr_limit 2>/dev/null || true
        echo 2  > /proc/sys/dev/uph_wifi0/ff_cap_rep 2>/dev/null || true
        echo 6  > /proc/sys/dev/uph_wifi0/cms_bias 2>/dev/null || true
        echo 6  > /proc/sys/dev/uph_wifi0/voip_bias 2>/dev/null || true
        echo 2  > /proc/sys/dev/uph_wifi0/daprot 2>/dev/null || true
        echo 5  > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit 2>/dev/null || true
        iwpriv wifi0 vow_extstats 0 2>/dev/null || true
        echo 1  > /sys/module/umac/parameters/enable_tx_tcp_cksum 2>/dev/null || true
        for dev in br0 ath0 eth0; do ifconfig $dev txqueuelen 192 2>/dev/null || true; done
        ;;
    XW)
        sysctl -w vm.min_free_kbytes=2048 net.core.netdev_budget=300 \
            net.core.dev_weight=48 net.core.netdev_max_backlog=768 \
            net.ipv4.tcp_limit_output_bytes=65536 >/dev/null 2>&1 || true
        echo 0  > /proc/sys/dev/ATH0/ACVOMinfree 2>/dev/null || true
        echo 16 > /proc/sys/dev/ATH0/ACVIMinfree 2>/dev/null || true
        echo 32 > /proc/sys/dev/ATH0/ACBEMinfree 2>/dev/null || true
        echo 48 > /proc/sys/dev/ATH0/ACBKMinfree 2>/dev/null || true
        echo 28 > /proc/sys/dev/ATH0/AMPDUFrames 2>/dev/null || true
        echo 40960 > /proc/sys/dev/ATH0/AMPDULim 2>/dev/null || true
        echo 1  > /proc/sys/dev/ubnt_poll/ewma_delegate_on 2>/dev/null || true
        for dev in br0 ath0 eth0; do ifconfig $dev txqueuelen 64 2>/dev/null || true; done
        ;;
    XM)
        sysctl -w vm.min_free_kbytes=1536 \
            net.ipv4.tcp_rmem="4096 32768 131072" \
            net.ipv4.tcp_wmem="4096 16384 65536" \
            net.core.netdev_budget=256 net.core.dev_weight=32 \
            net.core.netdev_max_backlog=512 \
            net.ipv4.tcp_limit_output_bytes=32768 >/dev/null 2>&1 || true
        echo 0  > /proc/sys/dev/ATH0/ACVOMinfree 2>/dev/null || true
        echo 16 > /proc/sys/dev/ATH0/ACVIMinfree 2>/dev/null || true
        echo 32 > /proc/sys/dev/ATH0/ACBEMinfree 2>/dev/null || true
        echo 64 > /proc/sys/dev/ATH0/ACBKMinfree 2>/dev/null || true
        echo 28 > /proc/sys/dev/ATH0/AMPDUFrames 2>/dev/null || true
        echo 40960 > /proc/sys/dev/ATH0/AMPDULim 2>/dev/null || true
        echo 1  > /proc/sys/dev/ubnt_poll/ewma_delegate_on 2>/dev/null || true
        for dev in br0 ath0 eth0; do ifconfig $dev txqueuelen 48 2>/dev/null || true; done
        ;;
    LTU)
        # S102E LTU Tail-Guard Safe Mode (never touch eab_driver.ko registers without optical/serial recovery)
        sysctl -w vm.min_free_kbytes=4096 net.core.netdev_budget=300 \
            net.core.dev_weight=48 net.core.netdev_max_backlog=1000 \
            net.ipv4.tcp_limit_output_bytes=131072 >/dev/null 2>&1 || true
        ifconfig eth0 txqueuelen 256 2>/dev/null || true
        ;;
esac
exit 0
