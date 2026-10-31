<!-- doc-head -->
*STAGE1520A — diseccion ELF LTU (AME/EAB/ASIC0) y radar DFS WA vs XC; cifras medidas, sin acceso a radio*
# STAGE 1520A — Disección ELF de LTU (`ame_*`) y de `ath_hal`/`ath_dfs` WA vs XC

## 0. Alcance y método
- Trabajo **100% estático y offline**: se leen módulos `.ko` ya extraídos en disco. No hay SSH, ni carga de módulos, ni parcheo, ni acceso a radio.
- Lector propio `tools/re/elf32_rel_any.py`: ELF32 `ET_REL`, detecta clase y endianness desde `e_ident`, valida límites de cada sección y sólo entonces devuelve bytes. Rechaza ELF64 y cualquier tabla de secciones fuera del fichero.
- Etiquetas: `CONFIRMED` (medido en bytes), `INFERRED` (deducido), `UNKNOWN` (no medido), `REFUTED` (medido en contra).
- Los nombres de símbolo se comparan por **tokens separados por no alfanuméricos**, no por subcadena: así `string` no cuenta como `ring` y `basic` no cuenta como `asic`.

## 1. Inventario real de las dos familias
| Familia | Arquitectura | Kernel (`vermagic`) | Módulos auditados |
| :--- | :--- | :--- | :--- |
| LTU CPE (`afltu_2.4.2`) | `ELF32` ARM little-endian | `3.14.65 SMP preempt mod_unload ARMv7 p2v8` | `ame_core.ko`, `ame_dev.ko`, `ame_dfs.ko` |
| LTU AP (`aflturocket_2.4.2`) | `ELF32` ARM little-endian | idéntico | `ame_core.ko`, `ame_dev.ko`, `ame_dfs.ko` |
| WA `8.7.25` | `ELF32` MIPS big-endian | `2.6.32.68 mod_unload MIPS32_R2 32BIT` | `ath_hal.ko`, `ath_dfs.ko` |
| XC `8.7.25` | `ELF32` MIPS big-endian | idéntico | `ath_hal.ko`, `ath_dfs.ko` |
| XC `8.7.4cs` | `ELF32` MIPS big-endian | idéntico | `ath_hal.ko`, `ath_dfs.ko` (tercera muestra) |

- `CONFIRMED`: las dos familias **no comparten arquitectura ni endianness**. Cualquier lector que asuma una sola codificación produce basura plausible en la otra.
- `CONFIRMED`: `ame_dev.ko` es **byte-idéntico** entre CPE y AP (`298.760 B`, mismo SHA-256). `ame_core.ko` **no** lo es (`3.282.052 B` vs `3.318.764 B`).
- `INFERRED`: toda afirmación extraída de `ame_core.ko` debe declarar de qué imagen viene; de `ame_dev.ko` no hace falta.

## 2. Stage 1518A — LTU: EAB, ASIC0, DMA, IRQ, ioctl/netlink y QAM
### 2.1 `eab_driver.ko` no existe como fichero
- `CONFIRMED`: en cada una de las dos rootfs LTU hay **154 módulos `.ko`** y **ninguno** contiene `eab` en el nombre. La carpeta de módulos es la autoridad: `eab_named_files = []` en ambas.
- `REFUTED`: la premisa de que `eab_driver.ko` sea un módulo separado en estas imágenes.
- `CONFIRMED`: la superficie EAB está **compilada dentro de `ame_core.ko`**: 60 cadenas con el token `eab`, entre ellas `bbp_eab_tx_isr`, `bbp_eab_rx_isr`, `bbp_eab_test_entry`, `eab_txcmd_dump`, `dump_eab_framestop_info`, `update_eab_mc`.
- `CONFIRMED`: `ame_dev.ko` **no** contiene ni una cadena con `eab` (0 de 0). La atribución `EAB -> ame_core.ko` es por tanto unívoca.
- `INFERRED`: el driver Ethernet EAB y el motor AME comparten módulo, así que separarlos en el análisis exige partir por símbolo, no por fichero.

### 2.2 Símbolos: no están stripped
- `CONFIRMED`: `ame_core.ko` (CPE) tiene **9.823 símbolos**, **9.699 definidos**, **2.590 funciones con nombre**, **322 objetos** y **123 imports**. En AP: **9.916** símbolos totales.
- `CONFIRMED`: `ame_dev.ko` tiene **1.855** símbolos y **783** funciones con nombre; es el mismo fichero en CPE y AP.
- `CONFIRMED`: existen `__ksymtab` utilizables (20 entradas en `ame_core.ko`, 18 en `ame_dev.ko`) y **todas** resuelven a una cadena válida.
- Consecuencia: en LTU se puede anclar por nombre real, no por heurística de cadenas.

