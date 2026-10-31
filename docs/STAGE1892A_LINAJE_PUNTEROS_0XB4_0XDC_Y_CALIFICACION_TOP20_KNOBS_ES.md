<!-- doc-head: Wave142, linaje MIPS local y backlog de veinte controles
CONFIRMED: descriptores, copias, allocation y campos de objetos en WA/XC.
UNKNOWN: dispatch completo de instancias y equivalencia con binarios activos.
Cuarenta ELF congelados; cero SSH, cero cambios de dispositivos, cero promociones SAFE_RAM.
-->
<!-- /doc-head -->

# Stage1892A: linaje de contadores y calificacion de controles

## Resultado y alcance

CONFIRMED, external controller: se reconstruyeron los segmentos locales que faltaban
entre descriptor de athbox, copia kernel y publicacion de estadisticas de UMAC.
Cada ventana contiene bytes, SHA-256, instrucciones, relocaciones e identidad de fuente.
Se verificaron por separado WA y XC contra los hashes de Stage1830A.
INFERRED: el enlace global entre todas las instancias de objetos durante ejecucion.
UNKNOWN: dispatch del kernel, algunos callbacks y hashes activos de Stage1770A.
Por ello este trabajo no prueba una ruta real de descarte del 3,8 % de tramas.

## Descriptor y copias

CONFIRMED, Linux/userspace y proprietary airMAX/LTU module:

| Paso | Evidencia local |
|---|---|
| Base de argumento ioctl | athbox 0x4018ec: s7 = sp + 0x25d0 |
| Descriptor | sp + 0x25f8: capacidad 0x1210; puntero en +4 = sp + 0x40 |
| Enlace al descriptor | 0x4024b0: [s7 + 0x10] = direccion del descriptor |
| Operacion | 0x402494/0x4024ac: ioctl 0x89f0, argumento s7 |
| Copia de entrada | UMAC carga [arg1 + 0x10], copia 8 bytes a kernel_sp + 0x338 |
| Copia de salida | destino = [kernel_sp + 0x33c], fuente = kernel_sp + 0x28, tamano 0x310 |

La rama por defecto evita la reasignacion de s7 usada por -ol.
La rutina comprueba longitud y puntero no nulos; no demuestra longitud >= 0x310.
El descriptor concreto de athbox proporciona capacidad suficiente.
No se transfiere este resultado al modo -ol ni a otro ejecutable.

## Allocation, publicacion y offsets

CONFIRMED, proprietary airMAX/LTU module: __ol_ath_attach conserva el retorno N de
alloc_netdev_mq y forma private = N + 0x2c0. Pasa private a ol_ath_attach,
que conserva el pdev devuelto por ol_txrx_pdev_attach en private + 0x1df80.
El handler ioctl carga pdev desde N + 0x1e240: es el mismo campo por aritmetica exacta.
La tabla .rodata+0xe31c se instala en N+0xb4; el slot +0x2c apunta al handler
0xbcbe0 WA / 0xbcbe4 XC. El kernel que invoca esa tabla no esta en el corpus.

ol_txrx_stats_publish copia pdev+0x128 al stack+0x30; la copia a usuario parte de stack+0x28.
La relacion comprobada es offset_usuario = 8 + offset_pdev - 0x128.

| Rotulo athstats | Offset usuario | Campo pdev para indice 1 | Incremento |
|---|---|---|---|
| no tx buffer | 0xb4 | 0x1d4, palabra baja | ol_tx_send 0xd3270 |
| xmit filtered | 0xdc | 0x1fc, palabra baja | ol_tx_completion_handler 0xd3664 |

Ambos incrementos son uint64 con carry y stride de ocho bytes.
Los nombres de funciones y la estructura indican envio/completado;
no se reconstruyo una condicion de agotamiento de buffers que explique esos rotulos.
UNKNOWN: el significado AC del indice 1. El cociente historico entre contadores
no se convierte en probabilidad de perdida ni permite sumar ambos rotulos como descartes.

## VAP, vdev, HTT y limites de instancia

CONFIRMED: el constructor VAP obtiene pdev del campo private+0x1df80;
ol_txrx_vdev_attach lo guarda en vdev+0 y ol_tx_send lo lee de su argumento vdev+0.
El argumento pdev de htt_attach se guarda en htt+4; htt_t2h_msg_handler lo carga
y lo entrega a ol_tx_completion_handler, que lo conserva como base del contador.
htt_htc_attach registra callback y contexto HTT en el request de HTCConnectService.
UNKNOWN: falta reconstruir el dispatch completo que entrega las mismas instancias
al constructor VAP, a cada llamada send y al callback HTC. Los campos por si solos
no prueban esa identidad global ni el comportamiento de un equipo activo.

ath_dev conserva su propio argumento en ath_tx_start y modifica campos +0x5b4/+0x5bc.
Es un objeto diferente del pdev de UMAC. No se igualan estructuras por offsets parecidos.
El init de UMAC registra drivers de bus; registro no equivale a instancia activa.
La atribucion de estas rutas es proprietary airMAX/LTU module, no QCA firmware.

## Top veinte del backlog

CONFIRMED, external controller: Stage1891A recorre los 40 ELF del corpus congelado,
verifica todos sus hashes y selecciona 20 candidatos unicos de la union publicada de 30.
Respeta el orden Pareto ordinal de Stage1789A; no estima ganancias fisicas nuevas.

| Resultado | Candidatos | Limite |
|---|---:|---|
| Puntero a handler en ctl_table | 4 | Registro de la raiz y semantica de escritura pendientes |
| Descriptor WEXT | 3 | Descriptor de argumentos no prueba dispatch al handler |
| LTU | 10 | ame_dev.ko exacto ausente del corpus congelado |
| Metadata de politica | 2 | No es interfaz kernel |
| Extension CT | 1 | Fuente sin binding al binario exacto del objetivo |

Todos siguen UNQUALIFIED, deshabilitados y sin valor propuesto ni ejecucion automatica.
No se modifico el catalogo de 571 controles. Promociones SAFE_RAM: cero.
Se requieren identidad activa, registro completo, limites, readback y rollback comprobados
antes de calificar un control para una campaña independiente de hardware.

## Cinco pilares y verificacion

A: ELF/MIPS, bytes, relocaciones y catalogo. B: preguntas abiertas, sin nuevas consultas externas.
C: A1-B1-A2-B2 y watchdog conservados como protocolo; cero bloques de hardware ejecutados.
D: analisis descriptivo y falsacion de equivalencias; sin ganancias simuladas presentadas como medidas.
E: ingestion real Stage1893A en project:futuramax; los receipts se regeneran con su identificador.
La suite Stage1894A verifica alteraciones de instrucciones, tablas, fuentes y ventanas.
El gate Stage1895A conserva JUnit, replay determinista, hashes y validacion de cinco pilares.
Un PASS local verifica los resultados y sus limites; no cierra los gaps de dispatch o hardware.

## Evidencia

- [Linaje Stage1890A](../artifacts/autoresearch/stage1890a_ath_dev_umac_0xb4_0xdc_struct_lineage_re_receipt.json)
- [Backlog Stage1891A](../artifacts/autoresearch/stage1891a_safe_ram_qualification_backlog_top20_receipt.json)
- [Memoria Stage1893A](../artifacts/autoresearch/stage1893a_wave142_memorymaster_ingest.json)
- [Gate Stage1895A](../artifacts/verification/stage1895a_wave142_astra7_gate.json)
