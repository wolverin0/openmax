<!-- doc-head: SUPERSEDED (W435, 31/10): PtP-Colo sizing at 7 km (BDP 863 B) and the BQL 8192 derived from it are wrong; the operator says the link is 450 m, so BQL must be re-derived (STAGE3098A). W336 + refresco W338 ES matriz maestra E2E: 15 avances probados (WA, XC, PBE-5AC, LTU, AF-4X, M5) contra lo aplicado en los 18 nodos OpenWrt, con nivel de evidencia por celda; Panel1 100% MATCH (0 differs) y sondas extendidas activas en W338 -->
Que cubre: cada avance real (txpower 23 dBm US, AQL por AC, fq_codel, BQL, TSQ, VM 64 MB, htt_max_amsdu_ampdu, nf_cal_period, ani_enable, RTS/CTS, coverage_class, WMM DiffServ, controlador adaptativo, OPMODE_NOTIF, separacion espectral por POP) cruzado con Panel1, Panel3, Panel2 y PtP-Colo.
Evidencia: telemetry.db (sondas extendidas W338 en vivo sobre 15/18 nodos), relectura W338 P1 de Panel1 (0 differs en .84, .41, .223 y .80), preflight W338 P3 de Panel2/Panel3 (10/12 snapshots nativos), binario MIPS fmx_omn_mips_be (96/96 en QEMU 24Kc), hyperresearch.db y MemoryMaster project:futuramax.
Hallazgo central (W338): Panel1 (.84 y sus 3 CPE) quedo 100% LEIDO EN VIVO con 0 differs tras corregir el bug de sysctl multi-clave (W338 P1); el colector Antes/Despues ya corre con sondas extendidas en vivo (W338 P2); fmx_omn_mips_be ya esta compilado para MIPS big-endian (W338 P4); Panel2 y Panel3 tienen preflight read-only en vivo (W338 P3) a la espera de aprobacion del operador para rollout.
Leer cuando: haya que decidir que aplicar en Panel3, Panel2 o PtP-Colo, o antes de citar un champion como vigente. Datos maquina: artifacts/curation/e2e_breakthroughs_vs_18nodes_audit.json.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Matriz maestra de avances y brechas E2E (Wave 336, refresco W338)

Auditoria offline del 29/10, refrescada en W338 con los recibos de W337. Esta ola no toco ningun radio: todo sale de archivos y bases locales.

## Como leer la matriz

Cada celda lleva un nivel de evidencia. Ninguno se infiere de un script por si solo.

| Nivel | Significa |
| :-- | :-- |
| LEIDO | el valor se leyo del equipo (colector, checks W335 o relectura W337) |
| DECLARADO | el script de persistencia lo escribe, pero no hay lectura posterior registrada |
| INCONSISTENTE | el script esta instalado y la ultima lectura muestra otro valor |
| PARCIAL | solo una parte del ajuste esta aplicada segun la lectura |
| NO APLICADO | la evidencia muestra que no esta, o que se revirtio |
| SIN SONDA | ningun colector lee ese ajuste en ese nodo: estado desconocido |
| PENDIENTE | avance listo offline, sin ejecucion en produccion |

Fuentes, con su sha256 en el JSON:
- telemetry.db: ultima fila con AQM por nodo, hasta el 29/10 01:25 UTC. Para cpe_200_169, cpe_210_21 y cpe_210_9 es del 28/10, ~23:20 UTC, porque su SSH falla de forma intermitente.
- Checks solo-lectura W335 del 29/10 10:25 UTC: archivos de persistencia, min_free_kbytes, aql_threshold y canales.
- Script del fix de cpe_200_80 (29/10 08:05), aun sin seguimiento en git.
- Verificacion post-fix del 29/10 08:13: solo rendimiento, no relee ajustes.

## Roster de los 18 nodos (todos WA en OpenWrt 24.10.4)

