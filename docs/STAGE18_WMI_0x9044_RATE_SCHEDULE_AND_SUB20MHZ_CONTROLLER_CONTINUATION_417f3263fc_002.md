<!-- doc-head: STAGE18_WMI_0x9044_RATE_SCHEDULE_AND_SUB20MHZ_CONTROLLER.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE18_WMI_0x9044_RATE_SCHEDULE_AND_SUB20MHZ_CONTROLLER.md) | Part 2/2
<a id="stage18b-wmi-retry-schedules-and-sub20mhz-planning"></a> [Stage18B: WMI retry schedules and sub20MHz planning](STAGE18_WMI_0x9044_RATE_SCHEDULE_AND_SUB20MHZ_CONTROLLER_CONTINUATION_417f3263fc_001.md#stage18b-wmi-retry-schedules-and-sub20mhz-planning) | <a id="prespecified-parent-question-and-acceptance"></a> [Prespecified parent, question and acceptance](STAGE18_WMI_0x9044_RATE_SCHEDULE_AND_SUB20MHZ_CONTROLLER_CONTINUATION_417f3263fc_001.md#prespecified-parent-question-and-acceptance) | <a id="wmi-command-and-descriptor-contracts"></a> [WMI command and descriptor contracts](STAGE18_WMI_0x9044_RATE_SCHEDULE_AND_SUB20MHZ_CONTROLLER_CONTINUATION_417f3263fc_001.md#wmi-command-and-descriptor-contracts) | <a id="pb030-and-pb040"></a> [PB030 and PB040](STAGE18_WMI_0x9044_RATE_SCHEDULE_AND_SUB20MHZ_CONTROLLER_CONTINUATION_417f3263fc_001.md#pb030-and-pb040)

<!-- stage822a-payload-begin -->
| Verified object | Value |
| --- | --- |
| Module SHA256 | `46525dc6f8b789bf820f0713841a2a9ecdcba833300ddb1ab1ef06fc4ab6a9c5` |
| AP container SHA256 | `55e9c94a2f0b466ff50ced26f589c755b955e751861b466bb71be9f87de261ee` |
| Original8500B segment SHA256 | `4352471afde9d65477ebf3af97cdfffb48080895a43b3e71745c08389c589483` |
| PB040 table | `0x0040bb40`, segment offset `0xb40`, bytes `060c121824303600` |
| Companion table | `0x0040b688`, offset `0x688`, bytes `0c1218243048606c` |

CONFIRMED: these bytes and address/offset arithmetic match the retained PB040 spec.
Interpreted as half-Mbps rate-like values they are `[3,6,9,12,18,24,27,0]` and
`[6,9,12,18,24,36,48,54]`. The first is not even a complete standard HALF-rate list
(4.5Mbps is absent). The spec's proposed `0x36→0x48` byte change is not a proved PLL
divider. Actual baseband clock control and effective5/10MHz operation remain UNKNOWN.

## Verification and evidence limits

The generated JSON contains12 explicitly synthetic schedules: four families ×
balanced/asymmetric/reversed-asymmetric inputs; three blocked bandwidth plans;
one synthetic timer arithmetic example; exact source/header/module bindings; and
zero measured hardware results. All execution/physical claims remain false or null.
The JSON validator reuses the typed plan, reconstructs timer arithmetic and rejects
contradictory nested claims of patching, transmission, clock verification or hardware
acceptance.

Input and output paths are checked before file metadata probes. UNC, mixed-separator
UNC, device/URI paths and mapped network drives are rejected. Local symlink/reparse
ancestors are rejected before accessing children through them. The CLI retains raw
path text until this guard runs. Ordinary pinned local files are then read and hashed.
No access to a real remote path is needed by the regression tests.

Development failures and repairs are preserved:

- Initial independent review reproduced remote-path probing with mocks, unsafe
  nested report assertions and HT use of the VHT-only LDPC auxiliary bit.
- First pytest process exited1 after45 passes and an INTERNALERROR. A `file://` URI
  normalized before the guard exposed the lexical check gap. The fixture's global
  `Path.stat` mock also interfered with pytest's failure reporting. Raw-text checking
  and scoped mock restoration fixed both; no real network/device probe occurred.
- Second run:68PASS, exit0, before the final CLI raw-path change. A later run also
  had68PASS with the generated JSON present. Independent review then found that
  exported-plan/JSON identity and budget checks could bypass builder restrictions,
  plus unguarded timing/table assertions. These passes did not close those findings.
- Repaired revision: **77PASS,0FAIL,0ERROR,0SKIP, exit0**,0.45s, on this single test
  file with `WEZBRIDGE_OPERATOR_ALLOW_HEAVY=1`. XML receipt:
  `C:/_tmp/systemp/s18b_pytest_repaired_20261025.xml`, SHA256
  `d6ee8b19f71eb837a9cacbec4dfc69c409a46d393a20c299849249cf8f924ca8`.

Coverage includes exact masks/golden/endian roundtrips, all four family/opcodes,
reserved and illegal combinations, capability gates, EVM/RSSI adaptation, TxBF/TPC,
identity and budget invariants, NoProbe paths, PB040 tamper rejection, clock/coverage
arithmetic, saturation, nested opposite claims and an offline build with all socket,
subprocess and file-writing calls denied. The emitted JSON is compared to a fresh
deterministic report; source/input/implementation hashes are checked. No other
pytest file, WSL, radio, shared service or bench recipe is executed.

Implementation bindings: controller
`42821a83cc35f9c6578f241a56aefd8d873435a4504278d12f2b77dec3c805ff`, tests
`957ae4c1705aec7f221990c5b5d778f4693d4d9484c08301a259ab4a9cab50ad`.
JSON SHA256: `1a36901575be2d284a00d532295ede76d08b5dd5ec3070410eb89f2ece48ea4d`.
Independent WMI review: **PASS_WITH_LIMITS**, zero material blockers,52 fresh
pure checks including all19 header masks, byte goldens/endian, malformed identity,
retry/TPC/BW invariants, nested ABI claims and NoProbe paths. The reviewer checked
the current JSON/source bindings and reused the root77PASS XML without running
another pytest file. Receipt:
`C:/_tmp/systemp/fmx_s18b_wmi_accepted_xtwhliqt/independent_wmi_review.json`, SHA256
`ba9ad8aa82a8835abddb63f0f08b560f8afbcc42d8eb34672d5e18c2e37b95a1`.
Independent PB040/timing review: **PASS_WITH_LIMITS**, zero material blockers,
42 fresh probes covering nested opposite claims, timing reconstruction, exact12/3
coverage, NoRead paths, all bandwidth models, saturation and cross-width refusal.
The reviewer verified the current source/JSON/XML pins and reused its separately
authenticated held-byte audit without exporting or re-extracting proprietary payloads.
Receipt: `C:/_tmp/systemp/fmx_s18b_review_final_81e6234435fa42988e40b0a7950b1198/code_review.json`,
SHA256 `7021fd8646a9caca87c684b3e4325e4aaee82185e457b69371cf1bb649672c2c`.
Both reviews cover code/tests/JSON; this coordinator documentation receipt was
added afterward. Software/planner acceptance does not accept a physical experiment.

## Reproduction and concrete remaining evidence

```powershell
$env:WEZBRIDGE_OPERATOR_ALLOW_HEAVY='1'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m controller.stage18_wmi_rate_schedule_and_sub20mhz_controller
python -m pytest -q tests/test_stage18_wmi_rate_schedule_and_sub20mhz_controller.py -p no:cacheprovider
```

The pinned retained `series_bw.h` is outside Git at
`C:/_tmp/systemp/fmx_pb_starlink_1d585ee/dl/include/AR9888/v2/hw/mac_descriptors/series_bw.h`,
SHA256 `49f8859e56320a902f9d5ae1e56a8fc16281659e1fedb8dc59a3883f354ff51b`.
If relocated, `--series-header` accepts an identical local file; missing or changed
bytes fail closed without fetching anything. The primary header is not copied into
the repository. No dependency installation or provider configuration was performed.

Missing physical evidence remains specific: authenticated installed-build peer
capabilities, vendor188-byte ABI/descriptor binding, packet-dependent field completion,
effective per-retry telemetry, actual chanbw/PLL/PHYCLK control at both ends, legal
RF occupancy/EIRP/DFS characterization and original recovery/operator gates. These
dependencies block execution, not this offline planner. No physical gain, usable
clock divider, working native message or Stage4/Stage5 acceptance is claimed.
<!-- stage822a-payload-end -->
