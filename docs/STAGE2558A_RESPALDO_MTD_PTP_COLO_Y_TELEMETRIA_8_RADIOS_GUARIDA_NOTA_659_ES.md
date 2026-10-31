<!-- doc-head: Wave 253 (2556A-2561A) sintesis ES: nota #659 sobre el respaldo MTD de PtP-Colo (.62 y .54, 2538A: 8 de 8 particiones mtd0/1/4/5 verificadas por md5 + 2 system.cfg, sin kernel ni rootfs, asi que no es una imagen completa) y la telemetria de las 8 radios OpenWrt de Guarida bajo psk2 (2496A-2499A: 7 de 8 leidas directo, fq_overmemory por hora 2358.64 en Panel3 contra 220.65 en Panel1, CPE .9 en MCS 0, desbalance 10, 12 o 3 dB segun la vista, ninguna fuente cuenta respuestas DUP); faltan 2500A y 2501A; banda :8787 a 1536A..2561A; SIN campeon -->
# Reporte ejecutivo - Nota #659: respaldo MTD de PtP-Colo y telemetria de las 8 radios de Guarida

**Wave 253 - Etapas 2556A-2561A - 2026-10-28 - sintesis 100% offline (esta wave no toco ningun equipo).**

## Que se hizo

Se concilio en la nota evergreen #659 el respaldo MTD de las dos radios de PtP-Colo (2538A, Wave 250) con la
telemetria de las dos celdas OpenWrt de Guarida bajo psk2 (2496A a 2499A, Wave 243). Se regeneraron los indices del
vault, el feed del Command Center :8787 se amplio a 1536A..2561A, se agregaron filas CRLF a
orchestration/autoresearch/results.tsv y las tres docs maestras siguen en 179 lineas con 0 apellidos.

Titular honesto: el respaldo de PtP-Colo esta **verificado en 8 de 8 particiones** y en los dos system.cfg, pero
**solo cubre mtd0, mtd1, mtd4 y mtd5**. El kernel (mtd2) y el rootfs (mtd3) **no se volcaron**, asi que el
"full_backup 1" del recibo quiere decir "todas las particiones previstas", no una imagen completa de la flash. **No
hay campeon** y no se afirma ninguna mejora.

Alcance de lectura: solo los cinco recibos JSON. No se abrieron las imagenes respaldadas, los system.cfg ni la captura
cruda, ni ningun binario o desensamblado. Las carpetas del respaldo llevan la direccion completa de cada radio en el
nombre, asi que no se copian; los equipos se nombran solo por el ultimo octeto y no hay direcciones MAC.

## Aclaraciones sobre el pedido

- 2500A y 2501A no existen; se leyeron 2496A a 2499A.
- "8 radios": 7 se leyeron directo (todas OpenWrt 24.10.4 con psk2); cpe_80 solo desde el AP, que muestra cifrado en
  uso, pero su version no se leyo.
- "0% DUP en .210.9": **ninguna fuente cuenta respuestas DUP**. Solo hay una frase del 2496A que dice que
  desaparecieron despues de psk2; el porcentaje no esta medido.
- "10 dB de desbalance": es la vista del AP en la primera foto; en la segunda (2499A) son 12 dB y en la vista del
  propio CPE son 3 dB.
- closed_loop_research_reactor.py no tiene la opcion --sync-hyperresearch (su arranque regenera recibos viejos) y
  build_hyperresearch_vault_index.py no existe; se uso `hyperresearch sync` y `hyperresearch index build`.

## Respaldo MTD de PtP-Colo (2538A)

- Las dos radios corren airOS 8 WA.v8.7.25, respondieron y no se les escribio nada (0 escrituras, 2 sesiones SSH de
  solo lectura).
- Cuatro particiones por radio, md5 del equipo igual al de la copia local en las 8: u-boot (262144 bytes), u-boot-env
  (65536), cfg (262144) y EEPROM (65536). Las copias locales tienen ademas sha256.
- u-boot y u-boot-env son identicas en las dos radios; cfg y EEPROM difieren (configuracion y calibracion propias).
- system.cfg capturado en las dos (197 y 191 lineas). Contiene la configuracion completa de cada radio; no se abrio.
- Para volver a este estado de airOS haria falta, ademas, el kernel y el rootfs de airOS 8 desde otra fuente.

## Telemetria de las celdas de Guarida (2496A a 2499A)

- psk2 confirmado en 3 de 3 estaciones de Panel3; en el unico episodio psk2 retenido, el puerto 4addr quedo
  reenviando antes de terminar el handshake de 4 pasos.
- Ambos AP con umbral AQL 4000. Veredicto 2499A: las dos celdas en psk2, Panel1 con 3 de 3 estaciones en NSS2 MCS7 o
  mas y Panel3 con 2 de 3.
- **fq_overmemory por hora de uptime: 2358.64 en Panel3 contra 220.65 en Panel1.** Supone un ritmo parejo desde el
  arranque; en la ventana de 45 s Panel3 sumo 184 y Panel1 0.
- **CPE .9**: MCS 0 en las dos direcciones y una sola cadena espacial; el AP registro 2184 envios fallidos hacia el
  en 45 s.
- La ventana es de 45 s, de solo lectura y sin trafico inyectado.

## Recibos no leidos

En la banda hay tres recibos sobre el CPE .9 y la cadena de 6035 MHz que el pedido no nombro (2532A, 2534A y 2539A).
No se abrieron; el 2534A habla de ajuste de RTS y distancia, asi que conviene revisarlo antes de decidir sobre el .9.

## Etapas 2556A y 2557A

La nota #659 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e `hyperresearch index build`
devolvieron 0 y el vault llego a 719 notas. El tablero se reconstruyo con 476 recibos en la banda, 0 apellidos, 0
alias, ninguna MAC de las fuentes y ninguna ruta del respaldo; el servidor :8787 responde HTTP 200. MASTER, CURRENT y
CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon**, sin A/B y nada aplicado por esta wave.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico por CLI
  con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Decidir si se agrega un respaldo del kernel y el rootfs de PtP-Colo, o si alcanza con bajar airOS 8 del fabricante.
- Guardar las carpetas del respaldo y los system.cfg como material sensible.
- Revisar 2532A y 2534A antes de cualquier accion sobre el CPE .9.
- Decidir si se investiga por que Panel3 pierde fq_overmemory diez veces mas rapido que Panel1.

Recibos: `stage2556a_ptp_colo_mtd_backup_and_panel3_8radio_psk2_note659_receipt.json`,
`stage2557a_command_center_1536a_2561a_refresh_receipt.json`, `stage2559a_memorymaster_ingest_receipt.json`,
`stage2561a_wave253_opus2_gate.json`.
