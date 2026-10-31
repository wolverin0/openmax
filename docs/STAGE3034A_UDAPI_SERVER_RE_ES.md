<!-- doc-head: W374 PARTIAL: inventario UDAPI y siete rutas corroboradas con captura; esquemas observados y limites explicitos -->
Analisis offline de binarios y referencia guardada, sin equipos ni ejecucion del target.
WA/XC, dependencias, Lua, framing parcial y superficies de escritura tienen identidad y offsets.
Siete perfiles JSON observados; contratos universales, framing completo y suficiencia UNKNOWN.
Se preservan cierre anterior, fallos y drift del traductor; no se inicia W373.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# W374 / Stage3034A: backend UDAPI de stock y candidato de solo lectura

**PARTIAL.** Se incorporo la referencia guardada suministrada por el Orchestrator
(`<orca-id>`); el cierre previo sin payloads queda preservado en el JSON.
La ultima instruccion del usuario mantiene W374 offline aunque el contrato aislado
actual indique W373. No hubo acceso a equipos ni implementacion del responder.
Atribucion: userspace stock Ubiquiti para handlers/protocolo; referencia guardada
para formas observadas; external controller para analisis y presupuesto.

## 1. Identidad y dependencias

Inputs: `artifacts/firmware_re_xc_ltu/{wa_8725_rootfs,xc_8725_rootfs}` y la
extraccion WA bajo `artifacts/autoresearch/waves_abcd_20261024/`.
El bundle `tools/bench/uisp_udapi_bundle/` es el adaptador/bridge calificado;
no contiene el backend nativo completo.

`bin/udapi-server`: 342404 B, ELF32 MIPS BE, sin section headers.
Version embebida `1.4.0-255-g9ce3f4c`, file offset `0x46744`.

| Plataforma | SHA-256 |
| --- | --- |
| WA | `edb7d53a393d165b2ae29e20d4d885ab0255e92d94a190e95e3fbaafb06ffe9e` |
| XC | `fe31db3486cb4e68a5523aab356ba3c3e268e98ad5dcac6245cbfc8599877719` |

Solo difieren dos bytes, `0x4711..0x4712`, del prefijo build-host en DT_RPATH:
`wa` / `xc`. El resto coincide, pero sus SHA no son iguales. Las bibliotecas
libc/pthread conservan identidades separadas por plataforma en el JSON.
Bridge WA: 606816 B, SHA `11c8f687586ef65fc0115966d3b6bded16f46b9f16568550692080aa5f01716e`.

Ocho DT_NEEDED directos mas loader/libdl transitivos; proveedores:

| SONAME / proveedor | Bytes |
| --- | ---: |
| libjson-c.so.2 | 33352 |
| libpthread.so.0 | 78652 |
| libm.so.0 | 89644 |
| libcrypt.so.0 | 17344 |
| librt.so.0 | 12520 |
| liblua.so.5.1.5 | 191868 |
| libgcc_s.so.1 | 87396 |
| libc.so.0 | 355492 |
| ld-uClibc.so.0 | 28968 |
| libdl.so.0 | 12504 |
| Lua cjson.so | 26192 |
| Lua bit32.so | 4840 |
| Lua struct.so | 9120 |

Los diez proveedores ELF iniciales pesan 907740 B; con tres C-modules Lua,
947892 B, mas 342404 B del servidor. **No es RSS.** El JSON incluye SHA,
SONAME, DT_NEEDED y rutas por plataforma. WA tiene proveedores pero faltan
ocho alias exactos en la extraccion; XC tiene los diez nombres exactos.
Eso distingue inventario de bytes de una instalacion cargable.

Las nueve raices Lua alcanzan **31 modulos Lua y tres requires nativos** por
llamadas literales analizadas, sin sitios require globales pendientes en ese
perfil. Los 31 chunks suman 242588 B y sus hashes coinciden en WA y XC.
`cjson.safe` tiene export `luaopen_cjson_safe` en cjson.so; bit32 y
struct tienen sus respectivos luaopen. No se ejecuto bytecode. Son chunks
Lua 5.1 con extension de integer tag 9. La resolucion efectiva de package.cpath,
preload y overrides del entorno sigue UNKNOWN. Los otros cuatro C-modules
stock se inventarian como presentes, fuera de esa clausura literal.
Esto no cierra dependencias de todos los helpers ejecutables que un handler
pueda invocar, ni prueba carga runtime de las bibliotecas.

## 2. Transporte y envelope local
Socket stream por defecto: `/var/run/ubnt-udapi-server.sock` (offset `0x468a0`).
Eventos: `/var/run/ubnt-udapi-bridge-event.sock` (`0x468c0`).
`configureSockets@0x40c31c` admite modalidades configurables.

- Sender `0x4446b0`: formato ASCII `%u` seguido de LF; llamada snprintf
  `0x444710`, literal en VA `0x4520c4`.
- Receptor: busca LF `0x444864`, convierte longitud `0x4448e8`, exige longitud
  anunciada **menor que 10485760 B** en `0x44492c..0x444934`.
