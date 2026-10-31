<!-- doc-head: Wave 446 rechaza 8192 por QoE y confirma la base persistente de ambos PowerBeam -->
18 ventanas finales verificadas: tres sweeps, doce A/A y tres fases A/B; ningún ABAB completo.
24192 no llegó a aplicarse: su referencia AUTO derivó antes de B.
Sin canario productivo; base BQL 32768/4542/800 persistida y reachability RF comprobada.
<!-- /doc-head -->

# Stage 3106A: BQL Ethernet PtP y Triple-Play

## Dictamen

**NO_GO para canario PtP-Colo.**
8192 obtuvo un par A1/B1, detenido por jitter fuera de su banda A/A.
El ensayo previsto de 24192 se detuvo en A1 con AUTO; B=24192 no se ejecutó.
Estos stops no prueban daño causal universal ni autorizan seleccionar otro límite productivo.
No se repitieron pruebas hasta obtener verde ni se imputaron fases faltantes.
El contraste fue RAM-only en .241/.242; después se persistió su base por directiva del operador.
Producción .62/.54, imágenes firmware y particiones protegidas intactas.

## Resultado medido

| Contraste | Cobertura | Resultado |
| --- | --- | --- |
| AUTO_MAX vs 8192 | 6 A/A + A1/B1 | NO_GO: jitter VoIP 20,619 > máximo A/A 15,570 ms; IPTV 5,563 > 4,678 ms |
| AUTO_MAX vs 24192 | 6 A/A + A1 | INCONCLUSIVE: la referencia AUTO perdió estabilidad antes de B |

| Único par 8192 | AUTO A1 | 8192 B1 | Delta |
| --- | ---: | ---: | ---: |
| TCP recibido Mbps | 5,006632 | 4,349632 | −13,12% |
| Ping RF cargado p50 ms | 16,0745 | 16,6635 | +3,66% |
| Ping RF cargado p95 ms | 79,54255 | 56,62405 | −28,81% |
| Ping RF cargado p99 ms | 107,03251 | 84,12161 | −21,41% |
| Jitter RTT VoIP ms | 11,89958 | 20,61873 | +73,27% |
| Jitter RTT IPTV ms | 3,87092 | 5,56329 | +43,72% |

BQL8192 fue leído y el delta nativo fq_overmemory fue cero en ambos nodos.
La meta numérica heredada de p95≤−25% aparece en un solo par; la QoE primaria empeoró.
No equivale a validación repetida, ABAB completo o aceptación del canario.
El límite adaptativo AP fue 8192 en seis muestras B; en A varió 9142..23756.
Inflight observado=0: el muestreo no resuelve ocupación pico ni starvation del driver.

Para el segundo contraste, la mediana A/A TCP era 3,610 Mbps.
A1 AUTO cayó a 0,793 Mbps: VoIP 19%, IPTV 46,579% y p99 191,159 ms, fuera de su banda.
No se atribuye ese deterioro a 24192, que todavía no estaba aplicado.

Las 18 ventanas finales incluyen 3 sweeps, 12 A/A y 3 fases A/B.
TCP recibido: 191.438.120 B; VoIP 17.315/18.000; IPTV 61.763/68.400; ICMP 351/360.
DUP reportados=0; reordenamiento recalculado=0. Piloto válido aparte; un piloto incompleto se conserva.

## Recorrido físico y parámetros

PowerBeam .241 AP y .242 STA: OpenWrt 24.10.4 / kernel 6.6.110, VHT20 / 5200 MHz.
STA carrier Ethernet=0; AP ag71xx-legacy a 1000 Mbps, con identidades SSH fijadas.
Fuente TCP nativa STA→RF→bridge AP→eth0 TX→host cableado.
Los deltas AP Ethernet TX y STA RF TX cubrieron los bytes recibidos; Ethernet STA permaneció en cero.
Así se ejercita **BQL TX del AP**, sin acreditar BQL Ethernet de la STA.
Es una variación explícita del recorrido de bajada planteado en W438.

Sólo se comparó limit_max del AP:
A=AUTO_MAX 1879048192 B frente a B=8192; 24192 quedó pendiente.
En todos los brazos se mantuvieron min=4542 B y hold=400 ms.
AUTO_MAX libera el techo DQL; no significa kernel stock ni reserva de 1,8 GB.
El límite adaptativo conserva historia y cambia con completions; no se reseteó artificialmente.
Preimagen de ambos nodos: **limit_max=32768, limit_min=4542, hold=800 ms**.
FQ/AQL, demás sysctl, radio, módulos kernel y firmware no se ajustaron.

## RTT y capacidad: qué se pudo identificar

Ping link-local sin carga TCP/UDP del ensayo: 20/20 respuestas por sentido.
AP→STA min/p50=1,382/1,6195 ms; STA→AP=1,447/1,466 ms.
No se usó propagación geométrica como RTT.

El barrido 1/2/4 flujos con Triple-Play entregó 4,172680 / 5,180664 / 4,318096 Mbps.
Eran sweeps con BQL original 32768/4542/800; no se mezclaron con el A/A AUTO/400.
CPU agregada STA entre primera/última muestra: aproximadamente 58,87/63,88/63,46%.
El reflector ucode consumió aproximadamente un tercio; hubo backlog y TX STA de 19,5 Mbps.
No apareció un plateau estable que permita separar capacidad RF de límites del endpoint/protocolo.

**RF_bottleneck_capacity_mbps y true_RF_BDP_bytes permanecen null.**
5,180664 Mbps × RTT peer 1,466 ms / 8 da 949,357 B como proxy de caudal TCP logrado × RTT.
No es el BDP RF verdadero ni deriva un BQL óptimo.
Los 450 m pertenecen a PtP-Colo; la distancia física del banco no se midió.
No se transfieren estas tasas a Colo en 5765 MHz.

