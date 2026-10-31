<!-- doc-head: Wave 252 diagnóstico de airtime y guard bloqueado para Panel 3 -->
El archivo evaluado no contiene candidatos factibles bajo las restricciones congeladas; no se suavizó el mínimo del CPE débil.
El punto publicado es diagnóstico, no único ni desplegable; el guard bloquea cualquier mutación antes de sondear el sistema.
Todo este trabajo es offline: no hubo SSH, despliegue, cambios en radios ni aceptación de hardware.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 2552A: airtime del CPE débil y límite de memoria FQ

## Datos de entrada y atribución

La síntesis usa los recibos 2498A/2499A de dos células OpenWrt y sus capturas reales previamente adquiridas.
Panel 3 registra tres estaciones; una presenta MCS 0/NSS 1, mientras las otras dos registran MCS 8/NSS 2.
Eso motiva el modelo de airtime; no prueba que esa estación sea la causa exclusiva de la presión de colas.
El contador global fq_overmemory aumentó 184 durante 71.61 s de uptime observados.
La etiqueta histórica «delta_45s» no sustituye ese intervalo real: su tasa sería 9250.10/h, distinta de la media acumulada 2358.64/h.
No se ajustó la simulación para reproducir esas tasas; un evento del contador tampoco identifica una cola individual.

## Resultado negativo del modelo

Se mantuvo la restricción de bulk débil mínimo 0.25 Mbps y retención del bulk protegido de al menos 95% respecto de su baseline.
Los dos optimizadores produjeron 120 evaluaciones de traza y un archivo de 106 puntos únicos válidos, incluido el baseline.
Ningún punto evaluado fue factible. Esto describe la búsqueda finita, no una demostración de imposibilidad global.
Los candidatos con p95 protegido cercano a 2 ms podían dejar el bulk débil prácticamente en cero: esa aparente mejora no es aceptable.
El mejor bulk débil observado en entrenamiento fue aproximadamente 0.083984 Mbps, aún inferior a 0.25 Mbps.

El frente diagnóstico contiene 25 puntos con objetivos equivalentes; sus rangos cero usan un denominador mínimo de 1e-12 y desempate lexicográfico.
Esos resultados no identifican una rodilla física única ni un óptimo validado: selection_domain=MIN_CONSTRAINT_VIOLATION_DIAGNOSTIC.
El punto seleccionado tiene constraint_violation=0.166016, feasible=false y apply_allowed=false.
Se conservan las salidas iniciales y las reparaciones de parser/publicación; no se relajaron restricciones ni se borró el resultado negativo.

| Parámetro | Identificación del baseline Panel 3 | Punto diagnóstico |
|---|---|---|
| BE AQL bajo/alto | Observado: 1500/3000 us | 500/3000 us |
| aql_threshold | Observado: 4000 us | 16000 us |
| airtime_weight débil | No medido; supuesto del modelo: 256 | 256 |
| RTS | No medido; supuesto del modelo: 2347 | 2347 |
| fq_memory_limit | Observado: 3145728 bytes | Fijo, sin optimizar ni escribir |
| fq_limit / fq_quantum | Observados: 512 / 3028 | Fijos, sin escribir |

El punto ni siquiera reduce el peso débil respecto del supuesto de baseline; no se presenta como una mejora de airtime confirmada.
Los límites VO/VI/BK nativos se conservan; solo BE entra en la búsqueda AQL.
En el modelo los cambios BE/umbral/RTS afectan a ambas AP independientes; el peso débil afecta solo a Panel 3.
Panel 1 no es un control inalterado de esa política. El guard generado cubre únicamente Panel 3, no la política completa de dos células.

## Holdout y límites de interpretación

