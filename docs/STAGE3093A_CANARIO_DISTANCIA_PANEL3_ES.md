<!-- doc-head: Stage 3093A (W433) ES: canario de distancia en Panel3 (distance 2850, clase 7, AP y cpe_210_9, solo RAM con watchdog); tres corridas, la tercera llego a B1: la CPE lejana paso de fallar todo a casi nada y su p95 bajo de 87-123 a 38 ms, pero la regla predeclarada aborto por un aumento minimo de fallas en cpe_210_238; NO_GO y revertido a clase 0 -->
Que cubre: corridas, ventanas medidas, por que aborto y que queda abierto.
Estado: NO_GO por regla predeclarada (NEAR_COST). Panel3 y cpe_210_9 de vuelta en clase 0, mismos boot ids, sin dmesg nuevo.
Datos maquina: artifacts/autoresearch/wave433_panel3_distance.json.
Leer cuando: antes de repetir el canario de distancia o de llevarlo a Panel2 (W447).
<!-- /doc-head -->
# Stage 3093A: canario de distancia en Panel3 (W433)

## 1. Corridas

- **Corrida 1 (30/10 19:41Z):** Claude Code la detuvo en AA2 por memoria baja. 0 escrituras.
- **Corrida 2 (20:58Z):** midio AA1, AA2 y AA3; un Ctrl+C externo la corto al empezar A1. 0 escrituras.
- **Corrida 3 (31/10 00:10Z):** tarea programada de un solo uso. Reuso las AA de la corrida 2 por orden del orquestador; corrio A1 y B1.
  - En B1 aplico la clase 7 en los dos equipos: watchdog armado, readback en clase 7, sin dmesg nuevo.
  - Al cerrar B1 aborto por la regla y restauro la clase 0 en los dos.
  - La tarea se borro al terminar.

## 2. Ventanas (falla por paquete bajada / p95 core ms)

| Ventana | Clase | cpe_210_9 | cpe_210_235 | cpe_210_238 |
| :-- | --: | :-- | :-- | :-- |
| AA1 | 0 | 1,0001 / 122,46 | 0,0 / 31,58 | 0,0002 / 51,29 |
| AA2 | 0 | 0,9996 / 122,73 | 0,0 / 48,17 | 0,0 / 56,53 |
| AA3 | 0 | 1,0 / 123,08 | 0,0 / 46,97 | 0,0 / 63,07 |
| A1 | 0 | 1,0 / 86,85 | 0,0 / 39,83 | 0,0004 / 53,02 |
| B1 | 7 | 0,0001 / 37,57 | 0,0 / 27,33 | 0,0014 / 43,7 |

## 3. Lectura

- **Lejana (CONFIRMED en una ventana B):** cpe_210_9 paso de 1,0 a 0,0001 de falla por paquete y de MCS 0 a 7. Su p95 core bajo de 87-123 a 38 ms y su perdida core de 7-15 % a 0. Entrego unas 10 veces mas paquetes.
- **Costo que disparo la regla:** cpe_210_238 subio a 0,0014 de falla por paquete (unos 15 de 10.410) frente a un maximo A de 0,0004 (unos 7 de 17.407). Su p95 core bajo de 51-63 a 44 ms.
- **La regla** compara contra el maximo A sin piso de ruido. No se cambia despues de ver los datos: el veredicto es NO_GO.

## 4. Abierto

- **Decidir** si se repite con una regla nueva declarada antes (por ejemplo, costo por conteo de fallas o por p95 en los dos origenes), o se acepta el resultado. Lo decide el orquestador o el operador.
- **W447 (Panel2):** sin PASS de este canario, la causa principal de Panel2 queda sin fix aprobado.
