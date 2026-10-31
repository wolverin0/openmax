<!-- doc-head: STAGE363A_GUARIDA_KITS_V2_OL_VERIFIER.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 363A — Updated Pre-Staged Guarida `Mode B` Kits v2 (`tools/guarida_stage0_kits/`) With `athstats -ol` Pre/Post Verifier

- **Status**: `CONFIRMED`
- **Attribution**: `external controller` + `proprietary airMAX/LTU module` (`bin/athbox` `-ol`) + `QCA firmware` (`wal_dbg_stats`)
- **Safety Boundary**: `0` live writes performed (`SG-01..05` compliant; pre-staged locally)
- **Script**: [`tools/verify/build_stage363a_guarida_kits_v2_ol_verifier.py`](../tools/verify/build_stage363a_guarida_kits_v2_ol_verifier.py)
- **Receipt**: [`artifacts/autoresearch/stage363a_guarida_kits_v2_ol_verifier.json`](../artifacts/autoresearch/stage363a_guarida_kits_v2_ol_verifier.json)

---

## 1. Upgrade Summary for `tools/guarida_stage0_kits/*.sh` (`CONFIRMED`)

Following `FMX-DISC-44` (`Stage 281A`: default `athstats` without `-ol` aliases `multiqueue_sent[1]` and `multiqueue_compl[1]` as `no tx buffer (data)` and `xmit filtered`) and `Stage 362A` (`Panel2 .82` `sta_priority='1 2 1'` + `daprot=2` + `ff_mcast_airtime_limit=5` deferred-list rescue), all 4 pre-staged `Mode B` kits in [`tools/guarida_stage0_kits/`](../tools/guarida_stage0_kits/) have been upgraded to **v2**:

| Kit Script | Target Node | New `athstats -ol` Pre/Post Verifier | Additional `Mode B` v2 Enhancements |
| :--- | :--- | :--- | :--- |
| [`almafuerte_60_mode_b.sh`](../tools/guarida_stage0_kits/almafuerte_60_mode_b.sh) | `198.18.0.3` (`Ap.Guarida`, `0xe3d6`) | `fmx_capture_ol_wal_stats "pre"` & `"post"` (`mpdus_requed`, `excess retries`, `underrun`, `ast_rxorn`) | Preserves `ackdistance=4050`, `airview=disabled`, `min_free_kbytes=4096` |
| [`guarida_61_mode_b.sh`](../tools/guarida_stage0_kits/guarida_61_mode_b.sh) | `198.18.0.4` (`St.Guarida`, `0xe3d6`) | `fmx_capture_ol_wal_stats "pre"` & `"post"` (`230.74M` `ast_rxorn` & `10.52M` `excess retries` baseline) | Preserves `ackdistance=4050`, `airview=disabled`, `min_free_kbytes=4096` |
| [`panel2_82_mode_b.sh`](../tools/guarida_stage0_kits/panel2_82_mode_b.sh) | `198.18.0.5` (`Panel2`, `0xe8e5`) | `fmx_capture_ol_wal_stats "pre"` & `"post"` (`139.75M` `mpdus_requed` & `2.80M` `mcast_dropped` baseline) | Adds **`sta_priority="1 2 1"`**, **`daprot=2`**, **`ff_mcast_airtime_limit=5`** (`Stage 362A`) |
| [`panel3_83_mode_b.sh`](../tools/guarida_stage0_kits/panel3_83_mode_b.sh) | `198.18.0.6` (`Panel3`, `0xe8e5`) | `fmx_capture_ol_wal_stats "pre"` & `"post"` (`9.52M` `excess retries` & `674.50M` `local_enqued` baseline) | Preserves `polling=enabled`, `ackdistance=3150`, `airview=disabled` |

---

## 2. Deterministic `athstats -ol` Verification Function

Every kit now defines and invokes:
```sh
fmx_capture_ol_wal_stats() {
    phase="$1"
    athstats -ol > "$BACKUP_DIR/athstats_ol_${phase}.txt" 2>/dev/null || true
    grep -E "mpdus_requed|excess retries|underrun|mcast_dropped|ast_be_nobuf|ast_rxorn" \
        "$BACKUP_DIR/athstats_ol_${phase}.txt" > "$BACKUP_DIR/wal_summary_${phase}.txt" 2>/dev/null || true
}
```
ensuring zero false-positive `SIOCGATHSTATS` (`0x89f0`) ABI aliasing during pre/post comparison.
