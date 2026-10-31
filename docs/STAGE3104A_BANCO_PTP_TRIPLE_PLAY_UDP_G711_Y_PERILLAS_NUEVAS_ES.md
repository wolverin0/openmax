<!-- doc-head: Wave 444 confirma Triple-Play real en PowerBeam, tres NO_GO y restauración RAM -->
26 ventanas finales válidas: 18 A/A y 8 A/B; sólo un ABAB completo.
Dos contrastes se detuvieron por latencia fuera de su banda A/A.
Sin candidato para PtP-Colo; restauración y reachability RF verificadas.
<!-- /doc-head -->

# Stage 3104A: banco PtP Triple-Play y controles runtime

## Resultado y alcance

Campaña final del 30/10 23:43 al 31/10 00:00 UTC, banco PowerBeam AP `.241` y STA `.242`.
Ambos OpenWrt 24.10.4 r28959, kernel 6.6.110, canal 40 / 5200 MHz / VHT20.
Sólo se cambiaron tres controles RAM de la STA, con watchdog; producción quedó fuera del ensayo.
La STA tenía Ethernet sin portadora y su dirección de gestión se aprendía por WDS.
SSH a la STA pasó por el AP con identidad fijada; los bytes RF cubrieron el TCP propio recibido.
No se cambiaron frecuencia, potencia, SSID, ancho, firmware, módulos kernel ni particiones.

| Control STA: A → B | A/A propias | Fases medidas | Decisión y disparador |
| --- | ---: | --- | --- |
| netdev_tstamp_prequeue: 1 → 0 | 6 | A1 B1 A2 B2 | NO_GO en B2: jitter VoIP 19,419 > 16,114 ms; TCP 5,780 < 5,938 Mbps |
| ani_enable: 1 → 0 | 6 | A1 B1 | NO_GO en B1: ping p99 135,732 > 109,240 ms |
| tcp_reordering: 3 → 6 | 6 | A1 B1 | NO_GO en B1: ping p99 101,385 > 100,536 ms |

Son salidas de la envolvente empírica de esta corrida, no demostraciones universales de daño causal.
No se realizaron A2/B2 en los dos contrastes detenidos ni se imputaron esas ventanas.
Los cuatro pares B conservaron oferta/pacing comparable según su ruido pareado A/A.
No corresponde proponer ningún cambio a PtP-Colo `.62/.54`.

## QoE medida bajo carga

A y B son medianas de las ventanas de cada condición; ANI y TCP tienen un único par.
Goodput TCP usa bytes recibidos / ventana nominal de 20 s.
El recibo también incluye el denominador conservador hasta el último fin real de transferencia.

| Control | TCP A/B Mbps | RTT p95 A/B ms | RTT p99 A/B ms | Jitter VoIP A/B ms | Pérdida VoIP A/B % |
| --- | --- | --- | --- | --- | --- |
| Timestamp | 6,488 / 6,075 | 46,397 / 41,987 | 54,586 / 70,919 | 7,650 / 13,817 | 0,800 / 0,350 |
| ANI | 6,278 / 6,160 | 27,230 / 81,345 | 58,924 / 135,732 | 10,453 / 12,209 | 0,300 / 1,100 |
| TCP reordering | 6,396 / 6,003 | 47,273 / 78,763 | 72,150 / 101,385 | 6,901 / 11,991 | 1,100 / 1,100 |

En las 26 ventanas: VoIP 25.794/26.000 ecos, IPTV 97.523/98.800 e ICMP 570/572.
DUP reportados: 0; reordenamientos recalculados: 0. TCP propio recibido: 399.802.368 bytes.
La reducción aislada de pérdida o jitter no permite GO si empeoran las otras guardas.
Las bandas son extremos de seis A/A y máximo ruido de tres pares; no intervalos inferenciales.

## Transporte y límites de interpretación

Dos descargas HTTP TCP simultáneas desde uhttpd en la STA hacia el host cableado.
Payload propio de 512 KiB con longitud y contenido verificados por el receptor.
El servidor TCP consume CPU del radio: este caudal no representa el techo RF ni una carga que pruebe saturación RF.
IPTV: UDP unicast CBR de 2 Mbps, 1316 bytes, siete paquetes MPEG-TS nulos por datagrama.
VoIP: RTPv2 PCMU, G.711 de 160 bytes, datagrama de 172 bytes cada 20 ms.
Se validan eco completo, SSRC y secuencia; se guardan timestamps, pacing, DUP y reordenamientos.
No se certifican multicast/IGMP, reproducción audiovisual, pérdida de playout ni latencia unidireccional.
Jitter significa EWMA de variaciones de RTT en orden de llegada; ICMP aporta p50/p95/p99 cargados.

