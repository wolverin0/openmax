<!-- doc-head: Stage 351A universal WA v8 SquashFS bake integrating R1..R30 and chain-imbalance rescue daemon -->
Documenta el empaquetado criptográfico `SquashFS` (`hsqs` `v8`) en `198.18.0.62` dentro de `firmware/openwrt/wa_universal_kit_v8/` (`16` imágenes para `PBE-5AC-Gen2` `0xe3d6`, `LBE-5AC-Gen2` `0xe7f9`, `LAP-120` `0xe8e5` y `NS-5ACL` `0xe7fa`), integrando `99-fmx-wmm-dscp-qos` (`70.15 Mbps`), `gro_normal_batch=16`, `99-fmx-wa-universal-champion-v4` y `fmx_chain_imbalance_rescue_daemon.sh`.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 351A — Universal `WA v8` SquashFS Bake (`<memorymaster-id>`)

- **Claim Status**: `CONFIRMED` (`Linux` / `mac80211` / `ath10k`)
- **Memory-Master Claim**: `<memorymaster-id>` (`id=<id>`, `scope="project:futuramax"`)
- **Builder**: [`tools/firmware/build_stage351a_wa_squashfs_v8_bake.py`](../tools/firmware/build_stage351a_wa_squashfs_v8_bake.py)
- **Output Kit (`16` Images)**: [`firmware/openwrt/wa_universal_kit_v8/`](../firmware/openwrt/wa_universal_kit_v8/)
- **Artifact**: [`artifacts/autoresearch/stage351a_wa_squashfs_v8_bake.json`](../artifacts/autoresearch/stage351a_wa_squashfs_v8_bake.json)

## 1. Placas `WA` Cubiertas (`16` Imágenes `factory` + `sysupgrade` AP/STA)

| Placa Ubiquiti `WA` | `board.sysid` | OpenWrt `board_id` | Archivos `v8` Generados en `firmware/openwrt/wa_universal_kit_v8/` |
| :--- | :---: | :--- | :--- |
| `PBE-5AC-Gen2` | `0xe3d6` | `ubnt,powerbeam-5ac-gen2` | `openwrt-24.10.4-powerbeam-5ac-gen2-v8-{factory,sysupgrade}-{ap,sta}.bin` |
| `LBE-5AC-Gen2` | `0xe7f9`, `0xe3d8` | `ubnt,litebeam-ac-gen2` | `openwrt-24.10.4-litebeam-5ac-gen2-v8-{factory,sysupgrade}-{ap,sta}.bin` |
| `LAP-120` | `0xe8e5`, `0xe7f5` | `ubnt,lap-120` | `openwrt-24.10.4-lap-120-v8-{factory,sysupgrade}-{ap,sta}.bin` |
| `NS-5ACL` | `0xe7fa`, `0xe7f7` | `ubnt,nanostation-ac-loco` | `openwrt-24.10.4-nanostation-ac-loco-v8-{factory,sysupgrade}-{ap,sta}.bin` |

## 2. Componentes Integrados en el `SquashFS` (`hsqs` `v8`)

1. **`/etc/hotplug.d/net/99-fmx-wa-universal-champion` (`v4`)**: Incluye `gro_normal_batch=16`, `fq_limit=512`, `tcp_early_retrans=4`, `vm.min_free_kbytes=4096`, `eth0` BQL `4542/36288/600` y `aql_threshold=4000`.
2. **`/etc/uci-defaults/99-fmx-wmm-dscp-qos`**: Ganador `R25..R30` (`70.15 Mbps` Bulk TCP + IPTV + VoIP Triple-Play QoE) con mapeo `iw_qos_map_set` y `gro_normal_batch=16`.
3. **`/usr/sbin/fmx_chain_imbalance_rescue_daemon.sh` (`Stage 349A`)**: Conmutador automático `SIMO-TX / 2x2-MRC-RX` (`>= 6 dB` disparo / `< 3 dB` histéresis).
4. **`/usr/sbin/fmx_xtensa_ram_patch_loader.sh` (`Stage 347A`)**: Cargador en RAM volátil `/tmp/firmware-5.bin` (`0` escrituras en Flash).
5. **`/lib/modules/6.6.110/mac80211.ko` (`v3`) + `/usr/sbin/fmx_pbe5ac_admitter.sh` (`v2`) + `/usr/sbin/fmx_ptp_rollback_watchdog.sh`**.
