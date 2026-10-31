<!-- doc-head: Wave358 P3 — parche ath10k-ct que copia rx_ppdu_end a un anillo acotado expuesto por debugfs, plan de build y formato de registro -->

# STAGE3018A — Parche PPDU-end, plan de build y contrato de registro

Pillar 2, lado kernel. W355 P3 refuto el acceso desde userspace en el ath10k-ct despachado
(sin tracepoint compilado, y pktlog lleva registros del firmware, no el descriptor del host).
Aqui esta el parche minimo, verificado, y el formato que consume lane_2.

Solo trabajo offline de fuente y planificacion: **no se cargo nada en ningun equipo**.

## 1. El parche

| dato | valor |
|---|---|
| fichero | `tools/ground_up/pillar2_kernel/fmx_ppdu_end_ring.patch` |
| tamano | 13978 B, 9 hunks |
| ficheros tocados | Makefile, core.h, debug.c, htt_rx.c |
| ficheros nuevos | fmx_ppdu_end.h, fmx_ppdu_end.c |
| verificacion | copia limpia + `git apply --check` + `git apply`: **OK** |

### Donde se engancha

`htt_rx.c`, funcion `ath10k_htt_rx_amsdu_pop`, justo despues de `rx_desc = (struct htt_rx_desc
*)msdu->data;` y antes del `skb_put`/`skb_pull` que descarta el descriptor. Es el ultimo punto
en el que el `htt_rx_desc` completo sigue en el `skb`.

### Coste cero cuando esta apagado

Se usa una **static key**: con el anillo desactivado la rama se parchea a nop y no se reserva
memoria. Los 256 KiB se piden en el primer `echo 1` y se liberan al descargar el modulo. No hay
coste de cache ni de allocacion en el camino de recepcion mientras esta apagado.

### Tamano

`2048 registros x 128 B = 262144 B = 256 KiB` exactos, que es el tope pedido. Dos entradas de
debugfs: `fmx_ppdu_end/enable` (0644) y `fmx_ppdu_end/records` (0444).

## 2. Correccion de un error mio de W355

En W355 P3 escribi que **la posicion del `ppdu_end` no es un offset fijo** porque el anillo
publica `ppdu_end_offset` en unidades de 4 bytes. **Eso es falso para RX.**

`struct htt_rx_desc` es una **union**, asi que `rx_desc->ppdu_end` esta a un offset fijo de
compilacion, y el propio driver lo usa asi (`htt_rx.c:874`). `ppdu_end_offset` se escribe
unicamente para el anillo **TX** (`htt_tx.c:621`) y no interviene en la recepcion.

Consecuencia practica: el parche accede a `rxd->ppdu_end` directamente y **no** necesita leer
ningun offset del anillo. Si lane_2 implemento algo leyendo `ppdu_end_offset` para RX, esta mal.

## 3. Formato del registro (contrato con lane_2)

Rutas:

```sh
echo 1      > /sys/kernel/debug/ieee80211/phy0/ath10k/fmx_ppdu_end/enable   # armar
echo reset  > /sys/kernel/debug/ieee80211/phy0/ath10k/fmx_ppdu_end/enable   # limpiar
echo 0      > /sys/kernel/debug/ieee80211/phy0/ath10k/fmx_ppdu_end/enable   # desarmar
cat /sys/kernel/debug/ieee80211/phy0/ath10k/fmx_ppdu_end/records            # leer
```

El flujo es **un header de 64 B y despues `count` registros de 128 B**, en orden de captura
(del mas viejo al mas nuevo). Todo little-endian.

### Header (64 B, magic `FPPH` = bytes `48 50 50 46`)

| offset | campo | bytes |
|---|---|---|
| `0x00` | `magic` | 4 |
| `0x04` | `version` | 2 |
| `0x06` | `header_size` | 2 |
| `0x08` | `record_size` | 4 |
| `0x0c` | `capacity` | 4 |
| `0x10` | `count` | 4 |
| `0x14` | `write_idx` | 4 |
| `0x18` | `total_captured` | 8 |
| `0x20` | `flags` | 4 |
| `0x24` | `rsvd[7]` | 28 |

`total_captured` es monotonico: si al releer el header avanzo mas que `count`, hubo registros
sobrescritos por dar la vuelta al anillo.

