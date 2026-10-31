<!-- doc-head: W416: identificación física del Rocket, perfil incompatible y prueba RAM preparada; transporte impidió aplicarla -->
Captura pasiva 60,265 s: PUBLIC_DEVICE_0050 / 198.18.0.136, LTU-Rocket del inventario; 37 ARP, cero drops.
Rocket: AP-PTMP 5725/20 PUBLIC_TERM_0007 AES1; .110: AP-PTMP 5500/20 FMX-LTU AES0. Ambos sin pares en las lecturas.
Dos intentos de prueba terminaron antes de autenticar al Rocket por timeout de canal: cero cambios RF/LTU.
Todos los alias y rutas creados quedaron restaurados. Enlace y benchmark NO establecidos; continúa W420.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# W416 — Identificación y preparación; enlace pendiente

## Inventario observado

| Equipo | Identidad y dirección | Evidencia |
| --- | --- | --- |
| LTU-Lite #1 | PUBLIC_DEVICE_0045, 198.18.0.63, afltu 2.4.0 | Lectura autenticada con clave fijada; AP real, board RAM 0xae05 preservado |
| LTU-Rocket | PUBLIC_DEVICE_0050, 198.18.0.136, aflturocket 2.1.0 | ARP y amecli; board 0xae05/name LTU-Rocket; eth0 PUBLIC_DEVICE_0082 en otra superficie |
| LTU-Lite #2 | PUBLIC_DEVICE_0043 | No observado en esta captura; dirección/configuración/estado actuales UNKNOWN |

La captura de 60 s contiene 37 tramas ARP, de un único emisor, solicitando gateway 198.18.0.2. No observar al Lite #2 no prueba que esté apagado. El IP sanitizado de W401 no se convirtió en una dirección actual por inferencia.

La primera clave SSH del Rocket se registró como first-seen, no como pin histórico: `d3d0bdfcec1b27a4bcaef4493d92d774d9a3b8d30d6202fe8a012e8c3dabe0a3`. Las lecturas posteriores fijaron esa clave y comprobaron board/modelo y la MAC eth0 observada. No se inventó una regla de conversión entre E0 y E6. Los saltos .20 y Loco se validaron con sus pines retenidos; .20 no recibió ningún exec.

## Desajuste comprobado

| Campo | .110 | Rocket |
| --- | --- | --- |
| Rol observado | AP-PTMP(Run), cero pares | AP-PTMP(Run), cero pares |
| Canal/ancho | 5500/20 | 5725/20 |
| SSID | FMX-LTU | PUBLIC_TERM_0007 |
| AES/autolink | 0 / 1 | 1 / 0 |
| Frame/duty en config | 2000 / 750 | 2000 / 750 |
| Powerout/ganancia | -4 / 26 | 46 / 26 |
| Cuatro sensores | 86/86/86/86 °C | 80/80/80/80 °C |

Los dos AP y sus perfiles distintos no constituyen una pareja AP/CPE. Se preparó Rocket como CPE 5500/20 FMX-LTU sin AES y con autolink, preservando board, potencia, ganancia y campos ajenos. El objetivo no consistía en cambiar 0xae05 del AP al ID físico de Lite 0xae08.

## Preparación verificada y ejecución real

Se inspeccionó el `ame_drv.sh` exacto del Rocket: SHA256 `27bb53a4ea50e49a26253fa2361fd301187c73b3e2a8879be747fc1b2bf15092`. No se invocaron ciegamente lanzadores de otras olas. El plan contiene copia privada byte exacta, cambios por clave sin divulgar claves AES, validación del ash real antes de activar, guard independiente de 600 s con techo de 1200 s, límites PID/starttime para stop/start, y restauración de archivo y perfil activo antes de desarmar. La revisión independiente resolvió tres hallazgos del código antes de permitir el ensayo.

Las pruebas locales del constructor pasaron: destino correcto, conservación de bytes ajenos/secretos y rechazo de claves duplicadas/board incorrecto. Un intento opcional de sintaxis en WSL tuvo WSAETIMEDOUT; no se reinició WSL ni se reutilizó como aceptación. El gate de sintaxis del Rocket estaba previsto antes de toda acción RF.

**La prueba no llegó a esos pasos:** `trial1.json` y `trial2.json` terminaron abriendo el canal Loco→Rocket, antes de autenticar al Rocket, tomar backup o subir scripts. No se creó un lock ni se armó un guard en el LTU. Cero cambios de perfil, reinicios de driver, flash o dispositivos de producción. El segundo intento conservó la primera falla y añadió evidencia del vecino LAN y un límite de apertura mayor.

## Limpieza y límites

Ambos intentos verificaron que dirección y ruta LAN de la Loco coincidían exactamente con sus preimágenes, además del mismo boot. Nunca se recargó la red/wifi ni se cambió el tráfico de W394. La captura y los diagnósticos sin alias no modificaron direcciones.

La causa del timeout no quedó demostrada en W416. La diferencia entre MAC ARP y eth0 no se convirtió en explicación causal ni se modificó la caché de vecinos. W420 aporta una instrucción posterior de sesiones persistentes, keepalive y reintentos; sus resultados pertenecen a esa ola.

No hubo enlace aceptado ni ventana de throughput/latencia de cinco minutos, ni mejora Karpathy. El gate confirma exclusivamente identificación, lecturas, preparación y limpieza, con `full_gate_pass=false`. Recibo principal: `artifacts/autoresearch/wave416_ltu_link.json`; continuación autorizada: W420.
