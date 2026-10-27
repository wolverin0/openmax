<!-- doc-head: OPENMAX_MASTER_RESEARCH_PROMPT.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](OPENMAX_MASTER_RESEARCH_PROMPT.md) | Part 2/2
<a id="master-prompt--openmax-cooperative-cpe-networking-distributed-compute--programmable-wisp"></a> [MASTER PROMPT — OpenMax: Cooperative CPE Networking, Distributed Compute & Programmable WISP](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#master-prompt--openmax-cooperative-cpe-networking-distributed-compute--programmable-wisp) | <a id="tu-rol-y-objetivo"></a> [Tu rol y objetivo](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#tu-rol-y-objetivo) | <a id="0-reglas-de-trabajo-obligatorias"></a> [0. Reglas de trabajo obligatorias](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#0-reglas-de-trabajo-obligatorias) | <a id="1-inventario-de-lo-que-ya-tenemos-hacer-primero"></a> [1. Inventario de lo que ya tenemos (hacer primero)](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#1-inventario-de-lo-que-ya-tenemos-hacer-primero) | <a id="2-pregunta-central-puede-una-cpe-buena-ayudar-a-otra-mala-sin-hardware-adicional"></a> [2. Pregunta central: ¿puede una CPE buena ayudar a otra mala SIN hardware adicional?](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#2-pregunta-central-puede-una-cpe-buena-ayudar-a-otra-mala-sin-hardware-adicional) | <a id="2a--relay-por-el-radio-principal-de-5-ghz-hipótesis-prioritaria"></a> [2.A — Relay por el radio principal de 5 GHz (hipótesis prioritaria)](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#2a--relay-por-el-radio-principal-de-5-ghz-hipótesis-prioritaria) | <a id="2b--radio-24-ghz-de-management-verificación-corta-probable-no-go"></a> [2.B — Radio 2.4 GHz de management (verificación corta, probable NO-GO)](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#2b--radio-24-ghz-de-management-verificación-corta-probable-no-go) | <a id="2c--qué-alternativa-sí-resuelve-el-problema"></a> [2.C — ¿Qué alternativa sí resuelve el problema?](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#2c--qué-alternativa-sí-resuelve-el-problema) | <a id="2d--pruebas-concretas-de-banco"></a> [2.D — Pruebas concretas de banco](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#2d--pruebas-concretas-de-banco) | <a id="3-aprovechar-las-cpe-como-sensores-cooperativos-optimización-wisp"></a> [3. Aprovechar las CPE como sensores cooperativos: optimización WISP](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#3-aprovechar-las-cpe-como-sensores-cooperativos-optimización-wisp) | <a id="4-scripts-útiles-y-ejecución-sobre-airos--ltu--openwrt"></a> [4. Scripts útiles y ejecución sobre airOS / LTU / OpenWrt](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#4-scripts-útiles-y-ejecución-sobre-airos--ltu--openwrt) | <a id="5-general-purpose-distributed-computing-objetivo-original-sin-desviar-la-investigación"></a> [5. General-purpose distributed computing: objetivo original, sin desviar la investigación](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#5-general-purpose-distributed-computing-objetivo-original-sin-desviar-la-investigación) | <a id="5a-factibilidad-de-ejecutar-binarios"></a> [5.A Factibilidad de ejecutar binarios](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#5a-factibilidad-de-ejecutar-binarios) | <a id="5b-benchmarks-útiles-y-comparables"></a> [5.B Benchmarks útiles y comparables](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#5b-benchmarks-útiles-y-comparables) | <a id="5c-arquitectura-de-scheduler"></a> [5.C Arquitectura de scheduler](OPENMAX_MASTER_RESEARCH_PROMPT_CONTINUATION_45c56d42ab_001.md#5c-arquitectura-de-scheduler)

<!-- stage822a-payload-begin -->
## 6. ZeroClaw / agentes por CPE: investigación crítica

Investigar el repo upstream y su **versión actual**, no asumir compatibilidad por anuncios de “ARMv7/MIPS” ni por PRs sin test. Revisar:

- Tamaño real del binario optimizado, RAM de arranque/pico, CPU idle, RAM ante requests, stack, TLS, crates y dependencias obligatorias.
- Cross-compile para `mips-unknown-linux-*` / MIPS endian real y ARMv7 EABI del `amesoc3`, ABI/libc/kernel mínimos, atomics 64-bit y syscalls antiguos. Diferenciar **compila**, **arranca** y **opera estable sin OOM**.
- Docker/QEMU y hardware bench; tamaño de los artefactos frente a flash de 16 MB/64 MB RAM para airMAX y recursos reales LTU. No asumir que 256 MB RAM significa 256 MB disponibles para apps.
- Riesgo de claves API en dispositivos domiciliarios, proveedores remotos, seguridad del shell/tools, update chain, exposición pública y acciones involuntarias.
- Comparar: (A) ZeroClaw íntegro en radio, (B) ZeroClaw central + worker C/Rust minimal, (C) modelo central sin agente, (D) modelo tiny local si hay una tarea específica que lo justifique.

**GO solo si una prueba concreta demuestra ventaja y costo aceptable.** No poner 1.800 agentes de IA ni gastar tokens/CPU por un framework que no agrega valor frente al scheduler determinista.

## 7. Investigación adicional: ideas no obvias, pero falsables

Proponer y rankear cualquier otra oportunidad verdaderamente diferencial al WISP existente, por ejemplo:

- La red como **observatorio distribuido de interferencia** y predictor de degradaciones por sector/barrio.
- Aprovechar topología/geometría conocida y perfiles estacionarios para predecir rutas físicas, handovers y fallas.
- Coordinación de experimentos sectoriales cuando la carga lo permita (sin pruebas invasivas simultáneas).
- Asistencia limitada P2P a nivel aplicativo/control sin segundo enlace RF (explicar qué mejora y qué NO puede mejorar).
- Modo recuperación resiliente donde existe una ruta física secundaria verificable.
- Posible multiplexación de la banda principal y combinaciones de vdev de QCA988x; distinguir capacidades del chip/driver vs firmware Ubiquiti real.
- Uso de capacidades LTU no expuestas (p. ej., OFDMA subband, control de MCS), pero **solo donde la RE y el hardware permitan una prueba estrictamente controlada**, respetando limitaciones/regulación.

Para cada idea incluir: **qué observación la refutaría en un día de banco**, valor esperado, complejidad, riesgo de degradar conectividad y si ya existe algo similar en OpenMax.

## 8. Plan de pruebas por etapas con gates

### Etapa 0 — Auditoría de estado y no duplicación

Leer repo, testbed y último commit; matriz de evidencias; reproducir offline verificadores ya existentes; identificar conflictos y gaps. Nada de acciones sobre radios.

### Etapa 1 — Experimentos offline y prototipos seguros

Validar software/firmware estático, capacidades de vdev, diseño de benchmark/worker, cross-compile y pruebas unitarias/integración en entorno local/emulación. Preparar scripts read-only y safety harness para hardware. No fabricar resultados RF.

### Etapa 2 — Banco dedicado, lectura y ejecución temporal

Inventory real (read-only), prueba binaria RAM-only, stress microcontrolado, telemetría, CPU budgeting, recovery. Registrar firmware/hardware exactos. Sin cambiar modos de producción.

### Etapa 3 — RF networking cooperativo aislado

A↔B vs B↔AP, STA+AP/mesh, 5 GHz shared-radio, escenario cerca/lejos, antenas reales, error cases, otro radio como control. En modo RF potencialmente disruptivo, usar autorización y preparación explícita.

### Etapa 4 — Piloto escalonado, sujeto a aprobación adicional

Primero 5 radios de laboratorio, luego 20 CPEs solo si consentidos y específicamente autorizados, y después considerar sector piloto. **No iniciar rollout automático**. Todo con rollback, error budget, observabilidad y ventana.

### Etapa 5 — Escala 1.800 (solo diseño hasta tener evidencia)

Tolerancia a fallos, seguridad, firmware heterogéneo, capacidad por sector, costos y criterios de suspensión. Validar que los resultados justifiquen siquiera desplegarlo.

## 9. Métricas y requisitos de aceptación

**Para relay:** mejora de throughput útil de B y de estabilidad **sin empeorar de forma relevante** A, el sector ni terceros; considerar airtime consumido, RTT p95/p99, reintentos, desconexiones, pérdida de management, distancia y ángulos de antena. Descartar en cuanto la doble transmisión degrade capacidad total o no funcione simultáneamente con uplink.

**Para scripts/telemetría:** bytes transmitidos/día, CPU time por muestra, RAM persistente, flaps, falsos positivos, incidentes localizados correctamente y tiempo ahorrado por operador. No coleccionar datos solo porque son accesibles.

**Para compute:** outputs correctos/verificados; throughput por job/hora/potencia; límites CPU/mem real; tiempo hasta preemption; QoE cliente bajo carga; fallas, reintentos, transferencias y energía. La ganancia debe superar centralizar el cálculo.

**Para agentes:** demostración de build reproducible, ejecución estable, límites de seguridad y ventaja cuantificable frente a un micro-worker sin IA.

**Para seguridad:** zero production mutations no autorizadas, identificadores/versiones exactos, cobertura rollback, fin de lease, secretos ausentes, comandos allowlist, logs/auditoría, resultado de fault injection en laboratorio, y no modificación de calibración/regulatory/DFS.

## 10. Entregables: producir archivos en el repo, no solo una respuesta de chat

Crear o actualizar, respetando la estructura existente y evitando duplicar documentación:

1. `docs/COOPERATIVE_CPE_FEASIBILITY.md`: estudio físico/protocolo de CPE↔CPE; 2.4 vs 5 GHz vs segundo hardware; mecanismos posibles/imposibles y gates.
2. `docs/DISTRIBUTED_COMPUTE_FEASIBILITY.md`: matriz CPU/ABI/RAM, modelado de jobs, seguridad, benchmark, comparación PC/servidor.
3. `docs/ZEROCLAW_EDGE_COMPATIBILITY.md`: compatibilidad por familia y evidencia de compilación/ejecución o blockers reproducibles.
4. `docs/WISP_EDGE_SCRIPTS_AND_INTELLIGENCE.md`: catálogo priorizado de scripts/telemetría/optimización, coste y valor.
5. `docs/OPENMAX_NEW_EXPERIMENTS.md`: backlog de experimentos ordenado por ROI/riesgo, cada uno con ID estable, PASS/FAIL/STOP/ROLLBACK, equipamiento, duración de medición y evidencia requerida.
6. Si es apropiado, nuevos scripts/tools/tests **no invasivos**, con test automatizado y comandos de reproducción; dejar clara diferencia entre scaffolding y funcionalidad probada.
7. `docs/OPENMAX_RESEARCH_DECISION.md`: tabla **DO NOW / LAB NEXT / CONDITIONAL / NO-GO**, con top 5 hallazgos y próximos tests accionables, blockers y oportunidades comerciales reales.

Si el repo tiene convenciones obligatorias (AGENTS/CONTRIBUTING), respetarlas. No borrar datos ni sobrescribir artefactos de otras investigaciones. No escribir resultados de benchmark sintéticos como si fueran físicos.

## 11. Formato de respuesta final que quiero

Respondé al finalizar con:

1. **Qué descubriste realmente** y qué contradice mis hipótesis o respuestas previas del asistente.
2. **Cuáles pruebas ya están hechas en OpenMax** y por qué no repetirlas.
3. **Top 10 experimentos nuevos ordenados**, con GO/NO-GO temprano, valor, riesgo y dispositivo exacto.
4. **Qué alcanzaste a ejecutar ahora** (commits, scripts, tests, resultados, artefactos) y qué quedó offline o bloqueado por autorización/hardware.
5. **Decisión preliminar** sobre relay 5 GHz / gestión 2.4 GHz / radio extra / sensores cooperativos / worker distribuido / ZeroClaw en CPE.
6. **Un próximo paso único, específico y seguro** de máxima relación información/riesgo.

No quiero una lista genérica de tecnologías ni un “PRD aspiracional”. Quiero ingeniería inversa con referencias a **archivos, funciones, direcciones, sysids, versiones, límites reales del driver, mediciones y falsación experimental**, y nuevos trabajos integrados al repo. **Sos libre de descubrir enfoques mejores que los que enumeré; no sos libre de inventar resultados o arriesgar la red productiva.**
<!-- stage822a-payload-end -->
