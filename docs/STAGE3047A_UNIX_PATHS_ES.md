<!-- doc-head: W387 rutas AF_UNIX del bridge: /run es padre del bind local previo al companion; alcance estatico -->
PARTIAL global; ruta critica /run/udapi-bridge-stream.sock.<PID> CONFIRMED_STATIC.
El padre /run debe resolver a directorio utilizable antes del bind; helper no hace mkdir.
Paths y orden del ELF fijo confirmados; exhaustividad de bibliotecas configurables separada.
Sin equipos, SSH, red ni ejecucion de binarios.
<!-- /doc-head -->

# W387 / Stage3047A: rutas Unix y ENOENT antes del companion

**Directorio critico: `/run`.** El bridge hace bind local en
`/run/udapi-bridge-stream.sock.<PID>` antes del connect al companion.
La ruta usa getpid(); no es un nombre fijo ni un archivo que haya que precrear.
La ausencia del directorio padre puede dar ENOENT en el bind local aunque el
socket remoto del companion este disponible. No se comprobo el estado del banco.

| Ruta o formato | Papel y callsite VA | Padre requerido |
| --- | --- | --- |
| /run/udapi-bridge-stream.sock.%d | bind cliente 0x41b820; %d=getpid() | /run |
| /run/udapi-bridge-ext-session-manager-server.sock | bind sesiones 0x433444 | /run |
| /var/run/ubnt-udapi-server.sock | default remoto; helper connect 0x41b87c; enlace completo default-handler parcial | /var/run |
| /var/run/ubnt-udapi-bridge-event.sock | bind eventos 0x41ba20, caller 0x444d98 | /var/run |
| /var/run/ubus.sock | default cfg 0x40c890; operacion especifica UNKNOWN | /var/run |
| /tmp/ubnt.socket.sysd | default cfg 0x40c830; operacion especifica UNKNOWN | /tmp |
| /tmp/ubnt.socket.ecstatsd | default cfg 0x40c850; operacion especifica UNKNOWN | /tmp |
| /tmp/ubnt.socket.oltd | default cfg 0x40c870; operacion especifica UNKNOWN | /tmp |
| /dev/log | connect syslog condicional, libc VA0x20080 | /dev |

Los defaults no son prueba de un bind/connect concreto: el enlace de los cuatro
daemons sysd/ecstatsd/oltd/ubus no se completo en este pase corto. La tabla no
significa que todos se abran en cada arranque. El proceso cliente no crea los
sockets remotos. El daemon propietario debe bindear su endpoint para que el
connect pueda completarse. Padre existente no implica endpoint disponible.
La resolucion real de symlinks entre /run, /var/run y /tmp en el banco es UNKNOWN.
El requisito es que el padre resuelva a directorio con permisos apropiados.

## Evidencia del bind cliente

Target: `artifacts/firmware_re_xc_ltu/wa_8725_rootfs/bin/udapi-bridge`,
606816 B, SHA `11c8f687586ef65fc0115966d3b6bded16f46b9f16568550692080aa5f01716e`.
El formato esta en VA0x465864/file0x65864. Provider0x444344 llama getpid en
0x44434c y snprintf en0x444368; su delay slot pasa el PID.
Los callers0x444404 y0x444eb4 pasan el resultado como ruta local al helper
edgeos_socket_open_localpath@0x41b700.

El orden es socket(1,2,0), remove(local)@0x41b80c,
**bind(local)@0x41b820**, y solo despues **connect(remote)@0x41b87c**.
Si el bind falla, se toma error/close/return sin contactar al peer por ese socket.
El helper no hace mkdir. remove(local) elimina un endpoint previo; no crea padres.
El literal `bind(): %s` se comparte con el servidor de eventos y no distingue
por si solo cual de los dos binds fallo. El diagnostico exterior
`failed to initialize UDAPI socket %s` puede nombrar el destino REMOTO aunque
lo que haya fallado sea el bind LOCAL. El gestor externo usa un diagnostico propio.
No crear manualmente un archivo con el nombre del PID.

En MIPS, **SOCK_STREAM=2 y SOCK_DGRAM=1**, verificados en el header local
congelado `STAGE3047A_native_mips_socket_bits.h`; no usar los numeros x86.
El cliente es STREAM. Los valores numericos no prueban una incompatibilidad
con un companion STREAM.

## Otros binds y bibliotecas

edgeos_socket_open_server realiza remove@0x41ba0c y bind@0x41ba20;
new_ext_session_manager realiza unlink@0x433434 y bind@0x433444 sobre su ruta
/run. Estos binds tambien requieren padres existentes; el constructor no los
crea en esa ruta. Los helpers make_dir/make_dir_recursive se clasifican aparte:
su mera presencia en el ELF no demuestra que preparen /run antes del cliente.

El censo directo distingue AF_UNIX de los sockets IP/netlink/packet; no todo
bind del binario tiene pathname Unix. El artefacto conserva llamadas y contextos,
formatos, defaults y parametros configurables con sus VA/file offsets.

El cierre DT_NEEDED alcanza13 SONAME (10 directos y3 transitivos), con hashes de
proveedores. libc contiene ademas `/dev/log`, cuyo padre es `/dev`: es la ruta
de syslog, separada del companion. Una biblioteca con soporte Unix configurable
puede recibir un pathname dinamico sin literal fijo en el ELF. No convertir
una busqueda de strings vacia en prueba de ausencia de ese comportamiento.
La exhaustividad de todos los caminos de libcurl/libwebsockets/libcrypto y de
valores configurados/indirectos sigue UNKNOWN. Por eso el gate global es
**PARTIAL**, con el bind critico CONFIRMED_STATIC; no se presenta un grep de
literales como un mapa completo de comportamiento de bibliotecas.

## Frontera y recibos

La ruta critica /run y el orden bind-antes-connect son CONFIRMED_STATIC para
esta identidad. La causa efectiva del error reportado en el banco es UNKNOWN;
no se observaron su filesystem, proceso activo ni argumento concreto del syscall.
No transferir estas VAs a otro bridge, incluyendo builds compat diferentes.

- Lista primero y evidencia: `artifacts/autoresearch/wave387_udapi_bridge_unix_paths.json`.
- Analisis fuente: `docs/STAGE3047A_native_*`.
- Revision independiente: `docs/STAGE3047A_review_*`.
- Gate: `artifacts/verification/wave387_lane4_unix_paths_gate.json`.

No se crearon directorios ni sockets en equipos. La lista es una especificacion
estatica para el Orchestrator; no constituye un despliegue o una prueba de restauracion.