| Nodo | Grupo y POP | Placa | Canal y ancho | fq quantum/limit/mem | aql_threshold | MemAvailable |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| panel1_ap .84 | G1, Torre Guarida | LAP-120 | ch48, 20 MHz | 3028/512/3 MiB | 4000, luego 5000 (W335) | 6.3 MiB |
| cpe_200_41 | G1 | NS-5AC Loco | ch48 | 300/8192/4 MiB | 5000 (W335) | 3.3 MiB |
| cpe_200_223 | G1 | LBE-5AC Gen2 | ch48 | 300/8192/4 MiB | 5000 (W335) | 2.2 MiB |
| cpe_200_80 | G1 | NS-5AC Loco | ch48 | 300/8192/4 MiB | 5000 (W335) | 3.1 MiB |
| panel3_ap .83 | G2, Torre Guarida | LAP-120 | ch149, 20 MHz | 3028/512/3 MiB | 4000 | 11.1 MiB |
| cpe_210_9 | G2 | LBE-5AC Gen2 | ch149 | 300/8192/4 MiB | sin sonda | 3.1 MiB |
| cpe_210_235 | G2 | LBE-5AC Gen2 | ch149 | 300/8192/4 MiB | sin sonda | 1.8 MiB |
| cpe_210_238 | G2 | LBE-5AC Gen2 | ch149 | 300/8192/4 MiB | sin sonda | 4.5 MiB |
| panel2_ap .82 | G3, Torre Guarida | LAP-120 | ch161, 20 MHz | vacio/512/3 MiB | 4000 | 16.6 MiB |
| 7 CPE de Panel2 | G3 | LBE-5AC Gen2 | ch161 | 300/8192/4 MiB | sin sonda | 4.4-9.2 MiB |
| ptp_colo_ap .62 | G4, POP Edificio Principal | LBE-5AC Gen2 | ch153, 20 MHz | 300/8192/4 MiB | sin sonda | 9.8 MiB |
| ptp_colo_sta .54 | G4 | LBE-5AC Gen2 | ch153 | 300/8192/4 MiB | sin sonda | 9.9 MiB |

- Las 7 CPE de Panel2 son cpe_200_213, cpe_210_166, cpe_200_169, cpe_210_239, cpe_200_183, cpe_210_21 y cpe_210_83.
- La telemetria de 01:25 UTC aun mostraba Panel1 en ch44 a 40 MHz, que quedo del banco de W334. Los checks W335 y el post-fix lo leen en ch48 a 20 MHz.
- mac80211 trae por defecto quantum 300 y limit 8192, y 16 MiB de memoria en radios VHT. Por eso el tope de 4 MiB de las CPE si es un ajuste aplicado. Su origen probable es la imagen WA; no se verifico.

## Matriz: avance contra estado en produccion

