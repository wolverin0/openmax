<!-- doc-head -->
*STAGE2066A — Liveness de los 8 stores priv+0x10 y mapa st_value de los 158 dynsym*
# STAGE 2066A — 8 stores y 26 símbolos

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático sobre recibos y módulos ya extraídos. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 2064A — los 8 stores están localizados, la liveness no
- `CONFIRMED`: los **8** stores en `priv+0x10` de la Stage 2053A se releyeron desde el recibo: **4 WA + 4 XC**.
- `CONFIRMED`: se reparten en **2 funciones**: `osif_ioctl_create_vap` (2 por familia) y `__ol_ath_attach` (2 por familia).
- `CONFIRMED`: cada uno lleva su módulo, función, dirección de store y registro base.
- `UNRESOLVED`: la instrucción `addiu reg,v0,imm` que deriva el puntero priv **no aparece antes del store** en el barrido hacia atrás dentro de la función. Los 8 quedan con `derivation_not_found`.
- `UNKNOWN`: si el registro sigue vivo en el store. No se afirma.

## 2. Stage 2065A — sólo 26 de los 158 nombres son direcciones reales
| Medición | Valor |
| :--- | ---: |
| Entradas con nombre en el dynsym | 158 |
| Definidas y con `st_value` distinto de cero | **26** |
| Con al menos un acierto (`word` o `jal`) | **26** |
| Aciertos totales | **54** |

- `CONFIRMED`: las 158 entradas con nombre incluyen muchas **no definidas**; sólo 26 tienen dirección.
- `REFUTED`: que las 158 entradas sean 158 funciones llamables. No lo son.
- `CONFIRMED`: las 26 definidas tienen uso localizable: 54 referencias entre palabras y `jal`.

## 3. Consecuencia
- El universo de nombres útiles de `ubntspecd` es **26**, no 158.
- Los 8 stores están acotados a 2 funciones y 2 familias; lo que falta es la derivación del registro, no la localización.
- Ninguna de las dos incógnitas se cierra con censos; ambas requieren flujo de registros completo.

## 4. Stage 2067A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.

## 5. Lo que no se prueba
- `UNKNOWN`: la liveness de los 8 stores.
- `UNKNOWN`: cuál de los 8 es el campo priv.
- `UNKNOWN`: el uso real de las 26 direcciones.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2064A` | `tools/re/extract_stage2064a_8_priv_0x10_stores_liveness_dissection.py` y su recibo |
| `2065A` | `tools/re/reconcile_stage2065a_ubntspecd_158_dynsym_st_value_to_caller_map.py` y su recibo |
| `2067A` | `tools/verify/record_stage2067a_memorymaster_ingest.py` y su recibo |
| `2068A` | `tests/test_stage2064a_to_2069a_suite.py` |
| `2069A` | `tools/verify/verify_stage2069a_wave171_opencode_gate.py` y la compuerta de la wave |
