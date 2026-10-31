<!-- doc-head: Stage 858A - eab_driver.ko is absent from a 154-module LTU tree so five prior receipts describe a binary this corpus cannot reproduce, while the telemetry surface that does exist is three distinct channels with ioctl and copy_to_user on ame_dev, generic netlink on ame_core and seventeen debugfs references on cds_mac_mod and zero nl80211 anywhere -->
<!-- /doc-head -->
# Stage 858A — LTU ioctl and netlink telemetry

- **Receipt**: [`artifacts/autoresearch/stage858a_ltu_eab_driver_netlink_and_ioctl_telemetry_re.json`](../artifacts/autoresearch/stage858a_ltu_eab_driver_netlink_and_ioctl_telemetry_re.json)
- **Tool**: [`tools/re/dissect_stage858a_ltu_eab_driver_netlink_and_ioctl_telemetry_re.py`](../tools/re/dissect_stage858a_ltu_eab_driver_netlink_and_ioctl_telemetry_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing transmitted.

## 0. The named binary is not in the corpus

The LTU module tree holds **154** modules. `eab_driver.ko` is not one of them.

**`REFUTED`**: `eab_driver_present = 0`, `eab_driver_files = 0`.

Every `eab` match under `artifacts/` is a **receipt or a document**, never a binary:

```
stage154a_ltu_ame_eab_full_re.json
stage323a_ltu_eab_driver_dma_ring_re.json
stage694a_ltu_eab_driver_dma_ring_and_zerocopy_tx_re.json
stage754a_ltu_eab_driver_irq_coalescing_and_napi_re.json
stage80a_ltu_eab_and_ame_dev_fullrea_dissection_20261026.json
```

**`CONFIRMED`**: `prior_receipts_without_source = 5`.

That is the consequence worth stating without softening: **five prior receipts describe a binary that
this corpus cannot reproduce.** Stages 323A, 694A and 754A report DMA-ring, zerocopy and NAPI
behaviour for `eab_driver`. Those claims may be entirely correct. They are **not independently
verifiable here**, and this stage does not restate them as if they were.

## 1. The telemetry surface that does exist

Four modules carry the whole vocabulary:

| Module | Bytes | `ioctl` | `genl` | `netlink` | `debugfs` | `copy_to_user` | `nl80211` |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| `ame_core.ko` | 3,282,052 | 8 | **4** | **5** | 0 | 1 | **0** |
| `ame_dev.ko` | 298,760 | **17** | 0 | 0 | 5 | **3** | **0** |
| `cds_mac_mod.ko` | 139,672 | 2 | 0 | 0 | **17** | 0 | **0** |
| `ame_radio_mod.ko` | 578,424 | 0 | 0 | 0 | 0 | 0 | 0 |

**`CONFIRMED`**: `telemetry_channels = 3`.

Three channels, three different modules, three different mechanisms:

1. **Character-device ioctl** — `ame_dev.ko`, 17 control references and 3 `copy_to_user` calls. This is
   the classic telemetry surface: a driver-defined ioctl set copying structures out to user space.
2. **Generic netlink** — `ame_core.ko`, `netlink` 5 with `genl` **4**.
3. **debugfs** — `cds_mac_mod.ko`, **17** references, the largest single debug surface in the tree.

`ame_radio_mod.ko`, at 578,424 bytes the second largest module in the tree, carries **zero** telemetry
vocabulary. **Size does not predict surface**, and a tool that picked its target by size would have
chosen the one module with nothing in it.

## 2. The netlink channel is generic, not wireless

**`CONFIRMED`**: `nl80211_hits = 0` across every module probed, and `netlink_is_generic = 1`.

So LTU's netlink surface is **generic netlink with a private family**, not `nl80211` vendor commands.
The practical consequence: a diagnostic tool built on `iw` or on `nl80211` vendor subcommands will find
**nothing** on these radios, and would conclude the telemetry does not exist.

`iwreq` also returns **0**, so there is no wireless-extensions path either. Both conventional wireless
interfaces are absent, and the surface is entirely proprietary.

## 3. What is established

| Claim | Status |
| :--- | :-: |
| `eab_driver.ko` is in the module tree | **REFUTED** (0 of 154) |
| five prior receipts describe it | **CONFIRMED** |
| those receipts are reproducible from this corpus | **REFUTED** (no source binary) |
| `ame_dev.ko` carries an ioctl surface | **CONFIRMED** (17 ioctl, 3 copy_to_user) |
| `ame_core.ko` carries generic netlink | **CONFIRMED** (`netlink` 5, `genl` 4) |
| `cds_mac_mod.ko` carries debugfs | **CONFIRMED** (17) |
| `ame_radio_mod.ko` carries any telemetry vocabulary | **REFUTED** (0 despite 578,424 bytes) |
| `nl80211` is used anywhere | **REFUTED** (0) |
| the ioctl numbers, family id and debugfs names | **UNKNOWN / not decoded** |

## 4. The operational reading

For LTU telemetry work, the targets are now unambiguous:

1. **structures out of the kernel:** `ame_dev.ko` — ioctl plus `copy_to_user`;
2. **events and asynchronous reporting:** `ame_core.ko` — generic netlink, private family;
3. **live counters and state dumps:** `cds_mac_mod.ko` — debugfs;
4. **not `nl80211`:** the vocabulary is absent, so any `iw`-based plan is dead on arrival;
5. **not `ame_radio_mod.ko` by size:** 578 KB and zero surface.

And one caution that outlasts this stage: `eab_driver.ko` is cited five times in the archive and is
absent from the corpus. Any downstream document that depends on those receipts should say so, or it will
inherit an unverifiable premise.

## 5. Gaps

- **`UNKNOWN`** — the `ame_dev` ioctl numbers and the structures they copy.
- **`UNKNOWN`** — the generic-netlink family id and its command set.
- **`UNKNOWN`** — the debugfs file names exposed by `cds_mac_mod.ko`.
- **Blocked** — `eab_driver.ko` absent, so its netlink and ioctl surface cannot be measured.
- **Known limit** — a token count locates a channel, it does not decode a protocol.
- **Not attempted** — disassembly, dynamic validation.
