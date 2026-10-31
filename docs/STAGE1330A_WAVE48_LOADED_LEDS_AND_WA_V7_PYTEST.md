<!-- doc-head: Wave48: pruebas locales fail-closed de carga e integración -->
Pruebas desechables sin SSH, separadas de la aceptación física.
<!-- /doc-head -->

# Stage 1330A — Pytest Wave48

La suite verifica cinco ventanas únicas y ordenadas, datos incompletos,
duplicación, cambios no autorizados de daemon y rechazo de CPU inválida.
Los deltas CPU excluyen el doble conteo de guest, rechazan reinicios y
conservan softirq positivo como observación.

Los tests impiden deducir zero-overhead de cinco ventanas LED ON, de un
valor softirq cero o de una bandera declarada como supuesto control.
RAW con hash alterado o transporte fallido no establece lectura real.
La matriz WA usa fixtures Linux desechables y no abre conexiones a radios.
Se verifican ocho casos normales y cinco adversarios del daemon real, identidad
de placa, un LED de enlace frente a cuatro RSSI y rechazo de TAR con modo 0777.
UDP exige nonce/secuencia, ambos tamaños, contabilidad real y RTT null si falta
echo; los RTT vacíos ICMP tampoco se convierten en cero. El CLI de la campaña
sin `--execute` debe devolver PLANNED sin SSH.

El primer pase local quedó en `.git/wave48_initial.xml`: 41 PASS. El gate final
ejecuta la suite ampliada y conserva su propia colección, JUnit y fuentes fijadas.
El defecto de reloj UDP detectado después de la captura queda preservado:
pruebas de aritmética ucode modelada exigen fracciones de segundo y aceptación
antes del deadline; el parser futuro rechaza COVERAGE ausente o fallido.
Estas pruebas locales no sustituyen ejecutar el helper corregido en hardware.

La colección y ejecución deben coincidir exactamente, sin fallos ni saltos.
El coordinador ejecuta en una sola sesión Linux las dependencias locales y
el gate; los archivos temporales no se reutilizan entre entradas WSL.

Recibo: `artifacts/verification/stage1330a_wave48_loaded_leds_and_wa_v7_pytest.json`.
