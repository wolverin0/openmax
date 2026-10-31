<!-- doc-head: Stage 1371A - regulatory.db usa la magia RGDB y no se pudo decodificar (bandas por pais UNKNOWN), firmware-5.bin ausente del rootfs, y el techo de frecuencias compilado en los modulos 6.6.110 es 5925 MHz sin ningun literal 6035 -->
# Stage 1371A — Límites de frecuencia: regdb y tabla de canales ath10k

- **Regdb**: [`stage1368a_wa_regulatory_db_and_6035mhz_superchannel_audit.json`](../artifacts/verification/stage1368a_wa_regulatory_db_and_6035mhz_superchannel_audit.json)
- **Módulos**: [`stage1369a_openwrt_ath10k_5ghz_channel_table_bounds.json`](../artifacts/verification/stage1369a_openwrt_ath10k_5ghz_channel_table_bounds.json)
- **Auditoría**: [`stage1370a_waves50_to_54_receipt_ledger.json`](../artifacts/verification/stage1370a_waves50_to_54_receipt_ledger.json)
- **Alcance**: offline estático. No se escribe ninguna imagen ni se contacta ningún equipo.

## 1. Lo que hay en el rootfs de las cuatro imágenes

| Fichero | Placas | Bytes | Idéntico | Estado |
| :--- | :-: | -: | :-: | :--- |
| `lib/firmware/regulatory.db` | 4/4 | **6.232** | sí | presente, **no decodificado** |
| `.../QCA988X/hw2.0/board.bin` | 4/4 | **2.116** | sí | presente |
| `.../QCA988X/hw2.0/firmware-5.bin` | **0/4** | — | — | **ausente** |

El firmware del QCA988X **no viaja en la imagen factory**. Eso ya limita lo que se puede afirmar:
la lista de bandas que el chip obedece la entrega el firmware, y aquí no está.

## 2. `regulatory.db`: presente, pero con otro formato

| Medida | Valor |
| :--- | :--- |
| magia | **`RGDB`** (no `REGD`) |
| versión declarada | **20** |
| tamaño | 6.232 B en las 4 imágenes, idéntico |
| registros de país que validan | **175** y ahí se rompe |
| ¿cierra la tabla por aritmética? | **no** |
| estructuras de rango de frecuencia plausibles en todo el fichero | **0** |

El formato mainline `REGD` tiene cabecera reconocible y una tabla de países que cierra exactamente en el
primer offset de reglas. Aquí la magia es otra, la tabla no cierra y un barrido del fichero completo no
encuentra **ni una** estructura `{inicio, fin, ancho, ganancia}` plausible.

**Conclusión etiquetada:** las bandas por país de `regulatory.db` son **`UNKNOWN`** en esta etapa.
No se afirma ni que AR/US/00 permitan 6035 ni que lo prohíban: no se pudo leer. Cualquier tabla de
bandas que se publicase a partir de estos bytes sería inventada.

## 3. Un obstáculo propio que hay que declarar

El lector SquashFS del proyecto **falla en todo fichero que ocupa más de un bloque de datos**. Está
medido, no supuesto: se buscó en la imagen entera una posición que satisficiera la cadena de tamaños que
declara el inodo y **no existe ninguna**. `ath10k_core.ko` ocupa 3 bloques y `cfg80211.ko` 2; los
ficheros pequeños (hasta 256 KiB, o en fragmento) se leen bien, y por eso las waves anteriores no lo
habían visto.

Solución aplicada, con procedencia explícita: los módulos se toman de
`artifacts/verification/stage117a_build/stock.tar` y se **comprueba que cada tamaño coincide con el
`file_size` que el inodo de la imagen declara**:

| Módulo | `file_size` del inodo | Tamaño en el tar | ¿Coincide? |
| :--- | -: | -: | :-: |
| `ath10k_core.ko` | 600.808 | **600.808** | **sí** |
| `cfg80211.ko` | 392.132 | **392.132** | **sí** |
| `mac80211.ko` | 815.640 | **815.640** | **sí** |

La coincidencia de los tres es la evidencia de que es el mismo artefacto; el `sha256` queda en el
recibo. No se presenta como una lectura directa de la imagen.

## 4. El techo de frecuencias compilado

Se comprobó la presencia de cada frecuencia central canónica de 5 GHz/6 GHz (5000 a 5925, paso 5 MHz)
como `u32` y como `u16` dentro del módulo.

| Medida | `ath10k_core.ko` |
| :--- | -: |
| frecuencias canónicas presentes | **85** de 186 |
| frecuencia más alta presente | **5925 MHz** |
| literales `6035` | **0** |
| literales `6100` | **0** |
| valores presentes por encima de 5925 | **5925** (y ninguno más) |
| ¿llega a 6100? | **no** |

`cfg80211.ko` llega a 5910 y tampoco contiene el literal. El techo medido en el código de los módulos
es **5925 MHz**.

## 5. La respuesta a la pregunta de 6035 MHz

Con lo medido, en este orden:

1. **`regulatory.db` no permite afirmar nada** sobre 6035: no se pudo decodificar (`UNKNOWN`).
2. **El driver no lleva ninguna entrada para 6035**: cero literales en `ath10k_core.ko`, y el máximo
   compilado es 5925.
3. Por tanto **6035 no se habilita cambiando la base regulatoria**: aunque un regdb permitiese la
   banda, el módulo no tiene el canal. No es un problema de `regd` ni de "superchannel" en
   `mac80211.ko`, que tampoco lo contiene.
4. **`UNKNOWN` final**: la lista real de canales del QCA988X la entrega `firmware-5.bin`, que **no está
   en la imagen**. Sin ese fichero, o sin leer `iw phy` en una placa, no se puede cerrar la pregunta
   del todo.

Lo que sí queda cerrado es lo que **no** funciona: no hay atajo por base regulatoria.

## 6. Auditoría 1338A..1367A

**30 números de etapa, 19 recibos, 11 etapas sin recibo** (4 con documento o test propio, 7 sin nada).
**2 recibos declaran dispositivos vivos** y 12 contienen marcadores de runtime; 6 no declaran clase de
evidencia. Coincidencia de etapa declarada con el nombre del fichero: **0 desajustes**.

## 7. Huecos

- **CONFIRMED** — ausencia de `firmware-5.bin`, presencia e identidad de `regulatory.db` y `board.bin`,
  y que no hay literal 6035 en los módulos.
- **UNKNOWN** — el layout de `regulatory.db` y, con él, todas las bandas por país.
- **UNKNOWN** — la lista de canales del firmware del QCA988X.
- **Límite conocido** — los módulos vienen de un tar cotejado por tamaño, no de leer sus bloques en la
  imagen.
- **No intentado** — arrancar una placa y leer `iw phy`, `iw reg get` o `dmesg` del ath10k.