| Avance | Probado en | G1 Panel1 + 3 CPE | G2 Panel3 + 3 CPE | G3 Panel2 + 7 CPE | G4 PtP-Colo |
| :-- | :-- | :-- | :-- | :-- | :-- |
| txpower 23 dBm, regdomain US | WA (script 29/10) | LEIDO 23 dBm US (W337) | SIN SONDA | SIN SONDA | SIN SONDA |
| AQL por AC + aql_threshold | WA, PBE-5AC | LEIDO por AC y threshold 5000 (W337) | AP LEIDO 4000; CPE SIN SONDA | AP LEIDO 4000; CPE SIN SONDA | SIN SONDA |
| fq_codel de mac80211 | WA, PBE-5AC, XC | LEIDO AP 4542/2048/4 MiB, CPE 1514/1024/4 MiB (W337) | AP LEIDO; CPE PARCIAL | AP LEIDO con quantum vacio; CPE PARCIAL | PARCIAL |
| BQL eth0 42392/4542/800 | WA, PBE-5AC | LEIDO CPE 42392/4542/800, AP 36288/4542/600 (W337) | SIN SONDA | SIN SONDA | SIN SONDA |
| CoTSQ tcp_limit_output_bytes | WA, LTU | LEIDO 65536 (W338 P1, 0 differs en los 4 nodos) | LEIDO en vivo (W338 P2/P3) | LEIDO en vivo (W338 P2/P3) | LEIDO en vivo (W338 P2) |
| VM 64 MB (min_free, oom, watermark) | WA, M5 | LEIDO min_free 4096, oom -900, watermark_boost 15000 | SIN SONDA | SIN SONDA | SIN SONDA |
| htt_max_amsdu_ampdu | WA (banco) | LEIDO 2/64 | SIN SONDA | SIN SONDA | SIN SONDA |
| nf_cal_period | WA | LEIDO 120 (se probo 30) | SIN SONDA | SIN SONDA | SIN SONDA |
| ani_enable | WA, XC, M5 | LEIDO 1 | SIN SONDA | SIN SONDA | SIN SONDA |
| RTS/CTS dinamico | WA, XC | LEIDO apagado | AP NO APLICADO (2534A revertido) | SIN SONDA | SIN SONDA |
| coverage_class / distance | WA, XC, PBE-5AC | LEIDO clase 0 | PENDIENTE (cpe_210_9, 2275 m) | SIN SONDA | SIN SONDA |
| WMM / DiffServ bypass | WA, PBE-5AC (banco) | SIN SONDA | SIN SONDA | SIN SONDA | SIN SONDA |
| controlador adaptativo | WA, LTU, AF-4X, M5 | AP NO APLICADO | SIN SONDA | SIN SONDA | SIN SONDA |
| OPMODE_NOTIF (fmx_omn) | WA (offline) | PENDIENTE, piloto cpe_200_80 | PENDIENTE | PENDIENTE | PENDIENTE |
| separacion espectral por POP | WA | LEIDO ch48 | LEIDO ch149 | LEIDO ch161 | LEIDO ch153 |

Conteo sobre 270 celdas (18 nodos por 15 avances), W336 contra W338:

| Nivel | W336 | W338 |
| :-- | :-- | :-- |
| SIN SONDA | 184 | 171 |
| LEIDO | 30 | 62 |
| DECLARADO | 19 | 0 |
| PENDIENTE | 19 | 19 |
| PARCIAL | 12 | 12 |
| INCONSISTENTE | 4 | 0 |
| NO APLICADO | 2 | 6 |

## Resultados de Wave 337 + Cierre Wave 338 (P1..P5)

- **Panel1 releido y 100% alineado (W337 P1 + W338 P1):** en `.84` y sus 3 CPE (`.41`, `.223`, `.80`), todas las celdas declaradas coinciden en vivo con **`differs_total: 0`** (`38/38 MATCH` en `.84` y `25/25 MATCH` en cada CPE).
  - Ajustes confirmados en vivo: `txpower 23 dBm US`, `AQL` por AC y `aql_threshold 5000`, `fq_codel`, `BQL`, `min_free_kbytes=4096`, `oom_score_adj=-900`, `htt_max_amsdu_ampdu=2 64`, `nf_cal_period=120`, `ani_enable=1` y las 12/7 claves `sysctl` (incluyendo `tcp_limit_output_bytes=65536` y `netdev_max_backlog=2048`).
