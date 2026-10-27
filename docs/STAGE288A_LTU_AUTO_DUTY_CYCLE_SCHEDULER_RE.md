<!-- doc-head: STAGE288A_LTU_AUTO_DUTY_CYCLE_SCHEDULER_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 288A: Binary RE of LTU Dynamic Split-Duty Scheduler (`50/50` $\leftrightarrow$ `67/33` $\leftrightarrow$ `75/25`)

## 1. Binary Provenance (`CONFIRMED` — Attribution: `proprietary airMAX/LTU module`)
- **`aflturocket_2.4.2/ame_core.ko`**: SHA-256 `a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af` (`515` duty/scheduler symbols).
- **`aflturocket_2.4.2/cds_mac_mod.ko`**: SHA-256 `883a8c29b8fd3c58a29f1e76ece68178b415540c263679c95e12b6df6953369c`.
- **Safety**: 100% static on-disk ELF32 dissection; zero touches on `/dev/ame*` or `.241`/`.242`/`.20`/`.250`.

## 2. Dynamic Split-Duty State Table (`80` Symbols = `2.0 ms` Superframe)
| `duty_cycle` (permille) | Mode | DL Symbols (`25 us`) | UL Symbols (`25 us`) | Turnaround/Guard Symbols |
| :---: | :--- | :---: | :---: | :---: |
| `500` | `50/50` Symmetric | `38` (`0.95 ms`) | `38` (`0.95 ms`) | `4` (`0.10 ms`) |
| `670` | `67/33` Balanced WISP | `51` (`1.275 ms`) | `25` (`0.625 ms`) | `4` (`0.10 ms`) |
| `750` | `75/25` Peak Downlink | `57` (`1.425 ms`) | `19` (`0.475 ms`) | `4` (`0.10 ms`) |

## 3. Auto-Adaptation Hysteresis & GPS Co-Site Lock (`CONFIRMED`)
- **Dynamic Transition**: In standalone/non-co-located sectors, `ame_core.ko` shifts between `500`, `670`, and `750` permille based on the ratio of AP EAB downlink queue depth to CPE uplink bandwidth requests (`BR`), broadcasting the new DL/UL boundary in the `0x9898` MAP header.
- **Co-Site Tower Lock**: On towers with multiple co-located LTU APs under GPS 1PPS sync, fixed `duty_cycle=670` (or `750`) must be enforced so DL-to-UL turnarounds remain phase-aligned.
