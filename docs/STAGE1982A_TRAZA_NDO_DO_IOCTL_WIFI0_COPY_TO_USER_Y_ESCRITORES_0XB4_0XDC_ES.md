<!-- doc-head -->
*STAGE1982A — Traza de ndo_do_ioctl wifi0, copy_to_user y escritores de 0xb4/0xdc*
# STAGE 1982A — La fuente del copy

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático de `umac.ko` y `ath_dev.ko` de WA y XC. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 1980A — el caso 0x89f0 copia desde s2
- `CONFIRMED`: el cuerpo del caso termina con una secuencia inequívoca:
  - `lw a0,4(s0)` — puntero de usuario;
  - `addu a1,s2,zero` — **origen** de la copia;
  - `addiu a2,zero,4624` — **tamaño**;
  - `jalr at` — llamada **indirecta**.
- `CONFIRMED`: la llamada no es un símbolo con nombre. El destino se materializa con un par `lui/addiu` que lleva una **reubicación**, y el módulo no exporta `copy_to_user`.
- `CONFIRMED`: por tanto la copia es `copia(destino_usuario, s2, 4624)` y `s2` es la base del struct de estadísticas.
- `CONFIRMED`: `wifi%d` existe en `.rodata` (3 apariciones), pero `alloc_netdev` y `register_netdev` **no son símbolos** de `umac.ko`; el netdev se crea fuera de este módulo.
- `UNKNOWN`: el offset exacto de `ndo_do_ioctl` en `net_device_ops`. No se localizó la asignación.

## 2. Stage 1981A — los escritores de 0xb4 y 0xdc
- `CONFIRMED`: **94** sitios `sw ...,0xb4(base)` y **48** `sw ...,0xdc(base)` en los cuatro módulos (142 en total).
- `CONFIRMED`: **ninguno** de esos stores cae dentro del cuerpo del caso 0x89f0.
- `UNKNOWN`: cuál de los 142 candidatos escribe la estructura que devuelve el handler. El stage los reporta como candidatos y **no** atribuye ninguno.
- `INFERRED`: el escritor está fuera del camino del ioctl, lo que es coherente con un contador que se actualiza en el camino de TX y no en la lectura.

## 3. Stage 1983A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.
- `CONFIRMED`: los identificadores quedaron registrados en los recibos.

## 4. Lo que no se prueba
- `UNKNOWN`: el offset de `ndo_do_ioctl` y la función registrada.
- `UNKNOWN`: cuál de los 142 stores es el escritor real.
- `UNKNOWN`: si el contador se incrementa por paquete o por error.
- `UNKNOWN`: cualquier lectura en vivo.

## 5. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1980A` | `tools/re/extract_stage1980a_wifi0_ndo_do_ioctl_copy_to_user_source_re.py` y su recibo |
| `1981A` | `tools/re/reconcile_stage1981a_source_base_0xb4_0xdc_writer_functions.py` y su recibo |
| `1983A` | `tools/verify/record_stage1983a_memorymaster_ingest.py` y su recibo |
| `1984A` | `tests/test_stage1980a_to_1985a_suite.py` |
| `1985A` | `tools/verify/verify_stage1985a_wave157_opencode_gate.py` y la compuerta de la wave |
