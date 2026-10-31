<!-- doc-head: Wave 249 (2532A-2537A) cerrada offline en Wave 266, CPE .210.9 de Panel3-Guarida, cadenas y RTS 512 -->
2532A: lectura RF/MAC de solo lectura después de psk2. Cadenas con 9 dB de diferencia en el AP y 3 dB en la CPE,
MCS0 NSS1 en ambos sentidos, cero sesiones block-ack, coverage class 0 y distance vacía en ambos extremos.
2534A: un ciclo A/B/A2 de RTS 512 escrito solo en tiempo de ejecución en el AP y revertido (tx failed 4202, 1052, 2671).
Este stage no escribe nada en radios: recalcula y documenta. Gate: artifacts/verification/stage2537a_wave249_opus1_gate.json.
Leer antes de tocar RTS, distance o la antena de la CPE .210.9.
<!-- /doc-head -->

# Stage 2535A: diagnóstico de cadenas y prueba RTS 512 en la CPE .210.9 de Panel3

## 1. Resumen ejecutivo

- La CPE .210.9 (2275 m según la radiografía, fila CONFIRMED) sigue en VHT-MCS0 con un solo flujo
  espacial en ambos sentidos aunque la señal es fuerte: -48 dBm vista desde el AP y -53 dBm vista
  desde la CPE. Con ese nivel la tasa no está limitada por la relación señal/ruido.
- Las cadenas del AP para esta estación están desbalanceadas 9 dB (-58 y -49 dBm); las de la CPE,
  3 dB (-55 y -58 dBm). El desbalance aparece en el sentido CPE hacia AP.
- No hay ninguna sesión block-ack: las 16 filas TID leen 0 en RX y TX en los dos extremos, así que
  no hay agregación A-MPDU y cada trama de 1500 B a 6,5 Mbit/s ocupa unos 1,9 ms de aire.
- Coverage class 0 ("up to 0m") y `distance` vacía en el AP y en la CPE; límites de reintento 7/4.
- Un único ciclo de RTS 512 (2534A) bajó tx failed de 4202 a 1052 (-74,96 %) y el RTT de 80 a 20 ms;
  la pérdida de ping solo bajó de 21,7 % a 16,7 %. La ventana de retorno A2 no volvió a la línea
  base (2671 fallos, 46 ms), no se registró la duración de cada ventana y RTS quedó apagado en los
  dos extremos. Es un indicio prometedor de un solo ciclo, no una mejora demostrada.

## 2. Fuentes y clase de evidencia

| recibo | clase | escrituras | verificación en el gate 2537A |
|---|---|---|---|
| 2532A | LIVE_HARDWARE_READ_ONLY_PRODUCTION | 0 de configuración | sha256 y tamaño de la captura cruda `wave249/2532a_rf_20261028T130813Z.json` (7575 B, f368c5f5…) |
| 2534A | LIVE_HARDWARE_RUNTIME_WRITE_REVERTED | RTS 512 en tiempo de ejecución, solo en el AP .83; 0 persistentes | `restored` verdadero, estado final "RTS off" en .83 y .210.9 |

Los dos recibos se leen tal cual estaban; este stage no los modifica. El gate recalcula cada número
de este documento a partir de los textos crudos de `iw` guardados en ellos.

## 3. Lectura RF/MAC después de psk2 (2532A)

### 3.1 Configuración PHY en ambos extremos

| campo | AP .83 | CPE .210.9 |
|---|---|---|
| canal | 149 (5745 MHz), 20 MHz | 149 (5745 MHz), 20 MHz |
| potencia | 20 dBm, VHT20 | 20 dBm, VHT20 |
| coverage class | 0 (up to 0m) | 0 (up to 0m) |
| opción `distance` | vacía | vacía |
| reintentos corto / largo | 7 / 4 | 7 / 4 |
| antenas configuradas | TX 0x3 RX 0x3 | TX 0x3 RX 0x3 |

### 3.2 Estado de la estación

| campo | visto desde el AP | visto desde la CPE |
|---|---|---|
| tx failed (acumulado) | 54101 | 30358 |
| tx retries (acumulado) | 23883 | 19141 |
| señal [cadena 0, cadena 1] | -48 [-58, -49] dBm | -53 [-55, -58] dBm |
| diferencia entre cadenas | 9 dB | 3 dB |
| tasa TX | 6,5 Mbit/s VHT-MCS 0 NSS 1 | 6,5 Mbit/s VHT-MCS 0 NSS 1 |
| tasa RX | 13,0 Mbit/s VHT-MCS 1 NSS 1 | 6,5 Mbit/s VHT-MCS 0 NSS 1 |
| sesiones block-ack (16 TID) | 0 | 0 |
| pérdida de beacons | n/a | 0 de 58428 recibidos |

En los dos extremos tx failed supera a tx retries. Con la semántica de libro (una trama fallida
agota todos sus reintentos) eso no puede pasar, así que estos contadores de ath10k no se usan como
"reintentos por trama"; solo se comparan entre ventanas del mismo extremo.

### 3.3 Diagnóstico de cadenas

