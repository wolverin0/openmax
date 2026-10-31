<!-- doc-head: W468 inventario histórico local y límites de calibración meteorológica -->
Informe descriptivo sin acceso de red ni cambios en radios o bases de datos.
Sin clima histórico emparejado: UNKNOWN y todos los umbrales UNSET.
<!-- /doc-head -->

# Calibración histórica: disponibilidad y clima

Estado: **UNKNOWN_INSUFFICIENT_MATCHED_WEATHER**.
Este trabajo implementa el inventario solicitado por la sección 3 de
[STAGE3138A](STAGE3138A_GATE_DE_CLIMA_PARA_OPERACIONES_ES.md).
No habilita ni calibra una política operativa.

## Evidencia local ejecutada

Constructor: `tools/ops/weather_gate/history_report.py`.
Salida: `tools/ops/weather_gate/wave468_historical_availability.json`.
SHA256 de esa salida:
`2e045c6ca1121c69ab43b8f752be328510957192dabd5a944ba29583ff95ccd2`.

La base `tools/observability/telemetry.db` se abrió mediante URI `mode=ro`,
`PRAGMA query_only=ON` y una transacción de lectura consistente.
Los conteos describen ese snapshot; el recolector puede seguir agregando filas.

| Fuente | Cobertura UTC del snapshot | Cantidad |
|---|---|---:|
| `openwrt_before_after_samples` | 2026-10-19 13:09:50.497427 a 2026-10-31 16:06:14.385880 | 49.272 filas |
| `fmx_sidecar_e2e_minute` | 2026-10-30 14:27 a 2026-10-31 16:05 | 206.125 filas válidas |

Rango SQLite del recolector: `seq 1..49272`; 40.486 filas tienen estado
`OBSERVED`. Esto describe disponibilidad del recolector, no continuidad RF.
Las sondas suman 2.477.277 paquetes enviados y 2.274.182 recibidos:
3.734 filas sin respuesta y 36.551 con alguna pérdida. No son eventos
independientes de caída: hay distintos nodos, orígenes y ventanas.

No se proporcionó un mapeo físico revisado. Todas las filas quedan sin sitio
asignado; no se deduce que un CPE esté físicamente en la torre de su AP.
La salida no exporta filas individuales, nombres de clientes, MAC ni coordenadas.

## Fuentes meteorológicas y Dude

La búsqueda local acotada no encontró un archivo de observaciones
meteorológicas históricas ni un historial Dude utilizable.
Se clasificaron explícitamente dos candidatos locales sin convertirlos en clima:

| Archivo | Clasificación | SHA256 |
|---|---|---|
| `artifacts/autoresearch/stage3138a_weather_gate.json` | Estudio, no historial | `74abcd59f9f2a0a138fbeb2f1c545eb886276e9a19187e09b6ef2aa6677ce34c` |
| `artifacts/canary_panel1_guarida/panel1_outage_confirmation_20261020T133042Z.json` | Recibo aislado, no serie Dude | `1dfe916fd762b977ba40c85d126bff39ab8b4ec913355694596843c18c35b1d5` |

Resultado: **0 observaciones meteorológicas, 0 registros Dude y 0 soportes
meteorológicos emparejados**. La ausencia en esta búsqueda no demuestra que
no exista una fuente externa: ese acceso está fuera del alcance.

## Contrato de entrada y unión

`--site-map` acepta un objeto JSON explícito `node_id -> nombre de sitio físico`.
Los nombres son etiquetas de sitio; no se aceptan IP, MAC o coordenadas.
El constructor es independiente de las coordenadas y de la política del controlador.

`--cache` acepta archivos JSON con `schema` y `records`:

- `fmx.weather_history.v1`: cada registro exige `site`, `source`,
  `kind=historical_observation`, fecha con zona horaria y valores en `weather`.
  Campos admitidos: `gust_mps`, `precipitation_mm`, `lightning_count` y
  `nearest_lightning_km`. Deben ser números finitos no negativos.
- `fmx.dude_history.v1`: `site`, `source`, `kind=historical_availability`,
  `observed_at` con zona horaria y `status=up|down`.

Estos esquemas son entradas del informe; no afirman que un adaptador existente
ya produzca esos formatos. No se aceptan pronósticos como observaciones.

Una observación puntual se une sólo al mismo instante UTC y sitio.
Un intervalo explícito `start_utc,end_utc` usa `[inicio,fin)`; no se inventa
una tolerancia temporal. Duplicados, fechas inválidas y soportes superpuestos
quedan rechazados o marcados ambiguos. Los orígenes de sonda se mantienen separados.

Cada soporte climático agrega enviados/recibidos de sus sondas antes de
calcular pérdida. Pearson requiere al menos tres soportes distintos por
sitio, origen y variable; varianza nula produce valor desconocido.
Una correlación descriptiva no prueba causa ni calibra un umbral.

## Límites y siguientes datos necesarios

Todos los límites permanecen **UNSET**: radio de rayos, ventana de rayos,
ráfaga y precipitación. No se calibran con datos ausentes.
Cambios de `boot_id` son candidatos de reinicio, sin prueba de que fueran
imprevistos. ICMP sin respuesta tampoco prueba falla RF ni causa meteorológica.

Para continuar hacen falta un mapeo físico revisado, historial observado con
procedencia y tiempos verificables, y etiquetas independientes de incidentes
planificados/no planificados. El controlador y los adaptadores siguen fuera
del alcance de este constructor.

## Verificación local

`node ../wezbridge/scripts/heavy-slot.cjs run --label wave468_history -- python -m pytest tools/ops/weather_gate/test_history_report.py -q -p no:cacheprovider`

Resultado fresco: **23 passed**, rc 0. Las pruebas usan SQLite desechable:
uniones por sitio/tiempo, pérdida, Dude separado, historial escaso/ausente,
fechas inválidas, privacidad, lectura sin mutaciones y preservación de integridad.
No se ejecutó ninguna conexión de red ni comando sobre radios.
