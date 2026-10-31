<!-- doc-head: Stage 3116A ES: diff estatico del driver ath10k-ct que enviamos (ath10k-6.10, ac71b14d, 2024-07-30) contra ath10k-6.18 (OpenWrt 25.12.6, bb84e159, 2025-12-01) y ath10k-7.2 (main, fcbdb70, 2026-07-31), solo codigo QCA988x; resultado: de los 3 fixes, 0 estan en 6.18 y los 3 (1 parcial) solo en 7.2; el codigo de datapath (htt_rx/htt_tx/ce/pci/debug) es cosmetico; lo relevante es el rework de recovery de 6.18 + 3 guardas de 7.2; backport minimo de ~100 lineas en 5 archivos aplica limpio sobre el stack de parches OpenWrt 24.10 (sin compilar); hallazgo extra: 25.12 cambia el firmware CT de QCA988x (2020.11.08 -> 2023.04.04 beta) -->
Que cubre: respuesta a "base de 2 anios de atraso", estado de los 3 fixes, otros fixes con archivo:funcion, factibilidad de backport vs cambio de base, firmware.
Estado: SOLO LECTURA / ESCRITORIO. 0 SSH, 0 escrituras en equipos, 0 flasheo. Nada compilado ni probado en hardware.
Entrada: STAGE3113A (#6, #13). Fuentes: greearb/ath10k-ct (clon scratch fuera del repo), openwrt/openwrt ramas openwrt-24.10, openwrt-25.12, main (raw GitHub).
Leer cuando: antes de decidir entre backport a smallbuffers 6.10 y salto de base 25.12.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

## Respuesta corta
- CONFIRMED: el driver es ac71b14d de 2024-07-30, 27 meses al 2026-10-31. Es lo que OpenWrt 24.10 trae por politica de rama estable (Makefile openwrt-24.10: PKG_SOURCE_DATE 2024-07-30, release 2). No es un error de armado nuestro.
- CONFIRMED: el atraso de codigo en las rutas QCA988x es chico. De 6.10 a 7.2, htt_rx.c/htt_tx.c/ce.c/pci.c/debug.c/htc.c/hw.c son cosmeticos (timer API, `%pK`->`%p`, `{0}`->`{}`, const/static, kzalloc_obj). Los grep de AIRTIME/aql/txq_limit/tx_airtime en mac.c/htt_*/wmi.c dan identico en 6.10, 6.18 y 7.2.
- CONFIRMED: NO hay fixes de AQL, airtime ni rate control del datapath entre 6.10 y 7.2. Lo que si cambia es recovery tras crash de firmware y 3 guardas contra NULL.
- CONFIRMED: saltar a 25.12.6 NO trae los 3 fixes (estan solo en main/7.2). Y trae el rework de recovery a medias (ver 1.3).

## Metodo y limites
- `git archive` de ath10k-6.10@ac71b14d, ath10k-6.18@bb84e15, ath10k-7.2@fcbdb70 y 6.10@HEAD; `diff -u` por archivo; hunks leidos a mano.
- Parches OpenWrt 24.10 de package/kernel/ath10k-ct/patches bajados y aplicados en orden sobre 6.10 para probar el backport.
- Sin kernel/toolchain: el backport se probo con `patch --dry-run` (aplica), NO se compilo ni se cargo. UNKNOWN: warnings/ABI en 6.6.110 + backports 6.12.96.
- Cambios del firmware CT son binarios: no hay diff estatico; solo release notes de commits de OpenWrt.

## 1. Los 3 fixes en 6.10
| # | Fix | 6.10 (nuestro) | 6.18 (25.12.6) | 7.2 (main) | Evidencia |
| --- | --- | --- | --- | --- | --- |
| 1 | NULL en `ath10k_htt_rx_netbuf_pop` (htt_rx.c) | FALTA | FALTA | PRESENTE | 6.10 solo chequea `fill_cnt==0`; lee `netbufs_ring[idx]` y hace `ATH10K_SKB_RXCB(msdu)->paddr` sin chequear NULL. 7.2 agrega warn + `reset_paddrs_ring` + avanza `sw_rd_idx` + `fill_cnt--` + `return NULL`. Los 2 callers (`ath10k_htt_rx_amsdu_pop`) ya manejan NULL con purge y -ENOENT. |
| 2 | `recovery_check_work` en `workqueue_aux` (core.c) | FALTA | FALTA | PRESENTE | 6.10/6.18: `workqueue_aux` solo lo usan sdio.c y wmi.c (svc_rdy_work). 7.2 agrega `ath10k_core_recovery_check_work`, `INIT_WORK`, `cancel_work_sync` en `ath10k_stop` (mac.c) y `struct work_struct recovery_check_work` (core.h). |
| 3 | `ar` NULL en `ath10k_wmi_tx_beacon_nowait` (wmi.c) | PARCIAL (defectuoso) | IGUAL a 6.10 | PRESENTE | 6.10/6.18 solo chequean `arvif < 8000` (decimal, no 0x8000) y despues hacen `ar = arvif->ar; spin_lock_bh(&ar->data_lock)` sin chequear `ar`. 7.2: umbral 0x8000, `%px` y chequeo de `ar` con `WARN_ON_ONCE`+return. Comentario de 7.2: crash visto tras FW crash "1/4/2026", fault en 0x2e38 (offset de `data_lock` con `ar` NULL, INFERRED). |

### 1.3 Matiz del recovery (INFERRED por lectura, no reproducido)
- 6.10 usa `ATH10K_FLAG_RESTARTING` (`test_and_set_bit`, "already restarting", se limpia en `ath10k_reconfig_complete`). Simple: un segundo evento se descarta sin bloquear.
- 6.18 lo reemplaza por `ath10k_core_needs_recovery`: `pending_recovery`, `fail_cont_count`, completion `driver_recovery`, `ATH10K_RECOVERY_TIMEOUT_HZ` 5 s y `ATH10K_RECOVERY_MAX_FAIL_COUNT` 4. A los 4 fallos seguidos `ar->state = ATH10K_STATE_WEDGED` y el driver deja de recuperar (radio muerta hasta reboot).
- En 6.18 el `wait_for_completion_timeout` corre en el contexto del llamador. `ath10k_pci_fw_dump_work` (pci.c) se encola en `ar->workqueue` (singlethread, la misma de `restart_work`): un segundo evento de crash con recovery pendiente bloquea el restart 5 s y suma un fallo. Es lo que 7.2 corrige con `workqueue_aux` ("avoid blocking recovery tracking").
- Consecuencia: 25.12.6 sola puede dejar el recovery peor que 6.10 en ese caso y agrega WEDGED terminal. Requiere watchdog externo (reboot/rollback) en nodos remotos: UNKNOWN si los kits actuales lo cubren para WEDGED.

## 2. Otros cambios con efecto en QCA988x
| Cambio | Archivo:funcion | En 6.10 | 6.18 / 7.2 | Relevancia PtMP/AP | Clase |
| --- | --- | --- | --- | --- | --- |
| Rework de recovery (contadores, WEDGED, completion) | core.c:`ath10k_core_needs_recovery`/`ath10k_core_start_recovery`; mac.c:`ath10k_reconfig_complete`; core.h | no | 6.18 | Alta: recuperacion tras `firmware crashed` | prerequisito de #2 |
| Salir rapido del cmd WMI si WEDGED | wmi.c:`ath10k_wmi_cmd_send` | no | 6.18; 7.2 lo reestructura (`else`) | Media: evita esperar 3 s por comando en estado muerto | va con el rework |
| Delete de group key = reemplazar por clave basura | mac.c:`ath10k_send_key` | borra la clave | 6.18 | Media (INFERRED): rekey GTK en AP. ~8 lineas, sin dependencia de API | opcional |
| `iterate_stations_atomic` -> `_mtx` | mac.c:`ath10k_mac_op_set_bitrate_mask` + `ath10k_mac_clr_bitrate_mask_iter` | atomic | ya en 6.10@HEAD (sync CT 2025-03-13), 6.18 | Media rate control: el iterador llama `ath10k_wmi_peer_set_param`, que puede dormir (credits); solo con `allow_pfr` y STA VHT. Aplica si usamos `iw set bitrates`/fixed-rate por STA (los ledgers lo mencionan) | opcional; requiere `ieee80211_iterate_stations_mtx` en backports (UNKNOWN) |
| PS multi-vif: aceptar CT via `TXRATE_CT` | mac.c:`ath10k_mac_vif_setup_ps` | no | 6.10@HEAD, 6.18 | Baja: evita rechazar PS con >1 vif | skip |
| `config_retry_limit` devuelve 0 en vez de -EINVAL | mac.c:`ath10k_config_retry_limit` | -EINVAL | 6.18 | Retries: ya cubierto por parche OpenWrt 24.10 `205-...unsupported-retr...` | ya cubierto |
| `peer_ps_state` bajo `data_lock` | wmi.c:`ath10k_wmi_event_peer_sta_ps_state_chg` | solo `lockdep_assert` | 7.2 | Baja (INFERRED): carrera de lectura de PS state en TX | skip |
| `vdev_delete_sync` con CRASH_FLUSH | mac.c:`ath10k_vdev_delete_sync`/`ath10k_remove_interface` | espera timeout | 6.18 | N/A probable: depende de `WMI_SERVICE_SYNC_DELETE_CMDS` (wave2/10.4), INFERRED | skip |
| `kfree(pkt_addr)` mgmt tx | wmi.c:`wmi_process_mgmt_tx_comp` y cleanup | leak | 6.18 | N/A probable: solo con `FW_FEATURE_MGMT_TX_BY_REF` (no CT 10.1), INFERRED | skip |
| `__skb_queue_purge` en pop paddr | htt_rx.c:`ath10k_htt_rx_pop_paddr32_list`/`64` | leak | 7.2 | N/A: solo `in_ord_rx` = `WMI_SERVICE_RX_FULL_REORDER` (10.4/wave2), INFERRED | skip |
| `dma_free_coherent` con direccion no alineada | ce.c:`_ath10k_ce_free_pipe`/`_64` | alineada | 7.2 | Baja: solo descarga del modulo | skip |
| Tabla MCS9 VHT20 (780,867 -> 865,960 y 1560,1733 -> 1730,1920) | mac.c:`supported_vht_mcs_rate_nss1/2` | vieja | 6.18 | Baja: decodificacion de rate reportado (INFERRED) | skip |
| LED/GPIO, canal 177, DT `qcom,calibration-data`, API mac80211 (`radio_idx`, `link_sta`) | core.c, mac.c, leds.c | no | 6.18 | Ninguna para nosotros | skip |
- Importante: ningun hunk toca la logica de AQL/airtime (`NL80211_EXT_FEATURE_AQL`, `ATH10K_AIRTIME_WEIGHT_MULTIPLIER`) ni el scheduling en htt_tx.c. El parche OpenWrt `988-...mac80211-loss-detection` (quita `REPORTS_LOW_ACK`) sigue igual en 25.12.

## 3. Backport minimo a ath10k-ct-smallbuffers 6.10 vs cambio de base
- Armado: hunks de 6.10 -> 7.2 filtrados a recovery + 3 guardas. Tamano: 97 lineas +/- (htt_rx 9, wmi 34, core.c 39, core.h 9, mac.c 6; diff sin CR), 5 archivos, 223 lineas de .diff.
- `patch --dry-run` OK sobre 6.10 puro y sobre el stack completo de parches OpenWrt 24.10 (001,002,010,201,202,205,206,300,960-0010,960-0011,988): solo offsets de 1 a 32 lineas. El `.diff` esta en el scratch `<tmp> (fuera del repo, no versionado).
- No toca `htt.h` ni `pci.c` (los archivos de los parches smallbuffers 960-*), asi que el recorte de ring (HTT_RX_RING_SIZE_MAX 512, CE dest 128/64/96) no cambia.
- Riesgo: MEDIO-BAJO en codigo (solo guardas y flujo de recovery, sin cambios de formato WMI/HTT), pero el recovery cambia comportamiento: agrega WEDGED terminal tras 4 fallos y quita `ATH10K_FLAG_RESTARTING`. Sin compilar: UNKNOWN. El bloque `recovery_check_work` resultante es identico al de 7.2 (verificado con diff).
- Alternativa minima aun: solo #1 y #3 (guardas puras, ~25 lineas, sin tocar recovery). Cubren los 2 crashes por NULL y no cambian el flujo de recovery.
- Cambio de base a 25.12.6: NO resuelve #1/#2/#3, trae el recovery de 6.18 con el bloqueo de 1.3, cambia opkg->apk, wifi shell->ucode, kernel 6.12 (STAGE3113A #13) e invalida el ledger de knobs. Ganancia de seguridad real, pero no de estabilidad del driver. Backport de los mismos ~100 lineas tambien haria falta en 25.12 (el parche de OpenWrt 25.12 sobre 6.18 aplicaria casi igual, no probado).
- Recomendacion (INFERRED, decide el operador): backport minimo a 24.10.4 para estabilidad (corto plazo) y salto de base 25.12.x por seguridad en paralelo, ambos con el mismo parche. Dependencia: ver 4 antes de decidir.

## 4. Hallazgo extra: el firmware CT tambien cambia en 25.12
- CONFIRMED (Makefile `package/firmware/ath10k-ct-firmware`): 24.10 = PKG_VERSION 2020.11.08, `firmware-2-ct-full-community-22.bin.lede.022`. 25.12 = 2023.04.04, `firmware-2-ct-full-community.bin` desde `candelatech.com/downloads/ath10k-fw-beta`. Commit `cb24806f` (2025-08-23): "update qca988X firmware to latest beta version"; nota: "Attempt to fix crash in scanning logic by making probe_timer ignore re-arm".
- CONFIRMED: nuestro firmware es el de 24.10 (2020.11.08). El crash de scan en firmware beta es un fix de QCA988x que ningun parche de driver da.
- UNKNOWN: compatibilidad del blob beta con el driver 6.10 (flags de features en `firmware-2.bin`) y diferencia de comportamiento RF/rate; se puede probar solo en banco, instalando el firmware en un 24.10.4 (el paquete es independiente del kmod). No hay release notes de ganancia de rate/retries para QCA988x, solo ese fix de scan.

## 5. Tarjetas siguientes (gate del operador; nada ejecutado)
1. Escritorio: compilar el backport con el SDK/ImageBuilder 24.10.4 (build kmod smallbuffers con el parche como `package/kernel/ath10k-ct/patches/9xx`). Criterio: build OK sin warnings nuevos, tamano del .ipk vs actual.
2. Banco (LAP-120 `.20`, Loco `.250`, con watchdog de auto-revert, nunca mtd0/1/5): A = actual, B = backport. Provocar crash de FW (debugfs `ath10k/simulate_fw_crash`) N veces y contar recuperaciones, `firmware crashed`, tiempo hasta trafico y mensajes `previous recovery`/`consecutive fail`/WEDGED. Sin umbrales inventados: decidir solo si B no es peor que la varianza A/A.
3. Banco: B2 = B + firmware 2023.04.04 beta; mismo A/B, ademas goodput/retries por STA (STAGE3113A tarjeta 1).
4. Si se usan fixed-rate por STA (`iw set bitrates`), probar con >=2 STA VHT para el caso `iterate_stations`.

## Limites
- 7.2 es main de ath10k-ct de 2026-07-31; 25.12.6 usa 6.18. No vimos el kernel/mac80211 de 25.12 (backports 6.18.55) contra 24.10 (6.12.96) mas alla de las versiones de Makefile.
- Los crashes que motivaron los fixes (1/4/2026) vienen de comentarios del codigo, sin trazas ni reportes: no sabemos si pasan en nuestro hardware (ath79 + QCA988x); no hay evidencia propia de `firmware crashed` en el repo en esta tarea (no se buscó).
