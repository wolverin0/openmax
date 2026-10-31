<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head -->
*STAGE1736A — controlador PtP-Colo con retune seguro a 5200 MHz por scan_list y blueprint de cohortes del Panel 2*
# STAGE 1736A — 5200 MHz scan_list-safe y Panel 2 en 4 cohortes

## 0. Frontera
- **100% offline**: `ssh_connections=0`, `radio_writes=0` en ambos recibos. El controlador no abre sockets.
- Primero se ejecutó `orca orchestration check --run <orca-id> --json`. Orca respondió **`worker_cannot_coordinate_own_run`**: este worker pertenece al run, así que sólo puede usar `check` sin `--run` y `send`. Queda registrado.

## 1. Stage 1734A — retune seguro por scan_list
- `CONFIRMED` (readback de `1669A`, host `198.18.0.92`): `radio.1.scan_list.status=enabled` y `radio.1.scan_list.channels=6035,5170,5200`, con `dfs.status=enabled`, `countrycode=511`, `chanbw=0` y `freq=0`.
- `CONFIRMED`: los tres canales existentes se conservan (`keep_ok=1`) y **5200 MHz ya está en la lista** (`target_5200=1`).
- `INFERRED`: retunear a **5745/5825** sacaría al STA de su lista; **5200 MHz (UNII-1, no-DFS)** mantiene el enlace alcanzable.
- Plan codificado: **Step-0a** expande `scan_list` a `6035,5170,5200,5745,5825` con lectura de vuelta; **Step-0b** retune del AP a **5200 MHz** + `allow_80211=1` + `op_mode=0` con **watchdog de 60 s**; **Step-1** flash del `factory.bin` certificado en `1668A` con `ban_time=1200`.
- `CONFIRMED`: `executable=0`. Step-0a y Step-0b tienen sus precondiciones satisfechas; **Step-1 está bloqueado por construcción** porque esta herramienta no tiene ruta de ejecución.

## 2. Stage 1735A — Panel 2 en 4 cohortes
- `CONFIRMED`: el Panel 2 (`198.18.0.5`) declara **22 CPEs**; el fichero de radiografía **no expone** una lista por CPE bajo las claves inspeccionadas (`cpes_discovered=0`), así que las etiquetas se rellenan por conteo declarado.
- `CONFIRMED`: reparto en **4 cohortes** de `6, 6, 5, 5` = **22** miembros.
- `CONFIRMED`: la tasa de fallo del Panel 2 tomada de `1704A` es **0.3636** (8 de 22).
- `CONFIRMED`: **4 de 4 cohortes bloqueadas**; cada una exige tres compuertas: **G1** doble bind 4addr limpio, **G2** `brport/state=3` en todos los puertos WDS y **G3** healer armado con `ban_time=1200`.
- `INFERRED`: el Panel 1 sano (tres CPEs en MCS7 NSS2) es la referencia de oro; ninguna cohorte del Panel 2 se declara buena sin medir G1 y G2.
- `UNKNOWN`: el estado real de 4addr y `brport` por cohorte; no se midió.

## 3. Lo que no se prueba
- `UNKNOWN`: que el STA reingrese tras el retune a 5200 MHz.
- `UNKNOWN`: la composición real de las cohortes (sin lista por CPE en la radiografía).
- `UNKNOWN`: la eficacia del healer en el Panel 2, sólo probada en el Panel 1.

## 4. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1734A` | `tools/rollout/run_stage1734a_ptp_colo_5200mhz_scanlist_safe_controller_update.py` + recibo |
| `1735A` | `tools/rollout/run_stage1735a_guarida_panel2_22cpe_staged_cohort_blueprint.py` + recibo |
| `1736A` | este documento (menos de 160 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1738A..1739A` | `tests/test_stage1734a_to_1739a_suite.py` y la compuerta de la wave |
