<!-- doc-head -->
*STAGE2048A — Disección de los llamadores de alloc_netdev y tabla GOT dinámica de ubntspecd*
# STAGE 2048A — Callers y tabla GOT

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático de ocho módulos y de `ubntspecd`. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 2046A — cuerpos completos de los llamadores
- `CONFIRMED`: se desensamblaron los cuerpos completos de las funciones que llaman a `alloc_netdev_mq`, `register_netdev` o `register_netdevice`: **26** registros de llamada que cubren los **7** nombres de llamador.
- `CONFIRMED`: se extrajeron **48** derivaciones del tipo `addiu reg,v0,imm` sobre el retorno de la llamada.
- `CONFIRMED`: se listaron **720** stores dentro de esos cuerpos, con su registro base y su offset.
- `INFERRED`: la lista de stores es completa por función; lo que falta es la semántica de cada campo.
- `UNKNOWN`: el layout de `priv`. Ningún store se atribuye a `priv+0x10`.

## 2. Stage 2047A — la tabla dinámica es casi vacía
- `CONFIRMED`: el rango `[DT_MIPS_GOTSYM, DT_MIPS_SYMTABNO-1]` de `ubntspecd` contiene **2** símbolos dinámicos.
- `CONFIRMED`: **0** de los símbolos buscados (`ioctl`, `socket`, `bind`, `sendto`, `recvfrom`, `open`, `read`, `close`) tiene sitios `lw` por esa fórmula.
- `REFUTED`: la idea de que `ubntspecd` resuelve sus llamadas por una tabla GOT dinámica extensa. La tabla tiene dos entradas.
- `INFERRED`: el binario está enlazado de forma que casi todas sus llamadas son directas, no por `dynsym`.

## 3. Consecuencia
- El "wrapper" de `ubntspecd` no se puede resolver por `dynsym` porque el `dynsym` no contiene esos nombres.
- Los 720 stores de los llamadores están listados; la atribución de campo sigue pendiente.
- Ambas rutas necesitan desensamblado de código local, no tablas dinámicas.

## 4. Stage 2049A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.

## 5. Lo que no se prueba
- `UNKNOWN`: el layout de `priv`.
- `UNKNOWN`: los nombres de las llamadas locales de `ubntspecd`.
- `UNKNOWN`: cualquier lectura en vivo.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2046A` | `tools/re/extract_stage2046a_7_alloc_netdev_callers_priv_init_dissection.py` y su recibo |
| `2047A` | `tools/re/reconcile_stage2047a_ubntspecd_full_dynsym_got_slot_table.py` y su recibo |
| `2049A` | `tools/verify/record_stage2049a_memorymaster_ingest.py` y su recibo |
| `2050A` | `tests/test_stage2046a_to_2051a_suite.py` |
| `2051A` | `tools/verify/verify_stage2051a_wave168_opencode_gate.py` y la compuerta de la wave |
