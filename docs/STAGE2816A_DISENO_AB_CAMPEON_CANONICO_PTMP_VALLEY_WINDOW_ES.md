<!-- doc-head: Stage 2816A (W337 P5) ES: diseno offline del experimento A1-B1-A2-B2 en ventana valle que reduce los tres juegos de valores champion PtMP (ledger v19, lectura en vivo y script del 29-10) a un champion canonico, con tres bloques de un factor -->
Que cubre: los tres juegos reales de valores (fq_codel, AQL por AC, aql_threshold, nf_cal_period) en AP y CPE de Panel1, la correccion de las cifras del despacho, la precondicion de relectura, tres bloques contrabalanceados de un factor, metricas, regla de decision fijada antes de medir, watchdog de 45 s y riesgos.
Estado: solo diseno. 0 SSH, 0 escrituras en radios. Ejecutarlo requiere autorizacion del operador y la relectura previa de Panel1 (W337 P1).
Datos maquina: artifacts/autoresearch/wave337_canonical_champion_ab_design_and_vault_sync.json. Matriz de origen: docs/MATRIZ_MAESTRA_AVANCES_Y_BRECHAS_E2E_ES.md.
Leer cuando: haya que elegir el champion PtMP canonico o antes de copiar valores champion a Panel3, Panel2 o PtP-Colo.
<!-- /doc-head -->
# Stage 2816A: diseno A/B del champion canonico PtMP en ventana valle (W337 P5)

## 1. Los tres juegos de valores, segun las fuentes

| Ajuste | Ledger v19 (Stage 55A) | Lectura en vivo (telemetria 29/10 01:25 UTC) | Script del 29/10 (fix de cpe_200_80) |
| :-- | :-- | :-- | :-- |
| AP fq quantum/limit/memoria | 4542 / 2048 / 4 MiB | 3028 / 512 / 3 MiB | 4542 / 2048 / 4 MiB (declarado) |
| AP AQL BE (low/high us) | 1500 / 3000 | sin sonda | sin cambio declarado |
| AP aql_threshold | 5000 | 4000; luego 5000 (W335 10:25 UTC) | 5000 |
| CPE fq quantum/limit/memoria | 1514 / 1024 / 4 MiB | 300 / 8192 / 4 MiB | 1514 / 1024 / 4 MiB |
| CPE AQL VI (low/high) | 1200 / 2400 | sin sonda | 1000 / 2000 |
| CPE AQL BE (low/high) | 900 / 1500 | sin sonda | 1500 / 3000 |
| CPE aql_threshold | 4000 | 5000 (W335) | 5000 |
| nf_cal_period | 30 (perfil base multi-CPE) | sin sonda | 120 |

Fuentes: `artifacts/autoresearch/champion_state_ledger.json` (stage55a_champion_v19 y el perfil openwrt_lap120_ptmp_multicpe_champion),
la auditoria W336 y `tools/panel1/deploy_cpe_champion_persistence.py`.

**Correccion del despacho.** El despacho decia "AP en vivo fq_quantum=300" y "script fq_quantum=3000". Las fuentes dicen otra cosa:
- 300 es lo que se lee en las CPE.
- Los AP leen 3028.
- El script declara 1514 en las CPE y 4542 en el AP.

El diseno usa los valores de las fuentes.

**Lectura clave.** El script y el ledger coinciden en el fq de la CPE y en el fq del AP. La discrepancia real es otra:
1. **fq del AP:** lo leido (3028/512/3 MiB) contra lo declarado (4542/2048/4 MiB).
2. **AQL de la CPE:** VI, BE y aql_threshold del ledger contra los del script.
3. **nf_cal_period:** 30 contra 120.
4. **Si el script de CPE quedo aplicado:** la ultima lectura mostraba los defaults 300/8192.

## 2. Precondicion: relectura (bloque 0, solo lectura)

Antes de cualquier escritura se relee cada valor de la tabla en .84 y sus 3 CPE. Es la tarea W337 P1.
- Si las CPE leen 1514/1024 y AQL del script, el brazo "script" es el estado actual.
- Si leen 300/8192, el script no se aplica: ese hallazgo va primero y el bloque 2 se replantea.
- txpower y regdomain se registran pero **quedan fuera** del experimento. Se mantienen constantes por el riesgo regulatorio de US 23 dBm.

## 3. Diseno: tres bloques contrabalanceados de un factor

