<!-- doc-head: Stage 1317A - causa exacta del corte LZMA en 3.103.862 bytes (registro PART de 64 B en el primer MiB), recuperacion completa de los 4 kernels y sus FDT, matriz LED real de las 4 placas WA y cierre verificado de 1252A -->
# Stage 1317A — El corte de 3,1 MB era un registro de 64 bytes, y el DTB estaba detrás

- **Recibo**: [`stage1314a_decompressed_kernel_3mb_dtb_and_led_strings.json`](../artifacts/verification/stage1314a_decompressed_kernel_3mb_dtb_and_led_strings.json)
- **Herramienta**: [`wa_kernel_part_record_and_fdt_extractor.py`](../tools/re/wa_kernel_part_record_and_fdt_extractor.py)
- **Libro mayor**: [`stage1316a_waves37_to_45_verified_ledger.json`](../artifacts/verification/stage1316a_waves37_to_45_verified_ledger.json)
- **Alcance**: offline estático. No se escribe ninguna imagen ni se contacta ningún equipo.

## 1. El corte, reproducido y explicado

Las Waves 44 y 45 midieron bien y concluyeron mal. El stream no está corrupto ni truncado: el
contenedor `OPEN` de Ubiquiti **inserta un registro de 64 bytes** en los últimos 64 bytes del primer
MiB de la parte `kernel`, y un codificador LZMA no se puede reanudar atravesando esos bytes.

| Medida | Valor | Estado |
| :--- | :--- | :--- |
| offset de entrada donde falla | **1.048.576** (`0x100000`) | **CONFIRMED** |
| salida producida antes del fallo | **3.103.862** | **CONFIRMED** |
| ¿idéntico en las 4 imágenes? | sí, mismo offset de entrada | **CONFIRMED** |
| registro insertado | 64 B en fichero `0x100144`, payload `0xFFFC0` | **CONFIRMED** |
| contenido del registro | `PART` + `rootfs` | **CONFIRMED** |
| ¿termina justo en el MiB? | sí, `0xFFFC0 + 64 = 0x100000` | **CONFIRMED** |

Las cuatro imágenes fallan en el mismo byte porque ese byte es estructura, no datos. La prueba de que
no había corrupción: **decodificar solo `payload[13:0xFFFC0]` da 3.103.862 bytes con `err=None`**.

## 2. La cola del stream estaba fuera del `uImage`

Quitar el registro no bastaba: el kernel quedaba corto y el FDT salía **truncado 201 bytes**, justo la
cola del *strings block*, que es donde viven los nombres de propiedad. Por eso el nodo existía pero
`gpio-leds` no se resolvía.

La cola está en el **hueco entre el payload y `hsqs`**: 3.312 / 3.310 / 3.304 / 3.228 bytes según la
placa. Regla final, medida:

```
stream = payload[13:0xFFFC0] + payload[0x100000:] + hueco_pre_squashfs
kernel = stream_decodificado[:usize]
```

## 3. Resultado: cuatro kernels exactos y cuatro FDT

| Placa | `usize` declarado | recuperado | FDT en | tamaño FDT | ¿FDT acaba en `usize`? |
| :--- | -: | -: | -: | -: | :-: |
| LAP-120 | 8.722.143 | **8.722.143** | 8.714.304 | 7.839 | **sí** |
| LBE-5AC-Gen2 | 8.722.147 | **8.722.147** | 8.714.304 | 7.843 | **sí** |
| NS-5AC-Loco | 8.722.155 | **8.722.155** | 8.714.304 | 7.851 | **sí** |
| PBE-5AC-Gen2 | 8.722.549 | **8.722.549** | 8.714.304 | 8.245 | **sí** |

Que el FDT termine **exactamente** en el último byte declarado no es casualidad: es la prueba de que la
reconstrucción es byte a byte correcta y de que no sobra ni falta nada.

El modelo del árbol coincide con la placa de cada imagen, así que no hay cruce de DTBs:

- `Ubiquiti LiteAP ac (LAP-120)`
- `Ubiquiti LiteBeam AC Gen2`
- `Ubiquiti Nanostation AC loco (WA)`
- `Ubiquiti PowerBeam 5AC Gen2`

