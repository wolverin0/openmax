<!-- doc-head: W469 LTU 2.4.2, derivado m?nimo 4096QAM RAM y evidencia separada -->
Estado EN CURSO: primera vuelta A verificada; segunda referencia RF y replay de red en preparaci?n.
Tres equipos bench; cero escrituras de firmware/particiones/configuraci?n persistente.
Capacidad nativa estimada, modulaci?n efectiva y goodput PC-to-SoC son evidencias distintas.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# W469 ? LTU 4096QAM sobre firmware oficial 2.4.2

## Contrato e identidad

S?lo Rocket LTU, Lite1 `.110` y Lite2. Recibo principal: `artifacts/autoresearch/wave469_ltu_4096_patched.json`.
Contrato aislado W469, ventana m?xima 240 min; cierre conservador 31/10 22:35 UTC. Nunca producci?n, flash ni particiones protegidas.
Rocket `PUBLIC_DEVICE_0050`, Lite1 `PUBLIC_DEVICE_0045`, Lite2 `PUBLIC_DEVICE_0043`.
Firmware exacto `aflturocket.v2.4.2` / `afltu.v2.4.2`, kernel `3.14.65`. Acceso directo `.110`, dos SSH RF encaminados por `.110`; no acceso a Loco/LAP/PBE.

## RE: el parche hist?rico de potencia no desbloquea 4096QAM

**CONFIRMED est?tico:** en `auto_pwr_decision`, el mapa MCS reduce 31 a 6 y el c?lculo `6-index` selecciona la primera pareja de `table_ptpPwrRange`. El parche Stage64A cambi? la ?ltima pareja (QPSK) y dej? en cero la de 4096QAM. No se carga esa modificaci?n equivocada.
Los campos tienen evidencia de l?mites de potencia recibida; atribuirles unidades de potencia TX ser?a incorrecto. Las tablas PtMP `table_APPwrRange` y `table_CPEPwrRange` son distintas.
**CONFIRMED est?tico:** las tablas PtMP MIMO contienen `(31,1)`; la variante SISO termina en 23. Esto habilita una hip?tesis de techo 31, no prueba que el selector o enlace use realmente 12X.
El antiguo guard Stage64A no carga m?dulos, no valida el SHA del m?dulo dev y escribe techo 11. Los wrappers posteriores `super4096`/`12x` est?n retirados (exit 65). No sirven como watchdog de esta prueba.

## Derivado m?nimo revisado

Se reconstruy? desde los originales exactos capturados en los tres equipos, conservando bytes y geometr?a ELF, relocaciones y metadatos salvo offsets expl?citos.
Core: umbrales `startThrd_4096` 97?90 y `stayThrd_4096` 90?82; setter `autoMcsCeiling` omite el reinicio de `adj_mcs` a `0x20`.
Dev: `frame_len_store` cambia el acceso 0x54?0x5c. No se toca `automcsUpDown` ni ninguna de las tres tablas de potencia.

| Pieza | SHA256 derivado |
| --- | --- |
| Core Lite | `184201fd427fd7780b1e63f9e9f7e5117b67f565a4c8631b851008a2b74d77d6` |
| Core Rocket | `3f544c66a261a7b0724c3b3abb4950ea76eab6b720a48113ee37bb72021dbaba` |
| Dev ambas familias | `37eea1f7ee1b29bcdf59648191cabe729110377898413fb4a930a46c236daec2` |

Fuentes y manifiesto: `docs/STAGE3140A_patched_modules/`. Revisi?n independiente: `docs/STAGE3140A_binary_independent_review.json` (bytes/ABI/identidad de archivos, no ejecuci?n). El m?dulo ARM EABI5 es de 336 B en `__this_module`; la cifra 384 B pertenec?a a otro kernel/MIPS y no aplica aqu?.

## Referencia fresca A

A las 18:52 y 18:55 UTC, dos enlaces oficiales 100 MHz, 5500/5500, frame 2000, duty 750, techo 23, autoMcs4096 10.

| Equipo desde AP | DL / UL estimada kbps | DL / UL ideal kbps | DL / UL CINR observado | Modulaci?n DL / UL |
| --- | --- | --- | --- | --- |
| Lite1 | 495360 / 49519 | 825600 / 198077 | 23 / 17?18 | 6X / 2X |
| Lite2 | 82560 / 24759 | 412800 / 99038 | 19 / 6?7 | 1X / 1X |

BLER se conserva crudo, unidades UNKNOWN; no equivale a p?rdida IP. EVM se conserva nativo sin conversi?n inventada.
La referencia ideal solicitada 826/198 Mbps es una estimaci?n de firmware para Lite1, no TCP. W467 final ten?a Lite1 495360/99038 y Lite2 165120/49519 kbps; su speedtest 65,32/32,12 Mbps fue SoC-a-SoC.

## PC-to-SoC y estado del banco

