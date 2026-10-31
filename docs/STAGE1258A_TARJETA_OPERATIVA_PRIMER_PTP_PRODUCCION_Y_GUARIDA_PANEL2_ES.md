<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1258A tarjeta operativa en español (actualizada en 1281A) para el primer enlace PtP de producción (v17, STA primero) y el camino Guarida Panel2; ahora citan dos envoltorios CLI nuevos (backup mtd 1278A y orquestador 1279A) verificados solo en dry-run offline (DRY_RUN_ONLY), nunca ejecutados en un radio; watchdog 45 s/120 s según el script real; brechas cerradas y abiertas; sección explícita de lo NO probado -->
# Stage 1258A - Tarjeta operativa: primer PtP de producción y camino Guarida Panel2

Estado: `CARD_NOT_EXECUTED`. Escrita completamente offline a partir de documentos y scripts que existen en el repo; ningún equipo fue tocado. Actualizada en 1281A con los dos envoltorios CLI de 1278A y 1279A.
Quien ejecuta: el lane live (Codex #1), con la compuerta del operador intacta. Esta tarjeta no autoriza nada por sí sola.
Etiquetas: CONFIRMED / INFERRED / UNKNOWN, más clase de evidencia (CONFIRMED_LIVE_HARDWARE, CONFIRMED_STATIC_BINARY, SIMULATED_MODEL_ONLY).

## 0. Veredicto de hoy (leer primero)

- Veredicto vigente: NO_GO para PowerBeam PtP, LiteBeam PtP y Panel1-Guarida (`docs/STAGE1128A_PTP_PRODUCTION_GO_NO_GO_DOSSIER.md`).
- Lo confirma, en solo lectura, `python tools/verify/ptp_production_go_no_go_dossier_generator.py` (sin `--write-receipt` no escribe nada). Hoy imprime `overall: NO_GO`, cohorte INCOMPLETE (0 de 18 pares) y 4 decisiones abiertas.
- PowerBeam: NOT_READY. LiteBeam: NO_EVIDENCE, no es equivalente a PowerBeam. Panel2: NOT_READY (`docs/STAGE1077A_PTP_AND_GUARIDA_PREROLLOUT_READINESS_MATRIX.md`).
- Esta tarjeta describe cómo se ejecutaría el primer enlace cuando el veredicto cambie. No lo cambia.

## 1. Comandos: dos envoltorios nuevos (solo DRY_RUN_ONLY) y la secuencia real de respaldo

Nivel de evidencia de los envoltorios: DRY_RUN_ONLY. Se construyeron y se probaron sin red, contra instantáneas locales y fixtures; ninguno se ejecutó jamás contra un radio. Recibos: `artifacts/verification/stage1278a_production_mtd_backup_cli_receipt.json` y `artifacts/verification/stage1279a_production_ptp_one_command_receipt.json`. Qué no prueban: sección 10.

| Paso | Dónde | Comando (PC del operador; `AP_IP`, `STA_IP`, `DIR` son valores a completar) |
| --- | --- | --- |
| A | PC | `python tools/verify/ptp_production_go_no_go_dossier_generator.py` (debe decir GO; hoy dice NO_GO) |
| B | PC | `python tools/deploy/run_production_ptp_canary_one_command.py --ap-ip AP_IP --sta-ip STA_IP --mode dry-run --out-dir DIR` (paquete de pre-vuelo de solo lectura; este modo nunca ejecuta, ni con `--execute`) |
| C | PC | `python tools/deploy/backup_and_verify_production_ptp_mtd.py --ap-ip AP_IP --sta-ip STA_IP --out-dir DIR` (lee por SSH mtd0/1/4/5 de ambos extremos, dos lecturas, sha256 local, chequeo estructural de ART; clave solo por la variable `FMX_SSH_PASSWORD` o por prompt, nunca como argumento) |
| D | PC | `python tools/deploy/run_production_ptp_canary_one_command.py --ap-ip AP_IP --sta-ip STA_IP --mode openwrt-v17-step2 --out-dir DIR` (imprime y valida el plan; sin `--execute` no hace nada) |
| E | PC | El mismo comando del paso D más `--execute --confirm "EXECUTE openwrt-v17-step2 AP=AP_IP STA=STA_IP"` (frase exacta; agregar `--dfs` si el canal es DFS) |

Cómo se frena el paso E (fail-closed, derivado de `tools/deploy/run_production_ptp_canary_one_command.py`): exige veredicto GO del generador 1128A, el manifiesto de 1278A en el mismo `DIR`, en vivo, fresco (6 h) y aprobado para ese par exacto, y todas las dependencias del modo sin BLOCKED. Rechaza hosts del backbone SG-01 y AP igual a STA. Salidas: 0 plan o éxito, 1 falló con rollback limpio, 2 uso o host inválido, o falta la frase, 3 precondición, 4 dependencia BLOCKED, 5 falló y el rollback quedó incompleto. Hoy el paso E terminaría en 3 (NO_GO).
- `--mode openwrt-v17-step2` NO flashea firmware: supone que ambos radios ya corren OpenWrt (lo verifica antes de escribir). Aplica el kit v17 y el watchdog v17 por SSH, STA primero, con captura previa y posterior del verificador 1097A importado como biblioteca.
- `--mode hybrid-step1` y `--mode airos-stock-tuned` hoy tienen pasos BLOCKED (emisión SquashFS 988A, actuadores retirados, flasheador atado al banco, sin aplicador airOS): ejecutar termina en exit 4.
- `--mode rollback` corre el `--rollback` del kit v17 (STA primero) y luego volcados de salud de solo lectura; exige igualmente `--execute` y la frase exacta, pero no pide GO ni manifiesto.
- Opciones extra: `--user` (por defecto root en el envoltorio, ubnt en el backup) y `--phy`. El backup también acepta `--dry-run`, `--snapshot-dir` y `--receipt-out` (solo con `--dry-run`).
- Los dos comandos corren en la PC; la autenticación SSH del envoltorio la resuelve el propio ssh (clave o agente).

Secuencia real subyacente en el radio, como respaldo manual si el envoltorio falla (el envoltorio solo ordena y valida estos mismos scripts):

| Paso | Dónde | Comando real |
| --- | --- | --- |
| 1 | PC del operador | `python tools/verify/ptp_production_go_no_go_dossier_generator.py` (debe decir GO; hoy dice NO_GO) |
| 2 | Radio (BusyBox sh, root) | `sh fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh --dry-run` (no escribe) |
| 3 | Radio | `sh fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh --apply` (agregar `--dfs` si el canal es DFS) |
| 4 | Radio | `sh fmx_ptp_rollback_watchdog_v17.sh --arm --peer HOST` (agregar `--dfs` si DFS) |
| 5 | Radio | `sh fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh --verify` |

- Ambos scripts viven en `firmware/openwrt/pbe5ac_gen2_ptp_kit/`: `fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh` y `fmx_ptp_rollback_watchdog_v17.sh`.
- Banderas reales del kit: `--dry-run` (por defecto), `--apply`, `--verify`, `--rollback`, `--root` (solo emulación offline, nunca en un radio), `--phy` (por defecto phy2), `--iface` (por defecto phy2-sta0; en el AP usar la interfaz AP), `--dfs`, `--watchdog-seconds N`.
- Banderas reales del watchdog: `--arm` (exige `--peer HOST`), `--rollback`, `--root`, `--iface`, `--phy`, `--dfs`, `--watchdog-seconds N`.
- Sigue faltando (UNKNOWN, no se inventa): un CLI propio y suelto para el verificador canary 1097A (`tools/autoresearch/ptp_canary_pre_and_post_flight_verifier.py` solo tiene `build_plan` y `verify`; el envoltorio los usa como biblioteca solo en `openwrt-v17-step2`). Los citados 1101A `--role pre|post` siguen sin existir (sección 9).
- El flasheo OTA de la imagen SquashFS (STA primero, AP después) sigue sin comando listo: ver sección 10.

Brechas de 1258A tras 1278A y 1279A (estado, no promesa):
- Cerradas parcialmente, solo como herramienta construida y verificada en dry-run: respaldo mtd0/1/4/5 para pares arbitrarios (incluye mtd4) y envoltorio de un comando para el v17 con compuertas, plan validado y rollback (sin flasheo OTA de firmware).
- Abiertas: nunca se ejecutó en un radio; no existe hash de referencia de mtd4 de producción (el primer respaldo en vivo lo crea y no lo compara con nada); el watchdog v17 nunca corrió en un radio; emisión SquashFS 988A BLOCKED; Guarida Panel 2 sin prueba de campo; typos de 1101A sin corregir; sin CLI 1097A suelto; el nombre de interfaz AP `phy2-ap0` del envoltorio se derivó de un patrón, no de una captura.

## 2. Pre-chequeos (todos deben ser verdaderos; si uno falla, no se sigue)

1. Veredicto: el paso 1 de la sección 1 dice GO. Si dice NO_GO, fin.
2. Alcance: solo equipos del enlace elegido; nunca un radio de producción llevado al switch local; nunca pedir al operador subir a una torre (`AGENTS.md`).
3. Alcanzabilidad: ambos extremos responden desde el host del operador y hay acceso fuera de banda al otro extremo. Registrar modelo, firmware, MAC e IP (`docs/STAGE1083A_PTP_LB_AND_GUARIDA_PANEL2_ROLLOUT_DOSSIER.md`, sección 2).
4. Backup y hash de mtd0, mtd1, mtd4 y mtd5 en ambos extremos, antes de cualquier flasheo. Particiones protegidas: mtd0 (u-boot), mtd1 (u-boot-env), mtd5 (EEPROM/ART); nunca se escriben.
   - Herramienta para producción: el paso C de la sección 1 (1278A, `tools/deploy/backup_and_verify_production_ptp_mtd.py`), solo dry-run verificado. La herramienta vieja `tools/inventory/probe_and_backup_pbe5ac_gen2_ground_up.py` está atada al par de banco y no recibe argumentos: no sirve para producción.
   - El verificador `tools/autoresearch/ptp_canary_pre_and_post_flight_verifier.py` hashea solo mtdblock0/1/5 y compara antes contra después. No incluye mtd4 y no hay hash de referencia de producción en el repo: el respaldo del paso C registra el primero (mtd4 es configuración y puede cambiar legítimamente; no es objetivo de invariancia). Gap abierto, sección 10.
5. Backbone SG-01 intacto: cero escrituras sobre el router de borde, `ether2-sw-poe200` y los switches PoE; nunca deshabilitar ni ciclar esa interfaz. Verificar el plan de cambios con `tools/autoresearch/guarida_panel1_to_panel2_bench_interop_gate_evaluator.py --changeset ARCHIVO.json` (solo evalúa el plan, exit 0 solo con GATE_PASS).
6. Dry-run primero: el paso B de la sección 1 y el paso 2 de la secuencia real en ambos extremos; guardar su salida como evidencia.
7. Línea base: capturar antes del cambio con las listas de comandos de solo lectura de `build_plan` en el verificador 1097A y en `tools/autoresearch/ptp_production_lb5ac_pbe5ac_canary_monitor.py`.
8. Decisión abierta del operador: `aql_threshold` 24000 (perfil campeón) contra 12000 (kit v17). El kit v17 escribe 12000. Registrar la elección antes de aplicar; no elegir en silencio.
9. Clase de canal decidida: DFS o no DFS. Fija la ventana (sección 4).
10. Ventana de mantenimiento y persona de respaldo física definidas (dossier 1083A).

## 3. Orden de ejecución (mandato del proyecto, verbatim)

> OTA: flash the remote STA FIRST with uci-defaults embedded in the custom SquashFS factory.bin (exact IP, disabled=0, SSID, freq, WPA2, wds=1, 24 dBm, stp=0, champion profile); then flash the local AP SECOND. Never bring a production radio to the local switch.

1. STA remoto primero, AP local después (`docs/STAGE1053A_PRODUCTION_PTP_OTA_ROLLOUT_RUNBOOK.md`, `docs/STAGE1101A_PTP_PRODUCTION_CUTOVER_ZERO_TOUCH_CHECKLIST.md`).
2. En cada extremo: dry-run, apply, arm del watchdog, verify (pasos 2 a 5 de la sección 1), post-vuelo con el verificador 1097A.
3. Snapshot: el kit lo crea en `--apply` en `/etc/fmx-pbe5ac-v17-snapshot/`. El watchdog lo reutiliza si es válido. Armar el watchdog DESPUÉS de `--apply` es seguro solo porque el snapshot ya existe; si no existiera, `--arm` tomaría uno del estado ya cambiado.
4. Los kits v17 son solo runtime: un reinicio descarta todo. Tras cualquier reboot, reaplicar u hornear el kit en la imagen (decisión abierta del operador).

## 4. Qué hace realmente el watchdog (según el script, no según la prosa)

Hay tres mecanismos de 45 s / 120 s. Ninguno restaura firmware ni flash.

| Mecanismo | Qué dispara el rollback | Qué restaura | Nivel de evidencia |
| --- | --- | --- | --- |
| Kit v17 `--apply` (ventana interna 45 s, 120 s con `--dfs`) | Que la interfaz no pase a operstate y carrier arriba dentro de la ventana, o que falle una escritura | AQL, aql_threshold, aqm, lowat, qdisc desde el snapshot | Ciclo dry-run/apply/verify/rollback del kit: CONFIRMED_LIVE_HARDWARE, solo banco (`docs/STAGE1175A_LIVE_PBE5AC_V17_VERIFIED_LIFECYCLE.md`, `docs/STAGE1043A_LIVE_PBE5AC_V16_KIT_DRYRUN_APPLY_VERIFY_ROLLBACK.md`, que es el kit v16). El vencimiento de la ventana: NO probado en vivo |
| `fmx_ptp_rollback_watchdog_v17.sh --arm --peer HOST` | Dos iteraciones seguidas de ping fallido (`ping -c 3 -W 2`, luego `sleep 1`) dentro de la ventana | Lo mismo que arriba, más `uci import`, `uci commit wireless` y `wifi reload` si hay export | Estático y simulado: raíz falsa y stubs (`docs/STAGE1099A_PTP_ROLLBACK_WATCHDOG_V17.md`, `docs/STAGE1100A_WATCHDOG_V17_AUDIT_AND_RESTRICTED_PATH.md`). NO probado en vivo |
| `fmx_ptp_rollback_watchdog.sh --apply` (guardia de arranque, 984A) | No llegar a un ping exitoso más lectura nativa verificada antes del plazo monotónico de 45 s / 120 s | Solo la transacción nativa en RAM | CONFIRMED_STATIC_BINARY: 39 tests con stubs, sin esperar 45 ni 120 s reales (`docs/STAGE985A_WATCHDOG_LOSS_DEADLINE_AND_FAULT_TESTS.md`). Física: UNKNOWN |

Lectura correcta, por el código del v17:
- 45 s (no DFS) o 120 s (DFS, `--dfs`) es la longitud de la ventana de observación. No es "45 s de enlace perdido": el rollback sale tras DOS fallos consecutivos, normalmente antes de que termine la ventana (cada ráfaga fallida puede tardar unos 6 s).
- Si el enlace aguanta toda la ventana, imprime `LINK_HELD` y termina con exit 0. Después de eso no queda ningún guardián armado.
- No dispara por pérdida porcentual, latencia ni throughput; solo por ping. Esos umbrales son del operador (sección 6).
- La ventana cuenta iteraciones, no reloj (nota `shortcut` del propio script): la ventana real puede ser más larga.
- Códigos de salida del v17: 0 enlace sostenido, 1 rollback limpio, 2 rollback fallido; `--rollback` manual: 0 ok, 2 falló, 3 snapshot inválido (no escribe nada).
- Verifica `md5sum -c manifest` del snapshot antes de restaurar; si falla, no escribe.
- `FMX_PING_RESULT` es solo de pruebas: jamás en un radio.

Garantizado por el script: no restaurar un snapshot corrupto, y no hacer rollback por un solo ping perdido. Probado en: raíz falsa en la PC (1100A). NO probado en un radio real.

## 5. Go / no-go

GO solo si TODO es cierto:
- El generador de 1128A dice GO: todos los veredictos READY, cohorte COMPLETE (18 pares), procedencia CLEAN, `disguised_count` 0 y ninguna decisión abierta sin resolver.
- Los pre-chequeos de la sección 2 pasaron, con evidencia guardada.
- El operador dio la compuerta (`gate: operator`) para este enlace en concreto.

NO-GO ante cualquiera: veredicto NOT_READY o NO_EVIDENCE, equipo inalcanzable, hash mtd no tomado, dry-run con salida inesperada, o aviso de que se tocaría SG-01.

Un GO del generador no equivale a PRODUCTION_READY: solo permite el siguiente paso escalonado.

## 6. Abortar y volver atrás

Umbrales de aborto del canary (basta uno; no promediar), de `docs/STAGE1125A_PTP_PRODUCTION_CANARY_MONITORING_AND_ABORT_CRITERIA.md`:
- Pérdida mayor a 2 %, p99 mayor a 40 ms, o desbalance de cadenas mayor a 6 dB.
- Un radar DFS (CAC) es DEGRADED, no aborto: no revertir por eso.
- Cambio en el hash mtd antes contra después (`FAIL_MTD_CHANGED`) es aborto inmediato y escalada.

Pasos:
1. Dejar que el watchdog actúe si el enlace cayó; no pelear contra él.
2. Rollback manual del extremo afectado, STA primero si cambiaron ambos: `sh fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh --rollback` o `sh fmx_ptp_rollback_watchdog_v17.sh --rollback`.
3. Volver a leer el perfil y comparar con la línea base. Si falta un cuadro de salud, correr una vez `sh fmx_ptp_v17_one_shot_health_dump.sh --peer HOST` (solo lectura, 1123A).
4. No reaplicar tras un rollback sin un pre-vuelo nuevo. Un rollback es un resultado válido y se reporta.
5. Si un rollback falla (exit 2 o 3): escalar al operador. No hay restauración de firmware automática en este repo. Corrección de 1281A: `firmware/openwrt/pbe5ac_gen2_ptp_kit/restore_stock_airos8_with_known_cfg.sh` es el mismo stub retirado de la sección 9 (con `--apply` termina en exit 65): no restaura nada, y 1279A lo marca como dependencia BLOCKED.

## 7. Qué registrar

Por radio y por extremo, en el receipt del lane live (`docs/STAGE1053A_PRODUCTION_PTP_OTA_ROLLOUT_RUNBOOK.md`, contrato `result_receipt_contract`):
- `controlled_aa_valid`, `physical_workload_acceptance`, `zero_false_positive`, `evidence_provenance_class`. Falta cualquiera, o es fixture sintético: el resultado es inválido.
- Modelo (PowerBeam o LiteBeam, por separado), canal DFS o no, ventana usada, hash del kit y del watchdog, decisión de `aql_threshold`.
- Salidas de dry-run, apply, arm y verify con sus exit codes; hashes mtd antes y después; si hubo rollback, su disparador y exit code.
- Captura pre y post del verificador 1097A y muestras del monitor 1121A.

## 8. Guarida Panel2 (22 CPEs): camino, sin acciones en vivo

Solo lectura de documentos. Ninguna acción en vivo desde esta tarjeta; la compuerta del operador sigue en pie.
- Estado: 882A `ready_count` 0 de 34 endpoints, INCOMPLETE; 1010A auditó solo Panel3, no Panel2; veredicto NOT_READY apoyado solo en 882A (`docs/STAGE1077A_PTP_AND_GUARIDA_PREROLLOUT_READINESS_MATRIX.md`, `docs/STAGE1080A_PTP_AND_GUARIDA_ROLLOUT_DECISION_MATRIX_V17.md`).
- Dossier de prerrequisitos: `docs/STAGE1083A_PTP_LB_AND_GUARIDA_PANEL2_ROLLOUT_DOSSIER.md`, sección 6. Compuerta <memorymaster-id>: confirmación local del AP en 2 rondas consecutivas de 5 sondeos, ambas seguidas. Pasarla no es PRODUCTION_READY.
- Seguridad: SG-01 (cero escrituras al backbone) y SG-03 a SG-05 (zero-touch del lado AP, sin tocar CPEs de stock); evaluador `docs/STAGE1111A_GUARIDA_PANEL1_TO_PANEL2_BENCH_INTEROP_GATE_EVALUATOR.md`. Nunca migrar un AP PtMP sin interop AP-side completa probada en banco con CPE airOS 8 de stock.
- Camino propuesto, ya escrito (canario Path A, cero flash, `gate: operator`): `docs/STAGE82B_IPTV_TRIPLE_PLAY_QOE_READINESS_AND_PANEL2_RUNBOOK.md`, sección 5.2: verificar 22 de 22 CPEs asociadas, armar guardián de 45 s, aplicar perillas volátiles, verificar y desarmar.
- Las cifras de 82B para Panel2 (goodput, p95, jitter IPTV) son SIMULATED_MODEL_ONLY (banco más SimPy); no son medidas de torre.

## 9. Hallazgos sobre documentos previos (para corregir, no corregidos aquí)

- `docs/STAGE1101A_PTP_PRODUCTION_CUTOVER_ZERO_TOUCH_CHECKLIST.md` paso 1 y 5 cita `ptp_canary_pre_and_post_flight_verifier.py --role pre` y `--role post`: ese archivo no tiene CLI de `--role` (su `__main__` solo escribe el receipt). Son funciones para el lane live.
- El mismo 1101A paso 4 cita `--arm` sin `--peer`; el script termina con exit 64 (usage) si falta `--peer`.
- 1101A paso 6 y 1125A dicen "rollback tras 45 s de enlace perdido": el script hace rollback tras dos pings fallidos dentro de una ventana de 45 s (sección 4).
- El manifiesto `firmware/openwrt/pbe5ac_gen2_ptp_kit/pbe5ac_remote_ota_prebaked_manifest_20261026.json` (Stage 62A) todavía declara un timeout de 180 s y hashes de watchdogs anteriores a 984A y v17: discrepa de la ley 45 s / 120 s.
- Los watchdogs por unidad `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog_ap_241.sh` y `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog_sta_242.sh` son hoy un stub retirado (mismo sha256 `edf58be7c1335da3d6e1daf3200ee63acf503e0c52dacf7ec7270480165aba4a`; `--apply` y `--rollback` terminan con exit 65). Ninguno restaura nada. El manifiesto 62A los sigue listando con otros hashes.
- Los archivos uci-defaults del árbol, `firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-pbe5ac-ptp` y `firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-pbe5ac-ptp-sta-242`, son el mismo stub retirado (974 B, mismo sha256): el contenido que pide el mandato (IP exacta, SSID, frecuencia, WPA2, wds=1, 24 dBm, stp=0) no sale de esos archivos. Lo reporta también `docs/STAGE1257A_CATALOGO_COMPLETO_VALORES_TUNEADOS_AUTORESEARCH_PTP_PTMP_LTU_ES.md`, sección 6.
- Hallazgo de 1279A, verificado en 1281A: `firmware/openwrt/pbe5ac_gen2_ptp_kit/enable_airos8_ap_hybrid_80211_for_openwrt_sta.sh` y `firmware/openwrt/pbe5ac_gen2_ptp_kit/restore_stock_airos8_with_known_cfg.sh` tienen el mismo sha256 `edf58be7c1335da3d6e1daf3200ee63acf503e0c52dacf7ec7270480165aba4a` (stub retirado, exit 65): ni habilitan el AP híbrido ni restauran airOS stock.
- El guardián `/tmp/fmx_panel2_canary_watchdog.sh` del runbook 82B no existe como script en el repo.

## 10. Qué NO está probado (lista honesta)

- El enlace PtP de producción nunca fue probado: cohorte 0 de 18 pares, A/A inválido en PowerBeam (906A, 1048A), 1176A y 1180A BLOCKED. Aceptación de producción: UNKNOWN.
- LiteBeam: NO_EVIDENCE; nada de PowerBeam se transfiere.
- El vencimiento de los temporizadores 45 s y 120 s con rollback real: NO probado en vivo en ninguno de los tres mecanismos. Lo hecho es estático o simulado (985A, 1099A, 1100A).
- Que un rollback restaure un enlace caído en un radio real: NO probado. Lo vivo (1175A, 1043A) fue el ciclo del kit en el par de banco, con rollback manual.
- Que el watchdog sirva para un flasheo OTA: no restaura firmware ni flash. Un SquashFS mal flasheado no tiene red de seguridad automática en el repo.
- Contenido uci-defaults de producción: los archivos del árbol son stubs retirados (sección 9); hay que reconstruirlo y revisarlo antes de hornear una imagen.
- Imagen SquashFS personalizada para producción: la emisión de imagen está BLOCKED / NOT_EXECUTED por falta de toolchain (`docs/STAGE988A_SQUASHFS_WATCHDOG_AND_REPO_HYGIENE_GATE.md`); el script de flasheo de banco `tools/deploy/run_stage105a_step1_hybrid_openwrt_ap_241_flash.py` no tiene argparse ni `--dry-run` y está atado a equipos de banco. Pasos que requieren compuerta del operador.
- Los envoltorios 1278A y 1279A: DRY_RUN_ONLY. La ruta SSH en vivo del backup (`SshTransport`), el chequeo de nombres de `/proc/mtd` en un radio real y todo `--execute` del orquestador nunca corrieron; no se verificó el comportamiento de dropbear/BusyBox con `cat /dev/mtdblockN`.
- Hash de referencia mtd4 de producción: no existe; se crea en el primer respaldo en vivo, que tampoco se hizo.
- Persistencia: los kits v17 son runtime; el comportamiento tras un reboot no está probado.
- Guarida Panel2 (22 CPEs): nunca probada en campo ni auditada en vivo; solo lecturas pasivas y simulación. Cualquier paso en vivo requiere compuerta del operador.
- Interoperabilidad física, uptime sostenido, tasa de falsos positivos cero y aceptación de producción: UNKNOWN en todos los extremos.

## 11. Fuentes leídas

`docs/STAGE1053A_PRODUCTION_PTP_OTA_ROLLOUT_RUNBOOK.md`, `docs/STAGE1097A_PTP_CANARY_PRE_AND_POST_FLIGHT_VERIFIER.md`, `docs/STAGE1098A_PTP_CANARY_SELFTEST_AND_FAULT_MATRIX.md`, `docs/STAGE1113A_OPERATOR_EXECUTIVE_PTP_AND_GUARIDA_READINESS_BRIEF.md`, `docs/STAGE1048A_PBE5AC_PTP_PRODUCTION_READINESS_GATE.md`, `docs/CURRENT_STATE.md`, `AGENTS.md`, `docs/STAGE984A_GUARDED_PTP_STARTUP_WATCHDOG.md`, los argparse y recibos de `tools/deploy/backup_and_verify_production_ptp_mtd.py` y `tools/deploy/run_production_ptp_canary_one_command.py` (1281A) y los scripts citados arriba. Hashes verificados en disco al escribir: kit v17 `8453c92df2716395f30bcc8bc9008bab208452dec775b2d78efd5552b7dce959` (igual al hash del kit en el ciclo vivo 1175A) y watchdog v17 `2c1e21f16b204b37c92dd09622a14bd544eea3a557a9bf76c90d9eb00ce35af8` (igual al de 1099A).