- **Bug de aplicacion parcial de sysctl (RESUELTO en W338 P1):** el bloque `sysctl -w` multi-clave abortaba al encontrar `net.core.netdev_budget_usecs` ausente en el kernel OpenWrt 6.6. Se corrigio con aplicacion individual por clave (`sysctl -w "$kv" 2>/dev/null || true`) tanto en [`tools/panel1/deploy_cpe_champion_persistence.py`](<repo>/tools/panel1/deploy_cpe_champion_persistence.py) como en vivo sobre los 4 nodos de Panel1 (0 cortes de enlace).
- **Sondas extendidas activas en vivo (W337 P3 + W338 P2):** `txpower/pais`, `BQL`, `sysctl` clave y `AQL/ani/nf_cal/rts` por PHY fueron implementadas (66 tests OK), los hashes SHA-256 del supervisor fueron re-sellados y el demonio [`fmx_persistent_before_after_openwrt_daemon.py`](<repo>/tools/observability/fmx_persistent_before_after_openwrt_daemon.py) ya corre en vivo sondeando directamente 15/18 nodos en `telemetry.db` (los 3 restantes tienen brecha puntual de SSH/banner: `panel1_ap` por rate-limit concurrente, `cpe_200_169` y `cpe_210_21`).
- **Preflight read-only en vivo de Panel2 y Panel3 (W337 P4 + W338 P3):**
  - Se ejecuto [`tools/panel2/run_wave338_panel2_panel3_readonly_preflight.py`](<repo>/tools/panel2/run_wave338_panel2_panel3_readonly_preflight.py) (20 tests OK) sobre los 12 nodos de Panel2 y Panel3 (0 escrituras RF/UCI).
  - En `panel3_ap` (`.83`), el delta del mismo boot sobre 31.56 s dio **`fq_overmemory_delta = 0` (`0.0/s`)** con `MemAvailable = 13,656 kB`.
  - 3 CPEs (`cpe_200_213`, `cpe_210_239`, `cpe_210_238`) tienen `MemAvailable < 5120 kB` (`4488..4552 kB`), por lo que requieren aplicar primero el tope `fq_codel memory_limit = 4 MiB` y `min_free_kbytes = 4096` antes de cualquier otro ajuste.
- **Binario MIPS `fmx_omn_mips_be` y candidato BDP PtP-Colo (W337 P2 + W338 P4):**
  - Se compilo estaticamente [`tools/firmware/fmx_omn/fmx_omn_mips_be`](<repo>/tools/firmware/fmx_omn/fmx_omn_mips_be) (`3,644` bytes `ELF32 MSB MIPS32 rel2`, 0 instrucciones FP, `96/96` casos byte-exactos verificados en `qemu-mips-static -cpu 24Kc`).
  - Se preparo el candidato calibrado por BDP (`limit_max=8192`) para `PtP-Colo .62/.54` en [`artifacts/autoresearch/wave338_fmx_omn_mips_binary_and_ptp_colo_bdp_candidate.json`](<repo>/artifacts/autoresearch/wave338_fmx_omn_mips_binary_and_ptp_colo_bdp_candidate.json).

## Que dice cada avance (resumen con evidencia)

- **AQL por AC:** aql_txq_limit es el limitador dominante en QCA988x. En R165..R182, con 1 CPE, dio de +3.1% a +15.8% de goodput BE.
  El champion multi-CPE v19 usa BE 1500/3000 y aql_threshold 4000 (results.tsv baseline_s145a: 59.2 Mbps, p95 53.8 ms).
- **fq_codel:** FMX-DISC-02 muestra que el default de 16 MiB ocupa el 25% de la RAM de 64 MiB, y propone el tope de 4 MiB. Los champions v11..v19 suben quantum y bajan limit.
- **BQL:** champions v17..v19 (Stages 51A, 52A, 55A, 3 CPE verificados) y PtP v18 (Stage 52A).
- **nf_cal_period:** el champion v2 (S19, PB-031) combino nf_cal_period 30 con retry 5/4 y txqueuelen 256: +4.2% de goodput y -19.8% de RTT.
- **ani_enable:** R23 (<memorymaster-id>) dio KEEP en banco a candidatos ANI asimetricos. En 2.4 GHz el R2AC exige ani 1; el R5AC co-ubicado gano con ani 0.
- **RTS/CTS:** el champion v5 (S24E, PB-021) uso RTS 512 adaptativo y bajo el p99 un 42%. En Panel3 solo hubo un ciclo, revertido.
- **WMM / DiffServ:** Stage 276A quedo CONFIRMED en banco (<memorymaster-id>). Stage 351A lo horneo en el WA Universal Kit v8 (<memorymaster-id>).
- **OPMODE_NOTIF:** W335B dejo el builder, la fuente C libnl-tiny y la prueba OTA con watchdog de 45 s, con 56 tests (<memorymaster-id>).
- **POP:** segun la correccion del operador (<memorymaster-id>), PtP-Colo esta en el POP Edificio Principal y Panel1/2/3 en Torre Guarida, a 7 km y 2 saltos PtP.
  Panel3 (5745 MHz) y Panel2 (5805 MHz) quedan a 60 MHz.

