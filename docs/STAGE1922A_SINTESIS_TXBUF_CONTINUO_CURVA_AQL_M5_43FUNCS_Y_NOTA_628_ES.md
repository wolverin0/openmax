<!-- doc-head: Wave 147 (1920A-1922A) sintesis ES: nota #628 une Waves 130 (contador 'no tx buffer' de Panel3 en 3 ventanas), 132 (el lector de athbox en offsets 0xb4/0xdc lee contadores de ENVIADOS/COMPLETADOS: no es una caida), 133 (rebind 996->997 limpio pero sin aceptacion operativa; AQL 18000 PtMP DESCARTADO), 135 (auditorias PII 1340/1340 y 237 docs), 137 (16000 contra 24000 DESCARTADO; los 5 puntos AQL no forman curva) y 139 (43 funciones M5 desensambladas y modelo de modo mixto); banda :8787 a 1536A..1925A con IDs cpe_ canonicos; SIN campeon; scholar inconcluso -->
# Reporte ejecutivo - Nota #628: contador de buffer TX, puntos AQL y 43 funciones del M5

**Wave 147 - Etapas 1920A-1922A - 2026-10-28 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se sintetizaron 12 recibos de las Waves 130, 132, 133, 135, 137 y 139 en la nota evergreen #628, el feed
del Command Center :8787 se amplio a 1536A..1925A y las tarjetas historicas ahora usan los IDs cpe_
canonicos. Titular honesto: **no hay campeon de trafico nuevo**, y el hallazgo principal es una
correccion: el "no tx buffer" de Panel3 no esta probado como caida de tramas.

## Wave 130 - contadores de Panel3 (en vivo, solo lectura)

- stage1818A: 3 ventanas de 10 s en Panel3 (3 de 6 CPEs: cpe_235, cpe_238, cpe_9).
  - Ratio "no tx buffer" sobre paquetes enviados: 1.819 %, 3.33 % y 2.735 %.
  - Se etiqueta CONTINUO con una heuristica fija (max/min <= 3.0). 0 escrituras.
- stage1819A: 3 sysctl reversibles en XC/LTU, todos restaurados; la RF no se encendio.

## Wave 132 - que lee realmente ese contador (estatica)

- stage1830A: en athbox, el lector de "no tx buffer" (offset 0xb4) y el de "xmit filtered" (0xdc) leen la
  palabra baja de los contadores de ENVIADOS (ol_tx_send) y COMPLETADOS (ol_tx_completion_handler).
  **drop_counter=false** en ambos, lo que explica por que siempre daban el mismo delta.
- La afirmacion "esas etiquetas prueban un 3.8 % de caidas reales" queda **refutada**. La equivalencia con
  el firmware en vivo sigue sin probar (no hay hash del modulo corriendo).
- stage1831A: 571 filas del catalogo; 2 controles exactos, 3 ausentes, 0 promociones SAFE_RAM.

## Wave 133 - rebind y AQL 18000 en PtMP (en vivo)

- stage1836A: interfaz nueva ifindex 996 -> 997 con un solo actor; netifd la agrego 2 veces, 0 EBUSY.
  Pero el ping inicial perdio 20 % y multicast_to_unicast quedo en 0: **sin aceptacion operativa**.
- stage1837A: umbral 3000 contra 18000 en 2 rondas: goodput -36.4 % y -58.4 %. **Descartado**.

## Wave 135 - auditorias (offline)

- stage1848A: 1340 de 1340 recibos historicos se muestran sin apellidos y sin cambios de hash; las
  fuentes conservan sus apellidos por diseno (historial inmutable).
- stage1849A: los 237 documentos del contrato quedan clasificados y todos SIN CAMBIOS (es una
  taxonomia, no una reparacion).

## Wave 137 - AQL 16000 contra 24000 y los 5 puntos

- stage1860A: un solo ABAB en el banco .241/.242.
  - TCP: A1 12.01, B1 7.32, A2 12.45, B2 19.27 Mbps; B perdio el primer par y tuvo perdida IPTV/VoIP.
  - **Descartado**.
- stage1861A: los 5 umbrales (12k, 16k, 18k, 20k, 24k) estan observados, pero salen de 4 sesiones con
  politicas distintas. **No hay curva causal, no hay curva limpia y el optimo es nulo**.

## Wave 139 - 43 funciones del M5 y modo mixto

- stage1872A (estatica): la capa 11ac-compat del M5 (43 funciones, 9208 bytes) da 2302 instrucciones,
  47 de ellas codificaciones desconocidas. Grafo de llamadas aciclico con 5 aristas internas.
- stage1873A (modelo): con 1 a 4 pares legacy, el sector mixto pierde entre 9.59 % y 26.85 % del goodput
  AC puro. El costo de la capa es un supuesto, no una medicion.

## recall-first y scholar (honestos)

recall-first: 3 de 6 consultas con aciertos (modo mixto M5 15, no tx buffer 5, curva AQL 3). scholar: UN
chequeo suave del principio de anomalia de rendimiento 802.11. El sondeo del motor funciono (P=0.90) pero
el unico candidato fue un paper fuera de tema (planificacion de sueno en IoT): unsupported, P=0.03.
Resultado **inconcluso**, no una refutacion. Nota #628 ingresada; vault en 628 notas.

## Etapa 1921A - banda 1536A..1925A, IDs canonicos y marca de vivo

- El builder pasa por el sanitizador compartido (sin modificarlo) y luego convierte cada alias a
  cpe_41, cpe_223, cpe_80 o cpe_91. En una fila de tabla con una sola IP de abonado, el alias toma el ID
  de esa IP: un mismo apellido corresponde a dos abonados de paneles distintos, y el de Panel2 queda
  como cpe_239.
- Se quitaron los nombres de pila y las celdas de nombre completo de esa tabla de inventario pasaron a
  cpe_ por IP. Quedan 0 alias y 0 apellidos del alcance en la pagina.
- 1746A y 1806A (y 1536A, 1543A) ahora figuran como en vivo: si un recibo no trae la clave, se deduce de
  su clase de evidencia LIVE (salvo DERIVED u OFFLINE).

## Limites y advertencias (honestas)

- **Sin campeon nuevo**: AQL 18000 en PtMP y 16000 contra 24000 en PtP, descartados.
- Todo porcentaje de "no tx buffer" de Panel3 es un ratio de un contador mal etiquetado hasta probar el
  hash del modulo en vivo.
- Quedan al menos 26 apariciones de 7 apellidos de OTROS abonados en tarjetas historicas, fuera del
  alcance de 4 apellidos: hace falta una lista aprobada por el operador.
- **Verificacion en navegador real: NO realizada** (Claude-in-Chrome no conecta); se verifico por CLI.

## Que sigue (decision del operador)

- Ligar el hash del umac.ko en vivo a los offsets de 1830A.
- Re-test de AQL con ventanas pareadas y una sola politica por AC.
- Corregir multicast_to_unicast del rebind antes de aceptarlo.
- Aprobar la lista de apellidos adicionales para limpiar toda la pagina.

Recibos: `stage1920a_hyperresearch_wave130_132_133_135_137_139_note628_receipt.json`,
`stage1921a_command_center_1925a_band_refresh_receipt.json`, `stage1925a_wave147_opus2_gate.json`.
