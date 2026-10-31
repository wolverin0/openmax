<!-- doc-head: STAGE3138A gate de clima para operaciones (reinicio nocturno, firmware, canarios). Estudio de escritorio 2026-10-31, solo lectura web; sin tocar equipos ni codigo. Etiquetas CONFIRMED/INFERRED/UNKNOWN. Datos estructurados: artifacts/autoresearch/stage3138a_weather_gate.json -->
<!-- /doc-head -->

# STAGE 3138A: gate de clima para operaciones

Pregunta: no iniciar (o abortar) una operacion de mantenimiento si hay tormenta, lluvia fuerte, rayos o viento fuerte ahora o en las proximas horas en el sitio. OpenWISP no trae nada de clima (verificado por el operador), asi que es un pre-chequeo propio. Zona: Pergamino, Buenos Aires.
Limite del estudio: las paginas del SMN respondieron 402/503 al fetch automatico, por eso los endpoints del SMN quedan UNKNOWN hasta probarlos desde el servidor real.

## 0. Hecho de arquitectura que condiciona todo (CONFIRMED en repo)
- El reinicio nocturno corre por cron EN el equipo: `tools/ops/fmx_night_restart/planner.py` (`cron_lines`) instala `fmx-night-restart scheduled --apply` semanal y `fault --apply` cada minuto. El runtime `runtime/fmx-night-restart` ya emite `NO_ACTION <razon>` (ej. `OUTSIDE_SLOT`, `POLICY_DISABLED`).
- Un equipo en un sitio sin enlace no puede consultar una API de clima. El gate NO debe ser una llamada de red desde el equipo: debe ser un archivo "hold" que el controlador escribe antes (con vencimiento) y que el runtime lee. Ver seccion 5.

