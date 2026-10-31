<!-- doc-head: Stage 1106A - which files really set the bridge multicast sysfs knobs, which spelling each write uses, and whether the brief's 1316B IPTV figure is attributable; static only -->
# Stage 1106A - bridge multicast sysfs paths

Auditor: `tools/re/audit_stage1106a_bridge_multicast_sysfs_paths.py`
Receipt: `artifacts/autoresearch/stage1106a_bridge_multicast_sysfs_paths.json`
Provenance class: `CONFIRMED_STATIC_BINARY` (files read as bytes and text only).

## 1. Why a path needs auditing at all

`multicast_snooping` is a bridge option and `multicast_to_unicast` is a bridge-port option. They live
on different objects, so a path that names one under the other resolves to nothing, and because these
writes are wrapped in `2>/dev/null || true` or guarded by `[ -f ]`, a wrong path looks exactly like a
successful one. The brief also states a "1316B IPTV protection" figure, which is the sort of number a
document inherits without anyone re-checking it.

## 2. Corpus as measured

| quantity | value |
| :--- | ---: |
| files examined (byte scan) | 9,858 |
| files carrying either token | 110 |
| of those, binaries | 17 |
| of those, text | 93 |
| text files that write a knob | 45 |
| text files that only read a knob | 1 |
| text files that only mention a knob | 47 |
| `multicast_to_unicast` occurrences | 1,155 |
| `multicast_snooping` occurrences | 646 |
| write statements | 927 |
| distinct write statements | 8 |
| read statements | 12 |
| files with a setting form, `firmware/` | 1 |
| files with a setting form, `artifacts/autoresearch/` | 44 |
| of those 45, source scripts | 1 |
| of those 45, receipts embedding a script | 44 |

The brief says 90 files. Measured: 110, and the difference matters. The 17 binaries are mac80211
`.ko` artefacts and one `ubntbox`; they carry the token as compiled string-table text and cannot write
sysfs. Of the 93 text files, one is a source script that generates the writes and 44 are receipts
holding a copy of that same rendered script, so a file count over the token is not a count of setters.

## 3. The spellings that are actually used

| normalised path | knob | form | verdict |
| :--- | :--- | :--- | :--- |
| `/sys/class/net/<bridge>/bridge/multicast_snooping` | snooping | bridge, class spelling | INFERRED valid |
| `/sys/devices/virtual/net/<bridge>/bridge/multicast_snooping` | snooping | bridge, devpath spelling | CONFIRMED valid |
| `/sys/class/net/<bridge>/brif/<port>/multicast_to_unicast` | m2u | port via brif | CONFIRMED valid |
| `/sys/devices/virtual/net/<bridge>/brif/<port>/multicast_to_unicast` | m2u | port via brif | CONFIRMED valid |
| `/sys/class/net/<port>/brport/multicast_to_unicast` | m2u | port via brport | INFERRED valid |
| `uci:wireless.@wifi-iface[*].multicast_to_unicast` | m2u | UCI option | UNKNOWN |

`path_form_valid = 5`, `path_form_invalid = 0`, `path_form_unknown = 1`.

Values written: `multicast_snooping` is only ever `1` (258 statements). `multicast_to_unicast` is `1`
in 667 statements and `0` in 2 (both rollback lines). Interface names reached: `br-lan` (704),
`phy0-ap0*` (338), `wlan0` (112).

## 4. The expected defect is absent, and the unexpected spelling is confirmed

The plausible first conclusion is that `brif` is a `brctl show` column pasted into a path and cannot
work. The corpus refutes that:

`artifacts/autoresearch/stage35a_openwisp_portal_and_m15_5ghz_bench_20261025.json` holds a getter dump
over `/sys/devices/virtual/net/br-lan/brif/phy0-ap0*/multicast_to_unicast` for four counterbalanced
phases:

```
A1: sta1 0, sta2 0, phy0-ap0 1
B1: sta1 1, sta2 1, phy0-ap0 1
A2: sta1 0, sta2 0, phy0-ap0 1
B2: sta1 1, sta2 1, phy0-ap0 1
```

A path that does not exist cannot answer with a number, and cannot move `0 -> 1 -> 0 -> 1` in step
with the arm. So the `brif` spelling resolves on this target (OpenWrt 24.10.4, kernel 6.6.110), and
the dynamic per-station ports spawn at `0` exactly as the packager's docstring claims. CONFIRMED, from
a receipt already in the corpus; not re-measured here.

`multicast_snooping` is separately confirmed by `stage696a_...json`, whose bench reads
`AP_MCAST_SNOOP` and `STA_MCAST_SNOOP` through `/sys/devices/virtual/net/br-lan/bridge/multicast_snooping`
and records `multicast_snooping_active: true`.

## 5. What remains unknown

- `/sys/class/net/<if>/...` is INFERRED: it is the canonical view of the same object proven through
  the `devices/virtual` spelling, but no readback in the corpus exercises the class spelling of
  `multicast_snooping` directly.
- `/sys/class/net/<port>/brport/multicast_to_unicast` is INFERRED: it is the documented per-port
  container, and it appears in this corpus only four times, never with a readback.
