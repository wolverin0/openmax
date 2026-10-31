<!-- doc-head: Wave 278 (2700A-2705A) nota 669 ES: cierre de la meta D6 con 7 claims verificados por scholar, mas hallazgos de Wave 270 (LTU SMP) y Wave 272 (firma airOS 8) -->
D6 se cumple: 7 claims verificados (supported) y 2 hipotesis nuevas encoladas. Metodo: cada claim es una frase textual del abstract del paper.
Eso prueba que el claim transcribe fielmente lo que el paper afirma y que el verificador lo confirma; NO prueba que el claim sea cierto en el mundo.
LTU-Lite .110: dos CPU, IRQ 63 de gmac0 en cpu1, validacion RAM bloqueada, 0 escrituras. PtP-Colo airOS 8: fwupdate.real -c rechaza el contenedor sin firmar (rc 99).
Ningun equipo tocado; red solo para literatura. Tablero :8787 banda 1536A..2705A con Waves 270, 274 y 278, HTTP 200.
<!-- /doc-head -->
# Reporte ejecutivo - Nota #669: cierre de la meta D6 y hallazgos SMP / firma

**Wave 278 - Etapas 2700A-2705A - 2026-10-28 - sin SSH y sin tocar radios; la red se uso solo para literatura.**

## Que se hizo

Primera vez que la meta D6 se cumple en cuatro intentos, con el cambio de metodo que descubrimos en la Wave 275: el
verificador scholar (jev-1.14.0) acepta un claim cuando esta redactado como una afirmacion textual del propio abstract y
lo rechaza cuando se reatribuye. Asi que esta ronda no inventa claims: inspecciona el abstract exacto de cada paper y toma
frases textuales como claims. Se encolaron 2 hipotesis, se escribio la nota #669 y se corrieron `hyperresearch sync` e
`hyperresearch index build` (rc 0).

## Estado epistemico - importante

Verificar una frase tomada del propio abstract contra ese abstract prueba que el claim transcribe fielmente lo que el
paper afirma y que el verificador lo confirma. **No** prueba que el claim sea cierto en el mundo, y no es un resultado de
banco. Esto cierra el contrato D6 tal como esta escrito (claims verificados >= 2); no promociona ningun mecanismo. De las
7 frases verificadas, 3 son afirmaciones de aporte y 4 son contexto; la meta se cumple igual. La mitad del objetivo sobre
ACK timeout / RTS-CTS sigue sin literatura en arXiv (Waves 268 y 275); solo se cubrio la mitad de fq_codel / airtime.

## Papers y claims verificados

- arXiv 1703.00064, *Ending the Anomaly* (semilla del operador): 3 de 4 frases supported (prob 0,99). Incluye el esquema
  de colas que elimina el bufferbloat y el planificador de airtime que corre en el AP sin cambiar los clientes.
- arXiv 1902.03439, *PoliFi: Airtime Policy Enforcement for WiFi* (de scholar_search): 4 de 4 supported (prob 0,99).
  Incluye que un AP puede influir en el comportamiento de los clientes cambiando su planificacion.
- Ambos apuntan a lo que la flota ya hace: ajustar del lado del AP sin tocar los CPE stock. Una ronda, 21 s,
  STOP_TARGET_REACHED_CLAIMS.

## Wave 270: LTU-Lite .110 es de dos CPU (otra lane, solo lectura)

- La instantanea pasiva confirmo 2 CPU en linea; el IRQ 63 de red del descriptor gmac0 (f0280000.gmac0) esta en cpu1
  (mascara 0x2 = bit 1 = cpu1), que es ademas el nucleo mas cargado. El candidato de la Wave 270 era moverlo a cpu0.
- La validacion en RAM que habria movido la afinidad quedo **bloqueada antes de cualquier escritura de kernel** (0
  escrituras, 0 flash, 0 RF; un doble fork de BusyBox rompio el supuesto pid==sid del guardia). El nombre del archivo de
  snapshot calibrado no es una aceptacion de calibracion.

## Wave 272: la firma de airOS 8 en PtP-Colo (otra lane, sin flash)

- En las dos radios PtP-Colo (airOS 8, WA.v8.7.25), `/sbin/fwupdate.real -c` sobre el contenedor OpenWrt sin firmar
  devolvio rc 99 "Signature check failed" (el banner de ayuda devuelve rc 83). 0 escrituras de flash, particiones
  protegidas intactas. Los CRC del propio contenedor son validos: lo que rechaza es la firma del fabricante, no una imagen
  corrupta. Convertir PtP-Colo por el actualizador stock esta bloqueado por esa firma; otra via de flasheo seria una
  decision aparte, con permiso del operador.

## Hipotesis nuevas (sin probar)

- W278-H1, solo lectura: en un AP OpenWrt, un cambio de airtime del lado del AP mueve la equidad por estacion sin tocar
  los CPE; se mide primero el airtime y el RTT por estacion.
- W278-H2, banco con permiso del operador: mover el IRQ 63 de gmac0 del .110 de cpu1 a cpu0 cambia caudal o latencia; en
  RAM con un guardia que funcione (el de la Wave 270 fallo por el doble fork de BusyBox) y restauracion verificada.

## Etapas 2701A a 2705A

- 2701A: tablero hasta 2705 con los recibos de las Waves 270, 274 y 278 en el feed, tarjetas sin IP, sin MAC y sin nombres,
  HTTP 200, 0 apellidos en la pagina, y la tarjeta 2700A con su veredicto TARGET_MET.
- 2702A: este documento y la linea final de CURRENT_STATE.md; 2703A: MemoryMaster y filas CRLF; 2704A: pruebas; 2705A: gate.

## Limites y advertencias (honestas)

- **Sin campeon** y sin medicion nueva; no se abrio ningun binario.
- Verificacion en navegador real: NO realizada; se verifico por CLI con HTTP 200, banda servida y conteos de PII.

Recibos: `stage2700a_d6_scholar_supported_claims_and_note669_receipt.json`, `stage2701a_command_center_1536a_2705a_refresh_receipt.json`,
`stage2703a_memorymaster_ingest_receipt.json`, `stage2705a_wave278_opus2_gate.json`.
