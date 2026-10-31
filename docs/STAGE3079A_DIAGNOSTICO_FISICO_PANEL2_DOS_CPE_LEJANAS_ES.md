<!-- doc-head: W419; diagnostico fisico solo lectura de Panel2 y dos CPE lejanas; diagnostico fisico sin compra ni migracion -->
30min muestreados desde interfaces WDS del AP; huecos y acceso CPE incompleto declarados.
Decisiones INFERRED; no se confirma causa ni se promete ganancia de servicio.
Recibo wave419_panel2_far_cpes.json; HTML artifacts/2026-10-30-panel2-clientes-lejanos.html.
<!-- /doc-head -->
# Stage3079A: Panel2 y sus dos CPE lejanas

## Alcance y continuidad

- Produccion solo lectura; cero uploads, cargas bulk, cambios RF/configuracion/flash.
- Se leyeron los seis antecedentes pedidos; W394/W417 no habilitan ajustes nuevos.
- Historial SQLite:90payloads verificados, pero sin RF suficiente durante30min para los tres nodos.
- AP historial con estaciones vacias;169 omitidas;21 solo dos lecturas de estacion en esa ventana.
- Se capturo ventana nueva: AP cada60s por30min y CPEs cada5min; se preservan errores.
- Estaciones AP mapeadas a aliases por identidad de registro; otras cinco solo como referencia agregada.
- No se exportan apellidos, MACs ni credenciales.
- El primer gap15dB de169 no persistio: mediana final1dB; no justifica realinear solo por ese dato.

## Medidas y sentido de los datos

- AP signal/cadenas=recepcion UL; AP TX=MCS/counters DL. CPE signal/cadenas=recepcion DL.
- Histogramas MCS/NSS ponderados por snapshots; no representan todos los paquetes/intentos.
- Ruido AP: 8 reportes negativos, mediana-109.0dBm; 22 ceros no utilizables, sin imputacion.
- Ruido CPE es reporte de canal, no CINR/EVM por cadena ni certificado de ausencia de interferencia.
- Deltas solo entre mismo boot, tiempo creciente, sin reasociacion/reset; los otros intervalos se excluyen.
- retries/failed por paquete reportado no equivale a probabilidad de perdida IP.

| CPE | AP UL cadenas medianas dBm | CPE DL cadenas medianas dBm | Muestras AP/CPE | Gap UL/DL dB |
| :-- | --: | --: | --: | --: |
| cpe_200_169 | -52.5/-53.0 | UNKNOWN/UNKNOWN | 30/0 | 1.0/UNKNOWN |
| cpe_210_21 | -64.0/-62.0 | -75.0/-66.0 | 30/5 | 2.0/5.0 |

- Medianas por cadena y mediana de diferencias emparejadas son estimandos distintos; su resta puede no coincidir.
- AP intentos/errores: 32/2. Huecos de SSH no se interpretan como caidas RF.
- cpe_200_169: span AP=1844.84s, max gap=181.44s; DL directo=0 muestras.
- cpe_200_169: AP TX MCS={'0': 25, '1': 5}; AP RX MCS={'0': 27, '1': 3}; CPE TX/RX NSS={}/{}.
- cpe_210_21: span AP=1844.84s, max gap=181.44s; DL directo=5 muestras.
- cpe_210_21: AP TX MCS={'0': 25, '1': 5}; AP RX MCS={'1': 6, '0': 24}; CPE TX/RX NSS={'1': 5}/{'1': 5}.

## Presupuesto nominal, no calibracion

- FSPL=20log10(4*pi*d*f/c), d en metros, f enHz; c=299792458m/s.
- Ganancias nominales boresight LAP12016dBi y LBEGen2 23dBi; ambos modelos fuente/registro.
- RSS nominal=Ptx cacheado+Gt+Gr-FSPL; escenario sin perdidas extras, no RSS garantizado.
- Potencia real por tasa/cadena, patron fuera de eje, polarizacion y terreno no medidos.
- cpe_200_169: distancia ACK historica2100..2250m; radiografia2043m, conservada aparte.
- cpe_200_169: nominal DL-51.8..-51.2dBm vs observado DLUNKNOWN; UL AP-50.0.
- cpe_200_169: Fresnel central5.21..5.39m; no perfil topografico.
- cpe_210_21: distancia ACK historica2100..2700m; radiografia2674m, conservada aparte.
- cpe_210_21: nominal DL-53.4..-51.2dBm vs observado DL-63.0; UL AP-60.0.
- cpe_210_21: Fresnel central5.21..5.90m; no perfil topografico.

- RSS estable no prueba LOS libre; alturas, azimut, vegetacion y geometria siguen UNKNOWN.
- La clase0 observada no prueba causa: el timeout base de firmware es desconocido y no se cambio nada.

## Decision fisica por CPE

### cpe_200_169: SIN CAMBIO FISICO AHORA
- Conservar equipo y orientacion: UL equilibrado respecto de referencias, DL directo desconocido; servicio aun afectado.
- Causa no confirmada: otras CPE logran MCS6..8 con gaps similares.
- Ganancia real de Mbps/latencia/perdida: UNKNOWN.
- Si solo la rama debil alcanza la fuerte sin perjudicarla: UL combinado ideal al gap mediano0.5dB; DL UNKNOWN por falta de lectura directa.
- Es escenario ideal de suma de potencia, no promesa de recuperar todo el gap en RSS combinado.
- No comprar mayor ganancia ni mover a otro sector sin evidencia adicional.
- La recomendacion no autoriza intervencion fisica; no se ejecuto realineacion.

### cpe_210_21: REALINEAR de forma diagnostica
- Conservar equipo actual; revisar orientacion, polarizacion y montaje en mantenimiento autorizado.
- Causa no confirmada: otras CPE logran MCS6..8 con gaps similares.
- Ganancia real de Mbps/latencia/perdida: UNKNOWN.
- Si solo la rama debil alcanza la fuerte sin perjudicarla: UL combinado ideal al gap mediano0.9dB; DL ideal al gap mediano1.8dB.
- Es escenario ideal de suma de potencia, no promesa de recuperar todo el gap en RSS combinado.
- No comprar mayor ganancia ni mover a otro sector sin evidencia adicional.
- La recomendacion no autoriza intervencion fisica; no se ejecuto realineacion.

## Alternativas y aceptacion posterior

- LR26dBi vsGen2 23: diferencia nominal+3dB, sujeta a potencia/EIRP, alineacion y patron.
- Mayor ganancia no corrige por si misma temporizacion, obstruccion o sector incorrecto.
- Mover de sector: falta RSSI candidato/azimut; no hay base para elegirlo.
- AP: conservar antena/orientacion; no se establece averia comun de cadena ni se arriesgan cinco enlaces.
- Si luego se autoriza, comparar ambas ramas, NSS/MCS y servicio antes/despues; conservar/restaurar baseline sin mejora.

## Fuentes

- [LAP12016dBi](https://dl.ui.com/qsg/MX/LAP-120/LAP-120_MX.html), [Gen2 23dBi](https://techspecs.ui.com/uisp/wireless/litebeam-5ac), [LR26dBi](https://techspecs.ui.com/uisp/wireless/lbe-5ac-lr?s=us).
- [FSPL ITUP.525](https://www.itu.int/rec/R-REC-P.525-5-202411-I/en); [Fresnel LINKPlanner](https://lp.cambiumnetworks.com/doc/profile.html).
- Distancias: W369 y radiografia24/10, estimaciones ACK/historicas, no coordenadas medidas.
- Gate confirma auditoria y trazabilidad; no reparacion fisica ni mejora de QoE.
