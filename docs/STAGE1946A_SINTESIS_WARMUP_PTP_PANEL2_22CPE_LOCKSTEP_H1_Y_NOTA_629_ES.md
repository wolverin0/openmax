<!-- doc-head: SUPERSEDED (W435, 31/10): PtP-Colo HOLD 9/9 at 6035 MHz is historical; production Colo runs OpenWrt 24.10.4 at ch153 / 5765 MHz and the link is 450 m (operator 30/10). Wave 151 (1944A-1946A) sintesis ES: nota #629 une Waves 144 (retest AQL 18000 con precalentamiento DESCARTADO + precheck de corte del colo en HOLD 9/9), 146 (telemetria 3 paneles: no_tx_buffer == xmit_filtered en toda ventana + ciclo sysctl XC/LTU), 148 (sector denso Panel2 22 CPE SimPy + NSGA-III con 0 candidatos factibles) y 149 (verificador de call-chain del dossier + matriz de reproducibilidad FAIL); banda :8787 a 1536A..1949A con IDs cpe_ canonicos; SIN campeon; scholar negativo parcial -->
# Reporte ejecutivo - Nota #629: precalentamiento AQL, corte del colo, lockstep de Panel3 y 22 CPE

**Wave 151 - Etapas 1944A-1946A - 2026-10-28 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se sintetizaron 8 recibos de las Waves 144, 146, 148 y 149 en la nota evergreen #629, el feed del Command
Center :8787 se amplio a 1536A..1949A y se compactaron los docs maestros. Titular honesto: **no hay
campeon de trafico nuevo**. El retest de AQL 18000 con precalentamiento se volvio a descartar, el corte del
colo quedo en espera y el modelo de 22 CPE no encontro ninguna configuracion factible.

## Wave 144 - retest AQL 18000 con precalentamiento y precheck del colo (en vivo)

- stage1902A (CONFIRMED_LIVE_HARDWARE): el banco .241/.242 se precalento (servidor, trafico TCP y lecturas
  antes/despues) para quitar el artefacto de A1 frio de 1747A/1807A. Un solo A1-B1-A2-B2 con el brazo B en
  aql_threshold 18000.
  - TCP por ventana: A1 13.29, B1 18.52, A2 19.38, B2 18.22 Mbps.
  - A1 siguio bajo (con 0.07 % de perdida IPTV y 0.2 % VoIP) y B perdio el segundo par.
  - Fallaron los gates de mejora pareada y de cero perdida. **Descartado**. El precalentamiento no rescato
    al umbral 18000.
- stage1903A (CONFIRMED_LIVE_READONLY): precheck de solo lectura del par del colo. El hash de la imagen
  factory quedo verificado y la config activa sin cambios, con 0 escrituras. La lista de corte de 9 pasos
  esta **9 de 9 en HOLD_NOT_EXECUTED**; ejecucion atomica, apply/rollback seguro y arranque hibrido sin
  certificar; operational_ready=false.

## Wave 146 - telemetria de 3 paneles y ciclo sysctl (en vivo, solo lectura)

- stage1914A: en cada ventana medida "no tx buffer" es igual a "xmit filtered" (Panel3 2513/1845/2284,
  Panel2 15592). Panel3 da 1.925 / 7.17 / 5.315 %, ahora en patron BURSTY (1818A era CONTINUO). Panel2:
  7 de 22 CPEs asociados, CPU del AP 95 %. Panel1: 3 CPEs sanos. El lockstep coincide con 1830A: ambas
  etiquetas leen un contador de enviados/completados, asi que ningun porcentaje es una tasa de caida.
- stage1915A: 3 sysctl reversibles del plano de gestion (rmem_default, optmem_max, tcp_fin_timeout),
  todos restaurados; no tocan el camino de datos.

## Wave 148 - sector denso Panel2 de 22 CPE (simulado)

- stage1926A (SIMULATED_MODEL_ONLY, 15 de 22 filas inferidas): el brazo stock pierde 87.6 % a nivel
  aplicacion; el brazo AQL de OpenWrt elimina las caidas por descriptor y mejora Jain (0.86 vs 0.63) y el
  p95 de VoIP (17.4 ms), pero la perdida de aplicacion sigue en 85.1 % y el p95 de cola sube a 437 ms:
  **la perdida se traslada** a la cola de software.
- stage1927A (SIMULATED_MODEL_ONLY): NSGA-III sobre 324 configuraciones con restricciones de cero caidas
  por descriptor, VoIP p95 < 15 ms y no-entrega < 1 %: **0 factibles, 0 en el frente, 0 en holdout**. No
  existe la curva de 34 puntos del enunciado.

## Wave 149 - dossier y reproducibilidad (estatica)

- stage1932A (CONFIRMED_STATIC_BINARY): de 18 afirmaciones del dossier, 9 CONFIRMED + 4 CONFIRMED_INSIDE,
  **2 refutadas** (C03 cae dentro de ame_fwd_mmap, no ame_fwd_open; C05 en mFifo_fault, no mFifo_create),
  2 no verificables offline y 1 discrepante. Son las dos unicas correcciones de offset que necesita.
- stage1933A (CONFIRMED_STATIC_CROSSREF): la matriz de reproducibilidad da **FAIL**: 1 ruta rota, 16 ids
  de descubrimiento citados sin registrar; 6 de 6 afirmaciones numericas mapean a un artefacto; 0
  apellidos en los 2 documentos publicos.

## recall-first y scholar (honestos)

recall-first: 3 de 6 consultas con aciertos (Panel2 22 CPE 6, matriz de reproducibilidad 3, checklist del
colo 1). scholar: UN chequeo suave del principio de equidad de tiempo de aire. El sondeo del motor
funciono (P=0.88) pero el verify contra el abstract de "PoliFi: Airtime Policy Enforcement for WiFi" dio
unsupported, P=0.18: ese paper trata de politicas de tiempo de aire, no de reparto equitativo. Negativo
parcial, no una refutacion. Nota #629 ingresada; vault en 629 notas.

## Etapa 1945A - banda 1536A..1949A y docs maestros

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero (178 recibos) con 0 apellidos
del alcance y 0 alias en toda la pagina (IDs cpe_ canonicos). Los docs maestros se compactaron con una
sola seccion de Waves 94..151 cada uno (<=179 lineas).

## Limites y advertencias (honestas)

- **Sin campeon nuevo**: el retest de AQL 18000 con precalentamiento se descarto.
- El corte del colo sigue en espera: 9/9 pasos sin ejecutar.
- Todo porcentaje de "no tx buffer" es un ratio de un contador mal etiquetado hasta ligar el hash del
  modulo en vivo.
- Quedan nombres de pila o apellidos de OTROS abonados en tarjetas historicas, fuera del alcance de 4
  apellidos: hace falta una lista aprobada por el operador.
- **Verificacion en navegador real: NO realizada** (Claude-in-Chrome no conecta); se verifico por CLI.

## Que sigue (decision del operador)

- Ligar el hash del umac.ko en vivo a los offsets de 1830A antes de creer cualquier porcentaje de buffer.
- Autorizar (o no) una ventana de corte del colo para ejecutar la lista de 9 pasos.
- Corregir los 2 offsets del dossier antes de cualquier envio.
- Aprobar la lista de apellidos adicionales para limpiar toda la pagina.

Recibos: `stage1944a_warmup_ptp_panel2_lockstep_h1_note629_receipt.json`,
`stage1945a_command_center_1536a_1949a_refresh_receipt.json`, `stage1949a_wave151_opus2_gate.json`.
