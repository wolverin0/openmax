<!-- doc-head: Wave138, seis CPEs simultaneos, airtime por estacion y VoIP sub10ms en modelo -->
SimPy y NSGA-III offline con carga y capacidad congeladas respecto de Wave134.
Cero TXbuf no implica cero perdida de aplicacion; la sobrecarga total permanece.
<!-- /doc-head -->

# Stage1868A: expansion a seis CPEs y frontera de voz sub10ms

## Alcance y evidencia

CONFIRMED: ejecucion local de SimPy/pymoo y lectura de recibos previos ligados por hashes.
INFERRED: respuesta del nuevo planificador. Atribucion: external controller.
UNKNOWN: efecto de una migracion real, identidades/rates de los tres pendientes y equivalencia con firmware.
No se abrieron conexiones SSH ni se escribieron radios; tampoco se ejecuto run-use.
La identidad Panel3-Guarida .83, LiteAP AC airOS8.7.25, procede del alcance previo del operador.
Los activos conocidos son `cpe_9`, `cpe_235` y `cpe_238`.
Los tres pendientes se representan como `cpe_hypothetical_1`, `cpe_hypothetical_2` y `cpe_hypothetical_3`.
Estos identificadores no inventan identidad ni confirman que se hayan asociado en produccion.

## Referencia congelada de Wave134

Se conservan 144Mbps de servicio nominal, overhead120us por paquete y96 descriptores.
La cola software permanece limitada a128 paquetes; el presupuesto de extraccion es32 por poll de250us.
Los valores proceden del ajuste descriptivo previo; no son capacidades medidas del AP.
La comparacion usa las mismas doce semillas184201–184212 y ventanas de2s con seis emisores activos.
Cada ventana empieza vacia y termina en [0,T), sin warm-up ni afirmacion de regimen estacionario.
Los recibos stock y OpenWrt previo se reproducen exactamente en metricas y contabilidad.
En el OpenWrt previo el peor p95 VoIP era17,981ms y la no entrega total media32,429 %.

## Trafico y emparejamiento

Por cada CPE: VoIP160B cada20ms, IPTV1316B a4Mbps tras replicacion multicast-to-unicast.
Bulk: rafagas de12–45 paquetes de1500B, separacion interna12us e intervalo exponencial medio35ms.
El Bulk es una carga exogena en lazo abierto; no implementa ACK, cwnd ni retroalimentacion TCP.
No se redujo la carga ni se aumento la capacidad para obtener menor latencia.
El generador nuevo copia los mismos flujos aleatorios y conserva el orden temporal estable.
Se verifican los ofrecidos por clase en cada par y se calcula SHA256 de la traza nueva.
En la referencia antigua se etiqueta como traza copiada, no como instrumentacion independiente de sus llegadas.

## Planificador propuesto y limites

El modelo nuevo usa deficit round robin de airtime por estacion y prioridad VO→VI→BE dentro de cada estacion.
`quantum` se expresa en microsegundos de airtime estimado, incluido overhead.
No equivale al quantum en bytes de un qdisc; los valores no son comandos de despliegue.
Solo se renueva credito si el saldo no cubre el paquete siguiente; AQL bloqueado no acumula credito por poll.
Una estacion que queda sin paquetes pierde inmediatamente el credito, incluso entre visitas.
El servicio del medio y la cola de descriptores siguen siendo no preemptivos.
Si la cola global esta llena, una llegada de voz puede expulsar la cola del flujo Bulk mas largo.
La expulsion queda contada como overflow Bulk y tambien como evento diagnostico, sin doble conteo de perdidas.
Si la expulsion vacia el flujo, se limpia su episodio de congestion CoDel.
La mejora combina reparto de airtime, prioridad, proteccion de voz y limites AQL; no aísla causalmente fairness.

La referencia suave usa aql_threshold18000us, BE1200us, VI600us, quantum600us y target5ms.
AQL bloquea la admision cuando se agota airtime pendiente global o por par/AC.
VO usa VI como aproximacion; un paquete puede exceder el limite individual si ese AC estaba vacio.
El control inspirado en CoDel usa target variable e intervalo100ms, con un descarte por intervalo y flujo.
La voz esta exenta del descarte CoDel deliberado; no se emula la ley completa de CoDel de Linux.
Esta combinacion no constituye una implementacion o verificacion de ath10k-ct/mac80211 de produccion.

## Comparacion en las doce semillas

