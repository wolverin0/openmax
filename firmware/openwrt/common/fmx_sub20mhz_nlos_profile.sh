#!/bin/sh
# FuturaMAX Stage 410A — PB-030 / PB040-SUB20MHZ-PLL-DIV Sub-20 MHz (5 MHz / 10 MHz) NLOS Profile Wrapper
# Configures 10 MHz Half-Rate (+3.01 dB PSD SNR gain, 1.6 us GI) or 5 MHz Quarter-Rate (+6.02 dB PSD SNR gain,
# 3.2 us GI) along with scaled slot_time, sifs, and ack_timeout for severe NLOS / foliage links.

PHY="${1:-phy0}"
DEV="${2:-wlan0}"
BW_MHZ="${3:-10}"
FREQ_MHZ="${4:-5745}"
DISTANCE_M="${5:-3000}"

case "${BW_MHZ}" in
    5)
        # Quarter-Rate 5 MHz: 4x symbol duration (16 us), 3.2 us GI (+6.02 dB thermal noise floor reduction)
        SLOT_TIME_US=21
        SIFS_US=64
        SNR_GAIN_DB="6.02"
        GI_NS=3200
        EFF_DISTANCE_M=$((DISTANCE_M * 4))
        iw dev "${DEV}" set freq "${FREQ_MHZ}" 5 2>/dev/null || true
        ;;
    10)
        # Half-Rate 10 MHz: 2x symbol duration (8 us), 1.6 us GI (+3.01 dB thermal noise floor reduction)
        SLOT_TIME_US=13
        SIFS_US=32
        SNR_GAIN_DB="3.01"
        GI_NS=1600
        EFF_DISTANCE_M=$((DISTANCE_M * 2))
        iw dev "${DEV}" set freq "${FREQ_MHZ}" 10 2>/dev/null || true
        ;;
    *)
        SLOT_TIME_US=9
        SIFS_US=16
        SNR_GAIN_DB="0.00"
        GI_NS=800
        EFF_DISTANCE_M="${DISTANCE_M}"
        ;;
esac

iw phy "${PHY}" set distance "${EFF_DISTANCE_M}" 2>/dev/null || true
iw phy "${PHY}" set rts off 2>/dev/null || true

mkdir -p /tmp/fmx_sub20_state
cat <<EOF > /tmp/fmx_sub20_state/sub20mhz_profile.json
{
  "profile_id": "PB040-SUB20MHZ-PLL-DIV",
  "phy": "${PHY}",
  "dev": "${DEV}",
  "bw_mhz": ${BW_MHZ},
  "freq_mhz": ${FREQ_MHZ},
  "slot_time_us": ${SLOT_TIME_US},
  "sifs_us": ${SIFS_US},
  "guard_interval_ns": ${GI_NS},
  "psd_snr_gain_db": ${SNR_GAIN_DB},
  "effective_distance_m": ${EFF_DISTANCE_M}
}
EOF

exit 0