### 2.3 ASIC0
- `REFUTED`: el token `asic0` aparece en **0 nombres de símbolo** y en **0 cadenas** de `.rodata` con límites de token, en las dos imágenes.
- `CONFIRMED`: el único acierto previo era un falso positivo (`test_hcam_basic`), corregido al pasar de subcadena a token.
- `INFERRED`: la superficie que la documentación llama `ame_ASIC0` se lee en este binario a través de las familias `ame_*` y `bbp_*`, no de un identificador `asic0`.

### 2.4 DMA, IRQ y dispatchers
- `CONFIRMED` (`ame_core.ko`, CPE): **8** funciones de la superficie DMA/BD/ring, entre ellas `pmut_bd_handler`, `ame_core_arx_BD_rate_update`, `ame_core_set_arx_bd_thr`, `bbp_util_rf_dma_capture_and_save`, `bbp_util_rf_dma_capture_and_wait`; y **72** funciones con token `irq`/`isr`/`interrupt` (`tx_isr_handlr`, `rx_isr_handlr`, `hcam0_isr_ut_handler`, `hfe_isr_ut_handler`, `bbp_mtx_enable_isr`).
- `CONFIRMED`: 4 objetos de estado de ISR en `.bss` (`rx_sleep_isr_interval`, `rx_work_isr_interval`, `tx_sleep_isr_interval`, `tx_work_isr_interval`), todos de 4 B.
- `CONFIRMED` (`ame_dev.ko`): **8** funciones DMA (`ame_dma_map`, `ame_dma_buffer_init`, `ame_dma_buffer_deinit`, `ame_dma_unmap`), **14** de IRQ (`ame_tx_isr`, `ame_hcam0_isr`, `ame_hcam1_isr`, `ame_hfe_isr`) y **6** de ioctl (`ame_ioctl` — dos símbolos homónimos —, `ame_dev_ioctl_register`, `ame_dev_ioctl_wCmd_register`, `ame_dev_ioctl_deregister`, `ame_dev_ioctl_wCmd_deregister`).
- `CONFIRMED` (`ame_core.ko`): 3 funciones ioctl (`device_ioctl_uni`, `ame_sched_ioctl_callback`, `ame_add_ioctl_callback`).
- `CONFIRMED`: **0** símbolos con token `netlink`, pero el import `__genl_register_family` está presente. `INFERRED`: hay registro genl sin funciones cuyo nombre lo delate; la búsqueda por nombre no es suficiente en este punto.
- `UNKNOWN`: la profundidad real de los anillos DMA y su descriptor vivo no se miden en estático.

### 2.5 Modulación 1024-QAM / 4096-QAM
- `CONFIRMED`: **0** funciones con token `qam`, pero **3 objetos** (escalares de 4 B en `.rodata`), resueltos y hasheados:
  - `mcsUpThrd_1024` = **93**
  - `startThrd_4096` = **97**
  - `stayThrd_4096` = **90**
- `CONFIRMED`: **55** funciones y **6** objetos en la superficie `mcs`/`modulation`, entre ellos las tablas de potencia por MCS `af_5xhd_mcs_txpwr_freq` (48 B), `af_ltu5_mcs_txpwr_freq` (48 B) y `mcs_txpwr_freq_ptp` (84 B).
- `CONFIRMED`: `af_5xhd_mcs_txpwr_freq` empieza `20, 22, 24, 26, 29, 29, 20, 22` y `af_ltu5_mcs_txpwr_freq` empieza `14, 17, 19, 22, 22, 22, 14, 18` (u32 little-endian leídos en su sección).
- `INFERRED`: los umbrales 93/97/90 gobiernan histéresis de subida y permanencia hacia 1024/4096-QAM; la correspondencia exacta con el scheduler queda para una etapa de decodificación.
- `UNKNOWN`: el contenido campo a campo de `mcs_txpwr_freq_ptp` (84 B) no se interpreta aquí; sólo se localiza, se hashea y se censa.

## 3. Stage 1519A — WA vs XC: radar DFS y tablas HAL
### 3.1 La premisa 8.7.11
- `REFUTED` (local): el árbol contiene **2 rutas** con `8711` y **0 ficheros `.ko`** bajo ellas; `ath_hal.ko` presente = **0**, `ath_dfs.ko` presente = **0**.
- `CONFIRMED`: las versiones realmente disponibles son **WA 8.7.25**, **XC 8.7.25** y **XC 8.7.4cs**. Este informe compara 8.7.25 WA contra 8.7.25 XC, y usa 8.7.4cs como tercera muestra.

### 3.2 `ath_dfs.ko`: mismo tamaño, 14 bytes distintos
- `CONFIRMED`: WA y XC pesan **203.796 B** cada uno, con SHA-256 distinto.
- `CONFIRMED`: difieren exactamente **14 bytes**, en **14 runs de 1 byte**, longitud máxima 1.
- `CONFIRMED`: los 14 son desplazamientos pequeños y positivos: **12 de +4** y **2 de +8** (`0x74→0x78`, `0xbc→0xc0`, `0xb8→0xbc`, `0x70→0x74`, `0x30→0x34`, `0x38→0x40`).
- `INFERRED`: XC va 4 bytes (y dos veces 8) por delante en esos puntos; es releaoyout de direcciones, no un cambio de lógica de radar.
- `CONFIRMED`: los **336** nombres de símbolo son idénticos en ambos (`0` sólo-WA, `0` sólo-XC).

