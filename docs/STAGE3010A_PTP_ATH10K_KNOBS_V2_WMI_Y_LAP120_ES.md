<!-- doc-head: Wave353 P2b — cierre de los 3 UNKNOWN, tabla WMI de PtP corto y ruta de driver LAP-120 (RE offline) -->

# STAGE3010A — Knobs PtP ath10k v2: UNKNOWN resueltos, WMI y LAP-120

Continuacion de STAGE3009A. Sigue siendo **RE estatico offline**: no se ejecuto nada en equipos.
Objetivo: cerrar los tres `UNKNOWN` de v1 y extender la tabla a los parametros WMI que importan
en un PtP corto, incluida la ruta de driver de la LAP-120 (AP de Panel1).

## 1. Los tres UNKNOWN de v1

### `fq_flow_limit` — v1 UNKNOWN → v2 **REFUTED**

Se enumero **la tabla completa** de nombres del debugfs `aqm` de `mac80211.ko`. Los nodos
escribibles son exactamente tres:

``fq_memory_limit`, `fq_limit`, `fq_quantum``

y los de solo lectura: `fq_flows_cnt`, `fq_backlog`, `fq_overlimit`, `fq_overmemory`,
`fq_collisions`, `fq_memory_usage`. **`fq_flow_limit` no aparece.** No es un hueco de
busqueda: la tabla esta entera y el nombre no esta. El limite equivalente que si existe es
`fq_limit`.

Para lane_3: usar `fq_limit`. Pedir `fq_flow_limit` fallaria al abrir el fichero.

### `BQL (limit_max / hold_time / limit)` — v1 UNKNOWN → v2 **CONFIRMED**

BQL **si** se pudo resolver, y no desde los modulos: desde el propio kernel de la canaria.
`immutable-prefix.bin` es un uImage (`27051956`, comp=lzma, arch=MIPS, `MIPS OpenWrt
Linux-6.6.110`). Descomprimido da 8860479 B y contiene los handlers:

- `bql_show_limit_max`
- `bql_set_limit_max`
- `bql_show_hold_time`
- `bql_set_hold_time`

`limit_max` y `hold_time` tienen handler de **escritura**; la superficie es la conocida:
`/sys/class/net/<dev>/queues/tx-*/byte_queue_limits/{limit,limit_max,hold_time}`. El
**default sigue UNKNOWN**: lo fija el codigo del kernel y no aparece como cadena.

### `ack_timeout` — v1 UNKNOWN → v2 **REFUTED**

Cero apariciones de `ack_timeout` en `ath10k_core.ko`, `mac80211.ko` y `cfg80211.ko`. En el
kernel 6.6.110 las dos apariciones son `tcp_syn_ack_timeout`, un sysctl de TCP que no tiene
nada que ver. El timing ACK/CTS se calcula en mac80211 (`ieee80211_rts_get`,
`ieee80211_ctstoself_get`), y la unica palanca del driver es `set-coverage-class`, que
**rechaza** configuraciones cuyo slot time derivado no sea 9 o 20 us:

> `failed to set coverage class: expected slot time of 9 or 20us in HW register`

Esa frase es la prueba de que el ACK timeout no es un knob: es una consecuencia.

## 2. Parametros WMI relevantes para un PtP corto

