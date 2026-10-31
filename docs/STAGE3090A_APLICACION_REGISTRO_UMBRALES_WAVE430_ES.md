<!-- doc-head: Wave 430 aplica el registro W422 en código propio y compara contra preimágenes reales -->
Registro APPLIED en alcance offline; cero acceso a dispositivos y cero despliegues.
La comparación Python no presenta regresiones nuevas; conserva siete fallos anteriores.
La aceptación nativa permanece pendiente por timeout de WSL.
<!-- /doc-head -->

# Wave 430: aplicación del registro de umbrales

## Resultado y alcance

`orchestration/thresholds.json` conserva las 29 filas y las fuentes congeladas de W422.
`APPLIED` describe los consumidores propios de esta entrega; cada fila declara su alcance.
No significa calibración física completa, migración de otros propietarios ni permiso de producción.
No hubo SSH, tráfico de banco, cambios en dispositivos ni reinicios de servicios compartidos.

El manifiesto `tools/verify/wave430_application_manifest.json` identifica las preimágenes,
el código final, los cinco kits generados y la evidencia por SHA-256.
El gate está en `artifacts/verification/wave430_lane1_thresholds_applied_gate.json`.

## Política aplicada

| Filas | Tratamiento |
| --- | --- |
| L01, L02, L03, L04 | Banda empírica del A/A del mismo equipo, ejecución, carga y contexto |
| M01, M02 | Eliminar pisos universales no calibrados en consumidores operativos propios |
| T01, T02, T03, T04 | Retirar valores numéricos rechazados o sin fuente como órdenes de parada |
| W03, W06 | Conservar la política W391 sin horarios ni topes globales inventados |
| D01 | Presupuesto documental leído del registro |
| W02, W04, W08 | Valores del contrato de rollback, E/S, propiedad y caducidad leídos del registro |
| T05 | Ciclo acotado preservado, sin promesa de seguridad térmica por duración |
| L05, L08 | Anotación de ID; sin nuevos números ni cambios en límites desconocidos |
| M05, L06, S02 | Sin guarda operativa propia; preservar modelos y validadores históricos |

Los valores `runtime_bindings` de KEEP preservan contratos existentes con fuente y hash anteriores.
No se presentan como óptimos medidos. Ausencia, tipo inválido o valor no finito falla cerrado.
Los kits reciben los valores al generarse; el dispositivo no necesita Python ni el repositorio.
Los auxiliares independientes exportan una instantánea del registro verificada por hash.

El harness ya exigía A/A desde W391: se conectó al registro sin sustituir observaciones por porcentajes.
El evaluador PtP exige observaciones completas, contexto coincidente e intervalos sin solapes ni replay.
Una mejora p95 no autoriza un candidato con p99, pérdida o capacidad fuera de su propia banda A/A.
La decisión exploratoria tampoco constituye un holdout independiente ni aceptación de producción.

## Controles y exclusiones

Se conservan lectura válida, identidad, permiso operativo, preimagen, rollback y caducidad.
No se introdujo una nueva parada RF por temperatura desconocida o antigua: sigue siendo telemetría.
No se inventó un nuevo piso global de RAM ni se transfirió calibración de otro equipo.

Pendientes de sus propietarios: M03/W05 en el daemon fijado; M04 en `tools/uisp_bridge_openwrt/`;
L09 en firmware; L10 en observabilidad; L12 en el controlador; W07 en el orquestador.
El daemon y `tools/panel1/wave344_ap_memory_repair/` conservan sus bytes originales.
Los cambios concurrentes de otros carriles se registran sin revertirlos ni atribuirlos a esta entrega.

Excepción histórica explícita: `capture_stage1322a_ltu_active_thermal_and_mtd_guard.py`
clasifica recibos antiguos en solo lectura y conserva su fuente exacta; no activa ni detiene RF.
También se preservan predicados usados por validadores de recibos y planes antiguos, sin volver a firmarlos.

## Verificación reproducible

- Comparación equivalente: 572 PASS / 7 FAIL antes frente a 574 PASS / los mismos 7 FAIL después.
- Cero regresiones nuevas y cero pruebas previamente aprobadas ausentes de la selección posterior.
- Contratos nuevos: 98 PASS, incluidos rechazo de p99/pérdida adversos, replay y solapes.
- Las ejecuciones finales registran hashes de entrada y confirman que no cambiaron durante pytest.
- Baseline: bytes reales del árbol sucio al iniciar, no HEAD ni una reconstrucción supuesta.
- El overlay cubre importaciones y lecturas Python; no virtualiza archivos leídos por WSL.
- 28 casos nativos se separaron de esa comparación; su intento fresco produjo errores por timeout de WSL.

Los siete fallos previos corresponden a cuatro comprobaciones de evidencia nativa histórica Panel3,
dos comprobaciones del kit/plan Panel3 y una prueba shell PtP con ruta Windows con espacios.
Sus trazas permanecen en los XML/logs de ambas revisiones; no se corrigieron fuera del objetivo.
Se conservaron los intentos iniciales y las regresiones térmicas encontradas y reparadas durante la tarea.
La revisión independiente también detectó y permitió corregir la omisión de p99/pérdida en el evaluador PtP.

Para verificar hashes, comparación, presupuesto documental y límites de aceptación, ejecutar:

```sh
python tools/verify/verify_stage3090a_wave430_thresholds_gate.py
```

El modo normal verifica sin recalcular firmas. `--record` crea explícitamente una nueva instantánea.
El resultado CONFIRMED corresponde al cambio offline y a la comparación Python.
La suite completa no está verde y la aceptación nativa no está concedida.
Pendientes: resolver el runtime WSL por su propietario y volver a ejecutar los casos nativos;
las filas de otros carriles requieren su propia migración y evidencia.
