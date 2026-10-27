<!-- doc-head: Stage 440A Pillar 4 LTU Short-Queue (SQ/NQ) Micro-AP, AD9361 Split-Frequency & Arria 10 8-Subband Kit (<220 lines) -->
Construye el paquete Ground-Up del Pilar 4 (`firmware/ltu_safe_kit/fmx_ltu_ground_up_sq_splitfreq_helper.sh`) consolidando y verificando los offsets binarios descubiertos en `Stages 342A`, `343A`, `376A`, `424A` y `438A` (`SQ/NQ` `NtoS`/`StoN`, `AD9361` `TX_LO != RX_LO` y subbandas `OFDMA`), con modo seguro `--inspect-only` por defecto.
<!-- /doc-head -->

# Stage 440A — Pillar 4 LTU Short-Queue (`SQ`/`NQ`) Micro-AP, `AD9361` Split-Frequency & `Arria 10` Subband Kit (`mm-fef1`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-fef1`, `id=155406`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Helper Script**: [`firmware/ltu_safe_kit/fmx_ltu_ground_up_sq_splitfreq_helper.sh`](../firmware/ltu_safe_kit/fmx_ltu_ground_up_sq_splitfreq_helper.sh) (`SHA-256`: `749ba247fa93beb03035e83038afb938d36dfb63cc084b601df76565bd07c046`)
- **Artifact**: [`artifacts/autoresearch/stage440a_ltu_sq_micro_ap_and_split_freq_kit.json`](../artifacts/autoresearch/stage440a_ltu_sq_micro_ap_and_split_freq_kit.json)

## 1. Síntesis Verificada de Offsets Binarios (`Stages 342A, 343A, 376A, 424A, 438A`)

| Subsistema Pilar 4 | Etapa Base | Evidencia Binaria y Registros Verificados (`CONFIRMED`) |
| :--- | :---: | :--- |
| **Planificador Dinámico `SQ` / `NQ` (`<= 16` CPEs)** | `Stage 342A` & `438A` | Hilos `SCHED_FIFO` (`ame.core.Hi=90`, `ame.core.Frm=85`, `ame.core.L2Q=54`) + máquina de estados `Top NQ CPE (NtoS)` <-> `Min SQ CPE (StoN)` (`numQ`, `numSQ`, `297` símbolos `sched` en `ame_core.ko`). |
| **`AD9361` Agile SDR Split-Frequency (`TX_LO != RX_LO`)** | `Stage 343A` | Bus SPI `/sys/class/spi_master/spi32766/spi32766.0` con sintetizadores independientes `RX_LO` (`0x231..0x235`) y `TX_LO` (`0x271..0x275`) en `ame_radio_mod.ko`. |
| **`LTU-Rocket` `Arria 10` Mailbox & Subbandas `OFDMA`** | `Stage 376A` & `424A` | `359` tokens `eab` integrados en `ame_core.ko` + control `ofdma_subband_type` (`ofdma_en`, `ofdma_start`, `ofdma_len`) + `HFE`/`HCAM` en `ap_cds_mac_mod.ko`. |

## 2. Garantía de Seguridad en Producción (`--inspect-only` / `--dry-run`)
El script `fmx_ltu_ground_up_sq_splitfreq_helper.sh` opera por defecto en modo `--inspect-only` (`zero_dev_ame_touches = True`, `hardware_writes_performed = 0`), emitiendo el diagnóstico JSON completo de afinidad `IRQ 52`, clase `SQ`/`NQ`, registros `AD9361` (`0x271..0x275` vs `0x231..0x235`) y estado de subbandas `OFDMA`.
