<!-- doc-head: Wave355 P3 — acceso a rx_ppdu_end (EVM/locationing) desde userspace en ath10k-ct OpenWrt 24.10.4, RE offline -->

# STAGE3014A — Acceso a PPDU end: layout, vias de userspace y punto minimo de parche

Pillar 2. RE estatico offline sobre el `ath10k_core.ko` despachado en OpenWrt 24.10.4.
Pregunta: **se puede leer `evm_p0..p15` y `locationing_timestamp` desde userspace sin parchear
el kernel**, y si no, donde esta el punto minimo de parche.

## 0. Un limite que condiciona todo

El modulo **no tiene `.BTF` ni `.debug_info`**. Sin esas secciones el binario no guarda los
offsets de las structs, asi que ningun offset se puede leer del `.ko` despachado. Lo unico
honesto es confirmarlos contra la fuente del arbol y declarar ese nivel de evidencia. Todo lo que
sigue esta separado por nivel.

## 1. Layout: CONFIRMADO contra la fuente, UNKNOWN contra el binario

Fuente exacta: `tools/research/srccache/ath10k-ct/ath10k/rx_desc.h`.

| offset | campo | bytes | struct |
|---|---|---|---|
| `0x00` | `evm_p0` | 4 | `rx_ppdu_end_common` |
| `0x04` | `evm_p1` | 4 | `rx_ppdu_end_common` |
| `0x08` | `evm_p2` | 4 | `rx_ppdu_end_common` |
| `0x0c` | `evm_p3` | 4 | `rx_ppdu_end_common` |
| `0x10` | `evm_p4` | 4 | `rx_ppdu_end_common` |
| `0x14` | `evm_p5` | 4 | `rx_ppdu_end_common` |
| `0x18` | `evm_p6` | 4 | `rx_ppdu_end_common` |
| `0x1c` | `evm_p7` | 4 | `rx_ppdu_end_common` |
| `0x20` | `evm_p8` | 4 | `rx_ppdu_end_common` |
| `0x24` | `evm_p9` | 4 | `rx_ppdu_end_common` |
| `0x28` | `evm_p10` | 4 | `rx_ppdu_end_common` |
| `0x2c` | `evm_p11` | 4 | `rx_ppdu_end_common` |
| `0x30` | `evm_p12` | 4 | `rx_ppdu_end_common` |
| `0x34` | `evm_p13` | 4 | `rx_ppdu_end_common` |
| `0x38` | `evm_p14` | 4 | `rx_ppdu_end_common` |
| `0x3c` | `evm_p15` | 4 | `rx_ppdu_end_common` |
| `0x40` | `tsf_timestamp` | 4 | `rx_ppdu_end_common` |
| `0x44` | `wb_timestamp` | 4 | `rx_ppdu_end_common` |
| `0x48` | `locationing_timestamp` | 1 | `rx_ppdu_end_qca988x` |
| `0x49` | `phy_err_code` | 1 | `rx_ppdu_end_qca988x` |
| `0x4a` | `flags` | 2 | `rx_ppdu_end_qca988x` |
| `0x4c` | `info0` | 4 | `rx_ppdu_end_qca988x` |
| `0x50` | `bb_length` | 2 | `rx_ppdu_end_qca988x` |
| `0x52` | `info1` | 2 | `rx_ppdu_end_qca988x` |

Total calculado: **84 bytes = 21 dwords**, que coincide con lo que afirma el doc STAGE348A
(84 B / 21 dwords). Los 16 `evm_p*` ocupan 0x00..0x3f, `tsf_timestamp` 0x40, `wb_timestamp`
0x44, y la cola de QCA988X 0x48..0x53.

Dos precisiones que el doc STAGE348A no tiene:

1. **El nombre `rx_ppdu_end_v1` no existe** en este arbol. El descriptor es
   `struct htt_rx_desc`, con un miembro `struct rx_ppdu_end ppdu_end`, y `rx_ppdu_end` es la
   union de variantes por chip. Para QCA988X la pareja es `rx_ppdu_end_common` +
   `rx_ppdu_end_qca988x`. El layout es correcto; el nombre no.
2. **La posicion del ppdu_end no es un offset fijo.** El anillo publica `ppdu_end_offset`, y el
   propio `htt.h` avisa de que esos offsets estan **en unidades de 4 bytes**. Cualquier
   extractor que asuma un desplazamiento fijo desde el inicio del descriptor se rompe en cuanto
   cambie la configuracion del anillo.

