<!-- doc-head: Waves 296 y 300, mapa espectral, auto-interferencia y propuesta de canales de la torre Guarida (offline) -->
Wave 296: separación borde a borde y centro a centro, fuga por máscara 802.11ac, acoplamiento y aislamiento MIMO;
el plan del brief (40 MHz) no coincide con lo leído (todo a 20 MHz). CORREGIDO en Wave 335: PtP-Colo no está en Guarida.
Wave 300 (sección 9, solo diseño): mover solo PtP-Colo a ch36 deja todo par >= 40 MHz; 60 MHz exige PtP-Colo en
6035 MHz o en DFS y Panel2 en ch165. Datos: artifacts/autoresearch/wave296_guarida_channel_plan_audit_20261028.json y
wave300_guarida_zero_overlap_channel_proposal_20261028.json. Sin SSH ni red; nada aplicado.
<!-- /doc-head -->

> **Corrección (Wave 335, topología confirmada por el operador):** PtP-Colo (.62/.54, 5765 MHz) está en el POP Edificio
> Principal, a 7 km y 2 saltos PtP de la Torre Guarida (Edificio Principal → Almafuerte .60 → Guarida .61). No es
> co-sitio con Panel3 (5745 MHz): se retiran los riesgos "ALTO/MEDIO" con PtP-Colo de este documento y las propuestas
> de la sección 9 que dependían de ellos. Los pares entre sectores de Guarida siguen valiendo.

# Wave 296: mapa espectral y auto-interferencia de la torre Guarida

## 1. Resumen ejecutivo

- **El plan del brief no es el estado leído.** El brief dice Panel1 ch149, Panel2 ch36, Panel3 ch100 y PtP-Colo
  ch161, todo a 40 MHz. Las lecturas en vivo guardadas (22 al 28 de octubre) muestran todo a 20 MHz: Panel1 5240,
  Panel2 5805, Panel3 5745, PtP-Colo 5765, y además el PtP Almafuerte-Guarida (.61) en 5355. Se analizan los dos.
- **Hoy, riesgo ALTO:** Panel3 (5735-5755) y PtP-Colo (5755-5775) son adyacentes con 0 MHz de guarda. En la
  geometría nominal supuesta, la fuga de uno sobre el otro queda unos 19 dB sobre el piso de ruido.
- **Hoy, riesgo MEDIO:** Panel2 (5795-5815) y PtP-Colo, 20 MHz de guarda (I/N cerca de 0 dB nominal).
- **Plan del brief:** también deja un par adyacente sin guarda, Panel1 (5735-5775) con PtP-Colo (5775-5815), pone
  Panel3 en DFS (ch100) y no considera el PtP de Almafuerte.
- El plan registrado en 2544A de llevar PtP-Colo a 6035 MHz eliminaría los dos pares de riesgo actuales.

## 2. Radios y canales

| radio | brief | leído en disco (20 MHz) | ocupación leída | fuente |
|---|---|---|---|---|
| Panel1-Guarida .84 | ch149, 40 MHz | ch48, 5240 | 5230-5250 | iw dev 22/10; 2588A, 2610A, 2640A |
| Panel2-Guarida .82 | ch36, 40 MHz | ch161, 5805 | 5795-5815 | iw dev en el cutover OpenWrt 28/10 |
| Panel3-Guarida .83 | ch100, 40 MHz | ch149, 5745 | 5735-5755 | iw dev 2532A, 28/10 13:08 UTC |
| PtP-Colo .62/.54 | ch161, 40 MHz | ch153, 5765 | 5755-5775 | iw dev en el cutover OpenWrt 28/10 |
| PtP Almafuerte-Guarida .61 | no figura | 5355 | 5345-5365 | plan 24/10 (fila CONFIRMED) y 2640A |

Un canal de 40 MHz no se centra en su canal primario: los del brief ocupan 5735-5775 (149+153), 5170-5210 (36+40),
5490-5530 (100+104) y 5775-5815 (157+161). 2544A registra para PtP-Colo un primario 6035 MHz (ch207) con respaldo
en 5200; la lectura del cutover lo muestra en 5765.

## 3. Separación entre pares, estado leído

