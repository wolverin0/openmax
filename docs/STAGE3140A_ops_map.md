<!-- doc-head: W469 offline operational map of retained LTU 2.4.2 bench sources -->
Identity and metrics are historical W467 observations until coordinator refresh.
No device sessions, native commands, swaps, firmware/config writes or secret exports.
Full source hashes and machine pointers: STAGE3140A_ops_map.json.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# W469: acceso, medici?n y rollback LTU (mapa offline)

El ?ltimo recibo retenido es W467 (31/10, 14:59?15:01Z). Los tres volvieron a firmware oficial 2.4.2; **esto no verifica el estado actual de W469**.

| Nodo | Gesti?n y camino retenido | MAC de radio | Host key SHA256 |
|---|---|---|---|
|ap110|198.18.0.63; PC direct TCP22|PUBLIC_DEVICE_0045|`a2db0ab6dff457121b196178a8a9fd6232a473b34cfff93832af6bc4ce4fe128`|
|rocket|198.18.0.138; PC -> authenticated ap110 -> direct-tcpip to198.18.0.138:22, retained RF route; fresh route/source proof required|PUBLIC_DEVICE_0050|`d3d0bdfcec1b27a4bcaef4493d92d774d9a3b8d30d6202fe8a012e8c3dabe0a3`|
|lite2|198.18.0.140; PC -> authenticated ap110 -> direct-tcpip to198.18.0.140:22, retained RF route; no Loco117 involved|PUBLIC_DEVICE_0043|`90a0f281d10f98e90f7701d298912a4d86b50e8ad78310bbebdf6192b1cad09e`|

Fuente: `STAGE3126A_session.py:19?20,50?66`; peers nativos `STAGE3134A_native.py:11`. Rocket requiere negociar RSA existente (`session:38?41,58?64`); no aceptar autom?ticamente ECDSA nueva. No se usa Loco117. MAC de Ethernet no se deduce de la de radio: .110/Lite2 necesitan lectura fresca; Rocket E6...A4:F6 s?lo es identidad W432 hist?rica.
Credenciales: s?lo pointer `tools/autoresearch/stage861_866_common.py::credential`, cargado por `STAGE3092A_session.py:35?41`; pin se compara antes de autenticar (`114?128`). No valores en este reporte.

## Baseline que s? existe

W467 final 100MHz/5500?5500/MIMO/75?25: .110 capacidad nativa DL495.360 y UL99.038 kbps; Lite2 DL165.120 y UL49.519 kbps. Ideal .110 DL825.600/UL198.077, combinado1.023.677 kbps: **estimaciones**, no goodput de aplicaci?n. Speedtest nativo de SoC a SoC:65,32/32,12Mbps.
`W467.analysis.width_sweep_native.FINAL_100MHz_pinned` y `firmware_ideal_capacity_100MHz_lite1`; doc3134:30?39,61?65. No hay `iperf` ni baseline PC?SoC en el artifact467. W467 documenta eth0 .110 todav?a100Mbps: medir negociaci?n y ruta gigabit fresca antes del nuevo ensayo. El puerto100 NO explica las mediciones anteriores hechas entre SoCs.

## M?tricas y l?mites del parser

`STAGE3134A_native.py:15?29`: af por MAC tx/rx speed y capacity, RSSI remoto/EVM/BLER; en el AP tx es DL y rx es UL. `status.py:19?37` toma ?ndices real/ideal, CINR/EVM TX/RX y capacidad actual/ideal desde status.cgi. Guardar campos crudos y firmware/boot.
?ltimo estado .110: tx_idx2/ideal4, DL CINR25; Lite2 tx_idx0/ideal4, DL CINR21. El emparejado nativo es64QAM6X frente ideal10X; no generalizar a todos los enum/firmwares. Unidades BLER UNKNOWN: status final tiene UL10000 aunque texto W467 anterior diga0. No equivale a packet loss validado.
`status.py:26` etiqueta cualquier MAC ajena a53:99 como Lite2: un nuevo lector debe exigir exactamente53:99 y58:CC completas.

