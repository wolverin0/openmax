#!/bin/sh
# FuturaMAX Stage 440A — Pillar 4 LTU Short-Queue (SQ/NQ) Micro-AP, AD9361 Split-Frequency
# (TX_LO != RX_LO), and Arria 10 / OFDMA 8-Subband Helper (fmx_ltu_ground_up_sq_splitfreq_helper.sh)
# Consolidates binary RE offsets from Stages 342A, 343A, 376A, 424A, and 438A.
# DEFAULT SAFETY MODE: --inspect-only / --dry-run on production units (ZERO writes to character devices).

set -u

MODE="${1:---inspect-only}"
MAX_CPE="${2:-16}"
TX_FREQ_MHZ="${3:-5785}"
RX_FREQ_MHZ="${4:-5220}"
SUBBAND_MASK_HEX="${5:-0xff}"

BOARD_SYSID="unknown"
if [ -f /etc/board.info ]; then
    BOARD_SYSID="$(awk -F= '/^board\.sysid=/ {print $2; exit}' /etc/board.info 2>/dev/null || echo unknown)"
fi

SPI_NODE="/sys/class/spi_master/spi32766/spi32766.0"
AME_CTRL_DIR="/sys/class/ame/ame_ctrl_dev"
IRQ52_AFFINITY="unknown"
if [ -r /proc/irq/52/smp_affinity ]; then
    IRQ52_AFFINITY="$(cat /proc/irq/52/smp_affinity 2>/dev/null || echo unknown)"
fi

# Determine SQ/NQ scheduler class mode (Stage 342A + Stage 438A NtoS / StoN dynamic poll list)
if [ "$MAX_CPE" -le 16 ] 2>/dev/null; then
    SQ_CLASS="SQ_MICRO_AP_LE16 (Short-Queue NtoS/StoN fast poll ring)"
else
    SQ_CLASS="NQ_STANDARD_64CPE (Normal-Queue poll ring)"
fi

# AD9361 Agile SDR synthesizer register bank mapping (Stage 343A: RX_LO 0x231..0x235, TX_LO 0x271..0x275)
if [ "$TX_FREQ_MHZ" != "$RX_FREQ_MHZ" ]; then
    SPLIT_FREQ_STATE="SPLIT_FREQUENCY_ACTIVE (AD9361 TX_LO 0x271..0x275=${TX_FREQ_MHZ}MHz != RX_LO 0x231..0x235=${RX_FREQ_MHZ}MHz)"
else
    SPLIT_FREQ_STATE="SYMMETRIC_LO (AD9361 TX_LO == RX_LO == ${TX_FREQ_MHZ}MHz)"
fi

if [ "$MODE" = "--inspect-only" ] || [ "$MODE" = "--dry-run" ]; then
    cat <<EOF
{
  "helper": "fmx_ltu_ground_up_sq_splitfreq_helper.sh",
  "stage": "440A",
  "execution_mode": "${MODE}",
  "board_sysid": "${BOARD_SYSID}",
  "irq52_smp_affinity": "${IRQ52_AFFINITY}",
  "sq_nq_scheduler": {
    "configured_max_cpe": ${MAX_CPE},
    "scheduler_class": "${SQ_CLASS}",
    "ame_core_transitions": ["Top NQ CPE (NtoS)", "Min SQ CPE (StoN)", "numQ / numSQ"],
    "rt_fifo_threads": {"ame.core.Hi": 90, "ame.core.Frm": 85, "ame.core.L2Q": 54}
  },
  "ad9361_split_frequency": {
    "spi_node": "${SPI_NODE}",
    "tx_lo_regs": "0x271..0x275",
    "rx_lo_regs": "0x231..0x235",
    "tx_freq_mhz": ${TX_FREQ_MHZ},
    "rx_freq_mhz": ${RX_FREQ_MHZ},
    "state": "${SPLIT_FREQ_STATE}"
  },
  "arria10_ofdma_subband": {
    "subband_mask_hex": "${SUBBAND_MASK_HEX}",
    "ame_core_tokens": ["ofdma_en", "ofdma_start", "ofdma_len", "ofdma_subband_type"],
    "ame_ctrl_dir": "${AME_CTRL_DIR}"
  },
  "hardware_writes_performed": 0
}
EOF
    exit 0
fi

echo "[fmx-ltu-sq-splitfreq] Refusing live SDR/FPGA register mutation without bench override; use --inspect-only or --dry-run."
exit 0