| par | centro a centro | borde a borde | riesgo | I/N pesimista / nominal / optimista |
|---|---|---|---|---|
| Panel3 / PtP-Colo | 20 MHz | 0 MHz | ALTO, adyacente sin guarda | +34,8 / +18,7 / -4,8 dB |
| Panel2 / PtP-Colo | 40 MHz | 20 MHz | MEDIO | +16,8 / +0,8 / -22,7 dB |
| Panel3 / Panel2 | 60 MHz | 40 MHz | BAJO | +13,6 / -2,4 / -26,0 dB |
| Panel1 / PtP Almafuerte | 115 MHz | 95 MHz | despreciable | +8,7 / -7,3 / -30,8 dB |
| resto (6 pares) | 390-565 MHz | 370-545 MHz | despreciable | menor a +8,4 / -7,6 / -31,1 dB |

## 4. Separación entre pares, plan del brief

| par | centro a centro | borde a borde | riesgo | I/N pesimista / nominal / optimista |
|---|---|---|---|---|
| Panel1 / PtP-Colo | 40 MHz | 0 MHz | ALTO, adyacente sin guarda | +30,8 / +14,8 / -8,7 dB |
| resto (5 pares) | 245-605 MHz | 205-565 MHz | despreciable | menor a +5,5 / -10,5 / -34,0 dB |

Panel3 en ch100 (5490-5530) cae en DFS: obliga a CAC y a salir del canal ante un radar detectado, cosa que
hoy ningún sector hace. El PtP Almafuerte en 5345-5365 cruza el borde de 5350 MHz: conviene revisar su
habilitación regulatoria, sea cual sea el plan.

## 5. Cómo se calculó

- Separaciones: centro a centro = |fc_a - fc_b|; borde a borde = mayor borde inferior menos menor borde superior
  (negativo = solapamiento).
- Fuga (ACLR): la máscara de emisión 802.11ac (0 dBr hasta ±9 MHz, -20 en ±11, -28 en ±20, -40 en ±30 para 20 MHz),
  integrada sobre la banda víctima. Da -23,4 dB entre 20 MHz adyacentes y -24,5 dB entre 40 MHz adyacentes. Más
  allá de 2 veces el ancho se supone un piso de -50 dBr.
- Acoplamiento: 20 dBm (leído en Panel3) + ganancia fuera de eje de cada antena - pérdida en espacio libre. Tres
  escenarios porque la torre no está relevada: 1 m y -5 dBi (pesimista), 2 m y -10 dBi (nominal), 3 m y -20 dBi
  (optimista). Selectividad del receptor supuesta: 30 dB adyacente, 45 dB con guarda de hasta 40 MHz, 60 dB más lejos.
- I/N: interferencia en banda contra un piso de -95 dBm (20 MHz, figura de ruido 6 dB). +18,7 dB equivale a que
  el receptor pierda unos 19 dB de sensibilidad mientras el otro radio transmite.

## 6. Aislamiento MIMO

- No existe medición de aislamiento entre puertos ni de polarización cruzada. Lo único medido es el desbalance
  entre cadenas (2532A): el AP de Panel3 recibe a .210.9 con -58 y -49 dBm (9 dB); la CPE recibe -55 y -58 (3 dB).
- 9 dB entre cadenas explica que ese enlace use un solo flujo (MCS0 NSS1). Las otras dos CPE de Panel3 usaron dos
  flujos en MCS 7-8 (2496A-2500A): el problema es de ese enlace, no de una cadena del AP.
- Entre radios de la torre no se supone aislamiento por polarización: todos son 2x2 de doble polarización, así que
  un interferente co-ubicado llega co-polar a al menos una cadena. El aislamiento sale solo de frecuencia,
  distancia y diagrama.

## 7. Qué no se puede afirmar

- Que Panel3 sufra hoy por PtP-Colo: los problemas de .210.9 (2532A, 2534A) se registraron a las 13:08 UTC del 28/10,
  antes del cutover de PtP-Colo a 5765 (cerca de las 19:14 UTC); no hay en disco la frecuencia previa de PtP-Colo.
- Valores de I/N absolutos: distancia entre antenas, azimuts y lóbulos no están medidos; los tres escenarios los acotan.
- Que el brief refleje un cambio posterior a las lecturas: no hay recibo que lo muestre.

## 8. Próximo paso (no ejecutado, requiere orden del operador)

1. Confirmar con una lectura de solo lectura (iw dev) los canales actuales de los cinco radios, y decidir si el
   plan del brief es una propuesta o el estado real.
2. Separar Panel3 de PtP-Colo con la propuesta A de la sección 9 (o B/C si se cierran sus condiciones).
3. Relevar distancia y azimut entre antenas en la torre para reemplazar los escenarios supuestos.

