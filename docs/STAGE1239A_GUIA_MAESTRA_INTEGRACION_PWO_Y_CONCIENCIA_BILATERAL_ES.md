<!-- doc-head: Stage1239A guia maestra en espanol de integracion del PredictiveWirelessOptimizer de whatsappbot-final con el bundle 1238A y la conciencia bilateral 3-tier SG-01, what-if/Pareto, peer-buddy AQM, diagnostico 9 sintomas/25 RC, tablas LTU y reglas de brecha; todo recommend-only -->
<!-- /doc-head -->

# Stage1239A - Guia maestra de integracion PWO y conciencia bilateral

Documento solo de guia (sin recibo propio). Offline, `live_devices_touched=false`. Fuente de datos: bundle de `artifacts/verification/stage1238a_pwo_whatsappbot_contract_bundle.json`, generado por `tools/uisp/pwo_whatsappbot_contract_exporter.py`.

## 1. Reglas de oro (honestidad)
- Todo es recommend-only: `recommend_only=True` y `auto_approve=False` en el bundle y en cada tarjeta.
- Ancho de canal fijo en 20 MHz (`fixed_width_mhz=20`); nunca se propone otro ancho.
- Todo proviene de modelos y entradas fabricadas offline: no hay radios, no hay llamadas en vivo, no es evidencia de campo.
- Cada recomendacion requiere aprobacion humana antes de ejecutarse.
- La atribucion a `.ko` es estatica (ingenieria inversa mas base comunitaria), no una reproduccion en vivo.

## 2. Como ingiere el PWO el bundle
1. El PredictiveWirelessOptimizer de whatsappbot-final lee el JSON del recibo `stage1238a_pwo_whatsappbot_contract_bundle.json` (copia manual por el operador; el exportador nunca escribe dentro de whatsappbot-final).
2. Comprueba `schema_version == "pwo-contract-1.0"`; si es otra version, rechaza el bundle.
3. Verifica `invariants`: `recommend_only` True, `auto_approve` False, `fixed_width_mhz` 20, `sg01_backbone_poe_protected` True. Cualquier desviacion invalida todo el bundle.
4. Revisa `validation.all_sections_present` y `validation.module_presence`: si un modulo falta, esa seccion es nula y el PWO debe degradar a solo lectura.
5. Carga las 6 secciones: `backbone`, `channel`, `peer_buddy_aqm`, `symptom_diagnostics`, `ltu_capability_tables`, `coverage_gap_rules`.
6. El validador de referencia es `validate_bundle()` del mismo modulo; el lado PWO debe replicar sus reglas.

## 3. Conciencia bilateral de sitio 3-tier y SG-01
- Seccion `backbone`, modulo `tools/uisp/full_3tier_backbone_and_sg01_guard_engine.py`.
- Tres niveles: Edificio Principal (tier 1), Almafuerte (tier 2, AP del PtP), Guarida (tier 3, STA del PtP con paneles 1 a 3).
- `blast_radius` da, por nodo o salto, los CPE aguas abajo y la ruta afectada: una falla en el salto Almafuerte-Guarida arrastra los CPE de Guarida (modelo sin doble conteo).
- SG-01: nunca apagar, desenergizar ni reciclar el PoE del backbone (`ether2-sw-poe200`, switches .200 y .201). Solo verbos de lectura pasan; todo lo demas se veta, fail-closed.
- En `sg01.probes`, deshabilitar el puerto y reciclar el switch .201 salen vetados; leer el estado sale permitido. El PWO debe pasar por este veto toda accion que mencione esos objetivos.

## 4. Simulador what-if de canal y Pareto
- Seccion `channel`, modulo `tools/uisp/bilateral_whatif_channel_simulator_and_pareto_ranker.py`.
- Enumera candidatos a 20 MHz y los puntua en ambos extremos del enlace `ptp-almafuerte60-guarida61`.
- Objetivos a minimizar: `bilateral_overlap`, `blast_radius_cpes`, `dfs_outage_risk`.
- `pareto_front` contiene los no dominados; el resto queda marcado `dominated`.
- `counterfactual` compara un optimizador unilateral (solo ve Guarida) contra el bilateral: el unilateral puede elegir un canal que colisiona en el extremo lejano; el bilateral lo evita. Esa es la razon de la conciencia bilateral.
- El PWO muestra el candidato como sugerencia; cambiar el canal lo decide una persona en ventana de mantenimiento.

