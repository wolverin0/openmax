<!-- doc-head: W420: transporte LTU, inventario observado y límites de aceptación -->
Diez canales SSH IPv4 al Rocket agotaron 30 s; LAP y Loco autenticaron rápidamente con sus claves fijadas.
Captura LAN de 60,140 s: Rocket PUBLIC_DEVICE_0050 / 198.18.0.136; 40 paquetes, cero descartes.
Diagnóstico TCP de 34,109 s: nueve SYN salientes, cero SYN-ACK y cero respuestas ARP; causa específica UNKNOWN.
Diez candidatos IPv6 y diez nuevos intentos IPv4 tras el PoE reportado también fallaron. No se aplicó el perfil Rocket.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# W420 — Transporte e inventario del banco LTU

## Plan vigente y alcance

El contrato aislado leído por `--my-task lane_4_opencode_deepseek` cambió durante la ejecución: Rocket AP-PTMP `5500/20`, SSID `FMX-LTU`, AES0; avisar PASO 1 sólo después de verificarlo. Después, el operador reconecta Lite #2 y .110 vuelve a CPE nativo `0xae08`; medir ambas estaciones y agregado durante cinco minutos cada uno. Este plan reemplaza el perfil `FMX-LTU-BENCH` y la secuencia PtP anterior.

La corrección de topología recibida del orquestador excluye RB1100 de este camino: .110 tiene cable al banco; Lite #2 se administra por aire cuando enlaza; Rocket está en LAN de la Loco. Es información del operador retransmitida, no una medición causal nuestra. Se mantiene .20 exclusivamente como transporte SSH, sin exec; Loco sólo alias RAM propio, observación autorizada y salto SSH. Sin producción ni PowerBeam .241/.242.

## Inventario: separar lectura actual de última lectura retenida

| Equipo | MAC | IP | Rol / RF / SSID | Firmware y capa de evidencia |
| --- | --- | --- | --- | --- |
| Lite #1 | PUBLIC_DEVICE_0045 | 198.18.0.63; RF 198.18.0.61 retenida | W420: AP-PTMP(Run), 5500/20, FMX-LTU, sin cifrado, cero pares | Última versión autenticada W416: afltu.v2.4.0; W420 no releyó versión |
| Rocket | PUBLIC_DEVICE_0050 en ARP; eth0 PUBLIC_DEVICE_0082 autenticada W416 | W420: 198.18.0.136 detrás de Loco | W420: configuración UNKNOWN. Última W416: AP-PTMP 5725/20 PUBLIC_TERM_0007 AES1 | Última W416: aflturocket.v2.1.0; sin autenticación W420 |
| Lite #2 | PUBLIC_DEVICE_0043, inventario | Actual UNKNOWN; no convertir prefijo sanitizado W401 en IP comprobada | Actual UNKNOWN; no observado en esta LAN no significa apagado | Última W401: afltu.v2.4.0, CPE 5500/20 FMX-LTU AES0 |

.110 respondió a las 18:08 UTC, boot `<uuid>`, uptime `274509.60 s`, txpwr -30 / powerout -4 / gain26, cuatro sensores `86/86/86/87 °C`. Se registraron sin reintroducir el corte térmico retirado en W378. No se cambió su radio antes del PASO 1.

## Transporte ejecutado y diagnóstico

El procedimiento local `STAGE3080A_session.py` mantiene una conexión activa por salto y reemplaza las conexiones invalidadas. Paramiko `set_keepalive(5)` es la implementación de keepalive usada; connect/banner/auth/channel tienen límites de 30 s. No es un recibo de OpenSSH ejecutado con `ServerAliveInterval`. Un único dueño externo limita cada operación a diez intentos; esperas 1, 2, 4, 8 y luego 15 s. Clave SSH verificada antes de credenciales, rechazo de identidad definitivo y registro de cada fracaso.

Diez aperturas IPv4 Loco→`198.18.0.136:22` vencieron antes de autenticar. LAP y Loco autenticaron inicialmente en aproximadamente 0,25 s cada uno. No se descartó la primera falla ni se presentó el TX del salto como recepción del Rocket.

La ruta Loco comprobada fue `198.18.0.93/24 dev br-lan src 198.18.0.137`; el vecino .147 apunta a PUBLIC_DEVICE_0050. `br-lan` contiene sólo `eth0`; `br-wan` conserva 198.18.0.67/24 y su gateway. No se puenteó ni recargó esa red para aparentar que una nueva IP 192.168.100.x sería directamente accesible.

Una captura pasiva de 60,140 s registró 40 paquetes y cero descartes. Todos los emisores IPv4 extraídos corresponden al Rocket .147/E0; se conserva la salida cruda y no se inventan equivalencias MAC E0/E2/E6.

