<!-- doc-head: Wave143, multicast real y healer canónico en banco PtMP -->
Cuatro ventanas ABAB con prueba Ethernet de conversión y restauración verificada.
Instalación canónica y reasociación controlada confirmadas; sin promoción de ajustes.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage1898A — Comparativa m2u y auditoría del healer

## Alcance y resultado

CONFIRMED: ejecución exclusiva sobre AP 198.18.0.43 y STA 198.18.0.67.
Stage1896 completó A1→B1→A2→B2: m2u0 frente a m2u1, con tráfico real.
Stage1897 instaló y verificó el nombre canónico del healer con ban_time1200.
Se conservan capturas, errores iniciales, fuentes y hashes; ninguna métrica procede de simulación.
La pérdida inicial de Wave133 no se reprodujo en las condiciones actuales.
Su causa sigue UNKNOWN: este ensayo no demuestra que multicast1 causara aquel fallo.

## Instalación canónica

Antes no existía `/usr/sbin/fmx_apvlan_bridge_healer.sh`.
Se instaló conservando la lógica de sondeo periódico y rápido del healer previo.
El nombre anterior ejecuta ahora la entrada canónica mediante un wrapper de compatibilidad.
Así los llamadores cron/hotplug existentes siguen utilizando la implementación canónica.
No se agregó un hook de puente ni una segunda operación addif.
netifd sigue siendo responsable de la incorporación al puente.
La instalación usó backup, archivos temporales, rename y rollback desacoplado de 45 s.
El backup original queda en `/tmp/fmx-wave143-healer/original.sh` y en las capturas del host.
Los dos archivos de `/usr/sbin` son cambios persistentes autorizados en el overlay.
No hubo escritura directa de particiones protegidas ni recarga de red.

SHA256 canónico: `1d30465bf846d99e03859c992bdb8af982a22526478f7c3709ac47f299621fa4`.
SHA256 compatibilidad: `708d1901a35ab8e7412723f0d1f2d08396e984b936f839b388b4862171274c25`.

## Stage1896: qué se comparó realmente

El estado original era snooping0, querier0, intervalo de respuesta1000 centisegundos y m2u0.
Con esas condiciones, cambiar sólo m2u podría no ejercitar la conversión.
Ambos brazos activaron temporalmente snooping1 y querier1, con intervalo100 centisegundos.
Se esperaron 3 s tras el alta del receptor; hairpin permaneció en0.
A usó m2u0 y B usó m2u1, sin modificar RF, AQL, cobertura o firmware.
Cada ventana restauró todos esos atributos originales mediante su script de rollback.

El probe MIPS estático envió UDP real a239.255.143.1:5794, TTL1 y datagramas de1316 bytes.
El receptor se unió explícitamente desde br-wan/198.18.0.67 y validó IP_PKTINFO.
La carga concurrente incluyó TCP bidireccional, VoIP UDP de64Kbps e ICMPv6.
Las secuencias y un token propio por ventana permitieron contar entrega, pérdida y duplicados.
La pérdida se calcula sobre los paquetes realmente enviados, no sobre el objetivo del generador.

Se capturaron informes IGMP nativos y 12 tramas de salida AP_VLAN por ventana.
En A, destino Ethernet `PUBLIC_DEVICE_0074`; en B, destino `PUBLIC_DEVICE_0036`.
El destino IP permaneció multicast en ambos casos: la conversión quedó demostrada directamente.
No se obtuvo un dump MDB: el recorrido interno se infiere de esas tramas y del código fuente.
La FDB y `/proc/net/igmp` no se presentan como sustitutos de un dump MDB.

| Métrica media | A: m2u0 | B: m2u1 |
|---|---:|---:|
| Goodput agregado Mbps | 73.339 | 74.637 |
| p95 ICMP ms | 25.103 | 21.702 |
| IPTV recibido Mbps | 3.866 | 3.657 |
| IPTV pérdida % | 0.0206 | 0 |
| VoIP pérdida % | 0.100 | 0 |
| IPTV jitter ms | 1.304 | 1.339 |
| VoIP jitter ms | 2.467 | 2.966 |
| ICMP recibidos | 40/40 | 40/40 |
| Duplicados ICMP/multicast | 0/0 | 0/0 |

Goodput incluye TCP bidireccional y los flujos UDP recibidos.
El jitter multicast usa deltas de tránsito: cancela el offset constante de reloj, no corrige su deriva.
B mostró +1.77% de goodput y -13.55% de p95, con menor carga IPTV ofrecida.
El generador ofreció A1=3.912677, A2=3.821233, B1=3.632239 y B2=3.681062 Mbps.
Por tanto, no fue una carga CBR exacta de4Mbps ni una prueba causal con carga constante.
Un bloque temporal no permite inferir superioridad general: no se promueve m2u1.

## Primer intento y criterio de adquisición

El primer A1 envió7065 de7598 paquetes objetivo; recibió7065, sin pérdida ni duplicados.
El generador devolvió exit2 por déficit de emisión y el arnés detuvo el intento.
Se conservó completo como INCOMPLETE, junto con sus fuentes y restauración.
El segundo intento conserva exit2 y acepta únicamente ese déficit documentado del emisor.
Exige END, token, grupo, puerto y conteos coincidentes; los demás errores siguen rechazándose.
Se registran separadamente déficit de emisión y pérdida de red, sin cambiar el binario.

## Stage1897: reasociación y estado final

Se invocó el modo controlado `--reassociate` del script canónico con ban_time1200.
La interfaz pasó de ifindex997 a998; la STA volvió a quedar aprendida en la FDB del puerto3.
Lecturas posteriores: estado3, multicast0 y10/10 pings, sin duplicados.
Los modos de verificación canónico y compatible devolvieron el mismo estado.
Esto verifica la entrada operativa y la reasociación solicitada, no la detección automática de un bloqueo.

La comprobación final independiente confirmó AQL, RF, cobertura, firmware e IP de gestión originales.
Snooping0, querier0, intervalo1000 y multicast0 quedaron restaurados.
Se retiraron los binarios temporales de tráfico y no quedaron cargas propias activas.

## Evidencia y cinco pilares

A: procedencia binaria histórica, ELF del probe y fuentes oficiales bridge/netifd, con límites explícitos.
B: invocaciones Scholar y reactor privado real; heurísticas, cero verificaciones Jev en vivo.
C: cuatro ventanas reales y guards de45s. D: comparación descriptiva sin promoción.
E: dos claims reales, uno por etapa, con readback y scope project:futuramax.
Claims correctos:1896→157719 y1897→157720, ambos candidate.
Dos registros iniciales tuvieron las etiquetas invertidas;157717/157718 se archivaron lógicamente.
El servidor no aplicó la supersesión solicitada; se conservaron solicitudes, respuestas e historial.
El evento privado del reactor conserva su etiqueta original1897, con correspondencia explícita a tráfico1896.
La fila finita de results.tsv conserva la decisión de no promover.
Pytest y el gate verifican hashes, tramas, métricas, instalación y restauración.
Su PASS certifica la adquisición y la auditoría, no un óptimo científico ni recuperación de fallos no inducidos.

- [Recibo1896](../artifacts/autoresearch/stage1896a_live_ptmp_m2u0_vs_m2u1_paired_abab_receipt.json)
- [Recibo1897](../artifacts/autoresearch/stage1897a_live_peer_healer_bantime1200_fdb_audit_receipt.json)
- [Manifiesto nativo](../artifacts/autoresearch/wave143/runtime_manifest.json)
- [Gate1901](../artifacts/verification/stage1901a_wave143_codex1_gate.json)
