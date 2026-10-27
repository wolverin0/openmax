<!-- doc-head: Stage 639A Universal WA/XC/XW v16 SquashFS (180 hsqs Images) Bake (<220 lines) -->
`Stage 639A` empaqueta las `180` imágenes universales `WA/XC/XW v16` SquashFS (`hsqs`) integrando `Stage 637A` (`fmx_qca_txbf_stbc_ldpc_guard.sh`), `WA Champion v10` (`256` ventanas: `netdev_tstamp_prequeue=0`, `tcp_autocorking=0`, `tcp_recovery=1`, `tcp_thin_linear_timeouts=1`, `PB-050 v1` `4000ms`) y `Stage 605A` (`fmx_qca988x_wmi_peer_rate_sgi_guard.sh`).
<!-- /doc-head -->

# Stage 639A — Universal `WA/XC/XW v16` SquashFS (`180` `hsqs` Images) Bake (`mm-7445`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-7445`, `id=155460`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v16`)**: [`99-fmx-wa-universal-champion-v16`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v16) (`sha256: d125b3e88291827979c7bbf19c9e6db2f230c4c9ca730f3a3d1277e669e54926`).

## 1. Integrated Ground-Up `v16` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 637A` `TxBF`/`STBC`/`LDPC` Guard** | `firmware/openwrt/common/fmx_qca_txbf_stbc_ldpc_guard.sh` | Activa `LDPC=1` (`+1.5..2.0 dB` FEC en `256-QAM`) y `STBC=1` mientras desactiva `SU-TxBF` sounding en parábolas fijas `2x2` (`Stage 615A`). |
| **`WA Champion v10` (`256` Windows `PB-050 v1`)** | `netdev_tstamp_prequeue=0`, `aql_txq_limit=4000`, `tcp_thin_linear_timeouts=1` | Elimina latencia de pre-encolado de timestamps en `MIPS 74Kc` y acelera recuperación de flujos livianos (`VoIP`/`SSH`/`DNS`). |
| **`Stage 605A` `WMI_PEER_ASSOC` & `SGI` Guard** | `firmware/openwrt/common/fmx_qca988x_wmi_peer_rate_sgi_guard.sh` | Protege `peer_phymode`, `vht_mcs_set` y `_RATE_SetSGIMasks` (`Stage 589A`). |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
