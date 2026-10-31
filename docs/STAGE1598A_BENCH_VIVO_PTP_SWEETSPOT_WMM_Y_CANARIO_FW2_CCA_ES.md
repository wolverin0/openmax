<!-- doc-head: Wave93 sweet spot vivo WMM y canario firmware2 bloqueado -->
Ocho ventanas reales; canario bloqueado y deriva historica del ledger preservada.
La integridad de los recibos no equivale a aceptacion del canario ni promocion.
<!-- /doc-head -->

# Stage1598A: banco vivo PtP, sweet spot y firmware2

Estado global: PARTIAL_BLOCKED_FIRMWARE_CANARY. El mandato completo de firmware no se ejecuto.
Banco .241 AP y .242 STA, trafico real iperf3 desde .186. Solo el coordinador ejecuto SSH de radio.

## Diseno finito y mediciones

Tres slots preregistrados; A1/B1/A2/B2 de20s en iteraciones1 y3. Iteracion2: crash/NA y cero ventanas.
Carga: TCP, IPTV UDP3Mbps/1316B y sondas G711 equivalentes64kbps/160B. ICMP:200 sondas64B/100ms.
Clasificacion bridge postrouting_wmm: EF/CS6 ->priority262/UP6, corroborada por counters nft y TID6/AC0.
Iteracion1 B: VO300/600us, BE1200/2400us, aql_threshold3000, eth0 BQLmax16384.
Iteracion3: repeticion del mejor kernel elegible si I1keep; de otro modo, refinamiento preregistrado BE1800/3600, threshold6000 y BQLmax24576.
Keep: mejora emparejada fmx_loss>=0.005, capacidad media>=95%, UDP<=2% y restauracion exacta.
Sirq se audita sin afirmar CPU cero ni causalidad LED. El objetivo completo incluye IPTV0% y canario vivo aceptado.

| Iteracion | Decision | Ventanas | p95 B ms | TCP B/A | fmx_loss |
|---|---|---|---|---|---|
| 1 | keep | 4 | 4.603 | 96.20% | 0.405531 |
| 2 | crash | 0 | NA | NA | NA |
| 3 | keep | 4 | 4.189 | 99.56% | 0.649440 |
I1: perdida IPTV maxima en B=0.052641%; VoIP=0.000000%.
I3: perdida IPTV maxima en B=0.070188%; VoIP=0.100000%.

No se sustituyeron medidas faltantes por cero ni se reutilizaron ventanas anteriores.
Las comparaciones kernel corresponden al firmware RAM preexistente a491; no al stock398 ni al nuevo canario Stage1579.

## Precondicion fallida y origen de la diferencia

El pathname activo mide204796B, pero SHA256 es `a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f`.
El requerido es `398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e`. Solo /rom coincide con el requerido.
En ambas radios ya habia tmpfs montado sobre /lib/firmware/ath10k/QCA988X/hw2.0 antes de Wave93.
firmware_info selecciona firmware-2.bin; fw_checksums del buffer retenido informa firmware92363606 y athwlan12b29d01.
Un SHA correcto en /rom no satisface la condicion sobre el archivo activo. No se desmonto la capa RAM ajena para forzarla.
Por eso no se armo el timer setsid de firmware, no hubo bindmount nuevo y no se recargo ath10k_pci.
El rollback de firmware queda NOT_EXECUTED, no PASS. Las guardias60s verificadas en esta ola cubren controles kernel.

## Canario offline y limites

El artefacto Stage1579 existente mide208179B y SHA `7747640770370b5700c31c9b35f5f14d2741e246a7d203188cdb9320656e4dc3`.
Su preimage decodificado de16B comienza en0x009b7584; el byte72->76 esta en0x009b758e, indice10 del preimage.
El artefacto por defecto tambien cambia invalid->Invalid en IE3seg1, vaddr0x0040bc3c.
El round-trip bit-exacto de segmentos es evidencia offline de integridad. No prueba carga BMI, WMI_READY ni cambio CCA fisico.
Una futura prueba requiere resolver el SHA activo con el operador, guardar baseline, probar guardia desacoplada y verificar buffers retenidos tras recarga.
Nunca se debe normalizar el origen ni aceptar solo el hash del pathname para sortear ese gate.

## Auditoria y restauracion

Se conservaron cinco muestras de cadenas RSSI, reintentos, airtime, colas y LED por ventana, mas24 muestras CPU a1s.
Los contadores FCS del firmware son del dispositivo/canal. dot11FCSErrorCount no soportado permanece UNKNOWN.
Los maximos Sirq a1s no demuestran ausencia de transitorios mas breves ni sobrecarga causal del daemon sin LED-OFF.
Al cerrar se restauro exactamente AQL/BQL/quantum/threshold original y se retiro solo el modulo nft_meta_bridge propio.
Se verificaron SHA activo a491, bytes, checksums retenidos y montaje tmpfs inicial sin cambios; LEDv4 conserva sus bytes y AUTO.
No hubo flash, cambio de particiones protegidas, produccion o PtP-Colo. Se liberaron solamente leases propios.
La falta del ensayo firmware mantiene mission_complete=false y required_fw2_live_acceptance=false aunque pytest pase.

## Artefactos

Validacion solicitada:129 tests Wave93 y203 del motor Wave91 aprobados, sin omisiones.
La ejecucion ampliada conserva473 aprobados y un fallo historico Wave84 sobre el prefijo de results.tsv.
El snapshot previo a nuestro anexo ya diferia del snapshot historico; nuestras tres filas preservaron su prefijo de3974B.
No se modificaron ledger compartido, snapshot ni test historico para forzar un PASS global.
[Registro de deriva previa](../artifacts/autoresearch/stage1596a/historical_ledger_drift_observation.json).

[Recibo1596A](../artifacts/autoresearch/stage1596a_live_ptp_pbe5ac_sweetspot_wmm_and_fw2_cca_ram_receipt.json).
[Auditoria1597A](../artifacts/autoresearch/stage1597a_live_ptp_fw2_ram_bindmount_and_sirq_audit.json).
Cinco pilares: fuentes/canario offline identificado, consultas del reactor y bibliografia reutilizada, controles ABAB kernel, diseno experimental y recall MemoryMaster.
Los IDs FMX vinculan evidencia local; no representan una nueva ingesta durable ni certificacion de produccion.
