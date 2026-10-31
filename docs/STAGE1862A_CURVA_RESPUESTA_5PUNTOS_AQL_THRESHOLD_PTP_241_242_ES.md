<!-- doc-head: Wave 137 cinco puntos AQL observados con controles de cada sesión -->
Síntesis de mediciones físicas existentes; no se crean puntos por interpolación ni se ajusta una curva causal.
Cada contraste conserva sus baselines, configuraciones nativas, pérdidas y restauraciones.
Cambiar límites por AC y momento de adquisición impide atribuir diferencias entre sesiones solo al umbral.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 1862A: respuesta empírica de cinco umbrales AQL

## Qué representa la síntesis

Se reúnen observaciones de PowerBeam .241/.242 obtenidas con tráfico real desde .186.
Los umbrales solicitados son 12000, 16000, 18000, 20000 y 24000 us; cada punto procede de ventanas físicas identificadas.
Este trabajo local no se conecta por SSH, no aplica perfiles y no repite los experimentos históricos.
Dos ventanas sobre el mismo enlace son medidas repetidas, no dos pares de radios independientes.
No se interpola, no se agrupan campañas como si fueran una sola y no se estima un óptimo.
La campaña 1860A terminó y su evidencia quedó vinculada a la ingestión 1863A real.

## Selección correcta de los puntos

| Umbral | Fuente | Brazo elegido | Límites por AC |
|---:|---|---|---|
| 12000 | 1669A | A1/A2 | VO 500/1000, VI 1500/3000, BE 3000/6000, BK 1500/3000 |
| 16000 | 1860A | B1/B2 | Todos 2000/4000 |
| 18000 | 1747A | B1/B2 | Los mismos del 12000 histórico |
| 20000 | 1807A | B1/B2 | Los mismos del 12000 histórico |
| 24000 | 1860A | A1/A2 | Todos 2000/4000 |

Stage 1669A no ensayó B 12000: su B fue 3000 y cambió además VO/BE, BQL y clasificación WMM.
La selección 12000 usa sus ventanas A reales; el contraste completo 1669A se conserva con todos sus cambios.
Stages 1747A y 1807A variaron solo el umbral dentro de sus respectivos ABAB; sus baselines originales fueron 12000.
En 1860A, A 24000/B 16000 comparten todos los AC 2000/4000; el snapshot original 12000 se restaura después de cada fase.
Por tanto, 24000 es un brazo experimental real, no el baseline histórico ni una etiqueta deducida de otro perfil.

## Cinco observaciones, sin ajuste de curva

Cada fila resume dos ventanas seleccionadas de la fuente anterior; no se mezclan sus baselines históricos.

| Umbral us | TCP medio Mbps | Media p95 ms | fmx_loss medio | ICMP recibidos/200 | IPTV perdidos/5700 | VoIP perdidos/1000 |
|---:|---:|---:|---:|---:|---:|---:|
| 12000 | 16.267457 | 9.490000 | 0.6780745 | 196 | 0 | 0 |
| 16000 | 13.296573 | 4.177750 | 0.3866260 | 184 | 11 | 2 |
| 18000 | 18.504317 | 5.272750 | 0.3667895 | 198 | 0 | 2 |
| 20000 | 10.100060 | 5.176000 | 0.4066840 | 150 | 1 | 0 |
| 24000 | 12.232921 | 6.342500 | 0.4084055 | 180 | 0 | 0 |

Ningún punto seleccionado presenta cero pérdida ICMP en sus dos ventanas.
El dato 18000 no se declara óptimo por tener el mejor promedio observado: cambian tiempo y perfil por AC frente a 1860A.

## Contraste fresco 16000 frente a 24000

El AQL por AC fue 2000/4000 en ambos brazos y solo cambió el umbral; nft y demás parámetros capturados permanecieron iguales.
A 24000 obtuvo 12.232921 Mbps y p95 medio 6.342500 ms; B 16000 obtuvo 13.296573 Mbps y 4.177750 ms.
B1 tuvo 7.322156 Mbps, 16/100 ICMP perdidos, 11/2850 IPTV y 2/500 VoIP perdidos.
B2 tuvo 19.270989 Mbps y cero pérdidas en las tres sondas; se conservan ambas ventanas, sin escoger solo B2.
La mejora media no superó el veto de mejora pareada ni el de cero pérdida: decisión discard.
Las ocho restauraciones 1860A y el estado final original 12000 con AC no uniformes quedaron verificados; leases liberados.

## Comparabilidad y verificación

El generador relee JSON nativos de iperf y las respuestas ping, sin convertir ausencia de respuestas en ceros.
TCP enviado y recibido quedan separados; UDP conserva paquetes enviados, total reportado por receptor y pérdidas.
La recepción derivada total-menos-pérdidas se distingue del campo nativo y de cualquier diferencia entre emisor y receptor.
En 1807A-B el IPTV suma 5700 enviados, 5699 como total del receptor y 1 perdido: la diferencia adicional de 1 queda explícita.
Los p95 son percentiles de respuestas recibidas; la media de dos p95 no es el percentil de las muestras agrupadas.
Las pérdidas de ICMP/UDP y los vetos de cada campaña permanecen visibles aunque mejore un promedio.

Se comprueban SHA256/longitud de ventanas y capturas, perfiles kernel antes/después y restauración final.
El inventario nft revela el cambio WMM de 1669A; en 1747A/1807A no cambia entre A/B.
Las identidades de firmware se conservan como SHA de archivo y CRC reportados por el driver, campos distintos.
Las diferencias temporales, RSSI, retries y Sirq observados no desaparecen al ordenar los puntos por umbral.
La igualdad de parámetros no capturados es UNKNOWN; no se presupone ni se rellena.
No hay A/A ni holdout independiente; los resultados no certifican producción ni una relación monótona.

## Baselines y decisión

Cada campaña mantiene su contraste A/B completo y su decisión original, sin elegir solo ventanas favorables.
El archivo 1861A conserva las 16 ventanas de cuatro ABAB y los cinco puntos seleccionados por fuente/brazo.
La síntesis no modifica results.tsv ni reclasifica un discard como keep.
Los cinco pilares referencian investigación y hardware reales reutilizados; el análisis no simula otro ensayo.
La ingestión 1863A aceptó el claim <memorymaster-id>, id 157695, en estado candidate; no es validación independiente.
La comprobación local de cinco pilares, normal y estricta, pasó 5/5 con exit 0 para 1861A.
PASS_EMPIRICAL_SYNTHESIS_ONLY acredita la síntesis y sus fuentes; no cambia los discard ni autoriza promoción.

## Evidencia histórica

[1669A: contraste con múltiples parámetros](../artifacts/autoresearch/stage1669a_live_ptp_colo_step0_channel_plan_and_241_242_ab_receipt.json).
[1747A: umbral 18000](../artifacts/autoresearch/stage1747a_live_241_242_gentle_aql_txq_ab_receipt.json).
[1807A: umbral 20000](../artifacts/autoresearch/stage1807a_live_241_242_aql20000_zero_loss_abab_receipt.json).
[Diseño 1860A congelado](../artifacts/autoresearch/stage1860a/preregistration.json).
[1860A: adquisición real 16000/24000](../artifacts/autoresearch/stage1860a_live_241_242_aql16000_ab_receipt.json).
[Síntesis 1861A: puntos, controles y pines nativos](../artifacts/autoresearch/stage1861a_ptp_aql_threshold_5point_response_curve_receipt.json).
[Ingestión real 1863A](../artifacts/autoresearch/stage1863a_wave137_memorymaster_ingest.json).
