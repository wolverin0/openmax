<!-- doc-head: Wave 127 (1800A-1802A) sintesis ES: nota #625 une Waves 104 (A/B coverage_class 0 vs 1 DESCARTADO en ambas rondas, dual-bind sin probar), 114 (auditorias Panel1/Panel3 read-only + ciclo XC/LTU reversible), 116 (plan colo 5200 MHz y blueprint Panel2 22 CPE, bloqueados), 120 (RE scheduler ame_core; eab_driver.ko ausente) y 121 (maquina de 6 cohortes 28 CPE bloqueada + SimPy); banda :8787 a 1536A..1805A; SIN campeon; scholar INCONCLUSIVO; solo IDs cpe_ -->
# Reporte ejecutivo - Nota #625: cobertura, AQL, scheduler LTU y 28 CPE

**Wave 127 - Etapas 1800A-1802A - 2026-10-28 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se sintetizaron 10 recibos de las Waves 104, 114, 116, 120 y 121 en la nota evergreen #625 y el feed del
Command Center :8787 se amplio a 1536A..1805A. Titular honesto: **no hay campeon de trafico nuevo**. El
unico A/B del conjunto se descarto en las dos rondas y no se reprodujo; el resto es auditoria en vivo de
solo lectura, planes bloqueados, RE estatica y una simulacion. Los abonados figuran solo como
cpe_41/cpe_223/cpe_80/cpe_91.

## Wave 104 - A/B de coverage_class (en vivo, DESCARTADO)

stage1663A (CONFIRMED_LIVE_HARDWARE) comparo coverage_class 0 (brazo A) contra 1 (brazo B) en ABAB con
triple-play, en 2 rondas:

- Ronda 0: goodput +0.71 %, p95 de RTT **+9.26 % (peor)** -> descartada.
- Ronda 1: goodput +1.48 %, p95 de RTT -16.21 % -> **descartada** (delta Pareto 0).

La mejora de la ronda 1 no se reprodujo, asi que coverage_class=1 **no se promueve**. Citar solo
"+1.48 % / -16.21 %" exagera el resultado; queda registrado como discrepancia del enunciado.

stage1662A (CONFIRMED_LIVE_HARDWARE) verifico ban_time=1200 con estado
POST_HEAL_PASS_DUAL_BIND_UNPROVEN: el camino post-heal pasa, pero el dual-bind sigue sin probarse.

## Wave 114 - auditorias de paneles y ciclo XC/LTU (en vivo, solo lectura / reversible)

- stage1722A (LIVE_HARDWARE_READ_ONLY_PRODUCTION): el healer 4addr no escribe log en /tmp; su presencia
  se prueba por el crontab, los scripts de hotplug y los puertos del bridge en forwarding con
  multicast_to_unicast. Panel3 (.83) tenia 3 de 6 CPEs asociados.
- stage1723A (LIVE_HARDWARE_ONDEVICE_AND_OTA_READONLY): ciclo finito de 3 iteraciones con solo los knobs
  reversibles de 1710A/1711A. Limites del propio recibo: las radios de banco no tienen par OTA, atpc y
  AirPrism quedaron excluidos, y la RF de .110 no se encendio.

## Wave 116 - plan colo 5200 y blueprint Panel2 (planes estaticos)

- stage1734A: controlador seguro para scan_list con objetivo 5200 MHz; conserva 6035/5170/5200 y sumaria
  5745/5825. **executable=0**, 1 paso bloqueado, 0 escrituras de radio, 0 SSH.
- stage1735A: blueprint de 22 CPE de Panel2 en 4 cohortes (6/6/5/5); 4 de 4 cohortes bloqueadas, 0 CPEs
  descubiertos.

## Wave 120 - RE del scheduler LTU (estatica)

- stage1758A (CONFIRMED_STATIC_BINARY): RE del scheduler en ame_core.ko (9799 simbolos, 21 refs de
  scheduler). **eab_driver.ko no esta presente en la imagen analizada** y el literal "tdma" aparece 0
  veces: la afirmacion TDMA se apoya en la estructura del scheduler, no en un simbolo con ese nombre.
- stage1759A (CONFIRMED_STATIC_DATA): reconciliacion de knobs TDMA/modulacion sobre 571 knobs.

## Wave 121 - cohortes de 28 CPE (plan + simulacion)

- stage1764A (CONFIRMED_STATIC_PLAN): maquina de estados unificada de 6 cohortes para 28 CPE; 6 de 6
  cohortes bloqueadas, executable=0; gates ban_time=1200, brport_state 3 y multicast_to_unicast.
- stage1765A (SIMULATED_MODEL): transicion SimPy determinista (coverage_class 1, aql_threshold 3000, 84
  streams IPTV) con 5 fallas de dual-bind inyectadas y 0 rollbacks: es un modelo, no un despliegue.

## recall-first y scholar (honestos)

recall-first: 3 de 6 consultas con aciertos (coverage-class AQL 15, cohortes Panel2 3, maquina de estados
Guarida 3); scheduler TDMA, eab_driver y colo 5200 dieron 0. scholar: UN chequeo suave del principio TDMA
con 4 s de espacio; el sondeo del motor funciono (P=0.93, source=live) pero el unico verify_claim dio
FETCH_FAILED (ReadTimeout): **INCONCLUSIVO, no un negativo**. Nota #625 ingresada; vault en 625 notas.

## Etapa 1801A - banda 1536A..1805A

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero; los 10 recibos aparecen con
su propia clase de evidencia y la seccion Control Maestro queda sin apellidos (solo cpe_*).

## Limites y advertencias (honestas)

- **Sin campeon nuevo**: el A/B de coverage_class se descarto dos veces con signos opuestos de p95.
- Colo 5200, Panel2 y la maquina de 28 CPE son **planes bloqueados** (executable=0).
- **Verificacion en navegador real: NO realizada** (Claude-in-Chrome no conecta); se verifico por CLI
  (HTTP 200 + bytes servidos) y balance de etiquetas, con reinicio limpio del daemon :8787.
- El tablero completo aun renderiza apellidos desde recibos historicos fuera de Control Maestro (flag de
  Wave 117, pendiente de decision del operador).

## Que sigue (decision del operador)

- Re-test reproducible de coverage_class y prueba del dual-bind antes de promover nada.
- Desbloquear los gates de cohortes antes de cualquier migracion de Panel2/Panel3.

Recibos: `stage1800a_hyperresearch_wave104_114_116_120_121_note625_receipt.json`,
`stage1801a_command_center_1805a_band_refresh_receipt.json`, `stage1805a_wave127_opus2_gate.json`.
