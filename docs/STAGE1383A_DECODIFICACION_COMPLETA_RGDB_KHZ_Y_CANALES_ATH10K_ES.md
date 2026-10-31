<!-- doc-head: Stage 1383A - lector SquashFS multi-bloque corregido (la cabecera de 4 bytes no existe), 12/12 modulos exactos, firmware-2.bin presente y firmware-5.bin ausente, tabla de canales estatica refutada y regdb RGDB v20 decodificado en kHz con 216 rangos hasta 7125 MHz -->
# Stage 1383A - Decodificacion completa: RGDB en kHz y canales ath10k

- **Lector**: [`stage1380a_squashfs_multiblock_fix_and_ath10k_extraction.json`](../artifacts/verification/stage1380a_squashfs_multiblock_fix_and_ath10k_extraction.json)
- **Decodificacion**: [`stage1381a_ath10k_exact_channels_and_rgdb_khz_rules.json`](../artifacts/verification/stage1381a_ath10k_exact_channels_and_rgdb_khz_rules.json)
- **Auditoria**: [`stage1382a_waves52_to_56_receipt_ledger.json`](../artifacts/verification/stage1382a_waves52_to_56_receipt_ledger.json)
- **Alcance**: offline estatico. No se contacta ningun equipo ni se escribe ninguna imagen.

## 1. El fallo del lector y su causa exacta

`Squash.read_file` consumia una cabecera de cuatro bytes por bloque de datos. En estas imagenes **esa
cabecera no existe**: el tamano vive solo en la lista de bloques del inodo y los bloques son contiguos
desde `blocks_start`, que es un offset **relativo al superbloque** en `0x280184`.

La prueba esta en el primer bloque de `ath10k_core.ko`:

| Medida | Valor |
| :--- | :--- |
| posicion absoluta | `0x280184 + 984040` = **`0x37056c`** |
| primeros seis bytes | **`fd 37 7a 58 5a 00`** (magia XZ) |
| lo que el codigo viejo leia como cabecera | `0x5a590100` |
| longitud que de ahi deducia | **5.832.960 B** para un fichero de 600.808 |

El ancla del superbloque **siempre estuvo bien**. El error era leer cuatro bytes que son parte del
flujo XZ y desplazar cada bloque siguiente. Con la geometria correcta los tres bloques dan
262.144 + 262.144 + 76.520 = **600.808**, exacto.

Por que sobrevivio veinte waves: todo fichero menor que un bloque (262.144 B) usa la ruta de
fragmento, que ya documentaba que no hay cabecera. La ruta de bloques nunca se habia ejercitado.

## 2. Extraccion directa desde las cuatro imagenes

| Medida | Resultado |
| :--- | -: |
| modulos extraidos | **12 de 12** (`ath10k_core.ko`, `cfg80211.ko`, `mac80211.ko` por 4 placas) |
| modulos cuyo tamano descomprimido iguala `file_size` | **12 de 12** |
| `ath10k_core.ko` | 600.808 B, 3 bloques, identico en las 4 |
| prueba de geometria (XZ en el primer bloque) | **4 de 4** |
| prueba de que la longitud vieja excedia el fichero | **4 de 4** |

## 3. El firmware que si viaja

| Fichero | Placas | Bytes | Identidad |
| :--- | :-: | -: | :--- |
| `board.bin` | **4/4** | 2.116 | identico en las 4 |
| `firmware-2.bin` | **4/4** | **204.796** | magia `QCA-ATH10K`, version `10.1-ct-8x-__fW-022-ecad3248` |
| `firmware-5.bin` | **0/4** | - | **ausente** |

El firmware es el **CT (Candela) `firmware-2.bin`**, no el `firmware-5.bin` de mainline. El listado
revela ademas que el directorio `hw2.0` contiene una entrada `hw2.0` que se resuelve a si misma; el
recorrido esta limitado en profundidad y los contadores del recibo se cuentan **por placa**, no por
entrada, para no inflar cifras.

## 4. La tabla de canales: refutada dentro del modulo

