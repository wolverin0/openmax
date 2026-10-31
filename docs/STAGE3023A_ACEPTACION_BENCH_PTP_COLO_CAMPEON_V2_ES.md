<!-- doc-head: Wave 363 P2c, NO_GO del campeon PtP-Colo v2 medido en PowerBeam -->
12 ventanas fisicas validas; regresion de RTT; banco restaurado. Retencion30min no completada.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# PtP-Colo v2: NO_GO para canario productivo

Decision: **NO_GO**. Mediana de seis deltas pareados: RTT p95 **+24.00%**;
caudal RX de enlace **-2.38%**. Cierre indicado por el coordinador en
`<orca-id>`; no se despliega en produccion.

## Alcance y metodo

- PowerBeam AP .241 y STA .242, OpenWrt24.10.4, 5200MHz/VHT20.
- Replica RAM autorizada de doce valores y bucles AQL de5/10s; persistencia en sombra RAM.
- A: fq_memory_limit3145728, fq_limit512, fq_quantum3028; AQL2000/4000 porAC.
- B: diff oficial de nueve valores; BQL limit_max24192, hold_time400, AQL threshold3000.
- VO300/600, VI1000/2000, BE1500/2500, BK500/1000; backlog2048, notsent8192.
- Tres rondas A1-B1-A2-B2;30s por ventana, UDP ofrecido300Mbps y25pings de64B.
- Cola RF ocupada en las12ventanas; STA sin incremento de RX Ethernet.
- Watchdog45s renovado cada10s; expiracion autonoma y restauracion verificadas enambos.
- Goodput aplicativo: **UNKNOWN**. La tabla usa RX L2 de interfaz por delta de uptime.

## Resultados por ventana

| Ronda | Fase | RX L2 Mbps | p50 ms | p95 ms | p99 ms | Ping recibidos/enviados |
|---:|:---|---:|---:|---:|---:|---:|
| 1 | A1 | 25.43 | 28.94 | 63.73 | 75.37 | 24/25 |
| 1 | B1 | 23.26 | 29.66 | 71.29 | 73.92 | 25/25 |
| 1 | A2 | 29.59 | 23.78 | 49.17 | 51.42 | 25/25 |
| 1 | B2 | 18.15 | 30.28 | 66.94 | 88.35 | 22/25 |
| 2 | A1 | 23.51 | 16.63 | 48.68 | 88.42 | 23/25 |
| 2 | B1 | 23.68 | 18.28 | 90.45 | 109.73 | 25/25 |
| 2 | A2 | 25.19 | 17.39 | 50.07 | 57.85 | 24/25 |
| 2 | B2 | 24.35 | 31.28 | 53.15 | 57.05 | 24/25 |
| 3 | A1 | 18.57 | 28.15 | 120.71 | 183.97 | 25/25 |
| 3 | B1 | 18.85 | 28.29 | 67.24 | 91.92 | 22/25 |
| 3 | A2 | 21.81 | 18.89 | 48.18 | 52.75 | 22/25 |
| 3 | B2 | 21.51 | 25.64 | 116.93 | 118.68 | 25/25 |

p95 corresponde a respuestas recibidas; la columna de ping conserva la perdida.

## Seguridad, pruebas y restauracion

- Pytest: **34/34 PASS**, rc0; matriz nativa QEMU/OpenWrt BusyBox: **15/15 PASS**.
- Contencion: RED3fallos/3pases; despues GREEN6/6. Ambos recibos preservados.
- Core: retry solo del FD lock, dos sleeps de1s y revalidacion antes de escribir.
- Cero retries de escrituras del kernel; log acotado a8192bytes.
- Diez rollbacks explicitos, cinco porradio, rc0 y readback A completo antes de medir A.
- MemAvailable minimo muestreado: AP8576KiB, STA17740KiB; floor5120KiB.
- Dos rondas finales read-only:12valores originales, mismo boot, rc.local/M2U preservados.
- Archivos, handles y NAT propios retirados. Cero sesiones productivas y cero escrituras mtd.
- Dieciseis casos locales de tamper rechazan copias alteradas; no generan mediciones.

## Retencion y limite del lector

Las12ventanas son del intento7, fuente `fc13d6ce...eedd493`, con20inputs congelados.
La retencion se intento en una sesion separada con la misma revision y preimagen.
Tres capturas AQM bajo carga tienen exactamente199bytes y terminan en `RW fq_quantum`
sin valor ni salto de linea. AQL y las otras perillas siguen observables.
El lector rechazo esas capturas y restauro ambos radios; no sustituyo un valor supuesto.
La causa exacta del limite de buffer queda INFERRED, sin auditoria RE en este carril.
El coordinador cancelo mas reparaciones/retencion porque la matriz ya determina NO_GO.
**30min de B bajo carga: NO COMPLETADOS**. No se reutiliza observacion previa en reposo.

## Contrato y evidencia

BQL24192 del kit difiere del objetivo literal8192. El incremento nativo
`fq_overmemory` acumulado en B es124171; es un contador, sin atribuirlo a OOM.
No se alcanzan las metas literales. Restauracion y tests no equivalen a promocion.

- [Recibo completo](../artifacts/autoresearch/wave363_ptp_colo_champion_v2_bench.json)
- [Gate NO_GO](../artifacts/verification/wave363c_lane1_ptp_colo_champion_bench_gate.json)
- [Pytest34](../tools/champion_kits/wave363_champion_full.xml)
- [GREEN](../tools/champion_kits/wave363_guard_green.xml)
- [RED preservado](../tools/champion_kits/wave363_guard_red.xml)

Core SHA256: `4dfd2eaae70f70ba9f4f1581b7d4e744712408c1d80009c941e0b1322d66c1f2`.
Banco restaurado y listo para que el coordinador reasigne .241/.242.
