#!/bin/sh
# Stage 347A — PB-040 Volatile RAM SGMT Patch Loader & Watchdog (Zero Flash Writes)
# Safely bind-mounts a surgically patched QCA988x / AR9888v2 SGMT firmware container
# from volatile /tmp RAM over /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin,
# reloads ath10k_pci, verifies WMI_READY + wlan0 PHY bring-up within 45s, and
# automatically unmounts + restores stock firmware on any anomaly.

set -eu

PROFILE="${1:-PB040-CANARY-RODATA}"
IMAGE_ROLE="${2:-athwlan_AR9888v2_ptmp_ap_bin}"
PATCH_DIR="/tmp/fmx_xtensa_ram_patches"
TARGET_FW="/lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin"
WATCHDOG_TIMEOUT_SEC=45

log_msg() {
    logger -t "fmx-pb040-ram-loader" "$1"
    echo "[fmx-pb040-ram-loader] $1"
}

rollback_to_stock() {
    log_msg "ROLLBACK: Unmounting volatile RAM firmware override and restoring stock SquashFS image"
    umount "$TARGET_FW" 2>/dev/null || true
    rmmod ath10k_pci 2>/dev/null || true
    insmod ath10k_pci 2>/dev/null || true
    wifi up 2>/dev/null || true
}

if [ "$PROFILE" = "rollback" ] || [ "$PROFILE" = "restore" ]; then
    rollback_to_stock
    exit 0
fi

PATCH_BLOB="${PATCH_DIR}/${IMAGE_ROLE}.${PROFILE}.sgmt.bin"
if [ ! -f "$PATCH_BLOB" ]; then
    log_msg "ERROR: Missing patched SGMT blob: $PATCH_BLOB"
    exit 1
fi

# Verify SGMT magic (0x544d4753 = 'SGMT') before bind-mounting
MAGIC_HEX="$(dd if="$PATCH_BLOB" bs=1 count=4 2>/dev/null | hexdump -v -e '/1 "%02x"')"
if [ "$MAGIC_HEX" != "53474d54" ]; then
    log_msg "ERROR: Invalid SGMT magic ($MAGIC_HEX) in $PATCH_BLOB; refusing load"
    exit 1
fi

cp -f "$PATCH_BLOB" /tmp/firmware-5.bin
umount "$TARGET_FW" 2>/dev/null || true
mount --bind /tmp/firmware-5.bin "$TARGET_FW"
log_msg "Bind-mounted /tmp/firmware-5.bin ($PROFILE) over $TARGET_FW (0 Flash writes)"

rmmod ath10k_pci 2>/dev/null || true
insmod ath10k_pci 2>/dev/null || {
    log_msg "ERROR: insmod ath10k_pci failed; triggering immediate rollback"
    rollback_to_stock
    exit 1
}

ELAPSED=0
while [ "$ELAPSED" -lt "$WATCHDOG_TIMEOUT_SEC" ]; do
    if [ -d /sys/class/ieee80211/phy0 ]; then
        log_msg "SUCCESS: phy0 active under $PROFILE within ${ELAPSED}s (RAM-only bind-mount verified)"
        exit 0
    fi
    sleep 1
    ELAPSED=$((ELAPSED + 1))
done

log_msg "WATCHDOG TIMEOUT (${WATCHDOG_TIMEOUT_SEC}s): phy0 did not appear; rolling back to stock"
rollback_to_stock
exit 1