Cada bloque cambia **un solo factor** y deja el resto en el valor leido en el bloque 0.
- **Secuencia por bloque:** A1, B1, A2, B2 la primera noche y B1, A1, B2, A2 la segunda.
- **Fases:** 10 min cada una (2 min de estabilizacion + 8 de medicion).
- **Duracion:** unos 48 min por bloque y noche.
- **Calendario:** un bloque por ventana valle de 03:00 a 05:00 ART, asi que son 6 noches para los 3 bloques.

| Bloque | Brazo A (control) | Brazo B (candidato) | Nodos |
| :-- | :-- | :-- | :-- |
| 1 - fq del AP | 3028 / 512 / 3 MiB (lectura) | 4542 / 2048 / 4 MiB (ledger = script) | .84 |
| 2 - AQL de la CPE | VI 1200/2400, BE 900/1500, threshold 4000 (ledger) | VI 1000/2000, BE 1500/3000, threshold 5000 (script) | 3 CPE, fq fijo 1514/1024/4 MiB |
| 3 - nf_cal_period | 30 (ledger) | 120 (script) | .84 y 3 CPE |

**Orden de los bloques.** Va primero el 1, porque es el AP con fq_overmemory 4070. Despues el 2 y por ultimo el 3, que es el de menor efecto esperado.

**Carga.**
- Servidor iperf3 en .61 y las 3 CPE como clientes, igual que en W334. Ningun proceso iperf3 en el AP.
- Por fase: 3 corridas TCP de 30 s con -R (bajada) y 3 sin -R (subida).
- Ping de 300 muestras con carga a cada CPE desde el colector.
- Las Simple Queues de MikroTik quedan intactas. La carga va por el bridge, sin pasar por las colas de plan.

**Aplicacion y reversion.**
- Todo se escribe solo en RAM (debugfs o sysctl). Cero `uci commit` y cero escrituras en flash.
- Antes de cada fase B se arma un watchdog de 45 s (canal 48, sin DFS) que restaura los valores A si no aparece la marca de aceptacion.
- Cada fase lee los valores al principio y al final. Si difieren de lo que el brazo debia tener, la fase se **invalida**.

## 4. Metricas y regla de decision (fijadas antes de medir)

**Metrica primaria:** RTT p95 con carga hacia las 3 CPE (mediana de las 3 CPE por fase).

**Secundarias:**
- goodput agregado de bajada y de subida;
- perdida de ping;
- delta de tx_failed;
- delta de fq_overmemory;
- MemAvailable de AP y CPE;
- CPU y softirq del AP.

**El brazo B gana el bloque si se cumplen las cuatro condiciones, en ambas noches:**
1. El p95 mejora al menos 10% de A1 a B1 y de A2 a B2.
2. El goodput no cae mas de 3%.
3. La perdida y el fq_overmemory no empeoran.
4. Ningun MemAvailable baja de 2 MiB.

**Empate o resultado mixto:** se queda el valor del ledger v19, porque es el que tiene historia de validacion.

**Invalidez:** si una noche tiene una fase invalidada, se repite el bloque. Nunca se decide con una sola noche.

**Champion canonico** = brazo ganador del bloque 1 (AP) + del bloque 2 (CPE) + del bloque 3 (nf_cal). Se registra en el ledger como v20 solo despues de 72 h de observacion en Panel1.

## 5. Riesgos y limites del diseno

- **Hotplug de la CPE:** `/etc/hotplug.d/net/99-fmx-cpe-champion` reaplica los valores del script ante cualquier evento de red. Puede pisar el brazo A del bloque 2.
  - **Mitigacion:** la relectura de inicio y fin de cada fase.
  - **Si pasa:** documentar el evento y repetir la fase.
- **Tamano de muestra:** 3 CPE y 2 noches por bloque dan poca potencia estadistica.
  - Solo detecta efectos grandes, de 10% o mas en p95.
  - Efectos menores se reportan como "sin diferencia demostrada".
- **Firmware:** el control de tasa de ath10k vive en el firmware, asi que hay variacion entre noches por RF. El contrabalanceo la compensa solo en parte.
- **Alcance:** Panel3, Panel2 y PtP-Colo no entran. El champion canonico se valida primero en Panel1.
  - Copiarlo a otros paneles es otra decision, con su propia prueba.
- **Sin medicion:** este documento no mide nada y no afirma causalidad.

## 6. Indexacion de la matriz W336 (parte 2 del contrato)

- **hyperresearch.db:** la matriz W336 queda indexada como nota evergreen, con el resumen, los hallazgos y la ruta a la matriz y al JSON. Las ids van en el JSON de este stage.
- **MemoryMaster:** project:futuramax recibe un claim con el diseno y la correccion de cifras. Sin IPs completas ni nombres de abonados.