- `uci set wireless.@wifi-iface[0].multicast_to_unicast='1'` is UNKNOWN. Whether the OpenWrt wireless
  layer maps that option onto the port attribute cannot be decided without the netifd/mac80211 scripts,
  which are not in this corpus. It accounts for 219 of the 927 write statements.

## 6. The 1316B IPTV figure

The figure is attributable, and it is not a protection mechanism. The corpus states

```
| UDP IPTV | 1316 B (7 x 188 TS), constant 2 Mbps |
```

i.e. seven 188-byte MPEG-TS packets, and receipts carry `iptv_payload_bytes: 1316`
(`stage599a_pbe5ac_lbe5ac_triple_play_vht40_field_certification.json` and its builder). Searching the
five scopes gives 1,367 occurrences of `1316`, of which 123 are bounded as a standalone number, 12 are
followed by a byte unit and 63 have IPTV or multicast language within 60 characters. The rest are
substrings of sha256 digests, ELF section offsets and floating-point noise. This stage's own tool,
receipts and docs are excluded from that search, because a document quoting a figure is not evidence
for it.

`iptv_1316b_attributable = 1`. What does not exist is any artefact named "1316B protection": the
protective work described around that flow is AC_VI pacing and AQL limits. The first pass of this
search called the figure unattributable and was wrong; the correction is recorded in the receipt's
premise corrections.

## 7. Behavioural findings

1. `multicast_snooping` is only ever written as `1` in this corpus, never `0`. The corpus's own
   `S39A-R1` note records that enabling snooping on CPE bridges cost goodput, so a blanket
   `snooping=1` with no role distinction is the risky shape, and no write in scope carries a role.
2. Interface coverage is narrower than the write set implies: every write names `br-lan`,
   `phy0-ap0*` or `wlan0`, and no `phy0-sta0` or `phy2-sta0` port appears. On a STA-role radio whose
   bridge port is the STA VAP, the port-attribute glob matches nothing and the write does nothing.
3. Failures are invisible: the writes are followed by `2>/dev/null || true` or guarded by `[ -f ]`, so
   the corpus cannot distinguish a successful write from a silent no-op by exit status.

## 8. Claims

| id | label | claim |
| :--- | :--- | :--- |
| C1 | CONFIRMED | 110 files carry either token, not 90, and 17 of them are binaries |
| C2 | CONFIRMED | only one text file under `firmware/` writes either knob; 44 receipts repeat a copy |
| C3 | CONFIRMED | the `brif` spelling resolves on this target, proven by a live 0/1 readback that tracks the arm |
| C4 | CONFIRMED | the bridge spelling of `multicast_snooping` resolves, proven by a live readback |
| C5 | REFUTED | no write names a knob under the wrong object; `invalid_paths` is empty |
| C6 | INFERRED | the `class` spelling resolves because it is the same object as the proven `devices/virtual` one |
| C7 | UNKNOWN | the `uci` wireless option may or may not reach the port attribute |
| C8 | CONFIRMED | the 1316 B figure is the IPTV payload size, and is attributable |
| C9 | CONFIRMED | no write reaches a STA-role port name |
| C10 | CONFIRMED | write failures are suppressed, so success cannot be inferred from exit status |
| C11 | UNKNOWN | no artefact is named "1316B IPTV protection" |

## 9. Gaps

- The live readbacks are pre-existing receipts and were not re-measured; this stage never contacted
  the target.
- No readback exercises the `class` spelling of `multicast_snooping` or the `brport` container, so both
  stay INFERRED.
- Whether a given write ran, and on which device, depends on the script that carried it; nothing was
  executed.
- Glob-versus-literal behaviour is read from the text; an unmatched glob is passed unexpanded and the
  failure is invisible, so on-target coverage is unknown.
- Whether the named interface exists when the write runs is not measurable offline; dynamic WDS ports
  appear and disappear with association events.
- The 1316 search covers `firmware/`, `artifacts/autoresearch/`, `docs/`, `controller/` and `tools/`; a
  figure introduced outside those scopes is not ruled out.
- The tree is live: other stages write receipts into `artifacts/autoresearch/` while this runs, so the
  examined set is pinned by `corpus_manifest_sha256` rather than assumed stable.

## 10. Reproduction

```
python tools/re/audit_stage1106a_bridge_multicast_sysfs_paths.py --print-summary
STAGE1106A files_scanned=9858 token_files=110 (binary=17 text=93) files_setting_knobs=45 m2u_refs=1155 snoop_refs=646 unique_paths=6 valid=5 invalid=0 unknown=1 iptv_1316b_attributable=1
```

Two consecutive runs produced a byte-identical receipt at generation
(`8eba80ddfb008e2ccfa5041b4c76c164992bffa1f3c5c2e80f07339437894069`). The examined corpus is pinned by
`corpus_manifest_sha256 = 302af2ec1e3146afeefe1a7f7d3f1b1a5ceba8f32749c58ef61fdc61aca5b933` and by a
wave cutoff at stage 1103: receipts from this concurrent wave are excluded, 30 files at generation, so
a later run cannot drift because a sibling stage committed a receipt while this one ran.