## Hallazgos principales

1. **Champion canonico pendiente:** en Panel1 rige el script del 29/10, ya LEIDO (W337). Difiere del ledger v19 en el AQL de las CPE, el threshold, nf_cal y el BQL del AP.
   El A/B de valle de Stage 2816A decide cual queda.
2. **Panel1 (W338):** la INCONSISTENCIA de W336 se cerro: la lectura de 01:25 UTC era anterior al fix. Queda abierto el bug de sysctl (K05).
3. **panel2_ap:** fq_quantum sin valor y fq_overmemory 183842, el peor del parque (panel1_ap 4070, panel3_ap 6296).
4. **cpe_200_80 tras el fix:**
   - Mejoro la senal de -56 a -47 dBm.
   - Su subida sigue en VHT-MCS 3, NSS 1, a 26 Mbps, con 12% de perdida bajo carga.
   - Solo rx 35.2 Mbps y tx 29.4 Mbps bridged; 48.0 Mbps agregados con las 3 CPE.
   - Es justo el caso que ataca OPMODE_NOTIF.
5. **Panel3, Panel2, sus 10 CPE y PtP-Colo** no tienen ningun champion de CPE declarado: solo el tope fq de 4 MiB.
6. **171 de 270 celdas siguen sin sonda** fuera de Panel1, hasta que las sondas de W337 P3 corran en vivo.
7. **Riesgo regulatorio:** txpower con regdomain US en Argentina necesita validacion antes de extenderse a otros paneles.

## Familias sin nodo de produccion (champion solo de banco)

| Familia | Estado |
| :-- | :-- |
| XC | imagenes pasivas horneadas (Stage 206A); champions R5AC/R2AC de banco en airOS |
| PBE-5AC | banco PtP .241/.242; champion PtP v18 (Stage 52A): 46.18-49.43 Mbps (+7.0%), p95 112.7->110.7 ms (-1.8%) |
| LTU | banco .110: LTU Safe Kit, +9.86% de goodput; el snapshot 1135A sigue bloqueado por la contrasena |
| AF-4X | perfil af4x_invictus: framelength 2.5 ms, -16.1% de p95 |
| M5 | perfil pbm5_xw_weak_ota: SIMO TX con MRC RX en enlace debil |

## Que falta aplicar, por prioridad

1. **Panel1:** corregir el bug de aplicacion parcial de sysctl (W338 P1). La relectura ya se hizo en W337.
2. **Champion:** elegir un juego canonico con un A/B en valle antes de copiarlo a otros paneles.
3. **panel2_ap:** fijar fq_quantum y bajar fq_overmemory. Es el AP con mas descartes.
4. **Panel3:** probar `distance` reversible para cpe_210_9 y, si gana, extender el champion de CPE a sus 3 CPE.
5. **Panel2:** champion de CPE para las 7 CPE, empezando por las de MCS 0 (cpe_200_169 y cpe_210_21).
6. **PtP-Colo:** su champion es el PtP v18 de banco; no hay nada aplicado aparte del tope fq.
7. **Colector:** las sondas ya estan escritas (W337 P3). Falta recargarlas: hay que resellar los pines del supervisor y reiniciar el demonio.
8. **OPMODE_NOTIF:** prueba OTA en cpe_200_80, con autorizacion del operador.

