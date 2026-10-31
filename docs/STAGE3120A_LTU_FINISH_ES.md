<!-- doc-head: W454 persistencia LTU, repetibilidad y limites de diagnostico -->
Banco exclusivo Rocket + Lite .110 + Lite2; evidencia en wave454_ltu_finish.json.
Los estados por criterio y los resultados numericos estan en el gate W454.
Persistencia, medicion, causalidad y aceptacion fisica se evalúan por separado.
<!-- /doc-head -->

# W454 — banco LTU

Se conservaron las configuraciones persistentes del banco: Rocket AP FMX-LTU,
5500/20, AES desactivado, ambos Lites CPE. No se escribio firmware ni particiones
protegidas. La Loco se uso exclusivamente como transporte SSH.

## Persistencia

Se solicitaron soft reboots una sola vez, en orden Rocket, .110, Lite2. Se
compararon boot ID, SHA256 de System, CRC nativo valido y SHA256 de todo el
archivo anexado al banco Active. El retorno de gestion del .110 exige alias
persistente /32, ruta por br0 y RETURN de NAT antes de MASQUERADE. La prueba SSH
crea una conexion autenticada nueva al Rocket y verifica su origen real .110 en
/proc/net/tcp del AP; el AP tiene solo ath0 en br0.

El Rocket y .110 recuperaron ambos pares. Lite2 tuvo re-asociacion tardia tras el
Rocket; no se atribuye a intervencion fisica sin confirmacion del operador. El
estado final despues del reboot de Lite2 se conserva explicitamente en el gate.

## Medicion y fallo conservado

TCP usa un solo CPE, 20 s por direccion y 20 probes RTT bajo carga por direccion.
Se registran retransmisiones TCP, MemAvailable y los cuatro getters de temperatura
antes/entre/despues; su escala fisica no fue calibrada. Los relojes internos de
los radios son distintos: no se usan sus epochs para inferir simultaneidad UTC.

La primera captura v4_AA1 es exploratoria y anterior al reboot .110. v4_AA2 fue
abortada por un error de secuenciacion del coordinador: se solicito el reboot
autorizado mientras la medicion estaba activa. No tiene metricas aceptadas. Se
probo el nuevo boot del CPE y se limpio solamente el servidor owned del Rocket,
con comprobacion de boot y propiedad de PID; no se enviaron señales a PIDs del
CPE despues del reboot. El guard nuevo impide reboot con cualquier campaña sin
limpieza; la regresion local cubre PREPARING, RUNNING y COLLECTED antes de acceso
al dispositivo. Los errores originales siguen en el recibo.

Las repeticiones post_v4_AA* pertenecen al nuevo boot .110. No se consideran A/B
los cambios de boot ni las fluctuaciones espontaneas de MCS. Con dos repeticiones
se informa el rango observado, no significancia poblacional ni umbrales nuevos.

## Señal y causa

Getters nativos de recepcion por cadena dieron .110 -36/-40 frente a Lite2
-76/-77, ambos con ganancia declarada 13 y configuracion de potencia comparable.
El AP tambien informa recepcion de Lite2 mucho mas debil. No demuestra una falla
de hardware: faltan intercambio fisico de posiciones/orientacion, obstrucciones,
polarizacion y verificacion de la unidad/antena por el operador.

No se confunden las dos entradas separadas por `/` de remote_info con dos
cadenas. La RE mostro pares de estructuras distintos; se prefieren rxpower0/1 y
rrxpower0/1. La escala fisica absoluta conserva el limite del productor no trazado.

El scheduler puede seleccionar SISO/QPSK mientras af txspeed imprime 256QAM.
Son superficies distintas, no prueba de modulación de cada paquete. `FB` no fue
demostrado como fallback: full-band es solo inferencia por las entradas SB.
SISO tampoco prueba una cadena averiada. Ver STAGE3120A_rate_mode_re.json y
STAGE3120A_telemetry_semantics.json para offsets, funciones y limites.

La RE del firmware identifica automcsceil oficial pero su efecto incluye
adaptacion de potencia; no se inventa un valor de ganancia, un umbral de señal o
una clave persistente. frame_len de este CPE tiene un callback incorrecto conocido
y no se escribio. Ningun valor B ni mejora persistente se promueve sin una prueba
causal que supere la variacion A/A y cumpla los criterios del contrato.

## Alcance de aceptacion

El gate distingue evidencia CONFIRMED de objetivo completo; ni CRC correcto ni
SSH ni pruebas locales establecen causalidad RF, hardware sano, rendimiento
PtMP agregado o aceptacion del operador. La RE se delego al rea-specialist;
el coordinador ejecuto y verifico las operaciones del banco. Los expedientes
anteriores W442 se usaron como entradas inmutables.

## Resultados finales de la secuencia

Lectura 12:20 UTC: los tres estan Run, Rocket tiene dos estaciones; ambos CPEs
ven el MAC del Rocket. forceSISO0/1 desactivados, txchainenable=2 y adj_mimo=MIMO
en los tres. dutycycle devuelve 75 y framelength 2; son lecturas del CLI, sin
ensayo de sus setters ni atribucion causal de una proporcion TDD.

Post reboot .110: UL 31,8242 / 29,7041 Mbps, DL 62,2673 / 64,1951 Mbps.
Lite2 volvio a asociarse durante esta secuencia: el conjunto de pares inicial
era uno y la lectura final muestra dos. Por eso estas repeticiones NO establecen
una banda A/A controlada para decidir sobre una perilla. No se compara como
mejora causal el UL exploratorio previo de 4,537 Mbps. No hubo ensayo B.
