<!-- doc-head: Wave 108 (1686A-1688A) sintesis ES: descubrimiento 4addr WDS half-bind (FMX-DISC-4ADDR-HALFBIND: hostapd Bind#1 + netifd Bind#2), defensa en 3 capas (99-fmx-4addr-verify + peer_healer ban_time=1200 + wpa_group_rekey=86400), superchannel PtP-Colo 6035 MHz (RE binario + preflight live-readonly), Pareto pymoo NSGA-II front-0 sobre 25 campanias reales, nota #622, y scholar INCONCLUSIVO por rate-limit (honesto, no es un negativo) -->
# Reporte ejecutivo - 4addr WDS half-bind, defensa en 3 capas, superchannel 6035 MHz y nota #622

**Wave 108 - Etapas 1686A-1688A - 2026-10-28 - 100% offline (0 SSH, 0 acceso a radios).**

## Que se hizo

Se sintetizo el descubrimiento del half-bind 4addr WDS (FMX-DISC-4ADDR-HALFBIND) y su defensa en 3
capas, el preflight del superchannel PtP-Colo 6035 MHz, y un Pareto pymoo NSGA-II (frente 0) sobre las
campanias reales. Se ingreso la nota #622 (evergreen); el vault paso de 621 a 622. El feed del Command
Center :8787 se amplio a la banda 1536A..1691A.

## Etapa 1686A - half-bind 4addr, defensa en 3 capas y 6035 (nota #622)

**El descubrimiento (FMX-DISC-4ADDR-HALFBIND):** cuando un cliente WDS 4addr se asocia, hostapd
(`nl80211_set_wds_sta`) hace el **Bind #1** en `br-lan` y avisa a netifd por ubus (`sta_connected`), que
hace el **Bind #2** (el puerto AP_VLAN). Si el Bind #2 se pierde o compite con la instalacion de
EAPOL/GTK, el puerto AP_VLAN se traba y el peer pierde trafico en silencio. Fuente:
`firmware/openwrt/common/fmx_ap_4addr_peer_healer.sh`; RE del camino apvlan/WMI en stage1680A
(CONFIRMED_STATIC_BINARY); auditoria del stack instalado en vivo en stage1650A (CONFIRMED_LIVE_HARDWARE,
estado PARTIAL_INSTALLED_STACK_AUDIT).

**La defensa en 3 capas:**

1. Verificacion por evento: `/etc/hotplug.d/net/99-fmx-4addr-verify --fast <sta_if>` 5 s despues del
   alta del AP_VLAN, mas `fmx_ap_4addr_peer_healer.sh` como watchdog cron de 60 s.
2. Ban/backoff: `ban_time=1200` s para que un peer que aletea no reentre al bucle de traba.
3. Higiene de rekey: `wpa_group_rekey=86400` s para refrescar la GTK y re-chequear el puerto en cada rekey.

**Superchannel PtP-Colo 6035 MHz:** stage1657A es un preflight 62<->54 live-readonly
(CONFIRMED_LIVE_READONLY) con el objetivo 6035 MHz; stage1680A tiene la RE de registros del superchannel
(CONFIRMED_STATIC_BINARY). Es un preflight y un artefacto de RE, NO un cutover en vivo.

## Etapa 1686A - recall-first y scholar (honesto)

- **recall-first (vault + MemoryMaster):** 2 de 6 consultas con aciertos (4addr WDS AP_VLAN 2, hostapd
  netifd 1; GTK rekey, wpa_group_rekey, 6 GHz superchannel y colo 6035 dieron 0, por ser nuevos o
  especificos de implementacion).
- **scholar-mcp: INCONCLUSIVO este run (no es un negativo).** El sondeo de liveness del motor funciono
  (P=0.92, source=live), pero la rafaga de verificacion por reclamo quedo **rate-limited**: cada
  scholar_verify_claim y el gate scholar_research devolvieron FETCH_FAILED (ReadTimeout / HTTP 429) en
  los 3 grupos, aunque scholar_search si trajo candidatos. Por eso el grounding de principios generales
  este wave es INCONCLUSIVO por fetch degradado, no un negativo semantico: no leer 0/3 como "la
  literatura refuto esto". La pata EDCA (prioridad de voz) quedo verificada en vivo en Wave 94 (nota
  #620, P=0.97) y se reusa por cita.

## Etapa 1687A - Pareto pymoo NSGA-II + refresh del Command Center

`pymoo` 0.6.2 (NonDominatedSorting, frente 0) sobre los vectores objetivo reales de `results.tsv`
(minimizar fmx_loss y p95, maximizar goodput): 25 campanias con vector valido, **frente de Pareto de 9
puntos** (D1 1, D2 4, D3 1, D4 1, PtMP-WA 2). El mejor punto por fmx_loss es el WA Champion v19
(fmx_loss=0.142). Son puntos empiricos de campanias (mezcla de filas keep/discard en vivo), no un modelo
re-optimizado; las filas crash/NA se excluyeron. Se reconstruyo `FUTURAMAX_COMMAND_CENTER.html`. Recibo
`artifacts/autoresearch/stage1687a_pareto_and_command_center_refresh_receipt.json`.

## Limites y advertencias (honestas)

- **scholar INCONCLUSIVO por rate-limit** (429/timeout), no un negativo; queda apoyado en recall + RE +
  la cita de EDCA de Wave 94. Una re-corrida limpia de scholar queda pendiente.
- La defensa en 3 capas esta instalada/auditada pero el audit es **PARTIAL**; el 6035 es un **preflight**,
  no un cutover. La RE del superchannel y del apvlan/WMI es **binario estatico**.
- **Verificacion en navegador real: NO realizada** (Claude-in-Chrome no conecta); se verifico por CLI y
  balance de etiquetas. El daemon :8787 (hot-reload) se atraso bajo las escrituras rapidas; se dejo un
  restart limpio al cierre para que el estado en vivo refleje la banda 1691.
- Nota de ejecucion: corri las etapas inline (scholar en background, pymoo inline) en vez de spawnear
  workers codex gpt-6-astra con bypass de sandbox, para mantener bajo control directo el etiquetado
  live-vs-binario-estatico y los veredictos de scholar (el estandar de honestidad).

## Que sigue (abierto, decision del operador)

- Re-correr scholar cuando el rate-limit afloje para grounding real de los principios.
- Cutover en vivo del 6035 (no solo preflight) y confirmacion A1->B1->A2->B2 del stack 4addr.

Recibos: `stage1686a_hyperresearch_4addr_dualbind_and_colo_6035mhz_note622_receipt.json`,
`stage1687a_pareto_and_command_center_refresh_receipt.json`, `stage1691a_wave108_opus2_gate.json`.
