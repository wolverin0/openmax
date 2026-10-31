<!-- doc-head: Wave53: pruebas del daemon real, paquetes y regresiones afectadas -->
Fixtures desechables Linux, sin SSH ni tráfico a radios.
<!-- /doc-head -->

# Stage 1360A — Pytest Wave53

La suite nueva ejecuta el shell real en cuatro layouts de placa y traza los
comandos: descubrimiento inicial, un iw por poll, un mv y cero text filters.
Prueba cadencia/config/env, asociación perdida, hijo AP/VLAN creado después del
arranque, peor cliente devuelto y cache de brillo mediante contador y mtime.
Identidad ausente/desconocida, banco parcial y trigger activo en verify fallan.

Los fixtures de paquetes comprueban TAR0755/0644, imágenes/históricos intactos,
ownership de ambos kits antes de escribir y rechazo de drift ajeno.
Los tests del router distinguen counters de configuración y bloquean comandos
mutantes o el puerto PoE protegido. Los límites CPU se comparan sin redondear.

El gate ejecuta además suites Wave37 y Wave44. Sus fixtures identifican
explícitamente PowerBeam. La validación JSON migra de forma explícita al esquema
aditivo: mantiene valores/campos originales y valida cada métrica nueva tipada
y sysfs_name; no hay skips ni eliminación de casos.

Colección/JUnit deben coincidir exactamente y las fuentes permanecer iguales.
Recibo: `artifacts/verification/stage1360a_wave53_zero_filter_led_pytest.json`.
