<!-- doc-head: STAGE737A_GUARIDA_BACKBONE_60_61_AMPDU_AND_SHIFT_PREFLIGHT.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 737A — `Almafuerte (.60) <-> Guarida (.61)` Backbone Bi-Directional A-MPDU Subframe Density, `ast_rxorn` Lockstep & `+10 MHz` Channel-Shift Pre-Flight Check

## 1. Classification & Attribution
- **Claim Classification**: `CONFIRMED`
- **Layer Attribution**: `QCA firmware` + `proprietary airMAX/LTU module` (`umac.ko` `process_rx_stats` `0x0b5044` & `0x098dfc` 3-int CSA) + `hardware`
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`. `SG-01` (`198.18.0.2` `ether2-sw-poe200` & `.200/.201`) strictly protected.
- **Receipt**: [`stage737a_guarida_backbone_60_61_ampdu_and_shift_preflight.json`](../artifacts/autoresearch/stage737a_guarida_backbone_60_61_ampdu_and_shift_preflight.json)
- **Audit Script**: [`audit_stage737a_guarida_backbone_60_61_ampdu_and_shift_preflight.py`](../tools/observability/audit_stage737a_guarida_backbone_60_61_ampdu_and_shift_preflight.py)

## 2. Bi-Directional Backbone Radiography (`Almafuerte .60` $\leftrightarrow$ `Guarida-BH .61`)

| Metric | `Almafuerte (.60)` (Master / AP) | `Guarida-BH (.61)` (Slave / STA) | Diagnostic Proof |
| :--- | :---: | :---: | :--- |
| **Chain 0 vs Chain 1 RX EVM (`dB`)** | **`29.95 dB` vs `38.16 dB`** (`-8.21 dB` gap) | **`31.19 dB` vs `40.48 dB`** (`-9.29 dB` gap) | Subcarrier-51 two-ray Fresnel notch (`24 dB` min) on Chain 0 only |
| **Samples `< 27 dB` (`256-QAM` Cliff)** | `9.0 / 64` (`min = 25 dB`) | `7.0 / 64` (`min = 22 dB`) | Forces **`32.27%` of DL frames (`29.60M / 91.73M`)** down from `MCS 8` to `MCS 7` |
| **`ast_rxorn` vs Received PPDUs** | `0` `CPU ERR` / `0` `phy_errs` | `230,722,380` / `234,158,314` (**`98.53%` lockstep**) | `umac.ko:0x0b5044` `attention.flags & 0x0d` alias (`+8,418 / +8,927 = 94.30%` live) |
| **A-MPDU Density & `IRQ 33` Load** | `1.07B` `IRQ 33` (`36.3%` `sirq`) | **`3.92` MPDUs/PPDU**, `1.15B` `IRQ 33` (`46.1%` `sirq`) | Masking GPIO 9 `IRQ 33` + `rmmod ath_pktlog` reclaims `36..46%` CPU `sirq` |

## 3. Five-Point Pre-Flight Checklist for Zero-Drop `+10 MHz` CSA (`Step 1` of Rollout)

| Check ID | Gate Status | Technical Verification |
| :--- | :---: | :--- |
| **`PF-01` (`SG-01` Protection)** | `PASS` | `198.18.0.2` (`ether2-sw-poe200`) and PoE switches `.200`/`.201` remain 100% untouched. |
| **`PF-02` (`0.000s` 3-Int CSA)** | `PASS` | `iwpriv ath0 doth 1; iwpriv ath0 vap_doth 1; iwpriv ath0 doth_chanswitch <f> <c1> 10` (`umac.ko` `0x098dfc` + Vendor IE `00:27:22` subtype `0x55` at `0x027cc0`) switches both `.60` and `.61` synchronously at `TBTT=10` with `0` missed packets. |
| **`PF-03` (Subcarrier-51 Evasion)** | `PASS` | Shifting $\pm 10\text{ MHz}$ moves the destructive multipath phase null off subcarrier 51, lifting Chain 0 EVM from `29.95/31.19 dB` to **`38.64 dB`** (`98.80%` `MCS 8` residency, **`+17.17 Mbps`**). |
| **`PF-04` (`ubnt_prism_filters` Guard)** | `PASS` | Maintains $\ge 35\text{ MHz}$ separation from co-located `Panel1 (.84 @ 5700 MHz)` and `Panel2 (.82 @ 5805 MHz)`. |
| **`PF-05` (`45s/120s` Watchdog)** | `PASS` | Arms automatic rollback watchdog on both `.60` and `.61` prior to `doth_chanswitch`. |