- El desbalance de 9 dB está en lo que el AP recibe de esta CPE. Las otras dos estaciones del mismo AP
  llegaron a MCS 7-8 con dos flujos en la auditoría posterior al cambio (2496A-2500A), lo que apunta al camino de
  la CPE .210.9 (alineación, polarización, conector o cable de una cadena) y no a una cadena del AP.
  Es una sospecha sin verificar: nadie inspeccionó la antena.
- Con 9 dB entre cadenas el segundo flujo espacial no es viable, lo que explica NSS 1, pero no
  explica MCS 0 con -48 dBm. Un MCS tan bajo con señal fuerte es lo que deja el control de tasa
  cuando las tramas fallan por colisión, interferencia o temporización, no por nivel de señal.
- Sin block-ack, cada fallo cuesta una trama completa de ~1,9 ms. Cualquier transmisión que el AP no
  oye y que pisa ese intervalo cerca de la CPE la invalida: la ventana vulnerable es enorme.

## 4. Prueba RTS 512 (2534A)

RTS 512 se escribió solo en tiempo de ejecución en el AP .83, con un temporizador de reversión de
240 s armado. El ciclo empezó a las 13:12:00 UTC y terminó a las 13:15:44 UTC (224 s para las tres
ventanas y las transiciones). Un primer intento se abortó porque el SSH a la CPE se cayó justo
después de poner RTS en el AP; RTS se forzó a apagado en los dos extremos en alrededor de un minuto.

| ventana | RTS | tx failed (delta) | tx retries (delta) | pérdida de ping | RTT medio |
|---|---|---|---|---|---|
| A_baseline_rts_off | apagado | 4202 | 1781 | 21,7 % | 80 ms |
| B_rts_512 | 512 | 1052 | 437 | 16,7 % | 20 ms |
| A2_rts_off_again | apagado | 2671 | 795 | 20,0 % | 46 ms |

Cambios recalculados (asumen ventanas de igual duración, que el recibo no registra):

| comparación | tx failed | tx retries | RTT |
|---|---|---|---|
| B contra A | -74,96 % | -75,46 % | -75,00 % |
| B contra A2 | -60,61 % | -45,03 % | -56,52 % |
| B contra el promedio de A y A2 | -69,39 % | | |
| A2 contra A (deriva sin cambio) | -36,44 % | | |

- La deriva entre A y A2 (-36,44 % sin tocar nada) es grande: una parte del efecto atribuido a RTS
  puede ser variación del canal. Hace falta repetir ciclos alternados con ventanas cronometradas.
- RTS en el AP afecta a las tres estaciones de Panel3, no solo a .210.9.
- Estado final: "RTS off" en .83 y en .210.9; 0 escrituras persistentes. Coverage class y
  `distance` no se tocaron porque la longitud real del trayecto no está medida y el valor del AP
  se aplica a las tres estaciones.

## 5. Qué se puede afirmar y qué no

| afirmación | estado |
|---|---|
| .210.9 en MCS0 NSS1, sin block-ack, coverage class 0 en ambos extremos | medido (2532A) |
| 9 dB entre cadenas en el AP para esta estación | medido (2532A) |
| causa física del desbalance (antena, cable, polarización) | sin verificar |
| RTS 512 redujo tx failed en un ciclo | medido una vez (2534A), con deriva y sin duraciones |
| RTS 512 mejora de forma sostenida | no demostrado |
| el timeout de ACK por defecto falla a 2275 m | no medido; ver el modelo 2623A |

El modelo de Wave 266 ([2622A/2623A](STAGE2624A_PARETO_SIMPY_PYMOO_RTS_Y_COVERAGE_CLASS_PANEL3_PANEL2_ES.md))
solo reproduce el -75 % cuando el timeout de ACK/CTS por defecto ya cubre los 2275 m y la mayor
parte de la interferencia cerca de la CPE respeta el NAV del CTS (2 de 12 escenarios). Si el timeout
quedara corto, el CTS también llegaría tarde y RTS empeoraría los fallos. Es una inferencia de modelo.

## 6. Contrato Karpathy de D3 al cierre (offline)

Meta: `panel3_admitter_running == true AND cpe_210_9_tx_failed_delta_pct <= -50% AND fq_overmemory_delta == 0`.

| término | valor | cumple |
|---|---|---|
| panel3_admitter_running | UNKNOWN_OFFLINE: una wave sin SSH no puede leer la tabla de procesos | no |
| cpe_210_9_tx_failed_delta_pct | -74,96 % en un solo ciclo revertido; RTS hoy apagado | numéricamente sí, sin persistencia |
| fq_overmemory_delta | incrementos mayores que cero en telemetry.db para panel3_ap | no |

Veredicto: TARGET_NOT_MET. El gate 2627A recalcula los tres términos desde el disco.

## 7. Próximo paso (no ejecutado, requiere orden del operador)

1. Medir el trayecto real y revisar alineación y conectores de las dos cadenas de la CPE .210.9.
2. Repetir RTS 512 en al menos tres ciclos A/B alternados con ventanas cronometradas iguales,
   registrando duración, tx failed, RTT y pérdida por ventana, con reversión automática.
3. Solo después decidir si RTS se persiste en Panel3.

## 8. Verificación

```
python tools/verify/verify_stage2537a_wave249_opus1_gate.py --write
python -m pytest tests/test_stage2532a_to_2537a_suite.py -q
```

No se abrió ninguna conexión a radios en este stage.
