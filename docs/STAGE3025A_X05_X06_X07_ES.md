<!-- doc-head: Stage 3025A (W365) ES: X06 resuelto offline (ninguna de nuestras placas ath79 LAP-120, LiteBeam AC Gen2, PowerBeam 5AC Gen2 y Loco 5AC tiene switch DSA en el camino ag71xx; todas tienen eth0 con PHY directo, asi que el commit f091230 no aplica) y specs A/B de banco de una variable con A/A primero y bloques ABBA para X05 (peso NAPI de ag71xx_legacy, 32 contra 64) y X07 (firmware ath10k-ct full-community-22 contra full-nrcc-community-22, en una CPE con un par) -->
Que cubre: el veredicto de X06 por placa con evidencia archivo:linea, y las specs exactas de X05 y X07: que cambia, en que equipo, que se mide, cuando gana B y como se vuelve.
Estado: offline. 0 SSH. X06 queda CONFIRMED_STATIC_SOURCE. X05 y X07 son solo especificaciones: ejecutarlas exige aprobar flasheo o escritura de firmware en banco.
Datos maquina: artifacts/autoresearch/wave365_x05_x06_x07.json. Origen: docs/REVISION_INFORME_EXTERNO_20261030_ES.md.
Arbol: OpenWrt v24.10.4, commit 78b23a26 (el de FMX-0011, tools/openwrt-build/MANIFEST.md). Las rutas son relativas a su raiz.
Leer cuando: antes de compilar variantes de ag71xx o de firmware ath10k-ct, o si alguien propone el parche DSA.
<!-- /doc-head -->
# Stage 3025A: X05, X06 y X07 (W365)

**Indice de perillas** (`artifacts/knob_index/knob_index.json`): ni el peso NAPI de ag71xx ni el firmware NRCC tienen entrada. Las dos estan **sin probar**. Lo mas cercano que si se probo es dev_weight, tx_bias, budget y napi_defer_hard_irqs; este ultimo fue la ronda M27a de 44A, DISCARDED.

## 1. X06: alineacion del header IP detras de tags DSA (commit f091230)

**Pregunta:** ¿alguna placa tiene un switch DSA con tag antepuesto en el camino ag71xx? Si lo tiene, el commit aplica; si es un PHY directo, no.

| Placa (perfil de imagen) | Evidencia | Camino | Veredicto |
| :-- | :-- | :-- | :-- |
| LAP-120 / LiteAP AC (`ubnt_lap-120`) | `target/linux/ath79/dts/ar9342_ubnt_lap-120.dts:3` incluye `ar9342_ubnt_wa_1port.dtsi` | eth0 -> PHY directo phy4 (RGMII) | **No aplica** |
| LiteBeam AC Gen2 (`ubnt_litebeam-ac-gen2`) | `.../ar9342_ubnt_litebeam-ac-gen2.dts:3`, el mismo include | eth0 -> phy4 | **No aplica** |
| PowerBeam 5AC Gen2 (`ubnt_powerbeam-5ac-gen2`) | `.../ar9342_ubnt_powerbeam-5ac-gen2.dts:3`, el mismo include | eth0 -> phy4 | **No aplica** |
| Loco 5AC (`ubnt_nanostation-ac-loco`) | `.../ar9342_ubnt_nanostation-ac-loco.dts:3`, el mismo include | eth0 -> phy4 | **No aplica** |

**Evidencia comun:**
- `ar9342_ubnt_wa_1port.dtsi:5-11`: mdio0 con `phy4: ethernet-phy@4`.
- `ar9342_ubnt_wa_1port.dtsi:13-23`: eth0 `status = "okay"`, `phy-mode = "rgmii-id"`, `phy-handle = <&phy4>`. Es GMAC0 a un PHY, sin switch en el medio.
- **El switch interno no se usa:** el ar8229 (`builtin-switch`, swconfig) cuelga de mdio1/eth1 en `ar934x.dtsi:244-292`. eth1 viene `status = "disabled"` (`ath79.dtsi:71-72`) y ninguno de nuestros archivos de placa lo habilita.
- **No hay DSA en el kernel:**
  - `target/linux/generic/config-6.6:3971`: `# CONFIG_NET_DSA is not set`;
  - el kernel compilado de FMX-0011 (`build_dir/.../linux-6.6.110/.config:845`) tambien lo dice;
  - `.config:3330-3336`: ningun `kmod-dsa*` seleccionado.
- **Driver:** el que se usa es el downstream `ag71xx_legacy` (`target/linux/ath79/config-6.6:1-2`: `CONFIG_AG71XX` no, `CONFIG_AG71XX_LEGACY=y`).
  - No tiene ninguna referencia a DSA.
  - Para `qca,ar9340-eth` ya suma `NET_IP_ALIGN` a `rx_buf_offset` (`ag71xx_main.c:1627-1630`), asi que el header IP de una trama sin tag ya queda alineado.
- f091230 no esta en el arbol 78b23a26; es posterior y del driver upstream.

**Veredicto X06:** el parche **no aplica a ninguna placa nuestra**. Queda REFUTED para este hardware, cerrado sin banco. Para que aplicara tendria que cambiar la placa (un switch DSA en eth0) o el driver.

## 2. X05: peso NAPI de ag71xx_legacy, 32 contra 64

