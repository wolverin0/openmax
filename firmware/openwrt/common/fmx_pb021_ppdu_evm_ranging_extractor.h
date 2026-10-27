/* SPDX-License-Identifier: ISC */
/* Stage 348A — PB-021 Per-PPDU 16-Pilot EVM & 12.5 ns Hardware Ranging Extractor
 * Hooked in `ath10k_htt_rx_amsdu_pop()` (`htt_rx.c:397-408`) BEFORE
 * `skb_pull(msdu, hw->rx_desc_ops->rx_desc_msdu_payload_offset)` discards `htt_rx_desc_v1`.
 */
#ifndef _FMX_PB021_PPDU_EVM_RANGING_EXTRACTOR_H_
#define _FMX_PB021_PPDU_EVM_RANGING_EXTRACTOR_H_

#include <linux/types.h>
#include <linux/byteorder/generic.h>

#define FMX_PB021_RING_SIZE 256
#define FMX_PB021_PPDU_DONE_MASK BIT(15)

struct fmx_pb021_ppdu_sample {
	u32 tsf_timestamp;
	u32 wb_timestamp_us;
	u32 evm_p[16];
	u8 locationing_timestamp; /* 0..79 @ 80 MHz = 12.5 ns (1.8737 m RTT step) */
	u8 phy_err_code;
	u16 flags;
	u32 info0;
	u16 bb_length;
	u16 info1;
} __packed;

struct fmx_pb021_ring {
	u32 write_idx;
	u32 total_captured;
	struct fmx_pb021_ppdu_sample samples[FMX_PB021_RING_SIZE];
};

static inline void fmx_pb021_capture_before_skb_pull(
	struct fmx_pb021_ring *ring,
	const struct rx_ppdu_end_common *common,
	const struct rx_ppdu_end_qca988x *qca988x)
{
	u16 info1;
	u32 idx;
	struct fmx_pb021_ppdu_sample *dst;

	if (!ring || !common || !qca988x)
		return;

	info1 = __le16_to_cpu(qca988x->info1);
	if (!(info1 & FMX_PB021_PPDU_DONE_MASK))
		return;

	idx = ring->write_idx & (FMX_PB021_RING_SIZE - 1);
	dst = &ring->samples[idx];
	__builtin_memcpy(dst->evm_p, &common->evm_p0, 16 * sizeof(u32));
	dst->tsf_timestamp = __le32_to_cpu(common->tsf_timestamp);
	dst->wb_timestamp_us = __le32_to_cpu(common->wb_timestamp);
	dst->locationing_timestamp = qca988x->locationing_timestamp;
	dst->phy_err_code = qca988x->phy_err_code;
	dst->flags = __le16_to_cpu(qca988x->flags);
	dst->info0 = __le32_to_cpu(qca988x->info0);
	dst->bb_length = __le16_to_cpu(qca988x->bb_length);
	dst->info1 = info1;

	ring->write_idx++;
	ring->total_captured++;
}

#endif /* _FMX_PB021_PPDU_EVM_RANGING_EXTRACTOR_H_ */
