<!-- doc-head: Wave 335 ES: plan maestro Opus 5.5 - estado global de la red OpenWrt (18 nodos), sintesis del debate de 5 rondas de ancho de canal, techo real multi-CPE en bridge de Panel1 (Wave 334), correccion topologica del operador, Simple Queues vs capacidad RF y hoja de ruta paso a paso -->
Estado: 18/18 nodos en OpenWrt 24.10.4. Debate de 5 rondas cerrado entre Claude y Codex (Gemini fue texto pre-escrito): base VHT40, ancho por CPE via OPMODE_NOTIF todavia sin probar en el aire.
Techo de Panel1 en bridge (Wave 334, 0 iperf3 en el AP): 153.39 Mbps en 40 MHz con la CPU del AP al 80.3%, asi que el AP limita cerca de 150 Mbps. El 147.92 Mbps rotulado 20 MHz es fisicamente dudoso y no se usa como techo.
Correccion del operador: PtP-Colo (ch153, 5765 MHz) esta en el POP Edificio Principal y Panel3 (ch149, 5745 MHz) en Torre Guarida, a 7 km y 2 saltos PtP. No hay interferencia co-sitio entre ellos. En Guarida, Panel3 y Panel2 (5805) estan a 60 MHz.
Los planes comerciales se limitan con Simple Queues de MikroTik (10/15 Mbps): la capacidad RF medida es margen, no lo que ve el cliente.
Siguiente paso: prueba en el aire de OPMODE_NOTIF sobre cpe_200_80, benchmark N de 5 o mas en ventana valle, y despues despliegue gradual con rollback.
<!-- /doc-head -->
# Wave 335 - Plan maestro: ejecucion y estado global

Documento de planificacion, sin escrituras en equipos. Las cifras salen de artefactos locales citados; donde un dato viene
del operador y no tiene recibo local, se marca asi.

## 1. Estado global de la red (al 29/10)

| Area | Estado | Fuente |
| :-- | :-- | :-- |
| Plataforma | 18/18 nodos en OpenWrt 24.10.4, 0 airOS hibrido | `artifacts/observability/full_before_after_report_20261028.json` (seq 2610) |
| Canales Guarida | Panel1 ch48 5240 / Panel2 ch161 5805 / Panel3 ch149 5745, 20 MHz | telemetria IW (Wave 326/329) |
| PtP-Colo | ch153 5765, 20 MHz, en POP Edificio Principal | telemetria IW + correccion del operador |
| Latencia | medianas de ventana 0-15 ms en Panel1/Panel3/PtP-Colo; Panel2 16-33 ms | `docs/WAVE309_SCORECARD_EJECUTIVO_18_NODOS_OPENWRT_ES.md` (v6) |
| Enlaces degradados | cpe_210_9, cpe_200_169 y cpe_210_21 en MCS 0/0 | Wave 324 / Wave 329 |
| Memoria | MemAvailable 2.3-2.8 MiB en cpe_200_223, cpe_210_235 y cpe_210_9 | Wave 329 |
| Panel2 | sin mejora de RTT demostrada contra airOS (AP 8.0 -> 14 ms de mediana) | Wave 317-329 |

## 2. Sintesis del debate de 5 rondas (Wave 330)

Fuente: `debates/001-asymmetric-channel-width-pwo-airtime-engine/synthesis.md`.
- Solo Claude (fable-5-1, max) y Codex (gpt-6-astra, ultra) participaron en vivo.
- Gemini fue texto fijo escrito antes del debate: su "consenso unanime" no cuenta.

**Acuerdos entre Claude y Codex**
- VHT40 como base comprometida. Los cambios de ancho del AP son lentos (permanencia minima 30 min) y transaccionales, solo
  en RAM, con watchdog armado antes de tocar nada (45 s sin DFS, 120 s o CAC+45 s con DFS).
- Ancho por CPE con el aviso VHT Operating Mode Notification (OPMODE_NOTIF):
  - AP -> CPE limita la subida de la CPE;
  - CPE -> AP limita la bajada.
- **No esta probado** que el firmware QCA988x respete ese limite: es la pregunta decisiva.
- El control de tasa de ath10k vive en el firmware, asi que la premisa de minstrel_ht era falsa. AQL y `airtime_weight`
  no fijan el ancho.
- Estrechar de 80 a 20 MHz da como mucho unos +6 dB, no 12.
- El dataset previo era n=1 y no certifica ningun plan.

