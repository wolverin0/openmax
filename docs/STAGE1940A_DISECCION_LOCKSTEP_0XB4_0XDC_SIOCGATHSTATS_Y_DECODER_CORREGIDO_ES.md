<!-- doc-head -->
*STAGE1940A — Disección del lockstep 0xb4/0xdc en SIOCGATHSTATS y decodificador corregido*
# STAGE 1940A — Lockstep 0xb4/0xdc

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0` en los tres recibos.
- Todo es análisis estático sobre `athbox` y `umac.ko` ya extraídos. No se cargó ningún módulo, no se ejecutó ningún binario y no hubo red.
- Etiquetas `CONFIRMED`, `INFERRED`, `UNKNOWN` y `REFUTED`. Este documento no contiene apellidos.

## 1. Stage 1938A — el binario de usuario
- `CONFIRMED`: `athbox` de WA y de XC son **byte-idénticos**: **202920** bytes, sha256 `c1d37671…`.
- `CONFIRMED`: es un **ET_EXEC MIPS big-endian** con **8 program headers** y **sin tabla de secciones**; el lector de objetos relocables no sirve y hubo que leerlo por segmentos.
- `CONFIRMED`: las dos etiquetas existen, una vez cada una: `%10u tx failed 'cuz no tx buffer (data)` en VA **0x4177dc** y `%10u tx failed 'cuz xmit filtered` en VA **0x4178cc**.
- `CONFIRMED`: el mismo bloque athstats imprime los contadores verdaderos `ast_be_nobuf`, `ast_tx_nobuf`, `ast_tx_buf_count`, `ast_tx_packets`, `ast_tx_mgmt` y `ast_tx_xretries`, entre las VA **0x196b4** y **0x1975c**.

## 2. Stage 1938A — tres pruebas de referencia negativas
- `CONFIRMED`: **0** pares `lui`+`addiu` referencian las dos etiquetas.
- `CONFIRMED`: **0** palabras literales de 32 bits contienen sus direcciones.
- `CONFIRMED`: **6** cargas relativas a `$gp` caen en el rango, pero sin el valor real de `gp` no son atribuibles; se reportan como heurística, no como prueba.
- `UNKNOWN`: por tanto el **mapeo etiqueta→offset del applet no se resolvió**. El binario construye esas direcciones de una forma que no es `la`, no es puntero literal y no es una carga `gp` identificable.

## 3. Stage 1938A — el lado kernel
- `CONFIRMED`: `SIOCGATHSTATS` es **0x89f0** y se despacha en `umac.ko` en **0x5cd20** (WA) y **0xbcc5c** (XC).
- `CONFIRMED`: el caso cae en **0x5cdc8** (WA) y **0xbccb0** (XC).
- `CONFIRMED`: el caso escribe los offsets **0x110c**, **0x1110**, **0x1114** y un bloque de **16** bytes en **0x1118**, y hace **19** llamadas por vtable.
- `CONFIRMED`: el cuerpo contiene dos candidatos de tamaño de copia, **0x1200** y **0x1210**, en ambas familias.
- `INFERRED`: el tamaño real es **0x1210** (4624) porque es el único que cubre el bloque parcheado hasta 0x1127; el de 0x1200 también lo cubre, así que la inferencia se apoya en el orden de las instrucciones, no en una traza.

## 4. Stage 1938A — el veredicto del lockstep
- `REFUTED`: la hipótesis de un **desajuste de layout usuario/kernel**. Ambas familias copian la misma estructura, con los mismos candidatos de tamaño y los mismos offsets parcheados. No hay divergencia de layout entre WA y XC.
- `INFERRED`: la explicación que queda es un **alias de contadores**: 0xb4 y 0xdc están dentro de los primeros 256 bytes del mismo blob y **no** son campos que el ioctl parchee; si ambos leen el mismo contador de paquetes transmitidos, avanzan juntos.
- `UNKNOWN`: qué campo del kernel ocupa 0xb4 y cuál 0xdc. La función que llena la estructura no se localizó.

## 5. Stage 1939A — decodificador corregido
- `CONFIRMED`: el decodificador debe **rechazar 0xb4 y 0xdc** como contadores de descarte.
- `CONFIRMED`: debe exigir un buffer de al menos el tamaño que copia el ioctl y tratar **0x110c..0x1127** como región parcheada en cada lectura, no como almacenamiento estable.
- `CONFIRMED`: debe aceptar solo etiquetas `ast_*` del bloque athstats como contadores de descarte.
- `UNKNOWN`: el offset de los **6** contadores verdaderos. La especificación los lista como `unresolved_offset` y se declara **PARTIAL**; no inventa números.
- `INFERRED`: una especificación parcial pero honesta es más útil que un mapa completo inventado, porque impide volver a leer 0xb4 como pérdida de buffer.

## 6. Stage 1941A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax` y `source_agent=opencode-session`.
- `CONFIRMED`: la lectura de ida y vuelta por `list_claims` devolvió los **3** con estado `candidate`.

## 7. Lo que no se prueba
- `UNKNOWN`: el campo del kernel en 0xb4 y en 0xdc.
- `UNKNOWN`: el mapeo etiqueta→offset dentro del applet.
- `UNKNOWN`: el offset de `ast_be_nobuf` y del resto de contadores verdaderos.
- `UNKNOWN`: el tamaño de copia exacto, que queda en dos candidatos.
- `UNKNOWN`: cualquier lectura en vivo. No se tocó ningún equipo.

## 8. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1938A` | `tools/re/extract_stage1938a_athbox_siocgathstats_0xb4_0xdc_lockstep_re.py` y su recibo |
| `1939A` | `tools/re/reconcile_stage1939a_corrected_siocgathstats_decoder_spec.py` y su recibo |
| `1941A` | `tools/verify/record_stage1941a_memorymaster_ingest.py` y su recibo |
| `1942A` | `tests/test_stage1938a_to_1943a_suite.py` |
| `1943A` | `tools/verify/verify_stage1943a_wave150_opencode_gate.py` y la compuerta de la wave |
