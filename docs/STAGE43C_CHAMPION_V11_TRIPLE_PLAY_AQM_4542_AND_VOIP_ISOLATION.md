<!-- doc-head: STAGE43C_CHAMPION_V11_TRIPLE_PLAY_AQM_4542_AND_VOIP_ISOLATION.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 43C: Champion v11 3-Tier Triple-Play (`fq_quantum=4542` 3×MTU + `fq_limit=2048/1024` + `AC_VO=300/600 us`) & OpenWISP NetJSON Integration

## 1. Executive Summary (`CONFIRMED`)

- **Task ID**: `T-S43C-GEM2-CHAMPION-V11-TRIPLE-PLAY-AQM-4542-AND-VOIP-AQL-INTEGRATION`
- **Modules Updated**:
  - [`controller/wisp_iptv_ptmp_sector_optimizer.py`](<repo>/controller/wisp_iptv_ptmp_sector_optimizer.py) (`load_empirical_stage37a_champion_v11_evidence`, `render_openwrt_triple_play_champion_v11_script`, `export_openwisp_triple_play_champion_v11_netjson_template`)
  - [`tools/serve_openwisp_dual_nms_live.py`](<repo>/tools/serve_openwisp_dual_nms_live.py) (`/api/v1/iptv/capacity/`, `/api/v1/controller/template/triple-play-v11/`, and Section 5 `a2)` inside [`artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`](<repo>/artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html))
- **Authoritative Physical Benchmark Receipt**: [`artifacts/autoresearch/stage37a_triple_play_aqm_fq_limit_bench_20261025.json`](<repo>/artifacts/autoresearch/stage37a_triple_play_aqm_fq_limit_bench_20261025.json) (`docs/STAGE37A_TRIPLE_PLAY_IPTV_VOIP_AND_MAC80211_FQ_LIMIT_BENCHMARK.md`)

## 2. Physical Discovery in Stage 37A: Why `S37A-R1` (`fq_quantum=3028`, `AC_VO=600/1200`) Lost `-3.628%` Goodput and Why `S37A-R2` (`Champion v11`) Won

Under simultaneous **3-Tier WISP Triple-Play load** across `LAP-120` AP (`198.18.0.43`) and 3 CPEs (`Loco 5AC` `.250`, `Rocket Prism 5AC Gen2` `.198`, `LiteBeam M5` `.251`):
1. **Tier 1 — VoIP (`WMM AC_VO`, `DSCP EF` / `0xb8` $\rightarrow$ `tid6_ac0`)**: `100 pps` (`128 Kbps`, `160`-byte G.711/Opus datagrams on UDP `5203`).
2. **Tier 2 — Dual `1080p60` IPTV (`WMM AC_VI`, `DSCP CS4` / `0x80` $\rightarrow$ `tid4_ac1`)**: `470 pps` (`5.0 Mbps`, `1,316`-byte `7 × 188B` MPEG-TS datagrams on UDP `5202`).
3. **Tier 3 — 3-CPE Bulk TCP (`WMM AC_BE`, `TOS 0x00` $\rightarrow$ `tid0_ac2`)**: Bidirectional multi-stream TCP saturation (`iperf3 --bidir -P 2`).

| Round | Configuration | Goodput $\Delta$ | `p95` RTT $\Delta$ | `p50` RTT $\Delta$ | Dual IPTV (`tid4_ac1`) Loss | VoIP (`tid6_ac0`) Loss | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S37A-R1`** (`M17`) | AP `fq_quantum=3028` (`2×MTU`), `fq_limit=2048/1024`, `AC_VO=600/1200 us` | `-3.628%` (`51.650 -> 49.776 Mbps`) | `-3.028%` | `+5.482%` | `2.314%` | `0.00%` | **`REFUTED`** (`AC_VO` `100 pps` + `AC_VI` `470 pps` preempt `2-MTU` TCP DRR turns) |
| **`S37A-R2`** (`M17b` **Champion v11**) | AP **`fq_quantum=4542` (`3×MTU`)** / CPE `1514`, **`fq_limit=2048/1024`**, `fq_memory_limit=4194304`, **`AC_VO=300/600 us`**, `AC_VI=1200/2400 us`, `AC_BE=1500/3000 us` | **`+2.648%`** (`49.657 -> 50.972 Mbps`) | **`-3.778%`** (`110.720 -> 106.537 ms`) | **`-22.452%`** (`53.638 -> 41.595 ms`) | **`0 / 5,684` (`0.00%`)** | **`0 / 1,198` (`0.00%`)** | **`CONFIRMED` (`PROMOTE_NEW_CHAMPION`)** |

### Causal Mechanism (`CONFIRMED`)
- Because `WMM AC_VO` (`CWmin=3, CWmax=7, AIFSN=2`) wins internal EDCA contention `100` times per second and `WMM AC_VI` (`CWmin=7, CWmax=15, AIFSN=2`) wins contention `470` times per second, `tid0_ac2` (`AC_BE`) is preempted every `~1.75 ms`.
- With `fq_quantum=3028` (`2×MTU`), each `tid0_ac2` DRR round released only `2` TCP segments before yielding, shortening `AC_BE` A-MPDUs (`-3.628%` goodput).
- Increasing AP `fq_quantum` to **`4542` (`3×MTU`)** while tightening `AC_VO` AQL from `600/1200 us` to **`300/600 us`** (`echo '0 300 600' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit`) and bounding `fq_limit` to **`2048` (AP) / `1024` (CPE)** restores 3-segment `AC_BE` A-MPDU density (`+2.648%` goodput) while cutting `p50` RTT by `-22.452%`, `p95` RTT by `-3.778%`, and delivering `0.00%` packet loss across both Dual `1080p60` IPTV (`0/5,684`) and VoIP (`0/1,198`).