| Escenario con seis activos | Goodput medio Mbps | Peor p95 VoIP ms | No entrega total media | TXbuf/ofrecidos medio |
|---|---:|---:|---:|---:|
| Stock airOS aproximado |54,962|18,778|32,409 %|31,879 %|
| OpenWrt previo Wave134 |55,285|17,981|32,429 %|0 %|
| Nuevo reparto y voz protegida |55,152|9,297|32,327 %|0 %|

Jain airtime medio del nuevo escenario:0,9933, con minimo0,9837 entre semillas.
Su maxima no entrega de voz es0,833 %; el p95 no oculta un descarte masivo de llamadas.
No entrega total significa descartes explicitos mas pendientes al cierre, sobre ofrecidos.
Los recibos separan TXbuf, overflow, CoDel, entregados y pendientes, globalmente y por clase.
El airtime incluye la parte de una transmision que sigue en curso al finalizar la ventana.
Los percentiles se calculan sobre entregados y conservan sesgo de censura por terminacion.
La persistencia de la sobrecarga Bulk/IPTV impide llamar a este resultado cero perdida de servicio.

## NSGA-III de cinco variables

Espacio discreto: aql_threshold3000/6000/12000/18000us; BE300/600/1200us; VI300/600/1200us;
quantum300/600/1200us; target1/3/5ms. Total324 configuraciones posibles.
NSGA-III usa dos semillas de algoritmo, poblacion20 y tres generaciones:120 evaluaciones.
Se evaluaron72 configuraciones distintas; una cache evita repetir simulaciones identicas.
Objetivos: maximizar goodput medio, minimizar peor p95 VoIP, no entrega total y1−Jain airtime medio.
Restricciones por semilla: cero TXbuf, p95 VoIP≤9,999999ms y no entrega de voz≤1 %.
El guard de voz exige muestras ofrecidas/entregadas y evita aprobar una latencia baja por descarte masivo.
Cuatro semillas entrenan; ocho disjuntas de la busqueda validan el frente una vez fijado.
Las semillas reservadas ya aparecieron en la comparacion de referencia; no son evidencia externa al modelo.
El frente de entrenamiento contiene50 configuraciones no dominadas y las50 pasan la validacion reservada.

| Metricas de los puntos validados | Intervalo o extremo |
|---|---:|
| Goodput medio sobre ocho semillas |55,063–55,139Mbps|
| Promedio de p95 VoIP por semilla |2,187–9,159ms|
| Peor p95 VoIP de todas las validaciones |9,421ms|
| No entrega total media |32,364–32,438 %|
| Jain airtime medio |0,9905–0,9939|

Los extremos pertenecen a puntos diferentes; no describen una configuracion ideal unica.
No se elige campeon ni se certifica optimalidad global sobre toda la grilla.
Las50 configuraciones son candidatos de modelo, no una garantia de sub10ms en RF real.

## Verificacion y continuidad

La suite1870A comprueba conservacion, carga congelada, limites, credito DRR y rechazo de recibos adulterados.
Se cubre el reinicio de credito antes de la siguiente visita y la ausencia de pines obligatorios.
La revision independiente inicial FAIL y los productores/recibos anteriores se conservan en wave138_attempt1.
La ejecucion previa del optimizador termino antes de la solicitud de parada; se preserva como no aceptada.
Tras corregir los hallazgos se repitieron ambos productores y la revision de sus hashes finales.
El gate1871A verifica ingesta/readback real de MemoryMaster y ejecuta la suite sobre esas fuentes.
Los cinco pilares son estructurales: A/B reutilizan procedencia historica, C delimita offline, D simula/optimiza y E ingesta.
No hubo nuevo RE, consulta Scholar/Jev, promocion, despliegue ni aceptacion fisica.

## Software y referencias locales

- Recibo y productor Stage1842A: evidencia congelada y escenario de seis CPEs reproducido.
- Recibo Stage1770A: tres activos, tres pendientes y observacion historica del AP.
- Catalogo firmware_knob_candidates y procedencia Wave104: reutilizacion local explicita.
- SimPy4.1.2, pymoo0.6.2, NumPy1.26.4, ejecutados localmente.
- Skills SimPy/pymoo de K-Dense, Scientific Agent Skills, DOI10.48550/arXiv.2609.00065.
La ultima referencia procede de metadatos incluidos y no se consulto externamente en esta tarea offline.
