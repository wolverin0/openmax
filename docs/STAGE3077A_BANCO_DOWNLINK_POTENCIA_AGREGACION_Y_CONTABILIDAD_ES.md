<!-- doc-head: W417; potencia RAM real y agregacion downlink en banco, dos NO_GO y restauracion observable confirmada -->
34 ventanas reales; sin CT rate override, produccion, flash ni configuracion persistente.
Recibo artifacts/autoresearch/wave417_downlink_airtime.json; gate wave417_lane1_downlink_airtime_gate.json.
MCS0..3 no sostenidamente calificado; no se certifica una CPE lejana ni airtime fisico por paquete.
<!-- /doc-head -->
# Stage3077A: potencia, agregacion y contabilidad de bajada

## Evidencia previa aplicada

- Se leyeron los seis documentos pedidos y W402 antes del banco; no se repitio su RE.
- W398 reporta1267us/paquete; W402 advierte mezcla de contadores y denominadores.
- W402 separa A-MSDU del primer campo y A-MPDU del segundo en htt_max_amsdu_ampdu.
- Se excluyeron override CT, mascaras de tasa, otros radios y escrituras persistentes.

## Banco y atenuacion natural

- AP LAP-120 .20 y Loco logica .250/RF .200.41, transporte IPv6 con claves de host fijadas.
- OpenWrt/kernel6.6.110,5180MHz,VHT20; hashes nativos de modulos y firmware retenidos.
- ath10k_core coincide con el candidato W402; mac80211 personalizado tiene otro hash.
- Preimagen: solicitud por VIF20dBm/global20, efectivo cacheado17, agregacion3/64.
- Se uso iw dev set txpower fixed, watchdog45s renovado sin cambiar generacion y fence atomico.
- Solicitudes20,10,5,0dBm: goodput63.10,58.04,44.55,39.32Mbps.
- RSSI recibido aprox -46,-54,-58,-59dBm; el hardware respondio, sin calibrar potencia RF.
- A0dBm solicitados, MCS4-5 en calificacion; luego hubo MCS3 pero no sostenido.
- No se probaron negativos: mac80211 los rechaza. Potencia de Loco no modificada.
- Fixed vs limit previo no tiene getter: se restauro fixed20 segun receta netifd instalada/UCI20.
- La igualdad de valores observables no prueba el modo oculto original ni potencia fisica calibrada.

## Diseno

- Cuatro ventanas de potencia, seis A/A compartidas y tres A1-B1-A2-B2 por candidato.
- A comun3/64; candidato W4023/32 (solo A-MPDU); H3 2/64 (solo A-MSDU).
- Potencia solicitada0 durante todas las A/A y A/B; AQL,FQ,airtime flags y canal originales.
- Host cableado envia TCP4flujos,16KiB,20s hacia receptor Loco; ICMP cada1s.
- Se prueban bytes recibidos contra peer TX, radio RX y Ethernet RX para descartar bypass.
- No son mediciones bidireccionales ni Triple-Play. Un peer no demuestra fairness.
- Guardas: nuevo crash/OOM,reboot,fallo de asociacion o instrumentacion; sin piso RAM inventado.

## Resultados: medianas de goodput y percentiles por ventana

| Candidato | Goodput A/B Mbps | Delta | p95 A/B ms | Delta | us/paquete A/B | Decision |
| :-- | --: | --: | --: | --: | --: | :-- |
| A-MPDU64 a32 | 36.942/35.733 | -3.27% | 20.192/22.617 | +12.01% | 2164.04/2150.11 | NO_GO |
| H3 A-MSDU3 a2 | 39.236/38.673 | -1.44% | 16.841/19.762 | +17.34% | 2163.77/2162.85 | NO_GO |

- Banda A/A pareada: goodput -5.19..+0.93%; p95 -22.61..+51.06%; us/paquete -0.763..+0.040%.
- Las reducciones us/paquete (-0.643% y -0.043%) no exceden el extremo favorable A/A.
- Tampoco hay mejora p95 consistente; controles A y RSSI varian, no atribuir cambios pequenos.
- Perdida agrupada por conteo: W402 A/B0/0%; H3 A0%, B1.667% (118/120).
- Una ventana B de H3 perdio2/20pings; la mediana de perdidas habria ocultado ese10%.
- Total678/680pings en34ventanas; percentiles de20son descriptivos, no SLA de cola extrema.

## El contador no es airtime fisico

- Delta tx_duration / delta tx_packets calculado con los contadores crudos y mismo boot.
- La duracion reportada dividida por tiempo monotono da 5.84..11.69 veces la ventana.
- Survey TX/activo en esas ventanas da 53.59..74.25%; son fuentes distintas, sin normalizarlas.
- El fallback host6Mbps+100us da floor((1511+38)*80/60)+100=2165us.
- Es compatible numericamente con lo observado; no demuestra last_tx_bitrate=0 ni su productor.
- El retorno CT temprano no basta: hay otro escritor de tasa en HTT per-peer.
- Faltan service map runtime, entrega de eventos, cohortes y exportador mac80211 exacto.
- La continuacion estatica WSL termino con WSAETIMEDOUT; no hubo reinicio ni reintento.
- El getter de agregacion es cacheado; no se midio la distribucion efectiva de subtramas.

## Cierre

- NO_GO ambos; prueba de MCS muy bajo/lejana sigue sin calificar y no se promociona a Panel2.
- Sin nuevo crash ni OOM. El crash W394 ya estaba en el log basal y se conserva como tal.
- Restore verifico solicitud20/global20/cache17 y3/64, perfil FQ/AQL/canal original.
- Lectura independiente final:10/10pings, RSSI de retorno -44dBm,34receptores terminados.
- Workspace, handle y bloqueo global ausentes; procesos propios ausentes.
- 15 pruebas locales de integridad/tamper; incluyen que la perdida agrupada no desaparezca.
- Gate confirma datos y restauracion observable; target heredado de Panel3 no se midio en este alcance.
