<!-- doc-head: 1400A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# PtP-Colo offline post-health comparator and partial cached baseline

Estado: PLANNED_WITH_VERIFIED_PARTIAL_CACHED_BASELINE; sin red ni ejecucion de comandos remotos.

Baseline Stage1344 validada por identidad/IP/MAC0xe7f9 y metricas RSSI/ruido/tasas del recibo cacheado.
Stage1344 no incluye ping ni muestra ether10-colo: baseline de salud completa UNKNOWN.
Default dry-readonly PLANNED, salida20; post-migration UNKNOWN y ninguna afirmacion postflash.
Input opcional --post-json exige ambos extremos reales .105.62/.54, replies ping reales y MK2-RS/ether10-colo.
Ausencias, ceros sin replies, identidades distintas, tipos invalidos o hashes discrepantes salen INVALID.
Se comparan RSSI/ruido/tasas; ping y router no inventan deltas cuando faltan en baseline.
Replays SIMULATED_FIXTURE pueden validar formato/contabilidad sin convertirse en evidencia live.
Incluso JSON live-submitted no certifica migracion, flash ni no-inferioridad sin prueba independiente.
No hay imports de red ni transporte; ningun SSH, router, radio o archivo de firmware se modifica.
