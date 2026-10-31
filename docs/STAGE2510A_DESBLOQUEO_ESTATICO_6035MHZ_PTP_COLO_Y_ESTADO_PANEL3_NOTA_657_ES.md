<!-- doc-head: Wave 245 (2508A-2513A) sintesis ES: nota #657 sobre el desbloqueo de 6035 MHz para PtP-Colo (.62 AP, .54 estacion, hw 207, VHT20): modulo ath10k_core y regulatory.db parcheados, 16 de 16 chequeos estructurales y paquete de 12 archivos, pero solo en disco: 0 escrituras a radios, preflight BLOQUEADO (gateway y MAC sin capturar), mapeo del canal 207 sin probar, la vuelta atras no arranca airOS 8 y el parche pierde 5845 y 5865 MHz; Panel3-Guarida .83 + 3 CPEs en OpenWrt kernel 6.6.110 con el CPE .9 debil; banda :8787 a 1536A..2513A; SIN campeon -->
# Reporte ejecutivo - Nota #657: desbloqueo de 6035 MHz en PtP-Colo y estado de Panel3-Guarida

**Wave 245 - Etapas 2508A-2513A - 2026-10-28 - sintesis 100% offline (esta wave no toco ningun equipo).**

## Que se hizo

Se sintetizo en la nota evergreen #657 la cadena completa del desbloqueo de 6035 MHz para el enlace PtP-Colo (recibos
2478A, 2479A, 2490A, 2491A y 2502A a 2506A) junto con el estado de Panel3-Guarida y sus tres CPEs en OpenWrt. Se
regeneraron los indices del vault, el feed del Command Center :8787 se amplio a 1536A..2513A, se agregaron filas CRLF a
orchestration/autoresearch/results.tsv y las tres docs maestras siguen en 179 lineas con 0 apellidos.

Titular honesto: el desbloqueo esta **preparado y verificado en disco, no en el aire**. Los nueve recibos son
estaticos, con **0 escrituras a radios** y 0 sesiones SSH, y el preflight consolidado dice **BLOQUEADO**. No hay
medicion del enlace, **no hay campeon** y no se afirma ninguna mejora.

Alcance de lectura: solo los recibos JSON de la cadena y los dos recibos de Panel3. No se abrieron el modulo, la base
regulatoria ni el firmware, ni ningun binario o desensamblado. Los equipos se nombran solo por el ultimo octeto; no se
copiaron direcciones MAC ni concesiones DHCP.

## Aclaraciones sobre el pedido

- El pedido habla de "desbloqueo", pero nada se aplico a las radios: el preflight 2506A esta BLOQUEADO y el mapeo del
  canal 207 a 6035 MHz no esta probado.
- El pedido nombra OpenWrt 24.10.4; ningun recibo de la cadena registra esa version. Los archivos llevan openwrt2410 en
  el nombre y el modulo dice kernel 6.6.110.
- firmware-2.bin no forma parte del paquete ni fue modificado; su limite de 4910 a 6100 MHz es el hallazgo de 2461A.
- El pedido no nombra fuentes; se leyeron todos los recibos de 6035 MHz y PtP-Colo dentro de la banda, despues de 2461A.
- Para Panel3 no hay lecturas mas nuevas que la verificacion de las 11:33 UTC ya resumida en la nota #656.
- Los recibos de la cadena dicen haberse generado en noviembre de 2026, despues de esta wave; se registra tal cual.

## La cadena del desbloqueo

- 2478A: la tabla de 5 GHz del modulo ath10k_core tiene 27 entradas, de 5180 a 5865 MHz. Los valores de hardware 203,
  207 y 211 corresponden a 6015, 6035 y 6055 MHz. La base regulatoria ya cubre 6035 dentro de 5925 a 7125 MHz.
- 2479A: dos variantes del parche, 6 bytes cada una, sin cambiar el largo de la tabla.
- 2490A: el parche **reemplaza** dos entradas, no agrega: 5845 MHz pasa a 6015 MHz y 5865 MHz pasa a 6035 MHz (hw 207).
  En la base regulatoria se reescribieron 8 reglas.
- 2491A y 2502A: 15 y 16 chequeos estructurales pasan (tamano, secciones, diferencia de 6 bytes en el modulo y 22 en la
  base). Las 8 reglas quedan con flags 0 y 30 dBm de EIRP.
- 2503A: paquete de 12 archivos para los dos roles (AP .62 y estacion .54). La vuelta atras restaura los archivos a los
  120 s, pero **no arranca airOS 8**.
- 2504A: el canal se escribe como 207, que es el valor de hardware, en VHT20, pais US y WDS en la estacion. El mapeo de
  ese canal a 6035 MHz en hostapd **no esta probado**.
- 2505A: las direcciones se conservan, pero el gateway es un marcador y la MAC falta en los dos roles.
- 2506A: **BLOQUEADO**, porque faltan los datos de identidad.

## Efectos colaterales

- El modulo parcheado **pierde 5845 y 5865 MHz**: esos lugares de la tabla pasan a ser 6015 y 6035.
- Las reglas regulatorias reescritas no tienen restricciones (flags 0) a 30 dBm en todo 5925 a 7125 MHz. Ningun recibo
  establece que ese uso este autorizado; eso queda fuera de estas fuentes.
- Una verificacion estructural no prueba que el kernel acepte el modulo.

## Estado de Panel3-Guarida

- Los cuatro equipos arrancaron OpenWrt (kernel 6.6.110) tras un cambio permanente de firmware; el preflight marco
  install_qualified false y no hay registro de vuelta atras.
- A las 11:33 UTC: LuCI 200 en los cuatro y el AP conectado a UNMS. El **CPE .9** sigue en MCS 1 con 3 de 4 pings y
  senal de -53 dBm.

## Recibos por encima de la banda

Otro carril escribio recibos de PtP-Colo por encima de 2513A (2514A a 2518A, 2520A y 2521A), con nombres que hablan de
identidad desbloqueada, preflight listo, cutover y refutacion de una premisa. No se abrieron y la nota no depende de
ellos; si el cutover ya ocurrio, esta nota describe el estado anterior.

## Etapas 2508A y 2509A

La nota #657 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e `hyperresearch index build`
devolvieron 0 y el vault paso de 715 a 716 notas. El tablero se reconstruyo con 455 recibos en la banda, 0 apellidos y
0 alias; el servidor :8787 responde HTTP 200. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon**, sin A/B y sin nada aplicado en el aire.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico por CLI
  con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Antes de inyectar en PtP-Colo: capturar gateway y MAC, probar el mapeo del canal 207 a 6035 MHz, tener una vuelta
  atras a airOS 8 y resolver la autorizacion regulatoria.
- Confirmar que perder 5845 y 5865 MHz no afecta a ningun enlace que use ese modulo.
- Revisar el CPE .9 de Panel3.

Recibos: `stage2508a_ptp_colo_6035mhz_unlock_and_panel3_state_note657_receipt.json`,
`stage2509a_command_center_1536a_2513a_refresh_receipt.json`, `stage2511a_memorymaster_ingest_receipt.json`,
`stage2513a_wave245_opus2_gate.json`.
