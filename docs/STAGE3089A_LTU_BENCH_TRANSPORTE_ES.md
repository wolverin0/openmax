<!-- doc-head: W429: pruebas de acceso al Rocket LTU con autoridad ampliada, sin configuración aplicada -->
ARP E6 instalado por netlink con ACK y readback: diez conexiones SSH fallaron; entrada eliminada y verificada.
Gateway RAM .1 con origen .250: cinco timeouts; ensayo cerrado al recibir instrucción de probar desde .1.
Origen .1 real: ping 3/0, tres rondas SSH22 y TCP443 sin conexión. Limpieza completa de red verificada.
PASO 1 y enlaces/mediciones siguen pendientes; gate CONFIRMED sólo para hechos, artefactos y restauración.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# W429 — Acceso al Rocket LTU: pruebas y resultado

## Objetivo y autorización

La orden del operador de 30/10/2026 18:35:49 UTC, evento `<uuid>`, autoriza la red del banco: ARP, alias y rutas en Loco, y configuración de los tres LTU para Rocket AP `5500/20 FMX-LTU` AES0 con ambos Lite como CPE. Sustituye la limitación previa de la Loco a un solo alias. Se mantuvieron excluidos producción, mtd0/mtd1, ART/calibración y firmware flash. No se solicitó autoridad adicional.

W420 quedó cerrado antes de empezar; W429 usa recibos separados. `.20` se utilizó como salto SSH sin exec. La Loco se fijó por clave SSH, modelo y boot antes de actuar. Todo archivo remoto creado se escribió en `/tmp` confirmado tmpfs. No se instaló paquete ni se recargó la red/radio.

## Pruebas realizadas

| Prueba | Condición comprobada | Resultado |
| --- | --- | --- |
| Primer setter ARP | BusyBox `ip neigh` sólo admite show/flush; applet arp ausente | `replace` rechazado, rc85; no creó entrada. Fallo conservado; preimagen vacía verificada al cerrar |
| Helper específico | ELF32 MIPS32r2 big-endian, o32 soft-float, musl estático, 43112 B | SHA256 `ea5c93b81ced311811753ef3c4d3c05e579851d3e710e9e2289d4daf609d1542`; self-tests host/QEMU y nativo, hash remoto coincidente |
| Vecino E6 | Sólo .147/br-lan, `PUBLIC_DEVICE_0082 PERMANENT`; kernel ACK y readback | 10 timeouts de canal SSH antes de autenticar. Eliminación por helper ACK y readback vacío |
| Gateway local | Diez segundos pasivos: 7 pedidos Rocket por .1, ninguna respuesta; br-lan sólo eth0 | Alias .1 con label propio y TTL600; ruta conservó src .250. Cinco timeouts SSH; no prueba desde .1 todavía |
| Origen .1 | Único alias del prefijo, TTL600, `ip route get .147` confirmó src .1 | Ping 3 enviados/0 recibidos; 3 rondas de SSH22 y TCP443, todos timeout antes de conectar |

El helper sólo permite `set`, `delete` y `--selftest` para .147/br-lan/E6. El self-test retorna antes de abrir un socket. En ejecución verifica ACK de kernel, secuencia y errno, con recepción acotada a 3 s. El recibo de compilación distingue self-tests sin envío de la actuación netlink real del banco.

La primera revisión detectó una carrera entre expiración y apply. Se preservó y corrigió antes de aplicar ARP: apply y restore comparten lock; dentro se validan boot, nonce, estado y plazo. El guard independiente de 600 s reintenta únicamente lock ocupado. La revisión de reparación y la del binario/plugin son independientes del implementador.

Las sesiones se mantuvieron por salto durante cada fase. Se reemplazaron transports invalidados. La fase con gateway .1 pero src .250 se interrumpió después de cinco fallos por la instrucción del orquestador `<orca-id>`: probar **desde .1**, HTTPS/ping y terminar en diez minutos si no hay respuesta. El proceso local salió con `KeyboardInterrupt`, rc1; su `finally` restauró direcciones y ruta. Se conserva el rc1 separado de la aceptación de limpieza.

La segunda sesión usó src .1 desde 19:04:55 UTC y cerró a las 19:13:08 UTC, dentro de diez minutos. Las tres rondas HTTPS fallaron abriendo TCP443: no hubo handshake TLS, HTTP ni identidad del servidor obtenida por ese camino. No se enviaron credenciales a TLS. Los límites de 30 s son por etapa SSH/canal, no un límite total de todas las etapas.

## Estado local observado y límites de diagnóstico

Loco `br-lan/eth0` estaba en forwarding (3), carrier1, operstate up, **10 Mbit/s full duplex**. En la lectura: tx_packets1895, rx_packets11848, tx_errors0, tx_dropped0 y rx_errors0. Son contadores puntuales, no una medida de pérdidas de abonados ni prueba de entrega al Rocket. La velocidad difiere de 100 Mbit/s retenidos en W401; no se atribuye una causa al cable por esa diferencia.

Se observó sólo tabla nft `inet fw4`; output policy accept y `output_lan → accept_to_lan` acepta br-lan. No se cambió firewall, qdisc, VLAN, WAN ni negociación. `tc` estaba ausente y `ip -s link` no era compatible: se conservaron esos errores y se usó sysfs para los campos anteriores. No se declara una auditoría exhaustiva del datapath ni causa establecida.

## Inventario y configuración

| Equipo | Identidad / dirección | Capa de evidencia |
| --- | --- | --- |
| Rocket LTU | PUBLIC_DEVICE_0050, 198.18.0.136 observados por ARP; eth0 PUBLIC_DEVICE_0082 retenida de W416 | Cero autenticaciones W429; firmware, boot y RF actuales UNKNOWN. Última lectura W416: aflturocket.v2.1.0, AP5725/20 PUBLIC_TERM_0007 AES1 |
| Lite #1 | PUBLIC_DEVICE_0045, 198.18.0.63 | Sin acceso W429; último W420 AP5500/20 FMX-LTU, cero pares. No se lo cambió a CPE antes del PASO1 |
| Lite #2 | PUBLIC_DEVICE_0043, IP actual UNKNOWN | Sin acceso W429; no asumir presencia o apagado ni reconexión física realizada |

No se aplicó IP fija, SSID, AES, rol ni persistencia a un LTU. No se quitó una clave ni se capturó un cuerpo de configuración del Rocket. La configuración actual no puede inferirse de los scripts preparados. **No se envió PASO 1 HECHO.** No hubo iperf ni ventanas de throughput/latencia; métricas y aceptación de dos estaciones permanecen null/false.

## Restauración y siguiente paso

Ambas fases verificaron el mismo boot Loco `<uuid>`, direcciones iniciales exactamente restauradas y ausencia de la ruta temporal 198.18.0.93/24. Se retiraron .250 y ambos alias .1. El vecino E6 y su intento previo nunca aplicado figuran RESTORED; la eliminación del E6 tiene ACK y readback. La segunda sesión cerró rc0. Las carpetas de diagnóstico permanecen sólo en RAM; los guards recibieron estado RESTORED, sin lease de red pendiente.

Se reportó al orquestador que puede realizar el cambio físico corto que ofreció: revisar cable, inyector PoE o puerto/conectar el Rocket directamente al banco con elementos probados y entregar un endpoint observable. Es una dependencia de acceso, no una solicitud de más autoridad. Con el Rocket accesible, la orden de configuración y medición continúa vigente.

El gate `CONFIRMED` confirma estas observaciones y restauración, con `full_gate_pass=false` y `full_objective_achieved=false`. No certifica el objetivo LTU, seguridad física de una configuración ni mejora Karpathy.