**Valor actual: 32, fijado al compilar.**
- `.../ag71xx/ag71xx.h:50` define `AG71XX_NAPI_WEIGHT 32` y `ag71xx_main.c:1681` lo pasa a `netif_napi_add_weight`.
- Las lineas 46-49 del header advierten que mas peso no es mejor, por fallos de D-cache.
- Las lineas 138-139 dimensionan con ese valor los histogramas de `napi_stats`.
- El upstream 0063f777b58d es del driver upstream: no esta en este arbol y no se usa.

**Como se cambia:** **no hay perilla en caliente.** El driver es built-in, asi que B es una imagen reconstruida con la linea 50 en 64. A es la **misma build sin el cambio** (A prima), no la imagen de stock: asi la unica diferencia es una linea. Depende de X02 (rebuild reproducible) y de que lane_4 compile las variantes (W366).

**Readback del peso:** `cat /sys/kernel/debug/ag71xx_legacy/19000000.eth/napi_stats`. La tabla llega hasta el peso (`ag71xx_legacy_debugfs.c:124`). El nombre del directorio sale del nodo `eth@19000000` y es INFERRED; el debugfs esta activo por `config-6.6:4`.

**Banco:** PtP con .241 (AP, siempre en A prima) y .242 (STA, equipo bajo prueba), dos PBE-5AC Gen2 con el mismo camino eth0 + phy4. La unica variable es el peso en .242; RF, colas y sysctl quedan fijos.

**Diseno:**
- **A/A primero:** dos fases A con el mismo protocolo de fase, reboot incluido. Si |delta goodput| es 2 % o mas, o |delta p95| es 5 % o mas, el banco no esta estable y se para.
- **Bloques:** 3 bloques ABBA. Cada fase arranca con un reboot (sysupgrade solo cuando cambia la imagen), 5 min de asentamiento y 10 min de medicion.
- **Carga:** iperf3 TCP con 4 flujos, 60 s por direccion, subida y bajada, desde hosts cableados detras de cada radio. Ping con carga cada 200 ms.
- **Metricas:**
  - goodput y RTT con carga (p50/p95/p99);
  - deltas de `/proc/net/softnet_stat` (processed, dropped, time_squeeze) y de `NET_RX` en `/proc/softirqs`;
  - histograma `napi_stats` y drops rx de `ethtool -S eth0`;
  - MemAvailable y delta de `fq_overmemory`.
- **Decision:** permutacion pareada por bloque con Sidak (889A). B gana solo con goodput +3 % o mas, p95 sin empeorar mas de 5 % y time_squeeze sin subir. Si no, se queda 32.
- **Rollback:** sysupgrade de vuelta a A prima (o al backup de la imagen original) y readback de `napi_stats` con la tabla hasta 32. Antes del primer flasheo, backup y hash de mtd0/1/4/5; sysupgrade no toca u-boot, env ni ART.

## 3. X07: firmware ath10k-ct, full-community-22 contra full-nrcc-community-22

**Actual:** `firmware-2-ct-full-community-22.bin.lede.022`, sha256 `398e4380...a38e`, version `10.1-ct-8x-__fW-022-ecad3248`. Fuentes: `package/firmware/ath10k-ct-firmware/Makefile:33-36` y `tools/openwrt-build/MANIFEST.md` seccion 1.

**Candidato:** `full-nrcc-community-22`, el nombre de Candela segun la revision. **No viene en 24.10.4**: el Makefile no lo menciona; solo trae `full-community-22` (linea 33) y `full-htt-mgt-community-22` (linea 40).
- El nombre exacto del archivo y su sha256 son UNKNOWN. Se fijan al bajarlo de candelatech.com/downloads, el mismo origen de la linea 28.
- Que significa "nrcc" se confirma en las notas de version de Candela antes de probar.

**Banco:** una CPE con un par. La CPE es la Loco 5AC .250 (equipo bajo prueba); el par es el LAP-120 .20, siempre en full-community-22. La unica variable es el firmware de .250; driver, kernel, RF, canal, potencia y colas quedan fijos.

**Cambio de firmware:**
1. Copiar el archivo NRCC sobre `/lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin`, en el overlay.
2. Comprobar su sha256.
3. Recargar: `wifi down; rmmod ath10k_pci ath10k_core; modprobe ath10k_pci; wifi up`. El enlace cae unos 30 a 60 s.

**Diseno:**
- **A/A primero:** con recarga de ath10k en cada fase, tambien en A, y los mismos umbrales que X05.
- **Bloques:** 3 ABBA. Cada fase: recarga, 3 min de asociacion y asentamiento, 10 min de medicion.
- **Carga:** iperf3 TCP con 4 flujos, subida y bajada, por el enlace .20 <-> .250, mas ping con carga.
- **Metricas:**
  - goodput y RTT con carga (p50/p95/p99);
  - `tx_retries` y `tx_failed` de la estacion, tasa y MCS (`iw station dump`);
  - crashes y version del firmware en `dmesg`;
  - MemAvailable, delta de `fq_overmemory` y CPU softirq.
- **Decision:** la misma de X05. Ademas, **cualquier crash del firmware en B lo descarta.**
- **Rollback:**
  1. `cp /rom/lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin /lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin`, que trae los bytes del squashfs.
  2. Comprobar que el sha256 es `398e4380...` y recargar ath10k.
  3. Ver en `dmesg` la version `10.1-ct-8x-__fW-022-ecad3248`.

## 4. Que aprueba el operador

- **X05:** cada flasheo de .242 y el uso del banco PtP durante la campana.
- **X07:** bajar y fijar el binario NRCC, la escritura en el overlay de .250 y el uso del banco PtMP.
- **Produccion:** ninguno de los dos llega hasta tener veredicto de banco.
