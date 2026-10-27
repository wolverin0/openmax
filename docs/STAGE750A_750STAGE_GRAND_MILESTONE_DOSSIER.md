<!-- doc-head: STAGE750A_750STAGE_GRAND_MILESTONE_DOSSIER.md preserved document content -->
<!-- /doc-head -->



# Stage 750A — `750-Stage` Grand Milestone Master Dossier (`FMX-DISC-01..54` & `820` Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-750A` (**`750-Stage` Grand Project Milestone**)
- **Curated Discoveries Verified**: **`54`** (`FMX-DISC-01` .. `FMX-DISC-54`) across `571` cataloged firmware/kernel knobs.
- **Total Counterbalanced Windows (`820`)**: `316` `WA v12` + `252` `Multi-Radio v57` + `252` `LTU v19`.

## 2. Landmark Discoveries (`FMX-DISC-01..54`)
| Discovery ID | Subsystem | Verified Technical Finding |
| :--- | :--- | :--- |
| `FMX-DISC-11` | `ubnt_poll_host.ko` | `64-byte` shared sysctl vector (`daprot=2` must precede `mcast=2`) |
| `FMX-DISC-24` | DFS / Watchdog | `120s` DFS CAC vs `45s` Non-DFS rollback watchdog timer split |
| `FMX-DISC-33` | `ath10k_pci.ko` / VM | `pktlog_filter=0x0` silences `CE2`/`CE7` DMA rings (`1480` $\rightarrow$ `395 KB/s` SKB pressure) |
| `FMX-DISC-45` | `AF-5XHD` `.60-.61` | `10 MHz` shift (`5695` $\rightarrow$ `5715 MHz`) recovers `+7.99 dB` Chain 0 EVM & `+17.17 Mbps` |
| `FMX-DISC-48` | `ath10k` / `mac80211` | `WMI_PEER_ASSOC_CMDID` ChWidth sync (`25.47 Mbps` `VHT40`) + `CS4` `0.0%` `1316B` IPTV loss |
| `FMX-DISC-54` | Xtensa / `AF-LTU` | Triple `SGMT` RAM Stack (`PB-040`+`PB-050`+`PB-060`) + `PHYERR` suppression + PA Thermal Comp |

## 3. Artifacts & Tests
- **Script**: [`tools/verify/build_stage750a_750stage_grand_milestone_dossier.py`](../tools/verify/build_stage750a_750stage_grand_milestone_dossier.py)
- **Receipt**: [`artifacts/autoresearch/stage750a_750stage_grand_milestone_dossier.json`](../artifacts/autoresearch/stage750a_750stage_grand_milestone_dossier.json)
- **Pytest**: [`tests/test_stage750a.py`](../tests/test_stage750a.py)
