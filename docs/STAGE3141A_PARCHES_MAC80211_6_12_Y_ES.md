<!-- doc-head: Stage 3141A ES: 2 fixes upstream de net/mac80211 (linux-stable 6.12.y, posteriores a los backports 6.12.52 de 24.10.4): 3b4d27acaf (siempre liberar el skb si ieee80211_tx_prepare_skb falla; TX_DROP perdia el skb) y 586c628c0b (crypto_tx_tailroom_needed_cnt se incrementaba 2 veces por clave TAINTED en reconfig tras reinicio de firmware). Escritos como parches de paquete OpenWrt 360/361 (subsys), aplican limpio sobre el stack 24.10.4 en las 2 variantes, kmod-mac80211/ath9k/cfg80211 -r2 compilados con el SDK 24.10.4 (WSL ~/fmx_bp2410), diff de desensamblado prueba el codigo nuevo. 25.12 (backports 6.18.55) YA trae ambos: sin trabajo. Imagenes NO rebuildeadas (el TEB v3 de las imagenes es un parche binario sobre el .ko oficial). NADA flasheado ni arrancado; A/B de banco pendiente -->
Que cubre: que hace cada fix, si nos pega, parches, build, evidencia, sha256, limites y siguiente paso.
Estado: SOLO ESCRITORIO. 0 acceso a equipos, 0 flasheo, 0 boot, nada publicado upstream, sin commit.
Entrada: STAGE3136A (fila 2 de la tabla de bugs), STAGE3118A (receta SDK/IB 24.10.4), STAGE3119A (2512), STAGE3116A (induccion de crash).
Salida: `firmware/openwrt/2410_bp/mac80211_6_12_y_fixes/` (`patches/`, `kmod/`, `evidence/`, `SHA256SUMS`).
Leer cuando: antes de armar una imagen 24.10.4 con mac80211 parchado, o antes del A/B de banco de estos fixes.
<!-- /doc-head -->

## 1. Resultado
| Fix (6.12.y) | Origen | En 6.12.52 | En 25.12 (6.18.55) | Parche | Compilado | Evidencia en el .ko |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 3b4d27acaf skb leak | upstream d5ad6ab61cbd (Felix Fietkau, mar-2026) | falta (CONFIRMED) | YA esta (CONFIRMED) | 360 | si, 2 variantes | si, ver 4 |
| 586c628c0b tailroom x2 | upstream 3f3d8ff31496 (M. Korenblit, ene-2026) | falta (CONFIRMED) | YA esta (CONFIRMED) | 361 | si, 2 variantes | si, ver 4 |
- CONFIRMED: ambos commits bajados de `github.com/gregkh/linux/commit/<hash>.patch` hoy (espejo de linux-stable); no se verifico firma GPG de tags ni se cruzo con git.kernel.org.
- CONFIRMED: el tarball `backports-6.12.52.tar.xz` del SDK trae `tx.c` sin `kfree_skb` en el TX_DROP de `ieee80211_tx_prepare_skb` y `key.c` sin el guard `KEY_FLAG_TAINTED` en `ieee80211_reenable_keys`. El tarball `backports-6.18.55.tar.zst` del SDK 25.12.6 trae las dos correcciones y el kdoc nuevo. Pista 25.12: omitida (no hay nada que portar).
- No se hizo rebuild de imagenes (ver 6).

## 2. Que hace cada fix y si nos pega
- 3b4d27acaf: `ieee80211_tx_prepare_skb()` tenia 3 caminos de error y solo 2 liberaban el skb. El primero (`ieee80211_tx_prepare()` == TX_DROP) devolvia false sin `kfree_skb`. El fix libera ahi y saca los frees redundantes de los llamadores (ath9k `channel.c` x2, hwsim) para no hacer double free; documenta la regla en `mac80211.h`. La parte mt76 del upstream no aplica en 6.12 (scan.c aparece despues de 6.14; el propio commit la excluye).
  - Nos pega: INFERRED, bajo. Los llamadores en 6.12.52 son solo ath9k `channel.c` (ath_scan_send_probe, ath_chanctx_send_vif_ps_frame) y hwsim. ath10k no llama a la funcion. En las imagenes AC el driver activo es ath10k, asi que la fuga solo puede ocurrir en radios ath9k con la ruta de channel-context/scan-probe (UNKNOWN si alguna de nuestras placas la ejercita). 3136A ya lo marcaba como "INFERRED nos pega".
  - Riesgo propio del parche: si se instala `kmod-mac80211` parchado con un `kmod-ath9k` sin parchar, el ath9k viejo libera el skb y mac80211 tambien (double free). Por eso `kmod-ath9k` -r2 va en el mismo set.
