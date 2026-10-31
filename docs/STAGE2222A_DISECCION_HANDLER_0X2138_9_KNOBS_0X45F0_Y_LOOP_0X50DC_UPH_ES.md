<!-- doc-head -->
# STAGE 2222A — El handler compartido `0x2138`, el de `sta_priority` y el bucle de `0x50DC`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2220A — por qué un solo handler sirve nueve knobs

Se decodificaron los **once** campos de cada registro de `.rodata` cuyo `proc_handler` es `0x2138` o `0x45F0`. Aparecen **31** registros por familia, no diez: los doce knobs son un subconjunto de una tabla mayor.

| Medición | WA | XC |
| :--- | ---: | ---: |
| Registros con estos dos handlers | **31** | **31** |
| Valores distintos de `.data` | **3** | **3** |
| `extra1` y `extra2` en cero | sí | sí |

Distribución de `.data` entre los 31 registros: `0x9A8` en 16, `0x9A4` en 8, `0x1A4` en 7.

- `CONFIRMED`: `+.0x1C` (`extra1`) y `+0x20` (`extra2`) valen **cero en todos** los registros.
- `REFUTED`: que `0x2138` discrimine por cotas. Un handler de mínimos y máximos usaría esos dos campos y están vacíos.
- `REFUTED`: que discrimine por `.data`. Sólo hay **tres** valores para 31 registros, así que el puntero de datos no basta.
- `CONFIRMED`: el único campo que **sí** es distinto en cada registro es `.procname`, en `+0x00`.
- `INFERRED`: por eliminación, `0x2138` decide el knob por el **nombre**, no por cotas ni por datos.
- `UNKNOWN`: el mecanismo exacto. Comparar cadenas en un `proc_handler` es caro y poco habitual; podría usar un índice derivado del nombre o un campo parchado en el clon.

### Los dos handlers

| Handler | Instrucciones | Llamadas directas | Indirectas | Almacenes |
| :--- | ---: | :--- | ---: | ---: |
| `0x2138` | 128 | **ninguna** | 0 | 19 |
| `0x45F0` | 128 | **`snprintf` × 5** | 0 | 25 |

- `CONFIRMED`: `0x2138` **no hace ninguna llamada** en la ventana medida. Escribe 19 veces y no delega.
- `CONFIRMED`: `0x45F0` llama **cinco veces** a `snprintf`: compone texto, lo que encaja con un campo de prioridad expresado como cadena.
- `REFUTED`: que los dos handlers compartan forma. Uno no llama y el otro formatea cinco veces.

## 2. Stage 2221A — el bucle de parcheo de `0x50DC`

Entre el primer `amalloc_private` y el `register_sysctl_table` hay **18** llamadas y **50** almacenes, de los cuales **32** no van a la pila.

| Secuencia de llamadas | Almacenes no-pila | Offsets parcheados |
| :--- | ---: | :--- |
| `amalloc_private`, `memset`, `snprintf`, `amalloc_private`, `memcpy` ×3 | 32 | `0x0`, `0xC0`, `0xF0` |

- `CONFIRMED`: la secuencia reserva, borra, formatea y copia tres veces antes de registrar.
- `CONFIRMED`: hay almacenes no-pila en `+0x000`, `+0x0C0` y `+0x0F0` con origen en `v0` y `at`, es decir punteros devueltos por las reservas.
- `CONFIRMED`: `0xC0` **no** es múltiplo de `0x2C`, así que el clon **no** es un arreglo simple de registros de 44 bytes. Es otra estructura, o un arreglo con cabecera.
- `INFERRED`: el bucle parchea punteros de instancia en el clon, no los campos de los registros originales.
- `UNKNOWN`: qué campo de qué estructura recibe cada uno de los tres offsets.

## 3. Qué cambia
- El handler compartido deja de ser «uno que sirve nueve knobs» sin explicación: se descartan cotas y datos, y queda el nombre como único discriminante.
- `0x45F0` queda caracterizado como formateador, no como escritor de enteros.
- El clon de `0x50DC` deja de suponerse un arreglo de registros de 44 bytes.

## 4. Lo que queda abierto
- `UNKNOWN`: el mecanismo real de discriminación de `0x2138`.
- `UNKNOWN`: el destino de los cinco `snprintf` de `0x45F0`.
- `UNKNOWN`: la estructura del clon, dado que `0xC0` no es múltiplo de `0x2C`.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2223A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2220A` | `tools/re/extract_stage2220a_uph_9knob_handler_0x2138_and_0x45f0_re.py` y su recibo |
| `2221A` | `tools/re/reconcile_stage2221a_uph_0x50dc_template_patching_loop_re.py` y su recibo |
| `2223A` | `tools/verify/record_stage2223a_memorymaster_ingest.py` y su recibo |
| `2224A` | `tests/test_stage2220a_to_2225a_suite.py` |
| `2225A` | `tools/verify/verify_stage2225a_wave197_opencode_gate.py` y su recibo |
