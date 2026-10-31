<!-- doc-head -->
# STAGE 2372A — CFG completo del `ioctl` `0x1E58` y los cuatro manejadores `ku_comm` de estación

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Medido sobre `artifacts/firmware_re_xc_ltu/`. WA y XC coinciden en todo lo reportado.
- Este documento no contiene apellidos.

## 1. Stage 2370A — grafo de bloques básicos

- `CONFIRMED`: **89** instrucciones, **16** bloques básicos, **5** llamadas a `ubnt_poll_ku_comm_*`.
- `CONFIRMED`: el cuerpo es una **cadena comparar-y-ramificar**. Cada `beq` salta a su manejador y el último comparado cae al error.

### 1.1 El mapa 5 a 5

| Comando | Rama | Manejador |
| :--- | :--- | :--- |
| `0xC2145504` | `0x1E7C` | `ku_comm_get_sta_spec_data` |
| `0x40905501` | `0x1E98` | `ku_comm_get_info` |
| `0xC0015502` | `0x1EA4` | `ku_comm_get_stalist` |
| `0xC2145505` | `0x1EB4` | `ku_comm_set_sta_spec_data` |
| `0xC6945503` | `0x1EC0` | `ku_comm_get_stainfo` |

- `CONFIRMED`: **cinco de cinco**, ninguno sin mapear. Las mitades bajas son `0x5501`..`0x5505`, consecutivas, como decía el brief.
- `CONFIRMED`: `0xC2145504` se compara a través de **`a0`**, no de `v1`.

### 1.2 Por qué fallaba antes

Tres defectos míos, en orden:

1. **`addiu rt,rs,imm` copia el valor del registro fuente.** Con `addiu a0,v1,0x5504` el comando pasa a `a0`. Un rastreador que sólo actualiza el destino pierde ese comando.
2. **`addiu rt,zero,imm` es carga inmediata.** Sin esa regla, `0x1EA8` (`addiu v1,zero,-25`) no fijaba `v1` y se arrastraba el valor anterior.
3. **El valor en una rama lo decide la arista de entrada, no la instrucción anterior.** `0x1EA8` está en el camino de fallo, así que en `0x1EB4` —alcanzado desde `0x1E88`— `v1` vale `0xC2145505`, no `-25`.

- `CONFIRMED`: la propagación correcta es por **aristas**, con fusión en los puntos de unión y descarte del registro cuando las entradas discrepan.

### 1.3 La alcanzabilidad de `0x1EB4`, que estaba en duda

```
0x1E74  lui   v1,0xC214
0x1E78  addiu a0,v1,0x5504     ; a0 = 0xC2145504
0x1E7C  beq   a2,a0,->0x1F58   ; cmd == 0xC2145504
0x1E80  addiu v1,v1,0x5505     ; v1 = 0xC2145505
0x1E84  sltu  a0,a2,v1         ; a0 = (cmd < 0xC2145505)
0x1E88  beq   a0,zero,->0x1EB4 ; si cmd >= 0xC2145505
```

- `CONFIRMED`: `0x1E88` **no** compara el comando contra cero, compara el **resultado de `sltu`**. Mi lectura anterior —«`a0` vale `0xC2145504`, nunca es cero, luego `0x1EB4` es inalcanzable»— era **falsa**: en `0x1E84` `a0` se sobrescribe con el booleano.
- `CONFIRMED`: `0x1EB4` **es alcanzable**, y `v1` vale allí `0xC2145505`.

- `UNKNOWN`: ningún rango de instrucciones queda inalcanzable en el grafo; aun así no se afirma nada sobre la alcanzabilidad en tiempo de ejecución de cada comando.

## 2. Stage 2371A — los cuatro manejadores

| Manejador | Entrada | Tamaño | Marco | Copias | Bloqueos |
| :--- | :--- | ---: | ---: | ---: | ---: |
| `get_stalist` | `0x185B8` | 408 | 24 | **0** | **0** |
| `get_stainfo` | `0x18750` | 312 | 40 | **0** | **0** |
| `get_sta_spec_data` | `0x18888` | 276 | 24 | **0** | **0** |
| `set_sta_spec_data` | `0x1899C` | 276 | 24 | **0** | **0** |

- `CONFIRMED`: **1.272** bytes en total, idénticos en WA y XC.
- `CONFIRMED`: **cero** `copy_from_user`, **cero** `copy_to_user`, **cero** `__copy_user` en los cuatro.
- `CONFIRMED`: **cero** `spin_lock`, `mutex`, `atomic` y semáforos en los cuatro.
- `CONFIRMED`: ninguno transporta datos al espacio de usuario. Delegan en rutinas internas del módulo.
- `UNKNOWN`: qué rutina interna hace la entrega, y con qué tamaño. Se miden las llamadas, no sus contratos.

- `CONFIRMED`: el nodo de carácter es **superficie de control**, no de datos: el `read` y el `write` de la tabla devuelven `-22`, y el `ioctl` despacha a funciones que no copian.

## 3. Lo que cambia
- El mapa de comandos deja de tener huecos: **5 de 5**, con la mitad baja alineada.
- `0xC2145504` deja de ser «argumento» y pasa a ser el comando del camino `get_sta_spec_data`.
- Queda corregida mi afirmación de la wave 222 sobre `0x1EB4`: era alcanzable, y el error estaba en leer `a0` como el comando cuando ya contenía un booleano.

## 4. Lo que queda abierto
- `UNKNOWN`: qué rutina interna completa cada `ku_comm`.
- `UNKNOWN`: el texto del directorio de `/proc`.
- `UNKNOWN`: las 7 cadenas sin conversión de los formateadores.
- `UNKNOWN`: `set_rate_override` y `vtable[456]`.

## 5. Stage 2373A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`.

## 6. Artefactos
`extract_stage2370a_uph_0x1e58_cfg_all_5_ku_comm_map_re.py`, `reconcile_stage2371a_uph_4_ku_comm_sta_handlers_re.py`, `record_stage2373a_memorymaster_ingest.py`, `test_stage2370a_to_2375a_suite.py` y `verify_stage2375a_wave222_opencode_gate.py`, cada uno con su recibo.
