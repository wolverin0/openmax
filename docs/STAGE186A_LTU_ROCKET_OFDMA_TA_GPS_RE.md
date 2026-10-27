<!-- doc-head: STAGE186A_LTU_ROCKET_OFDMA_TA_GPS_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 186A: Binary RE of LTU Rocket AP (`aflturocket_2.4.2`) OFDMA, Timing Advance & GPS Sync

## 1. Binary Provenance (`CONFIRMED` — Attribution: `proprietary airMAX/LTU module`)
- **AP `ame_core.ko`**: `3318764` bytes, SHA-256 `a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af` (`2627` functions, `331` objects).
- **AP `cds_mac_mod.ko` (`eab_driver`)**: `145332` bytes, SHA-256 `883a8c29b8fd3c58a29f1e76ece68178b415540c263679c95e12b6df6953369c` (`325` functions).
- **Safety**: 100% static on-disk ELF32 ARMv7 dissection; zero touches on `/dev/ame*` or `.241`/`.242`/`.20`/`.250`.

## 2. OFDMA Subchannel Allocation & `0x9898` MAP Ring (`CONFIRMED`)
- **Subchannel Grid**: LTU partitions `10..100 MHz` channels into `2.0 MHz` OFDMA subchannels (`5` subchannels at `10 MHz`, `10` at `20 MHz`, `20` at `40 MHz`, `50` at `100 MHz`) over `25 us` symbols.
- **MAP Broadcast**: `ame_core.ko` (`send_map_enable=1`, `sched_max_agg_cnt`, `sched_mcs_limit_symbol_begin=12`, `sched_ap_mcs_limit_symbol_end=62`, `sched_mcs_limit_symbol_end=72`) schedules per-CPE DL/UL resource blocks and injects MAP frames through `cds_mac_mod.ko` (`0x9898` EtherType ring).

## 3. Uplink Timing Advance (`TA`) & Cyclic Zone (`czlen`) (`CONFIRMED`)
- **Closed-Loop Ranging & TA**: AP tracks each CPE's uplink arrival offset against the System Frame Number (`SFN`) boundary and sends Timing Advance (`TA`) adjustments so concurrent uplink OFDMA transmissions align inside the Cyclic Zone (`czlen=5`).
- **Cross-Frame Backoff**: Controlled by `/sys/module/ame_core/parameters/cz_cross_frame_backoff_enable`.

## 4. GPS 1PPS Superframe Phase Lock (`CONFIRMED`)
- **1PPS Discipline**: At `25 us/symbol`, `40`-symbol (`1.0 ms`), `80`-symbol (`2.0 ms`), and `160`-symbol (`4.0 ms`) superframes divide `1.0 s` into `1000`, `500`, and `250` exact superframes per GPS 1PPS edge, eliminating co-site DL/UL inter-AP interference when `duty_cycle` (`500`/`670`/`750`) matches.