Después de los diez fracasos hubo **una apertura adicional de diagnóstico**, capturada durante 34,109 s: nueve SYN hacia .147:22, cero SYN-ACK, cero respuestas ARP y 23 solicitudes del Rocket por 198.18.0.2; 45 paquetes, cero descartes. Esto confirma tráfico saliente de Loco sin respuesta observada en esa LAN. No demuestra que el daemon SSH esté caído, ni que la diferencia E0/E6 sea la causa. Los relojes de `tcpdump` son del dispositivo; el recibo del host conserva UTC y duración monotónica.

El último ensayo usa dos direcciones IPv6 link-local **candidatas EUI-64**, derivadas por separado de la MAC eth0 E6 observada y de la MAC ARP E0 observada. No se presentan como direcciones descubiertas. Diez intentos totales alternados, pin exacto del Rocket antes de autenticar y comprobación posterior board/MAC; sin setter ARP ni cambios de radio.

Los diez candidatos IPv6 agotaron el canal. A las 18:15:07 UTC el orquestador retransmitió que el operador cicló el PoE del Rocket, sin mover cables. Se esperó más de 90 s y se inició una **nueva secuencia etiquetada**, preservando las anteriores: diez intentos IPv4 adicionales, todos timeout antes de autenticar. Son 30 intentos de bootstrap/candidato y una apertura de diagnóstico; no se atribuye el PoE a esta lane ni se supone que haya recuperado el equipo.

La segunda captura, ya posterior al PoE y a esos diez intentos, duró 60,110 s: 36 paquetes, cero descartes, mismo emisor PUBLIC_DEVICE_0050 / 198.18.0.136. No se autenticó al Rocket en ninguna de las dos fases.

En .110 se verificaron además `MemAvailable: 56220 kB` y el bind tmpfs `/tmp/air_fpga` sobre `/bin/air_fpga`; las tres rutas `/bin`, `/usr/bin` y `/tmp` dieron MD5 `9be14dc7957dd1bcaceeccf24358bb65`. El binario nativo subyacente sigue sin aceptar para transición CPE: esos hashes ven el montaje vigente.

## Preparación estática y fronteras

La revisión independiente aceptó sólo transporte, observación y lecturas de layout. Conserva el preflight fallido inicial y su corrección. Los plugins de escritura siguen requiriendo corregir la verificación recursiva y la invalidación de subclases, además de su propio examen; ningún PASS estático equivale a enlace o configuración aplicada.

REA produjo `STAGE3080A_native_management_persistence_boundary.json`, `STAGE3080A_ltu_profile_transition_static.json` y `STAGE3080A_native_cpe_transition_static.json`. El procedimiento CPE nativo debe verificar el montaje exacto de air_fpga, detener el daemon, retirar sólo el bind del parche y comprobar el ejecutable nativo antes de arrancar. `start /tmp` relanzaría el parche; no se transfieren hashes ni launcher del Rocket al Lite.

La evidencia LTU retenida identifica `mtd5=cfg`; la orden directa prohíbe mtd5. No se ejecutó cfgmtd ni se leyó un mapa actual del Rocket. Una autorización genérica de persistencia y una aclaración de otro panel no sustituyen esa prohibición explícita; la gestión RAM puede avanzar cuando exista acceso. No hubo lecturas de cuerpos de configuración ni divulgación de claves en W420.

## Límite de la siguiente prueba y cierre

La propuesta `STAGE3080A_transport_mac_hypothesis.json` permite revisar un A/B de la entrada de vecino .147: E0 observado frente a E6 de eth0 retenido. No demuestra una causa ni constituye una acción ejecutada. El orquestador autorizó esa ampliación y citó una orden general del operador sobre los LTU; la orden específica W416 del usuario para la Loco compartida permite únicamente alias RAM, "nothing else". AGENTS establece que peers no relajan gates. Se necesita una ampliación específica del operador para esa mutación o recuperar el acceso por otro camino; no se escribió la entrada ARP.

La limpieza quedó verificada a las 18:26:24 UTC: mismo boot de Loco, dirección y ruta del prefijo exactamente iguales a sus preimágenes, alias propio eliminado. Se cerraron todos los transports y el proceso local salió con código 0 (`FMX_SESSION_CLOSED`). Ningún lock RF ni watchdog de cambio LTU fue armado porque nunca se llegó a autenticar al Rocket.

PASO 1, nueva IP fija, persistencia, asociación de dos estaciones y mediciones siguen sin aceptar. No se envió PASO 1 HECHO sobre preparación estática. Un gate `CONFIRMED` confirma exclusivamente los hechos del intento y la restauración, con `full_gate_pass=false` y `full_objective_achieved=false`.
