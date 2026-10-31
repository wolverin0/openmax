<!-- doc-head: Historial Wave38 y actualización Wave47: AP-PTMP RAM activo con aceptación powerout menos4 a0 -->
Wave47 activó el AP en RAM; Wave38 permanece como historial fallido. OTA y persistencia se evalúan por separado.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1269A — Banco LTU de tres nodos

## Actualización operativa — Wave47

**Stage1320A: AP_RUNNING_RAM_VERIFIED**, 5500MHz,20MHz,FMX-LTU, ganancia26.
La captura aceptó `powerout=0`, dentro del nuevo intervalo autorizado `[-4,0]`.
`ath0` estaba arriba, AME activo y el PID4615 ejecutaba el binario con SHA256 verificado; máximo térmico68°C.
No se escribió mtd5 ni se instaló persistencia: la activación es únicamente RAM.
La evidencia y el sondeo OTA contemporáneos están en [Stage1323A](STAGE1323A_RESTAURACION_ACTIVA_AP_PTMP_RAM_LTU110_POWEROUT_MENOS4_ES.md).

## Resultado operativo de Wave38 — histórico

**INCOMPLETE. LTU-Lite #1 quedó con el servicio de radio detenido por rollback.**
No se confirmó asociación OTA, persistencia tras reinicio ni Champion v20 en tres nodos.
La gestión SSH de `.110` siguió accesible. No se reiniciaron equipos ni se modificaron puertos o PoE.

| Nodo | Identidad esperada | Evidencia de esta ejecución |
|---|---|---|
| Lite #1 `.110`, gi5 | `PUBLIC_DEVICE_0045` | Modelo y MAC confirmados; firmware `afltu.v2.4.0`; inicialmente CPE/Reset, sin enlaces. AP verificado transitoriamente en intento3; posteriormente detenido. |
| Lite #2 `198.18.0.72`, gi7 | `PUBLIC_DEVICE_0043` | FDB nativa en `0/7`; IPv6 `e263` y forma histórica `e063`, y salto desde `.110`, sin acceso SSH confirmado. |
| LTU-Rocket | `PUBLIC_DEVICE_0050` | Sin identidad, temperatura ni asociación actuales verificadas; ausente de la FDB capturada. |

La MAC en una FDB y un puerto físico activo demuestran presencia Ethernet observada; no prueban asociación radio.
VLAN actual de Lite #2: **UNKNOWN**, porque la consulta de VLAN agotó el tiempo.
La hipótesis histórica VLAN107 no se presenta como estado actual.

## ES-10XP

Destino autorizado: `PUBLIC_DEVICE_0052%29`.
La autenticación SSH solicitada falló; se conservó el fallo. La identidad documentada previamente permitió lecturas REST.
`GET interfaces` confirmó `gi1..gi8` activos; gi2 a100Mbps y los restantes a1Gbps, incluidos gi5/gi7.
gi7 figuró con PoE24V y STP forwarding. No hubo cambios de puertos, VLAN, alimentación o configuración.
Las rutas REST inexistentes y los timeouts permanecen en los recibos.

## Arranque y rol

El poststart existente declara AP y FMX-LTU, pero contiene `powerout=28` y ganancia13.
El archivo generado `/tmp/ame.cfg` también declara AP; eso no demuestra el rol efectivo del controlador.
El log contiene permiso denegado en `send_map_enable` y un fallo de segmentación.
Esos mensajes son observaciones; no se atribuye a ellos la causa exacta del reinicio ni del fallo completo del poststart.

El binario activo y `/tmp/air_fpga` coinciden:2359369bytes,
SHA256 `264165b450bc72a5223942f657cf34b1b2d478a32401780fc49a26aa693fd37a`.
Su byte en `0x1acc33` es `ea`. Se reutilizó; no se cargó un binario nuevo.

