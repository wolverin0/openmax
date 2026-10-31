<!-- doc-head: Stage 480A Guarida Backbone Almafuerte (.60) <-> Guarida-BH (.61) Subcarrier-51 Multipath Notch & 230.7M ast_rxorn Mitigation Kit -->
Documents the non-disruptive rescue kit (`rc.poststart_backbone_60_61_notch_rescue.sh`) for the `Almafuerte (.60) <-> Guarida-BH (.61)` backbone link, mitigating the `6.45 dB` Chain 0 multipath notch at subcarrier `51` (`Stage 419A`) and `230.7M` `ast_rxorn` RX FIFO overruns while strictly honoring `SG-01`.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 480A — Guarida Backbone (`.60 <-> .61`) Subcarrier-51 Multipath Notch & `230.7M` `ast_rxorn` Rescue Kit

- **Epistemic Status**: `CONFIRMED` (`Stage 419A` 64-subcarrier per-chain EVM radiography on `198.18.0.3` & `198.18.0.4`)
- **Attribution**: `hardware` (specular polarization-selective reflection on Chain 0) · `Linux` / `QCA firmware` (`ast_rxorn` NAPI drain)
- **Kit Script**: [`rc.poststart_backbone_60_61_notch_rescue.sh`](../firmware/guarida_safe_kits/rc.poststart_backbone_60_61_notch_rescue.sh) (`SHA-256: 1d8c4b9ff86e6ec9...`, strict `LF`)
- **JSON Receipt**: [`stage480a_guarida_backbone_60_61_subcarrier51_notch_rescue.json`](../artifacts/autoresearch/stage480a_guarida_backbone_60_61_subcarrier51_notch_rescue.json)

---

## 1. Stage 419A Subcarrier Radiography Diagnosis (`.60 <-> .61`)

Standard RSSI monitoring falsely reports the `Almafuerte (.60) <-> Guarida-BH (.61)` backbone as balanced (`signal = -54 dBm`, `rssi_chains = [39, 39]`). However, Stage 419A's 64-subcarrier `evm` dissection exposed a severe polarization-specific multipath notch:

| Radio Endpoint | Chain 0 Mean / Min EVM | Deepest Notch Subcarrier | Chain 0 Notch Depth | Chain 1 Mean / Min EVM | Chain 0 vs Chain 1 EVM $\Delta$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`Almafuerte (.60)`** | `30.45 dB` / **`24 dB`** | **Subcarrier `51`** | **`6.45 dB`** | `38.39 dB` / `37 dB` | **`-7.94 dB` RX / `-7.54 dB` TX** |
| **`Guarida-BH (.61)`** | `31.02 dB` / **`26 dB`** | **Subcarrier `45`** | **`5.02 dB`** | `38.55 dB` / `38 dB` | **`-7.53 dB` RX / `-7.54 dB` TX** |

Because a horizontal/vertical specular reflection (e.g., parapet or metal roof edge along the `.60 <-> .61` Fresnel path) cancels Chain 0 around subcarriers `45..51` while leaving Chain 1 flat at `38.5 dB`, `400 ns` Short Guard Interval (`SGI`) bursts suffer inter-symbol interference (`ISI`) and trigger massive Block-ACK re-sequencing alongside **`230.7M` cumulative `ast_rxorn` (RX FIFO overrun)** events.

---

## 2. Two-Layer Non-Disruptive Rescue (`SG-01` Safe)

1. **Layer 1 — `230.7M` `ast_rxorn` RX FIFO Overrun Cure**:
   - Doubles host NAPI drain capacity (`net.core.netdev_budget=600`, `net.core.dev_weight=128`, `net.core.netdev_max_backlog=4096`, `rmem_max=524288`, `txqueuelen=512`) so the MIPS CPU drains `QCA988x` RX DMA rings before hardware FIFO exhaustion occurs.
2. **Layer 2 — Subcarrier-51 Specular Multipath ISI Guard**:
   - Enforces **`800 ns` Long Guard Interval (`iwpriv ath0 shortgi 0`)** while preserving `2x2` `MRC` (`rxchainmask=3`, `txchainmask=3`) and clearing `uph_wifi0/flags` bit `0x2000` (`6672`).
