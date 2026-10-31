<!-- doc-head: SUPERSEDED (W435, 31/10): PtP-Colo HOLD and airOS at 6035 MHz are historical; production Colo runs OpenWrt 24.10.4 at ch153 / 5765 MHz and the link is 450 m (operator 30/10). Wave 248 (2526A-2531A) sintesis ES: nota #658 sobre PtP-Colo (.62 AP, .54 estacion) y Panel3-Guarida: el preflight de Wave 246 dice READY y Wave 247 armo dos imagenes OpenWrt 24.10.4, pero la lectura en vivo 2521A muestra que las dos radios corren airOS 8 WA.v8.7.25 y el enlace ya esta en 6.035 GHz, sin OpenWrt donde inyectar; faltan 2519A y 2522A a 2525A; Panel3 en psk2 3 de 3, CPE .9 en MCS 0; ninguna fuente respalda el mecanismo DUP / TID 00 RX; banda :8787 a 1536A..2531A; SIN campeon -->
# Reporte ejecutivo - Nota #658: preflight de PtP-Colo y psk2 en Panel3-Guarida

**Wave 248 - Etapas 2526A-2531A - 2026-10-28 - sintesis 100% offline (esta wave no toco ningun equipo).**

## Que se hizo

Se concilio en la nota evergreen #658 lo que dejaron Wave 246 (identidad y preflight de PtP-Colo), Wave 247 (imagenes
OpenWrt y la refutacion de la premisa del cutover) y Wave 243 (auditoria de psk2 en Panel3-Guarida). Se regeneraron los
indices del vault, el feed del Command Center :8787 se amplio a 1536A..2531A, se agregaron filas CRLF a
orchestration/autoresearch/results.tsv y las tres docs maestras siguen en 179 lineas con 0 apellidos.

Titular honesto: **el cutover de PtP-Colo no hace falta tal como se planteo**. La lectura en vivo y de solo lectura
2521A muestra que las dos radios corren **airOS 8 WA.v8.7.25** (kernel 2.6.32) y que el enlace **ya trabaja en 6.035
GHz**. No hay OpenWrt donde inyectar el modulo; pasarlas a OpenWrt seria una conversion completa de firmware de dos
radios de produccion. **No hay campeon** y no se afirma ninguna mejora.

Alcance de lectura: solo los recibos JSON de las tres waves y el recibo del cambio a psk2. No se abrieron imagenes,
modulos ni bases, ni ningun binario o desensamblado. Las MAC capturadas y las direcciones completas no se copiaron; los
equipos y gateways se nombran solo por el ultimo octeto.

## Aclaraciones sobre el pedido

- 2519A y 2522A a 2525A no existen. El numero 2520A lo usan dos recibos distintos: la reconstruccion de imagenes y el
  preflight del cutover.
- El pedido describe imagenes SquashFS para .62 y .54, pero esas radios no corren OpenWrt (2521A).
- El pedido atribuye la desaparicion total de los DUP en .210.9 a "TID 00 RX = 1". **Ninguna fuente menciona TID 00,
  reordenamiento RX ni A-MPDU**, y ninguna cuenta respuestas DUP. La unica mencion es una frase del 2496A: despues del
  cambio a psk2 "los DUP desaparecieron". El mecanismo queda **sin respaldo** y no se calcula ningun porcentaje.
- closed_loop_research_reactor.py no tiene la opcion --sync-hyperresearch (su arranque regenera recibos viejos) y
  build_hyperresearch_vault_index.py no existe; se uso `hyperresearch sync` y `hyperresearch index build`.
- Varios recibos dicen haberse generado en noviembre de 2026, despues de esta wave; se registra tal cual.

## PtP-Colo: Wave 246 (preflight estatico)

- Identidad capturada para los dos roles: LBE-5AC-Gen2, subredes /30 con gateway .61 (AP) y .53 (estacion). Las tres MAC
  de cada radio se escribieron en los arboles de configuracion; aca no se copian.
