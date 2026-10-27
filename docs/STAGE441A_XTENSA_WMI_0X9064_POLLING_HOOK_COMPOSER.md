<!-- doc-head: Stage 441A Pillar 3 Xtensa WMI 0x9064 Jump Table (0x009b2037) & Polling Hook Composer (0x0040f688) (<220 lines) -->
Reconcilia y verifica mediante descompresión `BMI_LZ` (`file_flags = 1`) los offsets exactos de `Stages 387A` y `423A` (`0x009b2037`, `0x009b5c02`, `0x0040f688` y `0x0040fb54`) sobre `openwrt_qca988x_hw20_firmware_2_ct.bin` y `athwlan_AR9888v2_ptmp_ap_bin` (`umac.ko`), generando los `32` descriptores de telemetría de cola por estación en IRAM (`0x00981a00..0x00981bff`).
<!-- /doc-head -->

# Stage 441A — Pillar 3 Xtensa `WMI 0x9064` Jump Table & Polling Hook Composer (`mm-831f`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-831f`, `id=155407`)
- **Attribution**: `QCA firmware`, `ath10k`
- **Builder**: [`tools/firmware/build_stage441a_xtensa_wmi_0x9064_polling_hook_composer.py`](../tools/firmware/build_stage441a_xtensa_wmi_0x9064_polling_hook_composer.py)
- **Artifact**: [`artifacts/autoresearch/stage441a_xtensa_wmi_0x9064_polling_hook_composer.json`](../artifacts/autoresearch/stage441a_xtensa_wmi_0x9064_polling_hook_composer.json)

## 1. Reconciliación Criptográfica de `Stages 387A` y `423A` vía `BMI_LZ` (`CONFIRMED`)

En `Stages 387A` y `423A`, el barrido estático sin descompresión `BMI_LZ` reportó que el segmento `SGMT` comprimido (`197,537` B $ightarrow$ `0x009b03a1`) terminaba `7,318` bytes antes de `0x009b2037`. Al descomprimir con `SgmtContainer.from_bytes()` (`file_flags = 1` `BMI_LZ`):

| Contenedor `SGMT` | Segmento | Rango Virtual Descomprimido | Bytes Descomprimidos | Direcciones Confirmadas Dentro del Segmento |
| :--- | :---: | :--- | :---: | :--- |
| `openwrt_qca988x_hw20_firmware_2_ct.bin` (`IE 3`) | `Seg 3` | `0x00983c00 .. 0x009b8a94` | `216,724 B` | `0x009b2037` (Jump Table) y `0x009b5c02` (Handler) |
| `openwrt_qca988x_hw20_firmware_2_ct.bin` (`IE 4`) | `Seg 2` | `0x0040b1a0 .. 0x00411df1` | `27,729 B` | `0x0040f688` (`32` palabras DRAM) |
| `athwlan_AR9888v2_ptmp_ap_bin` (`umac.ko`) | `Seg 2` | `0x0040d140 .. 0x0040fbb0` | `10,864 B` | `0x0040f688` (`32` palabras) y `0x0040fb54` (`0x00009064`) |
| `athwlan_AR9888v2_ptmp_ap_bin` (`umac.ko`) | `Seg 3` | `0x00983c00 .. 0x009c8fd4` | `283,604 B` | `0x009b2037` (`46250086...`), `0x009b207c` (`case 0x17`), `0x009b5c02` |

## 2. Anillo de `32` Descriptores de Telemetría de Cola en IRAM (`0x00981a00 .. 0x00981bff`)

Entre el final del Segmento 0 (`.lit4` `0x00980000..0x00981960`) y el inicio del Segmento 3 (`0x00983c00`) existe una ventana libre en IRAM donde el compositor ubica `32` descriptores de `16` bytes (`512` B totales) en `0x00981a00..0x00981bff`, codificando `tid0_be_backlog_bytes`, `tid5_vi_backlog_bytes`, `tid6_vo_backlog_bytes`, `head_sojourn_us` y el sello `0x90640000 | peer_id`.
