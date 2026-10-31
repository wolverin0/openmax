<!-- doc-head: Wave 131 (1824A-1826A) sintesis ES: nota #626 une Waves 118 (staging RAM colo con SHA256 igual a 1668A, rollback RF sin verificar; A/B aql_threshold 18000 DESCARTADO), 119 (segundo attach dual-bind refutado con EBUSY; coverage_class 1 RECHAZADO por holdout), 122 (Panel3 no tx buffer 3.85 % en una ventana de 11 s), 123 (RE de reintentos XC sin valores resueltos) y 125 (taxonomia de 571 knobs, cola segura vacia); banda :8787 a 1536A..1829A; SIN campeon; scholar negativo parcial; solo IDs cpe_ -->
# Reporte ejecutivo - Nota #626: colo, AQL 18000, buffer TX de Panel3 y 571 knobs

**Wave 131 - Etapas 1824A-1826A - 2026-10-28 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se sintetizaron 10 recibos de las Waves 118, 119, 122, 123 y 125 en la nota evergreen #626 y el feed del
Command Center :8787 se amplio a 1536A..1829A. Titular honesto: **no hay campeon de trafico nuevo**. El
A/B de AQL 18000 se descarto, el candidato coverage_class 1 fue rechazado por un holdout independiente y la
cola de knobs seguros quedo vacia. Los abonados figuran solo como IDs cpe_.

## Wave 118 - staging colo y A/B de AQL 18000 (en vivo)

- stage1746A (CONFIRMED_LIVE_RAM_STAGING, estado PARTIAL_RF_ROLLBACK_UNVERIFIED): la imagen factory del
  colo se cargo en /tmp de la radio .54 y su SHA256 leido coincide con la imagen de 1668A. Los archivos
  candidatos se cargaron en .54 y .62 sin tocar la config activa. Pendiente: step0 no ejecutado, rollback
  de RF sin verificar, guard sin armar, operational_ready=false.
- stage1747A (CONFIRMED_LIVE_HARDWARE): un solo A1-B1-A2-B2 en el banco .241/.242; el brazo B solo cambia
  aql_threshold de 12000 a 18000.
  - TCP por ventana: A1 6.56, B1 18.43, A2 17.04, B2 18.58 Mbps.
  - El ratio 1.568 (el "+56.8 %") sale de un A1 frio; A2 contra B2 es mucho mas parejo.
  - Gates: capacidad y p95 pasan; mejora pareada y cero perdida **fallan** (VoIP 0.4 % de perdida en B2).
  - **Decision: descartado**, sin promocion a produccion.

## Wave 119 - dual-bind y holdout de coverage_class (en vivo)

- stage1752A (CONFIRMED_LIVE_HARDWARE): interfaz AP/VLAN nueva (ifindex 995 -> 996). netifd la agrego al
  bridge; el hook temporal del segundo actor recibio **EBUSY** y dual_successful_attach=false, asi que el
  doble attach queda refutado. El ping post-heal fue 10/10. El nombre SIOCBRADDIF no aparece en el recibo.
- stage1753A (CONFIRMED_LIVE_HARDWARE): holdout independiente de 2 rondas (8 ventanas ABAB) del candidato
  de Wave 104 (coverage_class 1, VI 750/1500, BE 1200/2400):
  - Ronda 1: goodput -12.9 %, p95 de RTT +18.8 %.
  - Ronda 2: goodput -30.7 %, p95 de RTT +28.9 %.
  - **REJECT_HOLDOUT_REGRESSION**. Dos bloques no prueban significancia poblacional, pero cierran el
    candidato que la nota 625 ya habia registrado como descartado.

## Wave 122 - Panel1 y contadores de Panel3 (en vivo, solo lectura)

- stage1770A (LIVE_HARDWARE_READ_ONLY_PRODUCTION): cpe_41, cpe_223 y cpe_80 de Panel1 mantienen VHT-MCS7/8
  NSS2, brport state 3 y multicast_to_unicast, sin aumento de tx_failed frente a 1722A. Panel3 sigue con 3
  de 6 CPEs.
