<!-- doc-head -->
# STAGE 2162A — Los cinco manejadores `ku_comm` y el tamaño de `alloc_netdev_mq`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2160A — los cinco manejadores existen y son idénticos en las dos familias

| Tag | Símbolo | Entrada | Tamaño | Llamadas |
| :--- | :--- | :--- | ---: | ---: |
| U1 | `ubnt_poll_ku_comm_get_info` | `0x17024` | 5524 | 22 |
| U2 | `ubnt_poll_ku_comm_get_stalist` | `0x185B8` | 408 | 11 |
| U3 | `ubnt_poll_ku_comm_get_stainfo` | `0x18750` | 312 | 9 |
| U4 | `ubnt_poll_ku_comm_get_sta_spec_data` | `0x18888` | 276 | 6 |
| U5 | `ubnt_poll_ku_comm_set_sta_spec_data` | `0x1899C` | 276 | 6 |

- `CONFIRMED`: los cinco símbolos existen en `.symtab` con tamaño declarado, y las entradas y tamaños son iguales en WA y XC.
- `CONFIRMED`: entre los cinco suman **54 llamadas** por familia.
- `REFUTED`: que alguno llame directamente a `copy_from_user` o a `copy_to_user`. El módulo **no importa** ninguno de esos nombres: la lista de símbolos vigilados está vacía.
- `CONFIRMED`: de las llamadas, la única con nombre resuelto es `ubnt_poll_host_sta_hash_find`, dentro de U3. El resto son destinos dentro de `.text` sin símbolo, es decir ayudantes locales del propio módulo.
- `UNKNOWN`: los nombres de esos ayudantes locales. No están en la tabla.

## 2. Lo que el programa de usuario realmente emite

- `CONFIRMED`: de las cinco palabras de comando, **sólo `0x40905501` aparece en `ubntspecd`**, en las dos familias.
- `CONFIRMED`: `0xC0015502`, `0xC6945503`, `0xC2145504` y `0xC2145505` **no están** en el binario de usuario.
- `INFERRED`: `ubntspecd` sólo ejerce U1. Las otras cuatro entradas existen en el kernel pero no tienen emisor en este programa.
- `UNKNOWN`: si otro programa del firmware emite U2 a U5. La búsqueda se limitó a `ubntspecd`.

## 3. Stage 2161A — los argumentos del asignador

| Registro | Origen medido | Lectura |
| :--- | :--- | :--- |
| `a0` | `ori a0,s1,-6448` | derivado de `s1`, **no** es una constante |
| `a1` | `addiu a1,a1,0` | sin cambio |
| `a2` | `addiu a2,a2,0`, relocado contra `ether_setup` | el puntero de inicialización |
| `a3` | `addiu a3,zero,1` en el delay slot | 1 |

- `REFUTED`: que el tamaño privado sea una constante estática. `a0` se construye a partir de `s1` en ejecución, así que el valor no está en el objeto.
- `CONFIRMED`: el tercer argumento es `ether_setup`, resuelto por relocación, y el cuarto vale 1.
- `UNKNOWN`: el valor numérico de `s1` y, por tanto, el tamaño del bloque.

### Quién recibe un puntero derivado

- `CONFIRMED`: **ninguna** de las llamadas de la ventana `0xBBE00..0xBC300` recibe un puntero formado por copia directa desde `s0`, `s7` o `s2`.
- `CONFIRMED`: la ventana mantiene sus **49** símbolos distintos, ya medidos en la Stage 2149A.
- `INFERRED`: los campos `+0x1E1B4` y `+0x1E1B8` se escriben con **almacenes directos**, no delegando en un callee. Eso concuerda con la Stage 2125A, que encontró las dos únicas escrituras con esos desplazamientos dentro de la propia función.
- `REFUTED`: que exista una función de inicialización que reciba el bloque y rellene la tabla. No hay tal destinatario.

## 4. Lo que queda abierto
- `UNKNOWN`: los nombres de los ayudantes locales de los cinco manejadores.
- `UNKNOWN`: el tamaño privado que pide el asignador, que se calcula en ejecución.
- `UNKNOWN`: quién más emite U2 a U5 fuera de `ubntspecd`.
- `UNKNOWN`: el destino de `vtable[456]`, que sigue llenándose en ejecución.

## 5. Stage 2163A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2160A` | `tools/re/extract_stage2160a_uph_ku_comm_5_handlers_dissection_re.py` y su recibo |
| `2161A` | `tools/re/reconcile_stage2161a_umac_alloc_netdev_mq_size_and_vtable_init_re.py` y su recibo |
| `2163A` | `tools/verify/record_stage2163a_memorymaster_ingest.py` y su recibo |
| `2164A` | `tests/test_stage2160a_to_2165a_suite.py` |
| `2165A` | `tools/verify/verify_stage2165a_wave187_opencode_gate.py` y su recibo |
