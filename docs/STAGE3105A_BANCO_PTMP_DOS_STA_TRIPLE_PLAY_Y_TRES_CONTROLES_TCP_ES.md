<!-- doc-head: W445 PtMP real de dos estaciones, A/A propia, tres controles TCP y limites de memoria UISP -->
Evidencia fisica del banco; restauracion numerica y UISP verificados; sin promocion ni cambios de produccion.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Banco PtMP: dos estaciones y tres controles TCP

Actualizado UTC del PC: 2026-10-31T03:28:53.762719+00:00. Campana final iniciada: 2026-10-31T03:18:28.034631+00:00.
AP LAP-120, CPE Loco y segundo CPE LiteBeam, en VHT20. Loco usa gestion fija `.117`; `.250` es solo el identificador historico del contrato.
La base persistente conserva roles, direcciones y rutas. Durante las ventanas definitivas no hubo reinicio, recarga Wi-Fi, retune ni acceso a produccion.
Preparacion: LiteBeam `.116` paso de AP sin peers a STA del LAP mediante configuracion persistente con commit-confirm. Ethernet siguio separado de su interfaz RF; la gestion cableada no se uso para el trafico medido.

## Metodo y limites

Seis ventanas A/A nuevas de 20 s y tres bloques A1/B1/A2/B2 de 20 s por ventana: 18 ventanas finales reales, dos estaciones simultaneas.
Origen: PC, autorizado por `<orca-id>`; no se uso el servidor `.186`.
Por estacion: dos clientes HTTP TCP hacia un servidor ucode nativo en el CPE, VoIP G.711/PCMU de 172 B a 50 paquetes/s e IPTV de 1316 B a 2 Mbps, con eco UDP real. ICMP cargado desde el AP.
HTTP sirve 512 KiB por transferencia con accept secuencial. Esta implementacion y sus buffers de 32 KiB permanecieron iguales en A/A y A/B; pueden limitar el rendimiento absoluto.
El trafico TCP medido va CPE→PC; la carga UDP y su eco atraviesan RF. Se exigieron deltas TX del CPE y RX del peer AP suficientes para los bytes propios, y Ethernet TX inferior al TCP para descartar un bypass cableado.
Windows rechazo IPV6_TCLASS: DSCP no configurado, sin afirmacion de clasificacion EF/WMM. El jitter es variacion de RTT del eco; MOS es solo un modelo, sin aceptacion de audio o video.
Controles del emisor Linux, no firmware: tcp_min_tso_segs 2→1; tcp_tso_rtt_log 9→0; tcp_min_rtt_wlen 300→0. El valor se aplico a ambos CPEs y se restauro despues de cada B.
El readback prueba el valor Linux aceptado, sin demostrar por si solo segmentacion TSO efectiva, ejecucion de una rama concreta del kernel o mejoras en el forwarding del AP.
La busqueda local encontro cero usos previos para estos tres nombres; no demuestra novedad universal. Referencia primaria: [Linux 6.6 ip-sysctl](https://raw.githubusercontent.com/torvalds/linux/v6.6/Documentation/networking/ip-sysctl.rst).
Bandas A/A min/max descriptivas del mismo banco y carga, sin intervalos de confianza ni tasa de falsos positivos certificada. Una sola repeticion ABAB por control no habilita promocion.
Los tiempos UTC y perf_counter son del PC. No se presupone sincronizacion entre reloj del radio, PC y UISP.

## Banda A/A propia

| Estacion | TCP Mbps min/max | p95 ICMP ms min/max | VoIP perdida % min/max | IPTV perdida % min/max |
|---|---:|---:|---:|---:|
| loco | 7.091 / 13.605 | 44.052 / 81.129 | 0.000 / 0.200 | 0.000 / 1.289 |
| lbe | 11.770 / 15.624 | 37.066 / 60.402 | 0.000 / 0.100 | 0.000 / 0.211 |

## Contrastes retenidos

TCP es la media de las dos ventanas de cada brazo. La columna RTT es la media de los p95 por ventana, no un p95 agrupado.
| Control | Estacion | TCP A Mbps | TCP B Mbps | Delta TCP | p95 ICMP A/B ms | Dictamen del bloque |
|---|---|---:|---:|---:|---:|---|
| `tcp_min_tso_segs` | loco | 14.903 | 12.806 | -14.07% | 47.279 / 61.280 | NO_GO |
| `tcp_min_tso_segs` | lbe | 16.954 | 16.148 | -4.75% | 34.034 / 52.264 | NO_GO |
| `tcp_tso_rtt_log` | loco | 15.073 | 13.514 | -10.35% | 51.279 / 44.818 | NO_GO |
| `tcp_tso_rtt_log` | lbe | 18.219 | 15.899 | -12.73% | 34.879 / 36.348 | NO_GO |
| `tcp_min_rtt_wlen` | loco | 6.973 | 9.732 | +39.57% | 111.685 / 56.158 | NO_GO |
| `tcp_min_rtt_wlen` | lbe | 11.377 | 12.596 | +10.71% | 50.637 / 51.055 | NO_GO |

NO_GO significa que el gate observo dano o carga/pacing fuera de la banda propia. Una carga no emparejada impide atribuir causalmente el cambio al control; no prueba un limite del chipset.
No se promovio ningun candidato. Las series crudas, conteos enviados/recibidos, SSRC32, byte accounting, perfiles y readbacks estan en el recibo.

## OOM y restauracion

Primer piloto: no habia servidor HTTP; fallo preservado. Segundo: con UISP activo, la Loco sufrio OOM y el kernel termino nuestro companion. No se habia aplicado ningun B.
Hallazgo confirmado: ese conjunto UISP+carga real no entro en el presupuesto de la Loco observado. El portado del bridge a CPEs de esa clase queda bloqueado hasta reducir huella y repetir la calificacion cargada.
El Orquestador autorizo pausar solo el servicio UISP de la Loco durante toda A/A+ABAB (`<orca-id>`). Se mantuvo habilitado al arranque. Estos resultados no califican UISP simultaneo con la carga.
Tercer piloto: carga real valida. El cierre rc=0 produjo un aviso de servicio ya detenido; se preservo el fallo inicial del verificador y se reconcilio tras comprobar manifiesto, supervisor y estado real.
La primera campana completa se interrumpio por WinError 5 al reemplazar el JSON local; restauro ambos CPEs. Sus once ventanas medidas y su primer bloque NO_GO siguen retenidos, separados de la campana final.
La reparacion acota reintentos exclusivamente al reemplazo local del archivo; nunca reenvia una escritura RF. Se midio una A/A nueva y se repitieron los tres bloques, sin mezclar la banda anterior.
Cada CPE tuvo watchdog independiente de 45 s renovado cada 10 s, con receta y SHA previos a las escrituras. La receta de Loco tambien reactiva UISP si cae el PC tras la intencion de pausa.
Cierre final: valores TCP originales, procesos propios inactivos, espacios temporales y guards liberados; roles persistentes conservados. UISP volvio a ACTIVE con CPU/RAM por GET externo.
El watchdog de enlace antiguo retenido en Loco si aparece en ps; la inferencia previa de que estaba inactivo queda refutada. No se modifico ni se detuvo ese proceso.
No se verifico arranque en frio. La revision independiente fue estatica; la aceptacion fisica proviene de los readbacks del banco.

## Evidencia y alcance de aceptacion

- Recibo: `artifacts/autoresearch/wave445_ptmp.json`.
- Evaluador y pruebas: `docs/STAGE3105A_verify.py`, `docs/STAGE3105A_tests.py`.
- Gate: `artifacts/verification/wave445_lane2_ptmp_gate.json`.
Se reconstruyen los bytes CRLF originales para comprobar las fuentes retenidas normalizadas a LF; no se resellan pines de una ejecucion previa.
MemoryMaster MCP fallo por transporte; se uso evidencia primaria local y la referencia Linux. No se afirma ingesta ni cumplimiento completo de cinco pilares a partir de ese fallo.
El PASS del gate corresponde a la ejecucion y restauracion del contrato del banco; no autoriza portado de UISP a produccion ni promocion de rendimiento.
