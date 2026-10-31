<!-- doc-head -->
# STAGE 2492A — Artefactos binarios de 6035 MHz para el enlace PtP-Colo

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se generó y verificó sobre archivos locales en `artifacts/firmware_re_ath10k_tar/`.
- Este documento no contiene apellidos.

## 1. Stage 2490A — los dos artefactos

| Artefacto | Bytes | Origen |
| :--- | ---: | :--- |
| `ath10k_core_6035mhz.ko` | **714.672** | `ath10k_core_openwrt2410.ko` |
| `regulatory_6035mhz.db` | **6.232** | `regulatory.db` |

- `CONFIRMED`: los dos conservan **exactamente** el tamaño del original.

### 1.1 El módulo: variante con secundario por debajo

| Entrada | Offset | Campo | Antes | Después |
| ---: | :--- | :--- | ---: | ---: |
| 25 | `0x0620C8` | frecuencia `+4` | 5845 | **6015** |
| 25 | `0x0620CE` | `hw_value` `+10` | 169 | **203** |
| 26 | `0x062108` | frecuencia `+4` | 5865 | **6035** |
| 26 | `0x06210E` | `hw_value` `+10` | 173 | **207** |

- `CONFIRMED`: **6 bytes** cambiados en el `.ko`.
- `CONFIRMED`: 6035 y su secundario 6015 quedan presentes, que es lo que un canal de 40 MHz necesita.

### 1.2 La base regulatoria: 8 reglas habilitadas

Estructura de **16 bytes** por regla: inicio `+0` e fin `+4` en kHz big endian, `+12` un byte, **flags `+13`**, **máximo EIRP `+14`** como halfword big endian.

| # | Offset | Rango (kHz) | Flags | EIRP |
| ---: | :--- | :--- | ---: | ---: |
| 0 | `0x103C` | 5925000–6425000 | 2 → **0** | 1500 → **3000** |
| 1 | `0x104C` | 5925000–7125000 | 2 → **0** | 1200 → **3000** |
| 2 | `0x105C` | 5925000–7125000 | 10 → **0** | 1200 → **3000** |
| 3 | `0x106C` | 5925000–7125000 | 2 → **0** | 1500 → **3000** |
| 4 | `0x107C` | 5925000–7125000 | 2 → **0** | 2397 → **3000** |
| 5 | `0x108C` | 5925000–7125000 | 2 → **0** | 3000 → **3000** |
| 6 | `0x109C` | 5925000–7125000 | 2 → **0** | 2300 → **3000** |
| 7 | `0x10AC` | 5945000–6425000 | 2 → **0** | 2300 → **3000** |

- `CONFIRMED`: **22 bytes** cambiados en la `.db`: ocho de flags y catorce de EIRP. La regla 5 ya valía 3000, así que su EIRP no cambia.
- `CONFIRMED`: las ocho reglas **cubren 6035000 kHz**.
- `CONFIRMED`: los flags pasan de **2 o 10** a **0**, lo que quita el `NO-IR`/`PASSIVE-SCAN` que impedía levantar un AP sin indicación de radar.
- `CONFIRMED`: el EIRP sube a **3000 mBm = 30 dBm** en las ocho.

## 2. Stage 2491A — verificación estructural

| Comprobación | Resultado |
| :--- | :---: |
| ELF32 big endian | **sí** |
| Máquina MIPS (8) | **sí** |
| Tamaño del `.ko` sin cambio | **sí** |
| Número de secciones sin cambio | **sí** |
| 6035 presente | **sí** |
| 6015 (secundario) presente | **sí** |
| `hw_value` 203 y 207 | **sí** |
| Magia `RGDB` | **sí** |
| Versión 20 | **sí** |
| Tamaño de la `.db` sin cambio | **sí** |
| Flags a cero en las 8 | **sí** |
| EIRP 3000 en las 8 | **sí** |
| Las 8 cubren 6035 | **sí** |

- `CONFIRMED`: **15 comprobaciones**, todas en verde.
- `CONFIRMED`: diff del `.ko` = **6 bytes**; diff de la `.db` = **22 bytes**. Coincide exactamente con lo declarado, sin bytes fuera de los campos.
- `CONFIRMED`: `sha256` de ambos artefactos registrado en el recibo.

## 3. Qué queda listo para el enlace PtP-Colo
- `CONFIRMED`: existe un `.ko` que declara 6035 con secundario 6015.
- `CONFIRMED`: existe una `.db` que permite 6035 sin passive-scan y con 30 dBm de EIRP.
- `CONFIRMED`: el firmware target ya aceptaba 4910..6100 (wave 237), así que no se toca.

## 4. Lo que queda abierto
- `UNKNOWN`: si hostapd acepta el canal sin más cambios. La `.db` habilita la regla, pero hostapd tiene su propia validación.
- `UNKNOWN`: el comportamiento real en el aire. Nada de esto se probó en hardware.
- `UNKNOWN`: si el `hw_value` 203/207 exige calibración en `board.bin`.
- `UNKNOWN`: la firma de la `.db`. Ya estaba ausente y sigue ausente; si el kernel exige firma, habrá que resolverlo aparte.

## 5. Stage 2493A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax` y se añadieron las filas con **CRLF**.

## 6. Artefactos
`run_stage2490a_build_6035mhz_patched_ko_and_regdb.py`, `run_stage2491a_verify_6035mhz_binary_artifacts.py`, `record_stage2493a_memorymaster_ingest.py`, `test_stage2490a_to_2495a_suite.py` y `verify_stage2495a_wave242_opencode_gate.py`.
