<!-- doc-head -->
# STAGE 2090A — Lectores de la banda `0x41B8C4` y el offset real de `a0` en el manejador ioctl

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los bytes ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2088A — quién lee el byte de banda

La Stage 2076A dejó dos escritores sobre `0x41B8C4`. El barrido abstracto de esta etapa confirma **los mismos dos** y añade **dos lectores**:

| Tipo | WA | XC | Instrucción |
| :--- | :--- | :--- | :--- |
| Escritura (`-g`) | `0x40110C` | `0x40110C` | `sw zero,16(v0)` |
| Escritura (`-a`) | `0x40115C` | `0x40115C` | `sw v1,16(v0)` |
| Lectura | `0x40129C` | `0x40129C` | `lw v0,16(a0)` |
| Lectura | `0x4018A4` | `0x4018A4` | `lw v1,16(v0)` |

- `CONFIRMED`: las direcciones de escritura coinciden exactamente con las de la Stage 2076A, obtenidas ahora por otro método. Dos vías independientes dan el mismo par.
- `CONFIRMED`: la cadena completa es `0x420000 - 0x47F0 = 0x41B810`, que contiene `0x41B8B4`, más `0x10` igual a `0x41B8C4`.
- `CONFIRMED`: ambos lectores usan el mismo puntero global y el mismo desplazamiento.

### Qué hacen los lectores

Primer lector, en la ruta de opción desconocida:

```
0x401298  lw    a0,-18416(s6)
0x40129C  lw    v0,16(a0)          <-- lectura de la banda
0x4012A0  beq   v0,zero,0x1430     <-- banda 0 se va
0x4012AC  addiu v0,zero,5100       <-- con banda 1 aparece 5100
```

Segundo lector:

```
0x4018A0  lw    v0,-18416(s6)
0x4018A4  lw    v1,16(v0)          <-- lectura de la banda
0x4018A8  addiu v0,zero,1
0x4018AC  beq   v1,v0,0x238c       <-- banda 1 salta
```

- `INFERRED`: `5100` como frecuencia de centro en MHz corresponde a 5 GHz, y aparece solo cuando la banda vale 1. Eso encaja con `a : set 11a band` de la Stage 2076A.
- `CONFIRMED`: una ruta compara contra `0` y la otra contra `1`. Son los dos polos del mismo campo.
- `UNKNOWN`: la unidad exacta de `5100`. No hay tabla de canales en este binario que lo confirme.

## 2. La ruta del dispositivo no es un literal

- `REFUTED`: que exista la cadena `/dev/uph_wifi0`. No está en ninguno de los dos binarios.
- `CONFIRMED`: lo que existe es el formato `/dev/uph_%s` en `0x40A7A0`, con un único sitio que lo materializa.
- `CONFIRMED`: la ventana de llamadas alrededor de ese sitio pasa por los stubs de enlace diferido. El slot `0x41B6F0` es `strcpy` según la tabla `DT_JMPREL`, lo que encaja con construir la ruta a partir del nombre de la interfaz.
- `UNKNOWN`: la identidad de los demás slots. Solo cuatro tienen relocación `JUMP_SLOT`; el resto se resuelve por el cargador y su nombre no está en el archivo.

## 3. Stage 2089A — el manejador ioctl no contiene `lw s2,0x10(base)`

La premisa de la wave tenía dos partes. Las dos se midieron.

- `REFUTED`: que exista un símbolo llamado `ath_ioctl`. Hay **18** nombres relacionados (`ath_ioctl_debug`, `ath_ioctl_ethtool`, `ieee80211_ioctl`, `osif_ioctl_create_vap`, y otros) pero ninguno se llama exactamente `ath_ioctl`.
- `CONFIRMED`: el manejador sí se puede ubicar. Partiendo del ancla de la Stage 1980A en `0x5CDC8` y caminando hacia atrás hasta el `addiu sp,sp,-120` que además guarda `ra`, la entrada es `0x5CC58` en las dos familias.

Dentro de ese manejador:

| Medición | WA | XC |
| :--- | ---: | ---: |
| `lw s2,0x10(base)` en el manejador | **0** | **0** |
| Accesos a `0x10` en el manejador | 47 | 47 |
| `lw s2,0x10(base)` en todo el módulo | 6 | 6 |

- `REFUTED`: que el manejador contenga la instrucción que la wave pedía recorrer. No existe.
- `CONFIRMED`: los 47 accesos a `0x10` del manejador usan el registro `s0`, y el prólogo hace `addu s0,a1,zero`. Es decir, miran el **argumento del ioctl**, no el `net_device`.
- `CONFIRMED`: `a0` dentro del manejador se reutiliza como índice de un lazo (`addiu a0,a0,1`). El offset pedido, sumado a `a0` para formar la base, es **ninguno**: el manejador nunca desplaza `a0` para alcanzar un campo `0x10`.
- `CONFIRMED`: las 6 instrucciones `lw s2,0x10(base)` del módulo están fuera del manejador, en `0x184C0`, `0x52E3C`, `0x52F80`, `0xBC5CC`, `0xCE540` y `0xD8D54`, y en XC la cuarta pasa a `0xBC5D0`. Ninguna tiene `a0` como base.

### Los escritores de `0x10`

- `CONFIRMED`: el módulo tiene **2089** instrucciones `sw ...,0x10(base)` por familia.
- `CONFIRMED`: de ellas, **43** tienen la base producida por un `lw` previo, que es la forma que tendría un campo de estructura.
- `UNKNOWN`: cuáles de esas 43 parten de un `net_device`. Se listan como candidatas, no como prueba. El desborde de tamaño de símbolos vecinos impide asignar dueño exacto en todos los casos.

## 4. Lo que queda abierto
- `UNKNOWN`: el escritor del campo `priv+0x10` de la Stage 2077A. Esta etapa no lo nombra.
- `UNKNOWN`: la unidad de `5100` y la tabla de canales asociada.
- `UNKNOWN`: la identidad de los slots de enlace diferido sin relocación `JUMP_SLOT`.
- `UNKNOWN`: cualquier lectura en vivo. No hubo dispositivo.

## 5. Stage 2091A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2088A` | `tools/re/extract_stage2088a_ubntspecd_0x41b8c4_band_readers_and_poll_loop_re.py` y su recibo |
| `2089A` | `tools/re/reconcile_stage2089a_ath_ioctl_a0_to_s2_exact_offset_and_writer.py` y su recibo |
| `2091A` | `tools/verify/record_stage2091a_memorymaster_ingest.py` y su recibo |
| `2092A` | `tests/test_stage2088a_to_2093a_suite.py` |
| `2093A` | `tools/verify/verify_stage2093a_wave175_opencode_gate.py` y su recibo |
