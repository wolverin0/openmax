<!-- doc-head: Wave132, prueba binaria del alias no-tx-buffer y contraste FQ/AQL
CONFIRMED: offsets y llamadas; INFERRED: alias de envios/completados entre objetos.
UNKNOWN: la equivalencia con los binarios activos del registro Stage1770A.
Analisis offline, ocho modulos, dos ejecutables, cero SSH y cero escrituras de dispositivos.
-->
<!-- /doc-head -->

# Stage1832A: contador «no tx buffer» y gestión de colas OpenWrt

## Hallazgo principal

INFERRED, external controller: en el athbox local WA/XC, los rótulos
«no tx buffer (data)» y «xmit filtered» del modo por defecto interpretan palabras
de contadores de envíos y completados de la cola de índice 1.
CONFIRMED: instrucciones, relocaciones, offsets y formato exacto de cada fragmento.
INFERRED: la identidad completa del objeto pdev y del destino ioctl entre fragmentos.
REFUTED: esos rótulos, por sí solos, prueban un 3,8 % de descarte real de tramas.
UNKNOWN: los hashes de los ejecutables y módulos activos en Stage1770A no constan
en ese receipt, por lo que la equivalencia con el binario local sigue condicionada.

## Relectura de Stage1770A

Se verificó el SHA-256 del capture original y se recalcularon ambos snapshots.
El delta de paquetes enviados es 77.314; los dos rótulos aumentan exactamente 2.975.
El cociente es 3,8479447448 %. Es un cociente entre contadores, no una tasa de pérdida validada.
La captura emplea athstats sin -ol; no se repitió ninguna consulta de campo.
No se suman ambos deltas ni se atribuyen al firmware como dos clases de pérdida.

## Corpus y método

Se analizaron ath_dev, umac y ubnt_poll_host de WA/XC airOS 8.7.25,
ath10k_core y mac80211 extraídos, y ambos athbox para resolver la presentación.
Cada evidencia conserva ruta y SHA-256; los módulos usan offsets relativos a sección.
athbox carece de tabla de secciones y se recorre mediante los segmentos PT_LOAD.
Los formatos se enlazan al sink fprintf mediante la tabla dinámica y PLT.
La herramienta fullrea produjo controles de ath_tx_start e ieee80211_tx_dequeue.
Capstone y pyelftools reconstruyen llamadas y referencias R_MIPS_26/HI16/LO16.
Un import se vincula sólo a exports ejecutables del mismo dominio WA, XC u OpenWrt.
Los saltos indirectos sin prueba permanecen UNKNOWN; un load no se confunde con una dirección.
Se distinguen entradas de función, destinos interiores y referencias a datos.

## Cadena de presentación y copia

CONFIRMED, external controller, para ambos athbox locales:

| Rótulo | Lectura VA | Stack | Offset del buffer | Formato VA |
|---|---|---|---|---|
| no tx buffer | 0x402588 | 0xf4 | 0xb4 | 0x4177dc |
| xmit filtered | 0x4025d0 | 0x11c | 0xdc | 0x4178cc |

El buffer de usuario comienza en sp+0x40. Las ramas conducen a fprintf,
con el valor en a2 y la dirección final del formato construida en el delay slot.
Las instrucciones de retorno precargan el campo siguiente; no son la lectura del rótulo actual.
Las antiguas posiciones sp+0xf8 y sp+0x120 corresponden a otros rótulos.
No se reutiliza aquella tabla histórica como prueba de estos offsets.

CONFIRMED, proprietary airMAX/LTU module: ol_txrx_stats_publish copia 0x138 bytes
desde pdev+0x128 al área sp+0x30; __copy_user publica desde sp+0x28.
La relación de offsets es: user = 8 + pdev − 0x128, condicionada a la identidad de objeto.
Los sitios de publicación y copia se localizan por relocación en cada módulo.
XC desplaza esos sitios internos cuatro bytes respecto de WA; no se transfiere el offset.

| Rótulo | Función que incrementa | Store .text | Campo pdev, q=1 |
|---|---|---|---|
| no tx buffer | ol_tx_send | 0xd3270 | 0x1d4 |
| xmit filtered | ol_tx_completion_handler | 0xd3664 | 0x1fc |

Los incrementos son de 64 bits con carry, indexados con stride de ocho bytes.
Las posiciones leídas son sus palabras bajas. UNKNOWN: el nombre semántico AC de q=1.
Esta prueba identifica un alias plausible del número presentado; no demuestra una rama de descarte
activada por agotamiento de descriptores ni identifica un incremento interno de QCA firmware.

## Contraste con mac80211 y ath10k

CONFIRMED, ath10k/mac80211: el grafo estático contiene un import de ieee80211_tx_dequeue
desde ath10k_core y un export correspondiente en mac80211.
Dentro de ieee80211_tx_dequeue se verifican llamadas a:

- ieee80211_txq_airtime_check, elegibilidad de transmisión por airtime.
- ieee80211_calc_expected_tx_airtime, cálculo de airtime esperado.
- ieee80211_sta_update_pending_airtime, contabilidad de airtime pendiente.

Los receipts conservan ramas y offsets. INFERRED: su interpretación y feedback completo;
no se reconstruyeron aquí todos los predicados de umbral o completado.
FQ expone cadenas de límites, quantum y memoria; eso no equivale al tamaño de un ring TX.
UNKNOWN: el algoritmo CoDel completo puede estar inline; la ausencia de símbolos con
ese nombre no demuestra ausencia del algoritmo ni permite importar defaults de sch_fq_codel.
UNKNOWN: nombre ath10k_core y vermagic no fijan por sí solos una revisión ath10k-ct.
No se concluye pérdida cero, superioridad de rendimiento ni compatibilidad de ABI en ejecución.

## Reconciliación de controles

CONFIRMED: se recorrieron los 571 knobs sin modificar el catálogo y 58 símbolos TX relacionados.

| Control solicitado | Catálogo | Resultado |
|---|---|---|
| ath_txbuf | ABSENT | No convertir funciones de buffers en setter |
| tx_queue_len | ABSENT | Campo Linux distinto de AQL; interfaz actual UNKNOWN |
| dev_weight | ABSENT | Presupuesto de procesamiento Linux, no tamaño de ring TX |
| aql_txq_limit | EXACT | Umbrales de airtime; calificación UNQUALIFIED |
| aql_threshold | EXACT | Presencia del nombre; handler exacto pendiente |

Las coincidencias relacionadas se conservan aparte y no crean knobs nuevos.
No se proponen valores, rangos seguros, reinicios ni cambios de firmware.

## Verificación y cinco pilares

A: ELF, relocaciones, grafo, formatos, incrementos y catálogo con hashes.
B: evidencia local retenida y preguntas abiertas; cero consultas scholar nuevas.
C: ejecución offline; cero bloques A1→B1→A2→B2 y cero watchdogs activados.
D: separación entre cociente descriptivo, alias de ABI y causalidad de pérdidas.
E: ingestión real Stage1833A en MemoryMaster, scope project:futuramax.
La suite Stage1834A incluye fixtures ELF adversariales y controles de procedencia.
El gate Stage1835A ejecuta pytest y los verificadores de cinco pilares con hashes vinculados.
Los fallos iniciales del parser y sus causas se conservan en artifacts/autoresearch/stage1830a.

## Siguiente prueba necesaria

Antes de afirmar pérdida física: enlazar hashes del binario activo con el formato correcto,
separar modo por defecto y -ol, y reconciliar el contador con sus unidades reales.
Cualquier medición de campo requerirá su autorización propia; esta wave no la ejecuta.