- 586c628c0b: en reconfig, si el driver pide desconectar, las claves de la interfaz quedan TAINTED. `ieee80211_reenable_keys` incrementaba `crypto_tx_tailroom_needed_cnt` por cada clave, y despues `ieee80211_key_enable_hw_accel` lo incrementaba otra vez al marcarla como "no en hardware". Resultado: contador doble y WARN en `ieee80211_free_keys`. El fix omite el incremento en el bucle para claves TAINTED.
  - Nos pega: INFERRED, medio. El camino es "reconfig tras reinicio de firmware (`simulate_fw_crash`/recovery ath10k) con disconnect pedido por el driver", que es el escenario de STAGE3116A. Efecto probable de no tenerlo: WARN y contador de tailroom inflado (mas copias/realloc en TX con cifrado por software). UNKNOWN: si en campo se manifiesta; sin dato de produccion.

## 3. Parches y build
- `patches/360-fmx-wifi-mac80211-always-free-skb-on-ieee80211_tx_prepare_skb-failure.patch` (4 archivos: ath9k `channel.c`, `mac80211_hwsim.c`, `include/net/mac80211.h`, `net/mac80211/tx.c`). Mismo diff que 3b4d27acaf, cabecera original conservada.
- `patches/361-fmx-wifi-mac80211-dont-increment-crypto_tx_tailroom_needed_cnt-twice.patch` (`net/mac80211/key.c`). Mismo diff que 586c628c0b.
- Destino: `package/kernel/mac80211/patches/subsys/` (numeros 360/361 libres: el ultimo era 353). Orden: despues de los 3xx de OpenWrt; ninguno de los dos toca archivos que modifiquen los parches 2xx/3xx del feed en esas lineas.
- CONFIRMED (dry-run `patch -p1` sobre `backports-6.12.52` limpio, y `make package/mac80211/prepare V=s` real): aplican sin FAILED ni rejects en regular y smallbuffers. Solo corrimientos: mac80211.h +5, tx.c +1, key.c -6.
- No hay interaccion con el TEB/WDS: en 24.10 el TEB no es un parche C sino binario (3118A 4). Los parches 990/991 de `2512_bp/patches/` son C, para 6.18, y no se tocaron.
- Metodo: el SDK de 3118A (`~/fmx_bp2410/sdk/openwrt-sdk-24.10.4-ath79-generic_gcc-13.3.0_musl...`, feed base en tag v24.10.4, `.config` del SDK), copiando los 2 parches a `feeds/base/package/kernel/mac80211/patches/subsys/` y `PKG_RELEASE` 1 -> 2 (para que el manifest/opkg distinga el paquete). Comando: `make package/mac80211/clean; make package/mac80211/prepare V=s; make package/mac80211/compile V=s -j3`.
- Un primer `compile` fallo en `linux-firmware` (empaquetado de `rtl8723au-firmware`, dependencia arrastrada, no relacionado). Reintento identico: OK, rc=0, 4 min 47 s (los objetos de mac80211 ya estaban cacheados del build previo de 3118A, INFERRED). Causa del fallo UNKNOWN (posible carrera con -j3).
- Hubo cortes de WSL durante la sesion (WSAETIMEDOUT) que reiniciaron el `/tmp` de la distro; no afecta `~/fmx_bp2410`.

## 4. Evidencia de que el codigo parchado esta en el modulo
- CONFIRMED: el `mac80211.ko` del SDK sin parchar es el oficial (3118A: sha `8566fb1c...`, igual a `pbe5ac_gen2_ptp_kit/mac80211_rom_241.ko`). El parchado tiene sha `ec88a9ca...` y pesa 815 680 B contra 815 640 B (+40 B).
- CONFIRMED: reubicaciones `R_MIPS_26 kfree_skb_reason`: 82 en el oficial, 83 en el parchado (+1 llamada).
- CONFIRMED: diff de desensamblado normalizado (direcciones/offsets enmascarados) oficial vs parchado: 96 lineas (`evidence/mac80211_ko_disasm_norm.diff`). Los hunks relevantes:
  - TX_DROP: se agrega `li a1,2 ; jal kfree_skb_reason ; move a0,s0 ; b ... ; move v0,zero` = libera el skb (razon 2, SKB_DROP_REASON_NOT_SPECIFIED, que es en lo que se expande `kfree_skb`) y devuelve false.
  - `ieee80211_reenable_keys`: dentro del bucle aparece `lw v0,20(s0) ; andi v0,v0,0x2 ; bnez v0, ...` = test del bit 0x2 de `key->flags` (KEY_FLAG_TAINTED) antes de llamar a `increment_tailroom_need_count`. Es la unica funcion con el bucle sobre `sdata->key_list`.
  - El resto de las diferencias son corrimientos de constantes de offset (+32 B en varias) y reasignacion de registros.
  - Nota: las funciones aparecen sin simbolo en el .ko (strippeado) y los .o de build_dir se borran por autoremove, asi que la ubicacion de los hunks se dedujo del patron de instrucciones, no de nombres de simbolo (INFERRED en esa atribucion; el bit 0x2 y el `kfree_skb_reason` agregado son observados).
