<!-- doc-head: 1328A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# Four WA board LED association fixtures using the real shell daemon

Status: CONFIRMED_SIMULATED_FIXTURES_ONLY; atribucion: daemon Linux/sysfs ejecutado en fixtures descartables.

Ocho casos: cuatro placas por asociado/no asociado, ejecutando el shell real en Linux.
PBE conserva cuatro barras; LBE y NS Loco blue:power; LAP-120 white:dome como indicador de enlace.
Se verifican readback de brillo, JSON, identidad, layout, led_count y RSSI logico.
Cinco controles adversarios exigen fallo sin modificar ningun campo de LED.
Los otros LEDs conservan byte por byte sus valores y triggers.
iw y jsonfilter usan respuestas de fixture; no hubo RF, SSH, radios ni imagenes desplegadas.
Estas pruebas NO establecen aceptacion fisica PtMP ni rendimiento de enlaces.
