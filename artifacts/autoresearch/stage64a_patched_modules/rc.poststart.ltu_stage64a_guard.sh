#!/bin/sh
# FuturaMAX Stage 64A — Firmware-Upgrade-Safe LTU Kernel Module Guard & Runtime Optimizer
# Automatically bypasses binary module override if Ubiquiti LTU firmware is upgraded.

ORIG_CORE="/lib/modules/3.14.65/ame_core.ko"
ORIG_DEV="/lib/modules/3.14.65/ame_dev.ko"
CUR_CORE_SHA=$(sha256sum "$ORIG_CORE" 2>/dev/null | awk '{print $1}')
CUR_DEV_SHA=$(sha256sum "$ORIG_DEV" 2>/dev/null | awk '{print $1}')

EXPECTED_CPE_CORE_SHA="fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2"
EXPECTED_AP_CORE_SHA="a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af"
EXPECTED_CPE_DEV_SHA="912a7c1923aad381ac38ae922b78f69888cec0bd1558c09abf2de68657c8b955"

if [ "$CUR_CORE_SHA" = "$EXPECTED_CPE_CORE_SHA" ] || [ "$CUR_CORE_SHA" = "$EXPECTED_AP_CORE_SHA" ]; then
    logger -t fmx-ltu-guard "LTU v2.4.2 SHA-256 verified ($CUR_CORE_SHA); applying Stage 64A EAB + 4096-QAM tuning"
    # 1. Unlock EAB DMA ring buffer descriptors (0 = maximum hardware ring depth instead of default 49)
    if [ -w /sys/class/ame/ame_ctrl_dev/adj_maxBD ]; then
        echo 0 > /sys/class/ame/ame_ctrl_dev/adj_maxBD
    fi
    # 2. Enable 4096-QAM (12x) state machine in ame_core
    if [ -w /sys/class/ame/ame_ctrl_dev/autoMcs4096 ]; then
        echo 1 > /sys/class/ame/ame_ctrl_dev/autoMcs4096
    fi
    # 3. Raise autoMcsCeiling to 11 (4096-QAM MIMO 12x) without resetting adj_mcs when /tmp/ame_core_fmx.ko is active
    if [ -w /sys/class/ame/ame_ctrl_dev/autoMcsCeiling ]; then
        echo 11 > /sys/class/ame/ame_ctrl_dev/autoMcsCeiling
    fi
else
    logger -t fmx-ltu-guard "Firmware SHA-256 mismatch ($CUR_CORE_SHA); skipping binary patch for upgrade safety"
fi
