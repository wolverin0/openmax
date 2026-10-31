<!-- doc-head: Stage 3059A (W399) ES: el equipo que respondio en el banco como .112 no es el LTU-Lite 2 sino un Rocket 2AC Prism (airOS 2XC v8.7.11, 2,4 GHz, estacion, 6 dias encendido); no puede ser par LTU de .110, asi que no se escribio nada ni se corrio el PtP ni el A/B -->
Que cubre: la identificacion de solo lectura de .112 y por que la ola se detuvo antes de escribir.
Estado: solo lectura. 1 sesion SSH a .112 (clave de host registrada, sin coincidencia con las claves LTU auditadas). 0 escrituras en .112, en .110 y en /dev/ame.
Datos maquina: artifacts/autoresearch/wave399_ltu_ptp.json.
Leer cuando: antes de volver a intentar el PtP LTU del banco.
<!-- /doc-head -->
# Stage 3059A: .112 no es el LTU-Lite 2 (W399)

## 1. Lectura de .112 (CONFIRMED_LIVE_READONLY)

- **Placa:** Rocket 2AC Prism (sysid 0xe2f2). **Firmware:** 2XC.v8.7.11 (airMAX AC de 2,4 GHz).
- **Modo:** estacion (`radio.1.mode=Managed`), sin enlace (`wlanUptime=0`).
- **Encendido:** unos 6 dias, asi que no es un equipo recien conectado.
- **Clave de host:** no coincide con ninguna de las claves LTU auditadas (1266A).

## 2. Por que se detuvo

- Un Rocket 2AC trabaja en 2,4 GHz con airMAX; no puede asociarse al AP LTU de .110 en 5500 MHz.
- Configurarlo como par seria escribir en el equipo equivocado. No se intento el PtP ni el A/B.
- El Rocket LTU no aparecio en esta ola.

## 3. Que hace falta

- Operador: confirmar que equipo es el LTU-Lite 2 y en que puerto quedo; el OUI f0:9f:c2 y el HTTPS de Ubiquiti son comunes a todo Ubiquiti.
- Avisar tambien que .110 sigue transmitiendo sin par y sin guarda termica (84 C en W392).
- **Karpathy: TARGET_NOT_MET.** Sin enlace no hay snapshots ni A/B; ame_device_writes 0.
