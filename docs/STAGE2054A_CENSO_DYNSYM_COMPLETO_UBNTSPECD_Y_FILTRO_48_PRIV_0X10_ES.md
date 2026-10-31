<!-- doc-head -->
*STAGE2054A — Censo completo del dynsym de ubntspecd y filtro de los 48 punteros priv*
# STAGE 2054A — 160 símbolos y 8 candidatos

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático de `ubntspecd` y de los recibos de la wave anterior. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 2052A — el dynsym sí tiene nombres
| Medición | Valor |
| :--- | ---: |
| Símbolos en `0..SYMTABNO-1` | **160** |
| Con nombre | **158** |
| Bibliotecas `DT_NEEDED` | **3** |
| Instrucciones `syscall` directas | **6** |

- `CONFIRMED`: la tabla dinámica tiene **160** entradas, no dos. La wave anterior sólo recorrió el rango `[GOTSYM, SYMTABNO)`, que en este binario empieza casi al final.
- `REFUTED`: que `ubntspecd` carezca de símbolos dinámicos. Los tiene; lo que no tiene es un GOT extenso para ellos.
- `CONFIRMED`: hay **3** bibliotecas necesarias y **6** llamadas directas al sistema.

## 2. Stage 2053A — 8 stores en 0x10
- `CONFIRMED`: las **48** derivaciones `addiu reg,v0,imm` definen los registros que portan el puntero priv.
- `CONFIRMED`: de los **720** stores, **70** caen en el rango 0x00..0x20 usando uno de esos registros como base.
- `CONFIRMED`: **8** caen exactamente en el offset **0x10**.
- `INFERRED`: esos 8 son los candidatos reales al campo que la wave 165 buscaba.
- `UNKNOWN`: cuál de los 8 es el correcto. Un registro puede reutilizarse para otra base dentro de la misma función.

## 3. Consecuencia
- La ruta `dynsym` no estaba agotada: estaba mal recorrida. Con el censo completo hay 160 símbolos y 3 bibliotecas.
- El universo de candidatos a `priv+0x10` baja de 720 a **8**.
- Falta el flujo de registros para decidir cuál de los 8 es el campo real.

## 4. Stage 2055A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.

## 5. Lo que no se prueba
- `UNKNOWN`: cuál de los 8 stores en 0x10 es el campo priv.
- `UNKNOWN`: el uso de los 160 símbolos dinámicos por el código.
- `UNKNOWN`: cualquier lectura en vivo.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2052A` | `tools/re/extract_stage2052a_ubntspecd_all_dynsym_and_dt_needed_census.py` y su recibo |
| `2053A` | `tools/re/reconcile_stage2053a_48_priv_derivations_offset_0x10_filter.py` y su recibo |
| `2055A` | `tools/verify/record_stage2055a_memorymaster_ingest.py` y su recibo |
| `2056A` | `tests/test_stage2052a_to_2057a_suite.py` |
| `2057A` | `tools/verify/verify_stage2057a_wave169_opencode_gate.py` y la compuerta de la wave |
