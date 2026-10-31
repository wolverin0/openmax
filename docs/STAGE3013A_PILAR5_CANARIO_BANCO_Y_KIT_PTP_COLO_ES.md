<!-- doc-head: Wave355 P2, validaciÃ³n RAM de rescate NSS y kit de canario PtP-Colo -->
Separa la conmutaciÃ³n medida en PowerBeam del beneficio RF todavÃ­a no demostrado.
ProducciÃ³n intacta; el canario de PtP-Colo exige autorizaciÃ³n y pre-image verificable.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage3013A: Pilar5, banco y preparaciÃ³n del canario

Estado: banco completado; restauraciÃ³n nativa y limpieza verificadas. ProducciÃ³n intacta.

## Alcance y evidencia

- Banco: PowerBeam AP `198.18.0.45` y STA `198.18.0.46`.
- OpenWrt24.10.4, kernel6.6.110, 5200MHz/VHT20.
- Interfaces descubiertas: `phy9-ap0`/`phy9-ap0.sta1` y `phy8-sta0`.
- Control de NSS aplicado solo al transmisor AP; STA genera las descargas TCP.
- Sin cambios en frecuencia, potencia, firmware, particiones ni configuraciÃ³n persistente.
- Recibo principal: `artifacts/autoresearch/wave355_pillar5_bench.json`.
- RepeticiÃ³n RTT: `tools/ground_up/pillar5/wave355_rtt_retest.json`.
- Observador read-only: `tools/ground_up/pillar5/wave355_observation.jsonl`.

## Correcciones del daemon

`tools/ground_up/pillar5/fmx_chain_rescue.sh` reemplaza el comportamiento del
template antiguo dentro de este kit, sin editar el template compartido.
Lee las dos cadenas entre corchetes, excluyendo la seÃ±al agregada.
Usa deltas de bytes, paquetes, reintentos y fallos; reinicia la racha ante reset.
El disparo requiere tamaÃ±o promedio mayor que500B y reintentos/fallos positivos
durante dos muestras, ademÃ¡s del umbral de desbalance.
El retorno requiere tres muestras consecutivas por debajo del umbral de recuperaciÃ³n.

Los contadores de estaciÃ³n son agregados: no identifican quÃ© paquete concreto
mayor que500B sufriÃ³ la pÃ©rdida. Esa atribuciÃ³n por paquete queda UNKNOWN.
Solo hay eventos en `logger` y un estado JSON sustituido atÃ³micamente.
El directorio de estado debe permanecer por debajo de32KiB.
El archivo temporal de carga HTTP es separado, finito y no constituye un log.

## Seguridad y restauraciÃ³n

- Watchdog compartido: lease120s, renovaciÃ³n cada30s, dentro del rango aceptado1..600s.
- Cada cambio de mÃ¡scara comprueba lock, token, boot, deadline y piso de memoria.
- Pre-image VHT nativo: `03ff 03ff 0000 0000 0000 0000 0000 0000`.
- Rescate nativo: `03ff 0000 0000 0000 0000 0000 0000 0000`.
- El getter de antenas conserva TX/RX configurados con mÃ¡scara3.
- No se modifican los overrides ath10k existentes; se verifican al finalizar.
- El guard termina Ãºnicamente procesos propios con PID y startticks coincidentes.
- La limpieza exige restauraciÃ³n y ausencia de procesos antes de borrar lo propio.

Una mÃ¡scara RX3 confirma configuraciÃ³n de ambas cadenas, no prueba por sÃ­ sola
que el combinador fÃ­sico MRC entregue una ganancia concreta.
Tampoco NSS1 demuestra automÃ¡ticamente CDD o STBC: esas propiedades quedan UNKNOWN.

## Prueba de conmutaciÃ³n

No se usÃ³ atenuador fÃ­sico. En RAM se redujo el umbral de disparo y despuÃ©s
se elevÃ³ el umbral de recuperaciÃ³n, manteniendo los contadores reales.
El mismo daemon recorriÃ³ NSS2â†’NSS1â†’NSS2; se observaron ambas tasas NSS en trÃ¡fico.
DespuÃ©s se repusieron los umbrales normales6dB/3dB.
Es una inyecciÃ³n de umbrales; no simula una obstrucciÃ³n fÃ­sica demostrada.

## TCP y RTT medidos

Estos radios no tienen iperf3. La STA descargÃ³ archivos completos de2MiB desde
un uhttpd temporal del AP. El goodput incluye HTTP y establecimiento TCP.
No equivale a capacidad RF mÃ¡xima ni a un benchmark con endpoints externos.

Las primeras tres ventanas rechazaron `ping -i0.2`; sus RTT son invÃ¡lidos y
se conservan en el recibo. Una Ãºnica repeticiÃ³n acotada usÃ³ `ping -i1`.

| Ventana vÃ¡lida | TCP Mbps | RTTp50 ms | RTTp95 ms | RTTp99 ms | Ping |
|---|---:|---:|---:|---:|---:|
| Baseline |16.570|6.681|10.528|22.031|20/20|
| Disparo de rescate |16.805|7.952|17.260|20.093|20/20|
| Retorno por histÃ©resis |17.033|6.834|18.853|20.932|20/20|

Los valores incluyen el tiempo de transiciÃ³n dentro de cada ventana.
Tres ventanas de20 respuestas no bastan para establecer una mejora causal.
El objetivo de reducir RTTp95 en25% no se demuestra en esta ejecuciÃ³n.

## AceptaciÃ³n y lÃ­mites

El daemon fue observado durante1804.0s con watchdog activo.
MemAvailable mÃ­nimo: AP12688KiB y STA19344KiB.
El checkpoint nativo midiÃ³16KiB de directorio de estado y266B de JSON.
El observador independiente completÃ³61 muestras por nodo durante1800s.
Se restauraron las mÃ¡scaras originales, se conservaron los overrides y se
verificÃ³ ausencia de procesos, watchdog, servidor HTTP y archivos propios.
Pruebas locales: 19 del daemon y32 del kit, sin fallos en los XML finales.
Los intentos previos fallidos de fixtures permanecen archivados.
Kit: tools/ground_up/pillar5/CANARY_USAGE.md y canary_manifest.json.
PreparaciÃ³n offline: python tools/ground_up/pillar5/build_canary_kit.py
con --preimage, --run y --out; el kit exige permiso externo y no lo genera.
Gate: artifacts/verification/wave355_lane1_pillar5_bench_gate.json.
El contrato heredado de BQL8192 no se aplica: se conservÃ³32768.
No se autoriza despliegue automÃ¡tico en PtP-Colo.
La promociÃ³n requiere un canario autorizado con medidas bajo desbalance real,
transmisiÃ³n inversa, rollback y confirmaciÃ³n del desempeÃ±o de ambos extremos.