**Desacuerdos que siguen abiertos**
- Panel1 a 80 MHz: Claude si, tras A/B; Codex lo deja en 40.
- Umbrales por CPE y criterios de certificacion: Codex es mas estricto.

## 3. Techo real multi-CPE en bridge de Panel1 (Wave 334)

Fuente: `artifacts/observability/guarida_panel1_ground_up_fastpath_bridge_20261028.json`.
- **Metodo:** servidor iperf3 en .61 y las 3 CPE como clientes con `-R`, sin ningun proceso iperf3 en el AP .84 (bridge
  puro eth0 <-> phy0-ap0). Hubo 0% de perdida al restaurar.

| Ancho | Agregado | CPU AP | softirq | cpe_200_223 / cpe_200_41 / cpe_200_80 |
| :-- | :-- | :-- | :-- | :-- |
| 40 MHz | **153.39 Mbps** | 80.32% | 54.49% (35.5% cada 100 Mbps) | 68.99 / 70.56 / 13.84 |
| 20 MHz (3 corridas) | 63.95 / 70.45 / 147.92 | 68.7 / 45.4 / 58.2% | 41.86% en la ultima | ver nota |

**Lectura**
- El AP es un MIPS 74Kc de un solo nucleo (AR9342). A 153 Mbps en 40 MHz gasta 80% de CPU, mas de la mitad en softirq.
  Su techo esta cerca de **150 Mbps**, coincidente con la estimacion de Claude en el debate.
- El camino L2 ya es el rapido del kernel (sin br_netfilter). El propio artefacto concluye que no queda una perilla segura
  para subirlo.
- **Nota sobre 147.92 Mbps en 20 MHz:** no es fisicamente plausible en un canal de 20 MHz.
  - Con las tasas PHY de cada cliente (173.3 / 144.4 / ~52 Mbps), ese agregado exige ~92% del airtime con eficiencia MAC
    perfecta; lo normal es 60-70%.
  - El artefacto documenta un bug del parser de ancho que leyo 40 MHz como 20 MHz.
  - Hasta repetirlo con el ancho verificado, el techo de 20 MHz es **~64-70 Mbps** (las otras dos corridas).
- En 40 MHz, cpe_200_80 (la CPE mas debil) recibe solo 13.84 Mbps: la equidad entre CPE sigue siendo el problema, no la
  capacidad total.

**Persistencia "Champion" en .223/.41/.80/.84:** reportada por el operador. No hay recibo de la instalacion en los
artefactos de Wave 334 y no se verifico en este documento.

## 4. Correccion topologica obligatoria (operador)

| Equipo | Ubicacion | Canal |
| :-- | :-- | :-- |
| PtP-Colo AP .62 / STA .54 | POP Edificio Principal | ch153, 5765 MHz |
| Panel3-Guarida .83 | Torre Guarida | ch149, 5745 MHz |
| Panel2-Guarida .82 | Torre Guarida | ch161, 5805 MHz |

- Entre el POP y Guarida hay 7 km y 2 saltos PtP (Edificio Principal -> Almafuerte .60 -> Guarida .61).
  **PtP-Colo y Panel3 nunca se ven por RF: no hay interferencia co-sitio entre ellos.**
- En Torre Guarida, Panel3 (5745) y Panel2 (5805) estan a **60 MHz** entre centros, 40 MHz de borde a borde en 20 MHz.
  El contexto del debate decia 5755 MHz y 50 MHz, y estaba mal.
- **Que corrige esto:**
  - Wave 324 y la sintesis del debate mencionaban la adyacencia 5745/5765 como posible factor. Queda descartada.
  - La degradacion de cpe_210_9 sigue siendo exclusiva de su enlace; la hipotesis principal es el ACK/coverage_class a 2275 m.
- **Lo que sigue en pie:** en Guarida, ensanchar Panel2 o Panel3 a 40/80 MHz consume esos 60 MHz y exige planificar el
  espectro de los dos juntos.

## 5. Simple Queues vs capacidad RF

- **Dato del operador:** cada plan comercial se limita con Simple Queues de MikroTik a 10/15 Mbps. Lo que ve el cliente
  lo fija esa cola, no el radio.
- **Capacidad RF real medida:**
  - Panel1 bridge: 153 Mbps en 40 MHz y ~64-70 Mbps en 20 MHz;
  - una sola CPE: 112-122 Mbps en 40 MHz (Wave 331).
