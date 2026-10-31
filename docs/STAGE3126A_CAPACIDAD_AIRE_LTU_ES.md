<!-- doc-head: Stage 3126A (W459) ES: por que el banco LTU midio 5-31 Mbps de subida y 62-74 de bajada cuando la hoja de datos dice 900+ Mbps. Paso 0 resume el trabajo LTU previo y las hojas de datos; paso 1 mide la capacidad de aire en 20 y 50 MHz entre Rocket y Lite1 .110. Ancho 20 MHz, reparto 75/25, techo de modulacion 10x, Rocket en firmware 2.1.0 (tope 50 MHz) y generadores en el CPU del radio -->
Que cubre: resumen del trabajo LTU previo, hojas de datos oficiales, limites fisicos del banco y la medicion de capacidad de aire.
Estado: ver seccion 3 y el gate artifacts/verification/wave459_lane3_ltu_air_capacity_gate.json.
Datos maquina: artifacts/autoresearch/wave459_ltu_air_capacity.json. Direcciones del banco solo por ultimo octeto.
Leer cuando: antes de citar un numero de throughput LTU o de repetir una medicion LTU en el banco.
<!-- /doc-head -->
# Stage 3126A: capacidad de aire del banco LTU (W459)

## 1. Paso 0: que dice nuestro trabajo previo

- **Todas las mediciones por aire fueron a 20 MHz.** W441 (STAGE3101A) dio subida 4,5-6,3 y bajada 69-70 Mbps; W442 (STAGE3102A) dio 4,6-22 y 71-77; W454 (STAGE3120A) dio 30-32 y 62-64. El propio STAGE3101A aclara que no fue un benchmark con generadores externos ni una prueba de capacidad.
- **El iperf3 corrio en el CPU de los radios.** Los "SoC Bulk TCP" de 186 y 259 Mbps de STAGE103F fueron por Ethernet entre radios, no por aire. Los "stream" de unos 14 Mbps de STAGE12 y el goodput de STAGE15/17B/24F eran sesiones SSH. STAGE15 ademas no tenia enlace (W370 vio TOTAL LINKS 0).
- **La ingenieria inversa no es medicion.** STAGE11 leyo en la calculadora `ameeng.cgi`, a 40 MHz con reparto 75 y 4096QAM (12x), 453 Mbps de bajada, 108 de subida y 561 en total. Es una tasa de capa fisica calculada, nunca medida por aire. STAGE12 RE: a 20 MHz la sensibilidad es -63 dBm para 4096QAM, -69 para 1024QAM y -75 para 256QAM; la tabla PtP da -56 dBm para 4096QAM.
- **Las perillas del ledger** (familia LTU: 78, 69 probadas) miden latencia del lado Linux. Ninguna fila mide throughput por aire salvo STAGE50B: el techo 256QAM bajo TCP de 14,5 a 9,8 Mbps con -79 dBm.
- **Refutado:** "Rocket 2.1.0 y Lite 2.4.x no pueden enlazar juntos" (memoria de STAGE15). W454 y esta ola ven 2 enlaces arriba.
- **GUIA_UNIVERSAL_LTU_SAFE_CHAMPION** es solo sysctl/BQL/fq_codel del lado Linux; no afirma nada de RF.

## 2. Hojas de datos oficiales

| Equipo | URL | Ancho de canal | Throughput maximo | Otros |
| :--- | :--- | :--- | :--- | :--- |
| LTU-Rocket | https://dl.ubnt.com/ds/ltu-rocket | 10/20/30/40/50/60/80/100 MHz, con nota "FW version 2.3.0 and later" | "900+ Mbps", con nota "FW version 2.3.0 and later" | 29 dBm conducidos; (2) GbE; reparto subida/bajada 25/75, 33/67, 50/50 |
| LTU-Lite | https://dl.ubnt.com/ds/ltu-lite | 10/20/30/40/50/60/80/100 MHz, con la misma nota | "900+ Mbps", con la misma nota | 22 dBm por cadena; 13 dBi; (1) GbE |