## 9. Wave 300: propuesta de canales sin solapamiento (solo diseño, nada aplicado)

Datos: [wave300_guarida_zero_overlap_channel_proposal_20261028.json](../artifacts/autoresearch/wave300_guarida_zero_overlap_channel_proposal_20261028.json).

### 9.1 Canales permitidos

- Lista de ath10k en OpenWrt (lectura `iw phy` del 28/10, DFS-FCC; las imágenes de Guarida usan `country 'AR'`):
  sin DFS, 36-48 (5180-5240, 23 dBm) y 149-165 (5745-5825, 30 dBm); con DFS, 52-64 y 100-144; 5845/5865 sin
  permiso de emisión; 5340-5480 no aparece.
- CPE airOS 8 (LiteBeam 5AC Gen2/LR, NanoStation 5AC Loco): siguen al AP dentro de su lista de país, que cubre
  los mismos rangos en AR y US. No hay en disco la lista de cada CPE airOS: verificarla antes de mover Panel1 o
  Panel2, que todavía tienen CPE airOS.
- 6035 MHz (ch207) solo vale para PtP-Colo (OpenWrt en las dos puntas, desbloqueo propio de 2544A), nunca para
  un sector con CPE airOS.
- El PtP Almafuerte (.61, 5355) se deja fijo: retocarlo exige la punta de Almafuerte, y como 5355 está fuera de la
  lista de ath10k, habrá que moverlo si ese enlace pasa a OpenWrt.

### 9.2 Resultado de la búsqueda exhaustiva (20 MHz, 5 radios)

| restricción | mejor guarda mínima borde a borde |
|---|---|
| solo canales sin DFS | 40 MHz |
| PtP-Colo puede usar 6035 MHz | 60 MHz |
| PtP-Colo puede usar DFS | 60 MHz |

No se llega a 60 MHz sin salir de las bandas sin DFS: U-NII-1 mide 80 MHz (dos radios a lo sumo a 40 MHz) y
U-NII-3 100 MHz (dos radios a lo sumo a 60 MHz); con cinco radios y 5355 fijo, uno tiene que ir afuera.

### 9.3 Propuestas

| radio | hoy | A: mínimo cambio | B: óptima 60 MHz | C: 60 MHz con DFS |
|---|---|---|---|---|
| Panel1 .84 | 48 | 48 | 48 | 48 |
| Panel2 .82 | 161 | 161 | 165 | 165 |
| Panel3 .83 | 149 | 149 | 149 | 149 |
| PtP-Colo .62/.54 | 153 | 36 | 6035 MHz (respaldo ch36) | 100 (DFS, respaldo ch36) |
| PtP Almafuerte .61 | 5355 | 5355 | 5355 | 5355 |
| guarda mínima | 0 MHz | 40 MHz | 60 MHz (40 con respaldo) | 60 MHz |
| radios que cambian | - | 1 enlace PtP | Panel2 y PtP-Colo | Panel2 y PtP-Colo |

- **A**: solo cambia PtP-Colo (153 a 36), sin tocar ninguna CPE airOS. Elimina la adyacencia de 0 MHz; los pares
  más cercanos quedan a 40 MHz (Panel1/PtP-Colo y Panel3/Panel2). Revisar el presupuesto del enlace PtP-Colo con
  el límite de 23 dBm de U-NII-1.
- **B**: PtP-Colo a 6035 MHz, como ya planea 2544A, y Panel2 de 161 a 165. Todo par queda a 60 MHz o más. Depende
  de cerrar la cuestión regulatoria de 6035 MHz (Wave 291) y de verificar que cada CPE airOS de Panel2 acepte 5825
  MHz. El respaldo de 2544A en 5200 (ch40) quedaría a 20 MHz de Panel1: conviene cambiarlo a ch36 (40 MHz).
- **C**: lo mismo que B, pero dentro del dominio regulatorio, con PtP-Colo en DFS ch100. A cambio, 60 s de CAC
  tras cada arranque o cambio, y un radar detectado corta el backhaul; necesita respaldo sin DFS (ch36).
- Panel2 y Panel3, los sectores con los enlaces más largos (hasta 2674 y 2275 m), quedan en U-NII-3 (30 dBm)
  en las tres propuestas.

Recomendación: aplicar A primero; pasar a B (o C) solo cuando se resuelvan sus condiciones. Cualquier cambio
requiere orden del operador, una lectura `iw dev` previa de confirmación y un watchdog de reversión.
