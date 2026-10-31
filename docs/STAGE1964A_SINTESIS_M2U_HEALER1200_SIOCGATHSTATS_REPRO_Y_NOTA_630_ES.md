<!-- doc-head: Wave 154 (1962A-1964A) sintesis ES: nota #630 une Waves 143 (A/B en vivo m2u=0 vs m2u=1 SIN PROMOCION por un bloque + auditoria del healer canonico 4addr ban_time=1200 en ifindex 997, sin recuperacion automatica) y 150 (layout SIOCGATHSTATS struct {4608,4624} y spec que marca 0xb4/0xdc como ALIASED_DO_NOT_USE), y repara los huecos de reproducibilidad de 1933A (registra FMX-DISC-01..16 y corrige la ruta rota); banda :8787 a 1536A..1967A con IDs cpe_ canonicos; SIN campeon; scholar inconcluso -->
# Reporte ejecutivo - Nota #630: m2u, healer canonico, spec SIOCGATHSTATS y reproducibilidad

**Wave 154 - Etapas 1962A-1964A - 2026-10-28 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se sintetizaron 4 recibos de las Waves 143 y 150 en la nota evergreen #630, se repararon los 2 huecos de
reproducibilidad de la Etapa 1933A, el feed del Command Center :8787 se amplio a 1536A..1967A y se
actualizaron los docs maestros. Titular honesto: **no hay campeon de trafico nuevo**, y el aporte duro es
convertir el hallazgo de 1830A en una regla de decodificador: 0xb4 y 0xdc son alias, no contadores de
caida.

## Wave 143 - A/B de multicast-a-unicast y auditoria del healer (en vivo)

- stage1896A (CONFIRMED_LIVE_HARDWARE): un solo A1-B1-A2-B2 con brazo A en multicast_to_unicast 0 y brazo
  B en 1, con el snooping/querier normalizado y restaurado en cada ventana.
  - Brazo A: goodput 73.34 Mbps, perdida IPTV 0.021 %, VoIP 0.1 %.
  - Brazo B: goodput 74.64 Mbps, perdida IPTV 0 %, VoIP 0 %.
  - B es apenas mejor, pero el generador no llego a los 4 Mbps y es un solo bloque:
    **NO_PROMOTION_ONE_BLOCK_VARIABLE_OFFERED_LOAD**. La conversion m2u se prueba a nivel de trama (MAC de
    grupo en A contra MAC de abonado en B); la causa de perdida de la Wave 133 sigue DESCONOCIDA.
- stage1897A (CONFIRMED_LIVE_HARDWARE): auditoria del healer canonico (fmx_ap_4addr_peer_healer.sh llama a
  fmx_apvlan_bridge_healer.sh), instalado en el overlay persistente. Una reasociacion controlada en
  ifindex 997 (brport state 3) llevo ban_time=1200. **automatic_failure_detection_demonstrated=false**:
  prueba el punto de entrada canonico, no la deteccion automatica de wedge.

## Wave 150 - layout SIOCGATHSTATS y spec del decodificador (estatica)

- stage1938A (CONFIRMED_STATIC_BINARY): athbox de WA y XC son identicos byte a byte (202920 bytes). El
  struct compartido de SIOCGATHSTATS mide {4608, 4624}; el decode de offsets del applet quedo DESCONOCIDO
  y la hipotesis de layout distinto quedo REFUTADA (un solo struct, no dos).
- stage1939A (CONFIRMED_STATIC_BINARY, veredicto PARCIAL): la spec corregida marca 0xb4 (no_tx_buffer) y
  0xdc (xmit_filtered) como **ALIASED_DO_NOT_USE**. Reglas: nunca reportar 0xb4 como caida de buffer TX,
  nunca 0xdc como filtrado, un contador real debe llevar etiqueta ast_*, y los offsets >= 0x110c los
  reescribe el ioctl al leer. El tamano de copia se infiere 0x1210 (4624); los 6 offsets ast_* reales
  siguen sin resolver.

## Reparacion de la matriz de reproducibilidad de 1933A

La matriz de la Wave 149 (1933A) daba FAIL por 2 huecos. Se reparo sin tocar el recibo inmutable de
1933A: (1) se registraron los 16 ids FMX-DISC-01..FMX-DISC-16 como tokens literales en
docs/CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md (un registro canonico que los mapea a sus entradas
numeradas); (2) la unica ruta rota docs/contenedores se corrigio a
docs/STAGE264A_ALL_FIRMWARE_CONTAINER_VERIFICATION.md en su fuente, CONTEXTO_MAESTRO. Una re-ejecucion del
reconciliador a una ruta de scratch da broken=0, unregistered=0, unmapped=0, doc_pii=0, veredicto PASS; el
recibo 1933A en disco no cambia (mismo sha256). El doc CURATED tambien se paso a LF y se le quitaron los
apellidos (cpe_ y cpe_curNN).

## recall-first y scholar (honestos)

recall-first: 1 de 6 consultas con aciertos (registro de reproducibilidad 6); el A/B m2u, el healer
ban_time=1200, el rebind de ifindex, el layout SIOCGATHSTATS y los offsets 0xb4/0xdc dieron 0. scholar: UN
chequeo suave del principio de multicast a unicast. El sondeo del motor funciono (P=0.91) pero el unico
candidato fue un paper fuera de tema (rate-splitting multiple access): unsupported, P=0.03. Resultado
**inconcluso**, no una refutacion. Nota #630 ingresada; vault en 630 notas.

## Etapa 1963A - banda 1536A..1967A y docs maestros

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero (187 recibos) con 0 apellidos
del alcance y 0 alias en toda la pagina (IDs cpe_ canonicos). Los docs maestros llevan una linea de la
Wave 154.

## Limites y advertencias (honestas)

- **Sin campeon nuevo**: el A/B m2u es un solo bloque sin promocion.
- El healer audita el camino canonico, no demuestra recuperacion automatica.
- 0xb4/0xdc son alias; todo porcentaje de "no tx buffer" sigue siendo un alias hasta resolver un offset
  ast_* real contra un buffer en vivo.
- El doc CURATED tiene 197 lineas: cumple el presupuesto <200 del pedido, pero sigue por encima del tope
  interno de 180 (condicion preexistente; no se borro contenido historico).
- Quedan apellidos de OTROS abonados en tarjetas historicas, fuera del alcance de 4 apellidos: hace falta
  una lista aprobada.
- **Verificacion en navegador real: NO realizada** (Claude-in-Chrome no conecta); se verifico por CLI.

## Que sigue (decision del operador)

- Campana m2u de varios bloques con carga ofrecida constante antes de promover nada.
- Demostrar deteccion automatica de wedge del healer.
- Resolver un offset ast_* real contra un buffer en vivo.
- Aprobar la lista de apellidos adicionales para limpiar toda la pagina.

Recibos: `stage1962a_ptmp_m2u_healer1200_siocgathstats_note630_receipt.json`,
`stage1963a_command_center_1536a_1967a_refresh_receipt.json`, `stage1967a_wave154_opus2_gate.json`.