- **Consecuencias:**
  1. Con planes de 10/15 Mbps, un sector de 20 MHz bien enlazado tiene margen de 4-7 planes simultaneos a tope antes de
     saturar. El limite practico es la equidad (la CPE debil con MCS bajo consume mas airtime) y la latencia bajo carga.
  2. "Velocidad del cliente" y "capacidad del sector" no se mezclan en informes. Un test sin cola mide el radio; un test
     con cola mide el plan.
  3. Ensanchar a 40 MHz no le da mas velocidad a un cliente de 15 Mbps. Da margen de sector y menos airtime por bit,
     que si mejora latencia y equidad en hora pico.
  4. Para subir planes (50/100 Mbps) aplican los criterios del debate. El techo de ~150 Mbps del AP vuelve no
     certificable un plan de 150 Mbps en este SoC.

## 6. Hoja de ruta paso a paso

**Paso 1 - Prueba en el aire de OPMODE_NOTIF** (requiere aprobacion del operador; escritura reversible en RAM)
- Objetivo: saber si el firmware QCA988x respeta el ancho por CPE.
- Herramienta: un binario chico `fmx_omn` (libnl-tiny, `NL80211_CMD_FRAME`). Envia la accion VHT
  `[0x15, 0x02, opmode]`: categoria 21, accion 2, opmode = ancho en bits 0-1 y NSS-1 en bits 4-6. Hay que construirlo; no
  existe todavia.
- Ensayo: en Panel1 a 40 u 80 MHz, mandar AP -> cpe_200_80 opmode de 20 MHz. Volver con opmode del ancho original.
- **Prediccion falsable:**
  - `iw event` registra `sta opmode changed`;
  - `station dump` muestra 20 MHz con VHT-MCS;
  - la subida de cpe_200_80 pasa de MCS3 a ~MCS5 NSS1 con +3..6 dB.
- Captura de PPDU UL/DL para ver el ancho real en el aire.
- Criterio de corte: si el firmware ignora el limite, el ancho asimetrico VHT se descarta. Queda el fallback HT20/HT40 con
  reasociacion (`disable_ht40` / `disable_vht`) en ventana 03-05 h.

**Paso 2 - Benchmark N de 5 o mas en ventana valle**
- Panel1 en bridge puro como Wave 334 (0 iperf3 en el AP), en 20, 40 y 80 MHz, 5 o mas corridas por ancho.
- Registrar por cada corrida el agregado, el reparto por CPE, la CPU y el softirq del AP, el RTT p95/p99 bajo carga y
  el **ancho verificado con el parser corregido**.
- Repetir 20 MHz para confirmar o descartar el 147.92 Mbps.
- Ventana valle (madrugada) para no afectar clientes. Informar mediana e intervalo, no la mejor corrida.

**Paso 3 - Despliegue gradual con rollback** (solo si los pasos 1 y 2 pasan)
1. **Canario en Panel1-Guarida:** VHT40 comprometido + controlador solo en RAM. Transaccion
   PREPARE -> APPLY -> VERIFY -> ACCEPT/ROLLBACK, watchdog de 45 s y 72 h de observacion antes de comprometer.
2. **Paneles con espectro limpio sin DFS:** se ordenan por cantidad de CPE fuertes y factibilidad de espectro. El orden
   exacto entre ellos no tiene evidencia todavia.
3. **Panel2 y Panel3 de Guarida:** solo con plan de espectro conjunto, 40 MHz como maximo y aislamiento medido.
4. **Por cada sector:** verificar Simple Queues intactas y comparar latencia en hora pico antes y despues.

**En paralelo** (fuera del ancho de canal)
- **cpe_210_9:** prueba reversible de `distance` / coverage_class (~2300 m) en panel3_ap con cpe_210_9, vigilando a sus
  hermanas.
- **cpe_200_169 y cpe_210_21:** revisar el enlace y la causa del SSH intermitente.
- **LiteBeam con poca memoria:** vigilar MemAvailable antes de agregarles servicios.

## 7. Limites de este plan

- Los datos de Simple Queues y de la persistencia Champion son del operador, sin recibo local.
- Todo lo de OPMODE_NOTIF esta sin probar en el aire. El binario `fmx_omn` no existe.
- Sin afirmacion causal, de QoE ni de champion para ancho asimetrico.
