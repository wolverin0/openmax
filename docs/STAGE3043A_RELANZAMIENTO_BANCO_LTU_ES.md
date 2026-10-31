<!-- doc-head: Stage 3043A (W383) ES: relanzamiento RAM del LTU-Lite .110 del banco con el lanzador corregido en W378 (sin STOP termico, 4 sensores registrados). La radio quedo como AP-PTMP 5500 MHz 20 MHz FMX-LTU con powerout -4, verificada y sin tocar flash; el PtP con el LTU-Lite 2 no se establecio (0 enlaces, LAN del par sin respuesta), asi que el A/B de rendimiento y latencia quedo ABANDON. Temperatura de 66 a 80 C en 24.9 min -->
Que cubre: el relanzamiento en RAM, la serie de temperaturas, por que no hubo PtP y el estado en que quedo la radio.
Estado: solo banco .110, solo RAM. 0 escrituras en flash, particiones protegidas con hash igual, 0 escrituras en /dev/ame, sin reboot.
Datos maquina: artifacts/autoresearch/wave383_ltu_relaunch.json.
Leer cuando: antes de volver a usar el banco LTU o de planear el A/B de rendimiento con el LTU-Lite 2.
<!-- /doc-head -->
# Stage 3043A: relanzamiento del banco LTU (W383)

## 1. Relanzamiento (CONFIRMED_LIVE_HARDWARE)

- **Lanzador:** `tools/bench/ensure_ltu110_ram_ap_ptmp.py` de W378, sin cambios. Su evidencia se guardo en el scratchpad para no escribir rutas de otras olas.
- **Motivo de activacion:** ASIC_STOPPED, igual que en W370. Un intento, lock liberado.
- **Readback:** ap-ptmp, 5500 MHz, 20 MHz, FMX-LTU, powerout -4, antennagain 26; ath0 up, protocolo ame activo.
- **Potencia:** el lanzador aplica txpwr -30 y powerout -4. El -26 del despacho es el valor del primitivo 1267A, que usa powerout 0.
- **Guarda termica:** desactivada por decision de W378; el monitor solo registra.

## 2. Temperaturas (MEASURED, host cada 10 s)

| Sensor | Min | Max | Ultimo |
| :-- | --: | --: | --: |
| temp0 | 66 | 79 | 79 |
| temp1 | 66 | 79 | 79 |
| rtemp0 | 66 | 80 | 79 |
| rtemp1 | 66 | 80 | 79 |

- 128 muestras en 24.9 min con RF encendida; arranco a 67 C.
- Referencia: el corte del 27/10 fue a 72/72/72/73 C con el mismo powerout -4 (cuadro congelado, STALE).

## 3. PtP (NO SE ESTABLECIO)

- `af get remotelinks` dio TOTAL LINKS 0 durante toda la ventana y la LAN del LTU-Lite 2 no respondio.
- Causa UNKNOWN. El 27/10 (1254A) el LTU-Lite 2 ya estaba sin alimentacion; lo mas probable es que siga sin PoE.
- **A/B de rendimiento y latencia: ABANDON.** Sin enlace no hay trafico. `run_ltu110_60s_cooled_burst_mode.py` solo tiene backends simulados.

## 4. Estado final y contrato

- La radio queda como AP en RAM, sin guarda termica, como pide el contrato. Un reinicio la devuelve a CPE nativa (y el `rc.poststart` levanta powerout 28).
- **Karpathy: TARGET_NOT_MET.** calibrated_snapshots 0 (sin enlace), irq_cpu_balance_delta_pct UNKNOWN (sin A/B), ame_device_writes 0.
- **Siguiente paso:** operador da PoE al LTU-Lite 2; luego una ola corre el A/B con el enlace arriba.
