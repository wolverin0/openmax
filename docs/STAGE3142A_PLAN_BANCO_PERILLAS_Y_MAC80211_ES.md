<!-- doc-head: Stage 3142A (ES): plan listo para ejecutar de dos rondas de banco cuando se libere (LAP-120 .20 + Loco .117): ronda 1 = top-5 perillas de STAGE3135A (rc_max_per_thr, aql_threshold, tcp_notsent_lowat, tcp_limit_output_bytes, pktlog_filter) y ronda 2 = A/B de los fixes mac80211 6.12.y de STAGE3141A por intercambio de modulo en RAM (sin rebuild de imagen, sin tocar mtd0/mtd1/ART). Cada ronda tiene regla predeclarada en JSON con sha256, orden AA primero y luego A1-B1-A2-B2, y evaluador offline probado. Offline: 0 acceso a equipos -->
Que cubre: ledger de perillas, reglas JSON, evaluador, aplicar/revertir cada perilla, intercambio de modulo, comandos y dudas abiertas.
Estado: SOLO ESCRITORIO. No se ejecuto nada en equipos. MemoryMaster MCP no conecto en esta sesion; no se consulto ni se ingesto.
Archivos: artifacts/autoresearch/stage3142a_round1_knobs_rule.json, artifacts/autoresearch/stage3142a_round2_mac80211_rule.json, tools/bench/stage3142a_abab.py, tests/test_stage3142a_abab.py.
Leer cuando: antes de lanzar la ronda 1 o 2 en el banco, o al cambiar la regla (cambiarla cambia el sha256 y la invalida).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 3142A: plan de banco, perillas y mac80211

## 1. Reglas predeclaradas (sha256 de cada archivo; el archivo no puede contener su propio hash)

| Ronda | Archivo | sha256 |
| :-- | :-- | :-- |
| 1 | `artifacts/autoresearch/stage3142a_round1_knobs_rule.json` | `2c70083ec6499b6db56a989097a43b33ef4c324924695cab304928caa5676b6f` |
| 2 | `artifacts/autoresearch/stage3142a_round2_mac80211_rule.json` | `0fd73b9b1b839b89217b142c08bd788ab5dee0bfddcc4a12f93dc401d46b4ec2` |

- Cada JSON fija con sha256 (`pins`) harness, politica A/A, PROGRAM, thresholds, watchdog, carrier W445 y, en la ronda 2, parches y `.ko`. Los pins son del arbol de trabajo de hoy: `fmx_autoresearch_harness.py` esta modificado y `empirical_aa_policy.py` y `fmx_watchdog.sh` aun no estan versionados (git status). Si cambian, `--verify-pins` falla a proposito.
- Secuencia por corrida y por perilla (una variable por corrida): AA1..AA6, luego A1, B1, A2, B2, un solo arranque (el `AAContext` exige mismo boot id). 6 AA y 20 s son precedente de W445 (`STAGE3105A_BANCO_PTMP...md`), parametros de diseno, no derivados; el minimo del harness es 2.
- Metricas por ventana: RTT cargado p50/p95/p99 (ICMP del AP, agrupado), goodput TCP suma de las 2 STA, perdida UDP, Jain, `retry_rate` (retries/paquetes), `tx_failed_rate`, `mem_available_kib` (minimo entre nodos), `oom_events`, `station_drops`, `link_alive`.
- Cotas: ninguna numerica. Todas salen del min/max de las AA de la misma corrida (thresholds.json L01-L04; harness lineas de guardas). MemAvailable no es metrica del harness: guarda extra "no menor que el minimo AA" (hallazgo OOM de la Loco en W445). Temperaturas: no son criterio en ningun lugar.
- Decision (`tools/bench/stage3142a_abab.py`): A1 y A2 deben caer dentro de la banda AA (si no, INCONCLUSIVE_A_OUTSIDE_AA_BAND); `best_fmx_loss` = mediana de las perdidas de A1 y A2; B1 y B2 se juzgan cada uno con `compute_fmx_objective` directo (no `run_iteration`: movería el incumbente; restriccion de STAGE3135A seccion 5). Veredictos: KEEP_CANDIDATE (ambos KEEP, nunca promocion: falta replicacion independiente), NO_EFFECT_OR_INCONSISTENT, DISCARD_HARM_OUTSIDE_AA, CRASH_ROLLBACK, CRASH_A_ARM.

