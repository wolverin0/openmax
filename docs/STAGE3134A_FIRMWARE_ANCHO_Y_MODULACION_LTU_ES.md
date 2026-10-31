<!-- doc-head: Stage 3134A (W467) ES: banco LTU actualizado por el mecanismo stock al firmware oficial 2.4.2 (Rocket desde aflturocket 2.1.0, los dos Lite desde afltu 2.4.0) con hash de ui.com verificado, respaldo de cfg y mtd0-6, config conservada y reenlace confirmado; luego anchos 60/80/100 MHz con capacidad nativa por estacion A/A y la causa de la modulacion de bajada baja (potencia, ganancia, subida en 6025/6075 MHz por autofreqmode, reparto de trama) solo con perillas oficiales -->
Que cubre: actualizacion de firmware, anchos de canal mayores a 50 MHz, capacidad nativa por estacion y modulacion de bajada.
Estado: ver el gate artifacts/verification/wave467_lane3_ltu_fw_width_mod_gate.json.
Datos maquina: artifacts/autoresearch/wave467_ltu_fw_width_mod.json. Direcciones solo por ultimo octeto.
Leer cuando: antes de cambiar firmware, ancho o potencia del banco LTU, o de citar su capacidad.
<!-- /doc-head -->
# Stage 3134A: firmware oficial, ancho y modulacion del banco LTU (W467)

## 1. Firmware oficial 2.4.2 por el mecanismo stock

- **Fuente:** API oficial fw-update.ui.com, canal release.
  - aflturocket v2.4.2 (12/10/2026): SHA-256 `2d2664d7...ad192`, 38.918.528 bytes.
  - afltu v2.4.2: SHA-256 `c41ad561...71bbc`, 24.366.210 bytes.
  - Los hashes locales coinciden. En los radios se verifico md5 (tambien publicado por ui.com) mas tamaño, porque el busybox del Lite no tiene `sha256sum`.
- **Changelog:**
  - 2.3.0 agrega canales de hasta 100 MHz.
  - 2.4.0 apaga SSH solo en la config de fabrica; un upgrade conserva la config.
  - 2.4.1 corrige el acceso web roto en 2.4.0.
  - No documenta paso intermedio desde 2.1.0.
- **Respaldo previo en los tres:** system.cfg, running.cfg, /etc/persistent y mtd0-6 (spl, uboot_env0/1, uboot, EEPROM, cfg, dtb0). Hash de cada uno en el recibo; copias en una carpeta local ignorada por git.
- **Mecanismo:** el mismo que la interfaz web. La imagen va a `/tmp/fwupdate.bin`, se valida con el wrapper `fwupdate -c` (rc 0 en los tres) y se ejecuta `fwupdate -m`, que marca la actualizacion y graba al apagar. No hubo ninguna escritura directa a particiones.
- **Orden:** .110 cableado como canario, luego Lite2 (RF-only) y al final el Rocket (RF-only, el unico paso irreversible). Para el Rocket no hay rollback publicado de 2.1.0 ni vuelta automatica de banco (`altbootcmd=run bootcmd`): si fallaba, solo lo recuperaba el operador cableandolo. Riesgo aceptado con la autoridad del 30-31/10.
- **Resultado (CONFIRMED):**
  - Los tres volvieron con boot ID nuevo, `/etc/version` 2.4.2 y config conservada: ancho, aislamiento apagado y sshd activo. Reenlazaron, y .110 y Lite2 en 2.4.2 enlazaron tambien con el Rocket todavia en 2.1.0.
  - El Rocket agrego una host key ECDSA y la ofrece primero. La RSA fijada no cambio, asi que el pool negocia RSA para el Rocket en vez de aceptar una clave nueva.
  - Efecto colateral: el Rocket ahora transmite 30 dBm conducidos con la misma config (txpower 56 EIRP). Antes eran 23; 2.3.0 corrigio el tope de potencia manual del LTU-Rocket.

## 2. Anchos 60/80/100 MHz (capacidad nativa por estacion, A/A x2)

| Ancho | .110 bajada | .110 subida | Lite2 bajada | Lite2 subida | speedtest nativo .110 bajada |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 50 | 268,8 (64QAM) | 50,4 (16QAM) | 179,2 (16QAM) | 25,2 (QPSK) | 67,3 |
| 60 | 318,7 (64QAM) | 61,9 (16QAM) | 212,5 (16QAM) | 15,5 (QPSK 1x) | 84,4 |
| 80 | 409,0 (64QAM) | 81-122 (16/64QAM) | 136,3 (QPSK) | 20,3 (QPSK 1x) | 78,9 |
| 100 | 495,4 (64QAM) | 99,0 (16QAM) | 165,1 (QPSK) | 24,8-49,5 (QPSK) | 65,3 bajada / 32,1 subida |

