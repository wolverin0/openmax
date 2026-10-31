<!-- doc-head: Stage 1265A: gate independiente Wave 37 y aceptación parcial -->
AUTO sigue RSSI real; la prueba manual no reemplaza el umbral de cuatro barras.
<!-- /doc-head -->

# Stage 1265A — Gate Wave 37

El gate local revalida los recibos vivos de 1260A/1261A y el paquete 1262A.
Exige los dos hosts exactos, hash/tamaño de cada raw/stdin/payload, coincidencia
de fuentes desplegadas, servicio procd, sysfs real y restauración AUTO.
Compara configuración, colas, canal, boot y reinicios antes/después.
Verifica el overlay y sus SHA256SUMS, y fija las fuentes antes/después de pytest.

Comando desde Linux, en la raíz del repositorio:

```sh
python3 tools/verify/verify_stage1265a_wave37_codex2_gate.py --run-tests
```

Salida: `artifacts/verification/stage1265a_wave37_codex2_gate.json`.
`implementation_and_functional_gate_passed` separa implementación correcta de
`requested_both_auto_four`. La captura final tiene AP -64 dBm/tres barras y
STA -55 dBm/cuatro. Por ello, aunque la suite y el funcionamiento pasen, el
estado literal es `PARTIAL_SIGNAL_BELOW_FOUR_BAR_THRESHOLD`, `all_gates_passed=false`
y exit 1. La prueba manual de cuatro salidas no satisface cuatro barras AUTO.
Confirmación visual física UNKNOWN. No hay nueva certificación RF ni flasheo.