## 2. Ronda 1: ledger consultado (no se re-testea a ciegas)

Fuentes: `firmware_knob_candidates.json`, `artifacts/knob_index/knob_index.json`, `artifacts/verification/stage1256a_complete_tuned_knobs_production_ledger.json` (548 filas). Motivo de retest: los 190 recibos LAP-120 del 24/10 usaron guardas legacy (min_rep 2, rtt_budget 20, target 80) que thresholds.json L03 marca como no autoritativas, y no hubo A/A (STAGE3135A seccion 3).

| Perilla | Filas previas (campana/stage: delta) | Nota |
| :-- | :-- | :-- |
| rc_max_per_thr | ninguna en ledger ni indice; solo recibos 24/10 (bundle r100-r107 recalculado: p95 -57,0 a -90,5 %, goodput -1,7 a +2,4 %) | catalogo: `characterization_only`, `enabled=false`, UNQUALIFIED |
| aql_threshold | PtP v7: S145A -0,77 %, S167A -3,878 %, S275A -2,977 %, S139A -1,654 % (goodput) | PtMP: sin fila aislada |
| tcp_notsent_lowat | PtMP v23 S21-R2 (4294967295 a 16384 + netdev_budget): goodput -0,35 %, p95 -12,35 %, CHAMPION; PtP S135A +4,093 %, S381A -6,083 % | filas en bundle; signo depende del rol |
| tcp_limit_output_bytes | PtP S140A +4,994 %, S145A -0,77 %; airOS S68A +14,32 % | sin fila PtMP OpenWrt aislada |
| pktlog_filter | PtMP v23 S21-R1 (0x40 a 0, con ani y quiet_period): goodput +1,39 %, p95 **+31,37 %**, DESCARTADO. El +23,35 % es airOS XC `rmmod ath_pktlog` (S93B), otra plataforma | contradice "sin probar" de STAGE3135A; los kits v12-v20 ya escriben 0x0 |

Inconsistencia senalada, no resuelta: kits v14-v20 escriben `tcp_notsent_lowat=131072`, `tcp_limit_output_bytes=131072` y `aql_threshold=24000`; PROGRAM D1 (champion v19) dice aql 4000 y tcp_limit 64 KB; STAGE3135A dice lowat 8192; produccion lee 4294967295 en 12/16. Por eso el brazo A es siempre el valor leido al inicio de la corrida.

## 3. Ronda 1: carrier, aplicar y revertir

- Carrier: workload de W445 (`docs/STAGE3105A_protocol.py`, `STAGE3105A_nodes.py`, `STAGE3105A_campaign.py`): 2 STA (Loco `.117` y LiteBeam), PC como fuente, TCP CPE a PC (subida), VoIP G.711, IPTV 2 Mbps, ICMP cargado desde el AP. Guarda `fmx_watchdog.sh` (arm 45 s, renew cada 10 s). `tools/bench/run_live_autoresearch_lap120_loco195.py` usa 198.18.0.81/.41: direcciones viejas frente a W439; no usarlo como carrier.
- Host/direccion: `tcp_notsent_lowat` y `tcp_limit_output_bytes` se aplican en las 2 STA (emisoras de TCP). La direccion AP emisor (la del runner del 24/10) queda sin probar. AQL y ct_special se aplican como una sola variable de enlace en los nodos que tengan la superficie.
- Persistencia: ninguna. Todo es RAM, debugfs o sysctl; un reinicio revierte. No se editan kits, `/etc/sysctl.conf` ni uci.
- Restauracion: script generado por `render_restore_script` desde el valor leido (probado con `sh -n`), armado en el watchdog antes de la primera escritura.

