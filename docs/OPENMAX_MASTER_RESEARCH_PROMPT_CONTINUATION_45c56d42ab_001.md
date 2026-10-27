<!-- doc-head: OPENMAX_MASTER_RESEARCH_PROMPT.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](OPENMAX_MASTER_RESEARCH_PROMPT.md) | Part 1/2
<a id="6-zeroclaw--agentes-por-cpe-investigación-crítica"></a> [6. ZeroClaw / agentes por CPE: investigación crítica](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#6-zeroclaw--agentes-por-cpe-investigación-crítica) | <a id="7-investigación-adicional-ideas-no-obvias-pero-falsables"></a> [7. Investigación adicional: ideas no obvias, pero falsables](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#7-investigación-adicional-ideas-no-obvias-pero-falsables) | <a id="8-plan-de-pruebas-por-etapas-con-gates"></a> [8. Plan de pruebas por etapas con gates](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#8-plan-de-pruebas-por-etapas-con-gates) | <a id="etapa-0--auditoría-de-estado-y-no-duplicación"></a> [Etapa 0 — Auditoría de estado y no duplicación](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#etapa-0--auditoría-de-estado-y-no-duplicación) | <a id="etapa-1--experimentos-offline-y-prototipos-seguros"></a> [Etapa 1 — Experimentos offline y prototipos seguros](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#etapa-1--experimentos-offline-y-prototipos-seguros) | <a id="etapa-2--banco-dedicado-lectura-y-ejecución-temporal"></a> [Etapa 2 — Banco dedicado, lectura y ejecución temporal](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#etapa-2--banco-dedicado-lectura-y-ejecución-temporal) | <a id="etapa-3--rf-networking-cooperativo-aislado"></a> [Etapa 3 — RF networking cooperativo aislado](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#etapa-3--rf-networking-cooperativo-aislado) | <a id="etapa-4--piloto-escalonado-sujeto-a-aprobación-adicional"></a> [Etapa 4 — Piloto escalonado, sujeto a aprobación adicional](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#etapa-4--piloto-escalonado-sujeto-a-aprobación-adicional) | <a id="etapa-5--escala-1800-solo-diseño-hasta-tener-evidencia"></a> [Etapa 5 — Escala 1.800 (solo diseño hasta tener evidencia)](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#etapa-5--escala-1800-solo-diseño-hasta-tener-evidencia) | <a id="9-métricas-y-requisitos-de-aceptación"></a> [9. Métricas y requisitos de aceptación](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#9-métricas-y-requisitos-de-aceptación) | <a id="10-entregables-producir-archivos-en-el-repo-no-solo-una-respuesta-de-chat"></a> [10. Entregables: producir archivos en el repo, no solo una respuesta de chat](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#10-entregables-producir-archivos-en-el-repo-no-solo-una-respuesta-de-chat) | <a id="11-formato-de-respuesta-final-que-quiero"></a> [11. Formato de respuesta final que quiero](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_002.md#11-formato-de-respuesta-final-que-quiero)

<!-- stage822a-payload-begin -->
# MASTER PROMPT — OpenMax: Cooperative CPE Networking, Distributed Compute & Programmable WISP

## Tu rol y objetivo

Actuá como **Principal Wireless Systems Architect + Embedded Linux/Firmware Reverse Engineer + Distributed Systems Engineer + Adversarial Test Engineer**. Estás trabajando **dentro del repositorio OpenMax / FuturaMAX**: `https://github.com/wolverin0/openmax`. El operador administra un WISP de aproximadamente **1.800 dispositivos**, principalmente Ubiquiti airMAX AC y LTU, y dispone de un banco de pruebas con radios reales, firmware, herramientas de ingeniería inversa, capturas y scripts propios.

**Objetivo:** identificar, diseñar, implementar y, cuando esté autorizado y sea seguro, **probar en hardware de laboratorio** formas de aprovechar la flota existente en dos líneas independientes pero compatibles:

1. **Computación distribuida de propósito general** usando capacidad ociosa en CPEs (por ejemplo 02:00–07:00, solo si el servicio está realmente ocioso), sin degradar servicios de clientes.
2. **Networking cooperativo y radios programables**: averiguar si un CPE con buen enlace puede ayudar a uno con mal enlace; usar todas las mediciones de AP/CPE para optimizar capacidad, calidad y resiliencia; desarrollar scripts/mini-workers de alto valor.

Una tercera línea, **agentes compactos (ZeroClaw)**, se investiga críticamente para determinar si conviene ejecutarlos en los radios, adaptarlos o usarlos solamente en un controlador central. **No partas de que distribuir agentes equivale a sumar potencia de IA.**

No te limites a responder “no se puede” por las limitaciones de fábrica: existen reverse engineering, OpenWrt, parches ya desarrollados en OpenMax y hardware alternativo. Pero **tampoco afirmes que algo funciona sin pruebas reproducibles**. Buscá mecanismos concretos, condiciones de factibilidad y experimentos de refutación baratos.

## 0. Reglas de trabajo obligatorias

- **Primero leer el repo y verificar el HEAD real.** Empezar por `AGENTS.md`, `README.md`, `docs/CURRENT_STATE.md` (especialmente el addendum más nuevo), `docs/DECISIONS.md`, `docs/RESEARCH_LEDGER.md`, `docs/ADVERSARIAL_REVIEW_STAGE10_11.md`, `docs/HARDWARE_MATRIX.md`, `knowledge/HARDWARE_MATRIX.md`, `knowledge/AIROS_CONTROL_SURFACE.md`, `knowledge/RADIO_FIRMWARE_ANALYSIS.md`, `knowledge/QCA988X_CONTROL_BOUNDARY.md`, `knowledge/CUSTOM_MAC_GO_NO_GO.md`, `docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md`, `docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md`, `docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md`, y la documentación de testbed, telemetría y recuperación. Consultar código y evidencia cruda, no solamente resúmenes.
- **No repetir** lo que ya está demostrado, salvo que necesites un control independiente para validar una nueva hipótesis. Registrar resultados anteriores y sus límites antes de diseñar otro test.
- Diferenciar **CONFIRMADO EN BANCADA**, **CONFIRMADO POR ANÁLISIS ESTÁTICO**, **DEMOSTRADO EN HARDWARE SIMILAR**, **HIPÓTESIS**, **REFUTADO** y **NO VERIFICADO**. No convertir un símbolo en binario, un hook o un menú oculto en una función RF validada.
- No asumir que LiteBeam Gen2, Loco5AC, Rocket Prism 5AC y LTU comparten radios, CPU, RAM, flash, firmware, modos o rutas de rescate. Armar la matriz por **modelo + revisión + sysid + firmware + rol**.
- Todo experimento debe tener **hipótesis, mecanismo, precondiciones, dispositivos/versión, baseline, contrafactual, métricas, criterio PASS/FAIL, criterio STOP, rollback y artefactos de evidencia**.
- Preferir experimentos A/B/A/B, con repeticiones, tests bajo carga mixta y medidas p50/p95/p99. Demostrar ganancias netas de sector, no un único throughput aislado favorable.
- **No tocar producción de forma disruptiva, no flashear, no escribir en MTD/EEPROM/ART/calibración, no cambiar RF/canales/potencia/DFS, no cargar módulos, no hacer fuzzing ni reiniciar equipos de producción sin autorización específica.** En producción, a lo sumo inventario/telemetría pasiva y estrictamente dentro del alcance autorizado. No modificar equipos de clientes ni usar CPU/energía para tareas ajenas al servicio sin autorización adecuada.
- Los tests que puedan romper la conectividad se hacen en banco con equipo dedicado, control por Ethernet, alimentación y recovery físico/TFTP probado, snapshot de configuración/particiones, y secuencia de restauración verificable. **Un SSH exitoso no equivale a recuperación segura.**
- Nunca activar trabajos arbitrarios con shell desde un LLM, ni permitir a 1.800 radios ejecutar instrucciones generadas libremente. Los cambios de RF/reinicio necesitan gates determinísticos y aprobación. No copiar secretos, datos de clientes ni material identificable a reportes.
- Si no hay hardware accesible, avanzar con RE estático, emulación, cross-compile, análisis de interfaces, scripts read-only y protocolos de prueba. **No inventar una medición ni declarar haber corrido comandos que no se ejecutaron**.
- No pedir confirmación por cada paso de investigación offline: trabajá autónomamente dentro del alcance seguro. Para acciones fuera del alcance seguro, crear el plan y detener esa acción puntual hasta autorización.

## 1. Inventario de lo que ya tenemos (hacer primero)

Construir una **Matriz de Capacidades Reales** con, como mínimo:

- LiteBeam 5AC Gen2; NanoStation Loco5AC (y NanoStation 5AC cuando aplique); Rocket Prism 5AC Gen2; LTU Lite; LTU Rocket; cualquier otro hardware realmente presente en el inventario.
- SoC, ISA/endianness/ABI (MIPS 74Kc, ARM Cortex-A9, etc.), núcleos, frecuencia real, RAM usable bajo carga, flash libre y RAM tmpfs, kernel/libc/toolchain, soporte de procesos/hilos, permisos, init/cron, particiones/calibración, watchdog y temperatura/potencia cuando haya sensores.
- Radio principal y **radio secundario verdadero** por revisión: chipset, banda, front-end/PA/LNA, antena real, polarización, aislamiento, canales, drivers y vdevs. Diferenciar radio Wi-Fi de management, radio dedicado a AirView, BLE y cadenas MIMO del **mismo** transceptor.
- Stack de radio por firmware: airOS AC, OpenWrt/ath10k, ath10k-CT, LTU AME, radio firmware, TDMA, modos 802.11 estándar, 4addr/WDS/TEB, `iw list`/combinaciones de interfaces y límites de concurrencia.
- Herramientas disponibles de observabilidad (`mca-status`, `wstalist`, SNMP, procfs, sysfs, `iw`, debugfs, `iwpriv`, `ubntspecd`, `ame-debug-sched`, etc.) y cuáles están probadas realmente.
- Soporte de carga y persistencia de scripts/binarios: `airOS -cs`, cron stock cuando aplique, OpenWrt procd, despliegue RAM-only, compatibilidad con firmware exacto; detectar el límite documentado del buffer cron de airOS 8, hashes/relocations y riesgos de persistencia o desgaste de flash.

**Atención especial a lo que OpenMax ya descubrió:** los parches y límites de `ubnt_poll_host.ko`/ETH_P_TEB; la asociación híbrida stock airOS ↔ OpenWrt; `wifi1` del Rocket Prism con AirView y TX blanking; LTU `amesoc3` + AD9361 y el Arria 10 **solamente en modelos que realmente lo posean**; 4096-QAM y OFDMA como rutas confirmadas estáticamente pero no automáticamente ganancia RF en vivo. Auditar contradicciones y vigencia de cada hallazgo.

**Entregable:** tabla `confirmed / possible / blocked / evidence / lab test`, con links a archivos y commits.

## 2. Pregunta central: ¿puede una CPE buena ayudar a otra mala SIN hardware adicional?

No usar “mesh” como palabra mágica. Separar con precisión **relaying de tráfico**, **coordinación radio**, **diversidad cooperativa**, **asistencia de mediciones** y **redireccionamiento por otra ruta**.

### 2.A — Relay por el radio principal de 5 GHz (hipótesis prioritaria)

Analizar si el QCA988x y cada stack soportan alguna de estas combinaciones **simultáneamente**:

- STA uplink al sector + AP virtual local (`managed + AP`);
- STA uplink + 802.11s mesh point;
- STA uplink + otra STA / P2P / WDS / 4-address;
- AP/STA de mismo canal, diferencia entre soporte anunciado por `iw phy` y capacidad real del firmware/driver;
- 802.11s standalone, BATMAN-adv o ruteo IP en modo experimental cuando el uplink principal no debe mantenerse;
- interoperabilidad con `airOS 8`, módulos parcheados, OpenWrt, vendor IE y protocolo airMAX/TDMA: identificar exactamente **quién controla el airtime, ACK, rate y la transmisión de frames**.

Probar/explicar si STA↔STA realmente intercambia paquetes en el aire o si todo necesariamente pasa por AP; un túnel B→AP→A→AP puede duplicar tráfico **sin mejorar el enlace débil de B**. No llamar eso relay RF útil.

Auditar la restricción física de **antenas direccionales de las CPE apuntando al AP**, con enlace CPE A↔B posiblemente por lóbulos laterales/traseros; patrones de radiación, ángulos, Fresnel/LOS, distancia, interferencia, potencia efectiva y sensibilidad. Medir RSSI/SNR/MCS/PER **A↔B**, no inferir por buena señal A↔AP. Examinar airtime half-duplex de dos saltos, presupuesto de banda, fairness, latencia y saturación. El relay solo es aceptable si mejora **goodput utilizable / p95-p99 RTT / estabilidad / capacidad del sector** bajo carga real.

Investigar **si RX cooperativa/joint decoding/distributed MIMO** es siquiera posible con sincronización de reloj/fase, IQ baseband y control PHY del hardware concreto. Si no hay acceso a muestras/sincronía, descartarlo justificadamente en vez de dedicar semanas a una ilusión.

### 2.B — Radio 2.4 GHz de management (verificación corta, probable NO-GO)

El operador ya señaló que la antena secundaria es pequeña y no sirve para grandes distancias. No diseñar una mesh masiva basada en esa antena. Verificar **modelo por modelo**:

- Antena/ganancia/patrón, chipset, driver, alcance real esperable y throughput, Wi-Fi de management vs BLE.
- Si puede transportar datos IP y crear enlaces A↔B sin afectar gestión y sin reinstalar firmware.
- Si hay alguna oportunidad acotada (edificios contiguos, emergencia, mediciones) y umbral medido para descartarla.

**Regla de salida:** si link budget, funcionalidad de firmware o throughput efectivo son insuficientes, emitir NO-GO temprano; no seguir gastando recursos solo porque existe `wifi1`.

### 2.C — ¿Qué alternativa sí resuelve el problema?

Comparar:

1. Segundo radio/enlace físico en ubicación A como relay B→A→AP;
2. CPE o AP vecino de otro sector con mejor geometría y **re-asociación** de B;
3. Red de backup (enlace alternativo preexistente), roaming gestionado o multi-WAN cuando realmente exista un segundo uplink;
4. CPE A y B conectados por Ethernet o enlace dedicado, con L3 y políticas de tráfico;
5. Reorientación/antena/cambio de altura/reubicación de sector (solución RF sin complejidad mesh);
6. CPE A ayuda solo como **sensor** para diagnosticar a B (posibilidad inmediata sin relay físico).

Incluir comparación de BOM/costo de instalación/consumo, slots/airtime, QoS, compatibilidad y soporte operativo. **No prometer auto-relaying con la misma radio si no supera test de asociación simultánea + RF geométrica + airtime neto.**

### 2.D — Pruebas concretas de banco

Diseñar suite incremental con 3–5 radios propios, luego testbed real de 10–20 estaciones si pasa etapas iniciales:

- Leer combinaciones de interfaces, drivers, SKU, antena y calibration data **sin modificar**.
- Perfil 1: AP–STA normal; perfil 2: A↔B standalone; perfil 3: STA+AP; perfil 4: STA+mesh; perfil 5: tráfico B→A→AP (si soportado); perfil 6: alternativa de radio extra.
- Baseline directa B→AP con buen/mal enlace de forma controlada; medir distancia/obstáculos con escenarios representativos, no solamente banco de proximidad que sobrestima capacidad.
- Uplink/downlink y bidireccional, 1 y N flujos, UDP/TCP, 20/40/80 MHz **solo donde el entorno de laboratorio y normativa lo permiten**, pérdida, reintentos, MCS, interferencia, jitter, loaded latency, CPU/RAM/temperatura y degradación de A y de terceros.
- Cortar A, cortar B, re-asociar AP, interferencia breve, reinicio, pérdida de management, recuperación automática, bucles/rutas/vlan/MTU/NAT, estabilidad durante horas.
- Si falla una precondición crítica, documentar causa raíz y cerrar esa rama.

## 3. Aprovechar las CPE como sensores cooperativos: optimización WISP

Investigar e implementar primero en central/telemetría read-only, reutilizando controladores, modelos de historia, FFT, airtime, scripts y pruebas de OpenMax:

- **Airtime tax por CPE:** detectar clientes con tiempo de aire desproporcionado frente a bytes útiles, malos MCS, retries, colisiones y límites de estimación en QCA988x (no confundir estimación por `last_tx_bitrate` con airtime medido).
- **Diagnóstico diferencial por ubicación:** varios clientes degradados vs solo uno; hipótesis interferencia localizada, obstrucción, alineación, sector, energía, backhaul, CPE, cable, PoE o saturación.
- **Mapas RF dinámicos / fingerprint histórico por cliente:** predicción de degradación, vegetación, humedad/clima si hay correlación válida, variación de cadenas RX, CINR/MCS, calidad vs distancia y geografía.
- **Detección de interferencias:** cuáles datos son realmente accesibles en AirView/wifi1 y cuáles corresponden al canal que presta servicio; no confundir el espectro 2.4 con el 5 GHz del cliente ni declarar FFT continua sin validar impacto.
- **Recomendador de reasociación:** identificar una mejor AP/sector con capacidad y compatibilidad reales antes de mover una estación.
- **Scheduler/AQL/aggregation/RTS/ACK/rate masks/ATPC:** comparar oportunidades con lo ya implementado y con el control boundary real; no plantear knobs descartados por experimentos previos.
- **Autorreparación acotada:** detección y acción sobre problemas realmente reversibles; primero recomendaciones, luego canary con rollback y aprobaciones.
- **Tests de QoE de bajísimo impacto:** DNS/latencia a primer salto y POP, pérdida/jitter; evitar throughput tests simultáneos que saturen el sector.
- **Planificación de despliegue:** identificar el **menor cambio físico** que produciría mayor mejora neta (reorientación, un AP, ancho de canal, backhaul, relay dedicado), con estimación de confianza.

Para cada oportunidad: especificar señal medible, de dónde sale el dato, exactitud, frecuencia de muestreo, costo sobre CPE/AP/red, falsos positivos y cómo validarla contra incidentes reales.

## 4. Scripts útiles y ejecución sobre airOS / LTU / OpenWrt

Crear un **catálogo priorizado de scripts** clasificado por lectura/diagnóstico/acción, firmware exacto, costo CPU/RAM, seguridad y reversibilidad. Candidatos:

1. Heartbeat enriquecido con RSSI/SNR/MCS/retries/noise/CINR/frecuencia/cadena/CPU/mem/temp y timestamp fiable.
2. Análisis local barato de anomalías y reportes compactos (evitar streams pesados).
3. Scheduler de trabajos ociosos con prioridad mínima y kill switch.
4. Watchdog de servicio (diferenciar asociación RF, gestión y conectividad de cliente) con recuperación segura.
5. Captura breve de métricas en evento (no `tcpdump` permanente ni datos privados).
6. Verificación de drift de firmware/config/kernel y checksum de particiones de calibración **solo lectura**.
7. Detección PoE/cable/reboot/errores Ethernet y consumo de memoria.
8. Sondeo pequeño y coordinado de latencia para detectar congestión y problemas de ruta.
9. Canales de diagnóstico RF mediante interfaces existentes donde no impacten al radio de servicio.
10. Pruebas de microbench acotadas solo en banco.

Investigar APIs/CLI ya presentes y evaluar cuándo conviene **no ejecutar scripts en 1.800 CPEs** porque SNMP/SSH/controller puede resolverlo con menor riesgo. Separar airOS stock, `-CS`, módulo temporal en RAM, cron stock, OpenWrt y LTU. Verificar persistencia ante reinicio y upgrade; no escribir flash periódicamente. Diseñar formato de paquete firmado, compatibilidad y desinstalación.

## 5. General-purpose distributed computing: objetivo original, sin desviar la investigación

No convertir este proyecto en “solo monitoreo de red”. Diseñar y medir un **cluster de trabajos batch** usando CPUs de CPE durante 02:00–07:00 **o cuando exista ociosidad real**. El horario no es suficiente: debe medir carga por radio/sector y tener margen por ráfagas y tráfico nocturno.

### 5.A Factibilidad de ejecutar binarios

- Para cada SKU/firmware: CPU/ISA, big/little endian, libc/ABI, kernel syscalls, RAM libre, almacenamiento RAM, tamaño de binario, DNS/TLS/crypto disponible, posibilidad de ejecutar ELF compilado para esa plataforma y sandboxing disponible.
- Evaluar C estático/BusyBox-compatible y Rust `no_std` o mínimo si tiene sentido, `musl`/uClibc según ABI; medir costos reales. No asumir WASM/containers disponibles en MIPS de 64 MB.
- Construir micro-worker sin dependencias excesivas, preferiblemente proceso breve desde `/tmp`, sin writes persistentes ni privilegios innecesarios. Modelar actualizaciones sin tocar RF.
- Revisar cross-compile y QEMU-user **como filtro**, pero validar el binario definitivo en cada firmware real.

### 5.B Benchmarks útiles y comparables

Medir jobs pequeños deterministas y repetibles: SHA-256/hash de buffers no sensibles, compresión pequeña, enteros/floating-point, Monte Carlo independiente, pequeñas matrices o simulaciones. Registrar **trabajo completado por dispositivo-hora y por watt incremental**, no sumar “GHz” o “CPU-hours” como equivalentes a núcleos modernos. Medir cada familia con baseline, 5%/10%/20% de CPU **real aplicado**; priorización y throttling basados en carga; con y sin tráfico real; cinco horas emuladas mediante ventanas repetibles; impacto p95/p99; temperatura; estabilidad; watchdog/OOM.

Estimar escalado desde 5 radios a 20, 100 y 1.800 solo **con datos**, contemplando diversidad de hardware, tasa de disponibles, fallas, overhead de red y de control, congestión en POP, transferencia de inputs/outputs y energía consumida en domicilios. Comparar contra una PC moderna, mini PC, CPU de servidor y cloud, con costos locales verificables cuando se necesiten.

### 5.C Arquitectura de scheduler

Diseñar: controlador central, cola de tareas declarativas y firmas, catálogo de binarios por hash/arquitectura, heartbeats, leases/timeouts, idempotencia, reintentos, deduplicación de resultados, shard/reduce, prioridades, rate limits por AP/sector, verificación de resultados y métricas. Salida solo de red hacia servidor autorizado si se decide usar polling. **Nada de shell arbitrario o agente con permisos globales**. Fallo del controlador = workers dejan de ejecutarse por TTL/lease, no continúan indefinidamente.

Reglas de seguridad concretas: ventana habilitada configurable, CPU/mem max, RAM libre min, carga de sector max, tráfico cliente max, latencia/jitter guard, kill switch central + local, on-demand traffic preemption, watchdog, límites de temperatura/potencia y presupuesto de red por sector. No tratar `nice` como un límite de uso CPU verificable; implementar throttling cuantificable y medir la latencia de interrupción.

<!-- stage822a-payload-end -->
