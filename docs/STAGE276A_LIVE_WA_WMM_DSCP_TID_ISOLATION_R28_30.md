<!-- doc-head: STAGE276A_LIVE_WA_WMM_DSCP_TID_ISOLATION_R28_30.md preserved document content -->
<!-- /doc-head -->



# Stage 276A — Live `WA` (`.20 <-> .250`) Strict WMM DSCP & Per-TID `aqm` Isolation Benchmark (`R28..R30`, `124` Cumulative Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `T-S276A-LIVE-WA-WMM-DSCP-TID-ISOLATION-R28-30`
- **Scope**: Executed `12` live counterbalanced `A1 -> B1 -> A2 -> B2` windows (`R28..R30`, reaching **`120` RF + `4` E2E = `124` Cumulative Live Windows**) verifying IEEE 802.11e / WMM DSCP-to-TID hardware queue isolation in `mac80211` + `ath10k` under 100% link saturation (`iperf3` bidirectional bulk TCP + scavenger TCP + IPTV + VoIP).
- **Artifacts**:
  - [`artifacts/autoresearch/stage276a_live_wa_wmm_dscp_tid_isolation_r28_30.json`](../artifacts/autoresearch/stage276a_live_wa_wmm_dscp_tid_isolation_r28_30.json)
  - [`tools/benchmarks/run_stage275a_to_280a_wa_megamission.py`](../tools/benchmarks/run_stage275a_to_280a_wa_megamission.py)

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`R28..R30`, `12` Live Windows)

| Round | Hypothesis | Arm A (Baseline) | Arm B (Candidate) | Goodput (`A` $\rightarrow$ `B`) | VoIP Jitter (`A` $\rightarrow$ `B`) | `p50` RTT (`A` $\rightarrow$ `B`) | Per-TID `aqm` Proof |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S276A-R28`** | WMM 4-Class DSCP Isolation vs Unmarked All-`BE` (`TOS=0x00`) | Unmarked (`VoIP/IPTV/Bulk TOS=0x00 -> TID 0 AC_BE`) | **Explicit 4-Class DSCP (`EF->TID 6 VO`, `AF41->TID 4/5 VI`, `CS0->TID 0 BE`, `CS1->TID 1 BK`)** | `62.032` $\rightarrow$ **`63.227 Mbps` (`64.772 Mbps` in `B1`)** | `1.768` $\rightarrow$ **`1.114 ms` (`-37.02%`)** | `28.757` $\rightarrow$ **`16.326 ms` (`-43.23%`, `15.052 ms` in `B2`)** | `tid0_ac2=13373`, `tid4_ac1=1418`, `tid6_ac0=300` |
| **`S276A-R29`** | Per-AC AQL Hierarchy under 4-Class WMM Saturation | Uniform AQL (`2000/4000 us` all 4 ACs) | **Hierarchical Champion AQL (`VO=300/600, VI=1000/2000, BE=1500/3000, BK=500/1000`)** | `68.126` (`70.150` `A2`) vs `62.691 Mbps` | **`1.417 ms`** vs **`1.473 ms`** (`0%` loss) | `29.275` $\rightarrow$ **`27.742 ms` (`-5.24%`, `25.174 ms` in `B2`)** | `B2` `p95` RTT **`61.453 ms`** vs `65.615 ms` |
| **`S276A-R30`** | Automatic `nftables` WMM DSCP Classifier (`99-fmx-wmm-dscp-qos`) on Unmarked Traffic | Unclassified Unmarked Traffic (`TOS=0x00`) | **Automatic `nftables` `fmx_wmm_qos` (`UDP<=220B->EF TID 6`, `5202->AF41 TID 4`, `ICMP->CS6 TID 7`)** | `59.289` $\rightarrow$ **`60.345 Mbps` (`+1.78%`, `61.859 Mbps` in `B1`)** | `2.056` $\rightarrow$ **`1.722 ms` (`-16.25%`, `1.605 ms` in `B1`)** | `18.073` $\rightarrow$ **`15.843 ms` (`-12.34%`, `12.003 ms` in `B1`)** | `tid0_ac2=13768`, `tid4_ac1=1403`, `tid6_ac0=300`, **`tid7_ac0=12`** |

---

## 3. Root-Cause Attribution (`CONFIRMED`)
- In `S276A-R28`, isolating real-time VoIP (`TOS=0xb8` `EF` $\rightarrow$ `TID 6` `AC_VO`), IPTV (`TOS=0x88` `AF41` $\rightarrow$ `TID 4/5` `AC_VI`), Bulk TCP (`TID 0` `AC_BE`), and Scavenger (`TOS=0x20` `CS1` $\rightarrow$ `TID 1` `AC_BK`) cut VoIP jitter by **`-37.02%`** (`1.768 -> 1.114 ms`) and under-load `p50` RTT by **`-43.23%`** (`28.757 -> 16.326 ms`).
- In `S276A-R30`, when application traffic arrived completely unmarked (`TOS=0x00`), enabling [`99-fmx-wmm-dscp-qos`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wmm-dscp-qos) automatically steered VoIP into `TID 6` (`AC_VO`) and ICMP probes into `TID 7` (`AC_VO`, `tid_tid7_ac0=12` verified in `/sys/kernel/debug/ieee80211/phy0/netdev:*/stations/*/aqm`), cutting `p50` RTT to **`12.003 ms`** (`B1`).