| Orden | Perilla | A (leido) | B | Escribir | Leer / restaurar |
| :-- | :-- | :-- | :-- | :-- | :-- |
| P1 | rc_max_per_thr | 50 por defecto de ayuda (sin getter) | 28 | `echo 30064771100 > /sys/kernel/debug/ieee80211/phy0/ath10k/ct_special` | restaurar `echo 30064771122 > ...ct_special`; sin lectura: ver 3.1 |
| P3 | aql_threshold | leido | 4000 | `echo 4000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold` | `cat aql_threshold; cat aql_txq_limit`; restaurar umbral y los 4 AC low/high (catalogo: no solo BE) |
| P4 | tcp_notsent_lowat | leido | 8192 | `echo 8192 > /proc/sys/net/ipv4/tcp_notsent_lowat` | `cat` y restaurar leido |
| P5 | tcp_limit_output_bytes | leido | 65536 | `echo 65536 > /proc/sys/net/ipv4/tcp_limit_output_bytes` | idem |
| P2 | pktlog_filter | leido (kits: 0x0) | 0x0 | `echo 0x0 > .../ath10k/pktlog_filter` | si A == 0x0 la corrida se anula (B igual a A) |

Fuentes de B: catalogo (aql values 4000/8000/24000; ct_special observed 28/50), ledger S41A-R2 (lowat 8K), PROGRAM D1 (64 KB). Si el valor leido ya es B, esa corrida se anula.

### 3.1 P1: restauracion sin getter (decision del operador)
El catalogo declara `state_readback=help_only` y que el helper enmascara con 0xff: 28 y 50 son intentos reportados, no prueba de valor aplicado en firmware. El harness exige `restoration_verified=True`. Propuesta: True solo si escritura rc=0, epoca de asociacion igual, sin error nuevo de kernel/firmware y enlace vivo. Es INFERRED, no una lectura.

## 4. Ronda 2: mac80211 6.12.y (parches 360 y 361)

- **Respuesta: intercambio de modulo, no rebuild de imagen** (STAGE3141A seccion 6b). Las imagenes `2410_bp` llevan el `mac80211.ko` con parche binario TEB; reconstruir exige portar TEB a C, decision del operador.
- **Sin tocar mtd0/mtd1/ART: si.** El intercambio es en RAM: no se escribe flash. Se descarto `opkg install` de los `.ipk` -r2 para el A/B porque exige reinicio por brazo, cambia el boot id e invalida el contexto A/A de la misma corrida; queda como camino de persistencia posterior (escribe el overlay, no mtd0/1/5).
- Brazos: A = `firmware/openwrt/pbe5ac_gen2_ptp_kit/mac80211_rom_241.ko` (sha `8566fb1c...`, oficial 24.10.4, sin TEB); B = `firmware/openwrt/2410_bp/mac80211_6_12_y_fixes/kmod/mac80211.ko.patched` (sha `ec88a9ca...`). Esto aisla los fixes aunque la imagen del LAP traiga TEB. `SHA256SUMS` de la carpeta: 8/8 OK el 31/10.
- Cada ventana (AA incluidas) empieza con el mismo ciclo de recarga de su archivo, asi el ruido de recarga queda dentro de la banda AA. Secuencia: `wifi down; sleep 2; rmmod ath10k_pci ath10k_core mac80211; insmod /tmp/fmx3142a/<brazo>/mac80211.ko; kmodloader; wifi up`, esperar asociacion de la Loco. Sin probar en hardware; ciclo A a A previo como control positivo.
- Escritura solo en el LAP `.20` (cableado). La Loco `.117` es RF-only: solo lectura. Rollback: watchdog 45 s que recarga el `.ko` original guardado (con sha) y, si falla, reinicia (RAM, el flash queda intacto).
- Preflight: sha del `mac80211.ko` actual, `uname -r` 6.6.110, `lsmod` (si ath9k esta cargado, B lleva `ath9k.ko.patched` `5bd3bb48...` y A el ath9k propio respaldado; evita el doble free de STAGE3141A seccion 2), respaldo y sha de los `.ko`.
- Fase de crash tras el trafico de cada ventana: `simulate_fw_crash` modo hard, 5 veces, espera 180 s (precedentes de W457: 5 crashes por prueba, ventana ICMP de 180 s; no inventados). Se corta tras el primer crash sin retorno.
- Metricas extra de la ronda 2: `recoveries_completed`, `tailroom_warn_lines` (WARNING de `ieee80211_free_keys`/tailroom), `bad_recovery_lines` (`previous recovery`, `consecutive fail`, WEDGED, `Failed check-sdata-in-driver`), `time_to_traffic_s_max`, mas las comunes. Guardas = banda AA.
- 3b4d27acaf (fuga de skb): no medible con ath10k (solo ath9k y hwsim llaman la funcion); sin criterio. 586c628c0b: si `tailroom_warn_lines` es 0 en todas las AA y A, el veredicto es NOT_EXERCISED, sin conclusion.
- Riesgo medido: en W457 el crash hard del LAP no volvio por ICMP en 180 s (88 sondas) y tuvo el warning `drv_assign_vif_chanctx`; el brazo A puede fallar por si mismo.

