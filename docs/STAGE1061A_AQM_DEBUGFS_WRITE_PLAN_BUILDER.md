<!-- doc-head: Stage1061A offline mac80211 AQM and numeric AQL write plans with requested-field readback validation -->
Plans are never executed; syntax evidence is saved Stage1031A, not a new live test.
<!-- /doc-head -->

# Stage1061A: mac80211 debugfs write plans

`tools/qca988x/aqm_debugfs_write_plan_builder.py` builds JSON and shell text without contacting a device or executing a command. The owner is **mac80211**, not ath10k firmware.

| File | Admitted write payload |
|---|---|
| `/sys/kernel/debug/ieee80211/phyN/aqm` | `fq_limit UINT`, `fq_memory_limit UINT`, `fq_quantum UINT` |
| `/sys/kernel/debug/ieee80211/phyN/aql_txq_limit` | `AC_INDEX LOW HIGH`, with numeric index 0..3 |

The AC order is VO=0, VI=1, BE=2, BK=3. Labels such as `BE 1500 3000` are rejected. Native BC/MC is preserved by the readback parser but is not an admitted write target.

Syntax is tied to the saved Stage1031A ELF analysis: module SHA256 `19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416`, vermagic `6.6.110`, backports tag `6.12.52`. That binary alone does not establish an OpenWrt release version or compatibility with a different module.

Values are canonical ASCII unsigned decimal, limited to uint32. Plan policy additionally rejects zero AQM limits and requires positive ordered AQL limits. These checks are syntax/policy guards, **not evidence that every uint32 value is operationally safe**. Operational ranges require an explicitly qualified profile.

Public APIs:

```python
from tools.qca988x.aqm_debugfs_write_plan_builder import build_plan, validate_readback
plan = build_plan('phy2', {'fq_quantum': 3028}, {2: {'low': 1500, 'high': 3000}})
# validate_readback(plan, saved_aqm_text, saved_aql_text)
```

Readback validation reconstructs the plan to reject edited paths and compares only requested fields. AQM fields must be marked RW. It does not certify kernel identity, native PHY mapping, root qdisc parameters, unchanged unrelated fields, or rollback.

Before any later live execution, independently identify the active PHY, snapshot all state, qualify operational bounds, prove a restoration transaction, and acquire complete readback. This stage performs none of those live steps.

Receipt: `artifacts/autoresearch/stage1061a_aqm_debugfs_write_plan_builder.json`. Five-pillar source pointers are recorded with honest offline/not-executed status. No radio, SSH, flash, or research-network operation occurs.
