<!-- doc-head: Wave 140 (1878A-1880A) sintesis ES: nota #627 une Waves 126 (SimPy multihop 32 CPE y 29 puntos NSGA-II/III, solo modelo), 128 (auditoria de setter colo bloqueada; A/B aql_threshold 20000 DESCARTADO), 129 (ubnt_poll_host 154 funciones y tabla VoIP de 60 bytes; DRR de ath10k sin resolver), 134 (modelo de buffer TX de Panel3 y 22 puntos NSGA-III que pasan holdout de modelo; la perdida se traslada) y 136 (capa 11ac-compat de 43 funciones en M5, 28 con prefijo lmac); banda :8787 a 1536A..1883A con pagina completa sin apellidos; SIN campeon; scholar negativo parcial -->
# Reporte ejecutivo - Nota #627: SimPy multihop, Panel3, NSGA-III y capa 11ac-compat de M5

**Wave 140 - Etapas 1878A-1880A - 2026-10-28 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se sintetizaron 10 recibos de las Waves 126, 128, 129, 134 y 136 en la nota evergreen #627, el feed del
Command Center :8787 se amplio a 1536A..1883A y la pagina completa quedo sin apellidos de abonados.
Titular honesto: **no hay campeon de trafico nuevo**. Cuatro recibos son modelos SimPy/pymoo sin
aceptacion en hardware, el unico A/B en vivo (AQL 20000) se descarto y el setter del colo quedo bloqueado.

## Wave 126 - SimPy multihop y NSGA-II/III (simulado)

- stage1794A (SIMULATED_MODEL_ONLY): modelo multihop Colo -> Principal -> Guarida -> paneles con 32 IDs
  cpe_ (inventario historico, no censo en vivo). Colo a 40 contra 80 MHz: 163.96 contra 166.19 Mbps; la
  perdida IPTV del modelo es 33.4 % en ambos casos.
- stage1795A (SIMULATED_MODEL_ONLY): 2 corridas NSGA-II y 2 NSGA-III, cada una de 20 individuos por 3
  generaciones. Salen 29 puntos no dominados, re-evaluados en una sola semilla de holdout de 3 s. Ningun
  candidato baja la perdida IPTV del modelo (33.1 a 34.0 %). Nada se promueve.

## Wave 128 - setter del colo y AQL 20000 (en vivo)

- stage1806A (CONFIRMED_LIVE_READONLY): auditoria de solo lectura sobre la radio .54 del colo.
  **Estado BLOQUEADO**: no se aplico nada, el rollback de RF no esta verificado, softrestart puede escribir
  flash y el reset de athchans no es atomico.
- stage1807A (CONFIRMED_LIVE_HARDWARE): un solo A1-B1-A2-B2 en el banco .241/.242 con aql_threshold 20000.
  - TCP por ventana: A1 5.65, B1 3.45, A2 6.15, B2 16.75 Mbps.
  - B perdio el primer par; el ratio 1.711 sale solo de B2.
  - Gates de mejora pareada y cero perdida **fallan** (IPTV 0.035 % en B1).
  - **Decision: descartado**.

## Wave 129 - ubnt_poll_host contra ath10k (estatica)

- stage1812A (CONFIRMED_STATIC_BINARY): ubnt_poll_host.ko tiene 154 funciones y 31 entradas proc que
  comparten solo 3 variables. La tabla _voip_dynamic_duration_levels ocupa 60 bytes (30 valores u16) pero
  su paso de registro no esta probado. ath10k_core.ko esta sin simbolos en este artefacto, asi que **no hay
  quantum DRR** con el cual comparar: solo se prueban los imports de airtime de mac80211.
- stage1813A (CONFIRMED_STATIC_CROSSREF): 8 objetivos; la aritmetica DRR sigue DESCONOCIDA.

## Wave 134 - buffer TX de Panel3 y NSGA-III (simulado)

- stage1842A (SIMULATED_MODEL_ONLY): ajuste descriptivo 4.25 % contra el 3.85 % observado en 1770A (otros
  denominadores, no es calibracion fisica).
  - Con 3 CPEs el brazo AQL de OpenWrt elimina las caidas por descriptor y baja la no-entrega de 3.3 % a
    1.1 %.
  - Con 6 CPEs las caidas por descriptor desaparecen pero la no-entrega queda en 32.4 % en ambos brazos:
    **la perdida se traslada** a la cola de software, no desaparece.
- stage1843A (SIMULATED_MODEL_ONLY): NSGA-III sobre 243 configuraciones; de 50 puntos del frente, **22
  pasan las 8 semillas de holdout del modelo**. No es validacion en hardware.

## Wave 136 - capa 11ac-compat del M5 (estatica)

- stage1854A (CONFIRMED_STATIC_BINARY): ubnt_poll.ko del M5 XW 6.1.4 (553 funciones) trae una capa de
  compatibilidad 11ac de 43 funciones y 9208 bytes. **Solo 28 llevan el prefijo _11ac_compat_lmac_**; las
  otras 15 son hooks _11ac_compat_on_* y ayudantes. El ubnt_poll_host del AC no tiene ninguna, y
  allow_80211 no aparece en ninguno de los 7 modulos. El ruteo de pares legacy por esa capa es inferido y
  la penalidad de airtime es un modelo analitico.
- stage1855A (CONFIRMED_STATIC_CROSSREF): el catalogo de 571 knobs cubre 2 de 10 objetivos medidos del M5.

## recall-first y scholar (honestos)

recall-first: 2 de 6 consultas con aciertos (tabla VoIP 2, aql_threshold 20000 1). scholar: UN chequeo
suave del principio de puntos de referencia de NSGA-III con 4 s de espacio. El sondeo del motor funciono
(P=0.95, source=live) y el verify_claim contra el abstract de un analisis de runtime de NSGA-III dio
**unsupported, P=0.10**: ese abstract no describe los puntos de referencia. Es un negativo parcial sobre un
solo abstract, no una refutacion. Nota #627 ingresada; vault en 627 notas.

## Etapa 1879A - banda 1536A..1883A y pagina sin apellidos

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero (143 recibos). build_html ahora
aplica tools/sanitize_dashboard_pii.py a todo el HTML justo antes de escribirlo: las 21 apariciones
historicas quedaron como cpe_alias_NN y la pagina completa tiene 0 apellidos. Los documentos y recibos
fuente no se reescriben. Quedan nombres de pila junto al alias en 4 celdas de una tabla historica, fuera
del alcance de un sanitizador de apellidos.

## Limites y advertencias (honestas)

- **Sin campeon nuevo**: AQL 20000 descartado; los resultados NSGA y SimPy son de modelo.
- Setter del colo bloqueado; nada aplicado.
- 1746A y 1806A aparecen como no-vivos en el feed porque sus recibos no traen la clave live_devices_touched.
- **Verificacion en navegador real: NO realizada** (Claude-in-Chrome no conecta); se verifico por CLI
  (HTTP 200 + bytes servidos) y balance de etiquetas.

## Que sigue (decision del operador)

- Re-test de AQL con ventanas pareadas y precalentamiento.
- Setter atomico del colo con inverso verificado antes de cualquier aplicacion.
- Captura en vivo de Panel3 que separe caidas por descriptor de desborde de software.
- Decidir si se eliminan tambien los nombres de pila de la tabla historica.

Recibos: `stage1878a_hyperresearch_wave126_128_129_134_136_note627_receipt.json`,
`stage1879a_command_center_1883a_band_refresh_receipt.json`, `stage1883a_wave140_opus2_gate.json`.
