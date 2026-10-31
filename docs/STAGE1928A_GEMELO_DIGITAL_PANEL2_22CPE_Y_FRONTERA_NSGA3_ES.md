<!-- doc-head: Wave148 Panel2 22 CPEs, estudio offline NSGA-III sin candidato factible por no entrega de voz -->
<!-- /doc-head -->

# Stage1928A: gemelo digital Panel2 y frontera NSGA-III

Estudio local ejecutado con SimPy y pymoo. Atribucion: external controller.
CONFIRMED: ejecucion, semillas, contabilidad y resultados del programa.
INFERRED: comportamiento del modelo abstracto. UNKNOWN: QoE y compatibilidad de hardware.
No se abrieron conexiones SSH ni se escribieron radios. Ningun candidato fue promovido.

## Topologia y alcance

La radiografia aporta 22 CPEs de Panel2: 7 filas CONFIRMED y 15 INFERRED.
Se unieron dos rankings por identificador privado; solo se emiten cpe_001..cpe_022.
Estos IDs son locales al modelo y no identificadores globales de abonados.
Las clases de SNR modelado son near=1, mid=14, far=7.
SNR = RSSI - (-174 + 10 log10(40e6) + 7 dB NF) - 6 dB de margen.
No hay medicion de ruido RF; el SNR Ethernet no se usa como SNR de radio.

Cada CPE genera voz de 160 B cada 20 ms, IPTV de 4 Mbps y rafagas bulk.
Bulk usa 12..45 paquetes de 1500 B, intervalo exponencial medio de 35 ms.
Es trafico ofrecido sin realimentacion TCP, no una pila TCP emulada.
Las dos ramas usan exactamente las mismas llegadas y capacidades por CPE.
El servicio usa capacidad wireless del ranking, 120 us por paquete y factor de reintentos.
No se modela el cuello Ethernet aunque su velocidad se conserva como metadato.
La rama stock aproxima turnos TDMA de 2 ms y guardas de 40 us.
La rama OpenWrt combina DRR por estacion, AQL, CoDel aproximado y proteccion de voz.
No reproduce firmware airOS ni codigo interno del kernel Linux.

## Comparacion emparejada

Doce semillas 192601..192612, horizonte de 2 s desde colas vacias, 24 simulaciones.
Limites comunes: 512 paquetes software, 96 descriptores, 32 paquetes por poll de 250 us.
Se cuenta el airtime parcial al final y los paquetes sin terminar como no entregados.
Las latencias son de paquetes entregados; no representan a los perdidos.

| Metrica, media de 12 replicas | Stock abstracto | OpenWrt abstracto |
| --- | ---: | ---: |
| Goodput Mbps | 33.593 | 34.903 |
| VoIP p95 ms | 50.834 | 17.427 |
| Descartes por descriptor, % ofrecidos | 87.440 | 0 |
| No entrega total, incluidos pendientes, % | 87.634 | 85.090 |
| Jain de airtime | 0.6309 | 0.8626 |

El maximo p95 de voz OpenWrt es 17.819 ms. Cero TXbuf no significa cero perdida.
Estos numeros describen una carga muy saturada de un modelo sin calibracion de campo.
No son estimaciones de capacidad real ni evidencia causal aislada de AQL o DRR.

## Optimizacion y resultado negativo

NSGA-III: semillas 19271 y 19272, poblacion 20, 3 generaciones por ejecucion.
Se ejecutaron 120 evaluaciones, 60 configuraciones distintas de un espacio de 324.
Variables: aql_threshold, aql_txq_limit_be, aql_txq_limit_vi, quantum_us, codel_target_ms.
Quantum representa microsegundos de credito de airtime, no bytes de fq_codel Linux.
Objetivos: goodput, peor p95 de voz, no entrega total y equidad de airtime.
Entrenamiento: primeras 4 semillas. Ocho semillas reservadas para candidatos factibles.
Estas ocho ya se usaron en la comparacion base; no son validacion externa del modelo.
Restricciones por semilla: TXbuf=0, p95 voz menor a 15 ms, voz no entregada como maximo 1%.
La ultima restriccion evita aceptar latencia baja causada por censura de paquetes perdidos.

60/60 cumplen TXbuf=0 y 44/60 cumplen latencia; 0/60 cumplen no entrega de voz.
El peor p95 por candidato va de 7.125 a 23.031 ms.
La peor no entrega de voz por candidato va de 7.955% a 29.500%.
La media de no entrega total va de 83.877% a 86.036%.
Resultado: NO_VALIDATED_FEASIBLE_CANDIDATE. Frontera factible vacia.
No se ejecutaron simulaciones de candidatos sobre holdout al no existir frontera factible.
No se afirma imposibilidad global: se examinaron 60 de 324 configuraciones y un solo modelo.

## Evidencia y verificacion

[Simulacion](../artifacts/autoresearch/stage1926a_panel2_guarida_22cpe_dense_sector_simpy_receipt.json).
[Archivo NSGA-III](../artifacts/autoresearch/stage1927a_nsga3_panel2_22cpe_airtime_pareto_receipt.json).
[Memoria Stage1929A](../artifacts/autoresearch/stage1929a_wave148_memorymaster_receipt.json).
[Revision independiente acotada](../artifacts/verification/stage1931a_independent_review.json).
[Pruebas Stage1930A](../artifacts/verification/stage1930a_pytest_receipt.json).
[Gate Stage1931A](../artifacts/verification/stage1931a_wave148_astra8_gate.json).
El gate separa integridad del estudio y mitigation_target_achieved; aprobarlo no acepta QoE.
Los cinco pilares reutilizan catalogo y procedencia de investigacion historica explicitamente.
No se ejecuto un nuevo reactor ni RE binario. La memoria conserva estado epistemico nativo.
Proximo paso cientifico: calibrar servicio y carga ofrecida antes de recomendar parametros reales.