Ninguna de las dos hojas trae una tabla de throughput por ancho de canal ni una ventana de señal recomendada.

## 3. Banco al 31/10 (lectura en vivo, CONFIRMED)

- **El Rocket esta en aflturocket v2.1.0 y los Lite en afltu v2.4.0.** El Rocket solo ofrece 10/20/30/40/50 MHz (`getfrequencies.cgi`); el Lite ofrece hasta 100. Los 60/80/100 MHz y los 900+ Mbps exigen 2.3.0 o posterior en el Rocket.
- **Configuracion de los tres:** 20 MHz, reparto 75/25 (`duty_cycle` 750, trama 2000) y techo de modulacion `automcsceil` 10x (1024QAM): 4096QAM esta deshabilitado.
- **Capacidad nativa del Rocket a 20 MHz** (`af get txcapacity/rxcapacity` por estacion):

| Estacion | Bajada | Subida |
| :--- | :--- | :--- |
| .110 | 109,4 Mbps a 64QAM (6x) | 46,8 a 1024QAM (10x) |
| Lite2 | 73,0 a 16QAM (4x) | 37,4 a 256QAM (8x) |

  Escala lineal: 18,24 Mbps de bajada y 4,68 de subida por bit de modulacion. W454 midio el 57-68 % de ese techo nativo.
- **Señal despues de la reorientacion de Lite2** (STAGE3123A, 13:05Z): el AP ve a .110 en -57/-53 y a Lite2 en -67/-73; Lite2 ve al AP en -61/-66. El despacho cita -76/-77, que es el valor anterior a mover Lite2.
- **Subida en 6025 MHz:** los CPE transmiten en 6025 y el AP recibe ahi, aunque la configuracion dice `splitfreqmode=disabled`. 6025 esta dentro de la lista del Lite (5725-6190 a 20 MHz). El origen es UNKNOWN y sobrevivio a los reboots de W454.
- **No hay ningun host cableado capaz de mas de 100 Mbps detras de los radios:**
  - Rocket: `eth0` sin enlace y solo en br2; br0 tiene solo `ath0`.
  - .110: negocia a 100 Mbps. Los dos extremos anuncian solo 10/100 aunque el PHY soporta 1000. Esa es la firma de un cable o inyector de 2 pares (INFERRED).
  - Lite2: esta detras de la Loco .117, que es de W457, y no se uso.
- **Lite2 no responde por aire desde .110** porque el Rocket tiene `l2_isolation=enabled`, que bloquea el trafico entre estaciones.

## 4. Paso 1: cambios aplicados (persistentes, verificados con reboot)

- **Mecanismo:** el propio `rc.softrestart test` del firmware aplica `/tmp/system.cfg` sin grabar en flash. En cada radio RF-only quedo un watchdog local que lo reiniciaba a su config de flash si no se confirmaba. Despues se grabo con el mismo escritor que usa el boton Guardar. Toco solo la particion llamada `cfg` (indice 5 en este layout LTU); no toco spl, uboot ni EEPROM (indices 0-4).
- **Rocket `l2_isolation=disabled`:** Lite2 se alcanza por aire a traves de .110 sin usar la Loco, y el cambio aplico por via rapida sin cortar el enlace.
- **50 MHz en los tres** (`chanbw`, y `rx_chanbw`/`tx_chanbw` en los Lite): los dos CPE reenlazaron en menos de 40 s. 50 es el maximo del Rocket con 2.1.0.
- **Espectro del Rocket:** potencia media de 1 hora plana entre 5100 y 6200 MHz (unidades UNKNOWN).
- **Reboot de los tres:** boot ID nuevo y configuracion conservada (50 MHz, aislamiento apagado, 2 enlaces). Despues de este reboot la subida dejo de estar en 6025 MHz y quedo en 5500/5500. En W454 la subida en 6025 si sobrevivio a un reboot sin cambio de ancho, asi que el origen sigue UNKNOWN.

## 5. Paso 1: medicion (A/A x2 por configuracion, 15 s por prueba)

