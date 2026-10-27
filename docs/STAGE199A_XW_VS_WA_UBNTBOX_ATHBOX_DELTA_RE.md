<!-- doc-head: STAGE199A_XW_VS_WA_UBNTBOX_ATHBOX_DELTA_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 199A — `ubntbox` / `athbox` applet delta, XW.v6.3.6 vs WA.v8.7.25

- **Receipt**: [`artifacts/autoresearch/stage199a_xw_vs_wa_ubntbox_athbox_delta_re.json`](../artifacts/autoresearch/stage199a_xw_vs_wa_ubntbox_athbox_delta_re.json)
- **Tool**: `tools/re/audit_stage197a_to_199a_hal_and_xw_delta.py`
- **Scope**: offline static only. No device access.

## 0. Premise correction

The task asked for `XW.v6.3.6` vs **`WA.v8.7.11`**. **`WA.v8.7.11` does not exist in this
repository** — only `fwupdate.real.wa8711` and `2xc_8711_modules/*.ko`. The comparison therefore
uses `WA.v8.7.25`, which is the newest full WA rootfs available.

## 1. Binary inventory

| Image | Binary | Bytes |
| :--- | :--- | :-: |
| `WA.v8.7.25` | `ubntbox` | 899,180 |
| `XW.v6.3.6` | `ubntbox` | **570,776** |
| `WA.v8.7.25` | `athbox` | 202,920 |
| `XW.v6.3.6` | `athbox` | **162,520** |

Both airOS 6 builds are roughly **30 % smaller**. That alone signals a substantial applet
reduction, which the table delta confirms.

## 2. Applet delta

### `ubntbox`

| | Count |
| :--- | :-: |
| WA.v8.7.25 | **29** |
| XW.v6.3.6 | **25** |
| Common | 17 |
| Only in WA | **12** |
| Only in XW | **8** |

### `athbox`

| | Count |
| :--- | :-: |
| WA.v8.7.25 | **15** |
| XW.v6.3.6 | **10** |
| Common | **10** |
| Only in WA | **5** |
| Only in XW | **0** |

**`CONFIRMED`**: `athbox` in airOS 6 is a strict subset of airOS 8 — every XW `athbox` applet
exists in WA, and WA adds five. `ubntbox` is not a subset in either direction: it gained 12 and
lost 8.

## 3. Why the 8 XW-only applets are the interesting cell

An applet that exists in airOS 6 but **not** in airOS 8 is either:

- removed deliberately (feature retired, replaced by a daemon);
- renamed (the same functionality under a new applet name);
- still present but no longer dispatched from the table.

Distinguishing those requires comparing handler bodies, not names. This stage reports the
presence delta only and leaves the reason `UNKNOWN`.

Conversely the 12 WA-only applets are airOS 8 additions — the expected direction, and consistent
with the 899 KB vs 570 KB size gap.

## 4. The conflation warning

The task framed this as an applet audit across two releases. It is also a crossing of **product
lines**: `XW` is airOS 6 on M5 hardware, `WA` is airOS 8 on airMax AC. Any difference in the
table therefore has three possible causes:

1. **version** (6 → 8);
2. **platform** (M5 vs AC);
3. **build configuration**.

This stage cannot separate them. The receipt states this in `gaps`, and a test asserts the
warning is present, so a future reader does not treat the delta as a pure version diff.

## 5. What would separate the causes

Compare **XW.v6.1.4 vs XW.v6.3.6** for the version axis at fixed platform, and
**WA.v8.7.25 vs XC.v8.7.25** for the platform axis at fixed version. Both pairs are on disk.
Only then does the XW-vs-WA delta become interpretable as version-plus-platform rather than
three unknowns.

## 6. Gaps

- **`UNKNOWN`** — why the 8 XW-only `ubntbox` applets were dropped.
- **`UNKNOWN`** — whether any is renamed rather than removed.
- **`KNOWN LIMIT`** — presence is not behaviour: an applet present in both builds may be
  implemented differently, and this stage does not compare handler bodies.
- **`KNOWN LIMIT`** — the delta conflates airOS 6 vs 8 with M5 vs AC.
- **Not attempted** — dynamic validation.
