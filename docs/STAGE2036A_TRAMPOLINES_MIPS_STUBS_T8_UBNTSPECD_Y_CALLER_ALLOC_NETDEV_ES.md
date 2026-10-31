<!-- doc-head -->
*STAGE2036A — Trampolines .MIPS.stubs en ubntspecd y llamadores de alloc_netdev_mq*
# STAGE 2036A — Stubs y alloc_netdev_mq

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático de `ubntspecd` y de ocho módulos WA/XC. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 2034A — sólo 2 de 52 pasan por stub
- `CONFIRMED`: de los **52** sitios `jalr`, sólo **2** llegan a través de una palabra GOT que apunta al segmento ejecutable, es decir, a un trampolín de enlace perezoso.
- `CONFIRMED`: esos **2** se resolvieron leyendo el índice en `t8` del stub y buscándolo en `DT_SYMTAB`/`DT_STRTAB`.
- `CONFIRMED`: los otros **50** no pasan por un stub: son llamadas directas a código local.
- `INFERRED`: por eso la fórmula GOT de la wave anterior sólo acertaba en dos casos; el resto nunca fue una llamada dinámica.
- `UNKNOWN`: el nombre de los 50 destinos directos, que son funciones internas sin símbolo.

## 2. Stage 2035A — 26 llamadas y 7 llamadores
- `CONFIRMED`: hay **26** llamadas relocalizadas a `alloc_netdev_mq`, `register_netdev` o `register_netdevice` repartidas en los ocho módulos.
- `CONFIRMED`: pertenecen a **7** funciones distintas.
- `CONFIRMED`: cada llamada lleva su ventana de instrucciones, incluido el manejo del retorno en `v0`.
- `UNKNOWN`: el layout de `priv`. No se probó qué campo se escribe en `priv+0x10`.

## 3. Consecuencia
- El "wrapper" de ubntspecd no es un wrapper dinámico: la mayoría de las llamadas son directas a código propio.
- La construcción del netdev está acotada a 7 funciones, pero el layout de `priv` sigue sin resolverse.
- Ambas incógnitas necesitan análisis de flujo por función, no otra tabla.

## 4. Stage 2037A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.

## 5. Lo que no se prueba
- `UNKNOWN`: los 50 destinos directos de ubntspecd.
- `UNKNOWN`: el layout de `priv`.
- `UNKNOWN`: cualquier lectura en vivo.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2034A` | `tools/re/extract_stage2034a_ubntspecd_mips_stubs_t8_dynsym_resolver.py` y su recibo |
| `2035A` | `tools/re/reconcile_stage2035a_alloc_netdev_mq_caller_and_priv_layout.py` y su recibo |
| `2037A` | `tools/verify/record_stage2037a_memorymaster_ingest.py` y su recibo |
| `2038A` | `tests/test_stage2034a_to_2039a_suite.py` |
| `2039A` | `tools/verify/verify_stage2039a_wave166_opencode_gate.py` y la compuerta de la wave |
