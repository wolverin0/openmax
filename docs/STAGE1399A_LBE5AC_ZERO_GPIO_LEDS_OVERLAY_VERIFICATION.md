<!-- doc-head: 1399A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# LiteBeam zero-GPIO LED compatibility in isolated future overlays

Estado: CONFIRMED_STATIC_AND_SIMULATED; solo fuente/overlay aislado y fixtures Linux.

Stage1314 confirma que el DTB LiteBeam no declara GPIO LEDs; Stage1344 fija identidad0xe7f9.
La identidad exacta ubnt,litebeam-ac-gen2 acepta cero LEDs, sin crear nodos ni tocar GPIO.
Si existe blue:power, se usa como indicador de asociacion; si falta, led_count0 y led_states[].
layout none_or_power_only, RSSI logico0..4 y JSON conservan semanticas separadas.
Board ID opcional, si aparece, debe ser0xe7f9; unknown y PBE parcial fallan cerrado.
Dieciseis fixtures: perfiles v17/WA, AP/STA, asociado/no asociado, ceroLED/power; tres adversarios.
Overlays shipping v17/WA y aliases comunes sincronizados a899; init/config/boot exactos1358.
Preimagenes1358 preservadas por hash; manifests/TAR activos actualizados, filas ajenas intactas.
La fuente versionada694, daemon en dispositivos, imagenes y recibos1358 permanecen intactos.
No se ejecutaron SSH, RF, flash ni nuevos datos fisicos PtP-Colo.
