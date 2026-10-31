<!-- doc-head: Wave44: pruebas de perfiles RSSI y regresión afectada Wave37 -->
Fixtures Linux desechables, configuración segura y telemetría real del daemon.
<!-- /doc-head -->

# Stage 1306A — Pruebas de perfiles y telemetría

La suite Wave44 cubre producción60 y bench65, límites inclusivos, legado55,
prioridad de entorno, archivo explícito, rutas inseguras, enlaces simbólicos,
claves duplicadas/desconocidas, inyección, tipos y orden inválidos.
El daemon real corre sobre sysfs Linux desechable y un `iw` controlado;
los tests comprueban JSON, timestamps, asociación, brillo y preservación POWER/LAN.
Todos los escenarios nativos comparten una única entrada Linux por suite.

Los tests del verificador rechazan JSON inválido, pérdida ICMP mal contabilizada
y recibos incompletos. Los CLI de despliegue/verificación sin `--execute`
deben devolver PLANNED sin abrir SSH ni capturar datos de los radios.
El overlay incluye cuatro miembros y conserva su perfil de producción60.

El gate ejecuta además `tests/test_stage1260a_to_1265a_suite.py` como regresión
afectada. Su fixture especifica ahora legado55 explícitamente; sus expectativas
históricas permanecen intactas. El paquete añade configuración como cuarto miembro.

El primer intento Linux no encontró pytest: no hubo colección ni resultado de
tests. Se restauraron dependencias Python puras locales, sin descargas.
El primer pase Wave44 obtuvo 73 PASS antes de ampliar las pruebas del host.
Su XML queda en `.git/wave44_initial.xml`; el gate final conserva una ejecución
nueva con colección/JUnit identificados, cero fallos y cero saltos.

Recibo final: `artifacts/verification/stage1306a_wave44_rssi_profiles_pytest.json`.
Pruebas locales no prueban luz visible; aceptación visual física UNKNOWN.
