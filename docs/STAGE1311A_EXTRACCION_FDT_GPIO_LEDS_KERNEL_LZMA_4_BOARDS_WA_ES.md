<!-- doc-head: Stage 1311A - intento de extraccion FDT gpio-leds desde el kernel LZMA de las cuatro imagenes WA 24.10.4, con la cabecera uImage y los props LZMA parseados correctamente pero la decodificacion abortando al 36 por ciento antes de la region del arbol, de modo que los LEDs de tres placas siguen UNKNOWN y solo el PowerBeam queda confirmado por board.d -->
# Stage 1311A — FDT gpio-leds desde el kernel LZMA de las 4 imágenes WA

- **Recibo**: [`artifacts/verification/stage1308a_wa_kernel_fdt_gpio_leds_extraction.json`](../artifacts/verification/stage1308a_wa_kernel_fdt_gpio_leds_extraction.json)
- **Herramienta**: [`tools/re/wa_kernel_fdt_gpio_leds_extractor.py`](../tools/re/wa_kernel_fdt_gpio_leds_extractor.py)
- **Alcance**: offline estático. No se escribe ninguna imagen ni se contacta ningún equipo.

## 1. Lo que sí se consiguió: la cadena de arranque de la imagen

| Capa | Resultado |
| :--- | :-: |
| contenedor Ubiquiti `OPEN` | **CONFIRMED** |
| cabecera `uImage` en offset **0x144** | **CONFIRMED** |
| nombre del kernel | `MIPS OpenWrt Linux-6.6.110` |
| compresión | **3 = LZMA** |
| `ih_size` | **2.618.128** bytes |
| props LZMA del stream | `0x6d` → `lc=1, lp=2, pb=2` |
| tamaño declarado sin comprimir | **8.724.191** bytes |

**`CONFIRMED`**: el kernel es un `uImage` LZMA dentro del contenedor `OPEN`, con esos parámetros
exactos. Eso corrige dos suposiciones anteriores: no es un FDT plano (Wave 41) y no es un bloque XZ de
squashfs (Wave 42).

## 2. Lo que falló, con el número exacto

`lzma.decompress` **rechaza** el stream en todas las variantes probadas (`FORMAT_ALONE`, `FORMAT_XZ`,
`FORMAT_AUTO`). Con decodificación **raw** y los filtros derivados de los props sí produce datos, pero
**aborta a los 3.103.862 bytes de los 8.724.191 declarados**: el **36 %**.

```
esperado   8.724.191
obtenido   3.103.862     (35,6 %)
```

**`REFUTED`**: el `0xd00dfeed` **no aparece** en el prefijo recuperado. La región del árbol de
dispositivo está más allá del punto donde la decodificación se corta.

Consecuencia: los nodos `gpio-leds` de **LBE-5AC-Gen2, LAP-120 y NS-5AC-Loco** siguen **UNKNOWN**.

## 3. La matriz, con lo confirmado y lo que no

| Board | Fuente | LEDs | Estado |
| :--- | :--- | :-: | :--- |
| **PBE-5AC-Gen2** | `board.d/01_leds` (Wave 43) | **4** (`blue:rssi0..3`) | **CONFIRMED** |
| LBE-5AC-Gen2 | FDT del kernel | — | **UNKNOWN** |
| LAP-120 | FDT del kernel | — | **UNKNOWN** |
| NS-5AC-Loco | FDT del kernel | — | **UNKNOWN** |

`gpio_leds_recoverable = 0` en este recibo. La matriz de 1284A conserva el PowerBeam confirmado y las
otras tres sin dato, que es la verdad.

## 4. Por qué el corte a 36 % importa

Un corte no es un fallo cosmético: significa que entre el byte 3,1 MB y el 8,7 MB del kernel hay
contenido que no se puede leer. Cualquier afirmación sobre lo que hay ahí — incluidos los nodos LED —
sería inventada. Por eso el recibo marca `decompress_ok = 1` sólo si se superan 100 KB **y** el error de
cola queda registrado con su offset.

## 5. Camino de cierre, en orden de coste

1. **`unsquashfs`/`dtc` instalados**: leer el DTB desde el paquete del kernel, segundos.
2. **Decodificar sin tolerar cola corrupta** y aceptar sólo si `eof` es verdadero: distingue stream sano
   de stream truncado.
3. **Leer el DTB del equipo en vivo**: requiere que la autenticación SSH funcione, que en la Wave 43 fue
   **rechazada** en `.241`.

Ninguna de las tres es análisis adicional: dos son herramientas y una es acceso.

## 6. Consecuencia operativa (sin cambios)

El script de barras RSSI debe seguir **enumerando** `/sys/class/leds/` en runtime:

- en el **PowerBeam** puede esperar cuatro barras `blue:rssi0..3`;
- en **LBE, LAP-120 y NS-5AC-Loco** no hay dato estático y no debe asumirse ninguno;
- en ninguna debe abortar si el recuento no coincide.

## 7. Huecos

- **`UNKNOWN`** — los `gpio-leds` de las tres placas sin `board.d`; el FDT está tras el corte.
- **`UNKNOWN`** — si el stream LZMA está truncado en origen o mi lectura lo trunca.
- **`UNKNOWN`** — el estado real de `/sys/class/leds/` en `.241` (autenticación rechazada).
- **Límite conocido** — un nodo del árbol declara lo que el kernel expone, no lo que la placa pobló.
- **No intentado** — arrancar ninguna placa, medir triggers en vivo.