## Transporte y observador

TCP dd/nc cliente, sin iperf3 ni Python en radios; el host verifica payload cero.
Sólo cuenta lecturas completadas dentro de la ventana, con drenaje previo continuo.
Excluidos 34.905.076 B de calentamiento/frontera inicial y 52.560 B de frontera final.
Son timestamps de lectura de aplicación, no de llegada al cable.
El receptor cierra al terminar la ventana; luego se terminan las fuentes propias antes de esperar al reflector.

IPTV: UDP unicast CBR, 1316 B MPEG-TS nulo, 2 Mbps.
VoIP: RTPv2 PCMU, 160 B G.711 cada 20 ms; eco exacto con SSRC/secuencia.
20 s nominales: 1000 datagramas de voz y 3800 de IPTV, con oferta/pacing guardados.
No se certifican multicast, audio reproducido ni pérdida/demora unidireccional.
Jitter es EWMA de variaciones RTT; MOS es un proxy explícito, no voz escuchada.
Reflector ucode/socket privado y finito de 24 s, con módulo oficial cualificado en W444.
El reflector no se instaló persistentemente; no se afirma nueva validación de firma usign.

## Seguridad, fallos y cierre

Watchdog compartido 45 s en ambos nodos; renovación de la misma generación.
Boot/propietario/token/deadline/memoria legible se comprueban antes de cada escritura.
Procesos propios identificados por PID/startticks y argv privado; sin señales por nombre genérico.
El cierre intenta ambos nodos aunque falle uno; la ambigüedad impide aceptar restore.

Dos fallos de lector se conservaron: NET coincidía con SOFTNET y AQM truncó su último número bajo carga.
Los guards del intento con tráfico restauraron ambos equipos y eliminaron lo propio.
La corrección usa secciones delimitadas, hasta tres lecturas y rechazo de números sin newline.
Ocho snapshots AQM siguieron parciales: campos UNKNOWN, sin rellenar desde el baseline.
El parser de secciones vacías puede incluir marcadores posteriores en own_process_cpu_raw.
No se usa ese campo como prueba de ausencia; la inspección final ejecutó ps y lectura de sockets por separado.

Seis guards terminaron RESTORED/rc=0, seis limpiezas verificadas; sin errores de renovación/cierre.
El contraste tuvo 39 escrituras sysfs BQL verificadas, incluyendo restores de valores iguales; cero cambios RF.
Lectura independiente final: BQL 32768/4542/800 en ambos, mismo boot/peers, FQ/AQL completos coincidentes.
Sin procesos, archivos, handles ni listener UDP propios.
Ping RF final: **10/10, 0 DUP, 0% pérdida**; MemAvailable AP 16.120 / STA 17.524 KiB.
Se restauró configuración, no contadores ni estado adaptativo interno.

## Base persistente del banco

Tras cerrar la medición llegó la directiva de conservar IPs, roles y base instalada del banco.
Se verificaron archivos network/wireless sin cambios y base BQL 32768/4542/800, sin adoptar candidatos.
En cada nodo se corrigieron dos hooks BQL y se retiró de rc.local el fallback antiguo que cambiaba RF.
Se detuvo su proceso STA identificado y su hijo; los scripts completos de arranque no se ejecutaron.
Tres archivos por nodo quedaron respaldados con SHA en `/etc/fmx_rollback/w446_c5f7c448607549c18249fa95c673f520/`.
Dos guards 45 s fueron cancelados sólo tras verificar ambos nodos; luego se liberaron y eliminaron.
Una colisión action-lock rc=75 fue preservada y reintentada antes de cualquier escritura de ese intento.
El commit agregó seis escrituras sysfs BQL: total 45, más seis actualizaciones de archivos persistentes.
Hubo escrituras de configuración en overlay JFFS2: en este layout mtd5 es rootfs_data y ART es mtd7.
No hubo acceso de escritura raw MTD, flash de firmware ni cambios en ART/bootloader.
Readback posterior: hashes nuevos y backups correctos; red/wireless sin cambios, fallback y temporales propios ausentes.
Ping RF posterior 10/10, cero DUP/pérdida; MemAvailable AP 14.180 / STA 17.608 KiB.
Persistencia configurada y leída; no se probó reboot, pérdida de energía ni ejecución del rollback de archivos.
No se certificó una nueva instalación del bridge UISP.

## Auditoría y decisión

Recomputación offline 18/18 ventanas y diez alteraciones adversarias rechazadas.
Dos revisores independientes corroboraron datos y cierre en snapshots fijados por SHA.
No hubo pytest nuevo: validaciones ejecutables y pruebas de alteración están embebidas dentro del alcance autorizado.
Una banda de seis A/A no es un intervalo de confianza causal; el drift observado limita la inferencia.
No hay límite recomendado ni canario autorizado para AP/STA de Colo.
Para reconsiderarlo: arnés/baseline estable, cuello identificado y contraste aislado completo con QoE no inferior.

[Recibo, fuentes, muestras y validador](../artifacts/autoresearch/wave446_ptp_bql_bench.json).
[Gate](../artifacts/verification/wave446_lane1_ptp_bql_bench_gate.json).
DQL upstream: [definición](https://raw.githubusercontent.com/torvalds/linux/v6.6/include/linux/dynamic_queue_limits.h),
[completions](https://raw.githubusercontent.com/torvalds/linux/v6.6/lib/dynamic_queue_limits.c).