- Contadores athstats de Panel3 en una ventana de 11 s: "tx failed no tx buffer" 2975 sobre 77314 paquetes
  enviados = 3.85 %. El contador "xmit filtered" da exactamente 2975 (probablemente las mismas tramas) y
  hubo 3077 interrupciones de beacon miss. Es una observacion de una sola ventana, no una tasa medida.
- stage1771A (LIVE_HARDWARE_ONDEVICE_AND_OTA_READONLY): 3 escrituras reversibles (tx_queue_len y dev_weight
  en XC, sched_max_agg_cnt en LTU), todas restauradas; la RF no se encendio.

## Wave 123 - RE de reintentos en XC (estatica)

- stage1776A (CONFIRMED_STATIC_BINARY): umac.ko 8.7.25 expone _RATE_GetTxRetrySchedule y el valor inicial
  g_default_xretry_per_penalty = 30. **No resueltos**: la tabla de reintentos por TID, el limite de bytes
  A-MPDU y el intervalo de sondeo de rate. executable=0.
- stage1777A (CONFIRMED_STATIC_CROSSREF): 5 de 9 objetivos reconciliados entre catalogo y simbolo; se unen
  nombres, no comportamiento.

## Wave 125 - taxonomia de 571 knobs (inferencia offline)

- stage1788A: 571 knobs sobre 40 archivos ELF parseados (ame_core 2, ath10k_core 5, ath_dev 9, mac80211 7,
  ubnt_poll_host 8, umac 9; eab_driver.ko 0). Presencia binaria confirmada 423, desconocida 148. Niveles:
  PROTECTED 523, REQUIRES_RESTART 28, RF_HAZARD 20.
- stage1789A: la cola SAFE_RAM tiene **0 entradas elegibles** en los 4 dominios; el ranking prioriza
  adquirir evidencia, no predice ganancia. Ejecucion automatica no permitida.

## recall-first y scholar (honestos)

recall-first: 3 de 6 consultas con aciertos (no tx buffer Panel3 5, staging colo 2, taxonomia 571 knobs 1);
aql_threshold 18000, EBUSY de AP/VLAN y GetTxRetrySchedule dieron 0. scholar: UN chequeo suave del
principio AQL con 4 s de espacio. El sondeo del motor funciono (P=0.90, source=live) y el verify_claim
contra el abstract de "Ending the Anomaly" dio **unsupported, P=0.18**. Ese abstract no enuncia el limite de
airtime por estacion: es un negativo parcial sobre un solo abstract, no una refutacion, y no valida ningun
valor de FuturaMAX. Nota #626 ingresada; vault en 626 notas.

## Etapa 1825A - banda 1536A..1829A

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero con 120 recibos y Control
Maestro sin apellidos. Incidente corregido: un segundo daemon huerfano en el puerto 8771, lanzado antes
por este mismo carril (por la hora, probablemente en la Wave 89) y sin el parche de hot-reload,
reescribia el HTML con un builder viejo. Se detuvo ese proceso y :8787 sirve la banda
nueva con HTTP 200. Limitacion del feed: 1746A no trae la clave live_devices_touched y aparece como no-vivo.

## Limites y advertencias (honestas)

- **Sin campeon nuevo**: AQL 18000 descartado, coverage_class 1 rechazado por holdout.
- Staging colo solo en RAM, con rollback de RF sin verificar.
- El 3.85 % de Panel3 es una ventana de 11 s.
- **Verificacion en navegador real: NO realizada** (Claude-in-Chrome no conecta); se verifico por CLI
  (HTTP 200 + bytes servidos) y balance de etiquetas.
- El tablero completo aun renderiza apellidos desde recibos historicos fuera de Control Maestro (flag de
  Wave 117, pendiente de decision del operador).

## Que sigue (decision del operador)

- Repetir AQL 18000 con ventanas pareadas y precalentamiento antes de reconsiderarlo.
- Verificar el camino de revert de RF del colo antes de cualquier step0.
- Captura mas larga de contadores en Panel3 para separar "no tx buffer" de "xmit filtered".

Recibos: `stage1824a_hyperresearch_wave118_119_122_123_125_note626_receipt.json`,
`stage1825a_command_center_1829a_band_refresh_receipt.json`, `stage1829a_wave131_opus2_gate.json`.
