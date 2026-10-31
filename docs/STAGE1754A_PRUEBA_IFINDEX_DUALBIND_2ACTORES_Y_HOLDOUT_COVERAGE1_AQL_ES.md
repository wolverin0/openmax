<!-- doc-head: Wave119: ifindex nuevo, trazas reales de dos actores y holdout independiente -->
AP_VLAN995→996, netifd adjunta, hotplug encuentra el puerto ya adjunto.
Dos rondas nuevas con candidato fijo y restauración completa del banco WA.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Wave119: prueba física y límites de aceptación

Banco exclusivo: LAP-120 AP198.18.0.43, Loco STA198.18.0.67,
MAC PUBLIC_DEVICE_0036. Interfaces detectadas: APphy4 y STAphy6.
No se asumió phy0 ni se tocaron PowerBeam, LTU o Guarida.

## Stage1752: unregister y registro nuevo confirmados

El preflight encontró AP_VLAN `phy4-ap0.sta1`, ifindex995,
brport/state3 y multicast_to_unicast0. `99-fmx-apvlan-brbind` no existía.
El helper1200 de Wave104 y `99-fmx-4addr-verify` sí estaban instalados.
Se añadió temporalmente el hook solicitado como instrumentación explícita.
Esto no demuestra una función preexistente ni una instalación persistente.

Se verificó por SHA256 un strace mips_24kc del repositorio oficial OpenWrt,
se cargó en RAM y se trazaron exclusivamente ioctl del PID real de netifd.
El hook registró su ejecución y trazó su propia llamada brctl.
No se capturaron mensajes ubus completos ni contenido de credenciales.
Un watchdog independiente45s retiraba la instrumentación y restauraba multicast.

La operación fue `del_client` con ban_time5000 y eliminación explícita
del AP_VLAN exacto, sin bajar el AP ni recargar la red.
Se confirmó ausencia del netdev anterior y unregister nuevo en dmesg.
La reasociación creó ifindex996 y recuperó10/10 pings IPv6, pérdida0%.

| Actor | Evidencia directa | Resultado |
|---|---|---|
| netifd |SIOCBRADDIF sobre phy4-ap0.sta1, ifindex996|exit0, incorporación exitosa|
| hook temporal |SIOCBRADDIF sobre el mismo puerto unos171ms después|EBUSY, brctl exit1|
| hook temporal |escritura multicast_to_unicast y readback|exit0, state3, multicast1, master br-lan|

Los tiempos de las dos trazas usan el mismo reloj del AP; no se asumen
sincronizados con UTC del host. La pertenencia final se corroboró en sysfs.
Hay prueba de ejecución de dos actores, pero una sola incorporación exitosa.
EBUSY no es un segundo attach exitoso ni prueba de fallo de conectividad.
El criterio literal de dos attaches exitosos queda REFUTED en esta ejecución.
No se forzó una separación adicional del bridge para fabricar ese resultado.

Se retiraron el hook temporal y strace antes de iniciar el holdout;
multicast_to_unicast volvió a0, como en el baseline de descubrimiento.
El ifindex nuevo permanece996: un contador de identidad no se restaura a995.

## Stage1753: holdout independiente

Se prerregistraron dos rondas A1→B1→A2→B2 nuevas, sin reutilizar tráfico de1663.
En las dos rondas B fue exactamente coverage_class1, VI750/1500 y BE1200/2400,
aplicado a ambos radios. No se adaptó el candidato entre rondas.
Baseline observado: coverage0; VO300/600, VI1000/2000, BE1500/2500,
BK500/1000 y aql_threshold3000. Las AC están expresadas en µs de airtime.
Se usó `iw set distance450` con readback coverage1; no se midió distancia física.

Cada ventana tuvo20s de TCP bidireccional P1, IPTV UDP4Mbps/1316B,
VoIP64kbps/160B y ping IPv6 concurrente. Se conservaron JSON de ambos extremos,
stderr y códigos de cada proceso, RSSI, cadenas, bitrate, reintentos y proc/stat.
El goodput suma receptores; no se usa la suma genérica UDP de cero bytes.
No hubo strace ni sondeos SSH periódicos durante los20s de carga.

Antes de mutar se armaron guards45s independientes en ambos radios.
Restauran ajustes y limpian únicamente procesos propios por PID, starttime y
comando. Cada ventana verifica el tratamiento y su restauración; un error detiene
la campaña y conserva el intento. No se ejecutó `ubus call network reload`.

## Interpretación y cierre

| Ronda holdout | Goodput A→B Mbps | Cambio | p95 A→B ms | Cambio |
|---|---:|---:|---:|---:|
|1|74,581→64,943|−12,92%|28,843→34,263|+18,79%|
|2|75,083→52,041|−30,69%|32,184→41,491|+28,92%|

El candidato queda REJECT_HOLDOUT_REGRESSION, sin promoción.
Pings durante carga:149/160, pérdida6,875%; posteriores:24/24.
IPTV/VoIP también tuvieron pérdidas pequeñas, conservadas por ventana.
La mejora exploratoria de1663 no se reprodujo en este holdout.
Se verificaron al final coverage0, AQL original, RF y SHA256 del firmware,
IPs de administración, ausencia de cargas propias y multicast_to_unicast0.
No se escribió firmware ni ninguna partición protegida.

Se mantienen separados adquisición física, resultado del candidato y aceptación
del doble attach. Dos rondas del mismo enlace son medidas repetidas, no ocho
réplicas independientes. No se afirma significancia estadística ni óptimo global.
La promoción no es automática; los resultados y decisiones quedan en results.tsv.
El cambio de ifindex y la hora del ensayo distinguen este holdout del descubrimiento.

La evidencia binaria reutilizada es histórica y delimitada. Las fuentes oficiales
netifd/iw explican la semántica; las trazas nativas prueban lo realmente ejecutado.
Scholar se ejecutó con backend heurístico; no hubo verificación Jev en vivo.
MemoryMaster registra dos claims candidatos con lectura posterior de sus IDs.
El reactor procesa las dos rondas en una cola privada, sin alterar la compartida.

- [Recibo1752](../artifacts/autoresearch/stage1752a_live_fresh_ifindex_two_actor_dualbind_proof_receipt.json)
- [Recibo1753](../artifacts/autoresearch/stage1753a_live_ptmp_coverage1_aql_holdout_abab_receipt.json)
- [Capturas y hashes](../artifacts/autoresearch/wave119/runtime_manifest.json)
- [Gate1757](../artifacts/verification/stage1757a_wave119_codex1_gate.json)

La suite local es `tests/test_stage1752a_to_1757a_suite.py`.
Un PASS local verifica los recibos; no convierte EBUSY en una segunda inserción.
Resultado combinado con procedencia:31 tests PASS, cero fallos o skips.
Ambos gates de cinco pilares con `--require-live-hardware` terminaron exit0.
Stage1757: software PASS, adquisición COMPLETE, aceptación literal INCOMPLETE
por el segundo attach EBUSY. Los claims candidatos son157676 y157677.
