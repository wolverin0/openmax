<!-- doc-head: STAGE192A_HAL_WMI_ACCESSOR_AND_340KNOB_SINKS.md preserved document content -->
<!-- /doc-head -->


# Stage 192A — `ath_hal.ko` / `umac.ko` Vtable Accessor & `340`/`437` Knob Sinks (`CONFIRMED`)

## 1. Executive Summary & Attribution
- **Claim Status**: `CONFIRMED` (`live_devices_touched = False`; 100% offline ELF relocation & jump-table dissection).
- **Attribution**: `proprietary airMAX/LTU module` + `QCA firmware` + `hardware`.
- **Complete Coverage**: Traced all **`340` `airos_ioctl + hardware` knobs (`339` `airos_ioctl` + `1` `hardware`)** and all **`437` `airOS_UMAC_UPH` knobs (`339` `airos_ioctl` + `68` `airos_sysctl` + `30` `airos_module` = `438` total)** in `orchestration/autoresearch/firmware_knob_candidates.json`.

## 2. The 4 Indirect Vtable & Jump-Table Accessors (`CONFIRMED`)
1. **`ath_hal.ko` MMIO Register Accessor (`ath_hal_reg_write` @ `.text+0x00000c` & `ath_hal_reg_read` @ `.text+0x000020`)**:
   - `0x00000c`: `lw $v0, 0x3bc($a0); addu $a1, $v0, $a1; sw $a2, ($a1); jr $ra` (`*(volatile u32 *)(ah->ah_sh + reg_off) = val`).
   - `0x000020`: `lw $v0, 0x3bc($a0); addu $a1, $v0, $a1; lw $v0, ($a1); jr $ra` (`return *(volatile u32 *)(ah->ah_sh + reg_off)`).
   - **`ar9300_hal_template` Vtable (`.rodata+0x06b8..0x0a38`, `224` methods, `ah_offset = rodata_off - 0x06b0`)**:
     - `ah+0x108` (`.rodata+0x07b8`): `ar9300_get_capability` (`0x011d78`); `ah+0x10c` (`.rodata+0x07bc`): `ar9300_set_capability` (`0x012250`).
     - `ar9300_set_slot_time` (`0x011904`): writes **`AR_D_GBL_IFS_SLOT` (`0x1070`)** + shadow `0xde4($ah)`.
     - `ar9300_set_ack_timeout` (`0x0119a8`): RMWs **`AR_TIME_OUT` (`0x8014`, bits `[13:0]`)** + shadow `0xde8($ah)`.
     - `ar9300_set_cca_threshold` (`0x020c4c`): RMWs **`AR_PHY_CCA_0` (`0x9e1c`, bits `[18:12]`)** & **`AR_PHY_CCA_1` (`0x9e20`, bits `[7:0]`)**.
     - `ar9300_adjust_difs` (`0x025cb0`): writes **`AR_DLCL_IFS(0..3)` (`0x1040..0x104c`)** across WMM queues `0..3`.
2. **`ath_dev.ko` `sc_ops` Vtable (`ath_dev_attach` @ `.text+0x00f3bc..0x00fb5c` & `ath_set_config` @ `.text+0x0234c8`)**:
   - `0x00faf0..0x00fb04` binds `sc_ops->get_config_param = ath_get_config` (`0x023d10`) at **`sc_ops+0x208`** and `sc_ops->set_config_param = ath_set_config` (`0x0234c8`) at **`sc_ops+0x20c`**.
   - `ath_set_config` (`0x0234c8`) dispatches **`217` cases** via `.rodata+0x000d60`, loads `sc->sc_ah` (`lw $a0, 0x2980($a0)` at `0x023514`), and calls `ar9300_hal_template` (`jalr` on `0x108($ah)` / `0x10c($ah)`).
3. **`umac.ko` Offload WMI & HTT Dispatchers (`QCA988x`)**:
   - `wlan_set_param` (`0x003210`): `155`-slot jump table at `.rodata+0x000300` (`99` active cases) -> updates `vap`/`ic` shadow and calls `ic->ic_vap_set_param` (`ol_ath_vap_set_param` `0x0ad820`) or `sc_ops+0x20c` (`ath_set_config`).
   - `ol_ath_vap_set_param` (`0x0ad820`): `155`-slot jump table at `.rodata+0x0c870` (`37` active cases) -> `wmi_unified_vdev_set_param_send` (`0x0ad77c`, **`WMI_VDEV_SET_PARAM_CMDID = 0x901a`**).
   - `ol_ath_set_config_param` (`0x0b3308`): `161`-slot jump table at `.rodata+0x0d620` (`58` active cases) -> `wmi_unified_pdev_set_param` (`0x0a80f4`, **`WMI_PDEV_SET_PARAM_CMDID = 0x9006`**), `ol_ath_set_distance` (`0x0b3058`, **`0x905b`**), `ol_ath_set_wlan_pll` (`0x0b3148`, **`0x9061`**), and `ol_txrx_set_aggr_cfg` (`0x0d2f44` -> `htt_h2t_aggr_cfg_msg` `0x0d5a2c`, **`HTT_H2T_MSG_TYPE_AGGR_CFG = 0x07`**).
   - `__wmi_unified_cmd_send` (`0x0c21e0`): prepends 4-byte WMI command ID, allocates HTC cookie (`0x0b2ee8`), and calls `HTCSendPkt` (`0x0c5bdc`).
4. **`ubnt_poll_host.ko` Sysctl -> `HT_COMM` WMI `0x9065` Sink (`68` `airos_sysctl` knobs)**:
   - Sysctl handler `.text+0x002138` branches on `write != 0` (`0x002150 -> 0x00232c`), calling `ubnt_poll_host_ht_comm_tx` (`0x001080`) -> `umac.ko` `0x0b4910` (**`WMI_UBNT_HT_COMM_CMDID = 0x9065`**) into `athwlan_AR9888v2_*_bin`.

## 3. Sink Breakdown Across All `340` (`438` Total) Knobs (`CONFIRMED`)
| Sink Category | Knob Count | Primary Dispatcher & Target Sink |
| :--- | :---: | :--- |
| `HARDWARE_REGISTER_SINK` | `1` | Resolved in `stage192a_hal_wmi_accessor_and_340knob_sinks.json` |
| `KERNEL_MODULE_PARAM_TO_ATTACH_INIT` | `30` | Resolved in `stage192a_hal_wmi_accessor_and_340knob_sinks.json` |
| `RADIO_IOCTL_TO_WMI_PDEV_0x9006_AND_ATH_HAL_VTABLE` | `310` | Resolved in `stage192a_hal_wmi_accessor_and_340knob_sinks.json` |
| `UPH_SYSCTL_TO_HT_COMM_WMI_0x9065` | `68` | Resolved in `stage192a_hal_wmi_accessor_and_340knob_sinks.json` |
| `VAP_IOCTL_TO_UMAC_STATE_AND_SC_OPS` | `29` | Resolved in `stage192a_hal_wmi_accessor_and_340knob_sinks.json` |