El `ame_dev.ko` leído del equipo tiene SHA256
`7c55b6569ead4ec612f32759c0acbe251d879afbb8435cd0690f1e093f8c359d`.
La inspección ARM muestra la lectura del identificador de configuración en `.text+0x814`
y las constantes `0xae05`/`0xae0e` en `0x818`/`0x81c`, concordantes con el bloqueo documentado en Stage17B.
Con configuración RAM `0xae08`, intento2 devolvió CPE; con `0xae05`, intento3 devolvió AP.
La identidad física, las particiones de arranque y la calibración permanecieron sin escrituras.
Esto demuestra la diferencia de rol en estas ejecuciones; la causa del reinicio original sigue UNKNOWN.

## Intentos, protección y estado final

1. Intento1: el `nohup` local rechazó `sh -c` sin `--`; el PID no sobrevivió.
   La recuperación inicialmente defectuosa detuvo la radio aunque no había comenzado el cambio RF.
   Se corrigió el controlador y se agregó una regresión que impide ese rollback previo a RF.
2. Intento2: watchdog45s verificado, configuración térmica mínima y controlador inicializado;
   rol efectivo CPE. El verificador rechazó el resultado y dejó la radio detenida.
3. Intento3: alias RAM `0xae05`; readbacks reales AP-PTMP,5500MHz,20MHz,FMX-LTU y ganancia26.
   Se solicitó `powerout=0`, pero el readback fue **−4**. Su causa exacta no se estableció.
   El contrato exacto0/26 no pasó; hubo rollback y la radio quedó detenida. No se siguió reintentando.

Las preimágenes y los backups de mtd0/1/4/5 se guardaron y verificaron en almacenamiento privado fuera del repositorio.
Los intentos fallidos, sus fuentes ejecutadas y las salidas nativas están conservados.
El sanitizador de `.security.psk` se corrigió; los secretos se depuraron también de las capturas anteriores.
La corrección de privacidad está declarada; no se presenta como una nueva adquisición de hardware.

Temperaturas iniciales medidas: temp0=69,temp1=69,rtemp0=68,rtemp1=69°C.
El guard nativo exigió los cuatro sensores válidos y ≤70°C durante la inicialización.
Con el ASIC detenido, `af get temp*` devuelve error255: **no es una temperatura de255°C**.
La recuperación declaró temperatura previa al arranque UNKNOWN; no sustituyó lecturas frescas por el antiguo69.
El snapshot final no confirma una temperatura actual ni un enlace operativo.
No se midió potencia RF física; las consignas y el readback no son una calibración conducida.

## Persistencia y Champion

El mapa real identifica mtd4 como EEPROM y mtd5 como `cfg`.
El contrato del proyecto prohíbe escribir mtd5; por eso **no se ejecutó cfgmtd**.
El hook persistente no se instaló, no se afirma persistencia y no hubo prueba de arranque en frío.
El poststart heredado permanece pendiente de una corrección persistente autorizada para este mapa de particiones.
Los kits históricos v20 están retirados; los parámetros leídos no prueban Champion v20 activo.
No hubo aplicación de kits v20 ni acceso directo a `/dev/ame*`.
Las llamadas permitidas a `af`/`amecli` no instrumentan sus accesos internos.

## Evidencia y siguiente acción

- [1266: auditoría](../artifacts/verification/stage1266a_ltu_es10xp_and_poststart_audit.json).
- [1267: restauración fallida y rollback](../artifacts/verification/stage1267a_ltu_ap_ptmp_restoration_receipt.json).
- [1268: snapshot pasivo final](../artifacts/verification/stage1268a_ltu_live_link_and_thermal_snapshot.json).
- [1271: gate de pruebas y misión](../artifacts/verification/stage1271a_wave38_codex1_gate.json).
- [Controlador](../tools/bench/restore_stage1267a_ltu_ap_ptmp_and_ota_link.py) y [suite](../tests/test_stage1266a_to_1271a_suite.py).

Wave47 resolvió la consigna0 frente al readback−4 mediante autorización explícita del intervalo `[-4,0]`.
La persistencia sobre mtd5 sigue fuera del alcance RAM autorizado; el acceso y la asociación de los otros nodos se informan en Stage1323A.
La versión exacta de este documento correspondiente al gate Wave38 está archivada en `artifacts/verification/wave47/prior_wave38/`.
