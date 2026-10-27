<!-- doc-head: Stage 347A PB-040 Xtensa SGMT surgical RAM patch profiles, LITBASE disassembly, and volatile /tmp loader -->
Documenta la generación y verificación criptográfica (`SHA-256` + `12/12` segmentos `BMI_LZ` sin pérdida + desensamblado `Xtensa LITBASE = 0x009bb001`) de los 3 perfiles quirúrgicos en RAM (`PB040-CANARY-RODATA`, `PB040-CCA-AGC-OVERRIDE`, `PB040-SUB20MHZ-PLL-DIV`) sobre los 3 contenedores `SGMT` de `AR9888v2` (`umac.ko`), sin escrituras en Flash.
<!-- /doc-head -->

# Stage 347A — `PB-040` Xtensa `SGMT` Surgical RAM Patch Profiles (`mm-61aa`)

- **Claim Status**: `CONFIRMED` (`QCA firmware` / `ath10k` / `proprietary airMAX/LTU module`)
- **Memory-Master Claim**: `mm-61aa` (`id=155369`, `scope="project:futuramax"`)
- **Builder**: [`tools/firmware/build_stage347a_xtensa_sgmt_ram_patch_profiles.py`](../tools/firmware/build_stage347a_xtensa_sgmt_ram_patch_profiles.py)
- **Artifact**: [`artifacts/autoresearch/stage347a_xtensa_sgmt_ram_patch_profiles.json`](../artifacts/autoresearch/stage347a_xtensa_sgmt_ram_patch_profiles.json)
- **Volatile RAM Loader**: [`firmware/openwrt/xtensa_ram_patches_stage347a/fmx_xtensa_ram_patch_loader.sh`](../firmware/openwrt/xtensa_ram_patches_stage347a/fmx_xtensa_ram_patch_loader.sh)

## 1. Ground-Up Xtensa `LITBASE` (`SR 5`) & `SGMT` Architecture (`CONFIRMED`)

En el SoC/radio `QCA988x` (`AR9888v2` `Peregrine v2`), el firmware objetivo (`athwlan_AR9888v2_ptmp_ap_bin`, `athwlan_AR9888v2_ptmp_sta_bin`, `athwlan_AR9888v2_ptp_bin`) se empaqueta en un contenedor `SGMT` (`magic = 0x544d4753`, `file_flags = 1` `BMI_LZ`) con `4` segmentos cargados por `BMIFastDownload` y punto de entrada `BEGINADDR = 0x00983c00`:

1. **Segmento 0 (`0x00980000`) — `.lit4` Literal Pool**:
   - El firmware configura el registro especial Xtensa `LITBASE` (`SR 5`) en `0x009bb001` (`base = 0x009bb000`, `enable = 1`).
   - Así, una instrucción `l32r aT, imm16` con `imm16 = 0x1400` calcula `0x009bb000 + ((0x1400 - 0x10000) * 4) = 0x00980000` (el inicio exacto del Segmento 0).
2. **Segmento 1 (`0x0040b000`) — `.rodata` Tables & Strings**:
   - Contiene las cadenas de diagnóstico y la tabla de relojes/tasas sub-20 MHz (`5 MHz` Quarter-Rate / `10 MHz` Half-Rate).
3. **Segmento 2 (`0x0040d140` / `0x0040d130` / `0x0040cbc0`) — `.data` Tables**:
   - Contiene las tablas de despacho `WMI` (`0x9064` `WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID`).
4. **Segmento 3 (`0x00983c00`) — `.text` & Baseband Modal INI Arrays**:
   - Contiene el código ejecutable Xtensa LX4 y las tuplas INI modales del baseband (`struct ar9888_ini_array { u32 reg, u32 modal_a, u32 modal_b }`).

## 2. Perfiles Quirúrgicos Verificados (`12/12` Segmentos `BMI_LZ` Lossless)