## 5. Peer-buddy y AQM feed-forward backhaul a sector
- Seccion `peer_buddy_aqm`, modulo `tools/uisp/on_tower_peer_buddy_and_anomaly_disambiguator.py`.
- `disambiguate` clasifica en tres: `CO_SITE_SELF_INTERFERENCE`, `POP_POWER_OR_WEATHER_EVENT`, `SINGLE_RADIO_HANG`, con confianza y justificacion.
- Util para no confundir una falla de energia o clima de todo el PoP con autointerferencia o un radio colgado.
- `aqm_feed_forward`: si la capacidad del PtP aguas arriba cae X por ciento, se sugiere apretar el `target` y el `limit` de fq_codel/Cake del sector proporcionalmente (muestras al 0, 25, 50 y 75 por ciento).
- Es una sugerencia (`recommend_only=True`); el operador aplica el cambio.

## 6. Diagnostico de 9 sintomas y 25 RC con atribucion .ko
- Seccion `symptom_diagnostics`, modulo `tools/uisp/community_symptom_and_ko_root_cause_pwo_matcher.py`.
- 9 clases de sintoma (colapso de tasa de un CPE, parada silenciosa, falso DFS, M5 en AC, caida Ethernet 100M a 10M, modulacion LTU atascada, tormenta de desconexion, falla ATPC, latencia UDP/IPTV).
- Cada clase trae su `.ko` probable (`ubnt_poll_host.ko`, `ath10k_core.ko`, `eab_driver.ko`, `ame_core.ko`), confianza acotada a 0.9 y pasos de remediacion; los 25 RC y 117 hilos comunitarios respaldan la base (`thread_counts`, `kb_source`).
- La tarjeta `pwo_card` siempre lleva `auto_approve=False`; ningun paso se ejecuta solo.
- Sin coincidencia, el matcher devuelve confianza 0 y escala a un humano.

## 7. Tablas de capacidad LTU
- Seccion `ltu_capability_tables`, modulo `tools/uisp/pwo_ltu_binary_capabilities_and_frame_reconciler.py`.
- El binario `ame_core.ko` habilita 4096-QAM (12x, MCS 31) en 10, 20, 30, 40 y 50 MHz con MIMO 2x2; 60, 80 y 100 MHz quedan sin 4096-QAM. El PWO suponia 1024-QAM: discrepancia a corregir.
- Duraciones de trama del binario: 2, 2.5, 4 y 5 ms (el PWO solo listaba 2, 4 y 8 ms).
- Ojo: el ancho operativo propuesto sigue fijo en 20 MHz; las tablas describen capacidad, no una orden de cambiar ancho.

## 8. Las 3 reglas de brecha de cobertura
- Seccion `coverage_gap_rules`, modulo `tools/uisp/pwo_coverage_gap_rules_stall_eth_disconnect.py`.
- `SILENT_TRAFFIC_STALL_WHILE_ASSOCIATED`: asociado, RF sana, pero sin trafico o con perdida alta.
- `ETHERNET_LINK_SPEED_AND_CRC_FLAP`: velocidad Ethernet bajando o picos de CRC (causa fisica: cable, PoE, puerto).
- `CPE_DISCONNECT_STORM_AND_GPS_TA_DRIFT`: reasociaciones masivas con deriva de TA de GPS.
- Cada regla emite tarjetas recommend-only con causa raiz probable; una muestra sana debe dar cero tarjetas.

## 9. Flujo integrado recomendado
1. El PWO detecta un sintoma y lo pasa por `coverage_gap_rules` y `symptom_diagnostics`.
2. Desambigua con peer-buddy para separar PoP, autointerferencia y radio colgado.
3. Si hay que mover canal, consulta `channel` (bilateral, 20 MHz, Pareto) y `backbone` (radio de explosion).
4. Toda accion pasa por el veto SG-01; el PoE del backbone no se toca jamas.
5. Si cae la capacidad del PtP, sugiere el ajuste AQM; valida contra `ltu_capability_tables` si hay radios LTU.
6. Presenta la tarjeta a una persona; solo ella aprueba y ejecuta.

## 10. Verificacion
- Autoprueba: `tests/test_stage1238a_contract_exporter.py` (secciones, invariantes, validacion, bundle alterado falla).
- Regenerar el recibo: `python -m tools.uisp.pwo_whatsappbot_contract_exporter --write-receipt`.
