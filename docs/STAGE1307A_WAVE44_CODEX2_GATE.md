<!-- doc-head: Wave44: gate independiente de perfiles vivos, JSON y sysfs -->
Exige producción antes del bench65 final, lectura real y regresiones frescas.
<!-- /doc-head -->

# Stage 1307A — Gate Wave44

El gate sólo lee evidencia local. No ejecuta SSH ni modifica los equipos.
Verifica hashes/tamaños de recibos, raw, stdin y payload transitivos,
fuentes desplegadas, init, configuración y overlay v17.

Para cada radio exige producción60 antes del bench65 final activo,
JSON fresco y estable durante la lectura sysfs, servicio procd y habilitación.
El heartbeat puede avanzar y el RSSI variar dentro de la misma franja;
ambas lecturas deben concordar con los cuatro brillos e identidad/perfil/barras.
Comprueba que configuración RF, colas, canal, boot y reinicios no cambien.
Cuatro barras AUTO requieren RSSI medido mayor o igual a -65 dBm.
El verificador de host exige seis ICMP recibidos de seis enviados por radio,
con origen/ruta del puente PtP verificados. Esta muestra no acredita capacidad RF.

El perfil de producción empaquetado permanece -80/-73/-65/-60;
el override de bench es -80/-75/-70/-65. El gate exige pytest de Wave44 y
Wave37 con cero fallos/errores/saltos y fuentes sin cambios durante la ejecución.

```sh
python3 tools/verify/verify_stage1307a_wave44_codex2_gate.py --run-tests
```

Recibos: `artifacts/verification/stage1306a_wave44_rssi_profiles_pytest.json`
y `artifacts/verification/stage1307a_wave44_codex2_gate.json`.
La confirmación visual física permanece UNKNOWN, incluso con sysfs correcto.
