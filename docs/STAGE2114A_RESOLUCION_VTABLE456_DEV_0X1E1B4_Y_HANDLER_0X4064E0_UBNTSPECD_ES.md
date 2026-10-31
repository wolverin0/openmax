<!-- doc-head -->
# STAGE 2114A — Resolución de `vtable[456]` sobre `dev+0x1E1B4` y el handler `0x4064E0` de `ubntspecd`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los bytes ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2112A — primero hay que separar dos campos

El encargo llama "puntero de tabla" a `dev+0x1E1B4` y pide su entrada `+456`. La Stage 2100A ya mostró que son dos campos distintos, y esta etapa lo vuelve a medir en las cuatro parejas de módulos.

| Dirección | Qué contiene | Etiqueta |
| :--- | :--- | :--- |
| `dev+0x1E1B4` | el **receptor** que se pasa a la llamada | `CONFIRMED` |
| `dev+0x1E1B8` | el puntero a la **tabla** cuyo índice 456 se invoca | `CONFIRMED` |

- `REFUTED`: que `0x1E1B4` sea el puntero de tabla. El índice 456 se aplica sobre `*(dev+0x1E1B8)`.
- `CONFIRMED`: la aritmética es `s3 = dev + 0x20000`, y los dos campos quedan en `-7756(s3)` y `-7752(s3)`.

### ¿Dónde se inicializan esos campos?

| Medición | WA_umac | XC_umac | WA_ath_dev | XC_ath_dev |
| :--- | ---: | ---: | ---: | ---: |
| Escrituras con desplazamiento literal a `0x1E1B4` o `0x1E1B8` | **0** | **0** | **0** | **0** |
| Escrituras con desplazamiento relativo a `-7756` | **0** | **0** | **0** | **0** |
| Escrituras con desplazamiento relativo a `-7752` | 1 | 1 | 0 | 0 |

- `CONFIRMED`: la única escritura relativa es `sw zero,-7752(s7)` en `0xBBEA0` (WA) y `0xBBEA4` (XC). Escribe **cero** y usa una base distinta de `dev`, así que no inicializa la tabla de este camino.
- `CONFIRMED`: ninguna de las cuatro parejas escribe `dev+0x1E1B4` con un desplazamiento literal. El campo se llena por una ruta que esta búsqueda no alcanza.
- `UNKNOWN`: la instrucción exacta que inicializa el receptor.

### ¿Cuál es la función de `vtable[456]`?

- `CONFIRMED`: hay **6** lecturas del índice 456 con la forma `lw v0,456(v0)` en `umac.ko`, en `0x5C19C`, `0x5CDEC` y `0x5CF08` para cada familia. Ninguna en `ath_dev.ko`.
- `CONFIRMED`: se revisaron **16** corridas de punteros de código de al menos 120 entradas en `.rodata` y `.data`.
- `CONFIRMED`: la única corrida que llega al índice 114 y lo resuelve es la de 1268 entradas, y su entrada 114 vale `0x94D8C`, que decodifica como `addiu s1,zero,-22`: **mitad de función**, no un prólogo.
- `REFUTED`: que exista una tabla estática de operaciones cuyo índice 114 sea una función. No la hay en estos módulos.
- `UNKNOWN`: el destino real de `vtable[456]`. La tabla se llena en ejecución y no tiene dirección estática.

### Qué escribe el handler en el puntero devuelto

- `CONFIRMED`: en el cuerpo de `0x5CC58` el registro `s2` sólo recibe escrituras en tres desplazamientos: `4364` (`0x110C`), `4368` (`0x1110`) y `4372` (`0x1114`), en las dos ramas.
- `CONFIRMED`: escrituras a `+0xb4` sobre ese puntero: **0**. Escrituras a `+0xdc`: **0**.
- `REFUTED`: que el handler complete los campos `0xb4` y `0xdc` de la estructura que copia. No los toca.

## 2. Stage 2113A — el handler del dispositivo

El manejador `0x4064E0` quedó acotado en la Stage 2101A entre `0x4064E0` y `0x406530`, con marco de 4128 bytes. Aquí se mapea el camino completo.

| Eslabón | Medición | Etiqueta |
| :--- | :--- | :--- |
| Cadena de formato | `/dev/uph_%s` en `0x40A7A0` | `CONFIRMED` |
| Primera llamada | `0x4064FC` a `0x40B5D0`, slot GOT `0x41B7A4` | `CONFIRMED` |
| Segunda llamada | `0x406508` a `0x40B660`, slot GOT `0x41B7C8` | `CONFIRMED` |
| Guardado del descriptor | `sw v0,0(s0)` en `0x406518` | `CONFIRMED` |
| Llamadores | `jal` en `0x405C10` y `0x407850` | `CONFIRMED` |

- `CONFIRMED`: la función construye la ruta en un buffer de pila y guarda el resultado de la segunda llamada a través del puntero que recibe en `a1`. Ese resultado es el descriptor.
- `INFERRED`: la primera llamada es `sprintf(buffer, "/dev/uph_%s", nombre)` y la segunda es `open(buffer, 2)`. La forma de los registros encaja, pero los nombres de `0x40B5D0` y `0x40B660` **no están en el archivo**.
- `UNKNOWN`: la identidad de los dos slots. Sólo cuatro slots del binario llevan relocación `JUMP_SLOT` y ninguno es estos dos.

### Uso del descriptor

- `CONFIRMED`: el llamador de `0x405BF8` toma el descriptor de `24(sp)` y llama a `0x406550` y a `0x406530`.
- `CONFIRMED`: `0x406530` es un envoltorio de tres instrucciones que hace una llamada y devuelve cero.
- `CONFIRMED`: `0x406550` hace dos llamadas con `a2 = 144` y, en la segunda, pasa el pedido **`0x40905501`** como `a1` junto al buffer.
- `INFERRED`: por la forma, `0x406530` cierra el descriptor y `0x406550` lee y luego ejecuta un `ioctl` con ese pedido.
- `UNKNOWN`: el segundo llamador, `0x407850`, usa un puntero de salida dentro de una estructura en vez de una variable de pila. Su consumo posterior no se siguió.

## 3. Lo que queda abierto
- `UNKNOWN`: la función de destino de `vtable[456]`.
- `UNKNOWN`: la instrucción que inicializa `dev+0x1E1B4` y `dev+0x1E1B8`.
- `UNKNOWN`: el nombre de los dos stubs del camino del dispositivo.
- `UNKNOWN`: quién escribe `+0xb4` y `+0xdc` de la estructura devuelta, si alguien lo hace.

## 4. Stage 2115A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 5. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2112A` | `tools/re/extract_stage2112a_dev_plus_0x1e1b4_vtable456_target_re.py` y su recibo |
| `2113A` | `tools/re/reconcile_stage2113a_ubntspecd_0x4064e0_uph_device_handler_re.py` y su recibo |
| `2115A` | `tools/verify/record_stage2115a_memorymaster_ingest.py` y su recibo |
| `2116A` | `tests/test_stage2112a_to_2117a_suite.py` |
| `2117A` | `tools/verify/verify_stage2117a_wave179_opencode_gate.py` y su recibo |
