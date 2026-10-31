<!-- doc-head: W468 gate de clima local, fuentes gratuitas y permiso fail-closed W466 -->
Implementacion y pruebas offline; diagnostico SMN desde PUBLIC_TERM_0003 y muestra publica NOAA.
Produccion inactiva, umbrales sin calibrar, ningun cambio en radios o runtime de reinicio.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Gate meteorologico para mantenimiento

## Contrato entregado

`python -m tools.ops.weather_gate check --site SITE --json`

Devuelve exactamente `site`, `state`, `valid_until`, `reasons`.
Exit 0 significa CLEAR; HOLD y UNKNOWN devuelven un codigo distinto de cero.
Cada llamada vuelve a leer el archivo del sitio. Un archivo ausente, corrupto,
con campos repetidos, de otro sitio, con fecha futura o vencida produce UNKNOWN.
Una excepcion del proveedor nunca equivale a ausencia de tormenta.
El coordinador y el controlador deben compartir `FMX_WEATHER_STATE_DIR`
o pasar `--state-dir`; el ejemplo systemd utiliza `/var/lib/fmx-weather/state`.

El controlador local escribe el estado atomicamente por sitio. Incluye una ejecucion
`--once` y modo persistente explicito, con una unidad systemd de ejemplo no instalada.
El ejemplo local conserva todos los sitios UNKNOWN: faltan entradas verificadas,
coordenadas revisadas, politicas de frescura y calibracion numerica.
Las coordenadas se configuran por nombre de sitio, nunca por abonado.

## Cambio de integracion aprobado

Los mensajes `<orca-id>` y `<orca-id>` reemplazan la propuesta original
de escribir `/etc/fmx_weather_hold` por un coordinador host-side de W466.
Ese coordinador consulta el gate antes de cada nodo y entrega permisos de un solo uso.
Sin permiso el nodo no reinicia. Este carril no modifica el runtime ni instala archivos
en radios. El modo fault sigue deshabilitado y fuera de esta integracion;
su politica meteorologica requiere una decision cuando se habilite.

El harness offline consulta HOLD sin ejecutar el runtime, comprueba que no hay cambios,
y solo tras CLEAR ejecuta el runtime real en su raiz desechable `--test-only`.
El marcador de reinicio pertenece al fixture: no es un reinicio de hardware.
No se tomo el LiteBeam porque no habia liberacion vigente de W457 confirmada;
el mandato permite este harness como alternativa.

## Fuentes y limites observados

Solo se usan las tres fuentes gratuitas elegidas por el operador.

| Fuente | Evidencia fresca W468 | Consecuencia |
| --- | --- | --- |
| SMN | 3 GET desde PUBLIC_TERM_0003 a `ws.smn.gob.ar/alerts/type/AL`: 3 HTTP 503 | Feed estable no demostrado |
| Portal SMN alternativo | 3 GET desde PUBLIC_TERM_0003: 3 URLError | No se infiere nivel verde |
| NOAA GOES-19 GLM | NetCDF publico real de 223999 bytes, con SHA-256 retenido | Parser nativo comprobable, sin decision meteorologica del sitio |
| MET Norway | Parser y cliente con fixtures de JSON/cache/HTTP | Sin coordenadas verificadas, no se afirma clima real del sitio |

El diagnostico SMN hizo seis GET acotados y ninguna escritura remota.
Se guardan codigos, tiempos y hashes, sin cuerpos de autenticacion ni secretos.
No se declara estabilidad por tres respuestas ni se inventa un esquema de API SMN.
El intercambio local para un export oficial verificado esta explicitamente separado
de una API nativa. Zona, vigencia, completitud y procedencia deben verificarse.
El [borrador para consultar al SMN](STAGE3139A_CONSULTA_SMN_BORRADOR_ES.md) queda sin enviar.

La politica de mantenimiento retiene ante amarillo, naranja o rojo del SMN;
es una decision conservadora del operador, no una instruccion oficial de reinicio.
Los niveles y recomendaciones oficiales se publican en
[SAT del SMN](https://ws2.smn.gob.ar/alertas).

El parser NOAA lee NetCDF, unidades CF, fechas de cobertura y flags de calidad.
Los flags no validos no se convierten silenciosamente en cero rayos.
Una sola muestra de 20 segundos no prueba una ventana completa ni ausencia de rayos
en un sitio. La agregacion valida continuidad y calcula distancias solo con
coordenadas explicitas. Sin ventana/radio calibrados o frescura configurada: UNKNOWN.
Fuente: [NOAA Open Data](https://registry.opendata.aws/noaa-goes/) y
[guia tecnica GLM](https://www.ospo.noaa.gov/resources/documents/PUG/GS%20Series%20416-R-PUG-L2%20Plus-0349%20Vol%205%20v3.0%20final.pdf).

MET exige User-Agent con contacto real, cache segun Expires y consultas condicionales.
El cliente conserva esas restricciones y limita reintentos/lecturas; las variables
ausentes, como rafagas fuera del area de cobertura del modelo, quedan desconocidas.
La previsibilidad durante toda la operacion debe quedar cubierta explicitamente.
Se conserva atribucion a MET Norway; licencia y condiciones:
[terminos oficiales](https://docs.api.met.no/doc/TermsOfService) y
[modelo de datos](https://docs.api.met.no/doc/locationforecast/datamodel.html).
El permiso almacenado tambien vence a mas tardar en HTTP Expires: la regresion
se reprodujo primero y se corrigio sin borrar su JUnit fallido.

## Pruebas ejecutadas

La ejecucion final bajo heavy-slot de `tools/ops/weather_gate` y la suite original
`tools/ops/fmx_night_restart/test_night_restart.py` da 201 PASS, cero fallos.
Incluye CLEAR/HOLD/UNKNOWN, API fallida, datos viejos, vencimiento/corrupcion del
archivo, cambio entre nodos, coordenadas/ventanas ausentes, cache/304, NetCDF
truncado/corrupto/unsigned y el limite de HTTP Expires. JUnit: `pytest_closed.xml`.
El harness usa un marcador desechable y no constituye evidencia fisica.

## Calibracion e implantacion pendientes

El reporte historico usa SQLite `mode=ro`, `query_only` y snapshot transaccional.
Hay disponibilidad medida, pero no historial meteorologico ni Dude emparejable,
ni mapa fisico revisado para atribuir cada sonda a un sitio.
Resultado: UNKNOWN_INSUFFICIENT_MATCHED_WEATHER. Radio de rayos, ventana,
rafaga y precipitacion siguen UNSET; ningun valor del fixture es politica operativa.
Ver [reporte historico](STAGE3139A_HISTORICAL_CALIBRATION_ES.md).

Para promover hacen falta: endpoint/condiciones SMN confirmados, sitios y zonas
revisados, frescura explicita, historial emparejado para calibrar y aprobacion del
operador. Hasta entonces, produccion no se activa y el estado operativo es UNKNOWN.
No se instalaron servicios ni se cambiaron cron, RF, flash, PoE o el Orchestrator.

El recibo principal y el gate separan implementacion, fixtures, diagnostico de servidor,
fuentes reales, estado UNKNOWN y ausencia de aceptacion de produccion.
