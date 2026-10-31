<!-- doc-head: Wave134, agotamiento TX de Panel3 y mitigacion de colas simulada -->
SimPy y NSGA-III offline; cero descartes de descriptor no significa cero perdida de aplicacion.
Tres CPEs activos y tres pendientes; ajuste descriptivo sin identificacion fisica del sistema.
<!-- /doc-head -->

# Stage1844A: colas TX, AQL y frontera de mitigacion

## Evidencia y alcance

CONFIRMED: lectura local del recibo1770A y ejecucion reproducible de los dos productores.
INFERRED: respuesta del modelo. Atribucion de resultados: external controller.
UNKNOWN: capacidad real de buffers, causa del agotamiento, mejora en campo y equivalencia del firmware.
No hubo SSH, configuracion, despliegue ni escrituras a radios.
Panel3-Guarida .83, LiteAP AC con airOS8.7.25, es la identidad estipulada por el operador.
El modelo no vuelve a verificar esa identidad en hardware.
Stage1770A registra `cpe_9`, `cpe_235` y `cpe_238` asociados y tres pendientes sin identidad.
Los tres pendientes no generan carga en el escenario principal.

## Observacion original y denominador

En 11,07 s: 77.314 paquetes enviados y 2.975 eventos de falta de buffer TX.
El cociente 2975/77314 es 3,848 %; no es una probabilidad conocida de perdida sobre paquetes ofrecidos.
El contador xmit_filtered tambien aumenta 2.975: no se suma como una segunda perdida independiente.
Una ventana de contadores no identifica una causa ni determina tamanos de cola o distribuciones de rafagas.
El recibo original y las fuentes locales quedan ligados por SHA256.

## Modelo SimPy y trafico

Se ejecuta un medio compartido no preemptivo, descriptores finitos y colas de software por flujo.
La seleccion de software prioriza voz, video y Bulk, con round robin entre pares de la misma clase.
La cola de descriptores es FIFO; no reproduce las colas internas del firmware ni airMAX TDMA.
VoIP: 160 B cada 20 ms por CPE. IPTV: 1316 B, 4 Mbps por CPE tras replicacion multicast-to-unicast.
Bulk: rafagas de 12–45 paquetes de 1500 B, con separacion interna de 12 us.
El intervalo entre rafagas es exponencial de media35ms, con una secuencia independiente por CPE.
Es un sustituto de carga TCP en lazo abierto; no emula ACK, cwnd ni control de congestion.
Ambos sistemas reciben exactamente las mismas llegadas por semilla.
Cada ventana dura 2 s, comienza vacia y observa [0,T); no es regimen estacionario.
Se limita tiempo, cantidad de paquetes y eventos; una violacion aborta el calculo.

## Aproximacion OpenWrt ath10k-ct/mac80211

`tx_queue_len` limita la cola de software global. El overflow se cuenta por separado.
`dev_weight` representa un presupuesto de extraccion por poll de250us; no se afirma que sea un knob TX real.
AQL carga airtime estimado hasta completar el descriptor y bloquea nuevas admisiones al alcanzar limites.
El umbral global se explora en6000/12000/18000us; la referencia suave usa18000us.
Los limites por par son BE1200/2400/4800us y VI750/1500/3000us; VO usa VI como aproximacion.
Un flujo vacio puede admitir un paquete mayor a su limite de AC; no se emula exactamente el driver.
El modelo inspirado en FQ-CoDel usa objetivo5ms e intervalo100ms, sin descartar voz deliberadamente.
Descarta como maximo un paquete por intervalo y flujo; no implementa la ley completa de CoDel de Linux.
Su persistencia se limpia al vaciarse la cola o caer bajo el objetivo.
La revision independiente detecto ese reinicio faltante; se corrigio y quedo una regresion determinista.

## Ajuste descriptivo y doce semillas

Antes de la comparacion se fija una grilla de16 combinaciones: servicio24/72/96/144Mbps y32/64/96/128 descriptores.
La semilla184200 minimiza el error absoluto entre el cociente observado y TXbuf/entregados del modelo stock.
Seleccion:144Mbps y96 descriptores, mas120us de overhead por paquete; cociente ajustado4,245 %.
Los denominadores no son equivalentes: este ajuste es descriptivo, no una calibracion fisica.
La parametrizacion inicial24Mbps/32 descriptores se conserva en la sensibilidad, sin presentarla como evidencia del AP.
Las semillas184201–184212 quedan fuera del ajuste y ejecutan stock/OpenWrt emparejados.
La media stock TXbuf/entregados de esas doce semillas es3,049 %, distinta de la observacion3,848 %.
No se ajusta nuevamente para ocultar esa diferencia; el sistema sigue sin estar identificado.

