<!-- doc-head: Wave124 auditoria historica sin escritura, sanitizacion de vista y matriz de cuatro dominios -->
Evidencia local offline; conserva hallazgos, ambiguedades y limites de aceptacion.
<!-- /doc-head -->

# Stage1784A — Auditoría integral de PII, documentos y campeones

## Alcance y atribución

**CONFIRMED**: auditoría local de Wave124, Stages1782A..1787A, atribuida al `external controller`.
Se revisan los recibos `artifacts/autoresearch/stage*.json` y los documentos `docs/STAGE*.md`.
El inventario excluye las salidas de esta wave para evitar hashes autorreferenciales; el gate las valida aparte.
No se ejecutaron SSH, mediciones RF, cambios de configuración, despliegues ni pruebas en dispositivos.
Los hashes identifican una instantánea de trabajo compartido, no una aceptación de producción.

## Auditoría histórica

| Medida | Resultado de la instantánea Stage1782A |
| --- | ---: |
| Archivos examinados | 2829 |
| Recibos JSON | 1357 |
| Documentos Markdown | 1472 |
| Archivos con apellidos del alcance | 164 |
| Apariciones antes de sanitizar | 899 |
| Documentos fuera del contrato | 237 |
| JSON inválidos / errores de lectura | 0 / 0 |
| Colisiones de claves al sanitizar | 0 |
| Apariciones después de sanitizar en memoria | 0 |

El contrato documental exige menos de 220 líneas, una cabecera inicial y su cierre emparejado.
Este informe tiene cero exclamaciones fuera de los dos signos requeridos por los comentarios HTML.
El recibo conserva ruta, SHA256, conteos por identificador, líneas afectadas y resultado por archivo.
**CONFIRMED**: las fuentes leídas conservaron sus hashes durante el escaneo.
**REFUTED**: el corpus histórico completo cumple actualmente el contrato de privacidad y documentación.
Los hallazgos preexistentes permanecen documentados; esta wave no reescribe ni corrige los originales.

## Adaptador de presentación

`tools/sanitize_dashboard_pii.py` ofrece `sanitize_text`, `sanitize_value` y `render_json`.
Devuelve copias y sustituye claves y valores, con variantes de mayúsculas y acentos.
Los alias de presentación son `cpe_alias_01`, `cpe_alias_02`, `cpe_alias_03` y `cpe_alias_04`.
Estos alias identifican tokens de apellido; no atribuyen una identidad a una dirección o CPE física.
Una colisión de claves bloquea el renderizado para evitar perder valores históricos.
La CLI imprime la vista a stdout; no tiene una opción de escritura sobre el origen.
La cobertura de cero apellidos se limita a las cuatro familias solicitadas.
Es seudonimización: no elimina IPs, otras identidades ni toda forma posible de PII.
La integración y el despliegue del adaptador en todos los dashboards existentes quedan **UNKNOWN**.

## Matriz de cuatro dominios

Se preservan 62 filas de los dos TSV, con ruta, número de línea y hash verificables.
Los 42 IDs FMX-DISC explícitos se inventariaron por separado de las 17 entradas numeradas sin ID explícito.
Los dos IDs calificados con etapa y sufijo se conservan distintos de los IDs globales de igual número.
No se asignan IDs nuevos a esas entradas históricas.
Hay 17 etiquetas `keep`, 23 `discard` y ninguna `exploratory`; las otras 22 filas también se conservan.

| Dominio solicitado | keep | exploratory | discard |
| --- | ---: | ---: | ---: |
| OpenWrt PtMP `.20/.200.41` y Guarida `.84` | 10 | 0 | 12 |
| OpenWrt PtP `.241/.242` y PtP-Colo `.62/.54` | 5 | 0 | 3 |
| airMAX AC WA/XC `.198/.253` | 11 | 0 | 12 |
| AF-LTU `.110` | 10 | 0 | 3 |

Las categorías se superponen cuando una fila menciona varios dominios; no deben sumarse como ensayos únicos.
Los dominios se infieren de texto y metadatos, sin interpretar columnas numéricas de métricas como IPs.
Quedan 20 filas sin dominio resuelto y 42 IDs explícitos sin enlace demostrable a una fila de resultados.
Los enlaces admitidos son IDs explícitos o referencias de etapa inequívocas; los casos ambiguos se conservan.
**CONFIRMED** se limita a presencia y procedencia de registros; la validación física queda **UNKNOWN**.
Una etiqueta `keep` no demuestra campeón desplegado, mejora causal ni promoción autorizada.

## Cinco pilares y evidencia de cierre

A: procedencia local y hashes; no se ejecutó nueva ingeniería inversa.
B: cruce de fuentes locales; no se consultó literatura ni se activó el reactor externo.
C: límite offline y cero SSH; no se ejercitó ABAB ni un watchdog físico.
D: censo determinista y regresiones; no se infiere significancia estadística ni frontera Pareto física.
E: ingesta explícita en MemoryMaster, alcance `project:futuramax`, con recibo Stage1785A.
El gate de cinco pilares comprueba el contrato del recibo; no certifica ejecución física de los cinco pilares.
Las pruebas Stage1786A y sus salidas se registran en `artifacts/verification/stage1786a_pytest_receipt.json`.
El cierre local se determina en `artifacts/verification/stage1787a_wave124_astra6_gate.json`.
El gate exige hashes vigentes, salidas sanitizadas, contrato del informe, ingesta comprobada y pytest sin fallos.
La aceptación de producción permanece **NOT_ESTABLISHED**.
