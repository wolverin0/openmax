<!-- doc-head: Wave48: gate independiente y límites explícitos de aceptación -->
Lectura de evidencia local; nunca conecta ni modifica radios.
<!-- /doc-head -->

# Stage 1331A — Gate Wave48

El gate valida fuentes y RAW con SHA256/tamaño, campañas completas,
lecturas LED bajo carga, CPU/softirq y paquete/simulación WA v7.
Ejecuta pytest fresco y fija los bytes seleccionados antes y después.

```sh
python3 tools/verify/verify_stage1331a_wave48_codex2_gate.py --run-tests
```

La implementación y los tests pueden pasar sin demostrar todas las peticiones
literales. Si no existe control LED OFF/ON contrabalanceado autorizado,
`zero_overhead=UNKNOWN` y `literal_all_requirements_passed=false`.
Los ticks positivos refutan cero CPU de ejecución. Se observaron 7/138 echoes
no emparejados, pero el reloj UDP ejecutado tuvo división entera/coarse clock:
el resultado QoE de 150 ms es UNKNOWN_INVALID_TIMER, sin porcentaje válido.
Los bytes ejecutados se archivan; las reparaciones futuras no acreditan rerun.
La corrección LED y el paquete/fixtures pueden pasar con estado global parcial:
`PARTIAL_LITERAL_REQUIREMENTS_UNMET`, `all_gates_passed=false`, exit 1 esperado.
La confirmación visual y la aceptación PtMP viva permanecen UNKNOWN.

Recibos: `artifacts/verification/stage1330a_wave48_loaded_leds_and_wa_v7_pytest.json`
y `artifacts/verification/stage1331a_wave48_codex2_gate.json`.
