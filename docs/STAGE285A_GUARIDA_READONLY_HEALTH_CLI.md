<!-- doc-head: STAGE285A_GUARIDA_READONLY_HEALTH_CLI.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 285A — Non-Disruptive Read-Only Guarida Tower Health Snapshot CLI (`snapshot_guarida_tower_health_readonly.py`)

- **Status**: `CONFIRMED`
- **Attribution**: `external controller` (Read-Only Observability CLI) + `proprietary airMAX/LTU module` + `mac80211`/`ath10k`
- **Safety Boundary**: `0` configuration or flash writes (`SG-01..05` compliant)
- **CLI Tool**: [`tools/verify/snapshot_guarida_tower_health_readonly.py`](../tools/verify/snapshot_guarida_tower_health_readonly.py)
- **Receipt**: [`artifacts/autoresearch/stage285a_guarida_readonly_health_cli_receipt.json`](../artifacts/autoresearch/stage285a_guarida_readonly_health_cli_receipt.json)

---

## 1. Purpose & `Stage 59A` Zero-False-Positive Integration (`CONFIRMED`)

`tools/verify/snapshot_guarida_tower_health_readonly.py` provides a single deterministic, non-disruptive (`writes_performed == 0`) health scorecard across all 5 Guarida / Almafuerte nodes (`.60`, `.61`, `.84`, `.82`, `.83`), incorporating both:
- **`FMX-DISC-43`**: `IRQ 33` (`SPECTRAL-XMIT-FILTER`) interrupt rates (`1,150..2,285 irq/s`, `4,532,825,836` cumulative interrupts) and `/etc/persistent/rc.poststart` presence check.
- **`FMX-DISC-44`**: De-aliased `athstats -ol` `QCA9882` `wal_dbg_stats` (`true_ol_mpdus_requed`, `true_ol_excess_retries`, `true_ol_ast_be_nobuf = 0`) alongside the legacy aliased `no_tx_buffer_count` (`multiqueue_sent[1]`).

---

## 2. 5-Node Guarida Tower Scorecard Summary (`CONFIRMED`)

| Node IP | Hostname / Role | SysID / FW | Freq / Width | `sirq%` | `IRQ 33/s` | True `mpdus_requed` (`athstats -ol`) | True `excess_retries` (`athstats -ol`) | Health State |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`198.18.0.3`** | `Ap.Guarida` (`Almafuerte` AP) | `0xe3d6` `WA.v8.7.25` | `5355 MHz` (`20 MHz`) | `36.3%` | `1,858/s` | `30,900,030` | `4,170,241` | `ONLINE_NEEDS_STAGE0_MODE_B` |
| **`198.18.0.4`** | `St.Guarida` (`Guarida` STA) | `0xe3d6` `WA.v8.7.25` | `5355 MHz` (`20 MHz`) | `46.1%` | `1,303/s` | `18,934,701` | `10,495,377` | `ONLINE_NEEDS_STAGE0_MODE_B` |
| **`198.18.0.7`** | `Panel1-Guarida` (`3/4` CPEs) | `0xe8e5` `OpenWrt 24.10.4` | `5735 MHz` (`20 MHz`) | `< 2%` | `0/s` | `0` (`fq_overlimit=0`) | `0` | `HEALTHY_OPENWRT_24_10_4_CHAMPION` |
| **`198.18.0.5`** | `Panel2-Guarida` (`21/22` CPEs) | `0xe8e5` `WA.v8.7.25` | `5765 MHz` (`20 MHz`) | `26.8%` | `1,150/s` | **`139,634,216` (`20.33%`)** | `23` | `ONLINE_HIGH_CONTENTION_NEEDS_STAGE0_AND_STAGE1` |
| **`198.18.0.6`** | `Panel3-Guarida` (`5/6` CPEs) | `0xe8e5` `WA.v8.7.25` | `5730 MHz` (`40 MHz`) | `33.3%` | `2,285/s` | `4,896,555` | **`9,506,061` (`15.11%`)** | `ONLINE_POLLING_DISABLED_IRQ33_STORM_NEEDS_STAGE0` |

---

## 3. Usage

```bash
python tools/verify/snapshot_guarida_tower_health_readonly.py
```