- WDS activo en los dos roles; el recibo corrige a Wave 244, que lo habia puesto solo en la estacion.
- El canal 207 corresponde a 6035 MHz por aritmetica (5000 + 5 x 207); el propio recibo aclara que no esta probado que
  el driver lo acepte en marcha.
- 2518A dice **READY**, con dos pendientes: "sin probar en hardware" y "la vuelta a airOS 8 no esta implementada".
  0 escrituras a radios y 0 sesiones SSH.

## PtP-Colo: Wave 247 (imagenes y premisa)

- 2520A: dos imagenes de fabrica OpenWrt 24.10.4, una por rol, de 6910340 bytes. No estan firmadas, no se flasheo
  ningun equipo y no esta probado que el equipo las acepte.
- 2520A (cutover): solo la fase de preflight. Las dos radios responden, kernel 2.6.32 y rootfs al 100%.
- 2521A (en vivo, solo lectura, 2 sesiones SSH, 0 escrituras): premisa no respaldada, enlace ya en 6035 MHz, hace
  falta convertir a OpenWrt, 0 KB libres en el rootfs. Se retuvieron las fases de backup, carga, inyeccion y
  verificacion.
- Conciliacion: el READY de 2518A y las imagenes de 2520A valen para un destino OpenWrt; las radios corren airOS 8, asi
  que READY **no** significa que se pueda hacer el cutover planeado.

## Panel3-Guarida: Wave 243 (psk2)

- psk2 en los cuatro equipos, confirmado en 3 de 3 estaciones; el watchdog mantuvo psk2 en los cuatro. Todos con
  OpenWrt 24.10.4 y kernel 6.6.110.
- En el unico episodio psk2 retenido, el puerto AP/VLAN quedo reenviando antes de terminar el handshake de 4 pasos; la
  comparacion con el modo sin cifrado no se pudo hacer (el log ya habia rotado).
- **CPE .9** despues de psk2: MCS 0 de bajada y subida, una sola cadena espacial, 17138 envios fallidos del lado del CPE
  y 23412 vistos desde el AP, desbalance de cadenas de 10 dB. Justo despues del cambio volvieron 7 de 10 pings. El
  recibo sospecha del camino de RF (cadena de antena, alineacion o cableado), sin verificar.
- 2499A: las dos celdas en psk2; Panel3 tiene 2 de 3 estaciones en NSS2 MCS7 o mas; fq_overmemory por hora de uptime
  2358.64 en Panel3 contra 220.65 en Panel1.

## Etapas 2526A y 2527A

La nota #658 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e `hyperresearch index build`
devolvieron 0 y el vault llego a 718 notas. El tablero se reconstruyo con 469 recibos en la banda, 0 apellidos y 0
alias, y ninguna MAC de las fuentes de esta wave aparece en la pagina; el servidor :8787 responde HTTP 200. Los
recibos por encima de 2531A (2532A, 2538A y 2539A, de otro carril) quedan fuera y no se abrieron. MASTER, CURRENT y
CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon**, sin A/B y nada aplicado en el aire por esta wave.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico por CLI
  con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- PtP-Colo: decidir si se abandona el cutover (el enlace ya esta en 6035 MHz en airOS 8) o si se encara una conversion
  completa a OpenWrt, con banco, vuelta a airOS 8 y espacio en el rootfs resueltos antes.
- Revisar en sitio el camino de RF del CPE .9.
- Si se quiere sostener el mecanismo DUP / TID 00 RX, hace falta una medicion que lo registre.

Recibos: `stage2526a_ptp_colo_live_preflight_and_ampdu_dup_note658_receipt.json`,
`stage2527a_command_center_1536a_2531a_refresh_receipt.json`, `stage2529a_memorymaster_ingest_receipt.json`,
`stage2531a_wave248_opus2_gate.json`.