Lectura fresca `.110`: eth0 1000/full/carrier 1; PC NIC29 1 Gbps, origen `198.18.0.135`, destino `.110` por Ethernet. Bridge `br1` s?lo `eth0.1`, cuyo iflink 2 coincide con ifindex f?sico eth0 2. Esta ruta no mide goodput RF.
La primera admisi?n del medidor rechaz? correctamente antes de tr?fico la topolog?a VLAN a?n no contemplada. Se agreg? prueba positiva de padre f?sico y negativas de padre ajeno, RF adicional y transici?n de m?dulos. 26 fixtures offline PASS; a?n no equivalen a tr?fico real.
A 19:06 UTC Rocket inform? una estaci?n y Lite2 dio `No route to host` en tres reconexiones de s?lo lectura. Ocurri? antes de cargar m?dulos o cambiar RF/config. Master avisado en `<orca-id>`; respuesta `<orca-id>` (19:08:59Z) autoriza continuar Rocket + Lite1. Lite2 queda como gap, sin SSH ni recuperaci?n; s?lo se agrega al final si vuelve. Se fija expl?citamente la cohorte de un CPE antes de A/A, conservando las lecturas previas de dos.

## Retorno y l?mites de aceptaci?n

Cada cambio se prepara s?lo en `/tmp`; archivos originales y configuraci?n permanecen fijados por hash. El loader nativo detiene, descarga los cuatro m?dulos, exige ausencia de los cuatro y reci?n inserta el conjunto derivado/dependencias stock.
El guard commit-confirm debe estar vivo antes del ciclo; al expirar pide reboot hacia originales. Un watchdog de usuariospace no garantiza recuperar un kernel completamente bloqueado. La primera revisi?n del runner bloque? arm/launch por fallos concretos y se conserva en `docs/STAGE3140A_swap_review_initial.json`.
La aceptaci?n de B requiere readback del techo 31, enlace/SSH del tr?o y mediciones A/A?B?A. Techo 31 o archivo SHA correcto no prueban que la modulaci?n efectiva haya llegado a 12X. No habr? PASS de objetivo por una simulaci?n o una admisi?n offline.
La vuelta A usa reboot controlado, intenci?n ?nica sin repetir por p?rdida de transporte, boot nuevo y readback de archivos/configuraci?n/valores nativos y enlaces.

## Admisi?n del canario 19:25?19:27 UTC

27 checks del runner corregido PASS y revisi?n independiente adjunta. El primer lector host fall? por concatenar owner sin newline con status; se conserv? el fallo y se corrigieron ?nicamente separadores de lectura. Los scripts nativos guard/cycle siguieron byte-id?nticos; la adopci?n host exigi? hashes nativos intactos y m?s de 120 s de plazo restante antes del primer ciclo.
La ausencia real de los cuatro m?dulos qued? retenida antes de insertar. Los cuatro volvieron Live y el canario pas? de Scan transitorio a Run, con 1/31/2000/750. SSH nuevo con pins a .110 y Rocket prob? management y enlace; confirmaci?n a 19:26:07 y salida del guard observada a 19:27. No se obtuvo hash de c?digo cargado en memoria ni se infiere 12X del techo 31.
A/A PC-to-SoC (tres parejas): PC?SoC 81,66?102,88 Mbps, SoC?PC 28,25?29,04 Mbps; todos con limpieza verificada. Esta banda observada gobierna la comparaci?n, sin umbral de mejora inventado.

## Primera vuelta A y hallazgo de ciclo de vida

El Rocket recibi? un ?nico ciclo no confirmado a 19:30:31. La gesti?n dej? de responder aunque el canario segu?a asociado. No se repiti? la mutaci?n ni se confirm? el guard. Despu?s del plazo del guard y del reboot controlado ?nico de .110, ambos volvieron con boot nuevo y originales: Lite1 `<uuid>`, Rocket `<uuid>`. Los cinco SHA core/dev/loader/system.cfg/ame.cfg coincidieron; feature 10/23 y frame/duty 2000/750. La causa exacta del reboot del Rocket es INFERRED compatible con su guard; no se conserv? una traza de ejecuci?n de reboot en RAM.
El reload del canario cambi? el MAC del netdev Linux ath0 de stock PUBLIC_DEVICE_0085 a PUBLIC_DEVICE_0045. El reboot stock restaur? e6. Su topolog?a router br0?eth0.2, br1?eth0.1 es igual en ambos estados: la ausencia de ath0 del bridge NO es evidencia de un fallo en el CPE.
Rocket stock: ath0 PUBLIC_DEVICE_0050, master br0; eth0 aislado en br2. El loader nativo no repite la configuraci?n de MAC/bridge al recrear el netdev. La p?rdida efectiva de bridge del Rocket sigue INFERRED porque no se pudo leer el estado durante el fallo. El setter de MAC del driver s?lo hace commit del MAC del netdev en RAM; los generadores stock ejecutan ifconfig ath0 hw ether. Nunca se ejecutar? afcal ni se derivar?/escribir? identidad de f?brica. Evidencia: `STAGE3140A_network_replay_rca.json` y `STAGE3140A_network_replay_native_calls.json`.
La primera prueba SSH v?a .110 acredit? conectividad y Run; por s? sola no acredit? la ruta de egreso ni la preservaci?n de atributos de red. La segunda vuelta exigir? comparaci?n del snapshot stock y readback de MAC/master/bridges despu?s del ciclo. El primer intento y todas sus fuentes permanecen en module_trial_history/stock_restoration_history; no se borran al cualificar el boot nuevo.
