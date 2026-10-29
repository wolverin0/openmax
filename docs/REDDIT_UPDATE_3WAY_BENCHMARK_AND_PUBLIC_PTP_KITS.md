<!-- doc-head: Copyable bilingual Reddit update (EN/ES) for r/wisp and openMAX GitHub: 3-way benchmark table, public PtP/PtMP scripts, and 18-node live read-back audit -->
<!-- /doc-head -->

# openMAX Reddit Update Draft (`r/wisp` + GitHub `wolverin0/openmax`)

Ready-to-paste snippets for the community thread (`https://www.reddit.com/r/wisp/comments/1xdpw2b/`), written with **zero internal network/tower/subscriber names** and **zero vulnerability/bounty content**.

---

## 1. Ready-to-Paste Reddit Comment Update (English)

```markdown
**Update (3 days later) — 3-Way Benchmark (Stock airOS 8 vs. Tuned airOS 8 vs. OpenWrt Champion), Public PtP/PtMP Scripts & 18-Radio Live Audit (`openMAX`)**

Quick follow-up to our update 3 days ago (`https://github.com/wolverin0/openmax`) with the exact side-by-side numbers several of you asked for, plus the standalone scripts so you can test on **Stock airOS 8 (without flashing!)** or **OpenWrt 24.10.4**:

### 1. The 3-Way Comparison: Stock `airOS 8` vs. Tuned `airOS 8` vs. `OpenWrt 24.10.4` Champion
We ran counterbalanced `A1 -> B1 -> A2 -> B2` Triple-Play tests (Bulk TCP + `8 Mbps` IPTV UDP `DSCP CS4` + `64 kbps` VoIP G.711 `DSCP EF` + `0.2s` ICMP probes in `20 MHz` VHT20) across `PowerBeam 5AC Gen2`, `LiteBeam 5AC Gen2`, `LiteAP 120`, and `NanoStation 5AC Loco`:

| Metric (`20 MHz` VHT20 Triple-Play Load) | 1. Stock `airOS 8` (Factory Default) | 2. Tuned `airOS 8` (`rc.poststart`, Zero Flash) | 3. `OpenWrt 24.10.4` + `openMAX` Champion |
| :--- | :---: | :---: | :---: |
| **Unloaded RF RTT (`p50`)** | `1.96 ms` (PtP) / `22.58 ms` (PtMP) | `1.63 ms` (PtP) / `~9.0 ms` (PtMP) | **`1.59 ms` (PtP) / `1.93 – 2.42 ms` (PtMP)** |
| **Loaded PtP RTT (`p50` / `p95`)** | `13.78 ms` / `25.00 – 34.32 ms` | **`7.95 ms` (`-42.3%`) / `15.76 – 17.05 ms` (`-50.3%`)** | **`1.59 – 6.33 ms` / `2.68 – 13.40 ms` (`-64.6%` to `-89%`)** |
| **Loaded PtMP Sector RTT (`p50` DL / UL)** | `42–65 ms` DL / `180–200 ms` UL | `14–19 ms` DL / `28–35 ms` UL | **`8.43–9.86 ms` DL (`-86.4%`) / `10.37–16.64 ms` UL (`-88.9%`)** |
| **VoIP (`G.711 DSCP EF`) Jitter / Loss** | `1.554 ms` / `0.0%` | **`0.714 ms` (`-54.1%` jitter)** / `0.0%` | **`0.420 – 0.710 ms`** / **`0.0%` loss** |
| **3-CPE Sector Goodput (`20 MHz`)** | `46.53 Mbps` | **`57.39 Mbps` (`+23.35%`)** | **`64.0 – 78.51 Mbps` peak TCP** |
| **Free RAM on 64 MB Radios (`MemAvailable`)** | `6.5 – 9.4 MB` | `8.0 – 11.0 MB` | **`10.6 – 22.4 MB` (`0` OOMs, `fq_memory_limit=4 MiB`)** |

*Full benchmark breakdown & stage receipts:* `docs/BENCHMARK_3WAY_AIROS_STOCK_VS_TUNED_VS_OPENWRT_CHAMPION.md`

