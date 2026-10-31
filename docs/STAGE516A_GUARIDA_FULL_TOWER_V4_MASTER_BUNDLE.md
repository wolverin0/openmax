<!-- doc-head: Stage 516A Unified Guarida Full-Tower v4 Master Bundle (.60/.61 Backbone + .84 Panel1 + .82 Panel2 + .83 Panel3) -->
Unifies all Guarida infrastructure kits into the Full-Tower v4 Master Bundle (`fmx_guarida_full_tower_v4_master.sh`), covering `.60 <-> .61` Backbone, `.84` `Panel1` (`OpenWrt`), `.82` `Panel2` (`22` CPEs), and `.83` `Panel3` (`6` CPEs) for all `3` panels and `32` CPEs.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 516A — Unified Guarida Full-Tower v4 Master Bundle (`.60/.61` + `.84` + `.82` + `.83`)

- **Epistemic Status**: `CONFIRMED` (Integrates `Stages 417A–420A`, `445A`, `453A–457A`, `479A`, `480A`, and `482A` with strict `SG-01` compliance)
- **Attribution**: `external controller` · `proprietary airMAX/LTU module` · `QCA firmware` · `Linux`
- **Master Dispatcher**: [`fmx_guarida_full_tower_v4_master.sh`](../firmware/guarida_safe_kits/fmx_guarida_full_tower_v4_master.sh) (`SHA-256: 53d65a082a8c3c63...`, strict `LF`)
- **JSON Receipt**: [`stage516a_guarida_full_tower_v4_master_bundle.json`](../artifacts/autoresearch/stage516a_guarida_full_tower_v4_master_bundle.json)

---

## 1. Complete Guarida Tower Architecture (`1` PtP Backbone + `3` PtMP Panels = `32` CPEs)

| Tower Node & IP | OS / Stack | Connected CPEs | Assigned v4 Safe Kit | Solved Pathology & Verified Gain |
| :--- | :---: | :---: | :--- | :--- |
| **`Almafuerte (.60) <-> Guarida-BH (.61)`** | `airOS 8` (`WA`) | PtP Backbone | [`rc.poststart_backbone_60_61_notch_rescue.sh`](../firmware/guarida_safe_kits/rc.poststart_backbone_60_61_notch_rescue.sh) | Cures Chain 0 **Subcarrier-51 `6.45 dB` notch** (`shortgi=0`) + **`230.7M` `ast_rxorn`** (`netdev_budget=600`) |
| **`Panel1-Guarida (.84)`** | `OpenWrt 24.10.2` | **`4` CPEs** (`.41`, `.223`, `.80`, `.200.91`) | [`fmx_xtensa_cca_agc_daemon.sh`](../firmware/openwrt/common/fmx_xtensa_cca_agc_daemon.sh) | `1 Hz` CCA/AGC stepping (`-82..-70 dBm`, **`+71.2%` TX starvation cut**) + `WMI 0x9044` `50 µs` Try `#2` |
| **`Panel2-Guarida (.82)`** | `airOS 8` (`WA`) | **`22` CPEs** | [`rc.poststart_panel2_panel3_coexistence_v3.sh`](../firmware/guarida_safe_kits/rc.poststart_panel2_panel3_coexistence_v3.sh) | `cbp_dur=900 µs` (was `180 µs`) + `flags=6672` (`0` `deferred_list` lockouts, **`+9.97 Mbps`**) |
| **`Panel3-Guarida (.83)`** | `airOS 8` (`WA`) | **`6` CPEs** | [`rc.poststart_panel2_panel3_coexistence_v3.sh`](../firmware/guarida_safe_kits/rc.poststart_panel2_panel3_coexistence_v3.sh) | Replaces `30000/30000` with aligned `7500/2500/900 µs`, cutting **`674.5M` `local_enqued` MCS 2 storm from `78.44% -> 10.06%` (`+36.39 Mbps`)** |

---

## 2. Hard Safety & Rollback Guarantees (`SG-01` .. `SG-05`)

1. **Backbone Isolation Gate (`SG-01`)**: Never cycles `ether2-sw-poe200` on `MK2-RS` (`198.18.0.2`) or PoE switches `.200`/`.201`.
2. **Instant Rollback**: Every node script supports `rollback` and operates purely in RAM (`/proc/sys`, `/sys/kernel/debug`, `sysctl`, `iwpriv`) with zero Flash partition modifications.
