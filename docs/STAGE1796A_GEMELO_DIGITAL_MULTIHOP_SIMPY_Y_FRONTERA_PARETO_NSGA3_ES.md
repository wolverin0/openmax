<!-- doc-head: Wave126, gemelo de colas SimPy y aproximacion Pareto de cuatro objetivos -->
Ejecucion local reproducible; las predicciones no validan capacidades RF ni autorizan cambios.
Inventario historico de 32 CPEs, tres paneles y supuestos de conexion explicitados.
<!-- /doc-head -->

# Stage1796A: gemelo multihop y frontera Pareto

## Alcance y evidencia

CONFIRMED: ejecucion de SimPy y pymoo instalados, sin SSH ni escrituras de radios.
INFERRED: respuestas del modelo y capacidades supuestas. Atribucion: external controller.
UNKNOWN: rendimiento de hardware, convergencia global, interferencia e interop de campo.
La integracion serial Colo → Principal/Almafuerte → Guarida es un escenario supuesto.
No existe en esta wave una prueba de que todo el trafico real recorra esa ruta.
El inventario conserva exactamente 32 miembros; no suma nuevamente sus paneles.
Se usan exclusivamente identificadores `cpe_001` a `cpe_032` para abonados.
Los nombres, MAC e IP de abonados no aparecen en los resultados.

## Topologia, capacidad y carga

| Recurso | Configuracion del escenario | Naturaleza |
|---|---|---|
| PtP-Colo .62 ↔ .54 | 5200 MHz, VHT40/VHT80, 180/360 Mbps | Supuesto de capacidad |
| Principal → Almafuerte | 300 Mbps | Supuesto |
| Almafuerte → Guarida | 170 Mbps | Supuesto |
| Paneles 1/2/3 | 4/22/6 CPEs, medios compartidos independientes | Membresia historica |
| Enlace final | Minimo entre capacidad DL y Ethernet del inventario | Datos mixtos CONFIRMED/INFERRED |

Dos miembros inactivos tienen capacidad original cero, preservada en el recibo.
Para someter los 32 a carga se imputan 30 Mbps RF y 100 Mbps Ethernet en esos casos.
Estas imputaciones estan etiquetadas INFERRED, aunque la observacion original cero fuera CONFIRMED.
La carga incluye Bulk cerrado con trenes de 12 KB, IPTV de 4 Mbps y VoIP de 64 kbps.
IPTV usa paquetes de 1316 B: una copia por salto de backbone y 32 replicas unicast en los paneles.
VoIP usa 160 B cada 20 ms y prioridad EF/VO. VI precede a BE; el servicio no es preemptivo.
El goodput agregado suma entregas de aplicacion, incluidas replicas IPTV por destinatario.
Por ello no debe compararse directamente con los bytes transmitidos por el backbone.

## Parametros y semantica

Stage1663A, segunda ronda B1/B2: coverage_class=1, VO300/600, VI750/1500 y BE1200/2400 us.
El recibo original no promovio un campeon; esos valores son un escenario de referencia.
AQL se aproxima mediante admision de airtime por par y AC, con colas de software de 64 entradas.
La aproximacion permite un tren mayor al limite y no reproduce exactamente el driver ni su umbral global.
TXOP determina cuantos microsegundos puede ocupar una oportunidad; TXOP cero permite una trama.
Se asumen 60 us de overhead mas 3 us por coverage_class y un costo de reintentos no calibrado.
El Bulk incorpora pacing AIMD y 2 ms de ACK supuesto; no emula un stack TCP ni contencion de ACK inversos.
Tres `cpe_` se desconectan a 0,5 s. `ban_time=1200` significa 1200 ms.
La prohibicion vence a 1,7 s; se agregan 25–75 ms de handshake supuesto.
La prueba observa la reasociacion dentro de las ventanas de entrenamiento y evaluacion.

## Diseno experimental

