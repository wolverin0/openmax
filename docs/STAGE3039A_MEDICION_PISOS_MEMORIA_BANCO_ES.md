<!-- doc-head: Wave379, presion RAM escalonada en LAP-120 y Loco -->
Cruce descriptivo AP y OOM basal Loco; pisos calificados UNKNOWN, restauracion comprobada.
<!-- /doc-head -->

# Medicion de pisos de memoria por modelo

**Medicion detenida por OOM en la Loco, antes de completar su A/A.**
No hay pisos calificados para aplicar; ambos equipos quedaron restaurados y asociados.

## Metodo fijado antes de presionar memoria

- Banco: LAP-120 .20 y Loco .250, misma Loco accesible por su IP aerea .200.41.
- TCP bidireccional de cuatro flujos por sentido, continuo; AP hace forwarding Ethernet-radio.
- Receptor iperf3 en la Loco; sus sockets forman parte de la carga y del presupuesto de RAM.
- Tres ventanas A/A de20s por modelo; ping nativo cada1s, RTT p50/p95/p99 observados.
- Solo un equipo presionado a la vez; archivos tmpfs propios de512KiB residentes por escalon.
- Maximo16 escalones; detener al primer p99 sobre maximo A/A o goodput bajo minimo A/A, u OOM.
- Liberacion inmediata al detectar el cruce; dos ventanas de recuperacion con carga continua.
- El primer cruce es descriptivo, no una prueba estadistica de thrashing ni causalidad universal.
- No hay piso MemAvailable numerico que impida medir por debajo de5120/6144.
- Se registran MemAvailable/MemFree/Shmem, contadores disponibles, OOM, estacion y hostapd.
- Estos kernels no exportan pgmajfault/pswpin/oom_kill: sus tasas quedan UNKNOWN, nunca cero.
- Se conserva workingset_refault_file/activate/restore cuando esta disponible y evidencia dmesg.

## Derivacion propuesta

Para cada transicion anterior al cruce: r_i = M_anterior - M_actual - RAM_adicional_residente.
M es la mediana de MemAvailable; s es el desvio muestral de esos residuos (n y grados de libertad publicados).
q = M_ultimo_sin_cruce - M_cruce incorpora la resolucion observada del escalon.
Propuesta F = M_cruce + q + s; requiere q positivo y al menos dos transiciones previas.
Sin bracket o datos suficientes: F UNKNOWN. Una escala s no garantiza cobertura de seguridad.
Tres ventanas A/A y multiples escalones dejan incertidumbre alta y posibles cruces por ruido.
No se extrapola esta propuesta a XC/LTU, otros workloads, firmware ni produccion.

## Recuperacion y limites

Watchdog compartido45s renovado; liberador residente armado antes de reservar tmpfs.
El liberador usa builtins para leer tiempo y truncar16paths propios aun con fallo de fork.
Si no recupera la creacion local de procesos tras liberar RAM, dispone de fallback de reboot autorizado.
Esto no garantiza recuperacion ante todo kernel hang o fallo fisico; no se tomo control del watchdog de procd.
No se tocan particiones, persistencia, colas, potencia, firmware ni archivos ajenos de/tmp.
Alias y NAT privados se retiran al terminar; se verifican boot, enlace, perfil y temporales propios.

El intento1 no aplico presion: ping fraccionario era rechazado por BusyBox y el A/A fue invalido.
Se preserva el intento y la prueba loopback; el intento2 usa intervalo nativo entero y lectura de header acotada.

## Resultados fisicos

| Modelo | Primer cruce | RAM tmpfs | MemAvailable | Piso calculado | Piso calificado |
|---|---|---:|---:|---:|---|
| LAP-120 | paso6, goodput bajo envolvente A/A |3072KiB|5372KiB mediana|6046.63KiB provisional|UNKNOWN|
| Loco5AC | OOM en primer A/A, sin escalones propios |0KiB|2728KiB ultima lectura previa|UNKNOWN|UNKNOWN|

AP: A/A goodput77.497/76.950/85.162Mbps; p99 max81.079ms.
Paso6:67.967Mbps, p99=49.642ms. Se liberaron los3072KiB residentes al cerrar esa ventana.
q=5800-5372=428KiB; residuos previos=[8,20,-512,-504,-376,-512,-504]KiB.
Desvio muestral s=246.630628KiB (n=7,gl=6); margen=q+s=674.630628KiB.
F=5372+428+246.630628=6046.630628KiB. Es calculo descriptivo, no garantia de seguridad.
La recuperacion continuo en60.762/65.518Mbps: no volvio a la envolvente A/A.
Por eso la propuesta numerica del AP no queda validada; hay confusores del peer y la carga continua.

Loco: OOM nuevo mato al receptor propio iperf3 PID10887 en uptime488881s.
La ultima lectura antes del evento fue MemAvailable2728KiB/MemFree6628KiB;
la primera observacion posterior fue9792KiB, ya con memoria liberada por el kernel.
El valor exacto al OOM queda null. No se usa el valor posterior para fabricar un piso.
Se excluyeron del conteo los mensajes OOM antiguos de uptime271259s.
No se completo el A/A de la Loco; su punto y margen estan censurados por la izquierda.

Once ventanas completas (3A/A,6presion,2recuperacionAP) mas un A/A Loco abortado.
Todos los pasos aplicados verificaron512KiB adicionales residentes; ninguna presion propia en la Loco.
Tras cerrar TCP: AP9304KiB y Loco9244/9188KiB en las lecturas frescas.
Dos rondas verificaron boot, enlace, hostapd y perfil; sin iperf3, reapers ni handles propios.
No hubo reboot ni escrituras en flash. El fallback de reboot no se ejercito fisicamente.
La propuesta de patch queda dentro del recibo como registro provisional; no cambia guardas existentes.
Se conserva RECOVERY_PENDING de la salida del receptor: ausencia posterior no prueba cierre TCP limpio.
Siguiente medicion sugerida: receptor cableado externo tras la CPE y controles de recuperacion emparejados.

[Recibo](../artifacts/autoresearch/wave379_memory_floor_bench.json) ? [Gate](../artifacts/verification/wave379_lane1_memory_floor_gate.json)
