<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1131A runbook de campo en espanol para el rollout PtP (airOS 8 a OpenWrt, OpenWrt full, kit v17) y Guarida Panel1 .84; PREPARE-ONLY, no ejecutado, nada es PRODUCTION_READY -->

# Stage 1131A - Runbook de rollout de produccion PtP y Guarida (ES)

Estado: `RUNBOOK_NOT_EXECUTED`. Dueno de la ejecucion: Codex #1 (live lane).
Este documento se preparo offline: no hubo SSH ni dispositivos tocados.
Ningun valor de este runbook es `PRODUCTION_READY`.

## Mandato de flasheo (verbatim)
OTA: flashear la STA remota PRIMERO con uci-defaults embebidos en el factory.bin SquashFS... luego el AP local SEGUNDO. Nunca traer un radio de produccion al switch local.

## Estados honestos (de 1009A, 1077A, 1080A, 1113A)
- PowerBeam PtP: `NOT_READY`.
- LiteBeam PtP: `NO_EVIDENCE` (no equivale a PowerBeam `NOT_READY`; no hay ninguna evidencia controlada).
- Guarida Panel1 .84: `NO_CONTROLLED_EVIDENCE`, solo lectura, sin control A/A.
- Guarida Panel2: `NOT_READY`. Panel3: `NO_EVIDENCE`.
- El paquete esta `PREPARED_OFFLINE_NOT_RADIO_VERIFIED`.

## Decisiones abiertas
- `aql_threshold` 24000 vs 12000: decide el operador; este runbook no elige.
- Los kits v17 son runtime-only: tras un reboot hay que re-aplicar u hornear la configuracion.
- Re-firmado de `SHA256SUMS`: cubierto por 1109A; verificar antes de empaquetar.

## Pre-requisitos comunes
- Validador offline: `tools/autoresearch/ptp_hybrid_airos8_to_openwrt_ota_validator.py` (Stage 1110A, doc `docs/STAGE1110A_PTP_HYBRID_AIROS8_TO_OPENWRT_OTA_VALIDATOR.md`).
- Verificador pre/post vuelo: `tools/autoresearch/ptp_canary_pre_and_post_flight_verifier.py` (Stage 1097A).
- Kit v17: `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh`.
- Watchdog v17: `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog_v17.sh` (confirmar 45 s, rollback 120 s).
- Imagenes: `firmware/openwrt/pbe5ac_gen2_ptp_kit/openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-factory-sta-242.bin` y `...-factory-ap-241.bin`.
- Ventana de mantenimiento acordada y acceso fuera de banda al sitio local antes de empezar.
- Guardar capturas de cada paso en el receipt del operador; sin captura no hay paso cumplido.

## Paso 1 - Hybrid airOS 8 a OpenWrt (OTA)
Orden obligatorio: STA remota primero, AP local segundo.
1. Preflight read-only del AP airOS 8: `cat /tmp/system.cfg | grep -E '(allow_80211|op_mode|agg_SW_limit|cwmin|cwmax|txqueuelen)'`.
2. Valores esperados Hybrid Mode: `allow_80211=1`, `op_mode=0`, `agg_SW_limit=50000`, `cwmin=3`, `cwmax=7`, `txqueuelen=256`.
3. Generar el plan con `build_step1_plan(...)` del validador 1110A; revisar cada comando antes de usarlo.
4. Habilitar el modo hibrido en el AP airOS 8 con `firmware/openwrt/pbe5ac_gen2_ptp_kit/enable_airos8_ap_hybrid_80211_for_openwrt_sta.sh`. Nota: segun 1110A ese script esta retirado y no lleva knobs; usar los valores del paso 2 por la UI/CLI del AP y registrar la desviacion.
5. Flashear la STA remota con el factory.bin SquashFS (uci-defaults embebidos). No tocar el AP todavia.
6. Con la STA en OpenWrt, validar con `validate_step(capture, expected)`: debe dar `PASS` (otros: `FAIL_AIROS_HYBRID_KNOBS`, `FAIL_OPENWRT_READBACK`, `FAIL_CAPTURE_MALFORMED`).
7. Solo si el enlace hibrido esta estable, pasar al Paso 2. Si falla: rollback del lado STA y detener.

## Paso 2 - Full OpenWrt PtP
1. Flashear el AP local SEGUNDO con el factory-ap-241.bin. Nunca traer un radio de produccion al switch local.
2. Generar el plan con `build_step2_plan(...)` (1110A): el plan incluye solo `--dry-run` y `--verify`; `--apply` es accion humana explicita.
3. Pre-vuelo con el verificador 1097A. Sin parametro de piso MCS el resultado es `SKIPPED_NO_FLOOR`: no cuenta como pass.
4. Ejecutar el kit v17 en este orden, siempre uno por vez:
   - `--dry-run`: default, no escribe nada. Revisar la salida completa.
   - `--apply`: arma primero el watchdog v17; confirmar en 45 s o se revierte a los 120 s.
   - `--verify`: lectura posterior; comparar contra el pre-vuelo y registrar.
   - `--rollback`: ante cualquier degradacion, o cuando el operador lo ordene.
5. Como v17 es runtime-only, despues de cualquier reboot hay que re-aplicar u hornear; no asumir persistencia.
6. Aplicar primero en la STA y luego en el AP; verificar el enlace entre cada uno.
7. Criterio de abort: perdida de enlace sin confirmar, `--verify` en fallo, o el watchdog dispara. Detener y volver al estado previo.

## Activacion de Panel1 .84 (GATEADA)
Panel1 .84 no se activa hasta cumplir ambas condiciones:
- Confirmacion <memorymaster-id>: 2x5 probes AP-local completos y registrados.
- SG-01: backbone PoE, 0 writes (ninguna escritura sobre el backbone PoE).
Otras guardas: SG-03 a SG-05 son zero-touch del lado AP.
Pasos tras cumplir las condiciones:
1. Lectura pura del estado actual de Panel1 .84 y guardado de la linea base.
2. Plan `--dry-run` del kit; el operador revisa y autoriza.
3. `--apply` con watchdog armado; luego `--verify`.
4. Si cualquier gate no esta confirmado: no activar y escalar al operador.

## Despues de cada paso
- Archivar capturas y salidas de `--verify` junto al receipt del operador.
- No declarar exito por exit 0 o "terminado": solo por la lectura observada contra lo esperado.
- LiteBeam permanece `NO_EVIDENCE` hasta que exista evidencia controlada propia.
- Reportar a Codex #1 (live lane) el resultado de cada paso, incluidos los fallos.

## Evidencia
- Receipt: `artifacts/autoresearch/stage1131a_guarida_and_ptp_production_rollout_runbook_es.json`.
- `evidence_class` es `PRODUCTION_ROLLOUT_RUNBOOK_ES`; `execution_status` es `RUNBOOK_NOT_EXECUTED`.
- Claim id: `FMX-STAGE1131A-GUARIDA-AND-PTP-PRODUCTION-ROLLOUT-RUNBOOK-ES`.