Todos los generadores corren en el CPU de un radio. Cada numero es una **cota inferior** de la capacidad de aire. CPU es el porcentaje ocupado del total de 2 nucleos durante la prueba.

| Config | Cliente | TCP 2x2 bajada | TCP 2x2 subida | speedtest nativo bajada/subida | Capacidad nativa bajada/subida | CPU Rocket |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 20 MHz | .110 | 89,2 (A2; A1 parcial: 39,2 de 1 proceso) | 31,3 (A2) | 82,7 y 77,9 / 31,7 y 30,5 | 109,4 (6x) / 37,4 (8x) | 76-87 % |
| 50 MHz | .110 | 89,9 / 94,7 / 77,2 post-reboot | 47,0 / 42,9 / 48,9 | 81,9 / 38,6 | 268,8-358,4 (6x) / 50,4 (4x) | 77-84 % |
| 50 MHz | Lite2 | 70,3 / 70,8 | 11,7 / 11,6 | no corre (IPv6) | 179,2 (4x) / 12,6-25,2 (1-2x) | 76-79 % |
| 50 MHz | ambos a la vez | 81,3 / 86,2 en total | 27,4 / 27,8 | - | - | 89-91 % |

- **A 20 MHz el techo nativo (109) y el del generador (unos 90) casi coinciden,** asi que los 89 de TCP no se pueden atribuir solo al radio. TCP y el speedtest llegan al 71-82 % del techo nativo de bajada y al 82-85 % del de subida. Los 62-74 de W454 quedaron por debajo de los dos techos.
- **A 50 MHz el limite es el generador:**
  - El techo nativo de bajada de .110 sube a 269-358, pero el TCP queda en 77-95, igual que a 20 MHz.
  - Con dos CPE a la vez la bajada total es 81-86, igual que con uno, con el CPU del Rocket al 89-91 %.
  - UDP queda en 45-54 con el emisor del Rocket al 92-97 %.
- **La subida si mejoro con el ancho:** .110 paso de 31 a 43-49 Mbps.
- **Lite2 sigue debil:** sube en QPSK y el AP lo recibe en -67/-69 (linea `signal`), contra el objetivo de subida del propio firmware, `rxcpetgt=-60`. Lite2 recibe al AP en -62/-67. `af get rxpower0/1` del Rocket da el mismo valor para las dos estaciones, asi que no es por estacion y no se uso para esto.
- **El speedtest nativo a 50 MHz no dio salida en 3 de 6 corridas** (B1 bajada, B2 subida, P1 en los dos sentidos).
- **Modulacion de bajada en 64QAM (6x) en .110 con -53/-49 dBm,** por encima de la sensibilidad de 4096QAM de STAGE12. La causa es UNKNOWN y no se probo: candidatos son el EVM a la potencia de TX del Rocket y el techo `automcsceil` 10x.
- **Frente a la hoja de datos:** los 900+ Mbps requieren firmware 2.3.0 o posterior y canales de 60 a 100 MHz. Con 2.1.0 a 50 MHz, la capacidad nativa por estacion es 269-358 Mbps de bajada a 64QAM. Que llegue a unos 700 Mbps a 4096QAM es una escala lineal INFERRED, no una medicion.
- **Invalidos, en el recibo:**
  - Ventana A0: los servidores murieron al cerrar el canal SSH.
  - Ventana L0: `start-stop-daemon` no arranco sin pidfile.
  - Prueba `l2frame_gen`: el generador nativo era demasiado lento y el pool lo reintento 3 veces; se mataron todos.

## 6. Que falta y quien lo decide

- **Hosts gigabit cableados (accion fisica del operador):** detras del Rocket y de Lite2 no hay cable; .110 negocia a 100 Mbps en los dos extremos. Sin eso no hay medicion fuera de los radios.
- **Firmware 2.3.0 o posterior en el Rocket:** decision del orquestador. W432 vio que la actualizacion stock intenta escribir SPL/U-Boot, que es una particion protegida.
- **Siguiente prueba de banco, sin decision pendiente:** A/B de la potencia de TX del Rocket y del techo 12x, para subir la modulacion de bajada.