No había Python, iperf3, socat ni nc UDP adecuados en los radios.
Se cargó sólo en RAM ucode socket oficial para mips_24kc, verificado por SHA del índice HTTPS e importación nativa.
Módulo de 68.132 bytes, SHA256 `126c68c5b9faccd8972ce455054b085febaffc0e939e373e2f83df104a271548`.
No hubo opkg ni nueva validación usign. Reflector finito de 24 s con contadores constantes.
El nonce de instancia nativa difiere del nonce/SSRC del generador: ambos se registran, sin afirmar identidad entre ellos.
Stage 488 fue HTTP+ICMP; Stage 1007 fue loopback: ninguno reemplazó esta captura RF.

MOS es sólo un escenario de planificación G.107/G.113, no voz escuchada.
R0=93,2, Ie=0, Bpl=4,8, BurstR=4; G.711 de 20 ms y buffer supuesto de 60 ms.
La demora de entrada usa RTT p95 + 80 ms; no se afirma demora unidireccional medida.
El MOS modelado no decide GO. Referencias: [G.107](https://www.itu.int/rec/T-REC-G.107), [G.113](https://www.itu.int/rec/T-REC-G.113).

## Selección y antecedentes

El índice congelado `artifacts/knob_index/knob_index.json` tiene las tres filas PtP con probado/efecto_medido vacíos.
Ese cero corresponde al índice de contrastes aislados; no acredita búsqueda universal ni ausencia de uso en perfiles.
ANI y timestamp tuvieron NO_GO en PtMP W434; no se trasladó su resultado a PtP.
ANI devuelve caché host, no un getter efectivo del firmware.
TCP reordering aplica porque la STA es endpoint TCP; no prueba beneficio en forwarding de un bridge de producción.
Se excluyeron cobertura, AQL, FQ/BQL, GRO y agregación con antecedentes; no se usó CT rate override.

## Watchdog y cierre verificado

Watchdog compartido de 45 s en la STA, renovado cada 10 s en una misma generación.
Cada cambio comprueba boot, propietario, token, estado y deadline bajo action lock.
Los hijos cierran el FD del lock; PID/startticks y argv delimitan los procesos propios.
El restore escribe y relee las tres preimágenes: timestamp=1, ANI=1, tcp_reordering=3.
El piloto dejó expirar el watchdog nativo y comprobó el canario restaurado.
Cuatro guards terminaron RESTORED/rc=0; cuatro workspaces y handles quedaron eliminados.
Lectura independiente final: mismos boots, FQ/AQL/BQL/interfaces/pares y tres controles iniciales.
Sin listeners TCP 55445/UDP 55444 ni procesos propios; STA Ethernet carrier=0.
Ping posterior AP→STA: 10/10, 0 DUP, 0% pérdida; MemAvailable AP 15.040 / STA 18.040 KiB.
La limpieza acredita archivos propios, no vaciado indiscriminado de /tmp.

## Fallos conservados y auditoría

El EUI-64 derivado del MAC WLAN no correspondía al bridge; timeout inicial conservado.
La primera corrida guardaba JSON durante la carga y perturbó el pacing; quedó excluida.
La siguiente se detuvo por colisión con el lock de renovación y restauró las preimágenes.
La versión final sólo reintenta rc=75 por lock ocupado antes de ejecutar el cuerpo.
No se repiten cuerpos con resultado incierto ni se cambian bandas para conseguir GO.
El primer chequeo final de ps coincidió con su propio comando; se conservó y sustituyó por ps directo.
El validador offline corrigió dos supuestos erróneos: nonce nativo distinto y transferencia final de cero bytes.
Las primeras aserciones fallidas permanecen en el recibo; no implican otra prueba RF.

Recomputación offline: 26/26 ventanas, ocho mutaciones adversarias rechazadas y nueve fuentes sin drift.
Dos revisores independientes corroboraron métricas/cierre sobre snapshots identificados por hash.
El precheck externo guardado corresponde al controller anterior; no se presenta como precheck de la revisión final.
La fuente final ejecutada y su hash están en controller_attempts; el análisis posterior se etiqueta como tal.
No se afirma significancia estadística, captura pcap ni cumplimiento del objetivo heredado BQL8192/−25%.
Recibo reproducible: `artifacts/autoresearch/wave444_ptp_triple_play.json`.
Gate: `artifacts/verification/wave444_lane1_ptp_triple_play_gate.json`.
