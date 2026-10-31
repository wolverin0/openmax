<!-- doc-head: Wave 421, Stage 3081A: Loco 5AC en banco con receptor ligero, A/A fresco y pasos RAM de 512 KiB. Cruce descriptivo de p99 a 1024 KiB propios, sin OOM observado. Margen calculado 4276 KiB rechazado como piso operativo; no se aplica ninguna guarda. -->
<!-- /doc-head -->
# Loco 5AC: presion RAM y limite de la propuesta de piso

## Resultado

CONFIRMED: campana real terminada y restaurada. NO_GO para adoptar un piso fijo por modelo.
El receptor ligero evita el OOM que invalidaba el primer A/A de W379.
El primer cruce descriptivo fue p99=18,77123 ms frente a un maximo A/A de 14,69005 ms.
El goodput de ese paso, 18,615924 Mbps, seguia sobre el minimo A/A de 17,555375 Mbps.
El minimo necesario o piso universal de Loco sigue UNKNOWN; no se cambio ningun umbral.

## Banco y metodo

- LAP-120 .20 AP y Loco 5AC logica .250, alcanzada por su direccion RF .200.41 mediante salto SSH fijado en .20.
- Identidad de placa, claves de servidor SSH y boot_id verificados; mismo arranque antes y despues.
- Sin acceso a LTU detras de eth0, a produccion ni a los PowerBeam de otro carril.
- Descarga TCP real desde el host al receptor Loco, un flujo, 20 s, buffer de aplicacion y solicitud de socket de 16 KiB.
- La solicitud de socket no demuestra el consumo real del socket/kernel; este forma parte del presupuesto medido.
- ICMP IPv6 nativo de 64 B, un eco por segundo, simultaneo con TCP.
- Cinco A/A sin presion; banda de esa misma corrida: minimo goodput y maximo p99 observados.
- Pasos propios de 512 KiB residentes verificados por du; maximo planificado 16, detenido en el paso 2.
- Liberacion en el primer cruce p99/goodput o fallo de salud; dos ventanas de recuperacion iguales.
- Sin piso RAM fijo de aborto, cambios RF, colas, red, persistencia ni flash.
- Contraste de bytes recibidos por iperf con TX del peer AP y RX RF del CPE; eth0 no explica la carga.

## Ventanas de la pasada valida

| n | Fase | tmpfs KiB | DL recibido Mbps | p99 ms | MemAvailable mediana KiB | minimo KiB |
| :-- | :-- | --: | --: | --: | --: | --: |
| 1 | AA | 0 | 32.229 | 6.001 | 4202 | 4164 |
| 2 | AA | 0 | 22.930 | 9.353 | 4124 | 4124 |
| 3 | AA | 0 | 25.550 | 8.832 | 4100 | 4100 |
| 4 | AA | 0 | 17.555 | 14.690 | 4114 | 4100 |
| 5 | AA | 0 | 25.682 | 11.498 | 4128 | 4128 |
| 6 | PRESSURE | 512 | 18.901 | 7.422 | 4064 | 4064 |
| 7 | PRESSURE | 1024 | 18.616 | 18.771 | 3636 | 3636 |
| 8 | RECOVERY | 0 | 18.305 | 11.388 | 3636 | 3636 |
| 9 | RECOVERY | 0 | 18.811 | 9.471 | 3636 | 3636 |

Las nueve ventanas tuvieron perdida ICMP observada de 0%; no hubo eventos OOM nuevos ni reinicios observados.
Los contadores pgmajfault, pswpin y oom_kill no estan exportados: UNKNOWN/null, no cero.
Las tasas workingset nativas y MemFree se conservan con sus capturas en el JSON.

## Derivacion solicitada y decision

MemAvailable al cruce: 3636 KiB. Ultimo paso sin cruce: 4064 KiB; intervalo q=428 KiB.
Residuos previos: caida de memoria menos incremento RAM residente = [78, 24, -14, -14, -448] KiB.
Desviacion muestral s=212,002830 KiB, n=5, grados de libertad=4.
Formula predeclarada W379: F=3636+428+s=4276,002830 KiB, aproximadamente 4,176 MiB.
Es un margen descriptivo de una desviacion, sin cobertura de confianza ni garantia de seguridad.
Las cinco medianas A/A sanas eran 4100..4202 KiB: instalar F abortaria 5/5 ventanas sanas.
Ambas recuperaciones funcionaron a 3636 KiB, p99=11,38766/9,47079 ms y DL=18,304538/18,810986 Mbps.
Por eso F no identifica un minimo necesario; el patch propuesto queda vacio y sin aplicar.
La presion, el tiempo, los sockets, cache y el monitor no quedaron aislados causalmente.
No extrapolar este endpoint TCP a un CPE usado solo como bridge ni a otra imagen o carga.

## Intento conservado y seguridad

La primera pasada termino y restauro, pero llevaba un criterio p95 extra ajeno al metodo solicitado.
Detuvo el paso 1 por apenas 0,0131 ms; goodput/p99 permanecian dentro del A/A.
Se conserva completa en attempts[0], con derivacion invalidada para proponer un piso.
Una sola correccion de protocolo quito ese disparador; no se borraron los resultados previos.
El watchdog compartido SHA 2a125d4e...32074f usa generacion de 45 s renovada y lock durante dd.
Su aceptacion real revisionada de W350 se reutiliza; esta pasada verifica arm/renew/restore/limpieza, no repite la prueba de desaparicion del controlador.
El reaper residente libera archivos propios con builtins, sin fork ni reboot; un aborto posterior a dd vuelve a truncar.
La restauracion propaga fallos de truncacion. STOPPED del reaper no se usa como prueba de liberacion.
Se verificaron restore.rc=0, ausencia de workspace/handle y de procesos propios o iperf, y preimagen de colas/AQL/firmware/rc.local intacta.
El ping final fue 10 enviados/10 recibidos. Hostapd quedo vivo; su PID continuo no se muestreo durante toda la campana.
MemAvailable final fresco: AP 8676, Loco 3664 KiB; Shmem Loco 300 KiB. No se afirma que la memoria total volviera al inicio.

## Verificacion y reproduccion

[Recibo con runner y tests congelados](../artifacts/autoresearch/wave421_loco_memory_floor.json).
Runner SHA256: `59d74844aabe49545f4e845f656737560dd08128d1158469b620d239c5fb6a8d`.
21 pruebas pytest offline pasaron: formulas, evidencia real, adulteracion y liberacion shell en archivos desechables.
La prueba shell local no demuestra supervivencia bajo un cuelgue del kernel o un OOM forzado.
Se preservan el fallo inicial de coleccion por un junction ajeno y el falso positivo del MAC sintetico en el propio test, corregidos sin tocar mediciones.
Los tests estan embebidos en el recibo por el alcance exclusivo; se ejecutaron en un directorio temporal aislado.
La revision independiente confirma numeros y limites, sin autorizar un piso general ni despliegue.

## Fuentes leidas

W379 y su recibo; STAGE12_OFFLINE_DOE_AND_PTMP_MODEL; STAGE3061A_LTU_LITE2_DETRAS_DE_LA_LOCO_ES;
PLAN_ROLLOUT_CAMPEON_V2_ES; STAGE1013A_BUSYBOX_NC_UHTTPD_BRIDGE_SINK_ADAPTER;
STAGE1026A_OPENWRT2410_VO_VI_BE_BK_AQL_PARETO_CALIBRATION;
STAGE1249A_OPUS55_INPLACE_TOPOLOGY_AND_SG01_HARDENING.
