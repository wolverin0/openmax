<!-- doc-head -->
# STAGE 2138A — La familia `'U'` en el handler `0x1E58` y el proveedor `0xBBE30` de `umac`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los bytes ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2136A — el handler `0x1E58` cubre cinco comandos, no tres

El encargo pide los comandos `nr=1`, `nr=2` y `nr=3`. La cadena de comparaciones materializa **cinco** constantes, todas de tipo `'U'`:

| Comando | Número | Tamaño | Dirección | Rama |
| :--- | ---: | ---: | :--- | :--- |
| `0x40905501` | 1 | 144 | `write` | `0x1ED0` |
| `0xC0015502` | 2 | 1 | `read_write` | `0x1EF4` |
| `0xC6945503` | 3 | 1684 | `read_write` | `0x1F28` |
| `0xC2145504` | 4 | 532 | `read_write` | `0x1F58` |
| `0xC2145505` | 5 | 532 | `read_write` | `0x1F88` |

- `CONFIRMED`: la familia es `'U'` con números **1, 2, 3, 4 y 5**.
- `REFUTED`: que el handler sólo atienda tres comandos. Atiende cinco.
- `CONFIRMED`: cuatro de las cinco comparaciones tienen su constante fijada por el par `lui`/`addiu` inmediato anterior.
- `UNKNOWN`: la constante de la rama `0x1F88`. El registro que se compara viene de la cota `sltu` de `0x1E84`, y un barrido lineal no puede decidir su valor con la misma certeza. El recibo la marca con `certain=0`.

### La guarda de entrada

```
0x1E60  lw    v0,248(a0)        ; estructura del dispositivo
0x1E64  lw    a0,104(a1)        ; campo del descriptor de fichero
0x1E68  addiu v1,v0,-132
0x1E6C  bne   a0,v1,0x1FAC      ; si no coincide -> -22
```

- `CONFIRMED`: hay una comprobación de coherencia antes de despachar, y su fallo devuelve `-22`.
- `UNKNOWN`: el significado de los campos 248 y 104.

### Forma de cada rama

Las cinco ramas tienen la misma forma:

```
beq   a3,zero,<salida>      ; argumento nulo -> -22
lw    a0,96(v0)             ; receptor privado
jal   0x0                   ; llamada trasladada
addu  a1,a3,zero            ; delay slot: el puntero del usuario
```

- `CONFIRMED`: las cinco ramas cargan el receptor desde `96(v0)` y pasan el argumento del usuario en `a1`.
- `CONFIRMED`: **ninguna** rama carga un registro de longitud antes de la llamada.
- `INFERRED`: por los registros, la llamada transfiere datos entre el privado y el puntero del usuario. La dirección no está probada por el sitio de llamada.
- `UNKNOWN`: el destino de los cinco `jal 0x0`. Son trasladados y su valor es cero en el objeto.

### La estructura de operaciones

- `CONFIRMED`: la palabra `0x1E58` aparece **una vez** en `.data`, en el desplazamiento **`0x230A0`**.
- `CONFIRMED`: los vecinos inmediatos son `0x1E48` en `0x23088` y `0x1E50` en `0x2308C`, que son otros manejadores del mismo bloque.
- `CONFIRMED`: la inscripción del dispositivo de caracteres es una llamada trasladada en **`0x1D98`**, localizada por la relocación contra `register_chrdev_region`.
- `UNKNOWN`: el inicio exacto de la estructura. Sólo se afirma la posición del puntero, no el índice que ocupa.

## 2. Stage 2137A — el proveedor `0xBBE30` y la salida `0xBC2E4`

```
0xBBE28  ori   a0,s1,-6448      ; a0 = s1 | 0xFFFFE6D0
0xBBE2C  addiu a2,a2,0
0xBBE30  jal   0x0              ; llamada trasladada
0xBBE34  addiu a3,zero,1        ; delay slot: a3 = 1
0xBBE38  bne   v0,zero,0xBBE54
0xBBE3C  addu  s0,v0,zero       ; delay slot: s0 = v0
```

- `CONFIRMED`: la llamada recibe `a0` derivado de `s1`, `a2` sin cambios y `a3 = 1` en el delay slot.
- `CONFIRMED`: `s0` toma el valor de retorno en el **delay slot** del salto, así que la asignación ocurre antes de que el salto decida.
- `REFUTED`: que el valor de `s0` provenga de un argumento. Viene de un retorno.
- `UNKNOWN`: el destino del `jal`. Su operando es cero en las dos familias.

### El destino del salto

- `CONFIRMED`: `0xBC2E4` en WA y `0xBC2E8` en XC son el **epílogo común** de `__ol_ath_attach`.
- `CONFIRMED`: el epílogo hace `addu v0,s1,zero`, es decir devuelve el valor acumulado en `s1`.
- `CONFIRMED`: por tanto `bne v0,zero,0xBC2E4` significa "si la llamada falló, devolver `s1`".
- `INFERRED`: `s1` actúa como código de estado de la función. La etapa lo sigue un paso hacia atrás y no reconstruye todas sus asignaciones.

## 3. Lo que queda abierto
- `UNKNOWN`: el destino de los cinco `jal` del handler del kernel y del `jal` de `0xBBE30`.
- `UNKNOWN`: la dirección real de la transferencia en cada rama, porque no hay longitud explícita.
- `UNKNOWN`: la constante exacta de la rama `0x1F88`.
- `UNKNOWN`: el inicio y el índice de la estructura de operaciones en `0x23088`.

## 4. Stage 2139A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 5. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2136A` | `tools/re/extract_stage2136a_uph_0x1e58_ioctl_u_family_1_2_3_re.py` y su recibo |
| `2137A` | `tools/re/reconcile_stage2137a_umac_0xbbe30_s0_provider_and_0xbc2e4_re.py` y su recibo |
| `2139A` | `tools/verify/record_stage2139a_memorymaster_ingest.py` y su recibo |
| `2140A` | `tests/test_stage2136a_to_2141a_suite.py` |
| `2141A` | `tools/verify/verify_stage2141a_wave183_opencode_gate.py` y su recibo |
