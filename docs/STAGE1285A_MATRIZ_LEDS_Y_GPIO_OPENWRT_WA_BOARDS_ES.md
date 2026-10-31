<!-- doc-head: Stage 1285A - matriz LED y GPIO de las cuatro boards WA de OpenWrt 24.10.4, con las cuatro imagenes factory presentes pero sin DTS ni DTB en el repositorio y sin FDT recuperable del binario, por lo que el recuento de LEDs por board queda UNKNOWN y el script RSSI debe detectar en runtime -->
# Stage 1285A — Matriz de LEDs y GPIO en las cuatro boards WA

- **Recibo**: [`artifacts/verification/stage1284a_openwrt_wa_board_led_matrix.json`](../artifacts/verification/stage1284a_openwrt_wa_board_led_matrix.json)
- **Herramienta**: [`tools/re/openwrt_wa_board_led_and_gpio_matrix.py`](../tools/re/openwrt_wa_board_led_and_gpio_matrix.py)
- **Alcance**: offline estático. No se escribe ninguna imagen ni se contacta ningún radio.

## 0. Resultado en una línea

```
boards=4  images=4  boards_with_fdt=0  boards_with_rssi_bar=0
boards_single_led=0  boards_led_unknown=4  led_matrix_recoverable=0
```

La matriz **no es recuperable** de estos binarios. Los cuatro recuentos quedan **UNKNOWN**, no cero.

## 1. Las cuatro imágenes están, los DTS no

| Board | Modelo OpenWrt | `board_id` | Imagen 24.10.4 |
| :--- | :--- | :-: | :-: |
| **PBE-5AC-Gen2** | `ubnt_powerbeam-5ac-gen2` | `0xe3d6` | presente |
| **LBE-5AC-Gen2** | `ubnt_litebeam-ac-gen2` | `0xe7f9` | presente |
| **LAP-120** | `ubnt_lap-120` | `0xe7f7` | presente |
| **NS-5AC-Loco** | `ubnt_nanostation-ac-loco` | `0xe7f1` | presente |

**`CONFIRMED`**: las cuatro `*factory.bin` existen en `firmware/openwrt/` y se han hasheado.

**`REFUTED`**: en el repositorio **no hay DTS ni DTB de estas cuatro boards**. Los únicos tres ficheros de árbol de dispositivo que existen (`qca9558_ubnt_prismstation-5ac.dts`, `qca9558_ubnt_rocket-prism-5ac-gen2.dts`,
`qca9558_ubnt_xc_prism_gen2.dtsi`) pertenecen a la **línea XC**, no a estas WA.

## 2. El FDT tampoco está en la imagen

El factory de estas boards no es un contenedor con un FDT plano. Lo medido:

1. la imagen empieza por el magic **`OPEN`** (`4f 50 45 4e`), formato de actualización de Ubiquiti;
2. el sistema de ficheros **squashfs** aparece en el offset 2.621.828;
3. **no existe la firma `0xd00dfeed`** en ningún offset de la imagen;
4. al descomprimir los bloques **XZ** del squashfs se obtienen entre 15 y 16 MB por bloque y **tampoco aparece `0xd00dfeed`** en ninguno.

**`REFUTED`**: la matriz LED no se puede leer del binario por la vía del FDT.

## 3. Por qué esto es un resultado y no un fracaso

El objetivo operativo de la etapa era que **el script RSSI nunca falle en una board de un solo LED**. Un recuento estático equivocado consigue justo lo contrario: si afirmáramos «cuatro LEDs» sin evidencia, el script escribiría en `/sys/class/leds/` rutas que no existen y fallaría en tres de las cuatro boards.

Así que la conclusión correcta es la que **habilita** el objetivo:

> **Ninguna board debe asumir un recuento de LEDs. El script debe enumerar `/sys/class/leds/` en runtime y adaptarse.**

Eso funciona en las cuatro, con cuatro barras o con una, y no depende de un dato que este corpus no contiene.

## 4. Lo que sí queda establecido

| Afirmación | Estado |
| :--- | :-: |
| las 4 imágenes 24.10.4 existen y están hasheadas | **CONFIRMED** |
| existen DTS/DTSB para estas 4 boards | **REFUTED** |
| la imagen contiene un FDT plano | **REFUTED** (`0xd00dfeed` ausente) |
| el FDT aparece tras descomprimir el squashfs | **REFUTED** |
| PBE-5AC-Gen2 tiene 4 LEDs de barra | **UNKNOWN** |
| LBE-5AC-Gen2 tiene un solo LED de estado | **UNKNOWN** |
| LAP-120 tiene un solo LED de estado | **UNKNOWN** |
| NS-5AC-Loco tiene un solo LED de estado | **UNKNOWN** |
| hay un registro de desplazamiento 74HC595 en estas imágenes | **REFUTED** por tokens (0 apariciones) |
| la ausencia de token prueba que no hay shift register físico | **REFUTED** |

## 5. El `0` de `shift_register_tokens` y por qué no se promociona

`74hc595`, `shift_register` y `shift-register` dan **0 apariciones** en las cuatro imágenes. Eso **no** demuestra que la board no tenga un registro de desplazamiento: el nombre del componente no tiene por qué aparecer en un binario comprimido cuyo árbol de dispositivo no hemos podido leer. Queda como **REFUTED** solo en su forma débil: «no está nombrado en lo que se puede leer».

## 6. Consecuencia para la herramienta de campo

Regla que debe cumplir cualquier script de barras RSSI escrito contra este corpus:

1. **enumerar** `/sys/class/leds/` y quedarse con las entradas cuyo `device` corresponda a la radio;
2. **contar** lo enumerado; si son `>= 4`, usar barras; si es `1`, usar el único LED como indicador de estado;
3. **no** inferir el modelo desde el nombre del fichero de firmware;
4. **fallar suave**: si no hay LEDs, registrar y continuar, nunca abortar.

## 7. Huecos

- **`UNKNOWN`** — el recuento real de LEDs de las cuatro boards; requiere el DTS de OpenWrt o una lectura en el equipo.
- **`UNKNOWN`** — el mapeo GPIO de cada LED.
- **`UNKNOWN`** — si alguna de las cuatro usa un 74HC595.
- **Bloqueado** — sin DTS en el repositorio y sin FDT en la imagen, no hay ruta estática al dato.
- **Límite conocido** — un recuento de nodos en un árbol de dispositivo tampoco sería un recuento de LEDs poblados.
- **No intentado** — arrancar ninguna board, leer `/sys/class/leds/` en vivo.
