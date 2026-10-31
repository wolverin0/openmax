<!-- doc-head: Stage 3107A (W447) ES: regresion de Panel2 despues de la migracion; causa 1 CONFIRMED: dos CPE lejanas en coverage class 0 fallaban todos los frames y ocupaban el aire de la celda; canario A/A x3 + ABAB con la regla de W448 hasheada (AP 2700 m clase 6, cpe_200_169 2250 m clase 5, cpe_210_21 2700 m clase 6): GO, las 7 CPE bajaron su p95 core; persistido con backup y vuelta atras -->
Que cubre: causas, canario, veredicto, persistencia, monitoreo de 30 min y que queda.
Estado: 3_done. Veredicto GO (calculado sobre el log con la misma regla; el controlador aborto por un error de calculo despues de B2).
Datos maquina: artifacts/autoresearch/wave447_panel2_regression.json.
Leer cuando: antes de tocar fq/AQL en Panel2 o de repetir el cambio en otra celda.
<!-- /doc-head -->
# Stage 3107A: regresion de Panel2 (W447)

## 1. Causas (paso 1-2, solo lectura)

- **Causa 1 (CONFIRMED por el canario):** dos CPE lejanas en clase 0, falla por paquete cerca de 1,0 a MCS 0-1. Ocupaban el aire de la celda compartida.
- **Causa 2:** fq_overmemory de 5,7 M en 48 h. Probable consecuencia de la causa 1.
- **Causa 3:** fq_quantum, AQL y backlog distintos de Panel1. Menor.
- **Valores de Panel1:** sin PASS de banco exacto (W372 NO_GO).

## 2. Canario (regla de W448, hash c753a1b52f1b..., registrada antes de AA1)

- **Distancias:** maximo medido por airOS en W431. AP 2700 m (clase 6), cpe_200_169 2250 m (clase 5), cpe_210_21 2700 m (clase 6).
- **Ventanas:** AA1-AA3, A1, B1, A2 y B2 de 10 min, con watchdog en los 3 nodos. Antes, ensayo del watchdog en clase 0 en los tres.

| CPE | Rol | p95 core A ms | p95 core B1 / B2 | p95 core 30 min despues | falla/paquete max A/A | falla/paquete B1 / B2 |
| :-- | :-- | :-- | :-- | :-- | --: | :-- |
| cpe_200_169 | lejana | 98,39-551,16 | 21,96 / 26,42 | 36,06 | 0,9997 | 0,0013 / 0,0005 |
| cpe_210_21 | lejana | 177,77-349,98 | 24,03 / 20,16 | 20,43 | 1,0002 | 0,0004 / 0,0003 |
| cpe_200_213 | cercana | 68,56-116,78 | 26,08 / 19,34 | 32,09 | 0,0134 | 0,0017 / 0,0 |
| cpe_210_166 | cercana | 49,42-86,97 | 31,86 / 39,71 | 27,08 | 0,0001 | 0,0 / 0,0001 |
| cpe_210_239 | cercana | 65,76-74,69 | 22,31 / 23,18 | 18,91 | 0,0 | 0,0 / 0,0 |
| cpe_200_183 | cercana | 68,39-97,61 | 34,53 / 23,89 | 21,2 | 0,0156 | 0,001 / 0,0 |
| cpe_210_83 | cercana | 71,63-90,8 | 54,34 / 46,72 | 23,79 | 0,0 | 0,0 / 0,0 |

- **Lejanas:** pasaron de 1,0 a 0,0003-0,0013 de falla por paquete. Su p95 core bajo de 98-551 a 20-26 ms. La subida tambien se arreglo (de 0,995-1,0 a 0,002-0,006).
- **Cercanas:** las 5 bajaron su p95 core en B1 y B2. cpe_200_213 y cpe_200_183 bajaron sus fallas unas 10 veces.

## 3. Veredicto y aborto

- **Veredicto: GO.** Las dos lejanas cumplen (a) en B1 y B2; ninguna cercana cumple (b) o (c).
- **Aborto despues de B2:** el controlador aborto al calcular el test exacto. `comb(n, i) * p**i` desborda el float con miles de fallas. Fue un error mio, no una guarda.
  - El watchdog restauro clase 0 en los 3 nodos, con boot ids y dmesg limpios.
  - El veredicto se recalculo con la misma regla y la misma funcion sobre las 7 ventanas del log, con el binomial en espacio logaritmico.

## 4. Persistencia y despues

- **Persistido (03:50-03:59Z)** con uci y commit, backup en /etc/fmx_rollback/wireless.pre_w447, vuelta atras con /etc/fmx_rollback/w447_rollback.sh, watchdog durante el cambio y readback. Sin wifi reload.
- **Orden:** AP, cpe_210_21 y cpe_200_169. cpe_200_169 no respondia SSH en clase 0.
- **Reinicio de cpe_200_169:** reinicio cerca de las 03:57Z, sin escritura previa; actor UNKNOWN, probable watchdog residente (INFERRED). Su backup es la configuracion original.
- **Subida 60 s despues:** cpe_200_169 en 0,0029 de falla por paquete, cpe_210_21 en 0.
- **30 min despues (04:00-04:30Z):** dentro de lo esperado: lejanas bajo el minimo A/A y cercanas no peor que su maximo.
- **Pendiente:** fq/AQL de Panel2 (causas 2-3) se reevalua con la causa 1 resuelta: leer fq_overmemory en 24 h antes de proponer banco.