## Comparacion del modelo

| Escenario | Goodput medio Mbps | Peor p95 VoIP por semilla ms | No entrega total media | TXbuf/entregados medio |
|---|---:|---:|---:|---:|
| 3 activos, stock |40,631|16,730|3,318 %|3,049 %|
| 3 activos, OpenWrt suave |41,630|8,254|1,128 %|0 %|
| 6 activos hipoteticos, stock |54,962|18,778|32,409 %|47,259 %|
| 6 activos hipoteticos, OpenWrt suave |55,285|17,981|32,429 %|0 %|

No entrega = descartes explicitos mas paquetes pendientes al cierre, sobre paquetes ofrecidos.
El recibo separa TXbuf, overflow, CoDel, entregados y pendientes para cada clase.
Los pendientes no se cuentan como exitos y no se confunden con descartes ya observados.
Los p95 se calculan sobre entregados; los percentiles mantienen sesgo de censura por terminacion.
El airtime incluye la fraccion de una transmision en curso al cerrar la ventana.
El escenario de seis activos usa tres identidades hipoteticas, no nombres de CPEs pendientes reales.
Su degradacion impide extrapolar la validacion de tres activos a una futura carga de seis.

## NSGA-III y frontera

Espacio discreto: tx_queue_len64/128/256, dev_weight16/32/64, y los tres limites AQL indicados.
Total243 configuraciones posibles. Dos semillas del algoritmo, poblacion20 y tres generaciones.
Se ejecutaron120 evaluaciones del algoritmo y67 configuraciones distintas, con cache de duplicados.
Cuatro semillas simulan entrenamiento; ocho semillas disjuntas validan el frente fijado sin volver a optimizar.
Objetivos: maximizar goodput medio, minimizar peor p95 VoIP, no entrega total media y capacidad de cola configurada.
Restricciones por semilla: cero TXbuf, VoIP p95<10ms y, para evitar ocultar voz descartada, no entrega VoIP≤1 %.
La desigualdad numerica usa9,999999ms. La condicion de voz exige muestras ofrecidas y entregadas.
El archivo completo produce50 configuraciones no dominadas factibles en entrenamiento.
Solo22 cumplen tambien las ocho semillas reservadas; las otras28 permanecen registradas como no validadas.
Esas22 dan goodput medio41,543–41,843Mbps y no entrega total media0,911–1,549 % en validacion.
El peor p95 VoIP validado es8,286ms. Cada punto tiene compromisos distintos; no se selecciona un campeon.
La frontera es finita y condicional al modelo; ni la grilla completa ni la optimalidad global fueron certificadas.

## Verificacion y continuidad

Stage1846A prueba conservacion, limites, semillas, reinicio CoDel y rechazo de evidencia adulterada.
Stage1847A liga entradas, productores, revision y suite por hashes y exige ingestion/readback de MemoryMaster.
La revision inicial FAIL y los recibos previos permanecen en `artifacts/verification/wave134_attempt1`.
La revision independiente final es de codigo y evidencia local, sin aceptacion de hardware.
Cinco pilares: A/B reutilizan catalogo y procedencia historica; no hubo nuevos analisis binarios ni consultas Scholar.
C conserva el limite offline; D ejecuta SimPy/pymoo; E registra ingesta real en `project:futuramax`.
Un pase estructural del verificador no equivale a investigacion nueva de cada pilar.
El resultado permite comparar colas bajo supuestos; no autoriza migrar Panel3 ni afirma eliminar toda perdida.

## Software y referencias locales

- `stage1770a_guarida_panel1_and_panel3_delta_audit_receipt.json`: ventana y membresia observadas.
- `firmware_knob_candidates.json` y `wave104/research/provenance_final.json`: procedencia local reutilizada.
- SimPy4.1.2, pymoo0.6.2 y NumPy1.26.4, ejecutados localmente.
- Skills SimPy/pymoo de K-Dense: Scientific Agent Skills, DOI10.48550/arXiv.2609.00065.
La ultima referencia procede de metadatos incluidos; no se consulto externamente en esta tarea offline.
