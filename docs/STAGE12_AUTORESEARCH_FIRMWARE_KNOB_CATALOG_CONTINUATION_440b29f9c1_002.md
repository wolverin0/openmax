<!-- doc-head: STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG.md continuation 2 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG.md) | Part 2/3
<a id="stage12--catálogo-offline-de-controles-de-firmware"></a> [Stage12 — catálogo offline de controles de firmware](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#stage12--catálogo-offline-de-controles-de-firmware) | <a id="alcance-y-procedencia"></a> [Alcance y procedencia](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#alcance-y-procedencia) | <a id="cómo-interpretar-una-cota"></a> [Cómo interpretar una cota](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#cómo-interpretar-una-cota) | <a id="lectura-del-autoresearch-suministrado"></a> [Lectura del autoresearch suministrado](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#lectura-del-autoresearch-suministrado) | <a id="mac80211-ath10k-y-htt"></a> [mac80211, ath10k y HTT](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#mac80211-ath10k-y-htt) | <a id="ct_special-ids316"></a> [`ct_special` IDs3..16](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#ct_special-ids316) | <a id="wmi-pdevvdev101"></a> [WMI pdev/vdev10.1](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#wmi-pdevvdev101) | <a id="waxc-sysctl-módulos-e-ioctls"></a> [WA/XC: sysctl, módulos e ioctls](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#waxc-sysctl-módulos-e-ioctls) | <a id="ltu242-sysfs-ame"></a> [LTU2.4.2: sysfs AME](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#ltu242-sysfs-ame) | <a id="límite-hardware-y-aceptación-pendiente"></a> [Límite hardware y aceptación pendiente](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#límite-hardware-y-aceptación-pendiente) | <a id="inventario-individual"></a> [Inventario individual](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#inventario-individual) | <a id="parámetros-wmi101-del-mapa-retenido"></a> [Parámetros WMI10.1 del mapa retenido](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#parámetros-wmi101-del-mapa-retenido) | <a id="wextioctl-xc8725"></a> [WEXT/ioctl XC8.7.25](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_003.md#wextioctl-xc8725) | <a id="atributos-ltu-ap-y-cpe242"></a> [Atributos LTU AP y CPE2.4.2](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_003.md#atributos-ltu-ap-y-cpe242) | <a id="wavea-tablas-exactas-wa8725-resueltas"></a> [WaveA: tablas exactas WA8.7.25 resueltas](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_003.md#wavea-tablas-exactas-wa8725-resueltas)

<!-- stage822a-payload-begin -->
| Miembro | ID10x usado por10.1 | Clasificación |
| --- | --- | --- |
|`tx_chain_mask`|`0x1`|excluded|
|`rx_chain_mask`|`0x2`|excluded|
|`txpower_limit2g`|`0x3`|excluded|
|`txpower_limit5g`|`0x4`|excluded|
|`txpower_scale`|`0x5`|excluded|
|`beacon_gen_mode`|`0x6`|characterization_only|
|`beacon_tx_mode`|`0x7`|characterization_only|
|`resmgr_offchan_mode`|`0x8`|characterization_only|
|`protection_mode`|`0x9`|characterization_only|
|`dynamic_bw`|`0xa`|characterization_only|
|`non_agg_sw_retry_th`|`0xb`|characterization_only|
|`agg_sw_retry_th`|`0xc`|characterization_only|
|`sta_kickout_th`|`0xd`|characterization_only|
|`ac_aggrsize_scaling`|`0xe`|characterization_only|
|`ltr_enable`|`0xf`|characterization_only|
|`ltr_ac_latency_be`|`0x10`|characterization_only|
|`ltr_ac_latency_bk`|`0x11`|characterization_only|
|`ltr_ac_latency_vi`|`0x12`|characterization_only|
|`ltr_ac_latency_vo`|`0x13`|characterization_only|
|`ltr_ac_latency_timeout`|`0x14`|characterization_only|
|`ltr_sleep_override`|`0x15`|characterization_only|
|`ltr_rx_override`|`0x16`|characterization_only|
|`ltr_tx_activity_timeout`|`0x17`|characterization_only|
|`l1ss_enable`|`0x18`|characterization_only|
|`dsleep_enable`|`0x19`|characterization_only|
|`pdev_stats_update_period`|`0x1a`|characterization_only|
|`vdev_stats_update_period`|`0x1b`|characterization_only|
|`peer_stats_update_period`|`0x1c`|characterization_only|
|`bcnflt_stats_update_period`|`0x1d`|characterization_only|
|`pmf_qos`|`0x1e`|excluded|
|`arp_ac_override`|`0x1f`|characterization_only|
|`dcs`|`0x20`|excluded|
|`ani_enable`|`0x21`|excluded|
|`ani_poll_period`|`0x22`|excluded|
|`ani_listen_period`|`0x23`|excluded|
|`ani_ofdm_level`|`0x24`|excluded|
|`ani_cck_level`|`0x25`|excluded|
|`dyntxchain`|`0x26`|excluded|
|`fast_channel_reset`|`0x27`|excluded|
|`burst_dur`|`0x28`|characterization_only|
|`burst_enable`|`0x29`|characterization_only|
|`cal_period`|`0x37`|excluded|

vdev: dominio wire `u32`, semántica y rango RAM seguro desconocidos; sin propuesta ni getter efectivo probado.

| Miembro | ID10x usado por10.1 | Clasificación |
| --- | --- | --- |
|`rts_threshold`|`0x1`|characterization_only|
|`fragmentation_threshold`|`0x2`|characterization_only|
|`beacon_interval`|`0x3`|characterization_only|
|`listen_interval`|`0x4`|characterization_only|
|`multicast_rate`|`0x5`|characterization_only|
|`mgmt_tx_rate`|`0x6`|characterization_only|
|`slot_time`|`0x7`|characterization_only|
|`preamble`|`0x8`|characterization_only|
|`swba_time`|`0x9`|characterization_only|
|`wmi_vdev_stats_update_period`|`0xa`|characterization_only|
|`wmi_vdev_pwrsave_ageout_time`|`0xb`|characterization_only|
|`wmi_vdev_host_swba_interval`|`0xc`|characterization_only|
|`dtim_period`|`0xd`|characterization_only|
|`wmi_vdev_oc_scheduler_air_time_limit`|`0xe`|characterization_only|
|`wds`|`0xf`|characterization_only|
|`atim_window`|`0x10`|characterization_only|
|`bmiss_count_max`|`0x11`|characterization_only|
|`feature_wmm`|`0x12`|characterization_only|
|`chwidth`|`0x13`|characterization_only|
|`chextoffset`|`0x14`|characterization_only|
|`disable_htprotection`|`0x15`|excluded|
|`sta_quickkickout`|`0x16`|characterization_only|
|`mgmt_rate`|`0x17`|characterization_only|
|`protection_mode`|`0x18`|characterization_only|
|`fixed_rate`|`0x19`|characterization_only|
|`sgi`|`0x1a`|characterization_only|
|`ldpc`|`0x1b`|characterization_only|
|`tx_stbc`|`0x1c`|characterization_only|
|`rx_stbc`|`0x1d`|characterization_only|
|`intra_bss_fwd`|`0x1e`|characterization_only|
|`def_keyid`|`0x1f`|excluded|
|`nss`|`0x20`|characterization_only|
|`bcast_data_rate`|`0x21`|characterization_only|
|`mcast_data_rate`|`0x22`|characterization_only|
|`mcast_indicate`|`0x23`|characterization_only|
|`dhcp_indicate`|`0x24`|characterization_only|
|`unknown_dest_indicate`|`0x25`|characterization_only|
|`ap_keepalive_min_idle_inactive_time_secs`|`0x26`|characterization_only|
|`ap_keepalive_max_idle_inactive_time_secs`|`0x27`|characterization_only|
|`ap_keepalive_max_unresponsive_time_secs`|`0x28`|characterization_only|
|`ap_enable_nawds`|`0x29`|characterization_only|
|`mcast2ucast_set`|`0x2a`|characterization_only|
|`enable_rtscts`|`0x2b`|characterization_only|
|`ap_detect_out_of_sync_sleeping_sta_time_secs`|`0x2d`|characterization_only|
|`rc_num_retries`|`0x2c`|characterization_only|

### UMAC XC8.7.25

Ruta base `/sys/module/umac/parameters/`. Todos excluidos de candidatos; dominio del parser, sin semántica ni rango seguro. WA se inventaría por separado desde su módulo exacto en WaveA.

| Nombre | Tipo del parser | Modo de tabla |
| --- | --- | --- |
|`ahbskip`|param_set_int / int32|`0o644`|
|`war1_allow_sleep`|param_set_int / int32|`0o644`|
|`war1`|param_set_int / int32|`0o644`|
|`bmi`|param_set_int / int32|`0o644`|
|`ubnt_radar_mode`|param_set_uint / uint32|`0o644`|
|`ubnt_op_mode`|param_set_uint / uint32|`0o644`|
|`is_ubnt_ff`|param_set_uint / uint32|`0o644`|
|`is_ubnt_ptp`|param_set_uint / uint32|`0o644`|
|`max_vdevs`|param_set_uint / uint32|`0o644`|
|`max_peers`|param_set_uint / uint32|`0o644`|
|`vow_config`|param_set_uint / uint32|`0o644`|
|`enable_tx_tcp_cksum`|param_set_uint / uint32|`0o644`|
|`tgdeb`|param_set_uint / uint32|`0o644`|
|`host_80211_enable`|param_set_uint / uint32|`0o644`|
|`msienable`|param_set_int / int32|`0o644`|

### UPH WA8.7.25 y XC8.7.25

Cada fila corresponde a dos entradas con hashes de módulos distintos. El máximo del buffer es sólo capacidad de almacenamiento, no una cota semántica. Rollback/propuestas no calificados.

<!-- stage822a-payload-end -->