Se probaron seis plantillas de estructura (`chan_freq`, `freq_chan`, `chan_freq_hw`, `freq_hw_chan`,
`chan_freq_hw_width`, `freq_chan_hw_width`) con paso de 4 a 16 bytes.

| Medida | Valor |
| :--- | -: |
| plantillas que producen una racha valida de 12 entradas | **0** |
| racha mas larga con cualquier plantilla | **1** (solo 5180) |
| apariciones del literal 5180 en el modulo | **28** |
| vecindades registradas para auditoria | 12 |

**`ath10k_5ghz_channels` no existe como tabla estatica de frecuencias en este `ath10k_core.ko`.** El
driver CT obtiene los canales del firmware, y el firmware presente es `firmware-2.bin`. Cualquier
tabla de canales publicada desde este modulo habria sido inventada.

## 5. La base regulatoria: ahora si decodificada

La clave era la unidad: **todo esta en kHz, incluido el ancho de banda**. La estructura de rango es de
16 bytes big-endian:

    5170000   5250000   20000   0x100006a4
    start_khz end_khz   bw_khz  flags

| Medida | Valor |
| :--- | -: |
| magia / version | **`RGDB`** / **20** |
| tabla de paises | 291 slots de 4 B tras 8 B de cabecera |
| slots con codigo valido | **175** |
| cierra en el primer offset de reglas | **si** (8 + 291x4 = 1172 = `0x494`) |
| rangos de frecuencia distintos | **216** |
| extremo superior mas alto | **7125 MHz** |

Los cuatro ejemplos documentados aparecen **exactamente**:

| Inicio (kHz) | Fin (kHz) | MHz |
| -: | -: | :--- |
| 5170000 | 5250000 | 5170-5250 |
| 5250000 | 5330000 | 5250-5330 |
| 5490000 | 5730000 | 5490-5730 |
| 5735000 | 5835000 | 5735-5835 |

Que los cuatro esten presentes y con esos limites es la confirmacion de que la unidad y el formato son
los correctos, no una coincidencia de escaneo.

## 6. La atribucion por pais queda refutada

Se intento asignar cada rango al pais cuya region de offsets lo contiene. El resultado se refuta a si
mismo: **AR, US y 00 quedan sin bandas** y 6035 MHz recae en un unico pais implausible.

**Conclusion etiquetada:** la lista de bandas por pais es **`UNKNOWN`**. Se publica el inventario
global de rangos, que esta medido, y **no** se publica una tabla por pais que no se pudo decodificar.

## 7. Que significa para 6035 MHz

1. **Existe al menos un rango que cubre 6035 MHz** en el fichero (cobertura global = si). El techo de
   7125 MHz lo confirma: hay reglas de 6 GHz.
2. **A que pais pertenece ese rango: `UNKNOWN`.** La atribucion por region fue refutada.
3. **Del lado del driver no hay cambio**: cero literales `6035` en `ath10k_core.ko` y techo de canal
   compilado de **5925 MHz** (Wave 55).
4. Por tanto **6035 no se habilita con un cambio de base regulatoria**: aunque una regla lo cubra, el
   driver no tiene el canal.

## 8. Auditoria 1350A..1379A

**30 numeros de etapa, 18 recibos, 13 sin recibo** (4 con documento o test propio, 9 sin nada).
**0 recibos declaran dispositivos vivos**, 7 con marcadores de runtime, 9 sin clase de evidencia y
**1 desajuste** entre la etapa declarada y el nombre del fichero.

## 9. Huecos

- **CONFIRMED** - causa del fallo y su correccion; 12/12 modulos exactos; presencia de
  `firmware-2.bin` y ausencia de `firmware-5.bin`; unidad kHz y formato de 16 B del regdb; 216 rangos
  y techo de 7125 MHz.
- **REFUTED** - tabla de canales estatica en `ath10k_core.ko`; atribucion de rangos por region.
- **UNKNOWN** - bandas por pais en el regdb; lista de canales del firmware CT.
- **No intentado** - arrancar una placa y leer `iw phy`, `iw reg get` o el log del ath10k.
