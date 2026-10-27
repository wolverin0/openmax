<!-- doc-head: STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG.md continuation 3 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG.md) | Part 3/3
<a id="stage12--catálogo-offline-de-controles-de-firmware"></a> [Stage12 — catálogo offline de controles de firmware](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#stage12--catálogo-offline-de-controles-de-firmware) | <a id="alcance-y-procedencia"></a> [Alcance y procedencia](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#alcance-y-procedencia) | <a id="cómo-interpretar-una-cota"></a> [Cómo interpretar una cota](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#cómo-interpretar-una-cota) | <a id="lectura-del-autoresearch-suministrado"></a> [Lectura del autoresearch suministrado](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#lectura-del-autoresearch-suministrado) | <a id="mac80211-ath10k-y-htt"></a> [mac80211, ath10k y HTT](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#mac80211-ath10k-y-htt) | <a id="ct_special-ids316"></a> [`ct_special` IDs3..16](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#ct_special-ids316) | <a id="wmi-pdevvdev101"></a> [WMI pdev/vdev10.1](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#wmi-pdevvdev101) | <a id="waxc-sysctl-módulos-e-ioctls"></a> [WA/XC: sysctl, módulos e ioctls](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#waxc-sysctl-módulos-e-ioctls) | <a id="ltu242-sysfs-ame"></a> [LTU2.4.2: sysfs AME](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#ltu242-sysfs-ame) | <a id="límite-hardware-y-aceptación-pendiente"></a> [Límite hardware y aceptación pendiente](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#límite-hardware-y-aceptación-pendiente) | <a id="inventario-individual"></a> [Inventario individual](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#inventario-individual) | <a id="parámetros-wmi101-del-mapa-retenido"></a> [Parámetros WMI10.1 del mapa retenido](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_001.md#parámetros-wmi101-del-mapa-retenido) | <a id="umac-xc8725"></a> [UMAC XC8.7.25](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_002.md#umac-xc8725) | <a id="uph-wa8725-y-xc8725"></a> [UPH WA8.7.25 y XC8.7.25](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_002.md#uph-wa8725-y-xc8725)

<!-- stage822a-payload-begin -->
| Ruta | Parser / buffer | Verdad de lectura estática |
| --- | --- | --- |
|`/proc/sys/dev/uph_wifi0/set_host_diag`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/set_diag`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/get_diag`|proc_dointvec / 4B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/get_host_diag`|proc_dointvec / 4B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/enable`|proc_dointvec / 4B|Copies context byte+0xc4 into diagnostic scratch; formats integer vector; no hardware command.|
|`/proc/sys/dev/uph_wifi0/timing`|proc_dointvec / 64B|Copies context halfwords+0xc6/+0xc8/+0xca into diagnostic scratch; formats integer vector; no hardware command.|
|`/proc/sys/dev/uph_wifi0/gqparam`|proc_dointvec / 4B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/sqparam`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/status`|proc_dointvec / 4B|Copies radio-state byte+0x08 into diagnostic scratch; formats integer vector; no hardware command.|
|`/proc/sys/dev/uph_wifi0/hsr_diag`|proc_dostring / 2048B|Returns emptied local diagnostic scratch. Empty is not HSR-off evidence.|
|`/proc/sys/dev/uph_wifi0/get_reg`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/set_reg`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/ro`|proc_dointvec / 64B|Copies radio-state bytes+0x15e..0x166 into diagnostic scratch; formats integer vector; no hardware command.|
|`/proc/sys/dev/uph_wifi0/swr_limit`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/noack_mode`|proc_dointvec / 4B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/netconf`|proc_dostring / 2048B|Formats cached network statistics, then sends native stats request msg0x22; current output is not necessarily its reply.|
|`/proc/sys/dev/uph_wifi0/sta_priority`|proc_dostring / 2048B|Formats cached priority fields; no command dispatch.|
|`/proc/sys/dev/uph_wifi0/set_remote_host_diag`|proc_dostring / 2048B|Returns existing shared text scratch; node name does not execute its setter on read.|
|`/proc/sys/dev/uph_wifi0/set_remote_target_diag`|proc_dostring / 2048B|Returns existing shared text scratch; node name does not execute its setter on read.|
|`/proc/sys/dev/uph_wifi0/debug_block_sta`|proc_dostring / 2048B|Returns existing shared text scratch; node name does not execute its setter on read.|
|`/proc/sys/dev/uph_wifi0/evm_meas_config`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/debug_tid`|proc_dostring / 2048B|Returns existing shared text scratch; node name does not execute its setter on read.|
|`/proc/sys/dev/uph_wifi0/atpc`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/cms_bias`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/ff_cap_rep`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/voip_bias`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/ptp_xmit`|proc_dointvec / 4B|Copies context byte+0xd7 into diagnostic scratch; formats integer vector; no hardware command.|
|`/proc/sys/dev/uph_wifi0/fixed_frame`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/sta_rx_rssi_th`|proc_dointvec / 64B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph_wifi0/daprot`|proc_dointvec / 4B|Formats existing shared integer/vector scratch; does not dispatch the node-named setter/query. Output may be stale or from a different prior selector.|
|`/proc/sys/dev/uph/addradio`|proc_dostring / 128B|Returns empty local command scratch; does not add a radio.|
|`/proc/sys/dev/uph/gpsreset`|proc_dointvec / 4B|Returns reset scratch0 without calling GPS reset.|
|`/proc/sys/dev/uph/gps_info`|proc_dostring / 256B|Returns cached GPS information buffer; no reset or radio-add dispatch.|

### WEXT/ioctl XC8.7.25

Descriptores retenidos de UMAC/ath_dev XC; sin traslado al UMAC WA distinto. Conteo de argumentos no equivale a rango de configuración. Los getters no prueban enforcement en firmware. La tabla WA completa está en el catálogo JSON con su fuente exacta y se resume al final.

| Superficie | Entrada / salida en descriptor | Hipótesis |
| --- | --- | --- |
|`iwpriv ath<VAP> noackpolicy`|3 / 0 int32|ACK/retry/protection policy can trade airtime against delivery and tail latency; descriptor counts do not prove effect.|
|`iwpriv ath<VAP> get_noackpolicy`|2 / 1 int32|ACK/retry/protection policy can trade airtime against delivery and tail latency; descriptor counts do not prove effect.|
|`iwpriv ath<VAP> ff`|1 / 0 int32|Aggregation/fast-frame control may change amortized airtime and queue delay; ioctl ff is not UPH fixed_frame TDMA timing.|
|`iwpriv ath<VAP> get_ff`|0 / 1 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> mcast_rate`|1 / 0 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> get_mcast_rate`|0 / 1 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> ampdu`|1 / 0 int32|Aggregation/fast-frame control may change amortized airtime and queue delay; ioctl ff is not UPH fixed_frame TDMA timing.|
|`iwpriv ath<VAP> get_ampdu`|0 / 1 int32|Aggregation/fast-frame control may change amortized airtime and queue delay; ioctl ff is not UPH fixed_frame TDMA timing.|
|`iwpriv ath<VAP> maxampdu`|1 / 0 int32|Aggregation/fast-frame control may change amortized airtime and queue delay; ioctl ff is not UPH fixed_frame TDMA timing.|
|`iwpriv ath<VAP> get_maxampdu`|0 / 1 int32|Aggregation/fast-frame control may change amortized airtime and queue delay; ioctl ff is not UPH fixed_frame TDMA timing.|
|`iwpriv ath<VAP> vhtmaxampdu`|1 / 0 int32|Aggregation/fast-frame control may change amortized airtime and queue delay; ioctl ff is not UPH fixed_frame TDMA timing.|
|`iwpriv ath<VAP> get_vhtmaxampdu`|0 / 1 int32|Aggregation/fast-frame control may change amortized airtime and queue delay; ioctl ff is not UPH fixed_frame TDMA timing.|
|`iwpriv ath<VAP> amsdu`|1 / 0 int32|Aggregation/fast-frame control may change amortized airtime and queue delay; ioctl ff is not UPH fixed_frame TDMA timing.|
|`iwpriv ath<VAP> get_amsdu`|0 / 1 int32|Aggregation/fast-frame control may change amortized airtime and queue delay; ioctl ff is not UPH fixed_frame TDMA timing.|
|`iwpriv ath<VAP> set11NRates`|1 / 0 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> get11NRates`|0 / 1 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> set11NRetries`|1 / 0 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> get11NRetries`|0 / 1 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> basicrates`|1 / 0 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> vhtmcs`|1 / 0 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> get_vhtmcs`|0 / 1 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> enablertscts`|1 / 0 int32|ACK/retry/protection policy can trade airtime against delivery and tail latency; descriptor counts do not prove effect.|
|`iwpriv ath<VAP> get_enablertscts`|0 / 1 int32|ACK/retry/protection policy can trade airtime against delivery and tail latency; descriptor counts do not prove effect.|
|`iwpriv ath<VAP> rc_retries`|1 / 0 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> get_rc_retries`|0 / 1 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> bcast_rate`|1 / 0 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> get_bcast_rate`|0 / 1 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> vht_mcsmap`|1 / 0 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv ath<VAP> get_vht_mcsmap`|0 / 1 int32|WEXT private ioctl descriptor exposes a host setting/query; firmware consumption and per-frame enforcement remain unqualified.|
|`iwpriv wifi0 distance`|Ejemplo600; unidades/rangoUNKNOWN|Propagation/ACK timing input follows a proprietary ioctl path; not interchangeable with mac80211 coverage class.|

### Atributos LTU AP y CPE2.4.2

Cada fila tiene una entrada por build, con hashes y offsets distintos. Para todos, rango seguro/propuesta son null; exige restauración acoplada y retención diferida.

| Atributo | Encoding de host | Hipótesis |
| --- | --- | --- |
|`autoMcsCeiling`|base0 ->uint8 modulo256 ->hook+0x68|Constrain automatic MCS ceiling; changes can trade link margin/retries against spectral efficiency.|
|`adj_mcs`|base0 signed32 ->hook+0x114;core hardware guards apply|Select fixed/global MCS; scheduler fallback and delayed retention can undo an apparent immediate setting.|
|`autoMcs4096`|base0 signed32 pointer ->hook+0x70; semantic units UNKNOWN|Unknown scalar affects4096-QAM control; not proven an enable bit or timing unit.|
|`cpe_mcs`|three base0 fields ->uint16 peer,uint8 rate,uint8 operation;hook+0x120|Per-peer MCS/action tuple; cannot substitute global or mixed-MCS syntax.|
|`adj_mix_mcs`|six base0 fields each truncateduint8;hook+0x5f0|Six-field mixed-MCS policy; interactions with peer/FPGA/training remain unqualified.|
|`adj_mimo`|base0 signed32 ->hook+0x128|Adjust spatial-stream/MIMO mode; association, training and link margin can change.|
|`ofdma_en`|base0 ->uint8 modulo256 ->boolean;hook+0x274|Potential multiuser scheduler enable hook; empty show output prevents exact state/rollback verification.|
|`ofdma_subbands`|base0 ->uint8 modulo256;11111111 decimal becomes0xc7, not0xff;hook+0x280|RX/MRX subband reception mask in the retained core path; mask state alone is not multiuser allocation, OFDMA waveform or concurrent-user proof.|
|`ofdma_subband0_hdrIdx`|native base0 multi-field handler; detailed domains UNKNOWN|Header/subband control tuple; semantic layout and reversible range unknown.|
|`ldpc_iteration`|base0 ->uint8 modulo256;hook+0x430|Decoder work/latency tradeoff; iteration bounds, CPU/FPGA effect and hardware applicability unknown.|

### WaveA: tablas exactas WA8.7.25 resueltas

La extracción completa contiene696 archivos regulares verificados;244 enlaces y un dispositivo quedan sólo en metadata. El [informe WA/LTU](STAGE12_WA_UMAC_AND_LTU_STATE_MACHINE_RE.md) liga módulos, comparación8.7.4-cs, tablas y límites. `ubnt_spectral.ko` no aparece en la imagen; `ath_spectral.ko` es otro nombre observado, sin sustitución silenciosa. El contenedor8.7.4-cs no está disponible: la comparación usa su SquashFS retenido.

| Parámetro UMAC WA | Dominio del parser | Modo |
| --- | --- | --- |
| `ahbskip`, `war1_allow_sleep`, `war1`, `bmi`, `msienable` | signed32 |0644 |
| `ubnt_radar_mode`, `ubnt_op_mode`, `is_ubnt_ff`, `is_ubnt_ptp`, `max_vdevs`, `max_peers`, `vow_config`, `enable_tx_tcp_cksum`, `tgdeb`, `host_80211_enable` | unsigned32 |0644 |

Dominios signed32/unsigned32 son almacenamiento y parsing, no cotas físicas seguras. `ubnt_radar_mode` queda excluido. Los309 registros WEXT (290 nombrados,19 dispatchers) conservan selector y ambos descriptores de argumentos; aliases como chwidth70/122 siguen separados. Los34 nodos UPH vuelven a ligarse a la extracción exacta. Todos los registros actuales, offsets y42 hashes están en el JSON; las tablas XC/LTU anteriores se conservan con su propia versión. La [expansión reproducible](../artifacts/autoresearch/waves_abcd_20261024/expand_wave_a_catalog.py) parte de las248 entradas congeladas; el generador del primer audit es histórico y no debe sustituir este catálogo571.
<!-- stage822a-payload-end -->
