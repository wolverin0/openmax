<!-- doc-head: Stage 3108A (W448) ES: repeticion del canario de distancia de Panel3 con regla nueva predeclarada y hasheada antes de AA1 (opcion A del orquestador); GO: la CPE lejana paso de fallar todo a casi nada en B1 y B2 y su p95 core bajo de 117-188 a 33-40 ms, sin dano en las cercanas; clase 7 queda 24 h en RAM con watchdog -->
Que cubre: regla, calibracion del test de fallas, ventanas, veredicto y pasos siguientes.
Estado: PERSISTED (hold de 24 h cortado y reemplazado por persistencia por decision del orquestador). Veredicto GO. W433 corrida 3 sigue registrado como NO_GO.
Datos maquina: artifacts/autoresearch/wave448_panel3_distance_rerun.json (regla, sha256 1f670af6bc5e..., preregistro 2026-10-31T00:41Z, AA1 2026-10-31T00:43Z).
Leer cuando: antes de persistir la clase 7 en Panel3 o de llevarla a Panel2 (W447).
<!-- /doc-head -->
# Stage 3108A: canario de distancia en Panel3, segunda regla (W448)

## 1. Regla

- **Cambio:** el mismo de W433, `iw phy phy0 set distance 2850` (clase 7) en el AP de Panel3 y cpe_210_9. Solo RAM, mismo watchdog, mismas guardas.
- **Banda:** minimo y maximo de AA1-AA3, frescas de esta corrida.
- **(a) Beneficio:** falla por paquete y p95 core de la lejana por debajo del minimo A/A, en B1 y en B2.
- **(b) Dano en p95 o perdida:** una cercana queda danada si su p95 core, o su perdida core, supera su maximo A/A en B1 y en B2.
- **(c) Dano en fallas:** hace falta que su tasa de fallas supere su maximo A/A en B1 y en B2, y ademas que el test binomial exacto con exposicion de p menor a 0,005.
- **Por que (c) pide las dos cosas:** con datos de W433, el test solo marca dano en ventanas sin cambio (A1 contra AA p = 1,2e-4; AA1 contra AA2 y AA3 p = 1,9e-12).
- **Registro:** regla hasheada en el receipt antes de AA1; el controlador registro el mismo hash en el preflight.

## 2. Ventanas (falla por paquete / p95 core ms / perdida core %)

| Ventana | Clase | cpe_210_9 | cpe_210_235 | cpe_210_238 |
| :-- | --: | :-- | :-- | :-- |
| AA1 | 0 | 1,0002 / 133,38 / 14,29 | 0,0 / 54,94 / 0,0 | 0,0002 / 61,31 / 0,0 |
| AA2 | 0 | 1,0 / 116,94 / 5,56 | 0,0 / 44,61 / 1,85 | 0,0002 / 45,03 / 1,85 |
| AA3 | 0 | 0,9998 / 168,91 / 3,7 | 0,0 / 37,21 / 0,0 | 0,0001 / 57,12 / 0,0 |
| A1 | 0 | 1,0 / 153,0 / 16,67 | 0,0 / 39,88 / 0,0 | 0,0001 / 36,62 / 0,0 |
| B1 | 7 | 0,0001 / 33,48 / 0,0 | 0,0 / 34,06 / 1,85 | 0,0 / 21,08 / 0,0 |
| A2 | 0 | 0,9999 / 187,53 / 7,41 | 0,0 / 44,2 / 0,0 | 0,0002 / 43,64 / 0,0 |
| B2 | 7 | 0,0001 / 39,71 / 0,0 | 0,0 / 29,24 / 1,85 | 0,0 / 28,03 / 1,85 |

## 3. Veredicto: GO

- **(a) Lejana:** banda minima 0,9998 de falla y 116,9 ms de p95. B1 dio 0,0001 y 33,5 ms; B2, 0,0001 y 39,7 ms. MCS 0 a 7; perdida core de 4-17 % a 0. Entrego de 6 a 9 veces mas paquetes.
- **(b) Cercanas:** el p95 bajo en las dos (cpe_210_238 de 37-61 a 21-28 ms; cpe_210_235 de 37-55 a 29-34 ms). La perdida quedo dentro de la banda.
- **(c) Fallas:** las dos cercanas en 0 fallas en B1 y B2 (cpe_210_238 tenia 8 de 58 mil en A/A), p = 1.
- **Lectura:** INFERRED que el corte de fallas de la lejana libera aire para toda la celda; el AP no se juzga por regla (p95 25-34 ms en todas las ventanas).

## 4. Siguiente

- **Persistido (31/10 02:17Z, decision del orquestador, sin hold temporal):** distance 2850 en uci, con commit, en AP y cpe_210_9.
  - Backup en /etc/fmx_rollback/wireless.pre_w448 y vuelta atras con /etc/fmx_rollback/w448_rollback.sh.
  - Watchdog armado durante el cambio y cancelado despues del readback (uci 2850, clase 7, dmesg 0). Sin wifi reload.
  - Las 3 CPE de Panel3 quedaron en MCS 6-8.
  - Informe W423 de 24 h desde telemetria: 01/11 02:17Z.
- **24 h en RAM:** cortado. El proceso termino desde afuera cerca de las 02:09Z, al empezar el hold, sin pasar por su cierre. Fue el mismo patron que la corrida 2 de W433: ^C y borrado de pantalla; actor UNKNOWN.
  - El watchdog revirtio solo a clase 0 a las 02:12Z. Readback: mismos boot ids, dmesg en 0, sin lock.
  - No se relanzo por cuenta propia.
  - Propuesta: correr el hold con pythonw.exe, sin consola, para que un Ctrl+C de consola no lo corte. Al final corre el informe W423.
- **Persistir en Panel3:** despues del informe, con plan de vuelta atras.
- **Panel2 (W447):** el mismo cambio exacto es el canario para sus lejanas, cpe_200_169 y cpe_210_21.
