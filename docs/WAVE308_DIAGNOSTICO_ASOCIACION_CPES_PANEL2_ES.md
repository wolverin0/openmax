<!-- doc-head: Wave 308, diagnóstico de asociación de estaciones en Panel2-Guarida y mecanismo de admisión de CPE airOS stock (solo lectura) -->
Los 15 CPE de Panel2 que "faltaban" no son equipos: son slots modelados de la radiografía (P2_MODELED_SLOT, MAC
02:00:00:82:00:xx). UISP tenía 7 CPE reales y el AP stock mostró 7 estaciones en las 21 muestras previas al cutover;
después del cutover sigue en 7. Corrige Wave 304. Un CPE stock se asocia a un AP OpenWrt por el admitter de Vendor-IE
del AP; allow_80211/op_mode son parámetros del lado AP en airOS. Datos: artifacts/canary_panel2_guarida/wave308_*.json.
<!-- /doc-head -->

# Wave 308: asociación de estaciones en Panel2-Guarida

## 1. Resumen ejecutivo

- **No hay 15 CPE de Panel2 sin servicio.** Las 15 filas faltantes de la radiografía son slots modelados: nombres
  `P2_MODELED_SLOT_nn` (nn de 08 a 22), MAC administradas localmente (`02:00:00:82:00:xx`) y evidencia INFERRED. Se agregaron
  para completar un total supuesto de 22; no corresponden a equipos.
- **UISP lo confirma:** el manifiesto 114A registra en Panel2 7 CPE confirmados en UISP y 15 modelados. Esos 7 son
  exactamente los 7 migrados el 28/10 (.200.213, .210.166, .200.169, .210.239, .200.183, .210.21, .210.83).
- **Antes del cutover ya eran 7:** las 21 muestras guardadas del AP en airOS WA.v8.7.25, de 18:59:47 a 19:22:27 UTC,
  muestran 7 estaciones asociadas en todos los casos. Después del cutover, el AP OpenWrt muestra 7 a las 19:41:42 UTC.
  El cutover no dejó a nadie afuera.
- **Mecanismo:** `allow_80211=1` / `ubnt_op_mode=0` aparecen en este repo como parámetros del **AP** airOS, para que un
  AP stock acepte estaciones 802.11 estándar. Para el caso inverso (CPE stock contra AP OpenWrt) lo probado es el
  admitter de Vendor-IE del AP, que ya asocia a .200.80 en Panel1. La imagen de Panel2 lo incluye.
- **Corrección a Wave 304:** los CPE stock reales que quedan en Guarida son 4, no 20: Panel1 .200.80 y .200.91, Panel3
  .200.68 y .120.30. En Panel3, .210.106 también es un slot modelado.

## 2. Las 22 filas de Panel2

| clase | filas | cómo se identifica |
|---|---|---|
| reales, migradas a OpenWrt el 28/10 | 7 | evidencia CONFIRMED, MAC de fabricante, presentes en UISP (114A) y en el cutover |
| slots modelados, no son equipos | 15 | nombre `P2_MODELED_SLOT_xx`, MAC 02:00:00:82:00:xx, evidencia INFERRED |
| sin clasificar | 0 | - |

La cuenta de "22 CPE" que usan el estado del orquestador y Wave 304 sale de la radiografía modelada de 32 CPE. La
población medida de Panel2 es 7.

## 3. Estaciones vistas por el AP de Panel2 (telemetry.db, solo lectura)

| ventana (UTC, 28/10) | plataforma | muestras | estaciones |
|---|---|---|---|
| 18:59:47 a 19:22:27 | airOS WA.v8.7.25 (stock) | 21 | 7 en todas |
| 19:23:54 a 19:36:03 | reflasheo y arranque | 13 | sin lectura (ERROR / BACKOFF) |
| 19:41:42 | OpenWrt 24.10.4 | 1 | 7 |

Las señales no permiten identificar uno a uno a los equipos entre una muestra y otra: el AP stock rotula a las
estaciones como `peer_N` y el AP OpenWrt como un hash. Pero la cuenta coincide antes y después, y los 7 destinos del
cutover arrancaron OpenWrt y se asociaron.

## 4. Cómo se asocia un CPE airOS stock a un AP OpenWrt

- Un CPE airOS 8 en modo estación airMAX elige un AP que anuncie el elemento de proveedor de Ubiquiti (OUI 00:27:22).
  Un `hostapd` estándar no lo anuncia.
- La ruta probada en esta torre es del lado AP: `panel1_admitter.sh` publica ese Vendor-IE (TLV AES-128-ECB con
  hostname y SSID) durante el barrido del CPE y lo retira enseguida. Así el CPE se une en modo 4-addr WDS normal, sin
  IE. .200.80 (stock WA.v8.7.25) está asociado así a Panel1: en el reporte antes/después figura como híbrido, en MCS5.
- `panel2_admitter.sh` se genera a partir del de Panel1 y va en la imagen de Panel2. Hoy no tiene CPE stock que
  admitir.
- `allow_80211=1` y `ubnt_op_mode=0` sirven para la dirección contraria. El validador híbrido los describe como
  "Hybrid airOS 8 AP (allow_80211=1, op_mode=0) <-> OpenWrt STA", y el arnés PtMP los pone al convertir un radio stock
  en AP de sector. En WA.v8.7.11 son parámetros de `umac.ko` (`host_80211_enable`, `ubnt_op_mode`). En los bancos PtP,
  `ubnt_op_mode` vale 0 en el AP y 1 en la estación: es un ajuste por rol.
- **Conclusión:** un CPE stock no necesita cambiar sus propios `allow_80211`/`op_mode` para entrar a estos AP
  OpenWrt; el admitter del AP le da el IE que busca. Tocar esos parámetros en el CPE no está probado para el rol de
  estación en este repo e implicaría escribir en cada CPE de cliente. La otra ruta probada es migrar el CPE a OpenWrt.

## 5. Discrepancias con el brief

- El brief nombra a las 7 estaciones migradas como .45, .69, .71, .73, .89, .157 y .177. Ninguno de esos octetos
  aparece en el recibo del cutover. Las direcciones reales son las de la sección 1.
- El brief parte de que un CPE stock necesita `allow_80211=1` / `op_mode=0`. La evidencia del repo ubica esos
  parámetros en el AP airOS, y la ruta para un CPE stock es el admitter (sección 4).

## 6. Qué queda abierto

- No hay en disco una muestra del AP de Panel2 posterior a 19:41:42 UTC. Para seguir de cerca el sector conviene una
  lectura de solo lectura de la tabla de estaciones, aunque ya no se espera una caída.
- Wave 304 (`docs/WAVE304_MATRIZ_PRIORIDAD_CPES_PENDIENTES_GUARIDA_ES.md` y su JSON) clasifica como reales a 16 slots
  modelados. Requiere corrección; este trabajo no la modificó porque está fuera del alcance de esta tarea.
- El estado del orquestador sigue diciendo "Panel2 22 CPEs"; la cifra medida es 7.

## 7. Fuentes

Radiografía de 32 CPE; manifiesto 114A (conteos UISP); recibo del cutover de Panel2 del 28/10; reporte antes/después
del 28/10; telemetry.db leída con `mode=ro`; `tools/panel2/build_panel2_and_7cpe_openwrt_images_20261028.py`;
`tools/panel1/panel1_admitter.sh`; validador híbrido; bancos stage84a y stage86a; arnés PtMP; auditoría 2545A. Todas
están fijadas por sha256 en el JSON.
