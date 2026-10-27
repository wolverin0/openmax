<!-- doc-head: STAGE249A_LTU_HARQ_RETRANSMISSION_AND_RATE_FSM_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 249A: Binary RE of LTU Link-State Machine, Timers & HARQ Block-ACK Rings

## 1. Binary Provenance (`CONFIRMED` — Attribution: `proprietary airMAX/LTU module`)
- **`afltu_2.4.2/ame_core.ko`**: SHA-256 `fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2` (`127` HARQ/ACK symbols, `204` FSM/timer symbols).
- **`aflturocket_2.4.2/ame_core.ko`**: SHA-256 `a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af`.
- **Safety**: 100% static on-disk ELF32 dissection; zero touches on `/dev/ame*` or `.241`/`.242`/`.20`/`.250`.

## 2. Extracted Modulation Upshift/Downshift Timer & Penalty Table (`CONFIRMED`)
| Symbol | Value | Role in `ame_core.ko` Rate-Control FSM |
| :--- | :---: | :--- |
| `startThrd_4096` | `97%` | Minimum codeword pass rate at `1024-QAM` to enter `4096-QAM` (`MCS 31`) |
| `stayThrd_4096` | `90%` | Minimum codeword pass rate to hold `4096-QAM` before downshifting |
| `mcsUpThrd_1024` / `256` | `93%` / `96%` | Upshift pass-rate thresholds for `1024-QAM` and `256-QAM` |
| `mcsUpThreshold` / `Down` | `7` / `10` | Consecutive superframe counters for upshift / downshift |
| `mcsUpThreshold_timer` / `Dn` | `90` / `1` | Timer windows (`ms`/ticks) gating rate transitions |
| `penaltyThreshold` / `Time` | `60` / `4` | Penalty-box backoff duration after repeated upshift BLER failures |

## 3. Subframe LDPC Codeword HARQ vs 802.11ac A-MPDU Block-ACK (`CONFIRMED`)
- **Granular Codeword Recovery**: Controlled by `multi_ack_enable=1`, `ack_ratio_thr`, and `ackAccuulateCnt`, LTU selectively retransmits only corrupted LDPC codewords in the next `2.0 ms` superframe without head-of-line blocking across the entire aggregate frame.
