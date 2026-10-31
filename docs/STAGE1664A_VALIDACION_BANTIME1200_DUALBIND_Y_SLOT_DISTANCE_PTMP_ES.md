<!-- doc-head: Wave104: dos reasociaciones reales, ocho ventanas OTA y límites de la prueba dual-bind -->
Hardware .20 y .200.41; ajustes temporales restaurados, helper1200 desplegado.
La recuperación del enlace está confirmada; el doble bind no está demostrado.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Wave104: banco WA, ban_time1200, cobertura y AQL

## Resultado

Se ejecutaron dos desconexiones reales `del_client`, `ban_time=1200`,
y dos rondas A1→B1→A2→B2 con tráfico Triple-Play real entre AP LAP-120
198.18.0.43 y STA Loco 198.18.0.67, MAC PUBLIC_DEVICE_0036.
AP `phy4`, STA `phy6`: no se asumió `phy0`.
El gate operativo queda INCOMPLETE por falta de prueba del doble bind.
Los tests locales verifican los recibos y ese resultado negativo.

Stage1655 quedó escrito con los 134 tests anteriores aprobados y aceptación
operativa INCOMPLETE. No se cambió ese resultado para presentar un PASS físico.

## Stage1662: recuperación confirmada, doble bind desconocido

Se respaldó y desplegó `/usr/sbin/fmx_ap_4addr_peer_healer.sh` en .20.
SHA256 instalado: `04bcb46438aa84339e041add1c0f1a7a0f82d4b3ffe76d9ccba7483c510ef053`.
El watchdog independiente de 45s permitía restaurar la versión anterior.
Las dos llamadas `del_client` devolvieron exit0; cada prueba posterior recibió
5/5 pings IPv6 EUI-64, sin pérdidas. La STA volvió a estar asociada.

El AP_VLAN conservó ifindex995 y brport/state3 en las muestras.
No apareció un unregister nuevo en dmesg durante las ventanas observadas.
Las líneas antiguas de unregister se excluyeron por su tiempo de arranque.
Esto no confirma Bind#1 de hostapd ni Bind#2 de netifd: atribución UNKNOWN.
No se deduce una ventaja causal de1200 frente a500 con esta prueba separada.

## Stage1663: dos rondas diagnósticas completas

Cada ventana duró20s de carga: TCP bidireccional P1, IPTV UDP4Mbps/1316B
y VoIP64kbps/160B con DSCP. Se midió ping6 simultáneo, bitrate, RSSI,
señal por cadena, reintentos y `/proc/stat` antes/después.
La carga se inició en lotes separados en ambos extremos, sin consultas SSH
durante los20s. El goodput procede de contadores del receptor.

| Tratamiento B frente a su A | Goodput A→B Mbps | Cambio | p95 A→B ms | Cambio |
|---|---:|---:|---:|---:|
| coverage_class1 |72,226→72,738|+0,71%|35,334→38,608|+9,26%|
| coverage1 + VI750/1500 + BE1200/2400 |71,690→72,748|+1,48%|39,327→32,952|−16,21%|

Ambos extremos recibieron cada tratamiento. Baseline: coverage0,
VO300/600, VI1000/2000, BE1500/2500, BK500/1000 y aql_threshold3000.
Se usó `iw phy <phy> set distance450`, cuyo readback fue coverage1;
el argumento representa cobertura, no una distancia física medida del banco.
La clase usa unidades de3µs según iw; no se midieron registros de slot del ASIC.
AQL se escribió con `echo '<AC numérico> <low> <high>'` y readback exacto.

Pings de las ocho ventanas:160/160 bajo carga y24/24 posteriores.
Esto no significa cero pérdida UDP: los contadores IPTV/VoIP completos
permanecen en los JSON. El primer intento baseline descartado tuvo35% de
pérdida de ping y se conserva por separado; no se mezcló con la campaña compacta.
El segundo tratamiento combina dos factores; no aísla causalmente AQL.
Dos rondas, sin holdout independiente, no prueban significancia ni óptimo.
Ambas filas del ledger quedan discard; no se promovió un campeón.

## Fallos conservados y seguridad

El BusyBox rechazó sleep0.2 antes de desconectar; se corrigió a sleep1.
El watchdog restauró la versión anterior antes del segundo intento del helper.
Dos arranques de campaña rechazaron `printf` sobre AQL. Una traza separó
el fallo de escritura de iw: distance0 y `echo` sí devolvieron exit0.
Un fallo de banner SSH ocurrió antes de mutar; se comprobó salud antes de retomar.
La primera captura extensa tardó46,359s y venció el watchdog; no constituye ABAB.
Todos estos intentos y sus salidas se preservan junto a las ocho ventanas válidas.

Cada ventana válida tuvo un guard independiente45s por radio, readback del
tratamiento y restauración exacta. La comprobación final independiente confirmó
coverage0, las cuatro AC originales, firmware sin cambios y ningún iperf propio.
Se conservaron198.18.0.43/24 y198.18.0.81/24 en br-lan.
No se ejecutó network reload ni se escribieron particiones protegidas o firmware.
La única instalación persistente autorizada fue el helper; no se probó cold boot.
Potencia final: AP20dBm, STA17dBm; canal5180MHz/20MHz, sin cambios.

## Procedencia y verificación

La evidencia binaria es histórica y explícitamente delimitada; no equivale
a una nueva comparación ELF del driver desplegado. La verificación de fuentes
iw/mac80211 es nueva. Scholar nativo produjo resultados heurísticos: cero
verificaciones semánticas Jev en vivo. Los claims MemoryMaster quedan candidatos.
El reactor usa una cola privada; no modifica la cola compartida de descubrimientos.
Los guards de este arnés restauran ajustes; los servidores one-shot dependen
de completar la carga. Por eso el cierre exige comprobar ausencia de procesos,
no sólo el estado que devuelve el runner.

- [Capturas y hashes](../artifacts/autoresearch/wave104/runtime_manifest.json)
- [Recibo1662](../artifacts/autoresearch/stage1662a_live_bantime1200_full_dualbind_verification_receipt.json)
- [Recibo1663](../artifacts/autoresearch/stage1663a_live_ptmp_slot_distance_and_aql_triple_play_receipt.json)
- [Gate1667](../artifacts/verification/stage1667a_wave104_codex1_gate.json)

Comando local: `python -m pytest tests/test_stage1662a_to_1667a_suite.py -q`.
El gate distingue adquisición completa, tests locales y aceptación dual-bind.
Ambos comandos `enforce_5pillar_research_gate.py --require-live-hardware`
terminaron exit0. La comprobación final de procesos se repitió leyendo cmdline,
sin depender del tamaño declarado por procfs; la primera lectura se conserva.
