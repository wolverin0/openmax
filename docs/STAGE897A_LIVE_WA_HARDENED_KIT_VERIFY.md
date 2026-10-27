<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage897A — Native WA kit verification

2026-10-27. Status **BLOCKED**, physical acceptance **NOT_ACCEPTED**.
Owner: external controller for acquisition; Linux/ath10k native getters for observations.

## Fresh physical observations

| Address | Native observation | Claim |
| --- | --- | --- |
| .20 | OpenWrt24.10.4, LAP120 AR9342rev2; `phy0-ap0`, AP VLAN; no `ath0` or `tc` | CONFIRMED |
| .195 | TCP22 timeout | UNKNOWN identity and association |
| .250 | SSH banner ROSSSH; operator identifies MikroTik behind STA | CONFIRMED banner; excluded from WA writes |
| .251 | Successful ubnt native read: Rocket2AC Prism, board0xe2f2, airOS2XC8.7.11, 2422MHz | CONFIRMED; OpenWrt STA claim REFUTED for this read |

The .20 hostname is Panel1-Guarida, but native boot/hardware identity differs
from the separately recorded .84 production unit. Hostname alone is insufficient.
Documented project access succeeded on .20. Explicit operator-supplied root
credential attempts failed on .20/.251; secrets are absent from receipts.
No alternative subnet, tower, switch or MikroTik configuration was changed.

## Actual unchanged kit execution

Source: `firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh`.
SHA256 `df1501405609c5c1a6d89c6ee6a2b185519db40dcc512f0bb51f116aaaf3d485`.
Exact bytes streamed through SSH stdin to .20:

| Invocation | Native result | Interpretation |
| --- | --- | --- |
| `sh -s -- --dry-run` | exit0, PLANNED, runtime UNKNOWN | CONFIRMED planning only |
| `sh -s -- --verify` | exit64, unsupported mode | CONFIRMED no verify implementation |
| `--apply` | NOT_EXECUTED | No approved native transaction |

The initial long inline transport failed with EOF; its failure is retained.
Switching transport to stdin did not alter kit bytes or convert planning to apply.

## Preconditions preventing apply

| Contract | Requested | Canonical kit / native state |
| --- | --- | --- |
| fq_codel quantum | 1514 | 3028 |
| target / interval | 5ms / 100ms | 2.5ms / 50ms |
| flows / ECN | 1024 / enabled | 1024 / inherited ECN |
| board revision | Native identity field | Absent from ubus result |
| AQL getter | Native verifiable values | VO/VI/BE/BK labels rejected by numeric-only parser |
| qdisc snapshot | Restorable root fq_codel | `tc` unavailable |

No forged revision, parser shim, installed package or identity guard bypass was used.
The canonical kit has synchronous rollback; no independent45s recovery was proved.
Missing association/access prevents WA A/A and disjoint holdout acquisition.

## Evidence and continuation

[Receipt](../artifacts/autoresearch/stage897a_live_wa_hardened_kit_verify.json)
binds native captures, actual dry-run/unsupported verify output and independent review.
[Producer](../tools/autoresearch/run_stage897a_live_wa_hardened_kit_verify.py)
performs no apply. Independent review separates pure shell stubs from hardware proof.
Next: establish the actual OpenWrt STA and a compatible native identity/getter/qdisc
transaction implementing the requested profile before any application or WA campaign.