## 4. La matriz LED, ahora sí completa

| Placa | Nodos | Contenedor `gpio-leds` | LEDs | Estado |
| :--- | -: | :--- | -: | :--- |
| **PBE-5AC-Gen2** | 59 | `/leds` | **4** | **CONFIRMED** |
| LAP-120 | 54 | **ninguno** | **0** | **CONFIRMED** (ausencia) |
| LBE-5AC-Gen2 | 54 | **ninguno** | **0** | **CONFIRMED** (ausencia) |
| NS-5AC-Loco | 54 | **ninguno** | **0** | **CONFIRMED** (ausencia) |

El PowerBeam declara cuatro barras RSSI y coinciden con lo que ya decía `board.d` en la Wave 43:

| Nodo | `label` | GPIO | flag |
| :--- | :--- | -: | :-: |
| `/leds/rssi0` | `blue:rssi0` | 11 | 1 (activo bajo) |
| `/leds/rssi1` | `blue:rssi1` | 16 | 1 (activo bajo) |
| `/leds/rssi2` | `blue:rssi2` | 13 | 1 (activo bajo) |
| `/leds/rssi3` | `blue:rssi3` | 14 | 1 (activo bajo) |

Las otras tres placas **no declaran ningún LED en el árbol de dispositivo**. No es un fallo del parser:
el recorrido del árbol devuelve 54 nodos, el modelo es correcto, el FDT cierra en `usize`, y lo único
que llevan es `/keys/reset` (GPIO 12, activo bajo). La cadena `gpio-leds` sí aparece en el binario, pero
como tabla del driver `leds-gpio`, no como nodo.

Consecuencia: en LAP-120, LBE-5AC-Gen2 y NS-5AC-Loco, `/sys/class/leds/` **no puede** contener barras
RSSI creadas desde el DTB. Cualquier script que las espere debe enumerar y no asumir.

## 5. Cierre de 1252A

La Wave 45 dejó 1252A abierta porque el módulo que decía envolver no existe. La Wave 46 verificó los
artefactos que sí existen:

| Artefacto | Comprobación | Estado |
| :--- | :--- | :-: |
| `stage1248a_inplace_topology_and_sg01_upgrade.json` | declara `stage=1248A`, sin dispositivos tocados | **OK** |
| `stage1249a_waves32_36_backfill_receipt.json` | se declara índice de relleno y lista sus huecos | **OK** |
| `stage1250a_inplace_pwo_and_4probes_upgrade.json` | declara `stage=1250A` | **OK** |
| `stage1253a_wave35_opus55_inplace_gate.json` | `failures=[]` y estado explícito | **OK** |
| `docs/STAGE1251A_...ES.md` | 82 líneas, 1 `doc-head` | **OK** |
| `tests/test_stage1248a_to_1253a_suite.py` | **9 passed**, exit 0 | **OK** |

Dos premisas del encargo resultaron falsas y quedan escritas como tales:

1. `tests/test_stage1248a_opus55_inplace_replacement.py` **no existe**.
2. `tests/test_stage1242a_to_1247a_suite.py` **tampoco existe**.

Y una desviación medida, no aceptada en silencio: el documento 1251A lleva **un signo de exclamación**,
que rompe la norma de prosa del proyecto. El recibo lo registra con su cuenta exacta.

## 6. Consecuencia operativa

- El script de barras RSSI puede tratar `blue:rssi0..3` como **contrato** solo en el PowerBeam.
- En las otras tres placas debe enumerar `/sys/class/leds/` y operar con lo que encuentre, incluido nada.
- El desbloqueo del DTB ya no depende de SSH ni de `unsquashfs`: está resuelto offline en el fichero.

## 7. Huecos

- **CONFIRMED** — el registro de 64 B y el hueco pre-squashfs son la causa; ambos medidos.
- **UNKNOWN** — si el registro aparece también en imágenes de otras familias Ubiquiti; aquí son 4 de 4.
- **UNKNOWN** — el estado real de `/sys/class/leds/` en las placas; no se arrancó ninguna.
- **Límite conocido** — un nodo del árbol declara lo que el kernel expone, no lo que la placa pobló.
- **No intentado** — medir triggers en vivo o validar los GPIO contra el esquemático.
