<!-- doc-head: Stage1064A offline reconciliation of the historical Stage697A hotplug and the current retired actuator -->
Historical source, saved deployment claims and new unexecuted syntax plans remain separate evidence.
<!-- /doc-head -->

# Stage1064A — PtP hotplug AQM reconciliation

This stage performs no SSH, radio access, firmware loading or device writes. It reads exact local files and extracts the historical `CHAMPION_V4_CONTENT` using Python AST literal evaluation, without importing the live deployment producer.

| Evidence | Finding | Meaning |
|---|---|---|
| Stage697A embedded historical hotplug | `echo 300 > "$PHY/aqm/fq_quantum"` | Invalid child path: native mac80211 `aqm` is a writable file |
| Stage1031A saved static binary dissection | `fq_limit %u`, `fq_memory_limit %u`, `fq_quantum %u` | Grammar evidence for writes to the `aqm` file |
| Stage697A AQL loop | Numeric AC indices `0..3` | Already uses the numeric grammar; no label-to-index repair is claimed |
| Historical write handling | `2>/dev/null || true` | Suppressed errors cannot establish application or successful readback |
| Current local `99-fmx-wa-universal-champion` | Retired actuator stub | Its bytes differ from the saved historical payload; it is not a freshly observed radio file |

The receipt compares the AST-extracted historical payload SHA-256 with the saved Stage697A producer hash. It binds both the historical producer and the current retirement stub. The historical `deployed_on_241_and_242` claim is retained as a saved claim, not re-executed or upgraded to current evidence.

Stage1061A generates the corrected plan `fq_quantum 300` directed to `/sys/kernel/debug/ieee80211/phy2/aqm`, preserving the historical example value and numeric AQL limits. This is a grammar demonstration, not a recommended new champion or a deployment. Native phy identity, bounded operating ranges, rollback and complete readbacks remain prerequisites.

Stage1063A can parse observed tx/rx bitrates, VHT-MCS, NSS, chain signals and retry counters from saved or future station dumps. A historical rate override string does not prove the actual selected rate or any throughput benefit. Per-interface and per-peer identity are required before comparing counters.

Generate the offline receipt:

```powershell
python tools/verify/build_stage1064a_ptp_hotplug_aqm_fix_validation.py
```

Output: `artifacts/autoresearch/stage1064a_ptp_hotplug_aqm_fix_validation.json`.

Attribution: external controller for plan construction; mac80211 for the debugfs grammar. No QCA firmware performance effect, RF improvement, UDP QoE, loaded A/A or holdout is established. Research pillars record saved evidence and unexecuted activities explicitly; this offline wave does not claim fresh literature, memory ingestion or live autoresearch execution.