## 1. Fuentes locales (Argentina)
| Fuente | Que da | Acceso / fuente | Estado |
|---|---|---|---|
| SMN alertas (SAT) | Alertas por zona, colores verde/amarillo/naranja/rojo, hasta 72 h; se actualizan a las 6 y 18 h y extra si hace falta; "avisos a corto plazo" (ACP) hasta 3 h para tormentas severas, granizo y lluvia intensa detectados por radar | [Cadena 3](https://www.cadena3.com/noticia/sociedad/como-funciona-el-nuevo-sistema-de-alerta-temprana-del-servicio-meteorologico_434373), [Chequeado](https://chequeado.com/el-explicador/que-significan-las-alertas-meteorologicas-amarillas-naranjas-y-rojas/) | Contenido CONFIRMED (prensa); API oficial documentada UNKNOWN |
| SMN `ws.smn.gob.ar` | JSON de pronostico y alertas que usan clientes comunitarios | [py-smn](https://github.com/manucabral/py-smn) usa `https://ws.smn.gob.ar`; [py-ha-smn](https://pypi.org/project/py-ha-smn/) (beta, ene-2026): alertas, alertas de corto plazo y calor, token JWT y `location_id` por lat/lon | No documentado oficialmente, con token, sin garantia. Mi fetch a `ws.smn.gob.ar/alerts/type/AL` dio 503. INFERRED fragil |
| SMN descarga de datos | Datos publicos "actualizados cada dia" segun [py-smn](https://github.com/manucabral/py-smn) | `https://www.smn.gob.ar/descarga-de-datos` (fetch dio 402) | Sirve para historico, no tiempo real. Terminos UNKNOWN |
| Radar Pergamino | Radar doppler dual-pol de la red SINARAME; cobertura ~240 km por radar ([fuente](https://core.ac.uk/download/487445147.pdf)). Un registro externo lo lista como SMN con pagina `smn.gob.ar/radar/` ([WRD](https://wrd.mgm.gov.tr/Radar/Details/dTNhSjYvRCtrWm9zQ0pSRm9veG9wdz09)) | Datos crudos solo del archivo RELAMPAGO nov-2018/ene-2019 ([UCAR](https://data.ucar.edu/dataset/inta-pergamino-per-radar-data)) | Acceso publico actual a imagenes/productos, intervalo, API y terminos: UNKNOWN. Pedir acceso formal a SMN/INTA; no depender de scraping |
| INTA SIGA | Red de estaciones automaticas, datos cada ~10 min en tablas/mapas ([fuente](https://www.infocampo.com.ar/?p=224418)) | Portal `siga2.inta.gov.ar` | API/descarga y estacion en Pergamino: UNKNOWN. Util como verdad-terreno de lluvia/viento, no como pronostico |

Tampoco verifique si el SMN publica un feed CAP: UNKNOWN. Si existe, es la mejor fuente y reemplaza a `ws.smn.gob.ar`.

## 2. APIs globales (gratis y pagas)
| API | Cobertura Pergamino y campos | Gratis | Terminos que importan |
|---|---|---|---|
| [Open-Meteo](https://open-meteo.com/en/docs) | Global. Horario: precipitacion, `wind_gusts_10m`, `weather_code` (95/96/97/99 tormenta), CAPE. 15 min nativo SOLO Europa central y Norteamerica; en el resto es horario interpolado. `lightning_potential` solo en 15 min, o sea no util en Argentina | 600/min, 5000/h, 10000/dia, sin SLA ([pricing](https://open-meteo.com/en/pricing)) | Gratis es NO comercial; un WISP que cobra servicio es uso comercial, requiere plan pago ([terms](https://open-meteo.com/en/terms)). Standard 29 USD/mes por 1M llamadas segun su [Substack](https://openmeteo.substack.com/p/api-subscriptions-for-commercial) (fuentes secundarias discrepan; la pagina oficial no mostro numeros). CC BY 4.0 |
| [MET Norway](https://api.met.no/doc/TermsOfService) | Pronostico global; campo de probabilidad de tormenta: INFERRED, no verificado | Sin clave; User-Agent real obligatorio, respetar `Expires`, cache, coordenadas a 4 decimales, <20 req/s | CC BY 4.0; sin seccion de uso comercial; no usar nombre/logo Yr. Solo modelo, sin nowcast ni rayos |
| [OpenWeatherMap One Call](https://openweathermap.org/full-price) | Minutely 1 h, alertas gubernamentales; 1000 llamadas/dia gratis, luego 0.0012 GBP c/u | Si | Uso comercial permitido con atribucion visible. Si el feed de alertas incluye las del SMN: UNKNOWN. Rayos no documentados en lo que lei |
| [Tomorrow.io](https://www.tomorrow.io/weather-api/) | Rayos es capa Premium (Enterprise); capas core en el plan gratis, limites no publicados | Plan free existe | Terminos comerciales del free UNKNOWN. Rayos no gratis (INFERRED) |
| [Visual Crossing](https://www.visualcrossing.com/weather-data-editions) | Pronostico 15 dias; eventos (granizo, tornado); rayos y alertas no mencionados | Tope diario de registros (1000/dia sin confirmar) | Tilde de uso comercial en el plan gratis (CONFIRMED en la tabla) |
| [Meteomatics](https://www.meteomatics.com/en/weather-api/) | Global; rayos solo como fuente de observacion; modelos 1 km solo Europa/EEUU | Sin prueba API visible | A cotizacion |
| Rayos pagos: [Xweather (GLD360)](https://www.xweather.com/lightning-api), Earth Networks | Rayos globales por API; Xweather ofrece prueba de 30 dias | No | Precio UNKNOWN, cotizar |
| [Blitzortung](https://forum.blitzortung.org/showthread.php?pid=17617) | Red voluntaria | Sin API publica | Segun foro (2018, secundario): uso reservado a participantes, sin fines comerciales y prohibido para sistemas de alerta de tormenta. DESCARTADO |
| [NOAA GOES GLM](https://registry.opendata.aws/noaa-goes/) | GOES-19 (GOES-East) mide rayos totales sobre el hemisferio occidental ([NOAA](https://www.nesdis.noaa.gov/news/noaa-releases-initial-imagery-the-goes-19-lightning-mapper)); NetCDF GLM-L2-LCFA en bucket publico `noaa-goes19`, cadencia ~20 s y latencia 30-60 s segun [terceros](https://lightning-web.pages.dev/blog/goes-19-glm-lightning-detection/) | Gratis, sin cuenta | Abierto "para cualquier uso", pide atribucion y no implicar aval de NOAA. Cobertura de Pergamino: INFERRED (no verificada). Requiere codigo propio para leer NetCDF |

Conclusion: el nowcast real en Argentina sale de radar SMN y rayos GLM; Open-Meteo, MET Norway y OWM son pronostico de modelo (horas), no nowcast de celdas.

## 3. Diseno: senales y origen de cada umbral
No invento umbrales. Senales candidatas y de donde sale el valor:
| Senal | Fuente | Origen del umbral |
|---|---|---|
| Alerta SMN vigente en la zona (tormenta, lluvia, viento) o ACP | SMN | Nivel de color. "Amarillo = no iniciar, naranja = abortar" es decision del operador; el SMN define amarillo/naranja/rojo como Informate/Preparate/Seguir indicaciones ([Chequeado](https://chequeado.com/el-explicador/que-significan-las-alertas-meteorologicas-amarillas-naranjas-y-rojas/)) |
| Rayo a menos de X km en los ultimos N min | GLM | X y N: calibrar con historial propio (abajo). Sin valor oficial hallado |
| Probabilidad de tormenta o codigo 95+ en las proximas H horas | Open-Meteo o MET | H sale de la duracion real de la operacion (reinicio por sitio, ventana de rollout) |
| Rafaga y precipitacion horaria | Open-Meteo / estacion SIGA | Calibrar; los umbrales de las alertas SMN por zona: UNKNOWN, buscar su tabla |

Calibracion con datos propios (propuesta, no ejecutada): cruzar caidas de enlace y reinicios inesperados por sitio (antes/despues en `tools/observability/telemetry.db`, alertas del Dude) contra clima historico del mismo dia/hora (archivo de Open-Meteo y GLM historico en el mismo bucket NOAA). Medir por senal cuanto sube la tasa de caida con rayo a menos de X km, rafaga mayor a Y, etc., y fijar el corte con la tasa observada. Hasta tener esa curva, el gate usa solo el criterio categorico oficial (alerta SMN) mas "rayo reciente cerca = no".
Coordenadas: una por sitio (Guarida, Edificio Principal, Almafuerte, Colo, etc.) en un archivo de config de sitios; solo nombres de sitio, sin datos de clientes.

## 4. Casos limite (fail-closed o fail-open lo elige el operador)
- API caida o lenta: timeout corto y tres estados explicitos CLEAR, HOLD, UNKNOWN. Politica por tipo de operacion: el reinicio semanal podria ser fail-open (perder uno cuesta poco), el firmware masivo fail-closed (un corte a mitad de flasheo cuesta mucho). Decision del operador; siempre registrar UNKNOWN.
- Datos viejos: guardar `fetched_at` y `valid_until`; mas viejo que un limite elegido por el operador es UNKNOWN. Respetar `Expires` de MET.
- Reloj y zona: gate en UTC. El repo ya tiene la trampa (`cron_lines` falla con `UNVERIFIED_CRON_TIMEZONE`; ART es -180). Comparar con el reloj del servidor, no del equipo.
- Pronostico que oscila durante un rollout largo: re-chequear ANTES de cada nodo, no una vez al inicio; histeresis (salir de HOLD exige N lecturas limpias seguidas, N a elegir). Si un HOLD aborta el nodo en curso, lo define el operador.
- Tormenta local fuera del pronostico: por eso rayo GLM y radar son la senal real; el modelo solo avisa con horas.
- Radar sin servicio: UNKNOWN para esa senal, nunca "despejado".
- Rate limits y costos: pocos sitios con chequeo cada 5-10 min caben de sobra en cualquier plan gratis; MET pide offsets aleatorios y cache; OWM 1000/dia.
- Claves: en el vault, nunca en el repo ni en el equipo; el equipo solo ve el archivo hold.
- Enlace del sitio caido: el gate corre en el controlador (con internet), no en el equipo.
- Licencias: Open-Meteo gratis no vale para este uso (comercial); atribucion CC BY 4.0 donde se muestre.

## 5. Recomendacion (la opcion simple y robusta)
Un servicio chico `weather_gate` en el controlador que escribe por sitio un estado `CLEAR|HOLD|UNKNOWN` con `valid_until`, combinando:
1. Oficial: alertas y ACP del SMN para la zona (si no hay feed estable, respaldo manual: el operador fija HOLD).
2. Rayos: NOAA GLM (gratis, "cualquier uso") dentro de un radio R de cada sitio; R y ventana se calibran (seccion 3).
3. Pronostico horario para tormenta/rafaga en las proximas H horas: Open-Meteo plan comercial (mas simple) o MET Norway gratis con atribucion y User-Agent propio (sin codigo de tormenta verificado).
Integracion: (a) rollouts y canarios llaman `weather_gate check --site X` antes de cada nodo; HOLD, o UNKNOWN segun politica, no avanza. (b) Reinicio nocturno: el controlador sube `/etc/fmx_weather_hold` (estado + `valid_until`) unas horas antes del slot y otra vez cerca; el runtime lo lee y emite `NO_ACTION WEATHER_HOLD`; si falta o esta vencido aplica la politica del operador. El modo `fault` (cada minuto) es correctivo y no deberia bloquearse por clima salvo decision del operador. (c) Piloto OpenWISP firmware-upgrader: misma llamada previa a cada lote.
Que probar: (1) estados con respuestas simuladas (alerta, rayo, 503, dato viejo, JSON invalido); (2) UTC contra ART; (3) re-chequeo entre nodos con cambio de estado a mitad; (4) hold ausente, vencido o corrupto en el runtime (extender `test_night_restart.py`); (5) backtest contra el historial real de caidas.

## 6. Tres preguntas abiertas
1. Existe un feed estable de alertas SMN para uso automatico (endpoint o CAP, terminos, token)? Hoy solo hay clientes comunitarios no oficiales; probar desde el servidor y consultar al SMN.
2. Fail-open o fail-closed por tipo de operacion cuando el gate no sabe (UNKNOWN)? Decision del operador.
3. Hay acceso real al radar de Pergamino (SMN/INTA) y a la estacion SIGA, o alcanza GLM mas pronostico? Y: se paga Open-Meteo comercial o se usa MET Norway?
