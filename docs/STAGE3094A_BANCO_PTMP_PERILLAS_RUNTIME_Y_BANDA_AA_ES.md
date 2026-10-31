<!-- doc-head: Wave 434 confirma mediciones y restauraci?n; tres contrastes sin promoci?n -->
179 ventanas v?lidas; seis ABAB corregidos completos, todos NO_GO.
Cierre anticipado autorizado por aparici?n de otro peer de banco.
Cero cambios de producci?n y cero escrituras flash.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Wave 434: controles runtime PtMP en banco

## Resultado

**CONFIRMED**: mediciones reales y restauraci?n del banco. **NO_GO** para las tres perillas.
No se propone canary de Panel3. El beneficio no super? el ruido A/A propio de forma reproducible.
Esto no demuestra inutilidad universal de las perillas.

| Control AP | Contraste | ABAB completos corregidos | Ganancias p95 pareadas, ms | Veredicto |
| --- | --- | ---: | --- | --- |
| netdev_tstamp_prequeue | 1 ? 0 | 2 | ?0,875 / ?0,435; ?1,230 / ?2,556 | NO_GO |
| ani_enable | 1 ? 0 | 1 | +2,765 / +2,862; ruido A/A 4,246 | NO_GO |
| gro_normal_batch | 8 ? 16 | 3 | ?2,972 / +4,731; ?0,070 / +0,250; ?3,536 / ?1,826 | NO_GO |

Ganancia positiva significa reducci?n del RTT p95. Tambi?n se exigi? mejora del score sobre su ruido A/A.
Ninguno de los seis bloques completos super? ambos criterios en ambos pares.
El recibo conserva goodput, score, ruido y controles por ventana.

## Selecci?n y protocolo

LAP-120 AP de banco y Loco verificados por claves SSH fijadas y arranque; kernel 6.6.110, ath10k-ct.
Tres controles con cero ensayos aislados PtMP registrados al inicio en las filas congeladas del ?ndice.
El Orchestrator permiti? precedentes PtP: `<orca-id>`; no significa nunca activados en perfiles.
Timestamp cambia ubicaci?n de timestamp RX, cuya demanda efectiva es desconocida.
ANI contrasta adaptaci?n a interferencia; su getter refleja cach? host, no registros efectivos del firmware.
GRO contrasta amortizaci?n del procesamiento RX; el precedente PtP combinado no acredita PtMP aislado.
Se excluyeron controles ya probados y rate override que hab?a causado un crash en W394.
Tambi?n nf_cal_period: alias vac?o enga?oso, S403A-R44 existente y default FW no restaurable con certeza.
ps_state_enable no est? soportado en el mapa WMI10x; TCP local no gobierna este AP usado como bridge.

Tr?fico real host cableado ? bridge AP ? RF ? Loco; servidor ligado al bridge inal?mbrico de la Loco.
El alias LAN de la Loco no se utiliza; el AP no ejecuta iperf3.
TCP bidireccional, P1, buffers de 16 KiB, 20 s; 20 pings de 64 B originados en el AP por ventana.
Goodput es suma de recepciones DL y UL propias, no tasa por sentido ni techo RF.
Se verificaron bytes RF compatibles con la recepci?n; no se calific? backlog sostenido sobre capacidad.
No incluye UDP IPTV/VoIP, validaci?n multicliente ni una garant?a SLA de percentiles extremos.

Cada cohorte corregida usa 12 A/A nuevas y A1-B1-A2-B2, con mismo workload y controles fijos.
A/A y A/B ejecutan watchdog, renovaci?n, escritura del baseline y lecturas equivalentes.
Bandas min/max de la misma corrida y dispositivo; no porcentajes inventados ni valores num?ricos de W388.
Salir de banda restaura y detiene; deriva de A es inconclusa, no da?o atribuible a B.
Se revisan arranque, ?poca de asociaci?n, errores y peers globales antes de continuar.

## Integridad y cierre anticipado

181 intentos: 179 medidos, una A/A rechazada por el parser anterior y un A1 sin tr?fico cargado.
Los 179 v?lidos incluyen 43 exploratorios anteriores y 136 con instrumentaci?n corregida.
Estos ?ltimos: 108 A/A de nueve cohortes y 28 ventanas A/B; seis ABAB completos.
Dos ensayos ANI corregidos se interrumpieron por deriva de A; no se reclasifican como da?os.
3.580/3.580 respuestas ?nicas de ping, cero duplicados; goodput bidireccional 39,320?47,615 Mbps.

A las 22:16:41 UTC apareci? un segundo peer y se dispar? `GLOBAL_AP_PEER_SET_CHANGED`.
La campa?a termin? restaurada a los 117,566 min, antes del presupuesto solicitado de 150 min.
El coordinador confirm? que era una LiteBeam de W440 y orden? cerrar: `<orca-id>`, 22:27:04 UTC.
No se cambi? ni expuls? ese peer; no se mezclan bandas de uno y dos peers.
Una futura cohorte con dos peers necesita A/A nueva.

## Restauraci?n y comprobaciones

Watchdog compartido de 45 s, renovaci?n cada 10 s y fence com?n con la restauraci?n.
La preimagen se congela antes de escribir; cada cambio verifica propietario, token, boot y deadline.
13 episodios A/B y nueve guards A/A restaurados y limpios; 307 renovaciones sin errores registrados.
Lectura final AP 22:28:22 UTC: timestamp=1, GRO=8, ANI=1, FQ=16777216/8192/300, backlog=1000.
AQL permanece 5000/12000 en los cuatro AC, threshold=24000; mismo arranque y estado propio /tmp vac?o.
Comprobaci?n posterior por RF: Loco alcanzable, mismo arranque, receptor iperf3 ausente y ping 10/10.
No se tocaron producci?n, firmware, flash, potencia, frecuencia, SSID ni seguridad.

20 pruebas unittest offline pasan: datos crudos, cuantiles, bytes RF, hashes, restauraci?n y seis tamper negativos.
Dos revisores independientes auditaron el recibo congelado, sin SSH ni editar datos.
Se conservan el primer fallo local de quoting y el primer fallo de igualdad float de un ULP, con su correcci?n.
La A/A rechazada conserva sus datos: diferencia entre puntas de 16384 B no demuestra p?rdida TCP.
El parser corregido exige bytes y tasas exactos entre agregado receptor y sus streams locales.
Tres fuentes A/A hist?ricas exploratorias carecen de cuerpo exacto directo; sus recetas/hashes quedan conservados.
Los bloques exploratorios no sirven para promoci?n.

## Evidencia reproducible

[Recibo y fuentes ejecutadas](../artifacts/autoresearch/wave434_ptmp_autoresearch.json).
[Gate de integridad y cierre](../artifacts/verification/wave434_lane1_ptmp_autoresearch_gate.json).
El recibo incluye fuentes y SHA, snapshots originales, intentos fallidos, parser puro y suite offline guardada.
Las fixtures negativas prueban validaci?n local; no se presentan como evidencia f?sica.
No queda una decisi?n de despliegue: las tres propuestas se descartan para este contexto medido.
