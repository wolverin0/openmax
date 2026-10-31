<!-- doc-head -->
# STAGE 2462A — Por qué OpenWrt no tiene 6035 MHz y qué parche hace falta

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Medido sobre `artifacts/`. Este documento no contiene apellidos.

## 1. Stage 2460A — la tabla del módulo

`ath10k_core.ko` (600.808 B). Registro de **64 bytes**, big endian: `+0` banda, `+4` frecuencia, `+10` `hw_value`, `+12` `flags`.

| # | Offset | Frecuencia | hw_value |
| ---: | :--- | ---: | ---: |
| 0 | `0x0564BC` | 5180 | 36 |
| 20 | `0x0569BC` | 5745 | 149 |
| 24 | `0x056ABC` | 5825 | 165 |
| 25 | `0x056AFC` | 5845 | 169 |
| **26** | `0x056B3C` | **5865** | **173** |

- `CONFIRMED`: **27** entradas, todas `band=1`, `flags=0`, de 5180 a **5865 MHz**.
- `CONFIRMED`: la tabla de 2 GHz sigue en `0x056B7C`, **14** entradas de 2412 a 2484.
- `CONFIRMED`: **6035 no está** en la tabla (`has_target = 0`).
- `REFUTED`: mi informe anterior, que decía que no había tabla. Existía; yo buscaba enteros contiguos donde hay estructuras de 64 bytes. **Décima corrección de método.**
- `CONFIRMED`: en `umac.ko` de airOS 6035 aparece como valor, pero **la estructura de 64 bytes no está localizada** en ese binario, así que no le aplico los offsets de ath10k.

## 2. Stage 2461A — el firmware no es el límite

`patched_firmware2_canary.bin` (208.179 B, cabecera `QCA-ATH10K`). Literales little endian:

| Offset | Valor | Papel |
| :--- | ---: | :--- |
| `0x02CDC` | 2312 | mínimo 2 GHz |
| `0x02CE0` | 2732 | máximo 2 GHz |
| **`0x02CE4`** | **4910** | **mínimo 5 GHz** |
| **`0x02CE8`** | **6100** | **máximo 5 GHz** |
| `0x02CF8` | 2300 | — |
| `0x02CFC` | 4800 | — |
| `0x02D10` | −4800 | — |

- `CONFIRMED`: el firmware acepta **4910..6100 MHz**. 6035 ≤ 6100, así que **el firmware no limita**.
- `CONFIRMED`: el bloqueo está en **la tabla del módulo**, que termina en 5865.

### 2.1 El parche

| Ruta | Efecto |
| :--- | :--- |
| **Extender a 28** | cambia el tamaño de `.data`, desplaza la tabla de 2 GHz de `0x056B7C` y **rompe las relocaciones** |
| **Sustituir una entrada** | tamaño y relocaciones **intactos** |

- `CONFIRMED`: extender exige reparar el `.ko` entero.
- `INFERRED`: sustituir una entrada DFS o meteorológica en desuso es la ruta viable, con `hw_value` **207** para 6035.
- **`UNKNOWN`**: cuál entrada es seguro sacrificar. Requiere saber qué comandos usa el despliegue.

### 2.2 Consecuencia

- `CONFIRMED`: **no hace falta sustituir el blob del firmware**. Basta parchear la tabla del módulo.
- `INFERRED`: además hará falta que el dominio regulatorio permita la frecuencia, pero `regulatory.db` **no está en el repositorio** y por eso no se mide aquí.

## 3. Lo que queda abierto
- `UNKNOWN`: qué entrada sustituir.
- `UNKNOWN`: las reglas de `regulatory.db`.
- `UNKNOWN`: si hostapd filtra 6035 por su cuenta.
- `UNKNOWN`: la estructura de canales dentro de `umac.ko`.

## 4. Stage 2463A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax` y se añadieron las filas con **CRLF**.

## 5. Artefactos
`build_stage2460a_openwrt_ath10k_5ghz_channels_vs_airos_superchannel_re.py`, `build_stage2461a_qca988x_firmware2_vs_airos_target_fw_6035mhz_clamp_re.py`, `record_stage2463a_memorymaster_ingest.py`, `test_stage2460a_to_2465a_suite.py` y `verify_stage2465a_wave237_opencode_gate.py`.
