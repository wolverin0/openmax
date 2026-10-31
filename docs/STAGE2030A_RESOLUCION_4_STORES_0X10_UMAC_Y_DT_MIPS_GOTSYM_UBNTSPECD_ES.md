<!-- doc-head -->
*STAGE2030A — Los 4 stores a estructura en umac.ko y la resolución DT_MIPS_GOTSYM en ubntspecd*
# STAGE 2030A — 4 stores y GOT dinámico

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático de `umac.ko` y `ubntspecd`. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 2028A — los 4 candidatos
- `CONFIRMED`: quedan **4** stores `sw reg,0x10(base)` con base distinta de `sp` dentro de las funciones constructoras de WA y XC.
- `CONFIRMED`: para cada uno se reporta la instrucción que define el registro base y la que define el registro valor, dentro de la misma función.
- `INFERRED`: la rebanada hacia atrás identifica el origen inmediato, pero no prueba que el campo sea el que se copia después.
- `UNKNOWN`: el inicializador de `priv+0x10`. Sigue sin atribuirse.

## 2. Stage 2029A — la resolución GOT sólo cubre 2 de 52
- `CONFIRMED`: el segmento `PT_DYNAMIC` de `ubntspecd` contiene la metadata MIPS necesaria y se parseó sin tabla de secciones.
- `CONFIRMED`: de **52** sitios `jalr`, sólo **2** resuelven a un símbolo dinámico. **50** quedan sin resolver.
- `CONFIRMED`: **0** sitios resuelven a `ioctl`, así que no hay inmediatos de petición que extraer por esta vía.
- `INFERRED`: la mayoría de los `jalr` apuntan a stubs locales o la ranura GOT no se corresponde con el cálculo aplicado; el sesgo de `gp` o el diseño del GOT no encajan con la fórmula estándar en este binario.
- `UNKNOWN`: el mapa completo ranura → nombre.

## 3. Consecuencia
- El wrapper de `ubntspecd` no se resuelve con la metadata dinámica de este binario.
- Los 4 candidatos a estructura quedan documentados pero sin atribución.
- Ambas incógnitas necesitan desensamblado del stub PLT, no otra fórmula.

## 4. Stage 2031A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.

## 5. Lo que no se prueba
- `UNKNOWN`: inicializador de `priv+0x10`.
- `UNKNOWN`: mapa ranura GOT → nombre.
- `UNKNOWN`: cualquier lectura en vivo.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2028A` | `tools/re/extract_stage2028a_umac_4_struct_stores_0x10_resolution.py` y su recibo |
| `2029A` | `tools/re/reconcile_stage2029a_ubntspecd_dt_mips_gotsym_resolver.py` y su recibo |
| `2031A` | `tools/verify/record_stage2031a_memorymaster_ingest.py` y su recibo |
| `2032A` | `tests/test_stage2028a_to_2033a_suite.py` |
| `2033A` | `tools/verify/verify_stage2033a_wave165_opencode_gate.py` y la compuerta de la wave |
