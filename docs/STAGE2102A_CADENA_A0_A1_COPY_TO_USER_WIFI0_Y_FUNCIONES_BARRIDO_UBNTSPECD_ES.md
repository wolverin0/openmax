<!-- doc-head -->
# STAGE 2102A — Cadena `a0` a `a1` en el ioctl de wifi0 y funciones del barrido de `ubntspecd`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los bytes ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2100A — los dos "sitios de copia" del encargo no son sitios de copia

El encargo nombra `0x5CDC8` en WA y `0xBCCB0` en XC como sitios de `copy_to_user`. Medidos:

| Dirección | Qué es en realidad | Etiqueta |
| :--- | :--- | :--- |
| `0x5CDC8` (WA y XC) | entrada del cuerpo del caso `SIOCGATHSTATS`, dentro del manejador `0x5CC58` | `CONFIRMED` |
| `0xBCCB0` (XC) | entrada de **otra** función, `0xBCBE0` en WA y `0xBCBE4` en XC | `REFUTED` |
| `0x5CEE4` (WA y XC) | copia real de 4624 bytes | `CONFIRMED` |

- `REFUTED`: que `0x5CDC8` sea una llamada. Es el inicio del cuerpo del caso; la copia real está 284 bytes después.
- `REFUTED`: que `0x5CDC8` y `0xBCCB0` se correspondan. La función de `0xBCCB0` copia **784** bytes desde la pila, no el bloque de 4624.
- `CONFIRMED`: el manejador `0x5CC58` es idéntico en WA y XC y contiene **cuatro** copias masivas:

| Sitio | Tamaño | Origen (`a1`) |
| :--- | ---: | :--- |
| `0x5CEE4` | 4624 | `s2` |
| `0x5CF6C` | 4608 | `v0` |
| `0x5D000` | 384 | `v0` |
| `0x5D50C` | 12452 | `s2` |

## 2. La cadena completa desde `a0` hasta `a1`

Para la copia de 4624 bytes, la cadena resuelta instrucción por instrucción es:

```
prólogo         addu  s1,a0,zero        ; s1 = struct net_device *dev
0x5CDE0/0x5CDE4 lui   s3,0x2
                addu  s3,s1,s3          ; s3 = dev + 0x20000
0x5CDE8         lw    v0,-7752(s3)      ; v0 = *(dev + 0x1E1B8)
0x5CDEC         lw    v0,456(v0)        ; v0 = vtable[456]
0x5CDF0         jalr  ra,v0             ; llamada indirecta
0x5CDF4         lw    a0,-7756(s3)      ; delay slot: a0 = *(dev + 0x1E1B4)
0x5CDFC         addu  s2,v0,zero        ; s2 = valor devuelto
0x5CED8         addu  a1,s2,zero        ; a1 = el puntero devuelto
0x5CEE4         jalr  ra,at             ; copia de 4624 bytes
```

- `CONFIRMED`: el desplazamiento exacto sumado al `net_device` es **`0x1E1B4`**, resultado de `0x20000 - 7756`. El receptor de la llamada es ese campo.
- `CONFIRMED`: la tabla de métodos se lee en `*(dev + 0x1E1B8)` y el método usado es el índice **456**.
- `REFUTED`: que `a1` sea una estructura estática. Es el **valor devuelto** por una llamada indirecta, así que no tiene dirección fija en el binario.
- `UNKNOWN`: el nombre del método 456. No hay símbolo que lo cubra y la tabla se llena en ejecución.

## 3. Escritores de `+0xb4` y `+0xdc`

| Desplazamiento | Escrituras con base no-pila | Dentro del manejador |
| :--- | ---: | ---: |
| `+0xb4` | 44 | **0** |
| `+0xdc` | 18 | **0** |

- `CONFIRMED`: el manejador `0x5CC58` **no escribe** ninguno de los dos campos. Sólo los lee a través de la copia.
- `UNKNOWN`: cuáles de las 44 y 18 escrituras externas pertenecen a la misma estructura que devuelve el método 456. Sin flujo entre funciones no se puede afirmar.

## 4. Stage 2101A — no hay dos funciones de barrido, hay una sola

- `REFUTED`: que `0x40129C` y `0x4018A4` vivan en funciones distintas. Las dos están en la **misma** función, `main`, en `0x400F80` con marco de `-344`, en WA y en XC.
- `CONFIRMED`: `main` **no restaura su marco** en ninguna instrucción del binario, así que no tiene epílogo localizable. Su extensión queda acotada, no cerrada: 1537 instrucciones hasta el siguiente prólogo en `0x402784`, con 172 llamadas.
- `CONFIRMED`: la función que materializa `/dev/uph_%s` es otra, en `0x4064E0`, de 20 instrucciones y marco `-4128`.

### Qué hace esa función de 20 instrucciones

```
0x4064E0  addiu sp,sp,-4128
0x4064F8  addiu a0,sp,24          ; destino en pila
0x4064FC  jal   0x40B5D0          ; sprintf
0x406500  addiu a1,a1,-22624      ; a1 = 0x40A7A0 = "/dev/uph_%s"
0x406508  jal   0x40B660          ; open
0x40650C  addiu a0,sp,24          ; delay slot: el mismo buffer
```

- `INFERRED`: `sprintf(buffer, "/dev/uph_%s", nombre)` seguido de `open(buffer, 2)`. La forma encaja con las dos llamadas y con el formato, pero los nombres de `0x40B5D0` y `0x40B660` no están en el archivo.
- `CONFIRMED`: el buffer es de pila, dentro de un marco de 4128 bytes.

### Constantes en el rango de frecuencias

Dentro de `main`, en WA y en XC, aparecen exactamente estas constantes entre 2000 y 6000:

| Valor | Banda que sugiere |
| ---: | :--- |
| `2400` | 2.4 GHz (`INFERRED`) |
| `2485` | 2.4 GHz (`INFERRED`) |
| `3600` | intermedia (`UNKNOWN`) |
| `5100` | 5 GHz (`INFERRED`) |
| `5900` | 5 GHz (`INFERRED`) |

- `CONFIRMED`: son cinco valores, los mismos en las dos familias.
- `UNKNOWN`: la unidad. La etapa no afirma que sean MHz; sólo que caen en el rango y que acompañan al selector de banda.

## 5. Lo que queda abierto
- `UNKNOWN`: el nombre del método 456 de la tabla de `dev + 0x1E1B8`.
- `UNKNOWN`: la identidad de la estructura devuelta y, por tanto, de sus campos `0xb4` y `0xdc`.
- `UNKNOWN`: la unidad de las cinco constantes.
- `UNKNOWN`: la extensión exacta de `main`, porque no tiene epílogo.

## 6. Stage 2103A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 7. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2100A` | `tools/re/extract_stage2100a_wifi0_ioctl_copy_to_user_a1_from_chain_re.py` y su recibo |
| `2101A` | `tools/re/reconcile_stage2101a_ubntspecd_0x40129c_and_0x4018a4_freq_sweep_re.py` y su recibo |
| `2103A` | `tools/verify/record_stage2103a_memorymaster_ingest.py` y su recibo |
| `2104A` | `tests/test_stage2100a_to_2105a_suite.py` |
| `2105A` | `tools/verify/verify_stage2105a_wave177_opencode_gate.py` y su recibo |
