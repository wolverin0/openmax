<!-- doc-head: DEEPSEEK_OPENCODE_BRIEF.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 81A — DeepSeek 4.1 Flash (`OpenCode`) Firmware Boundary & Binary Audit Brief

## 1. Contexto Rápido del Proyecto (`FuturaMAX`)
Estamos auditando y optimizando el stack completo de firmware de Ubiquiti en tres arquitecturas reales del laboratorio (`<projects>/futuraMAX`):
1. **`airMAX AC` (`WA.v8.7.25` `AR9342` y `XC.v8.7.25` `QCA9558` + `QCA988x`)**:
   - Módulos kernel extraídos en `artifacts/`: `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko`, `ath_hal.ko`, `ath_pktlog.ko`.
   - Ya documentamos `UPH-BUG-01..08` en [`docs/UBIQUITI_AIRMAX_AC_UPH_BUG_DISCLOSURE_REPORT.md`](<repo>/docs/UBIQUITI_AIRMAX_AC_UPH_BUG_DISCLOSURE_REPORT.md) y `UMAC-BUG-01..05` / `ATHDEV-BUG-01..04` en [`docs/STAGE75A_UMAC_AND_ATH_DEV_FULLREA_BINARY_DISSECTION.md`](<repo>/docs/STAGE75A_UMAC_AND_ATH_DEV_FULLREA_BINARY_DISSECTION.md).
2. **`LTU` (`AF-LTU.v2.3.1` `Beetle` ARM Cortex-A7 + `ame_ASIC0` + `eab_driver.ko`)**:
   - Módulos kernel extraídos en `artifacts/`: `ame_core.ko`, `ame_dev.ko`, `eab_driver.ko`.
   - Ya documentamos `LTU-BUG-01..08` en [`docs/UBIQUITI_LTU_FIRMWARE_BUG_DISCLOSURE_REPORT.md`](<repo>/docs/UBIQUITI_LTU_FIRMWARE_BUG_DISCLOSURE_REPORT.md).

## 2. Tu Misión (`OpenCode DeepSeek 4.1 Flash`)
1. **Leé los reportes de disclosure actuales**:
   - [`docs/UBIQUITI_LTU_FIRMWARE_BUG_DISCLOSURE_REPORT.md`](<repo>/docs/UBIQUITI_LTU_FIRMWARE_BUG_DISCLOSURE_REPORT.md)
   - [`docs/UBIQUITI_AIRMAX_AC_UPH_BUG_DISCLOSURE_REPORT.md`](<repo>/docs/UBIQUITI_AIRMAX_AC_UPH_BUG_DISCLOSURE_REPORT.md)
   - [`docs/STAGE75A_UMAC_AND_ATH_DEV_FULLREA_BINARY_DISSECTION.md`](<repo>/docs/STAGE75A_UMAC_AND_ATH_DEV_FULLREA_BINARY_DISSECTION.md)
2. **Inspeccioná las superficies de frontera (`userspace <-> kernel` y `OTA/management`) en `artifacts/`**:
   - Revisá los binarios y módulos extraídos en `artifacts/` (`SquashFS`, daemons de administración web/discovery/OTA, `ioctl`/`procfs`/`sysfs`/`netlink` handlers en `ubnt_poll_host.ko`, `umac.ko`, `ame_core.ko`, `ame_dev.ko`, `eab_driver.ko`).
3. **Primer Paso Interactivo con el Operador (En Español)**:
   - Apenas termines de leer esos 3 documentos y listar los binarios disponibles en `artifacts/`, **presentale al operador un resumen corto (máximo 10 líneas en español)** de las 3 superficies más prometedoras que ves en `artifacts/` y **hacele una pregunta clara con opciones numeradas (1, 2, 3)** para que él elija por cuál superficie querés empezar a profundizar primero (por ejemplo: `1)` Daemons de red/discovery/web en SquashFS, `2)` Parsers de tramas OTA / management frames en `ubnt_poll_host.ko` y `umac.ko`, o `3)` Frontera `ioctl`/`mmap`/`netlink` en `LTU` `ame_dev.ko` / `ame_core.ko` + preparación de reporte de alto impacto).
   - **Regla de seguridad del repo**: Nunca modifiques `mtd0`/`mtd1`/`mtd5` ni toques `198.18.0.2` (`ether2-sw-poe200`). Todo análisis sobre binarios se hace sobre las copias locales en `artifacts/`.