La selección usa entrenamiento; los tres seeds holdout no eligen los parámetros del guard.
La comprobación del frente no restringido comprende 75 puntos por tres seeds: 225 réplicas de modelo, no radios ni pruebas de campo.
En holdout, el punto diagnóstico obtiene bulk protegido 15.980128 Mbps, bulk débil 0.0791573 Mbps y p95 protegido 6.252461 ms.
La restricción débil continúa incumplida; conservar unos 16 Mbps protegidos no autoriza promover el punto.
Tráfico ofrecido, tamaño SKB, probabilidades de error/reintento y efecto RTS son supuestos sin calibración física.
La reducción de errores por RTS no está medida; en el modelo se aplica a los frames elegibles de ambas AP, no solo al CPE débil.
CoDel usa un sustituto con objetivo 5 ms e intervalo 100 ms; no es una implementación validada de Linux fq_codel.
Las células no comparten medio en el modelo y solo se representa downlink; no se infieren efectos RF o de upstream reales.

## Guard 2551A: bloqueo permanente de este perfil

El shell se genera exclusivamente desde knee.json, ligado por SHA256 a sus parámetros y a la grilla congelada.
Por defecto imprime PLANNED/MODELED_ONLY con apply_allowed=0 y readiness=NO_DEPLOY.
--apply, incluso con las dos confirmaciones explícitas, --verify y --rollback terminan bloqueados antes de probes o escrituras.
No existe una opción que convierta este diagnóstico no factible en un perfil desplegable.

La plantilla conserva un contrato futuro de identidad privada exacta, rol AP/PHY y resolución dinámica IP→vecino→FDB→estación asociada única.
No presupone que el MAC Ethernet de una CPE coincida con su estación WLAN ni fija identidades privadas en este informe.
Sus rutas proc/sysfs son configurables para un harness desechable; eso no convierte un fixture en hardware.
Las lecturas de peso por estación y RTS deben existir y permitir snapshot exacto; los supuestos 256/2347 nunca sustituyen un getter ausente.
BE AQL, umbral y RTS son globales de PHY y requerirían reconocer ese alcance; el peso es por estación.
La memoria FQ de 3 MiB es un pool global compartido: no reserva memoria ni protege individualmente las colas de una estación.
default_qdisc=fq_codel solo expresa una política por defecto; sin readback activo mediante tc no hay prueba de qdisc instalada.
No se escribe ninguna qdisc ni se modifica FQ global; sus valores fijos solo delimitan el contexto de la plantilla.
Snapshot, readback y restauración son código no ejercitado con radios aquí; no se declara rollback OTA ni recuperación independiente.

## Verificación offline y procedencia

Se preservó el primer timeout de 30 s de WSL y las copias originales del generador y del guard.
La reparación 1 cambió únicamente el backend de pruebas a Git MSYS sh en Windows, sin reiniciar WSL ni sobrescribir el guard.
La sintaxis y el dry-run nativos devolvieron 0; apply normal, apply confirmado, verify y rollback devolvieron 65 por el bloqueo del modelo.
Estas comprobaciones no son pruebas BusyBox/MIPS ni aceptación de hardware; no ejecutaron los getters o setters de la plantilla.
La ingestión 2553A aceptó <memorymaster-id>, id 158045, como candidate; no representa validación independiente.
PASS_OFFLINE_INFEASIBLE_GUARD_BLOCK_ONLY acredita el artefacto bloqueado, no un beneficio de campo ni permiso de despliegue.

## Evidencia

[Modelo 2550A y límites](../artifacts/autoresearch/stage2550a_guarida_2cell_8radio_simpy_pymoo_pareto_receipt.json).
[Punto diagnóstico congelado](../artifacts/autoresearch/stage2550a/knee.json).
[Gráfico diagnóstico offline](../artifacts/autoresearch/stage2550a/pareto_diagnostic.svg).
[Procedencia del gráfico](../artifacts/autoresearch/stage2550a/plot_provenance.json).
[Guard y procedencia 2551A](../artifacts/autoresearch/stage2551a_weak_cpe_airtime_weight_and_fq_memory_guard_receipt.json).
[Shell generado, sin despliegue](../firmware/openwrt/common/fmx_panel3_weak_cpe_model_guard.sh).
[Pruebas nativas offline y primer fallo conservado](../artifacts/autoresearch/stage2551a/generation.json).
[Ingestión 2553A](../artifacts/autoresearch/stage2553a_memorymaster_ingest_receipt.json).