- CONFIRMED: 0 warnings del compilador en `net/mac80211/tx.c`, `key.c` y `ath9k/channel.c` (hay 58 warnings en el log, de otros archivos).
- ath9k: el hunk de `channel.c` se aplico (log de prepare) y `ath9k.ko` -r2 se compilo (sha `5bd3bb48...`, 148 248 B). No hay un ath9k.ko oficial de referencia en el repo para diffear: UNKNOWN a nivel binario, CONFIRMED a nivel de aplicacion del parche.

## 5. Archivos y sha256 (`firmware/openwrt/2410_bp/mac80211_6_12_y_fixes/`)
| Archivo | sha256 |
| :-- | :-- |
| `patches/360-...failure.patch` | `be9ac50ee5e0870ba07e3916f6e7e3818d2ad5fc091081d7178960468de4bbff` |
| `patches/361-...twice.patch` | `b7434d5bb7d6ff8cfa40a55d14b826facd20a4f2c05f8d84e20c15c555cc8fc0` |
| `kmod/kmod-mac80211_6.6.110.6.12.52-r2_mips_24kc.ipk` | `e809528c10f49ae1596e451dc8b8f18f6ab11b54703b71f3f89269440f983024` |
| `kmod/kmod-ath9k_...-r2...ipk` | `aade1ab256e67203eb27885f6e3b4895d2570e5902d7491a9b4b3858bf218afa` |
| `kmod/kmod-ath9k-common_...-r2...ipk` | `307bc7a6b32a3e83676b3d0ceb64301a86aa2203dd0a373175be2982466e61d1` |
| `kmod/kmod-cfg80211_...-r2...ipk` | `48e31fe432e161b29b4b512be0b22d269e1838ec867592a862abc981d97bf149` |
| `kmod/mac80211.ko.patched` | `ec88a9ca522e15c6533d37b5d98ced87ee26c379229f46129ff3d2fb591dca08` |
| `kmod/ath9k.ko.patched` | `5bd3bb4829783c9c361012e7775791a43307c77e31fbb01264fdbcc603fe56d0` |
- `SHA256SUMS` (misma carpeta) lista todo. Los `.ipk` de ath10k/ath11k/etc. del mismo build (-r2) quedan en el SDK y no se copiaron.
- Los `.ipk` no estan commiteados ni probados en equipo. `.ko.patched` son copias para inspeccion, no para flashear sueltos.
- Dependencia: los -r2 piden `kernel (=6.6.110~35ef4dd...-r1)`, el del release oficial (mismo que 3118A).

## 6. Imagenes: por que NO se rebuildearon
- Las imagenes `2410_bp` hornean `lib/modules/6.6.110/mac80211.ko` = `mac80211_teb_4addr_v3_6.6.110.ko`, un parche BINARIO (TEB 0x6558 + EAPOL 4-addr + AP_VLAN) hecho sobre los bytes del `.ko` oficial `8566fb1c` (3118A 4). El `.ko` parchado de este stage tiene otros bytes: reinsertar ese binario pisaria los fixes, y el instalar el -r2 pierde el WDS con airOS 8.
- Opciones (decision del operador, no inventada aca):
  - (a) Portar TEB + v3 a C sobre 6.12.52 (como en `2512_bp/patches/990-991`, hechos para 6.18.55) y rebuildear mac80211 con las 4 piezas. Costo: rebase de 2 parches + build completo (mac80211 ~29 min en 25.12, 3119A) + 5 imagenes. Es la ruta correcta si se quiere una imagen con todo.
  - (b) Para el A/B de banco de estos fixes solos, instalar los 3 `.ipk` -r2 (mac80211, ath9k, cfg80211) en un 24.10.4 oficial ya flasheado con `opkg install`, sin TEB (el banco de STAGE3116A mide recovery, no WDS).
- No se escribio ningun parche C de TEB para 24.10: queda fuera de lo pedido.

## 7. Pendiente y limites
- Banco (gate del operador, equipos LAP-120 `.20` y Loco `.250`, backup y hash mtd0/1/4/5, watchdog de auto-revert, nunca mtd0/1/5): A = 24.10.4 (o `2410_bp`) vs B = lo mismo + estos 3 `.ipk`, con la induccion de crash de STAGE3116A (`simulate_fw_crash` N veces). Contar `WARNING` de `ieee80211_free_keys`/tailroom, `previous recovery`/`consecutive fail`, y tiempo a trafico. Decidir contra la varianza A/A, sin umbrales inventados.
- Para el fix del skb leak no hay forma de medirlo con ath10k: se necesitaria una radio ath9k con scan/chanctx; si ninguna placa la usa, el fix es solo higiene (UNKNOWN).
- UNKNOWN: carga de modulos y boot en hardware o QEMU (0 pruebas); `kmod-cfg80211` -r2 se incluye por consistencia de ABI de version, sin cambios de codigo propios (INFERRED: solo cambio de PKG_RELEASE).
- Los parches de 66a7153fd6 (stats al desconectar) y 29a1a350af (carrera AQL en debugfs) de la misma fila de 3136A no se tocaron (no pedidos).