## 2. Userspace sin parche: REFUTADO

Ninguna de las dos vias posibles entrega el descriptor:

### Tracepoint `ath10k_htt_rx_desc`

**0 apariciones en el modulo.** El tracepoint no esta compilado en este `.ko`, asi que tracefs
no tiene nada que habilitar. No es que este desactivado: no existe en el build.

### pktlog por debugfs

`pktlog_filter` **si** existe (cadena en `0x717cc`; la fuente lo crea en `ar->debug.debugfs_phy`).
Ruta y comandos exactos:

```sh
mount -t debugfs none /sys/kernel/debug
echo 0x1 > /sys/kernel/debug/ieee80211/phy0/ath10k/pktlog_filter   # ATH10K_PKTLOG_RX
cat  /sys/kernel/debug/ieee80211/phy0/ath10k/pktlog_filter        # leer filtro activo
echo 0x0 > /sys/kernel/debug/ieee80211/phy0/ath10k/pktlog_filter   # desactivar
```

Bits del filtro (`ath10k-ct/debug.h`): `RX=0x01`, `TX=0x02`, `RCFIND=0x04`, `RCUPDATE=0x08`,
`DBG_PRINT=0x10`, `ANY=0x1f`.

**Pero no resuelve la pregunta.** pktlog transporta registros que genera el **firmware**
(tasa, longitud, resumen por paquete). El bloque `rx_ppdu_end` lo escribe el **host** en el
anillo de recepcion, y el firmware no lo ve. Por eso pktlog no puede contener `evm_p0..p15` ni
`locationing_timestamp`: no son datos que pasen por ahi.

Conclusion del item: **sin parche no hay acceso**. Ni tracepoint ni pktlog.

## 3. Punto minimo de parche: CONFIRMADO (ubicacion)

| dato | valor |
|---|---|
| funcion | ``ath10k_htt_rx_amsdu_pop()`() |
| fichero | `drivers/net/wireless/ath/ath10k/htt_rx.c` |
| linea de la funcion | [291, 1588] |
| enganchar antes de | `skb_pull(msdu, offsetof(struct htt_rx_desc, msdu_payload))` |
| linea del pull | [317] |

En ese punto el `skb` todavia lleva el `htt_rx_desc` completo; el `skb_pull` de la linea
siguiente descarta el descriptor y con el el `ppdu_end`. Es el ultimo instante util.

### Tres avisos que ahorran una compilacion fallida

1. **No se puede enganchar en binario.** `ath10k_htt_rx_amsdu_pop` fue **inlinada**: no existe
   como simbolo en el `.ko` despachado. El parche tiene que ser de fuente y recompilar.
2. **El header del proyecto no compila contra este arbol.**
   `firmware/openwrt/common/fmx_pb021_ppdu_evm_ranging_extractor.h` usa
   `hw->rx_desc_ops->rx_desc_msdu_payload_offset`, y ni `rx_desc_ops` ni
   `rx_desc_msdu_payload_offset` existen en este ath10k-ct: el pull real es
   `offsetof(struct htt_rx_desc, msdu_payload)`. Hay que ajustar el header antes de nada.
3. **El driver solo lee `tsf_timestamp` del ppdu_end** (linea [874], dentro de
   `ath10k_htt_rx_h_mactime`). `evm_p*` y `locationing_*` no se leen en ningun sitio, y por eso
   no hay copia en ningun lado: no es que esten ocultos, es que nadie los toca.

## 4. Resumen por item

| item | estado |
|---|---|
| 1 layout 84 B / 21 dwords | **CONFIRMED_SOURCE_LEVEL** (binario: UNKNOWN) |
| 2 userspace sin parche | **REFUTED** |
| 3 punto minimo de parche | **CONFIRMED_LOCATION** |

sin parche no hay EVM ni locationing desde userspace en este build

Camino mas corto: parche de fuente en `ath10k_htt_rx_amsdu_pop` antes del `skb_pull`, copiando
el bloque a un ring y publicandolo por debugfs. Bloqueante previo: el header existente.

Artefacto: `artifacts/autoresearch/wave355_pillar2_ppdu_access.json`.

