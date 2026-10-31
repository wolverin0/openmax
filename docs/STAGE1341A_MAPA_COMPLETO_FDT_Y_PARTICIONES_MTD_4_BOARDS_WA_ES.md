<!-- doc-head: Stage 1341A - mapa FDT completo de las cuatro placas WA (pcie, ath10k, wmac ath9k, eth, spi, flash, particiones, gpio-keys, gpio-leds) y comparacion medida de las particiones mtd de OpenWrt 24.10.4 contra el layout documentado de airOS 8 -->
# Stage 1341A — Mapa completo del árbol de dispositivo y particiones mtd de las 4 placas WA

- **Mapa**: [`stage1338a_wa_four_boards_complete_fdt_hardware_map.json`](../artifacts/verification/stage1338a_wa_four_boards_complete_fdt_hardware_map.json)
- **Comparación**: [`stage1339a_wa_fdt_mtd_partition_map_comparison.json`](../artifacts/verification/stage1339a_wa_fdt_mtd_partition_map_comparison.json)
- **Libro mayor**: [`stage1340a_waves44_to_49_receipt_ledger.json`](../artifacts/verification/stage1340a_waves44_to_49_receipt_ledger.json)
- **Alcance**: offline estático. No se escribe ninguna imagen ni se contacta ningún equipo.

## 1. El árbol, entero y tipado

El mapa guarda **cada nodo y cada propiedad** de las cuatro FDT recuperadas en 1314A, con su tipo
(`string`, `stringlist`, `cells`, `bytes`), su valor y sus bytes crudos. Nada se deduce de un nombre de
nodo: cada agrupación lista las rutas exactas que coincidieron.

| Placa | Nodos | Propiedades | Particiones | FDT acaba en `usize` |
| :--- | -: | -: | -: | :-: |
| LAP-120 | 54 | — | 5 | **sí** |
| LBE-5AC-Gen2 | 54 | — | 5 | **sí** |
| NS-5AC-Loco | 54 | — | 5 | **sí** |
| PBE-5AC-Gen2 | 59 | — | 5 | **sí** |
| **Total** | **221** | **1.100** | 20 | **4/4** |

PBE tiene cinco nodos más porque es la única con `/leds` y sus cuatro barras.

## 2. El hardware que el kernel enlaza

| Bloque | Ruta | `compatible` | Dato |
| :--- | :--- | :--- | :--- |
| PCIe | `/ahb/pcie@180c0000` | — | host PCIe |
| Wi-Fi 5 GHz | `/ahb/pcie@180c0000/wifi@0,0` | **`qcom,ath10k`** | QCA9882 sobre PCIe |
| Wi-Fi 2,4 GHz | `/ahb/wmac@18100000` | **`qca,ar9340-wmac`** | bloque AHB del AR9342 (ath9k-ahb) |
| Ethernet A | `/ahb/eth@19000000` | **`qca,ar9340-eth`, `syscon`** | `phy-mode=rgmii-id`, **`status=okay`** |
| Ethernet B | `/ahb/eth@1a000000` | **`qca,ar9340-eth`, `syscon`** | `phy-mode=gmii`, **`status=disabled`** |
| Flash SPI | `/ahb/spi@1f000000/flash@0` | **`jedec,spi-nor`** | `reg=<0>` (CS 0) |
| Botón | `/keys/reset` | — | GPIO **12**, activo bajo, en las 4 placas |
| LEDs | `/leds` | `gpio-leds` | **solo PBE**, 4 barras |

El switch interno del AR9342 está **deshabilitado** en el árbol: la placa usa el GMAC
(`eth@19000000`, RGMII hacia el AR8035), no el switch. Eso no es una opinión: es el `status` del nodo.

**Premisa refutada.** El encargo pedía los nodos `eth0` y `eth1`. El árbol **no define ningún alias
`ethernet0`/`ethernet1`**; los alias que existen son `led-boot`, `led-failsafe`, `led-upgrade` (los tres
apuntan a `/leds/rssi3`) y `serial0`. Por eso el mapa registra `eth_alias_present = false` y los dos
controladores por su ruta y su `compatible`, en vez de inventar un nombre que el árbol no usa.

## 3. La tabla de particiones, idéntica en las cuatro

| `label` | Offset | Tamaño | Fin | `read-only` |
| :--- | -: | -: | -: | :-: |
| `u-boot` | `0x00000000` | `0x00040000` | `0x00040000` | **sí** |
| `u-boot-env` | `0x00040000` | `0x00010000` | `0x00050000` | **sí** |
| **`firmware`** | **`0x00050000`** | **`0x00f60000`** | **`0x00fb0000`** | no |
| `cfg` | `0x00fb0000` | `0x00040000` | `0x00ff0000` | **sí** |
| `art` | `0x00ff0000` | `0x00010000` | **`0x01000000`** | **sí** |

