<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head -->
*STAGE1700A — controlador de rollout PtP-Colo (.62/.54) y plano de migración por etapas del Panel 3 de Guarida (.83)*
# STAGE 1700A — Rollout PtP-Colo y Panel 3

## 0. Frontera dura
- **Dry-run por defecto y único modo implementado.** `--execute` aborta antes de tocar nada. Registrado: `ssh_connections=0`, `radio_writes=0`.
- No se escribe en ninguna radio. El entregable es un **plan** con precondiciones, no una ejecución.

## 1. Stage 1698A — controlador PtP-Colo
### 1.1 Precondición estricta mtd0/1/4/5
- `CONFIRMED`: `stage1657a` registra los hashes de partición por host. Para `.54` (`LiteBeam 5AC`, `board.sysid 0xe7f9`) incluye `mtd0` con `sha256 988de514…` y `mtd1` con `63213a0b…`.
- `CONFIRMED`: el controlador exige que el conjunto observado coincida en **las cuatro** particiones antes de considerar el plan ejecutable.
- `CONFIRMED`: sin `--observed-hashes` la precondición es **`NOT_EVALUATED`** y los tres pasos quedan **BLOCKED**. Resultado medido: `executable=0`, `blocked_steps=3`.
- `REFUTED`: que `.62` tenga hashes en `1657a`; el recibo es del par `.62↔.54` pero solo aporta el conjunto de `.54`, así que `.62` queda sin precondición verificable.

### 1.2 Pasos codificados
| Paso | Objetivo | Acción | Bloqueo |
| :--- | :--- | :--- | :--- |
| Step-0 | `198.18.0.91` | retune de **6035 MHz** a **5755 MHz**, `allow_80211=1`, `op_mode=0` | sí |
| Step-1 | `198.18.0.92` | flash OTA `factory.bin` SquashFS + `99-fmx-4addr-verify` + `fmx_ap_4addr_peer_healer.sh ban_time=1200` + `fmx_ptp_rollback_watchdog.sh` | sí |
| Step-2 | `198.18.0.91` | flash completo de AP OpenWrt tras verificar `.54` como STA | sí |

- `CONFIRMED`: `1657a` declara **`hybrid_ready=false`**, de modo que Step-1 depende de la lectura de vuelta de Step-0.
- `INFERRED`: el orden 0→1→2 es el único que no deja el enlace sin AP funcional en ningún instante.

## 2. Stage 1699A — Panel 3 de Guarida
### 2.1 Estado real
- `CONFIRMED`: el Panel 3 (`198.18.0.6`) emite `PUBLIC_TERM_0005` en **5755 MHz** y `stage1674a` mide **3 CPEs**: `cpe_9` (−60 dBm, 2700 m), `cpe_235` (−57 dBm, 150 m), `cpe_238` (−56 dBm, 450 m), todas con `144.4 Mbps` de RX.
- `CONFIRMED`: la topología declara **6 CPEs** en el Panel 3, pero solo hay **3** medidas → **3 UNKNOWN**.
- `REFUTED`: que el Panel 3 tenga 6 CPEs verificadas; el recibo solo sostiene 3.

### 2.2 Referencia del Panel 1 y healer
- `CONFIRMED`: `stage1674a` marca el Panel 1 (`198.18.0.7`) como **sano**: tres CPEs en MCS7 NSS2 con **0 %** de pérdida tras el post-heal.
- `INFERRED`: la corrección de doble bind del Panel 1 y el healer con `ban_time=1200` son el patrón a replicar en el Panel 3.

### 2.3 Olas propuestas (todas bloqueadas)
1. **P3-W0** — inventariar las 6 configuradas; hoy 3 medidas.
2. **P3-W1** — aplicar el arreglo de doble bind y el healer `ban_time=1200`.
3. **P3-W2** — migrar de 2 en 2 CPEs con watchdog de rollback.
4. **P3-W3** — verificar 4addr WDS en las tres capas por CPE.

- `CONFIRMED`: `waves=4`, `blocked_waves=4`. Nada se ejecuta sin sesión de operador.

## 3. Lo que no se prueba
- `UNKNOWN`: la identidad de las 3 CPEs no medidas del Panel 3.
- `UNKNOWN`: el estado de `.62` en mtd; no hay hashes en el recibo vivo.
- `UNKNOWN`: que el healer con `ban_time=1200` cure el doble bind en el Panel 3; solo está probado en el Panel 1.

## 4. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1698A` | `tools/rollout/fmx_ptp_colo_and_guarida_panel3_staged_controller.py` + `stage1698a_ptp_colo_step0_5ghz_retune_and_step1_plan_receipt.json` |
| `1699A` | `stage1699a_guarida_panel3_6cpe_staged_migration_blueprint_receipt.json` |
| `1700A` | este documento (menos de 180 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1701A..1703A` | filas en `results.tsv`, `tests/test_stage1698a_to_1703a_suite.py` y la compuerta de la wave |
