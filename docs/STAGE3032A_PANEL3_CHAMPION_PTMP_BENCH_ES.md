<!-- doc-head: Wave 372, comparativa fisica PtMP Panel3 actual vs campeon oficial -->
12 ventanas TCP reales; piso6MiB y restauracion exacta verificados. Regla previa estricta: NO_GO.
<!-- /doc-head -->

# Panel3: benchmark PtMP en LAP-120

**NO_GO bajo la regla estricta predeclarada**: p95 mediano pareado **-24.11%**;
goodput TCP mediano pareado **-0.095%**. No se infiere una regresion material de capacidad.
La regla fijada antes de medir exigia p95 menor y caudal no menor, sin margen aprobado.

## Metodo y alcance

- LAP-120 .20, una Loco .200.41 asociada; 5180MHz/VHT20, sin cambios RF.
- A replica13 valores instalados de Panel3 en la telemetria guardada de CAMPEON_OFICIAL_V2.
- B aplica sus8 diferencias oficiales; no se consulto ni modifico Panel3 productivo.
- PC envia TCP ilimitado con4streams; Loco ejecuta solo receptor one-shot. AP hace forwarding.
- Alias .200.1 y NAT TCP temporales, bajo watchdog45s renovado; cero iperf3 en AP.
- Guard6144KiB antes de escribir y durante carga; maximo25min para el loop de3rondas.
- Kit RAM con guard6144 y hold0 admitido por el conf; cada brazo se mide30s bajo guard exterior.
- Persistencia redirigida a sombra RAM; no se prueba instalacion persistente productiva.
- Readbacks13 al inicio/final; prueba de cola ocupada y bytes aereos frente a bytes recibidos.
- Goodput: sum_received cliente y servidor coinciden enbytes en las12ventanas.

## Ventanas fisicas

| Ronda | Fase | Goodput Mbps | p50 ms | p95 ms | p99 ms |
|---:|:---|---:|---:|---:|---:|
| 1 | A1 | 102.459 | 10.543 | 21.398 | 34.511 |
| 1 | B1 | 102.283 | 10.408 | 19.518 | 21.383 |
| 1 | A2 | 102.719 | 10.540 | 26.962 | 28.088 |
| 1 | B2 | 101.499 | 10.263 | 18.977 | 23.175 |
| 2 | A1 | 102.415 | 11.612 | 22.006 | 27.101 |
| 2 | B1 | 102.163 | 11.702 | 25.941 | 29.661 |
| 2 | A2 | 102.108 | 15.140 | 36.639 | 63.447 |
| 2 | B2 | 102.089 | 10.524 | 22.977 | 25.544 |
| 3 | A1 | 102.222 | 10.436 | 24.024 | 37.962 |
| 3 | B1 | 102.632 | 9.262 | 18.947 | 21.220 |
| 3 | A2 | 97.924 | 10.054 | 25.135 | 29.831 |
| 3 | B2 | 102.167 | 9.055 | 18.329 | 25.683 |

## Guardas y limites

- Minimo MemAvailable6540KiB; no se cruzo el piso6144. Cero abortos.
- Pings: A150/150 y B150/150; B fq_overmemory delta0.
- Los13 originales del AP, boot y rc.local se verificaron despues de restaurar.
- Alias, NAT y archivos propios retirados; cargas y receptores finalizaron.
- Se reutilizo la libreria aceptada; hubo arm/renew/restore reales. No se repitio fire autonomo en esta wave.
- No se intento retencion30min: las12ventanas ya permiten aplicar la regla declarada.
- No hay evidencia de admisiones ni tx_failed del CPE productivo .210.9; estan fuera de alcance.
- Es un banco con un receptor, sin certificacion multipunto completa ni autorizacion productiva.

## Evidencia

- [Recibo y cliente/servidor JSON](../artifacts/autoresearch/wave372_ptmp_panel3_champion_bench.json)
- [Gate](../artifacts/verification/wave372_lane1_ptmp_panel3_champion_gate.json)
- [Arnes](../tools/champion_kits/run_wave372_panel3_bench.py)
- [Receptor acotado](../tools/champion_kits/wave372_receiver.py)
