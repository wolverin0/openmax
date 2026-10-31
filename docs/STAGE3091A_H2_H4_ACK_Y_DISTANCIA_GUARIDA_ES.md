<!-- doc-head: Stage 3091A (W431) ES: H4 solo lectura en Guarida: los 3 AP y todas las CPE estan en coverage class 0 sin opcion distance (CONFIRMED); las 3 CPE a mas de 2 km (cpe_200_169, cpe_210_21, cpe_210_9) tienen falla por paquete de 1,0 en bajada y subida y MCS 0 con buena senal, las 10 cercanas 0,15 % o menos; H2: canario exacto para Panel3 (distance 2850, clase 7, AP y cpe_210_9, solo RAM) que choca con la politica porque el banco dio NO_GO de costo: decide el operador -->
Que cubre: clase y distancia configuradas, distancia por CPE, quien queda fuera de la cobertura de ACK con sus reintentos y fallas, y el canario de produccion con como lo juzgaria el informe W423.
Estado: solo lectura. 0 escrituras. Datos maquina: artifacts/autoresearch/wave431_h2_h4.json. Informe visual: artifacts/2026-10-30-h2-ack-distancia.html.
Leer cuando: antes de escribir distance o coverage en Panel3 o Panel2.
<!-- /doc-head -->
# Stage 3091A: H4 y H2, ACK y distancia en Guarida (W431)

## 1. H4: que esta configurado (CONFIRMED)

- `iw phy phy0 info` en Panel1, Panel2 y Panel3 y en las CPE da `Coverage class: 0 (up to 0m)` en todas las interfaces. En W369, Panel1 y Panel2 eran INFERRED.
- No hay opcion `distance` en uci: queda el default 0 de OpenWrt. ath10k-ct no tiene dynack (W369).

## 2. H4: distancia y fallas por CPE (ventanas de 60 s del AP y 30 s de la CPE)

| Panel | CPE | airOS m | UISP m | Senal | MCS baj/sub | Falla/paquete baj | Falla/paquete sub |
| :-- | :-- | :-- | --: | --: | :-- | --: | --: |
| panel2 | cpe_210_21 | 2100-2700 | 2676 | -60 | 0/0 | 1,0013 | 0,9905 |
| panel2 | cpe_200_169 | 2100-2250 | 2044 | -53 | 0/- | 1,0005 | sin dato |
| panel3 | cpe_210_9 | 2700-2850 | 2276 | -51 | 0/0 | 0,9989 | 1,0012 |
| panel1 | cpe_200_80 | - | 4404 | -57 | 6/4 | 0,0015 | 0,0 |
| panel2 | cpe_200_213 | 300-300 | 6068 | -46 | 6/5 | 0,0003 | 0,0006 |
| panel1 | cpe_200_223 | - | 9 | -42 | 5/6 | 0,0 | 0,0 |
| panel1 | cpe_200_41 | - | 1139 | -47 | 8/4 | 0,0 | 0,0 |
| panel2 | cpe_210_239 | 300-450 | - | -33 | 8/6 | 0,0 | 0,0014 |
| panel2 | cpe_200_183 | 300-300 | 573 | -54 | 7/0 | 0,0 | 0,0049 |
| panel2 | cpe_210_83 | 450-450 | 578 | -47 | 7/0 | 0,0 | 0,0363 |
| panel2 | cpe_210_166 | 600-600 | 573 | -44 | 8/7 | 0,0 | 0,0023 |
| panel3 | cpe_210_238 | 600-900 | - | -40 | 6/4 | 0,0 | 0,0 |
| panel3 | cpe_210_235 | 150-1200 | - | -37 | 8/4 | 0,0 | 0,0 |

- **CONFIRMED:** las tres CPE lejanas tienen tantas tramas fallidas como enviadas (1,0 por paquete), en las dos direcciones, con MCS 0 y senal de -51 a -60 dBm. De las diez cercanas, ninguna pasa de 0,0015 en bajada.
- **INFERRED:** el AP no ve el ACK a tiempo y cuenta como fallida una trama que llego. El control de tasa ve 100 % de falla y baja a MCS 0. Cae a una distancia entre ~1,2 km (la cercana sana mas lejana) y ~2,0 km (cpe_200_169 ya falla). 2534A habia visto el CTS cubrir ~2,3 km, pero son timeouts separados.
- **Distancia de UISP:** sale de las coordenadas (coincide a metros). En cpe_200_80, cpe_200_213 las coordenadas estan mal (4-6 km con MCS 6 y 0 fallas). Para la lejana de Panel3 la mejor medida es airOS (2700-2850 m), no UISP (2276 m).
- **Otras explicaciones, no descartadas:** .9 sin sesiones BA (2532A); 9 dB de desbalance de cadenas en .9. cpe_200_169 no contesto la lectura de subida.

## 3. H2: canario exacto (no ejecutado)

- **Donde:** Panel3 (3 clientes). AP y cpe_210_9. Las cercanas no se tocan.
- **Valor:** `iw phy phy0 set distance 2850` en los dos, clase 7, cubre 3150 m. Clase 6 (2700 m) no cubre los 2850 m de airOS. Solo RAM, sin uci commit.
- **Orden y guardas:** AP primero, despues la CPE. Watchdog compartido armado antes. Readback `Coverage class: 7 (up to 3150m)` y dmesg sin rechazo.
- **Rollback:** `set distance 0` y readback 0. `wifi reload` o reboot tambien vuelven a 0.
- **Diseno:** el mismo dia, 3 ventanas A/A de 10 min en clase 0 y despues ABAB de 10 min, con la carga real.
  - Metricas: falla y reintentos por paquete y MCS por CPE (station dump del AP), subida de .9, sidecar origin=core p50/p95/perdida, fq_overmemory, memoria.
  - Abortar contra la banda A/A de la misma corrida, sin umbrales fijos: p95 o falla por paquete de una cercana arriba del maximo A/A, readback distinto, rechazo, desasociacion, crash o reinicio.
- **Esperado (INFERRED):** .9 sale de 1,0 de falla y de MCS 0. Las cercanas pagan 21 us de slot por acceso; el banco midio -2,8 % de goodput en clase 6.
- **Juicio con W423:** 24 h despues de dejar B, `before_after_report` sobre panel3_ap y las 3 CPE con `--hours 24`.
  - GO dentro de la banda A/A de cada equipo; ROLLBACK si una primaria sale hacia el lado malo o suben los reclamos; NO_VERDICT si falta cobertura.
  - El informe juzga el costo. El beneficio (falla por paquete del AP) sale de las ventanas ABAB, porque el informe no lo mide.
- **Despues:** Panel2 (cpe_200_169 y cpe_210_21) con la misma receta. Ahi pagan 5 cercanas.

## 4. Para decidir (operador)

- **Banco:** dio la parte de seguridad. W384: sin OOM, sin crash y restauracion exacta. Pero dio **NO_GO por su propia regla de costo:** -2,8 % de goodput en clase 6. W376 aborto por memoria antes de comparar.
- **El banco no puede medir el beneficio:** no tiene retardo de propagacion.
- **La politica de produccion del 30/10 pide un gate PASS de banco del cambio exacto.** Este canario no lo tiene: correrlo es aceptar un costo de ~3 % en las CPE cercanas de Panel3 a cambio de sacar a cpe_210_9 de 100 % de falla y MCS 0. Esa decision es del operador.