Una sola firma para las cuatro placas (`partition_signatures = 1`), y cierra exactamente en los
**16 MiB** (`0x01000000`) sin huecos ni solapes.

`art` lleva el `nvmem-layout` medido, que coincide con lo que ya decía `AGENTS.md §2`:

| Celda | Offset | Tamaño | Uso |
| :--- | -: | -: | :--- |
| `macaddr@0` | `0x0000` | **6 B** | MAC base |
| `calibration@1000` | `0x1000` | **1.088 B** | calibración 2,4 GHz |
| `calibration@5000` | `0x5000` | **2.116 B** | calibración 5 GHz (QCA9882) |

## 4. OpenWrt 24.10.4 contra airOS 8

La comparación usa el layout de airOS 8 **ya documentado en este repositorio**, citado con fichero y
línea, no re-medido aquí. Hay **dos variantes registradas**, y se reproducen las dos:

| Fuente | Variante |
| :--- | :--- |
| `docs/EXPERIMENTS_CONTINUATION_22e5692cde_006.md:115` | 6 particiones: `u-boot`, `u-boot-env`, **`kernel` 1M**, **`rootfs` 14.4M**, `cfg`, `EEPROM` |
| `docs/HARDWARE_MATRIX_CONTINUATION_d411365af3_001.md:131` | 5 particiones: `u-boot`, `u-boot-env`, **`firmware` 15.744 KiB**, `cfg`, `EEPROM` |
| `CURRENT_STATE.md:4153` (archivo) | el kernel airOS en `0x9f050000` y el rootfs en `0x9f150000`; escribe ambos en `/dev/mtd3` |

Resultado de la comparación contra la variante de 5 particiones:

| airOS `mtd` | Nombre airOS | OpenWrt `label` | Offset idéntico | Tamaño idéntico |
| :---: | :--- | :--- | :-: | :-: |
| `mtd0` | `u-boot` | `u-boot` | **sí** | **sí** |
| `mtd1` | `u-boot-env` | `u-boot-env` | **sí** | **sí** |
| `mtd2` | `firmware` | `firmware` | **sí** | **sí** |
| `mtd4` | `cfg` | `cfg` | **sí** | **sí** |
| `mtd5` | `EEPROM` | `art` | **sí** | **sí** |

**5 de 5 offsets y 5 de 5 tamaños idénticos.** En la variante de 6 particiones, `kernel` y `rootfs`
quedan **absorbidos** por la única `firmware` de OpenWrt, que empieza en la misma dirección.

Las direcciones airOS son de runtime en `KSEG1`; restando `0x9f000000` salen los offsets de flash
**`0x50000`** para el kernel y **`0x150000`** para el rootfs. Eso fija el hueco de kernel de airOS en
**1 MiB**, mientras que el blob de kernel de OpenWrt ocupa **2,5 MiB** (la squashfs validada empieza en
`0x280184` del `factory.bin` en las cuatro imágenes).

Consecuencia práctica: los dos firmware coinciden en la frontera de `firmware` y **no coinciden dentro
de ella**. El intercambio airOS ↔ OpenWrt funciona porque ambos reemplazan la región completa, no
porque las sub-particiones estén alineadas. Un rollback debe escribir la región entera, nunca una
sub-parte.

## 5. Libro mayor 1302A..1337A

**36 números de etapa.** En el corte de esta ejecución el libro mayor registra **21 recibos** y **17
etapas sin JSON propio**; de esas, 6 tienen documento o test bajo su propio nombre, 4 tienen el
entregable bajo otro nombre y 7 no tienen nada. Los recibos se clasifican por contenido, y la cadena de
hashes permite detectar deriva.

El directorio es compartido: **otro lane escribió dos recibos durante esta wave** (`1321A`, `1322A`), y
por eso el recibo es la fuente de las cifras, no este párrafo. Las pruebas de la wave verifican los
invariantes (`stages_with_receipt + stages_absent = 36`, las tres clases de ausencia suman el total) y no
un conteo congelado.

## 6. Huecos

- **CONFIRMED** — el árbol y la tabla de particiones están medidos en las cuatro imágenes.
- **CONFIRMED_DOCUMENTED** — el layout airOS 8 es una cita del repositorio, no una medida de esta etapa.
- **UNKNOWN** — qué variante airOS 8 corre cada unidad del parque; las fuentes discrepan en numeración.
- **INFERRED** — las direcciones de flash de airOS derivadas de `KSEG1`.
- **No intentado** — arrancar una placa y leer `/proc/mtd` en cualquiera de los dos firmware.
