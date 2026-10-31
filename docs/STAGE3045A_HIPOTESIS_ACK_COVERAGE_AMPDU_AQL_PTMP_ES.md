<!-- doc-head: Stage 3045A (W385) ES: investigacion offline (vault hyperresearch del reactor, scholar-mcp y OpenAlex) sobre timeout de ACK, coverage class, A-MPDU y AQL en PtMP largos con CPE stock y OpenWrt. Cinco hipotesis ordenadas con citas; la primera (anomalia de airtime y cola en Panel2) se puede probar en el banco LAP-120 con una Loco OpenWrt y un Rocket stock, con valores tomados del ledger -->
Que cubre: hipotesis ordenadas, su evidencia local y bibliografica, y el A/B de banco que se le pasa a lane_1.
Estado: offline. 0 accesos a equipos. Pasos de ingesta del reactor no ejecutados porque escriben fuera del alcance.
Datos maquina: artifacts/autoresearch/wave385_hyperresearch.json.
Leer cuando: antes de planear el proximo A/B de banco sobre AQL, A-MPDU o coverage class en PtMP.
<!-- /doc-head -->
# Stage 3045A: hipotesis ACK, coverage class, A-MPDU y AQL en PtMP (W385)

## 1. Punto de partida

- **W382 (MEASURED):** el tramo de radio de Panel2 tiene mediana 40 ms (Panel1 3, Panel3 12) y sus CPE suben en MCS 0 a 3.
- **W369:** bajada en MCS 0 solo en las 3 CPE a mas de 2 km; subida en MCS 0 tambien en CPE a 300-450 m.
- **Banco:** W376 aborto sin ventanas; W384 dio B1 -2,8 % contra la banda A/A con clase 6 (un par, NO_GO). Solo miden costo.
- **Indice de perillas:** en PtMP OpenWrt coverage_class, aql_txq_limit, aql_threshold, htt_max_amsdu_ampdu y agg_sw_retry_th no tienen efecto medido aislado.

## 2. Hipotesis ordenadas

| # | Hipotesis | Confianza | Banco |
| :-- | :-- | :-- | :-- |
| 1 | Latencia de Panel2 por anomalia de airtime y cola, no por distancia | INFERRED | si |
| 2 | Timeout de ACK/BA corto para CPE a mas de unos 2,3 km | INFERRED | solo costo |
| 3 | Tope de A-MPDU menor ayuda a las estaciones rapidas | UNKNOWN | si, despues de 1 |
| 4 | Asimetria stock/OpenWrt: el AP no tiene dynack | INFERRED | solo lectura |
| 5 | Menos reintentos de software por agregado | UNKNOWN | bloqueada: sin valor con fuente |

**1. Anomalia y cola.** Las CPE cercanas de Panel2 tambien tardan 44 a 54 ms, asi que la distancia no alcanza. Heusse et al. (INFOCOM 2003, doi 10.1109/INFCOM.2003.1208921): una estacion lenta baja a todas. Hoiland-Jorgensen et al. (ATC 2017, arXiv 1703.00064): la cola en el AP baja un orden de magnitud la latencia y el reparto de airtime no toca a los clientes. PoliFi (WCNC 2019, doi 10.1109/WCNC.2019.8885440).
- Precondicion de solo lectura: si el phy anuncia AIRTIME_FAIRNESS (UNKNOWN en QCA988x con firmware CT) y el AQL actual de Panel2.

**2. Timeout de ACK.** 2534A indica que el CTS cubre unos 2,3 km; cpe_210_9 (2,7-2,85 km) y cpe_210_21 (2,1-2,7 km) quedan al borde. Simo-Reigadas et al. (IEEE TMC 2010, doi 10.1109/TMC.2010.27), WiLDNet (NSDI 2007) y 2P (MobiCom 2005, doi 10.1145/1080829.1080847) muestran que el MAC sin ajustar rinde mal a distancia. El banco no tiene retardo: el beneficio solo se mide en Panel3 con aprobacion.

**3. A-MPDU.** A MCS 0 un agregado ocupa varios ms. Ledger 381A (PtP, enlace corto): 3 contra 2 A-MSDU dio -3,8 %. No se encontro literatura especifica.

**4. Mixto.** ath10k-ct no tiene dynack (W369); airOS ajusta su distancia. Hoy Guarida es 18/18 OpenWrt, asi que aplica a migraciones futuras.

**5. Reintentos.** airOS 62A dio +26 %, pero no hay valor medido para OpenWrt.

## 3. A/B para lane_1 (banco LAP-120 .20 + Loco .250 + Rocket .198)

1. **H1:** forzar la Loco a MCS bajo en RAM con `iw set bitrates`; carga TCP a las dos estaciones. A = AQL de OpenWrt 5000/12000 (ledger 140A), B = 1500/3000 del champion (ledger 123A y 140A). Metricas: p95 y p99 de la estacion rapida, goodput agregado y airtime por estacion si se expone.
2. **H3:** mismo montaje, htt_max_amsdu_ampdu por defecto contra 2 (ledger 381A).
3. **H2 costo:** clase 0 contra 6 en el AP con mas pares que W384.
- Una perilla por A/B, valores del ledger y sin pisos de aborto nuevos. No usa .241/.242.

## 4. Limites y contrato

- Jev marco partial o unsupported 3 de 4 claims aunque el fragmento citado los respalda; se reportan tal cual.
- Las citas son a nivel resumen; no se leyeron los textos completos.
- **Karpathy: TARGET_NOT_MET.** Las tres metricas piden equipos y esta ola es offline.
