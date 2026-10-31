<!-- doc-head: Wave359 P3 — build real del modulo con el parche fmx_ppdu_end usando el SDK oficial de OpenWrt 24.10.4 en WSL -->

# STAGE3019A — Build del módulo Pillar 2 con el SDK oficial

Build real, offline en disco local, en WSL y **fuera del repo**. No se cargó nada en ningún equipo.

## 1. SDK descargado y verificado

| dato | valor |
|---|---|
| fichero | `openwrt-sdk-24.10.4-ath79-generic_gcc-13.3.0_musl.Linux-x86_64.tar.zst` |
| bytes | 208 591 236 |
| sha256 esperado | `0b693ad6…ab52cdec5` |
| sha256 real | `0b693ad6…ab52cdec5` |
| verificación | `sha256sum` contra el `sha256sums` oficial del target — **MATCH** |
| target / kernel | `ath79/generic` / **6.6.110** (de `profiles.json` oficial) |
| vermagic ABI | `35ef4dd36891d37023436baa842fa311` |

El SDK **no** trae el paquete `ath10k-ct`: se instaló desde el feed `base`
(`feeds/base/package/kernel/ath10k-ct`).

## 2. El parche iba al árbol equivocado

El paquete compila **`ath10k-6.10/`** (`PKG_EXTMOD_SUBDIRS:=ath10k$(CT_KVER)`, `CT_KVER="-6.10"`),
no `ath10k/`. El primer intento aplicó el parche sin error… a `ath10k/`, que **nadie compila**.

Consecuencia más grave: `ath10k/` y `ath10k-6.10/` **no son el mismo código** (difieren
`htt_rx.c`, `core.h`, `debug.c`, `Makefile`, `rx_desc.h` y `htt.h`). Mis líneas de W355 y mi
«corrección» de W358 se referían al árbol viejo.

### La corrección que importa

En `ath10k-6.10` **`struct htt_rx_desc` es opaco**: solo tiene `fw_desc`/`pad`. No existe
`rxd->ppdu_end` ni `rxd->mpdu_start`. El compilador lo dijo sin ambigüedad:

```
error: 'const struct htt_rx_desc' has no member named 'ppdu_end'
error: 'const struct htt_rx_desc' has no member named 'mpdu_start'
```

Así que **mi corrección de W358 era falsa**: el acceso es dinámico, vía
`ath10k_htt_rx_desc_get_ppdu_end(hw, rxd)`, exactamente como hace
`ath10k_htt_rx_h_mactime`. W355 tenía razón y W358 la revirtió leyendo el árbol equivocado.
El código ahora usa el accesor y deriva la variante QCA988X justo detrás de la parte común.

## 3. Resultado del build

```sh
nice -n 19 make package/feeds/base/ath10k-ct/compile V=s -j1     # rc=0
```

| dato | construido | despachado |
|---|---|---|
| bytes | 2561928 | 714672 |
| vermagic | `6.6.110 mod_unload MIPS32_R2 32BIT` | `6.6.110 mod_unload MIPS32_R2 32BIT` |
| contiene `fmx_ppdu_end` | **36 apariciones** | 0 |
| secciones `.debug` | 1550820 B | 0 B |
| `.text` | 354336 B | 397392 B |

**El vermagic coincide exactamente**, que es la condición dura para que el módulo cargue en
nuestra imagen (kernel 6.6.110, MIPS32_R2, 32BIT).

### Sobre el tamaño

Nuestro `.ko` pesa 2561928 B y el despachado 714672 B. Descontando los 1550820 B de `.debug` que el
despachado no tiene, queda en **1011108 B** frente a 714672 B. La diferencia restante **no es
comparable**: el módulo despachado salió de la imagen del proyecto, con otra configuración, no
del SDK por defecto. Son comparables en vermagic y en presencia de código, no byte a byte.

`FPPU`/`FPPH` no aparecen en `strings` porque son constantes enteras (`0x46505055`,
`0x46505048`), no cadenas. Es esperado y no indica nada.

## 4. Lo que no se pudo cerrar

- **No se pudo extraer el `.ko` del `.ipk`**: no hay `ar` en la distro y el contenedor no
  responde a la firma ar clásica (detectado: `gzip`). El `.ko` verificado es el que produce
  el build, que es el mismo que el paquete instala.
- **No se cargó nada**: cargar el módulo y verificar el anillo de debugfs en runtime queda
  pendiente y prohibido en esta wave.

## 5. Artefactos

- `artifacts/ground_up/pillar2_build/ath10k_core.fmx_ppdu_end.ko` — módulo construido
- `artifacts/ground_up/pillar2_build/kmod-ath10k-ct_*.ipk` — paquete (regular y smallbuffers)
- `artifacts/ground_up/pillar2_build/manifest.json` — hashes y verificación

El SDK **no se copia al repo**: vive en `~/fmx_sdk`. Lo descargado son 208 MB y es reproducible
con el `sha256` anotado.

