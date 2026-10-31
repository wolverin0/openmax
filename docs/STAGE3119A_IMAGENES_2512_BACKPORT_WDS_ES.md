<!-- doc-head: Stage 3119A ES: pista B (decision del operador 31/10) = 5 imagenes OpenWrt 25.12.6 ath79 (LAP-120, LiteBeam AC Gen2, NanoStation AC Loco, PowerBeam 5AC Gen2, 5AC-500) con kmod-ath10k-ct(-smallbuffers) parchado (3 guardas NULL de ath10k-7.2 + recovery_check_work en workqueue_aux, rebase sobre ath10k-6.18) y kmod-mac80211 parchado (strip ETH_P_TEB 0x6558 + v3 4-addr autorizado, rebase del parche binario 24.10.4 a backports 6.18.55); compilado con el SDK oficial 25.12.6 (sha256 OK), imagenes con el ImageBuilder 25.12.6; todo compila, 0 warnings en archivos tocados; NADA flasheado ni arrancado -->
Que cubre: parches, build, prueba de que las imagenes llevan los kmods parchados, vermagic, tamanos, rutas, limites.
Estado: SOLO ESCRITORIO. 0 acceso a equipos, 0 flasheo, 0 boot. No commiteado. `.bin` fuera de git (`*.bin` en .gitignore).
Entrada: STAGE3116A (diff 6.10 vs 6.18 vs 7.2), STAGE3117A (imagenes 25.12.6 stock). Salida: `firmware/openwrt/2512_bp/`.
Leer cuando: antes del A/B de banco 24.10.4 vs 25.12.6-bp, o de tocar cualquiera de los 3 parches.
<!-- /doc-head -->

## 1. Resultado
- CONFIRMED: los 3 parches aplican y compilan con el SDK oficial 25.12.6 (`openwrt-sdk-25.12.6-ath79-generic_gcc-14.3.0_musl`, sha256 `941c19d4...31c6` = `sha256sums` de downloads.openwrt.org; GPG `.asc` no verificado). 0 errores; 0 warnings en `net/mac80211/rx.c` y en `ath10k-6.18/*`.
- CONFIRMED: las 5 imagenes se armaron con el ImageBuilder 25.12.6 y el mismo comando/PACKAGES/FILES que STAGE3117A (kit WA v20 + 14 helpers); el sha256 del ImageBuilder se verifico en 3117A (se reuso ese arbol, copiado).
- Nada quedo sin compilar. Un primer intento fallo (`core.c: 'return' with a value, in function returning void`): el filtro de hunks 6.18->7.2 habia omitido el `return false` del bloque WEDGED. Corregido (hunk agregado); el bloque `recovery_check_work`/`start_recovery` resultante es identico al de 7.2 (diff vacio).

## 2. Parches (en `firmware/openwrt/2512_bp/patches/`)
| Archivo | Destino | Que hace |
| :-- | :-- | :-- |
| `990-fmx-ath10k-ct-null-guards-and-recovery-check-on-aux-wq.patch` | `package/kernel/ath10k-ct/patches/` (ath10k-6.18, bb84e159) | htt_rx `netbuf_pop`: slot NULL -> warn + reset paddr + avanza idx + `fill_cnt--` + NULL. wmi `tx_beacon_nowait`: umbral `arvif` 8000 -> 0x8000 y guarda nueva de `ar`. Recovery: `ath10k_core_needs_recovery` pasa a `recovery_check_work` encolado en `ar->workqueue_aux`; `start_recovery` solo encola. 5 archivos (htt_rx.c, wmi.c, core.c, core.h con el campo `recovery_check_work`, mac.c con `cancel_work_sync` en `ath10k_stop`). |
| `990-fmx-mac80211-strip-eth-p-teb-airos8-wds.patch` | `package/kernel/mac80211/patches/subsys/` (backports 6.18.55) | Al entrar a `ieee80211_rx_mesh_data` (lo llaman el camino lento, cada subframe A-MSDU y fast-rx): si `skb_headlen >= 28` y el ethertype tras la conversion 802.3 es `0x6558`, `__skb_pull(14)` y `ip_summed = CHECKSUM_NONE`. |
| `991-fmx-mac80211-authorized-gated-4addr-delivery-v3.patch` | idem | En `ieee80211_rx_h_data` (iface AP, trama 4-addr): sin STA -> drop (igual que antes); si no esta AUTHORIZED se entrega sin evento; si esta AUTHORIZED, `test_and_set` WLAN_STA_4ADDR_EVENT y `cfg80211_rx_unexpected_4addr_frame` una vez; nunca `RX_DROP`. `__ieee80211_data_to_8023` convierte esas tramas como `NL80211_IFTYPE_AP_VLAN` (si no, cfg80211 rechaza FROMDS+TODS en AP). |
- Fuente de verdad del rebase mac80211: el parche BINARIO que esta en uso, `firmware/openwrt/pbe5ac_gen2_ptp_kit/patch_mac80211_teb.py` (21 instr TEB en el prologo de `ieee80211_rx_mesh_data` + 13 instr v3 en `ieee80211_rx_h_data`; modulo publico v4 `mac80211_teb_4addr_v3_6.6.110.ko`). No habia parche C real: el `999-futuramax-...0x6558.patch` de stage32c apuntaba a `util.c` y nunca se aplico (STAGE3117A 5.3). Rationale: FMX-DISC-03/36 (TEB) y FMX-DISC-38/41 (EAPOL 2/4 4-addr antes de AUTHORIZED).
- El pedido nombraba solo TEB. Se porto tambien v3 porque el modulo en uso es TEB+v3 y 6.18.55 conserva el `RX_DROP` de 4-addr en AP. Va en archivo separado: borrar `991-*` deja solo TEB.
- Cambio semantico vs binario (INFERRED, sin efecto en AP): el binario pisaba el codigo mesh; el C lo conserva despues del strip.