### 3.3 Tablas de radar localizadas por símbolo
- `CONFIRMED` (`ath_dfs.ko`, WA), objetos resueltos en su sección y hasheados:
  - `PRI_black_list` — **44 B = 11 × u32**; palabras big-endian: `833, 1107, 1470, 1666, 1997, 2200, 3333, 3600, …`
  - `PRI_black_list_delta` — **44 B = 11 × u32**; primeras palabras BE: `6, 15, 20, 6, 18, 20, 6, 10`
  - `etsi_radartool_alow` — **12 B = 3 × u32**
  - `fcc_radartool_alow` — **3 B**
  - `dfs_debug_level` — **4 B** (BE `3`)
- `CONFIRMED`: **107** funciones DFS y **5** objetos DFS en ambas familias.
- `INFERRED`: los valores `833..3600` son PRI en microsegundos coherentes con listas de radar ETSI/FCC; la validación contra norma queda fuera del alcance estático.
- `CONFIRMED`: superficies nombradas `etsi_*` y `fcc_*` conviven en el mismo módulo, así que la separación ETSI/FCC es por tabla, no por fichero.
- `UNKNOWN`: el layout de `etsi_radartool_alow` (12 B) no se decodifica campo a campo en esta etapa.

### 3.4 `ath_hal.ko`: tablas HAL y radares del ar9300
- `CONFIRMED`: WA **367.456 B** vs XC **360.896 B**; **292.240** bytes distintos en el prefijo común y **delta de longitud −6.560 B**.
- `CONFIRMED`: los **481** nombres de símbolo son idénticos (`0` sólo-WA, `0` sólo-XC), pese al cambio masivo de bytes.
- `CONFIRMED`: objetos HAL presentes en ambos, 836 B cada uno: `ar9300_11a_table`, `ar9300_11a_half_table`, `ar9300_11a_quarter_table`, `ar9300_11b_table`, `ar9300_11g_table`, `ar9300_11ng_table`, `ar9300_turbo_table`, `ar9300_xr_table`.
- `CONFIRMED`: tablas de radar dentro de `ath_hal.ko`: `ar9300_etsi_radars` **504 B** y `ar9300_fcc_radars` **504 B**, en las dos familias.
- `CONFIRMED`: `ath_hal_buildopts` (16 B) y `ath_hal_version` (9 B) existen como objetos.
- `CONFIRMED`: **416** funciones y **12** objetos en la superficie HAL en ambas familias.

### 3.5 Controles de detección
- `CONFIRMED`: el token `ar9300` aparece en **367** nombres de símbolo de `ath_hal.ko` (WA y XC).
- `REFUTED`: el token `qca9558` aparece en **0** nombres de símbolo y **0** cadenas de `.rodata`. Un HAL "qca9558" no existe con ese nombre en estos binarios.
- `INFERRED`: AR9342 y QCA9558 comparten la línea `ar9300_*`; distinguirlos exige leer tablas de `INI`/EEPROM por símbolo, no buscar el nombre del SoC.

## 4. Lo que estas etapas NO prueban
- `UNKNOWN`: ningún anillo DMA se mide en ejecución; los tamaños de tabla son sólo `size / record_size` aritméticamente posible, no un layout confirmado.
- `UNKNOWN`: ningún filtro de radar se valida contra pulsos reales; la presencia de tablas no implica aceptación o rechazo.
- `UNKNOWN`: no se aplica relocación, así que los punteros dentro de tablas siguen siendo addends de su propia sección.
- `UNKNOWN`: no se carga ningún módulo ni se toca hardware.

## 5. Artefactos de la Wave 80
| Etapa | Artefacto | Estado |
| :--- | :--- | :--- |
| `1518A` | `tools/re/extract_stage1518a_ltu_eab_driver_and_asic0_dma_elf_audit.py` + recibo JSON | `CONFIRMED` |
| `1519A` | `tools/re/extract_stage1519a_xc_vs_wa_ath_hal_and_dfs_radar_pulse_elf_audit.py` + recibo JSON | `CONFIRMED` |
| `1520A` | este documento (`< 175` líneas, 1 `doc-head`, 0 signos de exclamación) | `CONFIRMED` |
| `1521A` | `tests/test_stage1518a_to_1523a_suite.py` (≥ 20 pruebas) | `CONFIRMED` |
| `1522A/1523A` | `tools/verify/verify_stage1523a_wave80_ltu_xc_re_gate.py` + recibo de compuerta | `CONFIRMED` |