## Secuencia nativa de m?dulos: capacidad est?tica, no swap aceptado

Los scripts extra?dos AP/CPE2.4.2 son byteid?nticos SHA`ff6bcde8...116bdee0`. `ame_drv.sh:146?172,229?289,291?373`: stop ? remove ? insert DIRECTORIO_RAM ? start ? amecli conn0. `restart` s?lo stop/start; no cambia m?dulos.
Insert busca nombres exactos `ame_radio_mod.ko`, `ame_core.ko`, `ame_dev.ko`, `ame_dfs.ko` y cae a stock si faltan. Remove descarga dfs?dev?core?radio. Start no inserta; aplica AME_CFG y ajusta CPU/IRQ. No poner af_cal/air_fpga en el directorio del trial: start puede preferir esas copias.
Stop tiene esperas sin plazo y una rama `/dev/watchdog` si no detecta daemon. Los rc no prueban parada/carga. Antes de operaci?n real: hash del script nativo, originales/ABI/dependencias, flags/PID actuales y rollback stock comprobado. Canario cableado .110 primero. Mantener flash/config/RC A intactos para que reboot elimine B en RAM.
No encontr? una aceptaci?n retenida que pruebe swap completo de m?dulos2.4.2 con rollback aut?nomo de cada RF-only. Un shell watchdog no garantiza salir de un kernel colgado al descargar m?dulos.

## Guardas existentes: qu? reutilizar y qu? no

`STAGE3126A_apply.py:16?24,47?63`: arm?test RAM system.cfg con rc.softrestart test?confirm; watchdog independiente sleep1/reboot salvo /tmp/fmx459/ok. Es antecedente de CONFIG RAM empleado por W467, no validaci?n del unload/reload.
No tiene nonce/boot/PID-starttime/exclusi?n de guard previo ni obligaci?n de armar antes de test. El mismo API tiene persist/cfgmtd y reintentos idempotentes: **excluir persist y no ejecutar este wrapper ciegamente para B**. Adaptaci?n nueva debe probar guard vivo por nodo RF-only antes del cambio y confirmar s?lo tras peer/datos/pin reales.
Stage64 guard (`patch_ltu_ame_core_binary.py:353?388`) s?lo condiciona3sysfs al SHA de core. No carga m?dulos, no comprueba CUR_DEV_SHA en el branch, no restaura, no vigila ni confirma. Los parches del doc64 son evidencia est?tica.
Los wrappers actuales super4096/monitor/12x (`firmware/ltu_safe_kit`, l?neas2?3,19?22) est?n RETIRED: apply/verify/rollback salen65. `fmx_ltu_runtime_transaction.sh` es backlog/qdisc/UCI, no backend del m?dulo LTU.

## Comparaci?n autorizable desde este mapa

1. Lectura fresca pin/board/boot/2.4.2/m?dulos y rutas f?sicas; PC?SoC .110 s?lo con gigabit probado.
2. A/A stock con tr?fico/peers/roles/potencia/ancho id?nticos; goodput receptor, RTT cargado/loss, CPU/memoria/temperaturas y campos nativos.
3. B nombrado como bundle exacto de m?dulos, una sola transici?n/nodo cada vez y guard aut?nomo por RF-only. No atribuir efecto individual a un bundle de varios parches.
4. Volver a A con originales/links/datos comprobados y repetir la misma medici?n. Mantener fallos/rollback sin promoverlos a muestras v?lidas.

Stage3030 es obsoleto (head invalida el corte72C); Stage3061 describe descubrimiento v?a Loco, no la ruta W467; Stage1023 es pasivo, no benchmark. Temperaturas siguen como telemetr?a bajo pol?tica del operador.

Este mapa no ejecut? nada. Gap para el coordinador: negociaci?n gigabit y baseline PC?SoC, identidad/paths actuales, admisi?n del swap y guardas de m?dulo RF-only todav?a requieren evidencia nativa.