- Existe un camino raw/incremental mediante json_tokener_parse_ex
  `0x42713c`; no se afirma que el prefijo sea obligatorio en todas las modalidades.
- Conteo exacto del NUL final, modalidad usada por ese peer, concatenacion y
  vectores de interoperabilidad siguen UNKNOWN: el JSON guardado no son bytes del socket.
`applicationNew@0x428ec8` instala callback `0x4287d8`, que exige cuatro
campos string: **version, id, method, entity**. Compara GET, POST, PUT,
DELETE e INTERNAL. Lee tambien request, session, source y metadata;
sus tipos completos/obligatoriedad y el rango de version aceptado no se inventan.
La metadata de respuesta fija version `v1.0` y copia id/method/entity
(`0x428458`). El error builder `0x428570` crea `response` con statusCode y
error integer, message string y detail opcional string. Resultado interno cero
se convierte en statusCode 200 (`0x428614..0x42861c`). No es el enum UNMS.
El payload completo de exito por handler sigue parcialmente recuperado.

## 3. Siete GET: rutas corroboradas y esquemas observados

Fuente: `artifacts/autoresearch/wave361_stock_udapi_rpc_samples.json`, 112387 B,
SHA `e756e044de8d8dc5252163406ac7534684c594e9fccdfa90215ef6123bfb04de`.
Contiene 41 muestras: 21 RX, 20 TX, 20 pares unicos por socket/id, 11 nombres RPC.
RX 40 (Statistics) carece de TX retenido; eso no demuestra fallo del backend.
Los tokens anonimizados de entity/version coinciden con `anon_` mas los primeros
16 hex de SHA256 de literales PUBLICOS extraidos de server/bridge: catalogo de
96 entradas verificadas contra bytes y offsets. Los siete matches son unicos
dentro de ese catalogo: **INFERRED**, corroboracion de prefijo de 64 bits, no
prueba del valor original sin anonimizar. No se invirtieron IDs, claves o datos privados.
Los 41 tokens de version coinciden con el literal publico `v1.0`.

| RPC (prefijo udapi-) | Entity publica corroborada | RX/TX | Cuerpo respuesta |
| --- | --- | ---: | --- |
| getSystem | /system | 2/2 | objeto |
| getInterfaces | /interfaces | 2/2 | array |
| getDevice | /device | 3/3 | objeto |
| getServices | /services | 1/1 | objeto |
| getStatistics | /statistics | 3/2 | array |
| getWirelessInterfaces | /system/configuration/basic/wireless | 1/1 | objeto |
| getSystemAirosConfiguration | /system/airos/configuration | 2/2 | objeto |
Los 14 GET retenidos de esos siete tienen version/id/method/entity string,
method GET y ningun request. Los 20 TX del conjunto completo ecoan metadata;
los cuerpos JSON decodificados tienen perfiles Draft 2020-12 por RPC en
`capture_analysis.schema_profiles.methods`: rx_payload_schema,
tx_payload_schema y response_body_schema. `rpc_contracts` contiene referencias.
Son esquemas de lo OBSERVADO: required es interseccion, propiedades adicionales
permitidas; items de arrays vacios, tipos no nulos de campos solo-null, unidades
y variantes no vistas siguen UNKNOWN. No constituyen un contrato universal.
System incluye analyticsEnabled solo-null, defaultGateway, dnsServers, domainName,
factoryDefault, hostname, management, timezone y users; stp existe estaticamente
pero no en estas muestras. Interfaces contiene addresses/ethernet/identification/status;
Device, capabilities/errorCodes/identification. Statistics contiene device/interfaces/
timestamp/wireless: cpu es array identifier(string)/usage(integer), ram tiene
free/total/usage integer y uptime integer; las unidades siguen UNKNOWN.
Services contiene 11 objetos: cdp, discoveryResponder, discoveryScanner, lldp,
ntpClient, pingWatchdog, snmpAgent, sshServer, systemLog, unms y webServer.
Se conservan solo tipos de unms.key y snmpAgent.community (string), sin valores.
Wireless contiene country/hasAdvancedConfiguration/interfaces; Airos, network/system/wireless.
Otros cuatro RPC: RegulatoryDomain tiene 1 par y entity expandida UNKNOWN
(registro nativo `/system/airmax/regdomain/*`). Los hashes de literales del BRIDGE
corroboran getNeighbors GET `/tools/discovery/neighbors` (4 pares),
setSanitizedUispUrl PUT `/tools/unms/ui-url` y subscribeEvents POST
`/tools/events/subscribe` (un par cada uno). Su manejo local o forwarding al backend
no esta cerrado. No se deduce que siete rutas basten, ni se simula exito de escrituras.
Los payload_sha256 declarados no coinciden con ocho serializaciones estandar
probadas del JSON anonimizado; la procedencia de ese digest es UNKNOWN.
Se conservan digest declarado y digest canonico anonimizado por separado;
la discrepancia no demuestra corrupcion ni prueba hashing previo a anonimizar.
Lua airmaxAcFullConfig.get devuelve string cjson.safe.encode; no confundir
ese retorno interno con el cuerpo JSON decodificado observado por el bridge.