| Perfil | Imagen `SGMT` | Seg | Dirección Virtual | `.lit4` Slot (`Seg 0`) | Call-Sites `l32r` (`Seg 3`) | Cambio Exacto (`Len Preserved`) |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| `PB040-CANARY-RODATA` | `ptmp_ap_bin` | `1` | `0x0040b953` | `0x00981068` (`-> 0x0040b940`) | `0x009acbb9`, `0x009acbd5`, `0x009acbf2` (`b11a18`) | `0x65` (`'e'`) $\rightarrow$ `0x45` (`'E'`) (`1 B`) |
| `PB040-CANARY-RODATA` | `ptmp_sta_bin` | `1` | `0x0040b953` | `0x00981068` (`-> 0x0040b940`) | `0x009acbe5`, `0x009acc01`, `0x009acc1e` (`b11a18`) | `0x65` (`'e'`) $\rightarrow$ `0x45` (`'E'`) (`1 B`) |
| `PB040-CANARY-RODATA` | `ptp_bin` | `1` | `0x0040b8d3` | `0x00981040` (`-> 0x0040b8c0`) | `0x009abe0d`, `0x009abe29`, `0x009abe46` (`b11018`) | `0x65` (`'e'`) $\rightarrow$ `0x45` (`'E'`) (`1 B`) |
| `PB040-CCA-AGC-OVERRIDE` | `ptmp_ap_bin` | `3` | `0x009c7a78` | `0x009810dc` (`-> 0x009c7a60`) | `0x009ad001` (`413718` `l32r a4`) | `0x00029e00` `cca_thresh62` shadow `0x13721320` $\rightarrow$ `0x13761320` (`16 B`) |
| `PB040-CCA-AGC-OVERRIDE` | `ptmp_sta_bin` | `3` | `0x009c2e88` | `0x009810dc` (`-> 0x009c2e70`) | `0x009ad02d` (`413718` `l32r a4`) | `0x00029e00` `cca_thresh62` shadow `0x13721320` $\rightarrow$ `0x13761320` (`16 B`) |
| `PB040-CCA-AGC-OVERRIDE` | `ptmp_bin` (`ptp`) | `3` | `0x009bd8d8` | `0x009810b4` (`-> 0x009bd8c0`) | `0x009ac255` (`412d18` `l32r a4`) | `0x00029e00` `cca_thresh62` shadow `0x13721320` $\rightarrow$ `0x13761320` (`16 B`) |
| `PB040-SUB20MHZ-PLL-DIV` | `ptmp_ap_bin` | `1` | `0x0040bb40` | `0x009814ec` (`-> 0x0040bb40`) | `0x009b68ff` (`b13b19` `l32r a11`) | `060c121824303600` $\rightarrow$ `060c121824304800` (`8 B`) |
| `PB040-SUB20MHZ-PLL-DIV` | `ptmp_sta_bin` | `1` | `0x0040bb80` | `0x009814e0` (`-> 0x0040bb80`) | `0x009b62db` (`b13819` `l32r a11`) | `060c121824303600` $\rightarrow$ `060c121824304800` (`8 B`) |
| `PB040-SUB20MHZ-PLL-DIV` | `ptp_bin` | `1` | `0x0040ba90` | `0x009814dc` (`-> 0x0040ba90`) | `0x009b483b` (`b13719` `l32r a11`) | `060c121824303600` $\rightarrow$ `060c121824304800` (`8 B`) |

## 3. Protocolo de Activación en RAM (`0` Escrituras en Flash)

El script [`fmx_xtensa_ram_patch_loader.sh`](../firmware/openwrt/xtensa_ram_patches_stage347a/fmx_xtensa_ram_patch_loader.sh) copia el contenedor `SGMT` verificado a `/tmp/firmware-5.bin`, ejecuta `mount --bind /tmp/firmware-5.bin /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin`, recarga `ath10k_pci`, y supervisa la aparición de `/sys/class/ieee80211/phy0` con un watchdog de `45s`. Si ocurre cualquier anomalía o un reinicio eléctrico, el sistema restaura automáticamente el firmware original desde la partición SquashFS de solo lectura sin tocar jamás `mtd0`, `mtd1`, `mtd4` ni `mtd5` (`ART`).
