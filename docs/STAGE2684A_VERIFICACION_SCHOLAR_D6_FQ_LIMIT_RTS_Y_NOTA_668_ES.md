<!-- doc-head: Wave 275 (2682A-2687A) nota 668 ES: ronda scholar D6 sobre dimensionamiento fq y RTS/CTS / ACK timeout, con puente OpenAlex-arXiv -->
D6 no se cumple: 0 claims verificados por scholar de 2 pedidos, 3 hipotesis nuevas encoladas sin probar.
La literatura de enlaces largos y slot time no aparece en arXiv; Ending the Anomaly dio unsupported con dos parafrasis compuestas.
W271-H2 y W271-H3 siguen abiertas: la literatura no puede decidir el mapeo de rotulos del backport que corre en los AP.
Ningun equipo tocado; red solo para literatura. Tablero :8787 banda 1536A..2687A con Waves 269, 271 y 275, HTTP 200.
<!-- /doc-head -->
# Reporte ejecutivo - Nota #668: ronda scholar D6 sobre fq y RTS/CTS

**Wave 275 - Etapas 2682A-2687A - 2026-10-28 - sin SSH y sin tocar radios; la red se uso solo para literatura.**

## Que se hizo

Se corrio una ronda scholar acotada (como maximo 2 rondas y 25 minutos) sobre dos temas: (a) FQ-CoDel en mac80211 y el
dimensionamiento de las colas bajo agregacion 802.11ac, con el paper que nombro el operador (Ending the Anomaly, arXiv
1703.00064), y (b) RTS/CTS, slot time y ACK timeout en sectores exteriores con distancias mixtas. Se actualizo la cola del
reactor, se escribio la nota evergreen #668 y se corrieron `hyperresearch sync` e `hyperresearch index build` (rc 0).

Titular honesto: **la meta D6 no se cumple otra vez**: 0 claims verificados y 3 hipotesis encoladas. Sin campeon.

## Reglas fijadas antes de ver resultados

- Candidatos: resultados de scholar_search (arXiv), obras de OpenAlex con DOI de arXiv y el paper semilla del operador.
- Relevancia: el titulo y el abstract tienen que contener cada grupo de palabras clave del claim.
- Verificado: scholar_verify_claim (jev-1.14.0) con estado supported o partial y fuente live; los claims ya verificados
  antes no cuentan como nuevos.
- El servidor MCP de scholar no esta conectado a esta sesion: sus mismas funciones se llamaron por importacion directa.

## Resultado por claim

| Claim | Papers relevantes | Resultado |
| :--- | :--- | :--- |
| A1 planificador de airtime en el AP sin cambios en clientes | 4 | todos unsupported (el mejor 0,45, Ending the Anomaly) |
| A2 esquema de colas en la MAC que elimina bufferbloat | 1 (la semilla) | unsupported 0,15 |
| B1 ACK timeout y slot time segun la distancia | 0 | sin papers relevantes en arXiv |
| B2 RTS/CTS contra terminales ocultas | 1 | unsupported 0,37 |
| B3 slot time mas largo baja la eficiencia | 0 | sin papers relevantes en arXiv |

- Dos rondas en 172 s, 188 papers inspeccionados, 6 verificaciones; regla de corte STOP_MAX_ROUNDS.
- Un primer intento se cayo en la recuperacion de la ronda 1 antes de cualquier verificacion (error de decodificacion en
  el puente OpenAlex); se corrigio y se volvio a correr, sin descartar ningun veredicto.
- Causa probable para A1 y A2, no probada: el verificador rechaza atribuciones que el abstract no hace de la misma forma
  (el abstract le asigna la solucion de la anomalia a la solucion completa, no solo al planificador).

## W271-H2 y W271-H3

- Ningun claim quedo verificado, asi que esta ronda no confirma ni refuta esas hipotesis. Dependen de como el backport
  de mac80211 que corre en los AP rotula sus contadores fq; la auditoria estatica de la Wave 273 (2670A) encontro los
  rotulos pero no pudo resolver el mapeo porque las funciones fq estan compiladas en linea.

## Hipotesis nuevas (sin probar)

- W275-H1, solo lectura: en Panel3 .83 el contador fq_overmemory exportado sube solo en los minutos con rafagas de bajada.
- W275-H2, solo lectura: muestrear la vista aqm una vez por segundo bajo carga distingue los rotulos sin escribir nada;
  puede correr antes de la prueba W271-H2, que requiere permiso del operador.
- W275-H3, banco: subir la distancia de ACK de Panel3 para el CPE .9 ayuda a la estacion lejana pero le cuesta a las dos
  cercanas; se miden las tres en los mismos bloques.

## Etapas 2683A a 2687A

- 2683A: tablero hasta 2687 con los recibos de las Waves 269, 271 y 275 en el feed, tarjetas sin IP, sin MAC y sin nombres,
  HTTP 200, 0 apellidos en la pagina, y la tarjeta 2682A con su veredicto TARGET_NOT_MET.
- 2684A: este documento y la linea final de CURRENT_STATE.md; 2685A: MemoryMaster y filas CRLF; 2686A: pruebas; 2687A: gate.
- Curaduria del vault: las notas 664 a 668 recibieron resumen, tier y tipo de contenido; el lint ya no las marca.

## Limites y advertencias (honestas)

- **Sin campeon** y sin medicion nueva; no se abrio ningun binario.
- Verificacion en navegador real: NO realizada; se verifico por CLI con HTTP 200, banda servida y conteos de PII.

## Que sigue (decision del operador)

- Proxima ronda propuesta, no ejecutada: claims redactados como hallazgos del propio paper y texto completo de acceso
  abierto para la literatura de enlaces largos que OpenAlex encuentra fuera de arXiv, como instrumento aparte.

Recibos: `stage2682a_scholar_d6_verification_and_note668_receipt.json`, `stage2683a_command_center_1536a_2687a_refresh_receipt.json`,
`stage2685a_memorymaster_ingest_receipt.json`, `stage2687a_wave275_opus2_gate.json`.
