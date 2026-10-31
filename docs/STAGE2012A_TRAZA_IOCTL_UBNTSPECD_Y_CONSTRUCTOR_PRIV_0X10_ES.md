<!-- doc-head -->
*STAGE2012A — Traza de ioctl en ubntspecd y constructor de priv+0x10*
# STAGE 2012A — ioctl y constructor

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Análisis estático de `ubntspecd` y de los módulos WA/XC. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 2010A — los ioctl de ubntspecd
- `CONFIRMED`: `ubntspecd` es un **ET_EXEC MIPS** sin tabla de secciones y se leyó por program headers.
- `CONFIRMED`: contiene las cadenas `ioctl`, `open`, `socket` y `close` como nombres de PLT.
- `CONFIRMED`: hay **52** sitios `jalr` entre los dos binarios (WA y XC).
- `CONFIRMED`: **0** de esos sitios tienen un código de ioctl en el rango 0x8900..0x8fff dentro de la ventana de 12 instrucciones.
- `INFERRED`: el código de petición se construye en un registro mucho antes de la llamada, probablemente a partir de una tabla o de un cálculo, y no como inmediato cercano.
- `UNKNOWN`: el número exacto de ioctl que configura `ss_period`. No se adivina.

## 2. Stage 2011A — el constructor del netdev
- `CONFIRMED`: `umac.ko` importa **`alloc_netdev_mq`**, **`register_netdev`** y **`free_netdev`**; `ath_dev.ko` no importa ninguno.
- `CONFIRMED`: se identificaron **12** funciones constructoras por sus llamadas relocalizadas a esos tres símbolos entre WA, XC y ath_dev.
- `CONFIRMED`: dentro de esas funciones hay **26** stores a `0x10(base)`, frente a los **4178** del módulo completo.
- `CONFIRMED`: el offset `dev->priv` es **0x10** y el puntero que se guarda allí no queda identificado por esta traza.
- `UNKNOWN`: cuál de los 26 stores inicializa el campo que luego se copia.

## 3. Consecuencia
- La búsqueda de códigos de ioctl por ventana no basta: el binario construye el comando lejos de la llamada.
- El constructor sí se puede aislar por relocalización, y eso reduce el universo de 4178 a 26 stores.
- Ninguna de las dos incógnitas se cierra con census; ambas necesitan flujo de registros por función.

## 4. Stage 2013A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.

## 5. Lo que no se prueba
- `UNKNOWN`: el número de ioctl de `ss_period`.
- `UNKNOWN`: el store exacto que inicializa `priv+0x10`.
- `UNKNOWN`: cualquier lectura en vivo.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2010A` | `tools/re/extract_stage2010a_ubntspecd_ioctl_callsites_and_cmd_re.py` y su recibo |
| `2011A` | `tools/re/reconcile_stage2011a_netdev_priv_0x10_constructor_trace.py` y su recibo |
| `2013A` | `tools/verify/record_stage2013a_memorymaster_ingest.py` y su recibo |
| `2014A` | `tests/test_stage2010a_to_2015a_suite.py` |
| `2015A` | `tools/verify/verify_stage2015a_wave162_opencode_gate.py` y la compuerta de la wave |
