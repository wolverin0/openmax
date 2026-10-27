<!-- doc-head: Stage 708A AF-LTU (Beetle) Zero-Copy DMA Ring & ame_ASIC0 Backpressure Read-Only Guard (<200 lines) -->
`Stage 708A` construye el auditor read-only `firmware/ltu_safe_kit/fmx_ltu_dma_ring_backpressure_guard.sh` que operacionaliza la ingeniería inversa de `eab_driver.ko` y `ame_core.ko` (`Stage 694A`) auditando los anillos DMA entre el ARM Cortex-A7 y `ame_ASIC0` sin tocar `/dev/ame*`.
<!-- /doc-head -->

# Stage 708A — `AF-LTU` (`Beetle`) Zero-Copy DMA Ring & `ame_ASIC0` Backpressure Guard (`mm-cc53`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-cc53`, `id=155467`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Deliverable**: [`firmware/ltu_safe_kit/fmx_ltu_dma_ring_backpressure_guard.sh`](../firmware/ltu_safe_kit/fmx_ltu_dma_ring_backpressure_guard.sh)
- **SHA-256**: `1dd0f6f9e96ec1800d1c78660e5e58a8687805c46d112d5848cddf26ac93be18`
- **Artifact**: [`artifacts/autoresearch/stage708a_ltu_dma_ring_backpressure_guard.json`](../artifacts/autoresearch/stage708a_ltu_dma_ring_backpressure_guard.json)

## 1. Arquitectura de Contrapresión `ARM Cortex-A7 <-> ame_ASIC0` (`CONFIRMED`)
| Subsistema (`eab_driver.ko` / `ame_core.ko`) | Valor /Invariante | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| `IRQ 52` (`ame_asic0`) Affinity | `smp_affinity = 2` (`CPU1`) | Aísla las interrupciones de completitud DMA de `ame_ASIC0` en `CPU1`, separándolas de `GMAC0` (`IRQ 63` en `CPU0`) (`hardware`). |
| `net.core.busy_read` / `busy_poll` | `0` / `0` | Evita que el polling de sockets en `CPU0` compita por el spinlock del anillo DMA de `eab_driver.ko` (`Linux`). |
| `eth0` `byte_queue_limits/limit_max` | `36288 bytes` (`24` tramas) | Limita la cola en vuelo de `GMAC0` a un superframe `TDMA` de `2 ms`, evitando desborde de descriptores TX hacia `ame_ASIC0` (`Linux`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
