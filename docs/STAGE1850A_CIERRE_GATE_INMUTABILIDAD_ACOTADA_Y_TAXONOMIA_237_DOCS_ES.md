<!-- doc-head: Wave135 cierre local con recibos hasta1781A, matriz congelada y taxonomia documental -->
Control offline de procedencia y presentación; inventario de remediación sin editar documentos históricos.
<!-- /doc-head -->

# Stage1850A — Inmutabilidad acotada y taxonomía de 237 documentos

## Resultado y alcance

**CONFIRMED**: Stage1787A vuelve a pasar sus 26 comprobaciones con evidencia local.
La atribución corresponde al `external controller`; no se ejecutó SSH ni se tocaron dispositivos.
La modificación afecta al alcance del control, sin reescribir los recibos de investigación originales.
La aceptación física y de producción permanece **NOT_ESTABLISHED**.

## Stage1848A — Límite histórico explícito

La comparación de hashes usa exclusivamente recibos JSON numerados hasta `Stage1781A`, inclusive.
El orden compara número y sufijo: `1781A` entra; `1781B`, `1782A` y `17810A` quedan fuera.
Los documentos y el registro auxiliar sin número se excluyen de esta comprobación de inmutabilidad.
Las exclusiones llevan motivo; no se descartan silenciosamente.

| Comprobación | Resultado |
| --- | ---: |
| Recibos históricos comparados | 1340 |
| Entradas excluidas de la instantánea anterior | 1489 |
| Hashes históricos distintos o fuentes faltantes | 0 |
| Archivos históricos nuevos sin hash de referencia | 0 |
| Recibos con apellidos del alcance | 80 |
| Apariciones históricas | 436 |
| Apariciones después de sanitizar la vista | 0 |

Editar o eliminar un recibo anterior al límite sigue causando fallo.
Agregar un recibo histórico sin referencia también causa fallo; agregar uno posterior no invalida el conjunto.
Los alias `cpe_alias_01` a `cpe_alias_04` representan tokens de apellido, no identidades físicas.

## Matriz de campeones estable

Se conserva la matriz Stage1783A, con 42 IDs explícitos y 62 filas registradas.
El documento de descubrimientos debe conservar su hash completo.
Para cada TSV se exige procedencia continua de líneas, hash de cada línea y hash de los bytes originales.
Solo se admiten sufijos añadidos después de ese prefijo verificado.
La matriz se vuelve a calcular con copias temporales de los bytes verificados y debe coincidir exactamente.
Los cambios, eliminaciones o alteraciones de finales de línea dentro del prefijo siguen causando fallo.
Las filas añadidas no se aceptan como nuevos campeones ni amplían la matriz histórica.

## Stage1849A — Inventario de remediación

El conjunto se toma de las 237 violaciones registradas en Stage1782A, sin volver a seleccionar documentos.
Los 237 documentos actuales conservaban el hash de esa instantánea durante la clasificación.
Cada fila contiene razones históricas, clasificación actual y acciones propuestas; no se aplican esas acciones.

| Categoría | Histórica registrada | Clasificación actual |
| --- | ---: | ---: |
| Cierre de cabecera faltante | 232 | 232 |
| Aperturas de cabecera adicionales | 16 | 16 |
| Cabecera fuera de la primera línea | 1 | 1 |
| Sintaxis de cabecera mal formada | No evaluada | 15 |
| Exclamación en prosa | No evaluada | 1 |
| Más de 220 líneas | 0 | 0 |
| Exactamente 220 líneas | 0 | 0 |

Las categorías se superponen; sus cantidades no suman documentos únicos.
Se distingue el límite de 220 líneas porque el contrato del proyecto exige menos de 220.
La puntuación excluye comentarios HTML, código y destinos de enlaces; conserva etiquetas y texto alternativo visibles.
La taxonomía cubre el conjunto histórico de 237, no una nueva auditoría global de toda la prosa del repositorio.
**REFUTED**: esta wave haya reparado los 237 documentos; entrega un inventario, sin mutar documentos de otros carriles.

## Evidencia y límites

Los cinco pilares describen procedencia local, censo determinista, seguridad offline e ingesta real en MemoryMaster.
No se ejecutaron nueva ingeniería inversa, reactor externo, ensayos ABAB ni evaluación Pareto de hardware.
Stage1851A conserva el ID de ingesta y su lectura posterior en alcance `project:futuramax`.
La suite Stage1852A registra pruebas positivas y negativas de alcance, hashes, matriz, taxonomía y contrato del gate.
El recibo final está en `artifacts/verification/stage1853a_wave135_astra6_gate.json`.
El fallo previo de Stage1787A se conserva en `artifacts/verification/stage1848a_stage1787a_before_fix.json`.
Este informe tiene cero apellidos y cero exclamaciones fuera de los signos necesarios de los comentarios HTML.