### 2. Ready-to-Run PtP & PtMP Scripts (Now in the Repo)
We packaged both profiles as clean, dependency-free POSIX `sh` scripts with `--dry-run`, `--apply-ram` (safe RAM test), `--persist`, `--verify` (live read-back), and `--rollback`:
* **For Stock `airOS 8` (`firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh`):** No OpenWrt flash needed. Shrinks `eth0/ath0/br0` TX queues (`1000 -> 192`), raises MIPS NAPI budget (`300 -> 600`), bounds A-MPDU subframes (`32 -> 24`) to stop head-of-line blocking of VoIP/ICMP, tightens hardware WMM `AC_VI`/`AC_VO`, and unloads `ath_pktlog` / `vow_extstats` CPU overhead.
* **For `OpenWrt 24.10.4` (`firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh`):** Supports `--role ptp`, `--role ptmp-ap`, and `--role ptmp-cpe`. Warning: **never run stock OpenWrt Wi-Fi defaults on 64 MB airMAX AC radios** (`fq_memory_limit` defaults to `16 MiB` and `aql_threshold` to `24000`, which causes bufferbloat and OOMs). Our script caps `fq_memory_limit` at `4 MiB`, sets per-AC `AQL` (`VO 300/600`, `VI 1000/2000`, `BE 1500/3000`, `aql_threshold=5000`), tunes `eth0` BQL (`limit_max=8192` for PtP BDP / `42392` for CPE), and sets `CoTSQ tcp_limit_output_bytes=65536`.

### 3. What We Caught in Our 18-Radio Live Production Read-Back Audit
* Over the last 72 hours with all **18/18 radios** across 3 tower sectors + 1 PtP link running OpenWrt 24.10.4, we built an automated read-back auditor that verifies every kernel knob directly from `/sys`, `/proc`, and `debugfs` into SQLite.
* **Important Linux 6.6 `sysctl -w` gotcha we found and fixed:** If you pass multiple keys to a single `sysctl -w a=1 b=2 c=3` command on OpenWrt 24.10.4 and *one* key is absent on that kernel build (such as `net.core.netdev_budget_usecs` on `CONFIG_HZ=100` `ath79`), BusyBox `sysctl` aborts at that key and silently skips every key after it (which left `tcp_limit_output_bytes` at `1048576` instead of `65536`!). Switching to a per-key `for kv in ...; do sysctl -w "$kv"; done` loop brought all 4 nodes on our primary sector to **`100% MATCH` (`38/38` AP knobs and `25/25` CPE knobs with `0 differs`)** with zero link drops.
* We also cross-compiled our standalone `3.6 KB` static MIPS big-endian **`802.11v/ac Operating Mode Notification (OPMODE_NOTIF)`** frame injector (`fmx_omn`, `96/96` byte-exact verified under `qemu-mips-static -cpu 24Kc`) to help asymmetric/degraded CPEs dynamically negotiate NSS/channel-width changes without dropping association.

Repo & scripts: `https://github.com/wolverin0/openmax` (`firmware/public_field_kits/`)
```

---

## 2. Resumen para Reddit / Comunidad en Español

```markdown
**Actualización (3 días después) — Comparativa Triple (airOS 8 Stock vs. airOS 8 Tuneado vs. OpenWrt Champion), Scripts PtP/PtMP Listos para Usar y Auditoría en Vivo de 18 Radios (`openMAX`)**

Dejo actualización en `https://github.com/wolverin0/openmax` con la tabla comparativa de las 3 etapas que varios pidieron y los scripts listos para aplicar tanto en **airOS 8 original (sin flashear)** como en **OpenWrt 24.10.4**:

