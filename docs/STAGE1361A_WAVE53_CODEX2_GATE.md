<!-- doc-head: Wave53: gate de CPU estricta, lectura real y auditoría de sólo lectura -->
Headline requiere <0.5% en ambos; mínima <1% se informa por separado.
<!-- /doc-head -->

# Stage 1361A — Gate Wave53

El gate no conecta a radios/router. Reproduce contadores CPU, intervalos >=60s,
PID/starttime, SHA desplegado, JSON/sysfs, polls y ausencia de reescrituras.
Conserva/recalcula fases V2/V3; no mezcla su baseline con Wave48 bajo carga.
Verifica ambos paquetes/TAR/manifiestos e históricos protegidos.

La auditoría router exige RAW idéntico al declarado, alias local probado,
comandos API read-only, reglas sin cambios y muestra real bps/pps.
El CLI propuesto sigue sin ejecutarse; drain100/fallback MAIN no se acreditan.

```sh
python3 tools/verify/verify_stage1361a_wave53_codex2_gate.py --run-tests
```

Ejecuta las suites Wave53, Wave37 y Wave44 con cero fallos/saltos.
`all_gates_passed` exige además la meta preferida <0.5% en ambos radios.
Si sólo pasa <1%, informa `PARTIAL_PREFERRED_CPU_TARGET_UNMET` y
`required_scope_passed=true`. No afirma cero procesos ni aceptación visual.

Recibos: `artifacts/verification/stage1360a_wave53_zero_filter_led_pytest.json`
y `artifacts/verification/stage1361a_wave53_codex2_gate.json`.