## 4. Registro y superficies que no pertenecen al candidato

Hay 21 callsites de constructores generales y 13 de plataforma: nueve Lua y
cuatro nativos. Son llamadas presentes estaticamente, no 34 modulos vivos.
Append del contenedor rechaza NULL/deduplica paths; fallos detienen configuracion.
El JSON enumera los 34 callsites y el seguimiento constructor->registro.
Raices Lua: airmaxAcFullConfig, airmaxBasicSystem, airmaxBasicNetwork,
airmaxAcBasicWireless, airmaxCountries, airmaxZeroWaitDfs, airmaxScan,
airView y airmaxSystemToken. Las tres configuraciones basic registran
`/system/configuration/basic/{system,network,wireless}`. Las restantes rutas
y sus callsites tambien estan en el JSON.

| Superficie | Evidencia estatica y limite |
| --- | --- |
| Configuracion Lua | PUT usa request.body y escribe SYSTEM_CFG_PATH; separado del GET |
| Aplicar configuracion | applyConfiguration@0x40fcac alcanza rc.softrestart save via system |
| Upgrade | worker alcanza fwupdate -m; exige archivo y validaciones previas |
| Factory reset | factoryDefault alcanza factory_reset -R; enlace completo al provider de esa ruta pendiente |
| Servicios/usuarios | registrados setters; helpers actualizan UNMS y sshd; persistencia completa pendiente |
| Regdomain GET | ejecuta /bin/regdomain mediante shellRun; eso no demuestra escritura RF |
| Scan/AirView/token | registrados; sus efectos completos no estan aceptados como solo lectura |
Preparar temporales y crear/quitar/bind/chmod de sockets tiene caminos
estaticos identificados. Registrar setters no demuestra invocarlos al arrancar.
Escritura RF/flash al startup y RSS real: **UNKNOWN**.

## 5. Subset candidato y presupuesto de RAM

Propuesta sin implementar: conservar el transporte del bridge y sustituir
solo el backend local por un dispatcher de lecturas con entities exactas,
metodos permitidos y cache atomica alimentada por el traductor factual.
No cargar los setters/Lua nativos, ejecutar comandos enviados por clientes ni
pasar rutas arbitrarias al servidor stock. Rechazar mutaciones, INTERNAL,
rutas desconocidas, datos viejos y overflow con error explicito.
La allowlist propuesta fija GET/v1.0 y las siete entities; no es la gramatica
universal nativa. RegulatoryDomain, eventos y vecinos requieren contratos adicionales.
El snapshot analizado del traductor aporta version factual, CPU/RAM, interfaces y contadores,
RF observable y estaciones WDS. No aporta por si solo el esquema UDAPI ni la
configuracion airOS completa. Los hashes leidos difieren de W361; se conservan
esas revisiones en el JSON. La verificacion final detecto cambios concurrentes
en ambos archivos y fallo; no se repino el input ni se repitio para dar verde.
La integracion del candidato con la revision nueva requiere otra verificacion.
Campos propietarios desconocidos permanecen
desconocidos; no se falsifica identidad, firmware o estado connected.
Modelo hipotetico single-client: dos bancos de cache agregada de 256 KiB
(512), request 8, TX 16, protocolo 8, rutas 8, stack 64, allocator 64 y base
privada de codigo/datos supuesta 128: **808 KiB**. Excluye buffers kernel,
mapeos compartidos y procesos transitorios del traductor. Los maximos por RPC del JSON
anonimizado compacto suman 11109 B; no son tamanos wire ni picos de parseo.
No es una cota RSS, un minimo garantizado
ni prueba de que entre en la radio. Suficiencia UISP: **UNKNOWN**.

## 6. Evidencia y siguiente paso

Inventario/offsets, grafos Lua, fragmentos, fuentes y revision independiente:
`artifacts/autoresearch/wave374_udapi_server_re.json`.
Gate: `artifacts/verification/wave374_lane4_udapi_server_re_gate.json`.
Revision independiente del alcance estatico: PASS con limites. WSL objdump
fallo antes de generar disassembly; se preservo y se uso Capstone 5.0.7 sobre
los bytes originales, sin ejecutar el target ni repetir el fallo de startup.
Verificacion local: 41 envelopes y 20 cuerpos aceptados por perfiles observados;
44 envelopes y 11 cuerpos alterados rechazados. Las 14 reconstrucciones con
solo entity/version PUBLICAS pasan la politica propuesta; 28 casos con POST,
ruta de upgrade, id ausente o version futura se rechazan. No se ejecuto servidor.
Pendientes: vectores de framing crudo, entity regulatoria, localidad/semantica de
operaciones auxiliares, variantes nativas no observadas y fuentes factuales para
configuracion/capacidades/servicios. Se necesita calificar una revision estable del
traductor y un futuro responder antes de afirmar suficiencia o RSS real.
No se implemento, desplego o ensayo un responder ni se certifica aceptacion UISP.