## 5. Evaluador y pruebas
- `tools/bench/stage3142a_abab.py`: valida la regla, verifica pins, juzga A1-B1-A2-B2 reutilizando el harness (sin tocarlo) y renderiza los scripts de restauracion. Datos de prueba SINTETICOS; no hay dato de banco.
- Cola de pytest (via heavy-slot): `18 passed` en `tests/test_stage3142a_abab.py`; con `tests/test_fmx_autoresearch_harness.py` juntos: `22 passed`.

## 6. Comandos listos
```
python -m tools.bench.stage3142a_abab --rule artifacts/autoresearch/stage3142a_round1_knobs_rule.json --expect-sha256 2c70083ec6499b6db56a989097a43b33ef4c324924695cab304928caa5676b6f --verify-pins
python -m tools.bench.stage3142a_abab --rule artifacts/autoresearch/stage3142a_round2_mac80211_rule.json --expect-sha256 0fd73b9b1b839b89217b142c08bd788ab5dee0bfddcc4a12f93dc401d46b4ec2 --verify-pins
python -m tools.bench.stage3142a_abab --rule <regla> --expect-sha256 <sha> --context ctx.json --windows windows_<perilla>.json
```
Orden de la ronda 1: P1, P3, P4, P5, luego P2 solo si no se anula. Ronda 2 despues (necesita escribir el LAP).

## 7. Dudas abiertas
1. Aceptar o no el proxy de restauracion de P1 (3.1).
2. Re-otorgar autoridad de pausa de UISP en la Loco (`<orca-id>` cubrio solo W445) y de fuente PC (`<orca-id>`).
3. Hueco de driver: `STAGE3105A_nodes.Control.prepare` solo conoce sysctl `net/ipv4` y no hay guarda para el AP; P1, P3 y P2 necesitan una tabla ruta-por-perilla (`knobs[].path` del JSON) y un Control del AP; la ronda 2 necesita un driver de recarga. Es codigo vivo que no se pudo probar sin equipo.
4. Direccion del TCP: solo subida CPE a PC; AP emisor sin probar.
5. Cual `mac80211.ko` corre hoy el LAP (TEB o oficial): UNKNOWN hasta el preflight.
6. 6 AA, 20 s y 5 crashes son precedentes, no derivados; con banda AA mas ancha que el efecto, el veredicto sale inconcluso por diseno.
7. Que `simulate_fw_crash` llegue a la ruta TAINTED de 586c628c0b es INFERRED.

## Decisiones del orquestador (31/10, lane_5)
- P1 `rc_max_per_thr`: no se acepta el proxy de restauracion. Se revierte con reboot del LAP cableado (.20) al terminar la corrida P1 y se verifica boot nuevo + kit/hashes; cada perilla tiene su propio A/A, asi que el boot nuevo no invalida las siguientes.
- Pausa del servicio UISP de la Loco durante A/A+ABAB y PC como fuente de trafico: re-otorgadas para las dos rondas 3142A en los mismos terminos de `<orca-id>` / `<orca-id>` (habilitado al arranque, watchdog lo reinicia al salir).
- Conflicto de valores (kits 131072/24000 vs PROGRAM.md 64 KB/4000 vs produccion 4294967295): el brazo A es siempre el valor leido al inicio; el informe debe decir cual de los tres es.
- Falta codigo vivo (tabla de rutas por perilla + guard de AP; driver de recarga de modulo): Ronda 1 la ejecuta lane_1 (PtMP) escribiendo y testeando ese driver primero; Ronda 2 (recarga de modulo) va a lane_4. Ninguna arranca hasta que el banco este libre (W466, W469, W457b).