| parametro WMI | selector | categoria | exposicion ath10k-ct | superficie de usuario | evidencia en el driver |
|---|---|---|---|---|---|
| `WMI_10X_VDEV_PARAM_RTS_THRESHOLD` | 0x1 | RTS threshold | CONFIRMED | iw dev <dev> set rts <n> (nl80211) | `0x6be08` mac vdev %d recalc rts/cts  use-cts-prot: %d |
| `WMI_10X_VDEV_PARAM_FRAGMENTATION_THRESHOLD` | 0x2 | frag threshold | UNKNOWN | sin superficie encontrada | sin cadena |
| `WMI_10X_VDEV_PARAM_SLOT_TIME` | 0x7 | slot time (y por tanto ack/cts timeout) | CONFIRMED | no directa: lo fija el driver desde ERP/coverage | `0x6de2c` mac vdev %d slot_time %d |
| `WMI_10X_VDEV_PARAM_ENABLE_RTSCTS` | 0x2b | CTS protection / RTS-CTS enable | CONFIRMED | indirecta via proteccion de mac80211 y coverage | `0x6bde0` mac vdev %d cts_protection %d val: %d |
| `WMI_10X_PDEV_PARAM_AC_AGGRSIZE_SCALING` | 0xe | tx aggregation size | CONFIRMED | htt_max_amsdu_ampdu (debugfs) para los limites | `0x77588` htt h2t aggr cfg msg amsdu %d ampdu %d |
| `WMI_10X_PDEV_PARAM_BURST_DUR` | 0x28 | burst / txop duration | CONFIRMED_INTERNAL | sin superficie de usuario encontrada | `0x6e858` failed to disable burst: %d |
| `WMI_10X_PDEV_PARAM_BURST_ENABLE` | 0x29 | burst enable | CONFIRMED_INTERNAL | sin superficie de usuario encontrada | `0x6e858` failed to disable burst: %d |
| `WMI_10X_PDEV_PARAM_TXPOWER_LIMIT2G` | 0x3 | tx power 2.4 GHz | CONFIRMED | iw dev <dev> set txpower | `0x6c1c4` mac txpower 2g: %d, 5g: %d |
| `WMI_10X_PDEV_PARAM_TXPOWER_LIMIT5G` | 0x4 | tx power 5 GHz | CONFIRMED | iw dev <dev> set txpower | `0x6c1c4` mac txpower 2g: %d, 5g: %d |
| `WMI_10X_PDEV_PARAM_TXPOWER_SCALE` | 0x5 | tx power scale | UNKNOWN | sin superficie de usuario encontrada | sin cadena |

**Aviso sobre los selectores.** No salen de `firmware-2.bin`: ese binario no contiene nombres
WMI. Salen del enum que ya vive en `firmware_knob_candidates.json` (trabajo previo del repo), y
asi se declara en el artefacto. Lo que si es de esta wave es la columna de **exposicion en el
driver**, sacada de cadenas con offset en `ath10k_core.ko`.

Dos filas quedan `UNKNOWN` a proposito: **frag threshold** y **txpower scale** no tienen cadena
ni simbolo que los fije en este build. Declararlas seria suponer.

## 3. La ruta de driver de la LAP-120

| pieza | valor | estado |
|---|---|---|
| kernel | MIPS OpenWrt Linux-6.6.110, uImage lzma, load `0x80060000` | CONFIRMED |
| kernel descomprimido | 8860479 B, sha256 d369bc6e00253cf8 | CONFIRMED |
| mac80211.ko | 829464 B, sha256 19a8fde6c6e5efbe | CONFIRMED |
| ath10k_core.ko | 714672 B, sha256 1ef8144f569a84bb | **INFERRED** |
| firmware | 204796 B, cabecera `QCA-ATH10K` | CONFIRMED |
| board data | 2116 B | CONFIRMED |

**La salvedad que importa:** el `ath10k_core.ko` **no esta en los volcados de la canaria**. Se
reutiliza el build ath10k-ct de OpenWrt 24.10.4 que si esta en artefactos, asi que la columna de
driver para la LAP-120 es `INFERRED`, no leida de su propio dump. El kernel y el `mac80211.ko`
si son suyos.

## 4. Correccion al supuesto de partida

El dispatch pedia leer los WMI desde `firmware-5.bin`. **Ese fichero no existe en el repo.** El
arbol que despacha OpenWrt para QCA988X hw2.0 es:

- `firmware-2.bin` — 204796 B, cabecera ASCII `QCA-ATH10K`
- `board.bin` — 2116 B

`firmware-5.bin` pertenece a otras familias de chip (QCA9887/9984 y posteriores), no a esta.
Por eso los ids WMI se toman del enum del repo y la tabla declara esa procedencia en vez de
fingir que salen del binario.

## 5. Recuento

De los 3 `UNKNOWN` de v1: **2 quedan REFUTED con evidencia y 1 pasa a CONFIRMED**.
10 filas WMI: 8 con exposicion confirmada, 2 `UNKNOWN` declarados.

Artefacto: `artifacts/autoresearch/wave353_ptp_knob_settability_v2.json` (v1 intacto).
El kernel descomprimido **no se guarda**: son 8.8 MB derivados y reproducibles en segundos
desde el uImage. Queda su sha256 (`d369bc6e00253cf88c6e90dcb6051b2ceff75bcf93f176d4abacc8fcc3cff133`) y la receta en el artefacto, que es
lo que permite verificar que la descompresion es la misma.

