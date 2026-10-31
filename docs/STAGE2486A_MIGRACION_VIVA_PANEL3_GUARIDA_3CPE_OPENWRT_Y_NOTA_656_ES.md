<!-- doc-head: Wave 241 (2484A-2489A) sintesis ES: nota #656 sobre la migracion en vivo de Panel3-Guarida .83 y sus 3 CPEs (.9, .235, .238) a OpenWrt (kernel 6.6.110): cambio permanente de firmware en produccion, los cuatro arrancaron en 278 a 337 s, LuCI 200 y UNMS conectado; CPE .9 en MCS 0 a 1 con 1 de 4 pings perdido; el preflight marco install_qualified false y no hay registro de vuelta atras; RE estatico de 6035 MHz: la tabla del modulo ath10k corta en 5865 MHz y el firmware ya acepta 6035; banda :8787 a 1536A..2489A; SIN campeon -->
# Reporte ejecutivo - Nota #656: migracion en vivo de Panel3-Guarida y 3 CPEs a OpenWrt

**Wave 241 - Etapas 2484A-2489A - 2026-10-28 - sintesis 100% offline (esta wave no toco ningun equipo).**

## Que se hizo

Se sintetizo la migracion en vivo de Panel3-Guarida .83 y de sus tres CPEs a OpenWrt, junto con la verificacion
posterior (LuCI y UISP) y el analisis estatico del limite de 6035 MHz de la Wave 237, en la nota evergreen #656. Se
regeneraron las paginas de indice del vault, el feed del Command Center :8787 se amplio a 1536A..2489A, se agregaron
filas CRLF a orchestration/autoresearch/results.tsv y las tres docs maestras siguen en 179 lineas con 0 apellidos.

Titular honesto: la migracion es un **cambio permanente de firmware en un AP de produccion y tres CPEs de
abonados**, no un ciclo reversible ni un A/B. **No hay campeon** y las fuentes no tienen mediciones de antes y
despues, asi que no se afirma ninguna mejora.

Alcance de lectura: solo las cuatro fuentes del pedido (los dos recibos de la migracion y los recibos RE 2460A y
2461A). No se abrieron las imagenes de firmware ni los escritores de flash, ni ningun binario o desensamblado.
Las concesiones DHCP de la LAN de los abonados y todas las direcciones MAC quedaron afuera; los equipos se nombran
solo por el ultimo octeto.

## Aclaraciones sobre el pedido

- Las rutas de los recibos RE del pedido no existen. Los de las mismas etapas son
  stage2460a_openwrt_ath10k_5ghz_channels_vs_airos_superchannel_re_receipt.json y
  stage2461a_qca988x_firmware2_vs_airos_target_fw_6035mhz_clamp_re_receipt.json, y esos se leyeron.
- scholar_Pending_sync.py y build_research_index.py no existen en el repositorio; el vault se sincronizo e indexo con
  `hyperresearch sync` y `hyperresearch index build`.
- Los dos recibos RE dicen haberse generado el 2026-11-10, despues de la fecha de esta wave; se registra tal cual.
- El pedido nombra OpenWrt 24.10.4, pero ninguna fuente registra el numero de version de OpenWrt; solo el kernel
  6.6.110 y el modelo de placa. La nota y este documento nombran solo el kernel.

## La migracion (11:18 a 11:25 UTC)

- Los cuatro equipos arrancaron OpenWrt con kernel 6.6.110: el AP como ubnt,lap-120 (LiteAP AC) y los tres CPEs
  como ubnt,litebeam-ac-gen2. SSH respondio entre 278 y 337 s despues del reinicio.
- El preflight de memoria marco **install_qualified false** y device_write false en los cuatro equipos. Las fuentes
  no registran otra calificacion antes del reinicio ni un **plan de vuelta atras**.
- Radio despues del arranque: 5745 MHz (canal 149), 20 MHz, 4addr activo; el AP muestra 3 interfaces de estacion,
  una por CPE.
- Todos los equipos llevan ademas la direccion LAN de fabrica de OpenWrt en br-lan. Los hashes de /dev/mtd0,
  /dev/mtd1 y mac80211.ko son identicos en los cuatro; se registra tal cual, sin interpretarlo.

## Verificacion posterior (11:33 UTC)

- LuCI respondio 200 en los cuatro equipos. El AP corre panel3_admitter, udapi-bridge y uhttpd y dice "Connected to
  UNMS"; el estado de UNMS solo se leyo en el AP.
- Ping al gateway: AP 4 de 4 (6.2 ms); .235 4 de 4 (5.9 ms, MCS 8, -41 dBm); .238 4 de 4 (7.3 ms, MCS 7, -45 dBm);
  **.9 3 de 4 (25.3 ms, MCS 1, -53 dBm)**.
- AQL: el AP usa 1200/2400 por clase de acceso y los CPEs 2000/4000.
- **CPE .9 es el enlace debil**: en la migracion estaba en MCS 0 y en la verificacion en MCS 1, con buena senal. La
  velocidad no coincide con la senal; la causa es desconocida y cuatro pings no son una medicion de perdida.
- En los CPEs el listado de procesos solo muestra el propio grep, aunque LuCI respondio; se registra sin resolver.

## El limite de 6035 MHz (RE estatico, Wave 237)

- 2460A: la tabla estatica de 5 GHz del modulo ath10k de OpenWrt tiene 27 entradas y **corta en 5865 MHz**; 6035 no
  esta, mientras que las dos tablas umac de airOS si lo tienen. El recibo aclara que faltar en la tabla no prueba
  que la radio no pueda sintonizarlo.
- 2461A: el limite de banda del firmware qca988x va de 4910 a 6100 MHz, asi que **el firmware ya acepta 6035**; el
  bloqueo es la **tabla del modulo**. Alcanza con un parche del lado del modulo; reemplazar entradas conserva las
  relocaciones y extender la tabla rompe la seccion de datos. Las relocaciones se razonaron, no se probaron.
- Los dos son analisis estaticos con 0 escrituras a radios. Con Panel3 en OpenWrt, 6035 MHz queda fuera de alcance
  hasta que exista ese parche; nada se sintonizo en el aire.

## recall-first

6 de 6 consultas al vault tuvieron aciertos. No se corrio chequeo scholar (no se pidio).

## Etapas 2484A y 2485A

La nota #656 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista. El tablero se reconstruyo con 441 recibos en la
banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la banda nueva. MASTER, CURRENT y CURATED
siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon**, sin A/B y sin comparacion antes/despues: no se puede decir si la migracion mejoro o empeoro algo.
- La migracion cambio de forma permanente el firmware de equipos de abonados en produccion.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Revisar el CPE .9: velocidad MCS 0 a 1 con buena senal y un ping perdido.
- Conciliar el install_qualified false del preflight con la decision de flashear, y dejar un plan de vuelta atras.
- Decidir si se encara el parche del modulo ath10k para 6035 MHz.

Recibos: `stage2484a_panel3_openwrt_cutover_and_6035mhz_re_note656_receipt.json`,
`stage2485a_command_center_1536a_2489a_refresh_receipt.json`, `stage2487a_memorymaster_ingest_receipt.json`,
`stage2489a_wave241_opus2_gate.json`.