- **Capacidad estimada por el firmware a 100 MHz para .110** (`status.cgi`): 826 Mbps de bajada y 198 de subida si llegara a su indice ideal; 1.024 Mbps combinados. Es estimacion del radio, no medicion. Es el orden de los "900+" de la hoja de datos.
- **Ancho persistente: 100 MHz.** Es el maximo que da la mayor capacidad para .110. Lite2 pierde un escalon de modulacion desde 80 MHz por su señal.
- **Espectro:** plano en la lectura de W459. Los speedtest nativos corren en el CPU de los radios (cota inferior), por eso quedan en 65-84 aunque la capacidad nativa crezca.

## 3. Por que la bajada queda en 64QAM (.110) y QPSK (Lite2)

- **Lo que dice el firmware:** el indice ideal de bajada es 10X (1024QAM) para los dos CPE, pero el real es 6X y QPSK, con `dl_bler` de 9.100-9.800 (unidad UNKNOWN) y `ul_bler` 0. El CINR de bajada es 24-27 dB en .110 y 20-21 dB en Lite2, aunque señal contra piso de ruido da mas de 50 dB.
- **Descartado con perillas oficiales (CONFIRMED salvo donde se indica):**
  - Potencia de TX del Rocket, de 30 a 20 dBm con frecuencia fija: la potencia recibida baja 10 dB en los dos CPE y la modulacion no cambia.
    - CINR de .110: a 30 dBm 24, 24, 24, 27 y 25; a 20 dBm 24 y 27. Queda dentro de la misma banda A/A.
    - Agrupado por estado: la primera lectura de cada etiqueta es anterior a su cambio.
    - No es potencia, ni atenuacion, ni saturacion del receptor. La ganancia de antena es EIRP contable y cae en la misma prueba (INFERRED).
  - Reparto de trama 75/25 contra 50/50: solo reparte la capacidad (bajada de .110 495 contra 324). Modulacion y CINR iguales; queda 75/25.
  - `wireless.1.rate.mcs=4`: en la UI oficial es 10X (1024QAM), el maximo y default en PtMP. 12X (4096QAM) esta deshabilitado en PtMP.
  - SISO contra MIMO: SISO no subio el CINR, 25 dB en una lectura (INFERRED). MIMO restaurado.
- **Origen de la subida en 6025/6075 MHz (CONFIRMED por observacion):**
  - `radio.1.autofreqmode=enabled` en el Rocket hace que el AP elija sus frecuencias de TX y RX al reiniciar, aunque la config diga 5500 y `splitfreqmode=disabled`. Con solo un cambio de potencia la bajada salto de 5500 a 5655.
  - En 6075 el AP oia a .110 unos 10 dB mas debil que en 5500 (INFERRED: lecturas de boots distintos, con la potencia de subida bajo control automatico).
  - Quedo desactivado y grabado: 5500/5500 se mantuvo en dos reboots.
- **Causa restante (UNKNOWN, requiere revision fisica):** el CINR no sigue a la potencia, asi que el limite es distorsion y no ruido. Candidatos: multitrayecto por la geometria del banco (el firmware estima 32 m), alineacion de las antenas, o un piso de EVM de TX/RX.
- **Lite2:** el CINR de subida de 1-9 dB puede ademas degradar la realimentacion de la adaptacion de bajada (INFERRED).

## 4. Estado final y correccion a W459

- **Persistente y verificado con reboot de los tres** (14:58Z, 2 enlaces): firmware 2.4.2, 100 MHz, aislamiento L2 apagado. Rocket con autofreqmode apagado, 30 dBm y 75/25. En el Rocket la config en RAM es identica a la grabada en flash.
- **MIMO restaurado:** la capacidad final de .110 es 495.360 kbps y `tx_idx` volvio a 2, igual que en MIMO. En SISO era 330.240.
- **Piso de ruido:** AP -101 dBm y CPE -97 dBm (`status.cgi`), ademas del espectro plano de W459.
- **Ancho elegido 100 MHz, alternativa 60:** 100 maximiza .110 (495 nativos, 826 ideales). Lite2 queda en su peor punto, con bajada QPSK y CINR de subida de 1-9 dB. Su mejor ancho fue 60 MHz (212 de bajada en 16QAM).
- **Correccion a la review de W459:** los generadores de W459 corrieron de SoC a SoC por aire y nunca cruzaron el puerto de 100 Mbps de .110. Lite2, sin Ethernet, midio 70 Mbps igual. Ese puerto sigue bloqueando una medicion cableada.