## Capacidad RF contra planes

- Los planes se limitan en MikroTik Simple Queues a 10/15 Mbps. Es un dato informado por el operador, no leido en esta ola.
- El techo RF medido a 20 MHz esta entre ~64 y 70 Mbps por sector bridged. Con 3 CPE en Panel1 hubo 48.0 Mbps agregados.
- Por eso hoy el cuello por cliente es la cola del plan, no la radio. La excepcion son los enlaces degradados: cpe_200_80 en subida, cpe_210_9, y cpe_200_169 y cpe_210_21 en MCS 0.

## Conclusiones viejas ya superadas

| Antes | Ahora |
| :-- | :-- |
| Panel2 con 22 CPE | 7 CPE reales en OpenWrt (W308) |
| Panel3: champion RTS=512 + AQL | 2534A fue un ciclo revertido con 0 escrituras persistentes |
| Panel3 con 0% DUP | ninguna fuente cuenta respuestas DUP (2592A) |
| techo bridged de 147.92 Mbps a 20 MHz | artefacto del parser de ancho (W334/W335); tests/test_uisp_commercial_iptv_plan_matrix.py todavia lo afirma |
| minstrel_ht converge en 15-30 s | en ath10k el control de tasa vive en el firmware |
| Panel3 con interferencia co-sitio de PtP-Colo | retirado: estan en POPs distintos a 7 km |
| Panel2 y Panel3 a 50 MHz | Panel3 opera en 5745 MHz: 60 MHz de separacion |
| demonio Antes/Despues vivo, 7/8 nodos | 18 nodos enrolados; el resumen vivo no se actualiza desde el 29/10 01:25 UTC |
| aql_threshold 12000 contra 24000 (decision abierta) | produccion corre 4000 y 5000 |
| nf_cal_period 30 (champion v2) | el script de produccion declara 120, sin A/B |
| boveda en .hyperresearch/vault/ | no existe: es hyperresearch.db (747 notas, 601 evergreen) mas research/notes |
| roster: Panel1 con CPE airOS pendiente y Panel2 por migrar | 18/18 nodos en OpenWrt 24.10.4 |

## Experimentos duplicados

- **Banco LTU/XC (D3):** 68 filas de results.tsv barren sysctl con una sola iteracion por valor y un goodput ambiental de 0.01 a 12.08 Mbps. Sus "keep" son muestras retenidas, no champions.
  - Cambios repetidos: tx_queue_len 1000 a 256 (3 veces), wmem_default 131072 a 163840 (2), netdev_budget 600 a 300 (2), tcp_synack_retries 5 a 6 (2) y tcp_fin_timeout 60 a 45 (2).
  - Idas y vueltas: dev_weight 96/64, rmem_default y netdev_budget.
  - La lista completa (19 grupos) esta en el JSON.
- **PtP D2 (Waves 84, 91 y 93):** ABAB repetidos sin promocion.
- **Scorecard de 18 nodos:** de las versiones v1 a v6, solo v6 (W329) sigue vigente.
- **Banco de Panel1 a 20/40/80 MHz:** se midio tres veces con metodos distintos (OTA de context.md, techo bridged W334 y post-fix). No son comparables entre si.

## Limites

- **Solo evidencia en disco:** no se releyo ningun equipo. Lo DECLARADO puede estar o no aplicado.
- **Datos del operador:** Simple Queues y la topologia de POPs son datos informados, no leidos.
- **Origen del tope de 4 MiB:** no se verifico.
- **Sin causalidad:** no hay afirmacion causal ni de QoE nueva. Las cifras de rendimiento son de las mediciones citadas.

Fuente verificada del champion PtP v18: `artifacts/autoresearch/wave341_ptp_v18_provenance_audit.json`.