## 3. Recovery en 6.18 (lo pedido por el operador)
- CONFIRMED por lectura: 6.18 ya trae contadores (`pending_recovery`, `fail_cont_count`), completion `driver_recovery` 5 s y WEDGED tras 4 fallos. Se conservan; `reinit_completion`/`complete` ya estaban en 6.18 (no se tocan).
- El `wait_for_completion_timeout` de 5 s ahora corre en `workqueue_aux`, no en `ar->workqueue` (singlethread de `restart_work` y `fw_dump_work`): un segundo crash con recovery pendiente ya no frena el restart.
- Residual (INFERRED, mismo diseno que 7.2): `workqueue_aux` tambien es singlethread y corre `svc_rdy_work`; ese wait puede demorar el service-ready del restart hasta 5 s. `ath10k_wmi_wait_for_service_ready` espera 5 s + poll de CE + otros 5 s, asi que deberia alcanzar; no probado.
- WEDGED tras 4 fallos sigue siendo terminal: hace falta watchdog externo (STAGE3116A 1.3).

## 4. Build
- WSL Ubuntu (6 cpu, 4 GB), `-j3`. Feed `base` en el commit del SDK (`64900e75`). `.config` = el del SDK (`CONFIG_ALL_KMODS=y`, igual que `config.buildinfo` oficial: MAC80211_DEBUGFS, MAC80211_MESH, ATH_DFS, ATH_USER_REGD).
- `PKG_RELEASE`: ath10k-ct 1->2, mac80211 2->3, para que apk del ImageBuilder elija nuestros paquetes y no los del feed (con igual version el manifest no prueba nada).
- Paquetes inyectados en `packages/` del ImageBuilder (copia aparte, `~/ib2512bp`): `kmod-mac80211 6.12.112.6.18.55-r3`, `kmod-ath10k-ct(-smallbuffers) 6.12.112.2025.12.01~bb84e159-r2` (copias en `2512_bp/kmods/`). Dependencia de kernel `6.12.112~7f15b2e770f44b07009c08f8e8971baf-r1` = la del feed oficial.
- Tiempos: mac80211 (todas las variantes y drivers) 1733 s; ath10k-ct 521 s.

