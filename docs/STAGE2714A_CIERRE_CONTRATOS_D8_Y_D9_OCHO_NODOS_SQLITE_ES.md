<!-- doc-head: Wave280, ocho radios mixtos observados y bloques históricos D8 en SQLite -->
La disponibilidad descriptiva no es una mejora causal ni una migración de ocho radios a OpenWrt.
Los tiempos históricos de medición y los tiempos actuales de ingestión permanecen separados.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Cierre de contratos D8 y D9

## Alcance nuevo y explícito

La [prerregistración](../artifacts/autoresearch/stage2712a_wave280_preregistration.json)
limita la verificación a dos ciclos frescos en veinticinco minutos.
La meta exige daemon vivo, ocho radios Guarida observados en un mismo ciclo
y al menos una fila numérica descriptiva válida del mismo CPE hacia `198.18.0.132`.
Esta definición no modifica la meta histórica de ocho OpenWrt plenamente comparables.

Los [dos ciclos D9](../artifacts/autoresearch/stage2712a_d9_eight_nodes_and_delta_table_receipt.json)
cualificados contienen siete OpenWrt observados directamente y el CPE stock `.80`
con identidad airOS `WA.v8.7.25` y asociación actual al AP verificada.
No son ocho equipos OpenWrt. Una observación solo desde el AP conserva
plataforma actual desconocida y metadatos históricos por separado.
La prueba liga el identificador privado enrolado a la estación y al arranque,
uptime y ciclo del AP observado, sin publicar MAC ni apellidos.

Cada nodo se liga a su secuencia SQLite, run, ciclo y hash del payload.
El exporte congelado contiene únicamente las dieciséis filas propias de esos dos ciclos.
Los ciclos son distintos, del mismo proceso identificado, y sus secuencias aumentan.
La actualización continua posterior puede tener menos plataformas verificadas directamente;
una asociación válida sigue siendo distinta de una lectura de gestión completa.

## Tabla disponible, sin afirmar mejor rendimiento

Cada ciclo produjo ocho filas numéricas descriptivas, cuatro estadísticas por CPE.
La coincidencia de origen y destino no certifica igual carga ambiente,
algoritmo histórico de cuantiles ni contexto causal plenamente equivalente.
La bandera de comparación causal plenamente coincidente permanece falsa.

En el segundo ciclo, el CPE `.41` pasó de media histórica 9,7 ms a
10,881846 ms: aproximadamente **+12,18%**, con trece respuestas de quince.
El CPE `.223` pasó de 13,856 ms a 22,052929 ms: aproximadamente **+59,16%**,
con catorce respuestas de quince. Son aumentos de RTT, no una mejora.
Los valores históricos cargados de subida no se sustituyen por estos sondeos actuales.
Una lista no vacía con porcentajes `null` tampoco satisface la meta.

## D8: ingestión de bloques reales anteriores

El [puente D8](../artifacts/autoresearch/stage2713a_harness_sqlite_telemetry_bridge_receipt.json)
ingresó mediante el arnés dos bloques reales ya verificados de Wave276:
ocho fases originales `A1/B1/A2/B2`, conservadas con sus pines nativos.
El adaptador soporta específicamente `LTU_NATIVE_CPU_GAP_V1`, no un
contrato genérico de rendimiento RF ni persistencia automática de candidatos.

Las mediciones originales ocurrieron alrededor de 16:10–16:18 UTC;
la ingestión se efectuó a las 18:34 UTC. Las columnas guardan ambos tiempos.
El primer bloque conserva `discard` y cambio de brecha +28,146820%;
el segundo conserva `keep` y −75,308683%, con el alcance pasivo original.
Goodput y RTT no medidos permanecen `NULL`, sin rellenarlos con cero.
La guarda histórica verificada no se presenta como una guarda actualmente armada.
Repetir la ingestión conserva la misma identidad lógica y no agrega filas;
un conflicto de hash o una fase incompleta se rechaza sin sobrescribir historia.

El exporte SQLite incluye solo dos tablas propias: dos bloques y ocho fases.
La escritura es transaccional; las tablas compartidas ajenas se preservan.
El resumen LTU del monitor también es un caché histórico con fecha original,
sin SSH vivo de ese ciclo y excluido del conteo de radios Guarida.

## Verificación y trazabilidad

El [gate](../artifacts/verification/stage2717a_wave280_codex2_gate.json)
recalcula conteos, porcentajes, denominadores y procedencia histórica.
El [anexo CRLF](../artifacts/autoresearch/stage2716a_results_crlf_append_receipt.json)
liga cuatro filas nuevas a su prefijo y rango, permitiendo anexos posteriores.
La [memoria aceptada](../artifacts/autoresearch/stage2715a_memorymaster_ingest_receipt.json)
mantiene estado candidato; no constituye aceptación independiente ni aprobación productiva.
