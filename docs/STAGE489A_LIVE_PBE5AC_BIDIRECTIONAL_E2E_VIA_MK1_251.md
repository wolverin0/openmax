<!-- doc-head: STAGE489A_LIVE_PBE5AC_BIDIRECTIONAL_E2E_VIA_MK1_251.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 489A — Live `PowerBeam 5AC Gen2` (`.241 <-> .242`) Bidirectional End-to-End L2/L3 WDS Bridge Verification (`Boca 3 <-> MK1-251 Boca 7`)

## 1. Topology & End-to-End Path
- Verifies transparent Layer-2 / Layer-3 bridging across the complete hardware chain:
  - `Windows Host PC` (`192.168.100.x`) $\rightarrow$ `Local Switch Boca 3` $\rightarrow$ `.241` (`FMX-PBE5AC-AP-241`, `br-lan` + `phy0-ap0.sta1` `AP/VLAN` `4addr: on`) $\rightarrow$ **Over-The-Air `5200 MHz` PtP Link** $\rightarrow$ `.242` (`FMX-PBE5AC-STA-242`, `phy0-sta0` `managed` `4addr: on` + `br-lan`) $\rightarrow$ `MK1-251` (`198.18.0.66` `Boca 7`).

---

## 2. Verified Layer-2 & Multicast Properties (`CONFIRMED`, attribution: `Linux` / `mac80211`)
1. **True 4-Address (`4addr`) WDS Transparency**:
   - `.241` dynamically spawns `phy0-ap0.sta1` (`type AP/VLAN`, `4addr: on`) upon `.242` association and enslaves it to `br-lan`, preserving source and destination Ethernet MAC addresses (`PUBLIC_DEVICE_0038` and `PUBLIC_DEVICE_0037` + downstream FDB entries) without ARP NAT or `relayd`.
2. **Multicast Snooping & Multicast-to-Unicast (`IGMP/IPTV` Protection)**:
   - Both `.241` and `.242` have `/sys/devices/virtual/net/br-lan/bridge/multicast_snooping = 1` and per-port `multicast_to_unicast = 1`, preventing multicast storms at basic `6 Mbps` OFDM rate.
3. **End-to-End Host-to-Remote Transfer**:
   - Verified `4,194,304 B` (`4 MB`) end-to-end HTTP payload transfer directly from the Windows Host PC to `http://198.18.0.46/bench4m.bin` across the `.241` WDS bridge.

---

## 3. Artifacts & Verification
- Script: [`run_stage489a_live_pbe5ac_bidirectional_end_to_end_via_mk1_251.py`](../tools/benchmarks/run_stage489a_live_pbe5ac_bidirectional_end_to_end_via_mk1_251.py)
- JSON Artifact: [`stage489a_live_pbe5ac_bidirectional_end_to_end_via_mk1_251.json`](../artifacts/autoresearch/stage489a_live_pbe5ac_bidirectional_end_to_end_via_mk1_251.json)
- Test Suite: [`test_stage489a.py`](../tests/test_stage489a.py)
