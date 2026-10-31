<!-- doc-head: W368 PARTIAL: control A incompleto por cierre SSH; NRCC no cargado; AP y peer recuperados con readback -->
Formato e identidad de A/B revisados offline por rea-specialist.
Peer y listener temporal autorizados; primer intento de autenticacion fallido preservado.
Primera muestra de A incompleta; cero muestras comparativas, cero carga de NRCC.
Modulos y firmware originales, una estacion y limpieza AP/peer confirmados.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# W368 / Stage3028A: precondicion de carga y estado del banco

Resultado: **PARTIAL**, sin A/A valido, comparacion ni promocion de NRCC.
Atribucion: external controller para preflight y recibos; Linux/ath10k para
el estado observado. Rendimiento del firmware QCA candidato: UNKNOWN.

## Contrato y decision del orquestador

Despacho aislado W368 leido con `--my-task lane_4_opencode_deepseek`.
El mensaje `<orca-id>` resuelve el DUT como AP de banco LAP-120, conserva
su estacion intacta, excluye PowerBeam y aprueba 210 minutos. Diseno conservado:
A/A y tres bloques ABBA, con watchdog de 600 s renovado y releido por fase.
Cada fase conserva tres minutos de asentamiento y diez de medicion.
Las referencias originales a CPE y al limite 150 minutos quedan superadas por
esa decision concreta, sin ampliar el alcance a la estacion o a produccion.

## Identidad binaria revisada offline

| Variante | Bytes | SHA-256 |
| --- | --- | --- |
| A, full-community-22 | 204796 | `398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e` |
| B, full-nrcc-community-22 | 202844 | `cdc1af3c3df3d56134f4c6d3b5326ce2682314ee4288cc4f41012cfb0dd76b2d` |

Contenedores `QCA-ATH10K` con terminador NUL; IEs LE32 alineados a cuatro bytes
y EOF consistente. Version IE en offset 20: A `10.1-ct-8x-__fW-022-ecad3248`,
B `10.1-ct-8x-_AfW-022-d8dab8e8`. Imagen de codigo en offset 7256.
OTP identico, offset 108, 7140 B, SHA-256
`bab35d9992e061a545f81822762000549465609a92df5239848e266e58763d64`.
Solo cambia el bit 21 del bitmap de features; el driver lo llama
`ATH10K_FW_FEATURE_PEER_FIXED_RATE`. Esto no prueba por si solo la semantica
de la variante NRCC. Formato CONFIRMED_STATIC; compatibilidad de familia
INFERRED; carga, recursos, estabilidad y beneficio NRCC UNKNOWN.

## Preflight ejecutado y fallo preservado

El DUT tenia los modulos originales, firmware A y una estacion asociada;
no habia ruta a la subred del endpoint utilizado en W367.
Se agrego exclusivamente una direccion temporal de banco a br-lan, con
watchdog de 600 s y trap de limpieza; no se toco configuracion persistente.
El peer existente respondio 3/3 pings. El unico intento de conexion iperf3
al puerto 5201 devolvio `Connection refused`, exit 1; no transfirio la carga.
Esta sonda estaba limitada a tres segundos en caso de conexion y no cuenta
como fase A/A ni medida comparativa. No se escanearon otros endpoints.

Se retiro la direccion temporal, exit 0; el watchdog confirmo cancelacion y
se limpio su directorio RAM. Lectura final: mismo boot_id, uptime 1790.24 s,
MemAvailable 8888 kB, radio AP canal 36/20 MHz y una estacion asociada.
Hashes de core/PCI originales iguales a W367; firmware en /lib y /rom igual a A.
Sin debugfs parcheado, bind de firmware, alias o scratch remanentes.

## Precondicion resuelta y arranque

El primer preflight no encontro listener. El mensaje `<orca-id>`
autoriza iperf3 temporal de un solo uso en la Loco asociada, sin cambiar su
configuracion, con parada y verificacion al terminar. La carga termina en
radios; no equivale a hosts cableados y no prueba capacidad de forwarding puro.

El intento runtime 1 fallo al autenticar el peer: el puntero de credenciales
devuelve una tupla y el adaptador debe seleccionar su segundo elemento.
No cargo firmware ni inicio servidor; restaura el AP original por reboot y
readback CONFIRMED. Se preservo el intento y se comprobo el adaptador con
transporte simulado. Intento 2: peer correcto y hashes verificados, recarga
del firmware A en RAM y 180 segundos de asentamiento completados.
La primera muestra TCP de cuatro flujos termina con SSH exit -1, sin salida
ni exit status valido. Cero muestras completas; segunda A y ABBA no ejecutados.
El servidor del peer recibio trafico parcial y termino con
`select failed: Bad file descriptor`. Su log completo saneado se recupero antes
de limpiarlo, SHA-256 original
`39a97c7b063eb7f9f7056f28bbdfdb6228071092a5139fb8ac37e2f238bfc84a`.
No se acepta ese trafico parcial como goodput ni como control completo.
No se obtuvo pareja cliente/servidor ni ping con carga completo. Causa UNKNOWN:
exit -1 no demuestra OOM o crash del firmware; no quedo dmesg previo al reboot.

La limpieza del intento 2 restauro el AP por reboot, pero el canal al peer fallo.
Se conservo `RECOVERY_UNVERIFIED` del intento y se hizo exclusivamente una
recuperacion dirigida: alias RAM bajo watchdog, identidad Loco, rescate del log,
parada verificada por PID/starttime y ausencia de listener/scratch, sin repetir
el benchmark. Alias y watchdog auxiliares tambien se retiraron.
Lectura final AP: uptime 229.28 s, MemAvailable 10248 kB, una estacion,
modulos originales y firmware A en /lib y /rom con hashes exactos; sin bind,
alias, scratch ni debugfs parcheado. Recuperacion final CONFIRMED_RUNTIME.
Dos reboots controlados del AP en W368, cero del peer; cuatro alias temporales
incluyendo el primer preflight y la recuperacion. Cero escrituras flash o
configuracion persistente. NRCC no se cargo y sigue sin aceptacion runtime.
Goodput, RTT comparativo y deltas de reintentos/fq_overmemory quedan null.
El ping sin carga no los sustituye.

Revision estatica del runner y pruebas de fallos locales verifican rechazo
de A/A en los limites, perdidas/RTT incompleto, respuesta perdida despues de
mkdir y limpieza del peer fallida sin cierre verde. Los fallos de revision
anteriores se preservan. Esto no demuestra recuperacion hardware de un cuelgue.

Limite de inferencia: tres contrastes por bloque ABBA dan ocho permutaciones
de signo. El minimo p unilateral es 0.125 y bilateral 0.25; Sidak no permite
alcanzar 0.05. Aunque se completen los tres bloques, un efecto sera descriptivo,
sin promocion ni afirmacion de significancia. No sumar muestras internas como
bloques independientes. No reutilizar el par parcheado o watchdog W367.

Continuidad: diagnosticar la interrupcion del control A y mejorar la captura
de fallos antes de proponer otro A/A. Verificar exclusion del banco y recibir
un nuevo despacho del orquestador. No avanzar a B con este control fallido.

Evidencia completa: `artifacts/autoresearch/wave368_x07_nrcc_ab.json`.
Gate: `artifacts/verification/wave368_lane4_x07_nrcc_ab_gate.json`.
