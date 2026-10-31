<!-- doc-head: Stage 835A - bin/uav is a zero-byte file in all four rootfs so the validator the stage names has no content, while ubntbox at 899180 bytes carries system.cfg 31 times and persistent 28 times and implements persistence by tarring the persistent directory, with validate appearing exactly once and no key schema by that name -->
<!-- /doc-head -->
# Stage 835A — airOS UAV and cent-mgmt system.cfg key validator

- **Receipt**: [`artifacts/autoresearch/stage835a_airos_uav_and_cent_mgmt_config_validator_re.json`](../artifacts/autoresearch/stage835a_airos_uav_and_cent_mgmt_config_validator_re.json)
- **Tool**: [`tools/re/dissect_stage835a_airos_uav_and_cent_mgmt_config_validator_re.py`](../tools/re/dissect_stage835a_airos_uav_and_cent_mgmt_config_validator_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, **no config written**.

## 0. `uav` is empty in all four rootfs

| Rootfs | `bin/uav` bytes |
| :--- | :-: |
| `xc_8725_rootfs` | **0** |
| `xc_874cs_rootfs` | **0** |
| `xw_614_rootfs` | **0** |
| `xw_636_rootfs` | **0** |

**`REFUTED`**: `uav_all_zero_byte = 1`, `uav_readable = 0` of 4.

The stage names `/sbin/uav` as one of two validator hosts. **It contains nothing.** This is the
corpus-wide zero-byte stub defect again — the same defect that blocked `ubnt-gps-reader` (416A),
`libltu` (424A) and `ubnt-caldata` (785A).

## 1. `ubntbox` is real, and every copy is readable

| Image | `bin/ubntbox` bytes |
| :--- | :-: |
| `WA.v8.7.25` | **899,180** |
| `XC.v8.7.25` | **899,180** |
| `XC.v8.7.4cs` | 879,816 |
| `XW.v6.1.4` | 711,960 |
| `XW.v6.3.6` | **570,776** |

**`CONFIRMED`**: `boxes_ok = 5`, all readable. WA and XC v8.7.25 are the **same size (899,180) but
different binaries** — the same pattern Stage 831A found for `ubnt_poll_host.ko`. A size check would
have called them identical; only a byte comparison separates them.

## 2. The config vocabulary is persistence-oriented, not validation-oriented

| Token | Best-copy hits |
| :--- | :-: |
| `system.cfg` | **31** |
| `persistent` | **28** |
| `validate` | **1** |
| `invalid` | 5 |
| `tar -cz` | 1 |

**`CONFIRMED`**: `cfg_is_persistence_oriented = 1` (`persistent` 28 vs `validate` 1).

The surrounding strings make the mechanism explicit:

```
/tmp/system.cfg
/bin/tar -cz -O -C %s persistent
system.cfg.editor
kill -1 1        killall -USR1 ustatsd
```

**`CONFIRMED`**: `persistence_is_tar = 1`. Persistence is implemented by **archiving the `persistent`
directory with tar**, and the restart path is `kill -1 1` (re-init) plus `USR1` to `ustatsd`.

## 3. There is no key validator by that name

**`REFUTED`**: `validator_named = 0`. **One** `validate` occurrence in 899 KB is not a schema check —
it is a single string, not a per-key table.

And `schema` does not appear in the token census at all. So the stage's premise — a **key validator**
in `ubntbox` — is not supported by the vocabulary.

**`REFUTED`**: `key_schema_recovered = 0`. How a custom key is accepted or rejected was **not decoded**.

## 4. What actually decides persistence

The evidence points at a **directory**, not a schema:

| Mechanism | Evidence |
| :--- | :--- |
| `persistent/` survives reboot | `tar -cz -C %s persistent` |
| `system.cfg` is regenerated | `/tmp/system.cfg`, `system.cfg.editor` |
| services re-read on change | `kill -1 1`, `killall -USR1 ustatsd` |

**`CONFIRMED`**: a custom key survives if and only if it lands inside `persistent` **before** the
archive is taken. That is a **placement** rule, not a **schema** rule.

This is a materially different answer from the one asked for, and it is more actionable: it says
where to put a key rather than which keys are legal.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| `bin/uav` is readable | **REFUTED** (0 bytes × 4) |
| `ubntbox` is readable on all 5 images | **CONFIRMED** |
| WA and XC v8.7.25 `ubntbox` are identical | **REFUTED** (same size, different bytes) |
| `system.cfg` is referenced heavily | **CONFIRMED** (31) |
| persistence is implemented by tar of `persistent/` | **CONFIRMED** |
| a key validator is named in `ubntbox` | **REFUTED** (`validate` × 1) |
| a key schema was recovered | **REFUTED** |
| the rule that accepts or rejects a custom key | **UNKNOWN / not decoded** |

## 6. The operational reading

For "apply custom profiles without rejection", the corpus gives a **placement rule** and a warning:

1. write the key into the **`persistent`** tree, not only into `/tmp/system.cfg`;
2. expect a **service restart** to be what applies it (`kill -1 1`, `USR1` to `ustatsd`);
3. do **not** expect a schema rejection to be documented anywhere — there is no per-key validator by
   name, so a rejected key fails for a reason this corpus cannot enumerate.

The last point matters: absence of a validator does not mean any key is accepted. It means the
rejection, if it happens, is **not explained** in the readable corpus.

## 7. Gaps

- **`UNKNOWN`** — what accepts or rejects a custom `system.cfg` key.
- **`UNKNOWN`** — the contents of `bin/uav`, which is empty in every rootfs.
- **`UNKNOWN`** — whether `system.cfg.editor` performs any check before writing.
- **UNKNOWN** — the `persistent` tree layout and which subpaths are honoured.
- **Known limit** — a token count is not a schema.
- **Not attempted** — writing any config, dynamic validation.