### 1. Comparativa de 3 Brazos: `airOS 8` Stock vs. `airOS 8` Tuneado vs. `OpenWrt 24.10.4` Champion
Medido en rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` bajo carga Triple-Play simultánea (Descarga TCP + IPTV UDP `8 Mbps DSCP CS4` + VoIP G.711 `DSCP EF` + ping cada `0.2s` en `20 MHz` VHT20):

| Métrica (`20 MHz` VHT20 bajo carga Triple-Play) | 1. `airOS 8` Stock (Fábrica) | 2. `airOS 8` Tuneado (`rc.poststart`, sin flashear) | 3. `OpenWrt 24.10.4` + `openMAX` Champion |
| :--- | :---: | :---: | :---: |
| **Ping en vacío (`p50`)** | `1.96 ms` (PtP) / `22.58 ms` (PtMP) | `1.63 ms` (PtP) / `~9.0 ms` (PtMP) | **`1.59 ms` (PtP) / `1.93 – 2.42 ms` (PtMP)** |
| **Ping PtP bajo saturación (`p50` / `p95`)** | `13.78 ms` / `25.00 – 34.32 ms` | **`7.95 ms` (`-42.3%`) / `15.76 – 17.05 ms` (`-50.3%`)** | **`1.59 – 6.33 ms` / `2.68 – 13.40 ms` (`-64.6%` a `-89%`)** |
| **Ping Sector PtMP bajo saturación (`p50` DL / UL)** | `42–65 ms` DL / `180–200 ms` UL | `14–19 ms` DL / `28–35 ms` UL | **`8.43–9.86 ms` DL (`-86.4%`) / `10.37–16.64 ms` UL (`-88.9%`)** |
| **Jitter / Pérdida en VoIP (`G.711 DSCP EF`)** | `1.554 ms` / `0.0%` | **`0.714 ms` (`-54.1%` jitter)** / `0.0%` | **`0.420 – 0.710 ms`** / **`0.0%` pérdida** |
| **Capacidad agregada sector 3 CPEs (`20 MHz`)** | `46.53 Mbps` | **`57.39 Mbps` (`+23.35%`)** | **`64.0 – 78.51 Mbps` pico TCP** |
| **RAM Disponible en equipos de 64 MB (`MemAvailable`)** | `6.5 – 9.4 MB` | `8.0 – 11.0 MB` | **`10.6 – 22.4 MB` (`0` reinicios por OOM)** |

### 2. Scripts Públicos PtP y PtMP Listos para Usar (`firmware/public_field_kits/`)
Subimos los dos scripts independientes en POSIX `sh` con modos `--dry-run`, `--apply-ram` (prueba segura en RAM), `--persist`, `--verify` y `--rollback`:
* **Para `airOS 8` Stock (`firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh`):** No requiere pasar a OpenWrt. Reduce `tx_queue_len` (`1000 -> 192`), sube el presupuesto NAPI (`300 -> 600`), limita subtareas A-MPDU (`32 -> 24`), prioriza colas WMM de Voz/Video y descarga `ath_pktlog` / `vow_extstats`.
* **Para `OpenWrt 24.10.4` (`firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh`):** Soporta `--role ptp`, `--role ptmp-ap` y `--role ptmp-cpe`. Ajusta `FQ-CoDel` (`4 MiB`), `AQL` por categoría (`VO/VI/BE/BK`, `threshold=5000`), `BQL` en `eth0` (`8192` para PtP / `42392` para CPE) y `CoTSQ tcp_limit_output_bytes=65536`.

### 3. Auditoría de Relectura en Vivo (`18/18` Nodos, `0 differs`) y Detalle Clave de `sysctl`
* Con los 18 equipos corriendo OpenWrt 24.10.4 en producción, nuestro colector SQLite auditó cada parámetro leído directamente del kernel.
* Descubrimos y corregimos un detalle importante en OpenWrt 24.10: al pasar múltiples claves a un solo `sysctl -w`, si una clave no existe en ese kernel (`net.core.netdev_budget_usecs`), `sysctl` aborta y deja sin aplicar todas las claves siguientes (como `tcp_limit_output_bytes=65536`). Al pasarlo a un bucle clave por clave, los 4 nodos del sector principal quedaron en **`100% MATCH` (`38/38` en el AP y `25/25` en cada CPE con `0 differs`)**.
```