Stage1794A ejecuta A1→B1→A2→B2 para VHT40/VHT80 con tres semillas independientes.
Cada ventana dura 3 s, parte con colas vacias y termina en el intervalo semiabierto [0,T).
A2 y B2 son replays exactos; no se cuentan como replicas estadisticas independientes adicionales.
Los trabajos incompletos se registran separados de los descartes y de las entregas.
La perdida IPTV usada como objetivo es conservadora: descartes mas incompletos al cierre, sobre ofrecidos.
No representa exclusivamente perdida fisica ni una estimacion de regimen estacionario.
El jitter p99 es la variacion absoluta del retardo entre paquetes VoIP consecutivos recibidos.
Los pares separados por perdida se excluyen; la perdida VoIP se informa aparte.
Jain usa airtime servido por cada uno de los 32 CPEs, incluso el servicio parcial al cierre.
No mide igualdad de bytes ni compara recursos con una unica capacidad comun.

## Resultados de referencia del modelo

| Ancho | Goodput de aplicacion Mbps | VoIP jitter p99 ms | IPTV no entregado al cierre | Jain airtime |
|---|---:|---:|---:|---:|
| VHT40 | 163,955 | 1,898 | 33,365 % | 0,5754 |
| VHT80 | 166,187 | 1,670 | 33,355 % | 0,5702 |

Son promedios entre semillas de metricas por corrida; no son intervalos de confianza.
La mejora limitada de VHT80 es compatible con los cuellos posteriores impuestos por el escenario.
La perdida IPTV elevada impide interpretar estos puntos como una recomendacion de servicio.

## Optimizacion de cuatro objetivos

NSGA-II y NSGA-III minimizan [-goodput/100, jitter/100, perdida IPTV, -Jain].
Variables discretas: escala AQL 0,5/1/2; cobertura 0/1/2; BE TXOP 0/1504/3008 us;
VI TXOP 1504/3008/6016 us; ancho Colo 40/80 MHz. Espacio completo: 162 configuraciones.
Cada algoritmo usa dos semillas, poblacion 20 y tres generaciones: 60 evaluaciones por corrida.
Los duplicados cuentan en el presupuesto; una cache reutiliza simulaciones identicas.
Cada candidato se evalua con dos semillas comunes y ventanas de 2 s.
La frontera incluye todos los no dominados del archivo de entrenamiento, no solo la ultima poblacion.
Una semilla reservada y ventana de 3 s evalua la frontera una vez fijada, sin seleccionar sobre ella.
El recibo1795A conserva candidatos, signos, escalas, procedencia y trazas de evaluacion.
Resultado: 240 evaluaciones, 76 configuraciones unicas de 162 posibles y 29 puntos no dominados.
La frontera de entrenamiento abarca 123,694–166,682 Mbps, jitter p99 de 0,824–1,973 ms,
IPTV no entregado de 34,484–35,461 % y Jain de 0,5636–0,5760; los extremos no son un unico punto.
Los 29 puntos recibieron evaluacion con la semilla reservada; no se elige un ganador.
La frontera es una aproximacion finita; no acredita optimo global ni estabilidad estadistica.

## Verificacion y continuidad

La suite1798A comprueba conservacion, privacidad, limites, semillas, prioridades y dominancia.
Incluye la regresion de airtime parcial y controles negativos contra recibos adulterados.
El gate1799A liga fuentes y entradas por SHA256, ejecuta pytest y exige readback de MemoryMaster.
El pase estructural de cinco pilares no equivale a cinco investigaciones nuevas.
A/B reutilizan catalogo y procedencia local Wave104, sin nuevos analisis binarios ni llamadas Scholar/Jev.
C aplica el limite offline y el protocolo del modelo; D ejecuta simulacion y Pareto; E registra la ingestion real.
La revision independiente es acotada al codigo de productores y conserva los limites del modelo.
El historial mantiene el fallo inicial por capacidades cero y las ejecuciones canceladas por la correccion de airtime.
No hay campeon promovido, despliegue, flash ni aceptacion fisica.

## Fuentes locales y software

- `artifacts/guarida_32cpe_radiography_20261024.json` y recibo Stage1663A: entradas versionadas por hash.
- `artifacts/autoresearch/wave104/research/provenance_final.json`: procedencia historica reutilizada.
- `orchestration/autoresearch/firmware_knob_candidates.json`: IDs de AQL, cobertura y TXOP.
- SimPy 4.1.2, pymoo 0.6.2 y NumPy 1.26.4, instalados localmente.
- Skills locales SimPy/pymoo, K-Dense, Scientific Agent Skills, DOI 10.48550/arXiv.2609.00065.
La ultima referencia procede de sus metadatos incluidos; no se consulto la publicacion en esta tarea offline.