### Registro (128 B, magic `FPPU` = bytes `55 50 50 46`)

| offset | campo | bytes |
|---|---|---|
| `0x00` | `magic` | 4 |
| `0x04` | `version` | 2 |
| `0x06` | `record_size` | 2 |
| `0x08` | `seq` | 4 |
| `0x0c` | `tsf_timestamp` | 4 |
| `0x10` | `wb_timestamp` | 4 |
| `0x14` | `rsvd0` | 4 |
| `0x18` | `t_ns` | 8 |
| `0x20` | `peer_idx` | 2 |
| `0x22` | `vdev_id` | 2 |
| `0x24` | `info0` | 4 |
| `0x28` | `bb_length` | 2 |
| `0x2a` | `info1` | 2 |
| `0x2c` | `locationing_timestamp` | 1 |
| `0x2d` | `phy_err_code` | 1 |
| `0x2e` | `flags` | 2 |
| `0x30` | `evm[16]` | 64 |
| `0x70` | `rsvd1[4]` | 16 |

Notas de semantica:

- `t_ns` = `wb_timestamp` (us) x 1000 + `locationing_timestamp` x 12.5, en nanosegundos.
- `peer_idx` es un **indice** del firmware (`mpdu_start.info0 & 0x7ff`), no una MAC.
- `vdev_id` vale `0xffff` = **no disponible**: el descriptor no lleva vdev y la firma de
  `amsdu_pop` no lo recibe. Se deja explicito en vez de inventar un 0 que parezca real.
- `evm[16]` son los `evm_p0..p15` crudos, sin interpretar.
- Nunca se guarda una MAC de estacion: la politica del proyecto aplica igual aqui.

Protocolo de lectura: leer 64 B de header, luego `count*128` B; para un snapshot coherente,
releer el header y comparar `total_captured`.

## 4. Build: el repo no tiene SDK

**Estado: `CONFIRMED_ABSENT_IN_REPO`.**

Existe `firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py` y los manifiestos
ImageBuilder de 24.10.0 a 24.10.4, pero **ImageBuilder ensambla paquetes ya compilados y no
compila modulos de kernel desde fuente**. Para este parche hace falta el SDK.

- Necesario: **OpenWrt SDK 24.10.4, target `ath79/generic`** (estos radios son MIPS 24Kc BE).
- Kernel: el uImage de la LAP-120 declara `MIPS OpenWrt Linux-6.6.110`; el SDK debe traer
  exactamente 6.6.110 o el vermagic no cargara.
- Nombre de descarga: `openwrt-sdk-24.10.4-ath79-generic_<toolchain>_musl.Linux-x86_64.tar.zst` — **`INFERRED: el patron es el de las releases de OpenWrt, pero el nombre exacto del toolchain no se puede confirmar offline`**.

Pasos:

```sh
tar --zstd -xf openwrt-sdk-24.10.4-ath79-generic_*.tar.zst && cd openwrt-sdk-*
./scripts/feeds update -a && ./scripts/feeds install -a
cp fmx_ppdu_end_ring.patch package/kernel/ath10k-ct/patches/099-fmx-ppdu-end-ring.patch
make package/kernel/ath10k-ct/clean V=s
make package/kernel/ath10k-ct/compile V=s
ls bin/targets/ath79/generic/packages/kmod-ath10k-ct_*.ipk
```

**Puerta de vermagic:** antes de instalar, comparar `uname -r` del equipo con el kernel del
SDK. Si difieren, el modulo se compila pero no carga. Y el `mac80211.ko` despachado viene de
`backports-6.12.52` (la cadena esta en el propio `.ko`), asi que el SDK tiene que ser el mismo
24.10.4, no otra revision.

## 5. Que falta para que esto sea real

1. Compilar con el SDK (no hecho: no hay SDK en el repo y no se compila aqui).
2. Probar en banco, no en torre.
3. Confirmar en el equipo que `fmx_ppdu_end/records` aparece y que `enable` arma el anillo.

El parche aplica limpio y las comprobaciones estructurales pasan; lo que **no** esta verificado
es que compile, porque para eso hace falta el SDK. Eso queda dicho y no se disfraza.

