<!-- doc-head: Stage 3037A (W377) ES: informe antes y despues de OpenWrt para Panel1, Panel2 y Panel3 de la Guarida, sus CPE y el PtP-Colo. Antes son las estadisticas historicas de UISP (solo GET); despues es telemetry.db en solo lectura. Se compara la misma franja de 2 h del dia y solo dias habiles. La senal reportada subio en 14 de 15 radios, la latencia con la misma sonda no cambio y trafico, airtime y CCQ despues quedan UNKNOWN -->
Que cubre: como se armo el informe del operador artifacts/2026-10-30-antes-despues-openwrt.html, de donde sale cada numero y que no se puede concluir.
Estado: solo lectura. 43 GET a UISP con la lista permitida de core.Uisp y el certificado fijado; 0 escrituras en UISP; 0 accesos a equipos; telemetry.db abierta en modo ro.
Datos maquina: artifacts/autoresearch/wave377_before_after.json.
Leer cuando: antes de citar una mejora o un empeoramiento por la migracion a OpenWrt, o de planear una medicion con la misma sonda.
<!-- /doc-head -->
# Stage 3037A: antes y despues de OpenWrt (W377)

## 1. Fuentes

**Antes (airOS):** UISP `GET /devices/{id}/statistics?interval=month`.
- Series en bloques de 2 h desde el 30/09.
- Se usan solo los bloques que terminan antes del corte de cada nodo.
- Se descarto el dict de estaciones de UISP porque usa direcciones de hardware como clave.

**Despues (OpenWrt):** `openwrt_before_after_samples` de `tools/observability/telemetry.db`.
- Solo muestras con estado OBSERVED y plataforma OpenWrt.
- Desde el corte mas 1 h hasta `max_seq` (el numero exacto esta en el JSON).

**Que se excluyo:**
- **Puntos de UISP posteriores al corte:** vienen del puente de W361, que emite un esquema incompleto.
- **Eventos de UISP:** son solo cambios de firmware, no caidas.

## 2. Corte por nodo

El corte de cada nodo es el primero de estos dos momentos:
- la primera muestra OpenWrt en la BD;
- el primer evento de cambio de firmware en UISP dentro de los 5 dias previos a esa muestra.

La ventana de 5 dias descarta actualizaciones airOS a airOS anteriores (19/10 y 22/10 en tres CPE).

| Celda | Corte |
| :-- | :-- |
| Panel1 | 23/10 alrededor de las 18:40 ART, segun los eventos de UISP. El colector guarda muestras recien desde el 28/10. |
| Panel3 | 28/10 08:31 ART. |
| Panel2 y PtP-Colo | 28/10 16:41 ART. |
| cpe_200_80 | 28/10 20:02 ART. |

## 3. Comparacion justa

- **Dias:** solo dias habiles (ART) en los dos lados, porque el despues no tiene fin de semana.
- **Franjas:** cada lado se reduce a la mediana por franja ART de 2 h. Se conservan solo las franjas presentes en ambos lados y se toma la mediana entre ellas.
- **Diferencia:** se calcula solo si los dos lados miden la misma magnitud. Un lado faltante queda UNKNOWN con motivo; nunca se rellena.

## 4. Resultados (MEASURED salvo que diga UNKNOWN)

**Senal:**
- Subio en 14 de 15 radios, de +5 a +22 dB.
- Bajo en cpe_200_80 (-6,5 dB).
- En los 9 nodos de Panel2 y del PtP-Colo, la ultima muestra airOS del colector, tomada minutos antes del corte, coincide con UISP con menos de 4 dB de diferencia, asi que no es un artefacto de UISP. En Panel1 y Panel3 no hay ese control.
- Causa UNKNOWN: puede ser potencia de TX o una escala de medicion distinta. No prueba por si sola un enlace mejor, porque las CPE a mas de 2 km siguen en MCS 0 (Stage 3029A).

**Estaciones:**
- Panel2 tiene 7, Panel3 3 y el PtP 1, igual que antes.
- En Panel1 la mediana paso de 4 a 3, pero el cambio es anterior al corte: UISP ya mostraba 2 estaciones del 21 al 23/10.
- Del lado AP solo cuentan las muestras en que la sonda de pares corrio; en muchas el presupuesto la saltea.

**Latencia:**
- **Misma sonda (ICMP del colector):** solo en el AP de Panel2 (+1 ms) y en el PtP (0 y -2 ms), con una franja cada uno.
- **Resto:** antes el ping de UISP, despues el ping del colector; no se calcula diferencia.
- **A revisar:** las CPE de Panel2 dan 33,5-77 ms desde el colector. Antes UISP medía 25-30 ms con otra sonda.

**Trafico, airtime y capacidad:** hay valores de antes en UISP, pero despues son UNKNOWN porque la telemetria no guarda bytes ni airtime. CCQ es UNKNOWN en los dos lados.

**Disponibilidad:**
- Despues, el colector alcanzo al 93 % o mas de los intentos en 16 de 18 nodos.
- Los mas bajos fueron cpe_200_169 (80 %, pocas muestras por memoria) y panel1_ap (91 %).
- Antes se mide como bloques de 2 h sin ping en UISP. Son fuentes distintas y no se restan.

## 5. Contrato y limites

- **Contrato Karpathy:** target met. Demonio vivo (ultima fila de pocos segundos), 18 nodos observados y tabla con 37 diferencias medidas; el resto de las celdas tiene UNKNOWN con motivo.
- **Despues corto:** menos de 2 dias por nodo.
- **Siguiente paso util:** medir la latencia de las CPE de Panel2 con la misma sonda en la misma franja. Tambien leer la potencia de TX configurada, para explicar el salto de senal.
