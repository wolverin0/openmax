<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1299A - matriz de LEDs ath79 leida del script compartido 01_leds extraido de las cuatro imagenes 24.10.4, con PBE-5AC-Gen2 confirmado con cuatro LEDs RSSI y las otras tres boards fuera del script porque sus LEDs vienen del device tree, y con el intento SSH a 198.18.0.45 rechazado en autenticacion -->
# Stage 1299A — Matriz de LEDs ath79 y auditoría 30 de 30

- **Recibo principal**: [`artifacts/verification/stage1296a_live_ath79_01_leds_complete_matrix.json`](../artifacts/verification/stage1296a_live_ath79_01_leds_complete_matrix.json)
- **Extracción offline**: [`artifacts/verification/stage1290a_squashfs_board_d_01_leds_extraction.json`](../artifacts/verification/stage1290a_squashfs_board_d_01_leds_extraction.json)
- **Ledger**: [`artifacts/verification/stage1298a_stages1100a_to_1259a_continuity_ledger.json`](../artifacts/verification/stage1298a_stages1100a_to_1259a_continuity_ledger.json)
- **Alcance**: lectura offline de las imágenes. Sin escrituras, sin cambios de configuración.

## 1. El intento contra el equipo vivo y por qué no se usó

Se intentó leer `/etc/board.d/01_leds`, `/etc/board.json` y `/sys/class/leds/` por SSH en
`198.18.0.45` con las credenciales dadas. El puerto 22 respondió, pero la sesión fue **rechazada en
autenticación**:

```
AuthenticationException: Authentication failed
```

No se probaron contraseñas en serie ni se intentó `.242`. El contenido se obtuvo por otra vía.

## 2. La vía que sí funcionó: SquashFS offline

En la Wave 42 el lector SquashFS en Python puro fallaba en los 48 bloques de fragmento. La causa estaba
localizada y era mía: **los bloques de fragmento no llevan la cabecera de 4 bytes** que yo asumía; la
tabla ya da el tamaño y el bloque empieza directamente por el magic XZ.

Corregido, la extracción funciona en **4 de 4 imágenes**:

```
script_bytes = 23.616      lineas = 559      compatibles ubnt,*  = 15
```

## 3. La matriz, con lo que el script dice y lo que no

| Board | Compatible | ¿En `01_leds`? | LEDs RSSI | Estado |
| :--- | :--- | :-: | :-: | :--- |
| **PBE-5AC-Gen2** | `ubnt,powerbeam-5ac-gen2` | **sí** | **4** | **CONFIRMED** |
| LBE-5AC-Gen2 | `ubnt,litebeam-ac-gen2` | no | — | **REFUTED** |
| LAP-120 | `ubnt,lap-120` | no | — | **REFUTED** |
| NS-5AC-Loco | `ubnt,nanostation-ac-loco` | no | — | **REFUTED** |

El caso del PowerBeam está **compartido** con `ubnt,nanostation-ac`, `ubnt,nanobeam-ac`,
`ubnt,nanobeam-ac-gen2` y `ubnt,nanobeam-ac-xc`, y declara exactamente cuatro barras:

```sh
ucidef_set_rssimon "wlan0" "200000" "1"
ucidef_set_led_rssi "rssilow"       "RSSILOW"       "blue:rssi0" "wlan0" "1"  "100"
ucidef_set_led_rssi "rssimediumlow" "RSSIMEDIUMLOW" "blue:rssi1" "wlan0" "26" "100"
ucidef_set_led_rssi "rssimediumhigh" "RSSIMEDIUMHIGH" "blue:rssi2" "wlan0" "51" "100"
ucidef_set_led_rssi "rssihigh"      "RSSIHIGH"      "blue:rssi3" "wlan0" "76" "100"
```

**`CONFIRMED`**: el PowerBeam 5AC Gen2 tiene **cuatro LEDs de barra RSSI** en `blue:rssi0..3`, con
umbrales 1/26/51/76 sobre 100.

**`REFUTED`**: que las otras tres boards estén cubiertas por `01_leds`. `litebeam` aparece una sola vez y
como `ubnt,litebeam-m5-xw`; `lap-120` aparece **cero** veces; y de NanoStation solo están
`ubnt,nanostation-ac`, `ubnt,nanostation-loco-m-xw` y `ubnt,nanostation-m-xw`. Sus LEDs se declaran en el
device tree.

## 4. Consecuencia operativa, que es la que importa

El script RSSI **no puede apoyarse en `01_leds` para saber cuántos LEDs hay**:

1. en el **PowerBeam** puede esperar cuatro barras `blue:rssi0..3`;
2. en **LBE, LAP-120 y NS-Loco** debe **enumerar** `/sys/class/leds/` en runtime y adaptarse;
3. en ninguna board debe abortar si el recuento no coincide.

## 5. Cierre 30 de 30 — con una excepción que no se tapa

Diez etapas de Waves 32..36 recibieron recibo de enlace. **`1252A` sigue sin evidencia**:

- `tests/test_stage1248a_to_1253a_suite.py` **no existe** en el árbol;
- por tanto su recibo registra `suite: null` y `suite_result: "suite absent"`;
- permanece en `still_unresolved_after_wave43`.

Las otras nueve enlazan un doc o un wave gate real. Presentar «30/30» como treinta verificaciones
independientes seguiría siendo falso: son veinte verificaciones, nueve punteros y una ausencia.

## 6. Ledger 1100A..1259A

**101 recibos** para **99 etapas distintas** en ese rango. Los números de etapa **no son contiguos**, así
que no se declara un total esperado: contar lo que existe es el dato.

## 7. Huecos

- **`UNKNOWN`** — los LEDs de LBE, LAP-120 y NS-Loco; están en su device tree, que no se decodifica aún.
- **`UNKNOWN`** — el estado real de `/sys/class/leds/` en `.241`, porque la autenticación falló.
- **`UNKNOWN`** — por qué `1252A` no tiene suite ni evidencia.
- **Límite conocido** — un `ucidef_set_led_rssi` es un default declarativo, no prueba de LED poblado.
- **No intentado** — arrancar ninguna board, leer LEDs en vivo.
