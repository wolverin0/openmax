<!-- doc-head -->
*STAGE2024A — Los 26 sitios sw,0x10 en umac.ko y el wrapper de ubntspecd*
# STAGE 2024A — 22 saves y 4 candidatos

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático de `umac.ko` y `ubntspecd`. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 2022A — el recuento anterior estaba contaminado
- `CONFIRMED`: de los **26** sitios `sw reg,0x10(base)` que la Stage 2011A dejó dentro de las funciones constructoras, **22** son **guardados de prólogo** (`sw s0,16(sp)`), no escrituras de campo.
- `CONFIRMED`: solo **4** usan una base distinta de `sp` y son candidatos reales a escritura de estructura.
- `POR CONFIRMAR`: cuál de esos 4, si alguno, escribe el campo que luego se copia.
- `UNKNOWN`: el inicializador de `priv+0x10`.

La lección es directa: filtrar por nombre de función no distingue un `sw` a estructura de un `sw` al marco de pila. El recuento de 26 no eran 26 candidatos.

## 2. Stage 2023A — el wrapper de ubntspecd
- `CONFIRMED`: hay **52** sitios `jalr` entre los dos binarios.
- `CONFIRMED`: se agrupan en **4** grupos distintos por ranura GOT, lo que indica 4 callees distintos.
- `UNKNOWN`: qué ranura corresponde a `ioctl`, `socket`, `bind`, `sendto` o `recvfrom`. El binario no trae tabla de secciones que permita mapear la ranura al nombre.
- `INFERRED`: el demonio usa un wrapper propio sobre esas 4 llamadas, no una llamada directa por nombre.

## 3. Consecuencia
- El universo real de candidatos a inicializador baja de 26 a **4**.
- El wrapper de ubntspecd existe y tiene 4 callees, pero no se puede nombrar sin resolver la tabla dinámica.
- Ambas incógnitas necesitan análisis de flujo de registros, no otro censo.

## 4. Stage 2025A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.

## 5. Lo que no se prueba
- `UNKNOWN`: el inicializador entre los 4 candidatos.
- `UNKNOWN`: el mapa ranura GOT a nombre.
- `UNKNOWN`: cualquier lectura en vivo.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2022A` | `tools/re/extract_stage2022a_umac_26_constructor_sw_0x10_dissection.py` y su recibo |
| `2023A` | `tools/re/reconcile_stage2023a_ubntspecd_ioctl_wrapper_and_nl80211_trace.py` y su recibo |
| `2025A` | `tools/verify/record_stage2025a_memorymaster_ingest.py` y su recibo |
| `2026A` | `tests/test_stage2022a_to_2027a_suite.py` |
| `2027A` | `tools/verify/verify_stage2027a_wave164_opencode_gate.py` y la compuerta de la wave |
