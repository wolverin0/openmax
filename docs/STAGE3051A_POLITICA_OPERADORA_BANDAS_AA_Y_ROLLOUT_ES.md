<!-- doc-head: Wave391, politica operadora del 30/10 y guardas empiricas del mismo run -->
Implementacion offline validada: 109 pruebas propias y cero regresiones contra HEAD. Sin SSH ni despliegues.
<!-- /doc-head -->

# Politica del operador: A/A y rollout

## Cambios autorizados

| ID | Comportamiento |
|---|---|
| L01 | Perdida contra el maximo A/A observado del mismo run/equipo |
| L02 | p99 contra el maximo A/A observado del mismo run/equipo |
| L03 | Goodput minimo, p95 maximo y ruido del score derivados del A/A comparable |
| L04 | Rollout compara goodput, p95/p99, perdida y retries con ese A/A |
| W06 | Sin limite global de rondas/reloj por tarea; comandos, fases y rollback siguen acotados |
| W03 | Sin horario 03-05 ni un nodo por noche; subconjuntos escalonados del alcance autorizado |
| D01 | Presupuestos documentales y de formato conservados |

La fuente compartida es [operator_policy_20261030.json](../orchestration/autoresearch/operator_policy_20261030.json).
PROGRAM.md refleja esta decision; los recibos historicos conservan sus criterios originales.

## A/A obligatorio antes de medir un candidato

El contexto identifica run, equipos por clave fijada y arranque, workload y configuracion no variada.
Cada ventana declara metricas, tiempos, identidad, fase y evidencia de enlace, OOM y restauracion.
Faltantes no se convierten en cero ni en salud: bloquean la evaluacion.
No se reutilizan valores de Wave388 como defaults; IPv6 y buffers pequenos limitan su transferencia.
La banda es el minimo/maximo observado. No certifica tasas de falsos positivos ni sensibilidad al dano.
Se preservan pesos del score y desempate por complejidad; la mejora minima sale del ruido A/A del score.
Goodput debajo de la banda y p95/p99 o perdida por encima se rechazan incluso sin incumbente.
La igualdad con el borde no se etiqueta como dano.

CLI offline: `python -m tools.bench.evaluate_same_run_aa_policy --context CONTEXTO --baseline AA --candidate CANDIDATO`.
No transporta comandos a radios. ObjectiveConfig sin A/A se rechaza al construirlo y el harness bloquea antes del callback.
La captura/preflight A/A real de los drivers legacy queda pendiente; no se afirma enforcement en todo codigo externo.

## Alcance de produccion y evidencia exacta

Un PtP-Colo (.62/.54) y los tres paneles Guarida (.84/.82/.83), cada panel con menos de 15 clientes observados.
No se asume elegibilidad de Panel2 a partir del numero de CPEs ya migrados.
Se requieren banco PASS del cambio exacto, Before observado, monitoreo After armado y rollback armado.
Los gates que ya exigen operador siguen vigentes; esta tarea offline no autoriza despliegues.
El builder captura los bytes una vez, calcula el manifiesto/hash exacto y valida antes de escribir.
Con request genera solo los nodos evaluados; sin request construye offline con estado PENDING_EVIDENCE.
No basta un JSON que diga PASS: se verifican fuente, ejecucion, payload, mediciones A/A y referencias SHA.
Estas comprobaciones atan archivos locales; no autentican al productor fisico ni el estado actual del radio.

## Pruebas y limites de aceptacion

La revision independiente encontro y cerro: PASS sin ejecucion, hash no ligado al payload y omision de p99.
Suite final de componentes modificados: 109 aprobados, 0 fallidos, tambien en HEAD + solo archivos propios.
Se conservaron intentos fallidos de fixtures/validadores; no se repitieron benchmarks ni tocaron radios.
Primera suite completa: 4250 aprobados, 236 fallidos, 85 omitidos y 1464 errores, rc1.
Contrafactual final: HEAD limpio 4502 aprobados; HEAD + solo 15 archivos propios 4607 aprobados.
Ambos conservan 2418 fallos, 799 errores y 6 omitidos: cero regresiones y ninguna perdida de cobertura.
Los dos clones y los temporales generados por esta tarea se excluyen solo por comando; pytest.ini no se modifica.
Se corrigieron problemas del runner (caches/temporales y audit Windows); los intentos diagnosticos se conservaron.
El comparador detecta fallos nuevos y perdida de cobertura por errores de recoleccion.
No se comparo contra cambios sin commit ajenos: el segundo worktree contiene solo politica/tests propios.

## Pendientes fuera de alcance

Los parches W378 RAM/temperatura no se aplicaron: no son autoridad para nuevos numeros en esta decision.
El patch W06 para tools/orchestration y metadatos UISP queda UNAPPLIED para sus propietarios.
El daemon fijado de observabilidad conserva sus comparaciones descriptivas Stock Before/After.
El runner Panel1 externo a este scope aun tiene in_valley; necesita integracion del nuevo gate por su propietario.
La politica host no esta conectada a cada script apply de dispositivo: runtime_enforcement=false.
Los cinco kits existentes, los scripts ya desplegados y los pins historicos no se regeneraron.
El patch documental preparado encontro cambios concurrentes del propietario W397: no se aplico sobre ellos.

- [Recibo](../artifacts/autoresearch/wave391_policy_thresholds.json)
- [Gate](../artifacts/verification/wave391_lane1_policy_thresholds_gate.json)
