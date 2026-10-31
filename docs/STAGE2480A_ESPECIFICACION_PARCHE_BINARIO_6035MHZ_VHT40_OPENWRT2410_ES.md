<!-- doc-head -->
# STAGE 2480A — Especificación del parche binario de 6035 MHz VHT40 en OpenWrt 24.10.4

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo medido sobre los binarios extraídos en `artifacts/firmware_re_ath10k_tar/`.
- Este documento no contiene apellidos.

## 1. Stage 2478A — la tabla en el build de OpenWrt

`ath10k_core_openwrt2410.ko` (**714.672** B). Registro de **64 bytes**, big endian: banda `+0`, frecuencia `+4`, `hw_value` `+10`, flags `+12`.

- `CONFIRMED`: la tabla `ath10k_5ghz_channels` empieza en **`0x061A88`** (banda 1, 5180, hw 36).
- `CONFIRMED`: **27** entradas, de 5180 (hw 36) a **5865** (hw 173) en `0x062108`.
- `CONFIRMED`: la tabla de 2 GHz empieza en **`0x062148`** con 2412 (hw 1).
- `CONFIRMED`: **6035 no está** antes del parche.

La base se localizó por **firma de registro**, no por un offset fijo: el build de OpenWrt es distinto del de referencia y la tabla se movió de `0x0564BC` a `0x061A88`.

## 2. Qué exige VHT40

Un canal de 40 MHz necesita el primario de 20 y un secundario de 20 **contiguo**, arriba o abajo. Con `hw_value = (freq - 5000) / 5`:

| Frecuencia | `hw_value` |
| ---: | ---: |
| 6015 | **203** |
| 6035 | **207** |
| 6055 | **211** |

Como la tabla no tiene hueco para crecer sin romper las relocaciones, se **reemplazan las dos últimas entradas**.

## 3. Las dos variantes

### 3.1 Secundario por debajo (`6015` + `6035`)

| Entrada | Offset | Campo | Antes | Después |
| ---: | :--- | :--- | ---: | ---: |
| 25 | `0x0620C8` | frecuencia (`+4`) | 5845 | **6015** |
| 25 | `0x0620CE` | `hw_value` (`+10`) | 169 | **203** |
| 26 | `0x062108` | frecuencia (`+4`) | 5865 | **6035** |
| 26 | `0x06210E` | `hw_value` (`+10`) | 173 | **207** |

### 3.2 Secundario por encima (`6035` + `6055`)

| Entrada | Offset | Campo | Antes | Después |
| ---: | :--- | :--- | ---: | ---: |
| 25 | `0x0620C8` | frecuencia (`+4`) | 5845 | **6035** |
| 25 | `0x0620CE` | `hw_value` (`+10`) | 169 | **207** |
| 26 | `0x062108` | frecuencia (`+4`) | 5865 | **6055** |
| 26 | `0x06210E` | `hw_value` (`+10`) | 173 | **211** |

- `CONFIRMED`: cada variante toca **6 bytes**: cuatro de frecuencia y dos de `hw_value`.
- `CONFIRMED`: en las dos, 6035 queda **presente** y su secundario también, que es lo que `cfg80211_chandef_valid` exige.

## 4. Stage 2479A — reconciliación

Cada variante se aplicó **en memoria** y se comparó byte a byte contra el original.

| Variante | Bytes cambiados | Dentro de los campos | Tabla 27 | 6035 | Secundario | 2 GHz intacta |
| :--- | ---: | :---: | :---: | :---: | :---: | :---: |
| `secondary_below` | **6** | sí | sí | sí | sí | sí |
| `secondary_above` | **6** | sí | sí | sí | sí | sí |

- `CONFIRMED`: **6 bytes** por variante y **ninguno fuera** de los campos declarados.
- `CONFIRMED`: el tamaño del `.ko` no cambia (**714.672** B) y la tabla de 2 GHz sigue en `0x062148`.
- `CONFIRMED`: `sha256` del resultado registrado en el recibo para cada variante.
- `CONFIRMED`: **reconciliado = 1**.

## 5. El dominio regulatorio ya cubre 6035

`regulatory.db` (**6.232** B) tiene magia **`RGDB`** y guarda las frecuencias en **kHz big endian**.

| Valor | kHz | Apariciones BE |
| :--- | ---: | ---: |
| 5730 MHz | 5730000 | 19 |
| 5850 MHz | 5850000 | 23 |
| 5925 MHz | 5925000 | 21 |
| 7125 MHz | 7125000 | 7 |

- `CONFIRMED`: 6035 MHz = **6035000** kHz está **dentro** de un rango que la base ya declara.
- `CONFIRMED`: por tanto **no hace falta tocar `regulatory.db`** para habilitar 6035; el rango ya lo cubre.

### 5.1 Corrección: el módulo PHY no tiene los límites

- **`REFUTED`**: la expectativa de que `ath_openwrt2410.ko` (**28.000** B) contuviera los límites de banda de 5 GHz. Se buscaron 5850, 5925, 6035, 6100 y 7125 en cuatro codificaciones y **todas dan cero**.
- `CONFIRMED`: los límites no están como literales en ese módulo.

## 6. Estado del parche

- `CONFIRMED`: basta **un** cambio de 6 bytes en `ath10k_core_openwrt2410.ko` para que 6035 exista como canal.
- `CONFIRMED`: el firmware ya acepta 4910..6100 (wave 237), así que **no** hay que sustituir el blob.
- `CONFIRMED`: `regulatory.db` ya cubre la frecuencia, así que **no** hay que regenerarla.
- `INFERRED`: falta que hostapd acepte el canal; no se mide aquí.

## 7. Lo que queda abierto
- `UNKNOWN`: cuál de las dos variantes conviene. Depende de si el despliegue usa secundario arriba o abajo.
- `UNKNOWN`: el filtrado de hostapd.
- `UNKNOWN`: el índice de reglas de `regulatory.db` (sólo se midió la codificación de frecuencias).
- `UNKNOWN`: si el `hw_value` 203/207/211 requiere una entrada de calibración en `board.bin`.

## 8. Stage 2481A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax` y se añadieron las filas con **CRLF**.

## 9. Artefactos
`run_stage2478a_openwrt2410_6035mhz_vht40_binary_patch_spec.py`, `run_stage2479a_openwrt2410_6035mhz_patch_reconciliation.py`, `record_stage2481a_memorymaster_ingest.py`, `test_stage2478a_to_2483a_suite.py` y `verify_stage2483a_wave240_opencode_gate.py`.