## 5. Verificacion (squashfs extraido de cada sysupgrade con unsquashfs4)
| Placa | sysupgrade (B) | factory (B) | ath10k | ath10k_core.ko | mac80211.ko |
| :-- | --: | --: | :-- | --: | --: |
| LAP-120 | 7 274 761 | 7 275 160 | smallbuffers r2 | 601 824 | 858 416 |
| LiteBeam AC Gen2 | 7 143 707 | 7 144 088 | smallbuffers r2 | 601 824 | 858 416 |
| NanoStation AC Loco | 7 274 785 | 7 275 160 | smallbuffers r2 | 601 824 | 858 416 |
| PowerBeam 5AC Gen2 | 7 209 247 | 7 209 624 | smallbuffers r2 | 601 824 | 858 416 |
| PowerBeam 5AC-500 | 7 143 709 | 7 144 088 | ct (no smallbuffers) r2 | 601 600 | 858 416 |
| Stock 25.12.6 (3117A, LAP) | 7 274 761 | 7 275 160 | smallbuffers r1 | 601 348 | 857 880 |
- CONFIRMED vermagic de los 4 .ko en las 5 imagenes = `6.12.112 mod_unload MIPS32_R2 32BIT` = el de los .ko stock (ath9k/cfg80211). Tabla completa con sha256: `2512_bp/modules_in_images.csv`.
- CONFIRMED que el kmod es el nuestro (vermagic no lo distingue): manifests con `-r2`/`-r3`; `mac80211.ko` de la imagen = el de nuestro `.apk` (sha256 `637e42ce...`); `ath10k_core.ko` contiene `rx ring slot %d empty while popping netbuf` (stock: 0) y `arvif: %px` de la guarda wmi (stock: `%p`); `mac80211.ko` tiene 2 inmediatos `0x6558` en `.text` (stock: 1, uso previo no relacionado; +1 = el strip).
- CONFIRMED paridad de toolchain/config: el `cfg80211.ko` y `compat.ko` que compilo nuestro SDK (sacados de nuestro `kmod-cfg80211-r3.apk`, no instalado) son identicos byte a byte a los del feed oficial (`361b824d...`). Las imagenes llevan el `kmod-cfg80211-r2` del feed. Delta de los parches: mac80211 +536 B, ath10k_core +476 B.
- Tamanos de imagen identicos al byte a 3117A (relleno a bloque, INFERRED): mismo margen (~45 % de 0xf60000) y mismo overlay libre que la tabla de STAGE3117A.
- Ojo: el feed 25.12.6 cambio entre el build de 3117A (05:49) y este (10:25): `dnsmasq 2.93-r1 -> r2`, y `busybox`, `libnftables`, `wifi/utils.uc` con bytes distintos a igual version (CONFIRMED por diff del rootfs). No es de nuestros parches; el ImageBuilder baja el feed vivo.

## 6. Rutas exactas (todas bajo `firmware/openwrt/2512_bp/`)
- `ubnt_lap-120/openwrt-25.12.6-ath79-generic-ubnt_lap-120-squashfs-{factory,sysupgrade}.bin`
- `ubnt_litebeam-ac-gen2/openwrt-25.12.6-ath79-generic-ubnt_litebeam-ac-gen2-squashfs-{factory,sysupgrade}.bin`
- `ubnt_nanostation-ac-loco/openwrt-25.12.6-ath79-generic-ubnt_nanostation-ac-loco-squashfs-{factory,sysupgrade}.bin`
- `ubnt_powerbeam-5ac-gen2/openwrt-25.12.6-ath79-generic-ubnt_powerbeam-5ac-gen2-squashfs-{factory,sysupgrade}.bin`
- `ubnt_powerbeam-5ac-500/openwrt-25.12.6-ath79-generic-ubnt_powerbeam-5ac-500-squashfs-{factory,sysupgrade}.bin`
- Por placa: `.manifest`, `.bom.cdx.json`, `profiles.json`, `sha256sums` del ImageBuilder. Global: `SHA256SUMS` (imagenes + kmods + parches), `modules_in_images.csv`, `packages.txt`.
- Git: solo `*.bin` esta ignorado; `.apk`, `.patch`, `.csv`, manifests y `SHA256SUMS` quedarian rastreados si se agregan. No commiteado.

## 7. Limites y siguiente paso
- UNKNOWN en runtime: carga de modulos, WDS real contra CPE airOS 8 stock (TEB + EAPOL 4-addr), recovery tras `simulate_fw_crash`. El C del TEB/v3 replica la semantica del binario; no hay prueba en aire.
- 5AC-500 lleva `kmod-ath10k-ct` normal (default del perfil) parchado; no smallbuffers.
- Banco (gate de STAGE3113A/3116A, LAP-120 `.20` + Loco `.250`, backup y hash de mtd0/1/4/5, watchdog de auto-revert, nunca mtd0/1/5): (1) boot + `lsmod` + dmesg; (2) CPE airOS 8 stock en WDS: asociacion, EAPOL, AP_VLAN `phy*-ap0.sta1`, ARP/DHCP a traves de br-lan; (3) N x `simulate_fw_crash` contando `previous recovery`/`consecutive fail`/WEDGED. Sin umbrales inventados: comparar contra la varianza A/A.
